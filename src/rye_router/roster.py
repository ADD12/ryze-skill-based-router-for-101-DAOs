from typing import List, Optional
from .models import TeamMember

class RosterManager:
    def __init__(self):
        # Mock database of team members
        self.team_members = [
            TeamMember(user_id="u1", slack_id="U111", name="Alice", skills=["python", "database-admin"], is_available=True),
            TeamMember(user_id="u2", slack_id="U222", name="Bob", skills=["cuda", "python"], is_available=False),
            TeamMember(user_id="u3", slack_id="U333", name="Charlie", skills=["cesiumjs"], is_available=True),
        ]

    def update_availability_from_slack(self):
        """
        Poll Slack API to update real-time presence/status of team members.
        """
        # TODO: Implement Slack presence check
        pass

    def get_available_members(self, exclude_user_id: str) -> List[TeamMember]:
        """
        Returns a list of available team members, excluding the original job owner.
        """
        self.update_availability_from_slack()
        return [
            m for m in self.team_members 
            if m.is_available and m.user_id != exclude_user_id
        ]