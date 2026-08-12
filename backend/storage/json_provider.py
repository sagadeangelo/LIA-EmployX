import json
import os
from typing import List, Optional, Dict, Any
from .provider import StorageProvider

class JsonStorageProvider(StorageProvider):
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.mission_file = os.path.join(self.data_dir, "missions.json")
        self.event_file = os.path.join(self.data_dir, "events.json")
        
        # Initialize files if they don't exist
        for file_path in [self.mission_file, self.event_file]:
            if not os.path.exists(file_path):
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump([], f)
                    
    def _load(self, file_path: str) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    def _save(self, file_path: str, data: List[Dict[str, Any]]) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def save_mission(self, mission_data: Dict[str, Any]) -> None:
        import logging as _logging
        _diag = _logging.getLogger("DIAG")

        data = self._load(self.mission_file)
        mission_id = mission_data.get("id")
        existing = next((i for i, m in enumerate(data) if m.get("id") == mission_id), None)

        if existing is not None:
            data[existing] = mission_data
        else:
            data.append(mission_data)

        # ── PUNTO 4b ────────────────────────────────────────────────
        _cv = mission_data.get("shared_memory", {}).get("cv_document", {})
        _diag.info(
            "PRE_WRITE    metadata=%s",
            _cv.get("metadata") if isinstance(_cv, dict) else f"TYPE={type(_cv)}",
        )
        # ────────────────────────────────────────────────────────────

        self._save(self.mission_file, data)

    def get_mission(self, mission_id: str) -> Optional[Dict[str, Any]]:
        data = self._load(self.mission_file)
        return next((m for m in data if m.get("id") == mission_id), None)

    def list_missions(self) -> List[Dict[str, Any]]:
        return self._load(self.mission_file)

    def save_event(self, event_data: Dict[str, Any]) -> None:
        data = self._load(self.event_file)
        data.append(event_data)
        self._save(self.event_file, data)

    def get_mission_events(self, mission_id: str) -> List[Dict[str, Any]]:
        data = self._load(self.event_file)
        return [e for e in data if e.get("mission_id") == mission_id]
