"""
LIA EmployX — ATSAnalyzer
Responsabilidad EXCLUSIVA: Score ATS, keywords gap, compatibilidad con sistemas ATS.
Separado del CVExpert. No analiza estructura ni contenido narrativo del CV.
"""
from __future__ import annotations

from backend.agents.base.base_agent import BaseAgent, AgentMetadata
from backend.agents.base.agent_context import AgentContext
from backend.agents.base.agent_result import AgentResult
from backend.agents.base.shared_memory import SharedMemoryKey
from backend.agents.llm.llm_provider import LLMProvider
from backend.modules.mission.models import MissionEvent, MissionEventType
from backend.modules.profile.repositories.profile_repository import ProfileRepository


class ATSAnalyzer(BaseAgent):

    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            id="ats_analyzer",
            name="ATS Analyzer",
            version="1.0.0",
            author="LIA Team",
            description="Calcula el score ATS, detecta keywords faltantes y evalua compatibilidad con sistemas ATS.",
            capabilities=["ats_score", "keyword_gap_analysis", "ats_compatibility"],
            dependencies=["cv_expert"],
            priority=30,
            enabled=True,
        )

    def can_execute(self, context: AgentContext) -> bool:
        return context.mission.state.profile_id is not None

    async def execute(self, context: AgentContext) -> AgentResult:
        self._set_status("running")
        self.log("Calculando score ATS...")

        profile_id = context.mission.state.profile_id
        
        repo = ProfileRepository()
        profile = repo.get_by_id(profile_id) if profile_id else None
        
        cv_keywords = profile.cv_keywords if profile else []
        target_role = context.mission.target_position or "Software Engineer"
        cv_score = profile.cv_score if profile else 60

        required_keywords = _get_required_keywords(target_role)
        missing_keywords = [kw for kw in required_keywords if kw not in cv_keywords]
        present_keywords = [kw for kw in required_keywords if kw in cv_keywords]

        coverage = len(present_keywords) / max(len(required_keywords), 1)
        ats_score = int(cv_score * 0.5 + coverage * 50)
        compatibility = _assess_compatibility(ats_score)

        recommendations = [
            f"Score ATS: {ats_score}/100 ({compatibility})",
            f"Keywords presentes: {len(present_keywords)}/{len(required_keywords)}",
        ]
        if missing_keywords:
            recommendations.append(
                f"Agrega estas keywords criticas al CV: {', '.join(missing_keywords[:5])}"
            )

        events = [
            MissionEvent(
                mission_id=context.mission.id,
                type=MissionEventType.ATS_COMPLETED,
                source="ATSAnalyzer",
                title="ATS Score calculado",
                description=f"ATS Score calculado: {ats_score}/100. Keywords faltantes: {len(missing_keywords)}.",
                metadata={"ats_score": ats_score, "missing": missing_keywords, "present": present_keywords},
            )
        ]

        self._set_progress(100)
        self._set_status("completed")
        self.log(f"ATS Score: {ats_score}/100.")

        if profile:
            profile.ats_metrics.ats_score = ats_score
            profile.ats_metrics.missing_keywords = missing_keywords
            profile.ats_metrics.compatibility = compatibility
            repo.save(profile)

        return AgentResult.ok(
            progress=100,
            recommendations=recommendations,
            events=events,
            memory_updates={}
        )


def _get_required_keywords(target_role: str) -> list:
    role_lower = target_role.lower()
    if "flutter" in role_lower:
        return ["flutter", "dart", "firebase", "provider", "ci/cd", "git", "rest api", "agile"]
    if "python" in role_lower or "backend" in role_lower:
        return ["python", "fastapi", "postgresql", "docker", "redis", "git", "rest api", "agile", "sql"]
    if "ai" in role_lower or "machine learning" in role_lower:
        return ["python", "pytorch", "tensorflow", "langchain", "sql", "git", "mlops", "api"]
    return ["python", "sql", "git", "rest api", "agile", "docker", "ci/cd"]


def _assess_compatibility(ats_score: int) -> str:
    if ats_score >= 80:
        return "Alta compatibilidad ATS"
    if ats_score >= 60:
        return "Compatibilidad media - mejorable"
    return "Baja compatibilidad ATS - accion urgente"
