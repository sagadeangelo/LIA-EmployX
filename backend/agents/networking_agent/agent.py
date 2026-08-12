"""
LIA EmployX — LinkedInOptimizer
Responsabilidad UNICA: Optimizar el perfil de LinkedIn del candidato.
"""
from __future__ import annotations

from backend.agents.base.base_agent import BaseAgent, AgentMetadata
from backend.agents.base.agent_context import AgentContext
from backend.agents.base.agent_result import AgentResult
from backend.agents.base.shared_memory import SharedMemoryKey
from backend.modules.mission.models import MissionEvent, MissionEventType
from backend.modules.profile.repositories.profile_repository import ProfileRepository


class LinkedInOptimizer(BaseAgent):

    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            id="linkedin_agent",
            name="LinkedIn Optimizer",
            version="1.0.0",
            author="LIA Team",
            description="Genera recomendaciones para optimizar el perfil de LinkedIn del candidato.",
            capabilities=["linkedin_profile_optimization", "linkedin_scoring"],
            dependencies=[],
            priority=50,
            enabled=True,
        )

    def can_execute(self, context: AgentContext) -> bool:
        return True  # Siempre puede ejecutar

    async def execute(self, context: AgentContext) -> AgentResult:
        self._set_status("running")
        self.log("Optimizando perfil de LinkedIn...")

        mission = context.mission
        profile_id = mission.state.profile_id
        
        repo = ProfileRepository()
        profile = repo.get_by_id(profile_id) if profile_id else None

        skills = []
        if profile and profile.skills:
            skills = profile.skills.technical_skills
            
        target_role = context.mission.target_position or "Senior Engineer"

        profile_recs = _generate_linkedin_recommendations(skills, target_role, mission.remote)
        profile_score = _calculate_profile_score(skills)

        recommendations = [
            f"LinkedIn Score estimado: {profile_score}/100",
            *profile_recs[:3],
        ]

        events = [
            MissionEvent(
                mission_id=mission.id,
                type=MissionEventType.MISSION_COMPLETED,
                source="LinkedInOptimizer",
                title="LinkedIn analizado",
                description=f"LinkedIn analizado. Score estimado: {profile_score}/100.",
                metadata={"score": profile_score, "recommendations": profile_recs},
            )
        ]

        self._set_progress(100)
        self._set_status("completed")
        self.log(f"LinkedIn score: {profile_score}/100.")

        if profile:
            profile.linkedin_metrics.score = profile_score
            profile.linkedin_metrics.recommendations = profile_recs
            profile.linkedin_metrics.profile_level = "Intermediate" if profile_score < 80 else "Advanced"
            repo.save(profile)

        return AgentResult.ok(
            progress=100,
            recommendations=recommendations,
            events=events,
            memory_updates={},
        )


def _generate_linkedin_recommendations(skills: list, target_role: str, remote: bool) -> list:
    recs = [
        f"Actualiza tu headline a: '{target_role} | Open to Remote Opportunities'." if remote else f"Actualiza tu headline a: '{target_role}'.",
        "Agrega una foto profesional con fondo neutro.",
        "Completa la sección 'About' con tus logros cuantificados.",
        f"Agrega estas skills a tu perfil: {', '.join(skills[:5])}." if skills else "Agrega habilidades tecnicas relevantes.",
        "Activa 'Open to Work' con las posiciones de interes.",
        "Solicita al menos 3 recomendaciones de colegas o superiores.",
    ]
    return recs


def _calculate_profile_score(skills: list) -> int:
    base = 50
    base += min(len(skills) * 5, 30)  # Hasta 30 pts por skills
    base += 10  # Bonus base
    return min(base, 100)
