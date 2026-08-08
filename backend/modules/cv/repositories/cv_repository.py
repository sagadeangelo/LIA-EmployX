import json
import os
from typing import List, Optional
from datetime import datetime
from backend.modules.cv.models.cv_document import CVDocument

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data")
os.makedirs(DB_DIR, exist_ok=True)
CV_DB = os.path.join(DB_DIR, "cvs.json")

class CVRepository:
    def __init__(self):
        if not os.path.exists(CV_DB):
            with open(CV_DB, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _load(self) -> List[dict]:
        with open(CV_DB, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: List[dict]):
        with open(CV_DB, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def save(self, cv: CVDocument) -> CVDocument:
        data = self._load()

        # Use Pydantic's model_dump to recursively serialize all nested models
        # (e.g. CVMetadata) and coerce datetimes to ISO strings for JSON storage.
        cv_dict = cv.model_dump(mode="json")

        data.append(cv_dict)
        self._save(data)
        return cv
