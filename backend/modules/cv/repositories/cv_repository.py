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
    """Persistent repository for canonical CV documents."""

    def __init__(self) -> None:
        if not os.path.exists(CV_DB):
            self._save([])

    def _load(self) -> List[dict]:
        try:
            with open(CV_DB, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

        return data if isinstance(data, list) else []

    def _save(self, data: List[dict]) -> None:
        with open(CV_DB, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False, default=str)

    def save(self, cv: CVDocument) -> CVDocument:
        data = self._load()
        serialized = cv.model_dump(mode="json")
        cv_id = str(serialized.get("id") or "").strip()

        replaced = False
        if cv_id:
            for index, existing in enumerate(data):
                if str(existing.get("id") or "").strip() == cv_id:
                    data[index] = serialized
                    replaced = True
                    break

        if not replaced:
            data.append(serialized)

        self._save(data)
        return cv

    def get_by_id(self, cv_id: str) -> Optional[CVDocument]:
        normalized_id = cv_id.strip()
        if not normalized_id:
            return None

        for item in self._load():
            if str(item.get("id") or "").strip() == normalized_id:
                try:
                    return CVDocument.model_validate(item)
                except Exception:
                    return None

        return None

    def get_all(self, user_id: Optional[str] = None) -> List[CVDocument]:
        normalized_user_id = (user_id or "").strip()
        result: List[CVDocument] = []

        for item in self._load():
            if normalized_user_id:
                item_user_id = str(item.get("user_id") or "").strip()
                if item_user_id and item_user_id != normalized_user_id:
                    continue

            try:
                result.append(CVDocument.model_validate(item))
            except Exception:
                continue

        result.sort(key=lambda cv: cv.updated_at, reverse=True)
        return result

    def delete(self, cv_id: str) -> bool:
        normalized_id = cv_id.strip()
        if not normalized_id:
            return False

        data = self._load()
        remaining = [
            item
            for item in data
            if str(item.get("id") or "").strip() != normalized_id
        ]

        if len(remaining) == len(data):
            return False

        self._save(remaining)
        return True
