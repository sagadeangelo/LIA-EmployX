from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from ..schemas.command_center import (
    CommandCenterData,
    ExecutiveReport,
    Priority,
    Opportunity,
    Insight,
)

from backend.modules.mission.repositories import MissionRepository
from backend.storage.json_provider import JsonStorageProvider

router = APIRouter(prefix="/api/v1", tags=["Command Center"])

mission_repo = MissionRepository(JsonStorageProvider())


class CommandExecute(BaseModel):
    command: str


@router.get("/command-center/{mission_id}", response_model=CommandCenterData)
async def get_command_center(mission_id: str):
    mission = mission_repo.get_by_id(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    # Extraer información de shared_memory persistida en metadata
    sm = mission.metadata.get("shared_memory", {})

    executive_summary = sm.get(
        "executive_summary", "Esperando CV para iniciar el análisis..."
    )

    # Mapear Prioridades
    raw_priorities = sm.get("priorities", [])
    priorities = []
    for idx, p in enumerate(raw_priorities):
        priorities.append(
            Priority(
                id=f"p-{idx}",
                title=p.get("title", ""),
                description=p.get("description", ""),
                urgency=p.get("urgency", "medium"),
                status=p.get("status", "pending"),
            )
        )

    # Mapear Oportunidades
    raw_opportunities = sm.get("opportunities", [])
    opportunities = []
    for idx, o in enumerate(raw_opportunities):
        opportunities.append(
            Opportunity(
                id=f"o-{idx}",
                title=o.get("title", ""),
                company=o.get("company", ""),
                match_score=o.get("match_score", 0),
                url=o.get("url", ""),
            )
        )

    # Mapear Insights
    raw_insights = sm.get("insights", [])
    insights = []
    for idx, i in enumerate(raw_insights):
        insights.append(
            Insight(
                id=f"i-{idx}",
                content=i.get("content", ""),
                type=i.get("type", "market"),
            )
        )

    return CommandCenterData(
        executive_report=ExecutiveReport(
            summary=executive_summary, generated_at=datetime.utcnow()
        ),
        priorities=priorities,
        opportunities=opportunities,
        insights=insights,
    )


@router.post("/command-center/{mission_id}/execute")
async def execute_command(mission_id: str, payload: CommandExecute):
    # En el futuro, esto se enviará al MissionController como un comando humano
    return {
        "status": "success",
        "message": f"Command '{payload.command}' sent to Mission Controller.",
    }
