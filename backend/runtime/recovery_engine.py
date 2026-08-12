"""
LIA EmployX — Mission Runtime
Layer 6: RecoveryEngine

Al arrancar el backend, el RecoveryEngine:
  1. Lee todas las misiones del StorageProvider
  2. Identifica las que estaban en estados recuperables (RUNNING, QUEUED, WAITING_AGENT)
  3. Las pasa al RuntimeRegistry para reanudar la ejecución
  4. Emite un evento MissionRecovered por cada misión restaurada

Esto garantiza que ninguna misión se pierde tras un reinicio del servidor.

Flujo:
    FastAPI startup
        ↓
    RecoveryEngine.recover_all()
        ↓
    MissionRepository.get_all()
        ↓
    [misiones en RECOVERABLE_STATES]
        ↓
    RuntimeRegistry.recover_mission(mission)
        ↓
    MissionRuntime.recover(previous_state)
        ↓
    EventBus: MissionRecovered
"""
from __future__ import annotations

import logging
from typing import List

from backend.modules.mission.models import Mission
from backend.modules.mission.repositories import MissionRepository, MissionEventRepository
from backend.runtime.mission_state import RECOVERABLE_STATUSES, MissionStatus
from backend.runtime.runtime_registry import RuntimeRegistry

logger = logging.getLogger(__name__)


class RecoveryEngine:
    """
    Responsable de restaurar misiones interrumpidas al iniciar el servidor.
    """

    def __init__(
        self,
        mission_repo: MissionRepository,
        event_repo: MissionEventRepository,
        runtime_registry: RuntimeRegistry,
    ) -> None:
        self._mission_repo = mission_repo
        self._event_repo = event_repo
        self._registry = runtime_registry

    async def recover_all(self) -> List[str]:
        """
        Recupera todas las misiones que quedaron en estado activo.

        Returns:
            Lista de mission_ids que fueron recuperados.
        """
        all_missions = self._mission_repo.get_all()
        recovered_ids: List[str] = []

        recoverable = [
            m for m in all_missions
            if m.status in RECOVERABLE_STATUSES
        ]

        if not recoverable:
            logger.info("[RecoveryEngine] No hay misiones interrumpidas para recuperar.")
            return []

        logger.info(
            "[RecoveryEngine] Encontradas %d misiones para recuperar: %s",
            len(recoverable),
            [m.id for m in recoverable],
        )

        for mission in recoverable:
            import os
            # Integrity checks before recovery
            if not mission.state.file_path or not os.path.exists(mission.state.file_path):
                logger.error("[RecoveryEngine] Archivo faltante para misión %s", mission.id)
                mission.status = MissionStatus.FAILED
                mission.failureReason = "Archivo no encontrado en el servidor."
                self._mission_repo.save(mission)
                continue
                
            if mission.status in [MissionStatus.PROCESSING, MissionStatus.WAITING_AGENT] and not mission.state.metadata:
                logger.warning("[RecoveryEngine] Misión %s sin metadata, reseteando a STORED.", mission.id)
                mission.status = MissionStatus.STORED
                # Continuing with recovery will enqueue it properly since it's STORED
                self._mission_repo.save(mission)

            try:
                await self._registry.recover_mission(mission)
                recovered_ids.append(mission.id)
                logger.info("[RecoveryEngine] Misión %s restaurada.", mission.id)
            except Exception as exc:
                logger.exception(
                    "[RecoveryEngine] Error al recuperar misión %s: %s", mission.id, exc
                )

        return recovered_ids

    async def get_recovery_report(self) -> dict:
        """
        Devuelve un reporte del estado del sistema para el startup log.
        """
        all_missions = self._mission_repo.get_all()
        by_state: dict = {}
        for mission in all_missions:
            state = mission.status.value
            by_state[state] = by_state.get(state, 0) + 1

        return {
            "total_missions": len(all_missions),
            "by_state": by_state,
            "recoverable": [
                {"id": m.id, "title": m.title, "state": m.status.value}
                for m in all_missions
                if m.status in RECOVERABLE_STATUSES
            ],
        }
