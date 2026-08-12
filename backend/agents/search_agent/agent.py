"""
LIA EmployX — JobHunter
Responsabilidad: Buscar vacantes, calcular afinidad, priorizar oportunidades.
NO modifica documentos. NO calcula ATS.
"""
from __future__ import annotations
from typing import List

from backend.agents.base.base_agent import BaseAgent, AgentMetadata
from backend.agents.base.agent_context import AgentContext
from backend.agents.base.agent_result import AgentResult
from backend.agents.base.shared_memory import SharedMemoryKey
from backend.modules.mission.models import MissionEvent, MissionEventType


class JobHunter(BaseAgent):

    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            id="job_hunter",
            name="Job Hunter",
            version="1.0.0",
            author="LIA Team",
            description="Busca vacantes relevantes, calcula afinidad con el perfil y prioriza oportunidades.",
            capabilities=["job_search", "match_scoring", "opportunity_ranking"],
            dependencies=["career_agent"],
            priority=40,
            enabled=True,
        )

    def can_execute(self, context: AgentContext) -> bool:
        return context.shared_memory.contains(SharedMemoryKey.SKILLS)

    async def execute(self, context: AgentContext) -> AgentResult:
        self._set_status("running")
        self.log("Buscando vacantes relevantes...")

        mission = context.mission
        skills = context.shared_memory.get(SharedMemoryKey.SKILLS, [])
        target_companies = context.shared_memory.get(SharedMemoryKey.TARGET_COMPANIES, [])
        target_roles = context.shared_memory.get(SharedMemoryKey.TARGET_ROLES, ["Software Engineer"])
        ats_score = context.shared_memory.get(SharedMemoryKey.ATS_SCORE, 70)

        job_matches = _simulate_job_search(skills, target_companies, target_roles, mission.remote)
        top_jobs = sorted(job_matches, key=lambda j: j["match_score"], reverse=True)[:5]

        recommendations = [
            f"Encontradas {len(job_matches)} vacantes compatibles.",
        ]
        if top_jobs:
            recommendations.append(
                f"Top match: {top_jobs[0]['company']} - {top_jobs[0]['title']} ({top_jobs[0]['match_score']}%)"
            )
        if ats_score < 70:
            recommendations.append("Mejora tu ATS score antes de aplicar para aumentar tasas de respuesta.")

        events = [
            MissionEvent(
                mission_id=mission.id,
                type=MissionEventType.JOBS_FOUND,
                source="JobHunter",
                title="Vacantes encontradas",
                description=f"{len(job_matches)} vacantes encontradas.",
                metadata={"total": len(job_matches), "top_jobs": top_jobs},
            )
        ]

        self._set_progress(100)
        self._set_status("completed")
        self.log(f"{len(job_matches)} vacantes encontradas.")

        return AgentResult.ok(
            progress=100,
            recommendations=recommendations,
            events=events,
            memory_updates={
                SharedMemoryKey.JOB_MATCHES: job_matches,
                SharedMemoryKey.TOP_JOBS: top_jobs,
            },
        )


def _simulate_job_search(skills: list, companies: list, roles: list, remote: bool) -> List[dict]:
    """Simula busqueda de vacantes (Fase 3). Fase 4+: conectar a APIs reales."""
    DEFAULT_COMPANIES = ["Google", "Microsoft", "Stripe", "Notion", "Vercel", "Linear", "Shopify"]
    search_companies = companies if companies else DEFAULT_COMPANIES
    role = roles[0] if roles else "Software Engineer"
    jobs = []
    for i, company in enumerate(search_companies[:8]):
        match = max(50, 95 - i * 5)
        jobs.append({
            "id": f"job_{i+1}",
            "company": company,
            "title": f"Senior {role}",
            "location": "Remote" if remote else "San Francisco, CA",
            "remote": remote,
            "salary_min": 120000 + i * 5000,
            "salary_max": 160000 + i * 5000,
            "match_score": match,
            "required_skills": skills[:4] if skills else ["Python", "SQL"],
            "url": f"https://careers.{company.lower()}.com/job_{i+1}",
        })
    return jobs
