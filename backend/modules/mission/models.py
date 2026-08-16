from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from backend.runtime.mission_state import MissionStatus, MissionStage


class MissionEventType(str, Enum):
    MISSION_CREATED   = "MISSION_CREATED"
    MISSION_STARTED   = "MISSION_STARTED"
    MISSION_PAUSED    = "MISSION_PAUSED"
    MISSION_COMPLETED = "MISSION_COMPLETED"
    MISSION_FAILED    = "MISSION_FAILED"
    MISSION_CANCELLED = "MISSION_CANCELLED"
    CV_UPLOADED       = "CV_UPLOADED"
    STORAGE_COMPLETED = "STORAGE_COMPLETED"
    PDF_DETECTED      = "PDF_DETECTED"
    DOCX_DETECTED     = "DOCX_DETECTED"
    PARSER_STARTED    = "PARSER_STARTED"
    TEXT_EXTRACTED    = "TEXT_EXTRACTED"
    PROFILE_CREATED   = "PROFILE_CREATED"
    WAITING_AGENT     = "WAITING_AGENT"
    ANALYSIS_STARTED  = "ANALYSIS_STARTED"
    CV_PARSED         = "CV_PARSED"
    ATS_COMPLETED     = "ATS_COMPLETED"
    JOBS_FOUND        = "JOBS_FOUND"
    INTERVIEW_SCHEDULED = "INTERVIEW_SCHEDULED"
    OFFER_RECEIVED    = "OFFER_RECEIVED"


class MissionEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mission_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str
    type: MissionEventType
    severity: str = Field(default="info")
    title: str
    description: str
    stage: MissionStage = Field(default=MissionStage.RECEIVE_FILE)
    userMessage: Optional[str] = None
    developerMessage: Optional[str] = None
    logs: Optional[str] = None
    duration: int = 0
    metadata: Dict[str, Any] = {}


class AgentStatusInfo(BaseModel):
    id: str
    name: str
    status: str
    progress: int
    recommendations: List[str] = []


from backend.modules.cv.models.cv_metadata import CVMetadata


class MissionState(BaseModel):
    file_path: Optional[str] = None
    metadata: Optional[CVMetadata] = None
    raw_text: Optional[str] = None
    sections: Optional[Dict[str, str]] = None
    profile_id: Optional[str] = None


class Mission(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(default="temp_user")
    title: str
    career_goal: str
    target_company: Optional[str] = None
    target_position: Optional[str] = None
    salary_goal: Optional[float] = None
    location: Optional[str] = None
    remote: bool = False
    deadline: Optional[datetime] = None
    profile_id: Optional[str] = None

    status: MissionStatus = Field(default=MissionStatus.CREATED)
    current_step: MissionStage = Field(default=MissionStage.RECEIVE_FILE)
    progress: int = Field(default=0, ge=0, le=100)
    failureReason: Optional[str] = None

    active_agents: List[str] = []
    current_agent: Optional[str] = None
    last_heartbeat: Optional[datetime] = None
    execution_started_at: Optional[datetime] = None

    input: Dict[str, Any] = Field(default_factory=dict)
    configuration: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)

    outputs: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    artifacts: Dict[str, Any] = Field(default_factory=dict)

    timeline: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    state: MissionState = Field(default_factory=MissionState)
    agents_executed: List[str] = []

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def duration(self) -> int:
        if self.execution_started_at:
            end = self.updated_at if self.status in [MissionStatus.COMPLETED, MissionStatus.FAILED, MissionStatus.CANCELLED] else datetime.utcnow()
            return int((end - self.execution_started_at).total_seconds())
        return 0


class RuntimeStatus(BaseModel):
    online: bool
    active_agents: List[str]
    current_agent: Optional[str] = None


class SystemHealth(BaseModel):
    status: str
    database: bool
    storage: bool
    version: str


class MissionSnapshot(BaseModel):
    mission: Mission
    runtime: RuntimeStatus
    agent_statuses: List[AgentStatusInfo] = Field(default_factory=list)
    timeline: List[MissionEvent]
    progress: int
    current_step: str
    results: Dict[str, Any]
    health: SystemHealth
    warnings: List[str]
    errors: List[str]
    availableActions: List[str] = Field(default_factory=list)
    retryMode: str = Field(default="NONE")
