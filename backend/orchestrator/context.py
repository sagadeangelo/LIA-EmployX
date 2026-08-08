"""
Contexto compartido entre todos los especialistas.
Ahora respaldado por una Misión persistente.
"""

from typing import Any
from backend.modules.mission.models import Mission


class EmployXContext:
    def __init__(self, mission: Mission):
        self.mission = mission

    # Legacy properties mapped to mission metadata-backed state for backward compatibility
    @property
    def user(self):
        return self.mission.metadata.get("shared_memory", {}).get("user")

    @user.setter
    def user(self, val):
        self._shared_memory()["user"] = val

    @property
    def profile(self):
        return self.mission.metadata.get("shared_memory", {}).get("profile")

    @profile.setter
    def profile(self, val):
        self._shared_memory()["profile"] = val

    @property
    def jobs(self):
        shared_memory = self._shared_memory()
        if "jobs" not in shared_memory:
            shared_memory["jobs"] = []
        return shared_memory["jobs"]

    @property
    def timeline(self):
        return self.mission.timeline

    # --------------------------------------------------------

    def add_event(self, message: str):
        self.mission.timeline.append(message)
        print(f"[TIMELINE] {message}")

    # --------------------------------------------------------

    def set(self, key: str, value: Any):
        self._shared_memory()[key] = value

    # --------------------------------------------------------

    def get(self, key: str, default: Any = None) -> Any:
        return self._shared_memory().get(key, default)

    def _shared_memory(self) -> dict[str, Any]:
        shared_memory = self.mission.metadata.setdefault("shared_memory", {})
        if not isinstance(shared_memory, dict):
            shared_memory = {}
            self.mission.metadata["shared_memory"] = shared_memory
        return shared_memory
