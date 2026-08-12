"""
Tests del Mission Runtime — Recovery, Cancellation, State Machine, Timeline.

Ejecutar con:
    PYTHONPATH=. python backend/tests/test_mission_runtime.py
"""
import asyncio
import os
import tempfile
from fastapi.testclient import TestClient

# ── usar un directorio temporal para no contaminar data/ ──────────────────────
_tmpdir = tempfile.mkdtemp(prefix="lia_runtime_test_")
os.environ["LIA_DATA_DIR"] = _tmpdir

from backend.storage.json_provider import JsonStorageProvider
from backend.modules.mission.repositories import MissionRepository, MissionEventRepository
from backend.modules.mission.models import Mission
from backend.runtime.mission_state import MissionState, RECOVERABLE_STATES, TERMINAL_STATES, can_transition
from backend.runtime.event_bus import RuntimeEventBus
from backend.runtime.runtime_registry import RuntimeRegistry, init_runtime_registry
from backend.runtime.recovery_engine import RecoveryEngine
from backend.agents.bootstrap import build_registry


# ─────────────────────────────────────────────────────────────────────────────
# Helpers de test
# ─────────────────────────────────────────────────────────────────────────────

def make_repos():
    storage = JsonStorageProvider(data_dir=_tmpdir)
    return MissionRepository(storage), MissionEventRepository(storage)

def make_mission(title="Test Mission", state: MissionState = MissionState.CREATED) -> Mission:
    m = Mission(title=title, career_goal="Software Engineer")
    m.runtime_state = state
    return m


# ─────────────────────────────────────────────────────────────────────────────
# TEST 1: FSM — Transiciones válidas e inválidas
# ─────────────────────────────────────────────────────────────────────────────

def test_fsm_valid_transitions():
    assert can_transition(MissionState.CREATED, MissionState.QUEUED)
    assert can_transition(MissionState.QUEUED, MissionState.RUNNING)
    assert can_transition(MissionState.RUNNING, MissionState.COMPLETED)
    assert can_transition(MissionState.RUNNING, MissionState.PAUSED)
    assert can_transition(MissionState.RUNNING, MissionState.CANCELLED)
    print("[PASS] test_fsm_valid_transitions")

def test_fsm_invalid_transitions():
    assert not can_transition(MissionState.COMPLETED, MissionState.RUNNING)
    assert not can_transition(MissionState.CANCELLED, MissionState.RUNNING)
    assert not can_transition(MissionState.CREATED, MissionState.COMPLETED)
    print("[PASS] test_fsm_invalid_transitions")

def test_fsm_terminal_states():
    for state in TERMINAL_STATES:
        assert can_transition(state, MissionState.RUNNING) is False
    print("[PASS] test_fsm_terminal_states")


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2: MissionRuntime — Ejecución y Timeline
# ─────────────────────────────────────────────────────────────────────────────

async def test_runtime_execution_and_timeline():
    mission_repo, event_repo = make_repos()
    mission = make_mission("Runtime Exec Test")
    mission_repo.save(mission)

    bus = RuntimeEventBus()
    events_received = []

    from backend.runtime.runtime_events import MissionCompleted, AgentCompleted
    bus.subscribe(MissionCompleted, lambda e: events_received.append(e.event_type))
    bus.subscribe(AgentCompleted, lambda e: events_received.append(e.event_type))

    from backend.runtime.mission_runtime import MissionRuntime
    registry = build_registry()
    runtime = MissionRuntime(mission, mission_repo, event_repo, registry, bus)
    await runtime.run()

    # Verificar estado final
    saved = mission_repo.get_by_id(mission.id)
    assert saved.runtime_state == MissionState.COMPLETED, f"Expected COMPLETED got {saved.runtime_state}"
    assert len(saved.timeline) > 0, "Timeline debe tener entradas"
    assert saved.progress >= 0
    assert "MissionCompleted" in events_received
    print(f"[PASS] test_runtime_execution_and_timeline — {len(saved.timeline)} timeline entries, progress={saved.progress}%")


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3: SharedMemory persiste entre ejecuciones
# ─────────────────────────────────────────────────────────────────────────────

async def test_shared_memory_persistence():
    mission_repo, event_repo = make_repos()
    mission = make_mission("SharedMemory Persistence Test")
    mission.shared_memory["pre_existing_key"] = "pre_existing_value"
    mission_repo.save(mission)

    bus = RuntimeEventBus()
    from backend.runtime.mission_runtime import MissionRuntime
    registry = build_registry()
    runtime = MissionRuntime(mission, mission_repo, event_repo, registry, bus)
    await runtime.run()

    saved = mission_repo.get_by_id(mission.id)
    # La clave pre-existente debe sobrevivir
    assert saved.shared_memory.get("pre_existing_key") == "pre_existing_value", \
        "SharedMemory pre-existente no se preservó"
    print("[PASS] test_shared_memory_persistence")


