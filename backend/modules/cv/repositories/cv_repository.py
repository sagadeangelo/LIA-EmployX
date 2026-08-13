import json
import os
from typing import List, Optional

from backend.modules.cv.models.cv_document import CVDocument

DB_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(__file__)
            )
        )
    ),
    "data",
)
os.makedirs(DB_DIR, exist_ok=True)
CV_DB = os.path.join(DB_DIR, "cvs.json")


class CVRepository:
    """JSON persistence for canonical CV documents."""

    def __init__(self) -> None:
        if not os.path.exists(CV_DB):
            with open(CV_DB, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _load(self) -> List[dict]:
        with open(CV_DB, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: List[dict]) -> None:
        with open(CV_DB, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    def save(self, cv: CVDocument) -> CVDocument:
        """Upsert a CV by its stable document id."""
        data = self._load()
        cv_dict = cv.model_dump(mode="json")

        for index, existing in enumerate(data):
            if existing.get("id") == cv.id:
                data[index] = cv_dict
                self._save(data)
                return cv

        data.append(cv_dict)
        self._save(data)
        return cv

    def get_by_id(self, cv_id: str) -> Optional[CVDocument]:
        for item in self._load():
            if item.get("id") == cv_id:
                return CVDocument.model_validate(item)
        return None

    def get_all(self, user_id: str = "temp_user") -> List[CVDocument]:
        """Return CVs belonging to the requested user, newest first."""
        documents = [
            CVDocument.model_validate(item)
            for item in self._load()
            if item.get("user_id", "temp_user") == user_id
        ]
        documents.sort(
            key=lambda document: document.metadata.uploaded_at,
            reverse=True,
        )
        return documents
