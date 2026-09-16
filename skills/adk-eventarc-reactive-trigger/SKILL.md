---
name: adk-eventarc-reactive-trigger
description: >
  Trigger asynchronous Google ADK agent workflows reactively from Google Cloud Eventarc events
  including Cloud Storage uploads, Pub/Sub messages, and Cloud Audit Logs.
source: https://codelabs.developers.google.com/next26/eventarc-ai-agents?hl=en
---

# ADK Eventarc Reactive Agent Triggers

Use this skill when an ADK agent should execute asynchronously in response to enterprise
cloud events (e.g., a file uploaded to Cloud Storage, an event published to Pub/Sub, a new
CRM record created) rather than requiring a direct synchronous human HTTP prompt.

## When to Use

- Building automated event-driven ingestion, analysis, and fulfillment pipelines
- Launching an ADK multi-node workflow whenever a user uploads video/audio or documents
- Decoupling user-facing services from compute-heavy agent processing
- Coordinating serverless agent architectures using Cloud Run and Eventarc

---

## Core Architecture

Eventarc delivers events adhering to the open **CloudEvents v1.0** specification.
An HTTP service running the ADK `Runner` receives the event payload, maps event attributes
to workflow session inputs, and drives execution asynchronously:

```
[Cloud Storage: Upload PDF/Video]
               │
               ▼ (Emits google.cloud.storage.object.v1.finalized)
     [Eventarc Event Bus]
               │
               ▼ (HTTP POST /eventarc/handler with CloudEvent)
   [Cloud Run / GKE Agent Service]
               │
               ├── Parses CloudEvent headers & data (bucket, object name)
               ├── Creates unique ADK session_id
               └── Executes runner.run_async()
                     │
                     ▼
         [ADK Workflow Pipeline]
         - Read document from Cloud Storage
         - RAG embedding & classification
         - Generate report or commit database changes
```

---

## Step-by-Step Procedure

### 1. Implement the CloudEvent Receiver Route

In your FastAPI or web server hosting the ADK workflow:

```python
from fastapi import FastAPI, Request, HTTPException
from cloudevents.http import from_http
from google.adk import Runner

app = FastAPI()

@app.post("/events/storage-trigger")
async def handle_storage_event(request: Request):
    """Receive CloudEvents from Eventarc when files land in Cloud Storage."""
    # 1. Parse raw HTTP request into a CloudEvent object
    body = await request.body()
    headers = dict(request.headers)
    event = from_http(headers, body)

    # 2. Extract event attributes
    event_type = event["type"]
    if event_type != "google.cloud.storage.object.v1.finalized":
        return {"status": "ignored", "reason": "unsupported event type"}

    bucket = event.data.get("bucket")
    file_name = event.data.get("name")
    gcs_uri = f"gs://{bucket}/{file_name}"

    # 3. Create isolated session ID for this event
    session_id = f"event-{event['id']}"

    # 4. Initiate the ADK workflow run asynchronously
    initial_message = f"Process incoming file uploaded to {gcs_uri}"
    async for ev in runner.run_async(
        user_id="eventarc_service",
        session_id=session_id,
        new_message=initial_message
    ):
        log_workflow_event(ev)

    return {"status": "success", "session_id": session_id, "file": gcs_uri}
```

### 2. Configure Service Account Permissions

The Eventarc trigger requires permissions to invoke your Cloud Run or GKE agent service:

```bash
# Create service account for the trigger
gcloud iam service-accounts create eventarc-agent-invoker \
    --display-name="Eventarc Agent Invoker SA"

# Grant Cloud Run Invoker permission
gcloud run services add-iam-policy-binding adk-fulfillment-service \
    --region=us-central1 \
    --member="serviceAccount:eventarc-agent-invoker@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.invoker"
```

### 3. Create the Eventarc Trigger

Deploy the trigger routing events from your target Cloud Storage bucket:

```bash
gcloud eventarc triggers create gcs-agent-processor \
    --location=us-central1 \
    --destination-run-service=adk-fulfillment-service \
    --destination-run-path=/events/storage-trigger \
    --destination-run-region=us-central1 \
    --event-filters="type=google.cloud.storage.object.v1.finalized" \
    --event-filters="bucket=my-creator-raw-uploads" \
    --service-account=eventarc-agent-invoker@$PROJECT_ID.iam.gserviceaccount.com
```

---

## Environment & Implementation Caveats

- **Eventarc Retry Handling**: Eventarc retries event delivery if your endpoint returns a non-2xx status code or times out. Ensure your handler is **idempotent**: check if the `session_id` (derived from `event['id']`) has already started before executing tools.
- **Fast HTTP Acknowledgement**: Cloud Run has a request timeout. If the agent workflow takes several minutes, acknowledge the HTTP CloudEvent immediately with `202 Accepted` and spawn the `runner.run_async()` execution as a detached background task.
- **Dead-Letter Queues (DLQ)**: Configure a Cloud Pub/Sub dead-letter topic on the Eventarc trigger so poison-pill events (e.g. corrupted files) do not loop indefinitely.

---

## Edge Cases & Failure Modes

1. **Duplicate Event Delivery**: Cloud Pub/Sub and Eventarc guarantee at-least-once delivery, meaning duplicate events can occur. Use the CloudEvent `id` attribute as a database idempotency key to prevent running duplicate agent jobs.
2. **Missing Storage Read Permissions**: The Cloud Run service account must have `roles/storage.objectViewer` on the source bucket; otherwise, the first tool attempting to download the GCS URI will fail with a 403 error.
