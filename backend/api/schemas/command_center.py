from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ExecutiveReport(BaseModel):
    summary: str
    generated_at: datetime

class Priority(BaseModel):
    id: str
    title: str
    description: str
    urgency: str # low, medium, high
    status: str # pending, in_progress, completed

class Opportunity(BaseModel):
    id: str
    title: str
    company: str
    match_score: int
    url: Optional[str] = None

class Insight(BaseModel):
    id: str
    content: str
    type: str # market, skill, salary

class CommandCenterData(BaseModel):
    executive_report: Optional[ExecutiveReport] = None
    priorities: List[Priority] = []
    opportunities: List[Opportunity] = []
    insights: List[Insight] = []
