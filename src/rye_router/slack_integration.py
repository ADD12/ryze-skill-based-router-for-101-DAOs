from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from .models import RoutingDecision, JobError
from .config import settings


class SlackActionManager:
    def __init__(self, token: str = None):
        self.token = token or settings.slack_bot_token
        # Initialize client if token is available
        self.client = WebClient(token=self.token) if self.token else None

    def send_assignment_message(
        self, decision: RoutingDecision, error: JobError, slack_user_id: str
    ):
        """
        Assigns the task via a direct, interactive message in Slack.
        """
        if not self.client:
            print(
                f"Mock Slack Message to {slack_user_id}: You've been assigned job {decision.job_id} due to your skills in {decision.required_skills}."
            )
            return

        try:
            # TODO: Construct rich interactive blocks
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"🚨 *New Support Task Assigned*\n*Job ID:* {error.job_id}\n*System:* {error.system}\n*Reason:* {decision.reasoning}",
                    },
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Acknowledge"},
                            "style": "primary",
                            "value": f"ack_{error.job_id}",
                        }
                    ],
                },
            ]

            response = self.client.chat_postMessage(
                channel=slack_user_id,
                text=f"New task assigned: {error.job_id}",
                blocks=blocks,
            )
            return response
        except SlackApiError as e:
            print(f"Error sending Slack message: {e.response['error']}")
