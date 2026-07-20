# rye-skill-based-router-for-101-DAOs
Rye: The AI Governance Engine
Rye is the central intelligence of this system. It's a collection of services, likely running on a cloud platform or offline in a Mesh Fog AI community with little connectivity.
AI-driven systems, DAOs, and collaborative coding environments, DAOs can design a sophisticated and dynamic skill-based routing infrastructure governed by an AI agent named Rye.

This system will integrate with Slack for real-time communication and dynamically manage support tasks based on team member availability and expertise, particularly for errors that arise before a recurring deadline like a weekly meeting.
This closed-loop system where:
1. Job Monitoring: Systems (like GitHub Actions, Jenkins, supercomputer schedulers, etc.) report their status to a central hub.

2. Error Ingestion: When a job fails, it sends a detailed error payload to an event bus.

3. AI Triage (Rye): Rye intercepts the error, parses it to understand the context and required skills (e.g., Python, CUDA, CesiumJS, database-admin).

4. Dynamic Roster Management: Rye maintains a real-time status of all team members, their skills, and their availability, which is updated automatically based on their Slack status.

5. Intelligent Routing: Rye queries its roster to find the best-suited, available team member who is not the original owner of the failed job.

6. Slack-based Action & Communication: Rye assigns the task via a direct, interactive message in a dedicated Slack channel, and manages the entire support lifecycle through Slack.![RYE](https://github.com/user-attachments/assets/2781c7c2-427e-4bca-98ee-65f8fb8eb41a)

## Getting Started

1. **Install dependencies:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Configure Environment:**
Create a `.env` file in the root directory:
```env
SLACK_BOT_TOKEN=xoxb-your-slack-token
SLACK_SIGNING_SECRET=your-slack-signing-secret
OPENAI_API_KEY=sk-your-openai-key
DATABASE_URL=sqlite:///./rye.db
GITHUB_WEBHOOK_SECRET=supersecret
API_ADMIN_TOKEN=admin_token_123
```

3. **Seed Database:**
```bash
python seed_db.py
```

4. **Run the API:**
```bash
python main.py
```

5. **Test Webhooks / Event Bus:**
In a separate terminal, simulate a CI/CD failure:
```bash
python event_bus_example.py
```

## Slack App Installation Guide

To enable Rye to route errors and send interactive messages, you must configure a Slack App:

1. **Create the App:**
   - Go to [Slack API: Applications](https://api.slack.com/apps) and click **Create New App**.
   - Choose **From scratch**, name it `Rye Router`, and select your workspace.

2. **Configure Permissions (OAuth & Permissions):**
   - Scroll to **Scopes** -> **Bot Token Scopes** and add the following:
     - `chat:write` (to send assignment messages)
     - `users:read` (to check roster presence/availability)
   - Click **Install to Workspace** at the top.
   - Copy the **Bot User OAuth Token** (`xoxb-...`) and set it as `SLACK_BOT_TOKEN` in your `.env`.

3. **Enable Interactivity (for the "Acknowledge" button):**
   - Go to **Interactivity & Shortcuts** in the sidebar.
   - Toggle **Interactivity** to **On**.
   - Set the **Request URL** to your public API domain: `https://<your-domain>/slack/interactivity`
   - *(Note: For local testing, you can use [ngrok](https://ngrok.com/) to expose port 8000).*

4. **Configure Security:**
   - Go to **Basic Information** in the sidebar.
   - Scroll down to **App Credentials** and copy the **Signing Secret**.
   - Set this as `SLACK_SIGNING_SECRET` in your `.env` so Rye can verify payloads securely.

## API Endpoints
- `POST /webhook/error`: Ingests an error from a system, routes it to the best available member via AI triage.
- `POST /slack/interactivity`: Handles Slack block actions (e.g., clicking "Acknowledge" on a task).
- `GET /health`: Basic health check.
- `GET /admin/roster`: Requires `X-API-Key`. Returns the current team roster.

You can view the full Swagger/OpenAPI docs by visiting `http://localhost:8000/docs` while the server is running.