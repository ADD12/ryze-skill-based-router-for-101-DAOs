from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class JobError(BaseModel):
    job_id: str
    owner_id: str
    system: str  # GitHub Actions, Jenkins, etc.
    error_message: str
    stack_trace: Optional[str] = None
    timestamp: datetime = datetime.now()

class TeamMember(BaseModel):
    user_id: str
    slack_id: str
    name: str
    skills: List[str]
    is_available: bool  # Derived from Slack status
    current_workload: int = 0

class RoutingDecision(BaseModel):
    job_id: str
    assigned_user_id: str
    required_skills: List[str]
    reasoning: str