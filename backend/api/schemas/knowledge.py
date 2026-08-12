from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class KnowledgeAssetBase(BaseModel):
    title: str
    type: str # CV, Cover Letter, LinkedIn, Certificate, Portfolio, Document
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class KnowledgeAssetCreate(KnowledgeAssetBase):
    pass

class KnowledgeAssetUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class KnowledgeAsset(KnowledgeAssetBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
