from sqlalchemy import Column, String, Boolean, Integer, JSON
from .database import Base


class DBTeamMember(Base):
    __tablename__ = "team_members"

    user_id = Column(String, primary_key=True, index=True)
    slack_id = Column(String, unique=True, index=True)
    name = Column(String)
    skills = Column(JSON)  # List of skills
    is_available = Column(Boolean, default=True)
    current_workload = Column(Integer, default=0)
