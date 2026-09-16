---
name: adk-a2a-agent-federation
description: >
  Federate distributed AI agents across network boundaries using Google ADK 2,
  the Agent-to-Agent (A2A) protocol, Agent Card declarations (agent.json), and
  Gemini Enterprise Agent Runtime.
source: https://codelabs.developers.google.com/codelabs/create-multi-agents-adk-a2a?hl=en
---

# ADK Agent-to-Agent (A2A) Federation

Use this skill when building multi-agent architectures where specialist agents run as
independent microservices or in dedicated runtime environments, communicating over the
standardized Agent-to-Agent (A2A) protocol rather than sharing in-process Python memory.

## When to Use

- Dividing a monolithic agent into domain-specific services owned by separate teams
- Delegating specialized tasks (e.g. reservation, billing, inventory) to isolated runtimes
- Calling an external agent hosted on Gemini Enterprise Agent Runtime from a root ADK coordinator
- Standardizing inter-agent contracts using structured Agent Cards (`agent.json`)

---

## Core Mental Model

In-process multi-agent systems (`sub_agents=[agent_a, agent_b]`) share Python memory and
run on the same host. In enterprise production, specialist agents require independent
scaling, isolated credentials, and language-agnostic network contracts.

The **A2A Protocol** defines a standardized JSON-RPC 2.0 communication layer:

```
[User] ──► [Root Coordinator Agent] (Cloud Run / GKE)
                 │
                 ├──(A2A Protocol / JSON-RPC 2.0 over HTTPS)
                 │   - Authenticated via OIDC Google ID token
                 │   - End-to-end session & traceparent correlation
                 ▼
     [Specialist Agent] (Agent Runtime)
        - Exposes /.well-known/agent.json
        - Executes isolated database/API tools
        - Returns typed structured response
```

---

## Step-by-Step Procedure

### 1. Author the Agent Card (`agent.json`)

Every federated A2A agent must define an Agent Card at its root or under `/.well-known/agent.json`.
This file serves as the discovery manifest declaring capabilities, input schemas, and authentication:

```json
{
  "name": "restaurant_reservation_agent",
  "version": "1.0.0",
  "description": "Checks table availability and creates confirmed dining reservations.",
  "endpoints": {
    "a2a": "/a2a/v1"
  },
  "capabilities": [
    {
      "name": "book_table",
      "description": "Book a table for a party size at a specific ISO timestamp.",
      "input_schema": {
        "type": "object",
        "properties": {
          "party_size": {"type": "integer"},
          "reservation_time": {"type": "string", "format": "date-time"}
        },
        "required": ["party_size", "reservation_time"]
      }
    }
  ]
}
```

### 2. Implement the A2A Server Handler

Wrap the agent logic with the ADK A2A server transport or Agent Platform SDK:

```python
from google.adk import Agent
from google.adk.a2a import A2AServer

reservation_agent = Agent(
    name="reservation_worker",
    model=config.MODEL,
    instruction="Check database and confirm table reservations.",
    tools=[check_table_db, insert_reservation_db],
)

app = A2AServer(agent=reservation_agent, agent_card_path="agent.json").get_app()
```

### 3. Deploy to Gemini Enterprise Agent Runtime

Deploy the specialist agent container to Agent Runtime using Google Cloud CLI:

```bash
gcloud alpha agent-engine agents create reservation-agent \
    --region=us-central1 \
    --source-dir=./reservation_agent \
    --agent-card=./reservation_agent/agent.json \
    --service-account=reservation-agent-sa@$PROJECT_ID.iam.gserviceaccount.com
```

Record the deployed agent's remote A2A endpoint URL.

### 4. Connect the Remote A2A Agent to the Root Coordinator

In the coordinator agent, register the remote A2A service as an external toolset using
the `A2AToolset` client:

```python
from google.adk import Agent
from google.adk.a2a import A2AToolset

reservation_tools = A2AToolset(
    endpoint="https://reservation-agent-runtime.cloud.run/a2a/v1",
    agent_card_url="https://reservation-agent-runtime.cloud.run/.well-known/agent.json",
    auth_audience="https://reservation-agent-runtime.cloud.run",
)

root_coordinator = Agent(
    name="restaurant_concierge",
    model=config.MODEL,
    instruction="Greet the user and delegate bookings to the reservation service.",
    tools=[reservation_tools],
)
```

The coordinator automatically extracts capability schemas from the remote Agent Card
and makes them callable as standard ADK tools.

---

## Environment & Implementation Caveats

- **Identity Propagation**: Always configure the client toolset with an `auth_audience`. In production, the coordinator generates an OIDC ID token matching the audience, ensuring unauthorized callers cannot hit the specialist agent directly.
- **Trace Context Passing**: Ensure your HTTP client passes standard `traceparent` headers so Cloud Trace visualizes the distributed hop from coordinator to specialist agent as a single trace.
- **Payload Size Limits**: Avoid passing heavy binary assets (e.g. video files, large PDFs) directly across A2A JSON-RPC payloads. Pass Google Cloud Storage URIs (`gs://...`) instead.

---

## Edge Cases & Failure Modes

1. **Agent Card Schema Drift**: If the specialist agent changes its input parameters without updating the Agent Card, the coordinator generates tool calls matching the obsolete schema, failing validation. Automate Agent Card regeneration from Pydantic schemas in CI/CD.
2. **Cascading Timeout Exhaustion**: If the specialist agent takes 12 seconds to respond and the coordinator timeout is set to 10 seconds, the coordinator drops the connection while the specialist agent continues executing. Set downstream timeouts strictly shorter than upstream caller deadlines.
