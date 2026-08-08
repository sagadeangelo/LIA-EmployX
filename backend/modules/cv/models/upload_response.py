from pydantic import BaseModel
from backend.modules.mission.models import MissionSnapshot

class UploadMissionResponse(BaseModel):
    snapshot: MissionSnapshot
