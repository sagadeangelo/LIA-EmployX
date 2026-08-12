"""
LIA EmployX — Runtime Inspector API

GET /runtime                   → estado global del runtime
GET /runtime/missions          → lista de misiones activas en el runtime
GET /runtime/{mission_id}      → inspección detallada de una misión
GET /runtime/{mission_id}/memory   → SharedMemory actual
GET /runtime/{mission_id}/timeline → Timeline de la misión
GET /runtime/{mission_id}/events   → Eventos del Event Log
POST /runtime/{mission_id}/cancel  → Cancelar misión
POST /runtime/{mission_id}/pause   → Pausar misión
"""

from fastapi import APIRouter, HTTPException
from typing import Any, Dict, List

from backend.runtime.runtime_registry import get_runtime_registry
from backend.modules.mission.repositories import (
    MissionRepository,
    MissionEventRepository,
)
from backend.storage.json_provider import JsonStorageProvider

router = APIRouter(prefix="/api/v1/runtime", tags=["Runtime Inspector"])

# Compartir el storage con el módulo de misiones
_storage = JsonStorageProvider()
_mission_repo = MissionRepository(_storage)
_event_repo = MissionEventRepository(_storage)


@router.get("", summary="Estado global del Mission Runtime")
async def get_runtime_status() -> Dict[str, Any]:
    registry = get_runtime_registry()
    return {
        "status": "running",
        "active_missions": len(registry),
        "active_mission_ids": registry.list_active(),
        "registered_event_types": registry._bus.registered_event_types(),
    }


@router.get("/missions", summary="Lista de misiones activas")
async def list_runtime_missions() -> List[Dict[str, Any]]:
    registry = get_runtime_registry()
    return registry.inspect_all()


@router.get("/{mission_id}", summary="Inspección detallada de una misión")
async def inspect_mission(mission_id: str) -> Dict[str, Any]:
    registry = get_runtime_registry()
    info = registry.inspect(mission_id)
    if info:
        return info
    # Misión no activa en runtime — buscar en storage
    mission = _mission_repo.get_by_id(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return {
        "mission_id": mission.id,
        "state": mission.status.value,
        "current_agent": mission.current_agent,
        "progress": mission.progress,
        "execution_seconds": None,
        "last_heartbeat": (
            mission.last_heartbeat.isoformat() if mission.last_heartbeat else None
        ),
        "errors": mission.errors,
        "note": "Mission not in active runtime (may be completed/cancelled)",
    }


@router.get("/{mission_id}/memory", summary="SharedMemory actual de la misión")
async def get_mission_memory(mission_id: str) -> Dict[str, Any]:
    mission = _mission_repo.get_by_id(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return {
        "mission_id": mission_id,
        "shared_memory": mission.metadata.get("shared_memory", {}),
        "updated_at": mission.updated_at.isoformat(),
    }


@router.get("/{mission_id}/timeline", summary="Timeline de la misión")
async def get_mission_timeline(mission_id: str) -> Dict[str, Any]:
    mission = _mission_repo.get_by_id(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return {
        "mission_id": mission_id,
        "timeline": mission.timeline,
        "total_entries": len(mission.timeline),
    }


@router.get("/{mission_id}/events", summary="Event Log de la misión")
async def get_mission_events(mission_id: str) -> Dict[str, Any]:
    events = _event_repo.get_by_mission(mission_id)
    return {
        "mission_id": mission_id,
        "events": [e.model_dump() for e in events],
        "total": len(events),
    }


@router.post("/{mission_id}/cancel", summary="Cancelar misión activa")
async def cancel_mission(mission_id: str) -> Dict[str, Any]:
    registry = get_runtime_registry()
    cancelled = await registry.cancel_mission(mission_id, reason="API cancel request")
    if not cancelled:
        raise HTTPException(status_code=404, detail="Mission not active in runtime")
    return {"status": "cancellation_requested", "mission_id": mission_id}


@router.post("/{mission_id}/pause", summary="Pausar misión activa")
async def pause_mission(mission_id: str) -> Dict[str, Any]:
    registry = get_runtime_registry()
    paused = await registry.pause_mission(mission_id)
    if not paused:
        raise HTTPException(status_code=404, detail="Mission not active in runtime")
    return {"status": "pause_requested", "mission_id": mission_id}
