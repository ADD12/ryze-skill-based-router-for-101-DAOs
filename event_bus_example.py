import requests
import json
from datetime import datetime
import time

def simulate_github_action_failure():
    """
    Simulates a webhook payload sent by a CI/CD system like GitHub Actions 
    when a job fails.
    """
    url = "http://localhost:8000/webhook/error"
    
    payload = {
        "job_id": f"gh-action-{int(time.time())}",
        "owner_id": "u1", # The person who triggered the job (e.g. Alice)
        "system": "GitHub Actions",
        "error_message": "CUDA out of memory. Tried to allocate 2.00 GiB.",
        "stack_trace": "Traceback (most recent call last):\n  File 'train.py', line 45, in <module>\nRuntimeError: CUDA out of memory.",
        "timestamp": datetime.now().isoformat()
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Sending error payload to {url}...")
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Failed to connect to {url}. Is the Rye API running?")
        print(e)

if __name__ == "__main__":
    simulate_github_action_failure()