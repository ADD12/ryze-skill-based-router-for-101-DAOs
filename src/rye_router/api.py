from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from .models import JobError
from .triage import AITriage
from .roster import RosterManager
from .router import SkillRouter
from .slack_integration import SlackActionManager

app = FastAPI(title="Rye - Skill-based Routing AI Agent")

# Initialize modules
triage = AITriage()
roster = RosterManager()
router = SkillRouter(triage=triage, roster=roster)
slack_manager = SlackActionManager()

class WebhookResponse(BaseModel):
    status: str
    message: str
    assigned_to: str = None
    reasoning: str = None

@app.post("/webhook/error", response_model=WebhookResponse)
async def handle_error_webhook(error: JobError):
    """
    Error Ingestion endpoint. Accepts detailed error payload from event bus or CI/CD system.
    """
    decision = router.route_error(error)
    
    if decision:
        # In a real app, map assigned_user_id to slack_user_id
        assigned_member = next((m for m in roster.team_members if m.user_id == decision.assigned_user_id), None)
        slack_id = assigned_member.slack_id if assigned_member else "UNKNOWN"
        
        # Send Slack action
        slack_manager.send_assignment_message(decision, error, slack_user_id=slack_id)
        
        return WebhookResponse(
            status="success",
            message="Error routed successfully.",
            assigned_to=decision.assigned_user_id,
            reasoning=decision.reasoning
        )
    else:
        # Fallback logic if no one is available
        return WebhookResponse(
            status="warning",
            message="No available team members found for routing.",
        )

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "rye"}