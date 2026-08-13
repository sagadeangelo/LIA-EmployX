from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional

from backend.modules.mission.models import (
    Mission,
    MissionSnapshot,
    MissionEvent,
    RuntimeStatus,
    SystemHealth,
)
from backend.api.schemas.mission import MissionCreate
from backend.storage.json_provider import JsonStorageProvider
from backend.modules.mission.repositories import (
    MissionRepository,
    MissionEventRepository,
)
from backend.modules.mission.controller import MissionController
from backend.runtime.runtime_registry import get_runtime_registry
from backend.runtime.mission_state import MissionStage, MissionStatus

router = APIRouter(prefix="/api/v1/missions", tags=["Missions"])

# Global repositories for read access (safe at import time)
storage_provider = JsonStorageProvider()
mission_repo = MissionRepository(storage_provider)
event_repo = MissionEventRepository(storage_provider)


def get_mission_controller():
    # Use the global singleton initialized in lifespan
    runtime_registry = get_runtime_registry()
    return MissionController(mission_repo, event_repo, runtime_registry._agent_registry)


@router.post("", response_model=MissionSnapshot)
async def create_mission(mission_data: MissionCreate):
    mission = Mission(**mission_data.model_dump(), user_id="temp_user")
    mission_repo.save(mission)
    controller = get_mission_controller()
    return MissionSnapshot(
        mission=mission,
        runtime=RuntimeStatus(online=True, active_agents=[], current_agent=None),
        timeline=[],
        progress=mission.progress,
        current_step=mission.current_step.value,
        results=mission.outputs,
        health=SystemHealth(status="ok", database=True, storage=True, version="1.0.0"),
        warnings=mission.warnings,
        errors=mission.errors,
        availableActions=controller.get_available_actions(mission),
        retryMode=controller.get_retry_mode(mission),
    )


@router.get("", response_model=List[Mission])
async def list_missions(status: Optional[str] = None):
    missions = mission_repo.get_all()
    if status == "active":
        active_missions = [
            m for m in missions 
            if m.status not in (MissionStatus.COMPLETED, MissionStatus.FAILED, MissionStatus.CANCELLED)
        ]
        active_missions.sort(key=lambda x: x.created_at, reverse=True)
        return active_missions
    
    missions.sort(key=lambda x: x.created_at, reverse=True)
    return missions


@router.get("/{mission_id}/snapshot", response_model=MissionSnapshot)
async def get_mission_snapshot(mission_id: str):
    mission = mission_repo.get_by_id(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    events = event_repo.get_by_mission(mission_id)
    controller = get_mission_controller()
    return MissionSnapshot(
        mission=mission,
        runtime=RuntimeStatus(
            online=True,
            active_agents=mission.active_agents,
            current_agent=mission.current_agent,
        ),
        timeline=events,
        progress=mission.progress,
        current_step=mission.current_step.value,
        results=mission.outputs,
        health=SystemHealth(status="ok", database=True, storage=True, version="1.0.0"),
        warnings=mission.warnings,
        errors=mission.errors,
        availableActions=controller.get_available_actions(mission),
        retryMode=controller.get_retry_mode(mission),
    )


@router.post("/{mission_id}/run")
async def run_mission(mission_id: str):
    mission = mission_repo.get_by_id(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    get_mission_controller().trigger_engine(mission_id)
    return {"status": "engine_triggered", "mission_id": mission_id}


@router.post("/{mission_id}/resume")
async def resume_mission(mission_id: str):
    mission = mission_repo.get_by_id(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    mission.status = MissionStatus.PROCESSING
    mission.failureReason = None
    mission_repo.save(mission)

    get_mission_controller().trigger_engine(mission_id)
    return {"status": "resumed", "mission_id": mission_id}


@router.post("/{mission_id}/restart")
async def restart_mission(mission_id: str):
    mission = mission_repo.get_by_id(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    mission.status = MissionStatus.PROCESSING
    mission.current_step = MissionStage.RECEIVE_FILE
    mission.failureReason = None
    mission.progress = 0
    mission_repo.save(mission)

    return {"status": "restarted", "mission_id": mission_id}


@router.delete("/{mission_id}")
async def delete_mission(mission_id: str):
    return {"status": "deleted", "mission_id": mission_id}
