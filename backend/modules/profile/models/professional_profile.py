from pydantic import BaseModel, Field
from typing import List, Optional
import uuid

class PersonalInfo(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    portfolio: str = ""
    website: str = ""
    professional_summary: str = ""
    career_goal: str = ""
    current_position: str = ""
    years_of_experience: int = 0

class Experience(BaseModel):
    company: str = ""
    role: str = ""
    start_date: str = ""
    end_date: str = ""
    description: str = ""
    achievements: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    skills_used: List[str] = Field(default_factory=list)

class Education(BaseModel):
    institution: str = ""
    degree: str = ""
    level: str = ""
    period: str = ""

class Skills(BaseModel):
    technical_skills: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    programming_languages: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    cloud: List[str] = Field(default_factory=list)

class Language(BaseModel):
    language: str = ""
    level: str = ""
    certification: str = ""

class Certification(BaseModel):
    name: str = ""
    provider: str = ""
    date: str = ""

class ATSMetrics(BaseModel):
    ats_score: int = 0
    detected_keywords: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)
    compatibility: str = ""
    observations: List[str] = Field(default_factory=list)

class LinkedInMetrics(BaseModel):
    score: int = 0
    profile_level: str = ""
    observations: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

class CareerMetrics(BaseModel):
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    areas_for_improvement: List[str] = Field(default_factory=list)
    employability_level: str = ""

class ProfessionalProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "temp_user"
    
    personal_info: PersonalInfo = Field(default_factory=PersonalInfo)
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    skills: Skills = Field(default_factory=Skills)
    languages: List[Language] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    
    ats_metrics: ATSMetrics = Field(default_factory=ATSMetrics)
    linkedin_metrics: LinkedInMetrics = Field(default_factory=LinkedInMetrics)
    career_metrics: CareerMetrics = Field(default_factory=CareerMetrics)
    
    # Optional raw data for agents that need deeper context
    cv_keywords: List[str] = Field(default_factory=list)
    cv_score: int = 0
