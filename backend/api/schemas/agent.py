from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class AgentBase(BaseModel):
    name: str
    role: str
    description: str
    capabilities: List[str] = []
    status: str = "idle" # idle, working, completed, error

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None
    capabilities: Optional[List[str]] = None
    status: Optional[str] = None

class Agent(AgentBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
