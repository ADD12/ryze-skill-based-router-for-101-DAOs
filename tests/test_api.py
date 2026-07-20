from fastapi.testclient import TestClient
from unittest.mock import patch

from src.rye_router.api import app
from src.rye_router.security import verify_github_signature, verify_slack_signature

# Override security dependencies for testing the core API logic
app.dependency_overrides[verify_github_signature] = lambda: True
app.dependency_overrides[verify_slack_signature] = lambda: True

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "rye"}


@patch("src.rye_router.slack_integration.SlackActionManager.send_assignment_message")
@patch("src.rye_router.router.SkillRouter.route_error")
@patch("src.rye_router.roster.RosterManager.get_member_by_user_id")
def test_webhook_error_endpoint_success(
    mock_get_member, mock_route_error, mock_send_message
):
    # Mock the router decision
    from src.rye_router.models import RoutingDecision, TeamMember

    mock_route_error.return_value = RoutingDecision(
        job_id="test_job",
        assigned_user_id="u1",
        required_skills=["python"],
        reasoning="Test reasoning",
    )

    # Mock the returned member
    mock_get_member.return_value = TeamMember(
        user_id="u1", slack_id="S111", name="Alice", skills=[], is_available=True
    )

    payload = {
        "job_id": "test_job",
        "owner_id": "u4",
        "system": "Jenkins",
        "error_message": "Failed to compile",
        "timestamp": "2023-10-01T12:00:00",
    }

    response = client.post("/webhook/error", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["assigned_to"] == "u1"

    # Verify Slack action manager was called
    mock_send_message.assert_called_once()


@patch("src.rye_router.api.slack_manager")
def test_slack_interactivity_ack(mock_slack_manager):
    from unittest.mock import MagicMock

    # Setup mock slack client
    mock_slack_manager.client = MagicMock()
    mock_slack_manager.client.chat_update = MagicMock()

    import json

    # Create the nested payload structure that Slack sends
    slack_payload = {
        "type": "block_actions",
        "user": {"id": "S123"},
        "channel": {"id": "C123"},
        "message": {"ts": "12345.6789"},
        "actions": [{"value": "ack_test_job_1"}],
    }

    # Send it as form data just like Slack does
    response = client.post(
        "/slack/interactivity", data={"payload": json.dumps(slack_payload)}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    mock_slack_manager.client.chat_update.assert_called_once()