# ─────────────────────────────────────────────────────────────────────────────
# TEST 4: Cancellation limpia
# ─────────────────────────────────────────────────────────────────────────────

async def test_cancellation():
    mission_repo, event_repo = make_repos()
    mission = make_mission("Cancellation Test")
    mission_repo.save(mission)

    bus = RuntimeEventBus()
    from backend.runtime.mission_runtime import MissionRuntime
    registry = build_registry()
    runtime = MissionRuntime(mission, mission_repo, event_repo, registry, bus)

    # Cancelar inmediatamente antes de run
    await runtime.cancel("Test cancel")

    saved = mission_repo.get_by_id(mission.id)
    assert saved.runtime_state == MissionState.CANCELLED, f"Expected CANCELLED got {saved.runtime_state}"
    print("[PASS] test_cancellation")


# ─────────────────────────────────────────────────────────────────────────────
# TEST 5: Recovery Engine — detecta misiones interrumpidas
# ─────────────────────────────────────────────────────────────────────────────

async def test_recovery_engine_detects_interrupted():
    mission_repo, event_repo = make_repos()

    # Simular una misión que quedó en RUNNING (backend cayó)
    interrupted = make_mission("Interrupted Mission", state=MissionState.RUNNING)
    mission_repo.save(interrupted)

    # Misión completada — no debe recuperarse
    completed = make_mission("Completed Mission", state=MissionState.COMPLETED)
    mission_repo.save(completed)

    bus = RuntimeEventBus()
    registry = RuntimeRegistry(mission_repo, event_repo, bus)
    engine = RecoveryEngine(mission_repo, event_repo, registry)

    report = await engine.get_recovery_report()
    assert report["total_missions"] >= 2
    assert any(m["id"] == interrupted.id for m in report["recoverable"])
    assert not any(m["id"] == completed.id for m in report["recoverable"])
    print(f"[PASS] test_recovery_engine_detects_interrupted — recoverable: {[m['id'] for m in report['recoverable']]}")


# ─────────────────────────────────────────────────────────────────────────────
# TEST 6: Recovery Engine — recupera y completa la misión
# ─────────────────────────────────────────────────────────────────────────────

async def test_recovery_engine_recovers_and_completes():
    mission_repo, event_repo = make_repos()

    # Simular misión interrumpida en RUNNING
    interrupted = make_mission("Recovery Completion Test", state=MissionState.RUNNING)
    mission_repo.save(interrupted)

    bus = RuntimeEventBus()
    recovered_events = []
    from backend.runtime.runtime_events import MissionRecovered
    bus.subscribe(MissionRecovered, lambda e: recovered_events.append(e))

    registry = RuntimeRegistry(mission_repo, event_repo, bus)
    engine = RecoveryEngine(mission_repo, event_repo, registry)
    recovered_ids = await engine.recover_all()

    # Esperar que el task asíncrono de recovery termine
    await asyncio.sleep(2)

    assert interrupted.id in recovered_ids
    assert len(recovered_events) == 1
    assert recovered_events[0].mission_id == interrupted.id

    saved = mission_repo.get_by_id(interrupted.id)
    assert saved.runtime_state == MissionState.COMPLETED, f"Expected COMPLETED after recovery, got {saved.runtime_state}"
    assert len(saved.timeline) > 0
    print(f"[PASS] test_recovery_engine_recovers_and_completes — {len(saved.timeline)} timeline entries")


# ─────────────────────────────────────────────────────────────────────────────
# Runner
# ─────────────────────────────────────────────────────────────────────────────

def run_all():
    print("\n" + "=" * 60)
    print("  LIA EmployX — Mission Runtime Tests")
    print("=" * 60 + "\n")

    # Tests síncronos
    test_fsm_valid_transitions()
    test_fsm_invalid_transitions()
    test_fsm_terminal_states()

    # Tests asíncronos
    asyncio.run(test_runtime_execution_and_timeline())
    asyncio.run(test_shared_memory_persistence())
    asyncio.run(test_cancellation())
    asyncio.run(test_recovery_engine_detects_interrupted())
    asyncio.run(test_recovery_engine_recovers_and_completes())

    print("\n" + "=" * 60)
    print("  ✅ All Mission Runtime Tests PASSED")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_all()
