from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class MissionBase(BaseModel):
    title: str
    career_goal: str
    target_company: Optional[str] = None
    target_position: Optional[str] = None
    salary_goal: Optional[float] = None
    location: Optional[str] = None
    remote: bool = False
    deadline: Optional[datetime] = None

class MissionCreate(MissionBase):
    pass

class MissionUpdate(BaseModel):
    title: Optional[str] = None
    career_goal: Optional[str] = None
    target_company: Optional[str] = None
    target_position: Optional[str] = None
    salary_goal: Optional[float] = None
    location: Optional[str] = None
    remote: Optional[bool] = None
    deadline: Optional[datetime] = None
    progress: Optional[int] = None
    status: Optional[str] = None

class Mission(MissionBase):
    id: str
    progress: int = Field(default=0, ge=0, le=100)
    status: str = Field(default="active")
    active_agents: List[str] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
