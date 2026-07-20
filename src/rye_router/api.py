from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json

from .models import JobError
from .triage import AITriage
from .roster import RosterManager
from .router import SkillRouter
from .slack_integration import SlackActionManager
from .database import get_db, engine
from . import db_models
from .security import verify_github_signature, verify_slack_signature, verify_admin

# Create tables
db_models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Rye - Skill-based Routing AI Agent")

triage = AITriage()
slack_manager = SlackActionManager()


class WebhookResponse(BaseModel):
    status: str
    message: str
    assigned_to: str = None
    reasoning: str = None


@app.post(
    "/webhook/error",
    response_model=WebhookResponse,
    dependencies=[Depends(verify_github_signature)],
)
async def handle_error_webhook(error: JobError, db: Session = Depends(get_db)):
    """
    Error Ingestion endpoint. Accepts detailed error payload from event bus or CI/CD system.
    Secured by GitHub Webhook Signature.
    """
    roster = RosterManager(db_session=db)
    router = SkillRouter(triage=triage, roster=roster)

    decision = router.route_error(error)

    if decision:
        assigned_member = roster.get_member_by_user_id(decision.assigned_user_id)
        slack_id = assigned_member.slack_id if assigned_member else "UNKNOWN"

        # Send Slack action
        slack_manager.send_assignment_message(decision, error, slack_user_id=slack_id)

        return WebhookResponse(
            status="success",
            message="Error routed successfully.",
            assigned_to=decision.assigned_user_id,
            reasoning=decision.reasoning,
        )
    else:
        # Fallback logic if no one is available
        return WebhookResponse(
            status="warning",
            message="No available team members found for routing.",
        )


@app.post("/slack/interactivity", dependencies=[Depends(verify_slack_signature)])
async def slack_interactivity(request: Request, db: Session = Depends(get_db)):
    """
    Handles interactive components from Slack (like button clicks).
    Secured by Slack Signing Secret.
    """
    try:
        form = await request.form()
        payload = form.get("payload")
        if not payload:
            raise HTTPException(status_code=400, detail="Missing payload")

        data = json.loads(payload)

        # We only care about block_actions (button clicks)
        if data.get("type") == "block_actions":
            actions = data.get("actions", [])
            user_info = data.get("user", {})
            channel_id = data.get("channel", {}).get("id")
            message_ts = data.get("message", {}).get("ts")

            for action in actions:
                value = action.get("value", "")

                if value.startswith("ack_"):
                    job_id = value.replace("ack_", "")
                    slack_id = user_info.get("id")

                    print(f"User {slack_id} acknowledged job {job_id}")

                    # Update message to reflect acknowledgment
                    if slack_manager.client and channel_id and message_ts:
                        try:
                            slack_manager.client.chat_update(
                                channel=channel_id,
                                ts=message_ts,
                                text=f"Job {job_id} acknowledged.",
                                blocks=[
                                    {
                                        "type": "section",
                                        "text": {
                                            "type": "mrkdwn",
                                            "text": f"✅ *Job {job_id} has been acknowledged by <@{slack_id}>.*",
                                        },
                                    }
                                ],
                            )
                        except Exception as e:
                            print(f"Failed to update Slack message: {e}")

        return {"status": "ok"}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid payload")


@app.get("/admin/roster", dependencies=[Depends(verify_admin)])
def get_full_roster(db: Session = Depends(get_db)):
    """
    Admin-only endpoint to view the full team roster.
    Secured by API Key (RBAC).
    """
    roster = RosterManager(db_session=db)
    # Get everyone by passing an impossible exclude ID
    members = roster.get_available_members(exclude_user_id="nobody")
    return members


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "rye"}
