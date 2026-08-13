from __future__ import annotations

from pydantic import BaseModel

from backend.modules.mission.models import MissionSnapshot
from backend.modules.cv.models.cv_document import CVDocument
from backend.modules.profile.models.professional_profile import (
    ProfessionalProfile,
)


class UploadMissionResponse(BaseModel):
    """
    Respuesta del endpoint:

        POST /api/v1/cv/upload

    Contiene:

        snapshot
            Estado de la Mission.

        cv
            CVDocument estructurado generado por el pipeline.

        profile
            ProfessionalProfile generado a partir del CV.
    """

    snapshot: MissionSnapshot

    cv: CVDocument | None = None

    profile: ProfessionalProfile | None = None