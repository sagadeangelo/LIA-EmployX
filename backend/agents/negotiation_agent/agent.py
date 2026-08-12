"""
LIA EmployX — NegotiationCoach
Responsabilidad UNICA: Preparar estrategia de negociacion salarial basada en vacantes encontradas.
"""
from __future__ import annotations

from backend.agents.base.base_agent import BaseAgent, AgentMetadata
from backend.agents.base.agent_context import AgentContext
from backend.agents.base.agent_result import AgentResult
from backend.agents.base.shared_memory import SharedMemoryKey
from backend.modules.mission.models import MissionEvent, MissionEventType


class NegotiationCoach(BaseAgent):

    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            id="negotiation_coach",
            name="Negotiation Coach",
            version="1.0.0",
            author="LIA Team",
            description="Prepara la estrategia de negociacion salarial con datos de mercado y tactcas probadas.",
            capabilities=["salary_negotiation", "market_analysis", "offer_evaluation"],
            dependencies=["job_hunter"],
            priority=80,
            enabled=True,
        )

    def can_execute(self, context: AgentContext) -> bool:
        return context.shared_memory.contains(SharedMemoryKey.TOP_JOBS)

    async def execute(self, context: AgentContext) -> AgentResult:
        self._set_status("running")
        self.log("Preparando estrategia de negociacion...")

        mission = context.mission
        top_jobs = context.shared_memory.get(SharedMemoryKey.TOP_JOBS, [])
        skills = context.shared_memory.get(SharedMemoryKey.SKILLS, [])

        # Calcular rango salarial de mercado a partir de las vacantes encontradas
        salaries = [j.get("salary_max", 0) for j in top_jobs if j.get("salary_max")]
        market_max = max(salaries) if salaries else 150000
        market_min = min([j.get("salary_min", 0) for j in top_jobs if j.get("salary_min")]) if top_jobs else 100000
        target_salary = mission.salary_goal or market_max
        
        strategy = _build_negotiation_strategy(target_salary, market_min, market_max, skills)

        recommendations = [
            f"Rango de mercado detectado: ${market_min:,.0f} - ${market_max:,.0f} USD/año",
            f"Salario objetivo: ${target_salary:,.0f} USD",
            *strategy[:3],
        ]

        events = [
            MissionEvent(
                mission_id=mission.id,
                type=MissionEventType.OFFER_RECEIVED,
                source="NegotiationCoach",
                title="Estrategia de negociación preparada",
                description=f"Estrategia de negociacion preparada. Objetivo: ${target_salary:,.0f}.",
                metadata={"market_min": market_min, "market_max": market_max, "target": target_salary},
            )
        ]

        self._set_progress(100)
        self._set_status("completed")
        self.log("Estrategia de negociacion completada.")

        return AgentResult.ok(
            progress=100,
            recommendations=recommendations,
            events=events,
            memory_updates={
                SharedMemoryKey.SALARY_STRATEGY: strategy,
                SharedMemoryKey.MARKET_SALARY_DATA: {
                    "min": market_min,
                    "max": market_max,
                    "target": target_salary,
                },
            },
        )


def _build_negotiation_strategy(target: float, market_min: float, market_max: float, skills: list) -> list:
    tactics = [
        f"Pide un {int((target / market_max - 1) * 100 + 15)}% sobre el promedio de mercado como ancla inicial.",
        "Negocia el total compensation: salario base + equity + bonos + beneficios.",
        "No des una cifra primero. Haz que la empresa haga la primera oferta.",
        "Usa ofertas competitivas de otras empresas como palanca de negociacion.",
        "Si no pueden llegar al salario, negocia dias de PTO, trabajo remoto o equity adicional.",
    ]
    if len(skills) >= 5:
        tactics.insert(0, f"Tu stack ({', '.join(skills[:3])}) tiene alta demanda. Tienes poder de negociacion.")
    return tactics
