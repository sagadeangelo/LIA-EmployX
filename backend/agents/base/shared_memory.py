"""
LIA EmployX — Agent Collaboration Engine
Layer 1: SharedMemory (Tipada con Enum de Claves)

La memoria compartida entre agentes. Los agentes la leen pero nunca la
modifican directamente. Solo el MissionController aplica cambios via AgentResult.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional


class SharedMemoryKey(str, Enum):
    """
    Claves tipadas para SharedMemory.
    Todo acceso a la memoria compartida debe usar este Enum.
    Esto elimina errores de escritura y hace el código auto-documentado.
    """
    # Perfil del candidato
    SKILLS             = "skills"
    SKILL_GAPS         = "skill_gaps"
    CAREER_STRATEGY    = "career_strategy"
    TARGET_COMPANIES   = "target_companies"
    TARGET_ROLES       = "target_roles"

    # Análisis del CV
    CV_KEYWORDS        = "cv_keywords"
    CV_SCORE           = "cv_score"
    CV_IMPROVEMENTS    = "cv_improvements"
    CV_STRUCTURE       = "cv_structure"

    # ATS
    ATS_SCORE          = "ats_score"
    MISSING_KEYWORDS   = "missing_keywords"
    ATS_COMPATIBILITY  = "ats_compatibility"

    # Vacantes
    JOB_MATCHES        = "job_matches"
    TOP_JOBS           = "top_jobs"

    # LinkedIn
    LINKEDIN_PROFILE   = "linkedin_profile"
    LINKEDIN_SCORE     = "linkedin_score"

    # Documentos generados
    COVER_LETTERS      = "cover_letters"

    # Entrevista
    INTERVIEW_PLAN     = "interview_plan"
    INTERVIEW_QUESTIONS = "interview_questions"

    # Negociación
    SALARY_STRATEGY    = "salary_strategy"
    MARKET_SALARY_DATA = "market_salary_data"


class SharedMemory:
    """
    Almacenamiento key-value compartido entre agentes durante un ciclo de misión.

    IMPORTANTE: Los agentes NUNCA modifican SharedMemory directamente.
    Solo devuelven un AgentResult con 'memory_updates', y el MissionController
    aplica esos cambios. Esto garantiza inmutabilidad del contexto desde la
    perspectiva del agente.
    """

    def __init__(self, initial: Optional[Dict[Any, Any]] = None):
        self._store: Dict[str, Any] = {}
        if initial:
            for key, value in initial.items():
                if isinstance(key, SharedMemoryKey):
                    self._store[key.value] = value
                else:
                    self._store[key] = value

    def put(self, key: SharedMemoryKey, value: Any) -> None:
        self._store[key.value] = value

    def get(self, key: SharedMemoryKey, default: Any = None) -> Any:
        return self._store.get(key.value, default)

    def remove(self, key: SharedMemoryKey) -> None:
        self._store.pop(key.value, None)

    def contains(self, key: SharedMemoryKey) -> bool:
        return key.value in self._store

    def snapshot(self) -> Dict[str, Any]:
        """Devuelve una copia del estado actual. Útil para logging y debugging."""
        return dict(self._store)

    def merge(self, updates: Dict[SharedMemoryKey, Any]) -> "SharedMemory":
        """
        Crea una NUEVA instancia de SharedMemory con los updates aplicados.
        El MissionController usa este método para propagar resultados de un agente
        al siguiente sin mutar el contexto original.
        """
        new_store = dict(self._store)
        for key, value in updates.items():
            new_store[key.value] = value
        new_instance = SharedMemory()
        new_instance._store = new_store
        return new_instance
