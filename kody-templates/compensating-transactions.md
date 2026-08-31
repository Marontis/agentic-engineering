---
title: "External API call in agent path without compensating transaction"
scope: "file"
path: ["**/agent*/**/*.py", "**/executor*/**/*.py", "**/tools/**/*.py"]
severity_min: "high"
languages: ["python"]
buckets: ["reliability", "correctness"]
enabled: true
---

## Instructions

When a PR adds or modifies code in an agent execution path that makes an
external API call (HTTP POST/PUT/DELETE, email send, database write to an
external service, message queue publish), check whether a compensating
transaction — an undo operation — is defined for that call.

Filesystem rollback cannot undo external side effects. If an agent workflow
calls an external API and then fails on a later step, the external effect
persists unless there is an explicit reversal.

Flag the PR if:

1. A `requests.post`, `httpx.post`, `aiohttp` session POST/PUT/DELETE, or
   equivalent appears in an agent execution path without a corresponding
   undo/compensate/rollback function registered for that step.
2. An email or notification send is triggered by an agent action without
   an idempotency key or deduplication check.
3. A database write to an external service (not the agent's own state DB)
   has no reversal path documented or implemented.
4. The PR claims "rollback on failure" but the rollback only covers local
   filesystem state, not the external call that already completed.

Origin: research — Fault-Tolerant Sandboxing for AI Coding Agents
(arXiv:2512.12806). External API calls are the boundary where filesystem
snapshots stop providing safety guarantees.

## Examples

### Bad example
```python
# YOUR REAL CODE HERE — paste the actual diff.
#
# Template:
async def deploy_step(self, config: DeployConfig):
    # Creates a real cloud resource — no undo if next step fails
    resp = requests.post(f"{CLOUD_API}/instances", json=config.to_dict())
    instance_id = resp.json()["id"]
    # ... later steps that might fail ...
```

### Good example
```python
# YOUR REAL FIX HERE — paste the corrected version.
#
# Template:
async def deploy_step(self, config: DeployConfig):
    resp = requests.post(f"{CLOUD_API}/instances", json=config.to_dict())
    instance_id = resp.json()["id"]
    self.compensations.push(
        lambda: requests.delete(f"{CLOUD_API}/instances/{instance_id}")
    )
    # If any later step fails, compensations unwind in reverse order
```
