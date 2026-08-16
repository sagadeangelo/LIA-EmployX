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
    """
    Persistencia de CVDocument.

    La fuente de verdad de los CV persistidos es data/cvs.json.

    Cada CV pertenece a un user_id y puede estar asociado a un
    ProfessionalProfile mediante professional_profile_id.
    """

    def __init__(self) -> None:
        if not os.path.exists(CV_DB):
            self._write_all([])

    # ==========================================================
    # LOW LEVEL STORAGE
    # ==========================================================

    def _load_raw(self) -> List[dict]:
        try:
            with open(
                CV_DB,
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

            if not isinstance(data, list):
                return []

            return data

        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _write_all(self, data: List[dict]) -> None:
        temp_file = f"{CV_DB}.tmp"

        with open(
            temp_file,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False,
                default=str,
            )

        os.replace(
            temp_file,
            CV_DB,
        )

    # ==========================================================
    # CREATE / UPDATE
    # ==========================================================

    def save(
        self,
        cv: CVDocument,
    ) -> CVDocument:
        """
        Inserta o actualiza un CV.

        La identidad del CV está determinada por cv.id.
        """

        data = self._load_raw()

        cv_dict = cv.model_dump(
            mode="json"
        )

        for index, existing in enumerate(data):
            if str(existing.get("id", "")).strip() == str(cv.id).strip():
                data[index] = cv_dict
                self._write_all(data)
                return cv

        data.append(cv_dict)

        self._write_all(data)

        return cv

    # ==========================================================
    # GET BY ID
    # ==========================================================

    def get_by_id(
        self,
        cv_id: str,
    ) -> Optional[CVDocument]:
        """
        Obtiene un CV por su identificador.
        """

        cv_id = cv_id.strip()

        if not cv_id:
            return None

        for item in self._load_raw():
            if str(item.get("id", "")).strip() != cv_id:
                continue

            try:
                return CVDocument.model_validate(item)
            except Exception:
                return None

        return None

    # ==========================================================
    # GET BY USER
    # ==========================================================

    def get_by_user(
        self,
        user_id: str,
    ) -> List[CVDocument]:
        """
        Devuelve todos los CV pertenecientes al usuario.
        """

        user_id = user_id.strip()

        if not user_id:
            return []

        result: List[CVDocument] = []

        for item in self._load_raw():
            if str(item.get("user_id", "")).strip() != user_id:
                continue

            try:
                result.append(
                    CVDocument.model_validate(item)
                )
            except Exception:
                # Un CV corrupto no debe bloquear
                # la recuperación del resto.
                continue

        result.sort(
            key=lambda cv: cv.updated_at,
            reverse=True,
        )

        return result

    # ==========================================================
    # GET ALL
    # ==========================================================

    def get_all(
        self,
        user_id: Optional[str] = None,
    ) -> List[CVDocument]:
        """
        Devuelve todos los CV válidos almacenados.

        Si user_id es proporcionado, devuelve únicamente
        los CV pertenecientes a ese usuario.

        Se mantiene esta firma por compatibilidad con
        consumidores existentes del repositorio.
        """

        normalized_user_id = (user_id or "").strip()

        result: List[CVDocument] = []

        for item in self._load_raw():
            if normalized_user_id:
                item_user_id = str(
                    item.get("user_id", "")
                ).strip()

                if item_user_id != normalized_user_id:
                    continue

            try:
                result.append(
                    CVDocument.model_validate(item)
                )
            except Exception:
                continue

        result.sort(
            key=lambda cv: cv.updated_at,
            reverse=True,
        )

        return result

    # ==========================================================
    # DELETE
    # ==========================================================

    def delete(
        self,
        cv_id: str,
    ) -> bool:
        """
        Elimina un CV por ID.

        Devuelve True si existía y fue eliminado.
        """

        cv_id = cv_id.strip()

        if not cv_id:
            return False

        data = self._load_raw()

        original_length = len(data)

        remaining = [
            item
            for item in data
            if str(item.get("id", "")).strip() != cv_id
        ]

        if len(remaining) == original_length:
            return False

        self._write_all(remaining)

        return True