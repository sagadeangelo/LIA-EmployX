"""
LIA EmployX — CVExpert
Responsabilidad: Analizar CV, mejorar estructura, detectar palabras clave, recomendar mejoras.
NO busca vacantes. NO calcula ATS directamente (eso es ATSAnalyzer).
"""
from __future__ import annotations

from backend.agents.base.base_agent import BaseAgent, AgentMetadata
from backend.agents.base.agent_context import AgentContext
from backend.agents.base.agent_result import AgentResult
from backend.agents.base.shared_memory import SharedMemoryKey
from backend.agents.llm.llm_provider import LLMProvider
from backend.modules.mission.models import MissionEvent, MissionEventType
from backend.modules.profile.repositories.profile_repository import ProfileRepository


class CVExpert(BaseAgent):

    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            id="cv_expert",
            name="CV Expert",
            version="1.0.0",
            author="LIA Team",
            description="Analiza el CV, mejora su estructura, detecta palabras clave y genera recomendaciones.",
            capabilities=["cv_analysis", "keyword_extraction", "structure_improvement", "cv_scoring"],
            dependencies=["career_agent"],
            priority=20,
            enabled=True,
        )

    def can_execute(self, context: AgentContext) -> bool:
        # Necesita que el CV haya sido subido y parseado
        return context.mission.state.metadata is not None

    async def execute(self, context: AgentContext) -> AgentResult:
        if not context.mission.state.metadata:
            return AgentResult.failure("No hay CV parseado disponible en el contexto.")

        self._set_status("running")
        self.log("Analizando estructura del CV...")

        profile_id = context.mission.state.profile_id
        
        repo = ProfileRepository()
        profile = repo.get_by_id(profile_id) if profile_id else None
        
        skills = profile.career_metrics.strengths if profile else []

        # --- Lógica determinista (Fase 3) ---
        sections = context.mission.state.sections or {}
        detected_keywords = _extract_keywords_from_sections(sections, skills)
        cv_score = _calculate_cv_score(sections, detected_keywords)
        improvements = _generate_improvements(sections, detected_keywords)

        recommendations = [
            f"Score actual del CV: {cv_score}/100",
            *improvements[:3],
        ]

        events = [
            MissionEvent(
                mission_id=context.mission.id,
                type=MissionEventType.CV_PARSED,
                source="CVExpert",
                title="CV analizado",
                description=f"CV analizado. Score: {cv_score}/100. Keywords detectadas: {len(detected_keywords)}.",
                metadata={"score": cv_score, "keywords": detected_keywords},
            )
        ]

        self._set_progress(100)
        self._set_status("completed")
        self.log(f"CV analizado. Score: {cv_score}/100.")

        if profile:
            profile.cv_keywords = detected_keywords
            profile.cv_score = cv_score
            profile.career_metrics.areas_for_improvement.extend(improvements)
            repo.save(profile)

        return AgentResult.ok(
            progress=100,
            recommendations=recommendations,
            events=events,
            memory_updates={}
        )


def _extract_keywords_from_sections(sections: dict, skills: list) -> list:
    """Extrae palabras clave relevantes del CV."""
    all_text = " ".join(str(v) for v in sections.values()).lower() if isinstance(sections, dict) else ""
    
    TECH_KEYWORDS = [
        "python", "flutter", "dart", "fastapi", "docker", "kubernetes", "aws",
        "react", "node", "postgresql", "redis", "git", "ci/cd", "agile", "scrum",
        "machine learning", "langchain", "tensorflow", "pytorch",
    ]
    found = [kw for kw in TECH_KEYWORDS if kw in all_text]
    # Combinar con skills ya detectadas por CareerAgent
    combined = list(set(found + [s.lower() for s in skills]))
    return combined


def _calculate_cv_score(sections: dict, keywords: list) -> int:
    """Calcula un score básico del CV."""
    score = 40  # Base
    if isinstance(sections, dict):
        section_count = len(sections)
        score += min(section_count * 8, 40)  # Hasta 40 pts por secciones
    score += min(len(keywords) * 2, 20)     # Hasta 20 pts por keywords
    return min(score, 100)


def _generate_improvements(sections: dict, keywords: list) -> list:
    """Genera recomendaciones de mejora."""
    improvements = []
    if isinstance(sections, dict):
        if "summary" not in str(sections).lower():
            improvements.append("Agrega un resumen profesional al inicio del CV.")
        if "experience" not in str(sections).lower():
            improvements.append("Asegúrate de incluir tu experiencia laboral con métricas cuantificables.")
    if len(keywords) < 8:
        improvements.append("Incluye más palabras clave técnicas relevantes a tu rol objetivo.")
    improvements.append("Usa verbos de acción en tus logros (Implementé, Lideré, Optimicé).")
    return improvements
