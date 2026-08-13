from pydantic import BaseModel

from backend.modules.mission.models import MissionSnapshot
from backend.modules.profile.models.professional_profile import ProfessionalProfile


class UploadMissionResponse(BaseModel):
    """
    Response returned after the upload boundary completes.

    The Mission snapshot identifies the runtime operation while `cv`
    is the persisted ProfessionalProfile consumed by the Flutter UI.
    """

    snapshot: MissionSnapshot
    cv: ProfessionalProfile | None = None
