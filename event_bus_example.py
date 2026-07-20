import requests
import json
from datetime import datetime
import time
import hmac
import hashlib


def simulate_github_action_failure():
    """
    Simulates a webhook payload sent by a CI/CD system like GitHub Actions
    when a job fails. Includes HMAC-SHA256 signature for security.
    """
    url = "http://localhost:8000/webhook/error"
    secret = b"supersecret"  # Must match github_webhook_secret in Settings

    payload = {
        "job_id": f"gh-action-{int(time.time())}",
        "owner_id": "u1",  # The person who triggered the job (e.g. Alice)
        "system": "GitHub Actions",
        "error_message": "CUDA out of memory. Tried to allocate 2.00 GiB.",
        "stack_trace": "Traceback (most recent call last):\n  File 'train.py', line 45, in <module>\nRuntimeError: CUDA out of memory.",
        "timestamp": datetime.now().isoformat(),
    }

    # Calculate webhook signature
    payload_bytes = json.dumps(payload).encode("utf-8")
    signature = "sha256=" + hmac.new(secret, payload_bytes, hashlib.sha256).hexdigest()

    headers = {"Content-Type": "application/json", "x-hub-signature-256": signature}

    print(f"Sending error payload to {url} with signature {signature[:20]}...")
    try:
        # We use data=payload_bytes instead of json=payload to ensure exact byte match for HMAC
        response = requests.post(url, data=payload_bytes, headers=headers)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Failed to connect to {url}. Is the Rye API running?")
        print(e)


if __name__ == "__main__":
    simulate_github_action_failure()
