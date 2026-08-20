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


from backend.api.routes.jobs_proxy import fetch_freehire_payload

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
        target_roles = context.shared_memory.get(SharedMemoryKey.TARGET_ROLES, ["Software Engineer"])
        ats_score = context.shared_memory.get(SharedMemoryKey.ATS_SCORE, 70)

        try:
            job_matches = await _fetch_real_jobs(skills, target_roles)
        except Exception as e:
            self.log(f"Error consultando vacantes: {e}")
            return AgentResult.failure(f"Error consultando FreeHire: {e}")

        # Como el match_score ya no se inventa (es None), simplemente tomamos los primeros 5
        top_jobs = job_matches[:5]

        recommendations = [
            f"Encontradas {len(job_matches)} vacantes compatibles.",
        ]
        if top_jobs:
            recommendations.append(
                f"Top job: {top_jobs[0]['company']} - {top_jobs[0]['title']}"
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


async def _fetch_real_jobs(skills: list, roles: list) -> List[dict]:
    """Busca vacantes reales en FreeHire usando el proxy config."""
    q_parts = []
    if roles:
        q_parts.append(roles[0])
    if skills:
        q_parts.extend(skills[:3])
    q = " ".join(q_parts)

    params = {"q": q, "limit": 10, "offset": 0}
    payload = await fetch_freehire_payload(params)
    data = payload.get("data", [])

    jobs = []
    for j in data:
        enrichment = j.get("enrichment", {})
        jobs.append({
            "id": j.get("public_slug") or j.get("external_id") or "unknown",
            "company": j.get("company", "Empresa Confidencial"),
            "title": j.get("title", "Posición Confidencial"),
            "location": j.get("location", ""),
            "remote": j.get("work_mode", "") == "remote",
            "salary_min": enrichment.get("salary_min"),
            "salary_max": enrichment.get("salary_max"),
            "match_score": None,  # No inventar datos
            "required_skills": j.get("skills", []),
            "url": j.get("url", ""),
            "description": j.get("description", "")
        })
    return jobs
