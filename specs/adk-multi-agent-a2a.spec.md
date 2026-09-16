# ADK Multi-Agent A2A Specification Template

> Fill in this template when designing a distributed, multi-agent system communicating
> across service boundaries via the Agent-to-Agent (A2A) protocol and Gemini Enterprise
> Agent Runtime.

---

## 1. System Architecture & Agent Federation

### What is the multi-agent topology?

- [ ] **Hierarchical Coordinator**: One central root agent delegates tasks to specialized subordinate A2A agents.
- [ ] **Chained Pipeline**: Autonomous agents pass artifacts sequentially across A2A endpoints.
- [ ] **Peer Mesh**: Independent peer agents discover each other dynamically via an Agent Directory registry.
- [ ] **Hybrid**: Central coordinator with autonomous peer-to-peer sub-clusters.

### Agent Inventory & Roles:

| Agent Name | Role / Specialization | Deployment Target | Protocol Interface |
|:-----------|:----------------------|:------------------|:-------------------|
| `root_coordinator` | Request triage, user interaction, routing | Cloud Run / GKE | Web / SSE to client |
| `reservation_agent` | Table availability, booking commitments | Agent Runtime | A2A JSON-RPC 2.0 |
| `inventory_agent` | Product catalog, stock verification | Agent Runtime | A2A JSON-RPC 2.0 |
| `billing_agent` | Payment token verification, invoicing | Agent Runtime (Isolated) | A2A JSON-RPC 2.0 |

---

## 2. Agent Card & Capability Declarations (`agent.json`)

Each federated agent must expose an authenticated Agent Card declaring its capabilities and security requirements:

```json
{
  "name": "reservation-service-agent",
  "version": "1.0.0",
  "description": "Handles restaurant reservations, seating checks, and cancellations.",
  "endpoints": {
    "a2a": "https://reservation-agent-runtime.cloud.run/a2a/v1"
  },
  "capabilities": [
    {
      "name": "check_table_availability",
      "description": "Check open slots for given party size and timestamp.",
      "input_schema": {
        "type": "object",
        "properties": {
          "party_size": {"type": "integer"},
          "datetime": {"type": "string", "format": "date-time"}
        },
        "required": ["party_size", "datetime"]
      }
    }
  ],
  "authentication": {
    "type": "OIDC",
    "audience": "https://reservation-agent-runtime.cloud.run"
  }
}
```

- [ ] Agent Card published at `/.well-known/agent.json`
- [ ] Capabilities declared with OpenAPI-compatible JSON schemas
- [ ] OIDC Audience configured for mutual authentication

---

## 3. Communication Protocol & Envelope Structure

### What transport and message protocol will be used?

- [ ] **JSON-RPC 2.0 over HTTPS** (Standard A2A baseline)
- [ ] **gRPC Streaming** (Low-latency bidirectional agent communication)
- [ ] **Cloud Pub/Sub Asynchronous Queues** (Decoupled event-driven federation)

### Message Envelope Specification:

- [ ] **`session_id`**: Maintained across inter-agent hops for end-to-end trace correlation.
- [ ] **`traceparent`**: W3C distributed tracing context passed in headers.
- [ ] **Caller Identity Token**: Signed Google ID token verifying caller authority.
- [ ] **Timeout & Deadlines**: Explicit deadline header passed (default: 15 seconds).

---

## 4. Security & Delegation Boundaries

### How are inter-agent requests authenticated and authorized?

- [ ] **Google Cloud Service Account OIDC**: Callers generate ID tokens via IAM and target the recipient's audience.
- [ ] **Scoped Delegation**: Coordinator forwards the original user's identity claims using IAM Workload Identity.
- [ ] **Data Minimization**: Subagents receive only the fields necessary for their subtask, not the entire conversational history.

### Error Handling & Fallback Contracts:

- [ ] Subagent unreachable: Return graceful degradation payload to coordinator within 3 retries.
- [ ] Subagent schema violation: Intercept and flag in coordinator; do not pass raw error to end user.
- [ ] Circuit breaker enabled: Trips after 3 consecutive failures to prevent cascading latency.

---

## 5. Deployment & Runtime Operations

### Agent Runtime Hosting:

```bash
# Register agent in Gemini Enterprise Agent Runtime
gcloud alpha agent-engine agents create reservation-agent \
    --region=us-central1 \
    --source-dir=./reservation_agent \
    --agent-card=./reservation_agent/agent.json \
    --service-account=agent-runtime-sa@$PROJECT_ID.iam.gserviceaccount.com
```

- [ ] Provisioned service accounts with minimal IAM roles
- [ ] Configured health check endpoint (`/healthz`)
- [ ] Integrated Cloud Logging and Cloud Trace for distributed inter-agent visibility
