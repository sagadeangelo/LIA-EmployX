"""
LIA EmployX — InterviewCoach
Responsabilidad UNICA: Preparar al candidato para entrevistas basadas en las vacantes encontradas.
"""
from __future__ import annotations
from typing import List

from backend.agents.base.base_agent import BaseAgent, AgentMetadata
from backend.agents.base.agent_context import AgentContext
from backend.agents.base.agent_result import AgentResult
from backend.agents.base.shared_memory import SharedMemoryKey
from backend.modules.mission.models import MissionEvent, MissionEventType


class InterviewCoach(BaseAgent):

    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            id="interview_coach",
            name="Interview Coach",
            version="1.0.0",
            author="LIA Team",
            description="Prepara al candidato para entrevistas tecnicas y de comportamiento basadas en las vacantes.",
            capabilities=["interview_preparation", "technical_interview", "behavioral_interview"],
            dependencies=["job_hunter"],
            priority=70,
            enabled=True,
        )

    def can_execute(self, context: AgentContext) -> bool:
        return context.shared_memory.contains(SharedMemoryKey.TOP_JOBS)

    async def execute(self, context: AgentContext) -> AgentResult:
        self._set_status("running")
        self.log("Preparando plan de entrevistas...")

        mission = context.mission
        skills = context.shared_memory.get(SharedMemoryKey.SKILLS, [])
        top_jobs = context.shared_memory.get(SharedMemoryKey.TOP_JOBS, [])
        target_role = mission.target_position or "Senior Engineer"

        questions = _generate_interview_questions(skills, target_role)
        interview_plan = {
            "technical_questions": questions["technical"],
            "behavioral_questions": questions["behavioral"],
            "preparation_tips": questions["tips"],
            "target_companies": [j["company"] for j in top_jobs[:3]],
        }

        recommendations = [
            f"Plan de entrevista creado para {len(top_jobs)} empresas.",
            f"Preguntas tecnicas generadas: {len(questions['technical'])}",
            "Practica respuestas con el metodo STAR para preguntas de comportamiento.",
        ]

        events = [
            MissionEvent(
                mission_id=mission.id,
                type=MissionEventType.INTERVIEW_SCHEDULED,
                source="InterviewCoach",
                title="Plan de entrevistas generado",
                description="Plan de preparacion de entrevistas generado.",
                metadata={"companies": interview_plan["target_companies"]},
            )
        ]

        self._set_progress(100)
        self._set_status("completed")
        self.log("Plan de entrevistas completado.")

        return AgentResult.ok(
            progress=100,
            recommendations=recommendations,
            events=events,
            memory_updates={
                SharedMemoryKey.INTERVIEW_PLAN: interview_plan,
                SharedMemoryKey.INTERVIEW_QUESTIONS: questions["technical"],
            },
        )


def _generate_interview_questions(skills: list, target_role: str) -> dict:
    role_lower = target_role.lower()
    
    if "flutter" in role_lower:
        technical = [
            "Explica el ciclo de vida de un Widget en Flutter.",
            "Diferencias entre StatelessWidget y StatefulWidget.",
            "Como implementas BLoC o Provider para manejo de estado?",
            "Como optimizas el rendimiento de una lista grande en Flutter?",
            "Explica el concepto de Keys en Flutter y cuando los usas.",
        ]
    elif "python" in role_lower or "backend" in role_lower:
        technical = [
            "Explica las diferencias entre async/await y threading en Python.",
            "Como diseñarias una API REST con FastAPI para alta concurrencia?",
            "Que es un ORM y cuales son sus ventajas y desventajas?",
            "Como implementas caching en un sistema de alta demanda?",
            "Explica el patron Repository y por que lo usarias.",
        ]
    else:
        technical = [
            f"Explica tu experiencia con {skills[0] if skills else 'tu stack principal'}.",
            "Describe un proyecto complejo que hayas liderado.",
            "Como manejas conflictos tecnicos en el equipo?",
            "Que es SOLID y como lo aplicas en tu trabajo diario?",
            "Describe tu proceso de code review.",
        ]

    behavioral = [
        "Cuentame de un proyecto fallido y que aprendiste.",
        "Como priorizas tareas cuando tienes multiples deadlines?",
        "Describe una situacion donde discrepaste con tu lider tecnico.",
        "Como mantienes tu conocimiento tecnico actualizado?",
        "Que significa para ti el codigo de calidad?",
    ]

    tips = [
        "Usa el metodo STAR: Situacion, Tarea, Accion, Resultado.",
        "Prepara preguntas inteligentes para los entrevistadores.",
        "Investiga la cultura y productos de cada empresa.",
        "Practica coding en voz alta explicando tu razonamiento.",
    ]

    return {"technical": technical, "behavioral": behavioral, "tips": tips}
