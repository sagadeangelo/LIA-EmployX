"""
LIA EmployX — CareerAgent
Responsabilidad: Analizar objetivo profesional, detectar skill gaps y definir estrategia.
NO modifica el CV. NO busca vacantes.
"""
from __future__ import annotations

from backend.agents.base.base_agent import BaseAgent, AgentMetadata
from backend.agents.base.agent_context import AgentContext
from backend.agents.base.agent_result import AgentResult
from backend.agents.base.shared_memory import SharedMemoryKey
from backend.agents.llm.llm_provider import LLMProvider
from backend.modules.mission.models import MissionEvent, MissionEventType
from backend.modules.profile.repositories.profile_repository import ProfileRepository


class CareerAgent(BaseAgent):

    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            id="career_agent",
            name="Career Agent",
            version="1.0.0",
            author="LIA Team",
            description="Analiza el objetivo profesional, detecta skill gaps y define la estrategia de carrera.",
            capabilities=["goal_analysis", "skill_gap_detection", "strategy_planning", "company_prioritization"],
            dependencies=[],
            priority=10,
            enabled=True,
        )

    def can_execute(self, context: AgentContext) -> bool:
        # Siempre puede ejecutar — es el primer agente del pipeline
        return True

    async def execute(self, context: AgentContext) -> AgentResult:
        self._set_status("running")
        self.log("Analizando objetivo profesional...")

        mission = context.mission

        # --- Lógica determinista (Fase 3) ---
        # En Fase 4+ esto usará self._llm.extract() sobre el career_goal

        # 1. Detectar skills actuales inferidos del goal
        detected_skills = _infer_skills_from_goal(mission.career_goal)

        # 2. Detectar skill gaps según el target_position
        skill_gaps = _compute_skill_gaps(detected_skills, mission.target_position)

        # 3. Definir estrategia
        strategy = _build_strategy(mission)

        # 4. Priorizar empresas
        target_companies = (
            [mission.target_company] if mission.target_company else ["OpenAI", "Google", "Microsoft", "Stripe"]
        )

        # --- Construir resultado acumulativo ---
        recommendations = [
            f"Refuerza estas habilidades: {', '.join(skill_gaps[:3])}",
            f"Estrategia principal: {strategy}",
            f"Empresas priorizadas: {', '.join(target_companies[:3])}",
        ]

        events = [
            MissionEvent(
                mission_id=mission.id,
                type=MissionEventType.MISSION_CREATED,
                source="CareerAgent",
                title="Career Agent completado",
                description="Career Agent completó análisis de objetivo profesional.",
                metadata={"skills": detected_skills, "gaps": skill_gaps},
            )
        ]

        self._set_progress(100)
        self._set_status("completed")
        self.log("Análisis completado.")

        profile_id = mission.state.profile_id
        if profile_id:
            repo = ProfileRepository()
            profile = repo.get_by_id(profile_id)
            if profile:
                profile.career_metrics.strengths = detected_skills
                profile.career_metrics.weaknesses = skill_gaps
                profile.career_metrics.areas_for_improvement = [f"Focus on {gap}" for gap in skill_gaps]
                profile.career_metrics.employability_level = "High" if len(skill_gaps) < 3 else "Medium"
                
                # also we can update skills list if we want
                profile.skills.technical_skills.extend([s for s in detected_skills if s not in profile.skills.technical_skills])
                
                repo.save(profile)
        return AgentResult.ok(
            progress=100,
            recommendations=recommendations,
            events=events,
            memory_updates={
                SharedMemoryKey.SKILLS: detected_skills,
                SharedMemoryKey.TARGET_ROLES: [mission.target_position]
                if mission.target_position
                else ["Software Engineer"],
            },
        )


# --- Funciones de lógica determinista ---

def _infer_skills_from_goal(career_goal: str) -> list:
    """Infiere habilidades del texto del objetivo profesional."""
    SKILL_KEYWORDS = {
        "flutter": "Flutter", "dart": "Dart", "python": "Python",
        "fastapi": "FastAPI", "ai": "AI/ML", "machine learning": "Machine Learning",
        "sql": "SQL", "aws": "AWS", "docker": "Docker", "kubernetes": "Kubernetes",
        "react": "React", "node": "Node.js", "java": "Java", "kotlin": "Kotlin",
        "senior": None, "engineer": None, "developer": None,
    }
    goal_lower = career_goal.lower()
    found = [skill for kw, skill in SKILL_KEYWORDS.items() if kw in goal_lower and skill]
    return found if found else ["Python", "SQL", "Git", "REST APIs"]


def _compute_skill_gaps(current_skills: list, target_position: str | None) -> list:
    """Detecta habilidades faltantes para el target position."""
    POSITION_REQUIREMENTS = {
        "flutter": ["Flutter", "Dart", "Firebase", "BLoC/Provider", "CI/CD"],
        "backend": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"],
        "ai": ["Python", "PyTorch", "LangChain", "Vector DBs", "MLOps"],
        "fullstack": ["React", "Node.js", "PostgreSQL", "Docker", "AWS"],
    }
    if not target_position:
        required = ["Docker", "CI/CD", "System Design", "Agile"]
    else:
        pos_lower = target_position.lower()
        required = next(
            (reqs for key, reqs in POSITION_REQUIREMENTS.items() if key in pos_lower),
            ["Docker", "CI/CD", "System Design"]
        )
    return [skill for skill in required if skill not in current_skills]


def _build_strategy(mission) -> str:
    if mission.remote:
        return "Aplicar a posiciones 100% remotas en empresas US/EU con portfolio visible en GitHub."
    if mission.deadline:
        days = (mission.deadline - __import__("datetime").datetime.utcnow()).days
        return f"Campaña agresiva de {days} días enfocada en {mission.target_position or 'el rol objetivo'}."
    return "Búsqueda sistemática combinando LinkedIn, networking y aplicación directa a empresas."
