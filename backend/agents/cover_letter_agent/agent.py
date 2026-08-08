"""
LIA EmployX — CoverLetterGenerator
Responsabilidad UNICA: Generar cartas de presentacion personalizadas por vacante.
Requiere que JobHunter haya encontrado vacantes (TOP_JOBS en SharedMemory).
"""
from __future__ import annotations
from typing import List

from backend.agents.base.base_agent import BaseAgent, AgentMetadata
from backend.agents.base.agent_context import AgentContext
from backend.agents.base.agent_result import AgentResult
from backend.agents.base.shared_memory import SharedMemoryKey
from backend.modules.mission.models import MissionEvent, MissionEventType


class CoverLetterGenerator(BaseAgent):

    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            id="cover_letter_agent",
            name="Cover Letter Generator",
            version="1.0.0",
            author="LIA Team",
            description="Genera cartas de presentacion personalizadas para cada vacante prioritaria.",
            capabilities=["cover_letter_generation"],
            dependencies=["job_hunter"],
            priority=60,
            enabled=True,
        )

    def can_execute(self, context: AgentContext) -> bool:
        return context.shared_memory.contains(SharedMemoryKey.TOP_JOBS)

    async def execute(self, context: AgentContext) -> AgentResult:
        self._set_status("running")
        self.log("Generando cartas de presentacion...")

        mission = context.mission
        top_jobs = context.shared_memory.get(SharedMemoryKey.TOP_JOBS, [])
        skills = context.shared_memory.get(SharedMemoryKey.SKILLS, [])

        cover_letters = []
        for job in top_jobs[:3]:  # Genera para los top 3
            letter = _generate_cover_letter(job, mission, skills)
            cover_letters.append({"job_id": job["id"], "company": job["company"], "letter": letter})

        recommendations = [
            f"Generadas {len(cover_letters)} cartas de presentacion personalizadas.",
            "Cada carta esta optimizada para la empresa y rol especificos.",
        ]

        events = [
            MissionEvent(
                mission_id=mission.id,
                type=MissionEventType.MISSION_COMPLETED,
                source="CoverLetterGenerator",
                title="Cartas de presentación generadas",
                description=f"{len(cover_letters)} cartas de presentacion generadas.",
                metadata={"companies": [cl["company"] for cl in cover_letters]},
            )
        ]

        self._set_progress(100)
        self._set_status("completed")
        self.log(f"{len(cover_letters)} cartas generadas.")

        return AgentResult.ok(
            progress=100,
            recommendations=recommendations,
            events=events,
            memory_updates={SharedMemoryKey.COVER_LETTERS: cover_letters},
        )


def _generate_cover_letter(job: dict, mission, skills: list) -> str:
    """Genera una carta de presentacion (Fase 3: template. Fase 4+: LLM)."""
    skills_str = ", ".join(skills[:4]) if skills else "software development"
    return (
        f"Dear {job['company']} Team,\n\n"
        f"I am writing to express my strong interest in the {job['title']} position at {job['company']}. "
        f"With expertise in {skills_str}, I am confident in my ability to contribute meaningfully to your team.\n\n"
        f"My career goal of {mission.career_goal} aligns perfectly with {job['company']}'s mission and values. "
        f"I am particularly excited about this opportunity because of the company's innovative approach to technology.\n\n"
        f"I look forward to the opportunity to discuss how my background can benefit your team.\n\n"
        f"Best regards,\n[Your Name]"
    )
