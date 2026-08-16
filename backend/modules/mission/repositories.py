import logging
from typing import List, Optional
from datetime import datetime
from .models import Mission, MissionEvent
from backend.storage.provider import StorageProvider
from backend.runtime.pipeline import MissionPipeline

class MissionRepository:
    def __init__(self, storage: StorageProvider):
        self.storage = storage

    def save(self, mission: Mission) -> Mission:
        mission.updated_at = datetime.utcnow()
        # Automatically update progress based on current_step
        mission.progress = MissionPipeline.get_progress(mission.current_step)

        mission_dict = mission.model_dump()
        self.storage.save_mission(mission_dict)
        return mission

    def get_by_id(self, mission_id: str) -> Optional[Mission]:
        data = self.storage.get_mission(mission_id)
        if data:
            return Mission(**data)
        return None

    def get_all(self) -> List[Mission]:
        data = self.storage.list_missions()
        return [Mission(**m) for m in data]

class MissionEventRepository:
    def __init__(self, storage: StorageProvider):
        self.storage = storage

    def save(self, event: MissionEvent) -> MissionEvent:
        self.storage.save_event(event.model_dump())
        return event

    def get_by_mission(self, mission_id: str) -> List[MissionEvent]:
        data = self.storage.get_mission_events(mission_id)
        events = [MissionEvent(**e) for e in data]
        events.sort(key=lambda x: x.timestamp)
        return events

