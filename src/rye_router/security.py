import hmac
import hashlib
import time
from fastapi import Request, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from .config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_github_signature(request: Request):
    """
    Verifies the webhook payload signature from GitHub Actions / Event Bus.
    Role: Webhook Sender (System)
    """
    if not settings.github_webhook_secret:
        return True

    signature_header = request.headers.get("x-hub-signature-256")
    if not signature_header:
        raise HTTPException(status_code=401, detail="Missing signature header")

    body = await request.body()
    hash_object = hmac.new(
        settings.github_webhook_secret.encode("utf-8"),
        msg=body,
        digestmod=hashlib.sha256,
    )
    expected_signature = "sha256=" + hash_object.hexdigest()

    if not hmac.compare_digest(expected_signature, signature_header):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")


async def verify_slack_signature(request: Request):
    """
    Verifies the request came from Slack using the Slack Signing Secret.
    Role: Slack App
    """
    if not settings.slack_signing_secret:
        return True

    slack_signature = request.headers.get("X-Slack-Signature")
    slack_request_timestamp = request.headers.get("X-Slack-Request-Timestamp")

    if not slack_signature or not slack_request_timestamp:
        raise HTTPException(status_code=401, detail="Missing Slack headers")

    if abs(time.time() - int(slack_request_timestamp)) > 60 * 5:
        raise HTTPException(status_code=401, detail="Replay attack detected")

    body = await request.body()
    sig_basestring = f"v0:{slack_request_timestamp}:{body.decode('utf-8')}"

    my_signature = (
        "v0="
        + hmac.new(
            settings.slack_signing_secret.encode("utf-8"),
            sig_basestring.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
    )

    if not hmac.compare_digest(my_signature, slack_signature):
        raise HTTPException(status_code=401, detail="Invalid Slack signature")


async def verify_admin(api_key: str = Security(api_key_header)):
    """
    Verifies administrative access via API Key.
    Role: Human Admin / CLI
    """
    if not api_key or api_key != settings.api_admin_token:
        raise HTTPException(status_code=403, detail="Not authenticated as admin")
    return api_key
