from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class SkillScore(BaseModel):
    technical_skills: float
    cognitive_ability: float
    communication: float
    behavioral_skills: float
    job_readiness: float

class StudentProfile(BaseModel):
    student_id: str
    name: str
    email: str
    institution: str
    degree: str
    graduation_year: int
    cgpa: Optional[float] = None
    resume_text: Optional[str] = None
    scores: Optional[SkillScore] = None
    overall_score: Optional[float] = None
    placement_probability: Optional[float] = None
    suitable_roles: Optional[List[str]] = []
    skill_gaps: Optional[List[str]] = []
    created_at: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime] = None

class AssessmentResult(BaseModel):
    student_id: str
    test_type: str
    score: float
    time_taken: Optional[int] = 0
    answers: Optional[Dict[str, str]] = {}
    evaluated_at: Optional[datetime] = datetime.now()

class PsychometricResult(BaseModel):
    student_id: str
    extraversion: float
    agreeableness: float
    conscientiousness: float
    neuroticism: float
    openness: float
    behavioral_score: float
    evaluated_at: Optional[datetime] = datetime.now()
