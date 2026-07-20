from typing import List, Optional
from sqlalchemy.orm import Session
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from .models import TeamMember
from .db_models import DBTeamMember
from .config import settings

class RosterManager:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.slack_token = settings.slack_bot_token
        self.slack_client = WebClient(token=self.slack_token) if self.slack_token else None

    def update_availability_from_slack(self):
        """
        Poll Slack API to update real-time presence/status of team members.
        """
        if not self.slack_client:
            # Skip checking if Slack token is not configured
            return
            
        members = self.db.query(DBTeamMember).all()
        for member in members:
            if not member.slack_id:
                continue
            try:
                # Check user presence (active or away)
                response = self.slack_client.users_getPresence(user=member.slack_id)
                presence = response.get("presence", "away")
                
                # Active means they are online and available
                is_available = (presence == "active")
                
                if member.is_available != is_available:
                    member.is_available = is_available
            except SlackApiError as e:
                print(f"Error fetching presence for {member.slack_id}: {e.response['error']}")
                
        self.db.commit()

    def get_available_members(self, exclude_user_id: str) -> List[TeamMember]:
        """
        Returns a list of available team members, excluding the original job owner.
        """
        self.update_availability_from_slack()
        db_members = self.db.query(DBTeamMember).filter(
            DBTeamMember.is_available == True,
            DBTeamMember.user_id != exclude_user_id
        ).all()
        
        return [
            TeamMember(
                user_id=m.user_id,
                slack_id=m.slack_id,
                name=m.name,
                skills=m.skills,
                is_available=m.is_available,
                current_workload=m.current_workload
            ) for m in db_members
        ]
    
    def get_member_by_user_id(self, user_id: str) -> Optional[TeamMember]:
        m = self.db.query(DBTeamMember).filter(DBTeamMember.user_id == user_id).first()
        if m:
            return TeamMember(
                user_id=m.user_id,
                slack_id=m.slack_id,
                name=m.name,
                skills=m.skills,
                is_available=m.is_available,
                current_workload=m.current_workload
            )
        return None