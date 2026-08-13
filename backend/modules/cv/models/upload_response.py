from pydantic import BaseModel

from backend.modules.mission.models import MissionSnapshot
from backend.modules.cv.models.cv_document import CVDocument


class UploadMissionResponse(BaseModel):
    """
    Respuesta del endpoint de subida de CV.

    snapshot:
        Estado de la Mission y del Runtime.

    cv:
        CVDocument estructurado generado por el pipeline.
    """

    snapshot: MissionSnapshot
    cv: CVDocument | None = None
