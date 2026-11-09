---
name: google-adk
description: >
  Design, orchestrate, secure, federate, and evaluate production multi-agent systems
  with Google Agent Development Kit (ADK 2). Covers the 3 orchestration pillars
  (Graph Workflows, Collaborative Agents, Dynamic Workflows), lifecycle callback
  interceptors, asynchronous long-running tool resumption, MCP multimodal tool
  interception, Model Armor & Cloud DLP security guards, A2A protocol federation,
  A2UI declarative widgets, Eventarc reactive CloudEvent triggers, and golden
  dataset trajectory CI/CD gates.
license: CC-BY-4.0
repository: https://github.com/Marontis/agentic-engineering
---

# Google Agent Development Kit (ADK 2) Engineering Guide

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

Use this skill when architecting, building, securing, or evaluating agent workflows with the **Google Agent Development Kit (ADK 2)**. This skill uses progressive disclosure: use the routing matrix and core invariants below to choose the right architectural pattern, then load only the specific reference guide in `references/` needed for your current subtask.

## When to Use

- Designing single-agent or multi-agent ADK 2 workflows (static DAGs, specialist teams, or runtime-sized fan-out/recursion)
- Attaching non-invasive lifecycle callbacks (`before/after_agent`, `before/after_model`, `before/after_tool`) for memory, telemetry, or guardrails
- Suspending and resuming long-running external jobs (`LongRunningFunctionTool`) or human approval gates (`RequestInput`)
- Connecting MCP servers (`mcp_toolset`) and sanitizing heavy multimodal payloads before context re-injection
- Hardening customer-facing ADK agents with Google Cloud Model Armor and Sensitive Data Protection (SDP / Cloud DLP)
- Federating distributed specialist agents across Cloud Run / Agent Runtime over the Agent-to-Agent (`A2A`) protocol
- Streaming declarative `A2UI` interactive widgets to React/mobile frontends and dispatching client actions back to the ADK `Runner`
- Triggering headless ADK workflows reactively from Cloud Storage, Pub/Sub, or Audit Logs via Eventarc (`CloudEvents v1.0`)
- Enforcing deterministic trajectory and parameter quality gates in CI/CD with `adk eval` and `pytest`

---

## Reference Routing Matrix (Load on Demand)

Read only the reference file matching your active engineering task:

| Engineering Subtask | Reference Guide | Key ADK 2 Primitives |
|:---|:---|:---|
| **Multi-agent orchestration & workflow topology** | [`references/orchestration-patterns.md`](./references/orchestration-patterns.md) | `Workflow`, `JoinNode`, dict routers, `mode="single_turn"`, `mode="task"`, `@node(parallel_worker=True)`, `ctx.run_node` |
| **Memory recall, context enrichment & lifecycle hooks** | [`references/lifecycle-callback-interceptors.md`](./references/lifecycle-callback-interceptors.md) | `before/after_agent_callback`, `before/after_model_callback`, `before/after_tool_callback`, Vertex AI Memory Bank |
| **Async jobs (>30s), webhooks & human approval gates** | [`references/async-long-running-tool-resumption.md`](./references/async-long-running-tool-resumption.md) | `LongRunningFunctionTool`, `RequestInput`, `FunctionResponse(id=call_id)`, `DatabaseSessionService` |
| **MCP servers & multimodal payload sanitization** | [`references/mcp-multimodal-tool-interception.md`](./references/mcp-multimodal-tool-interception.md) | `mcp_toolset`, parameter injection in `before_tool_callback`, GCS offloading in `after_tool_callback` |
| **Prompt injection defense & PII redaction** | [`references/model-armor-interceptor.md`](./references/model-armor-interceptor.md) | `ModelArmorClient.sanitize_user_prompt`, `DlpServiceClient.deidentify_content`, fail-closed interceptors |
| **Cross-service distributed agent federation** | [`references/a2a-agent-federation.md`](./references/a2a-agent-federation.md) | `/.well-known/agent.json` Agent Card, `A2AServer`, `A2AToolset`, OIDC `auth_audience`, `traceparent` |
| **Interactive frontend cards, forms & action buttons** | [`references/a2ui-dynamic-widgets.md`](./references/a2ui-dynamic-widgets.md) | Typed Pydantic `output_schema` widgets, `text_summary` fallback, `/api/session/{id}/action` resumption |
| **Event-driven serverless pipelines (GCS / Pub/Sub)** | [`references/eventarc-reactive-trigger.md`](./references/eventarc-reactive-trigger.md) | `cloudevents.http.from_http`, Eventarc triggers, idempotent `session_id = f"event-{event['id']}"` |
| **Golden dataset regression & trajectory CI/CD gates** | [`references/eval-golden-dataset-ci.md`](./references/eval-golden-dataset-ci.md) | `adk web` trace export, `AgentEvaluator`, `tool_trajectory_match_rate >= 0.95`, noise-margin acceptance gate |

---

## Core Architectural Decision Tree

Every ADK 2 orchestration design begins with one question: **Who decides what runs next?**

> *"Predictable work stays as functions; clear rules become explicit routing; reasoning uses the model."*

```
Would a prebuilt SequentialAgent / ParallelAgent / LoopAgent suffice?
│
├─ YES ──────────────────────────────► Use prebuilt agent (cheapest, no custom graph needed)
│
└─ NO — I need routing, payload joining, or non-agent function nodes
   │
   Can you draw the workflow before the input arrives?
   │
   ├─ YES ───────────────────────────► Pillar 1: Graph Workflow
   │                                    (Static DAG, 0-LLM Python nodes, JoinNode, dict-edge router)
   │                                    → Read: references/orchestration-patterns.md
   │
   └─ NO
      │
      ├─ Known team, request picks subset? ─► Pillar 2: Collaborative Agents
      │                                       (Coordinator + mode="single_turn" or mode="task" subagents)
      │                                       → Read: references/orchestration-patterns.md
      │
      └─ Does the shape itself depend on input? ─► Pillar 3: Dynamic Workflow
                                                   (@node(parallel_worker=True) + bounded ctx.run_node recursion)
                                                   → Read: references/orchestration-patterns.md
```

---

## Graph Nodes vs. Lifecycle Callbacks vs. Tools

Do not pollute the macro `Workflow` DAG with cross-cutting concerns. Separate responsibilities strictly across ADK's three execution layers:

| Layer | Use For | Do NOT Use For | Reference |
|:---|:---|:---|:---|
| **Graph Node (`Workflow`)** | Shared data dependencies, parallel fan-out/join (`JoinNode`), deterministic branching, human approval gates (`RequestInput`). | Agent-local memory recall, prompt guardrails, PII redaction, telemetry logging. | [`orchestration-patterns.md`](./references/orchestration-patterns.md) |
| **Lifecycle Callback** | Inbound Model Armor checks (`before_agent`), Memory Bank injection (`before_model`), MCP parameter injection (`before_tool`), PII/media sanitization (`after_tool`), memory consolidation (`after_agent`). | Multi-branch routing, parallel worker fan-out, synchronization barriers. | [`lifecycle-callback-interceptors.md`](./references/lifecycle-callback-interceptors.md) |
| **Tool (`tools=[...]`)** | On-demand retrieval or external mutations requested autonomously by the model (`FunctionTool`, `LongRunningFunctionTool`, `mcp_toolset`, `A2AToolset`). | Mandatory context that the agent must *always* possess before reasoning. | [`async-long-running-tool-resumption.md`](./references/async-long-running-tool-resumption.md) |

---

## Non-Negotiable Production Invariants

1. **Never Leave Subagent `mode` Unset When Parallelism or Synthesis Is Needed**: Default `mode=None` exposes only `transfer_to_agent`, permanently stranding the user with a single specialist. Use `mode="single_turn"` for parallel tool-like specialist dispatch and synthesis, or `mode="task"` for multi-turn conversational intake with a typed `output_schema`.
2. **Enforce Hard Recursion & Fan-Out Bounds in Python Code**: Every recursive `@node` (`ctx.run_node`) must enforce an explicit `depth < MAX_DEPTH` guard in Python and attach a `RetryConfig` to `@node(parallel_worker=True)` so a single transient 429/503 does not cancel sibling workers.
3. **Sanitize Every Tool Output & Peer Message**: Never allow raw database outputs, third-party MCP responses, or base64 media blobs directly into model context. Redact PII via Cloud DLP (`after_tool_callback`) and offload heavy media to Cloud Storage (`gs://...`) before inference continues.
4. **Persist `call_id` Atomically for Resumption**: Both `RequestInput` and `LongRunningFunctionTool` suspend the process and resume only when `Part(function_response=FunctionResponse(id=call_id, ...))` is delivered against a persistent `DatabaseSessionService`.
5. **Gate Every Prompt, Skill, or Model Change on Full Trajectory Evaluation**: Require `tool_trajectory_match_rate >= 0.95`, zero schema errors, zero policy violations, and no regression beyond baseline noise margin $\delta$ on previously-correct and held-out cases (`references/eval-golden-dataset-ci.md`).

## Cross-References

- [`../rules/adk-security-and-evaluation.md`](../../rules/adk-security-and-evaluation.md) — Always-active DO/DON'T rules for ADK security, interceptors, and evaluation gates
- [`../rules/agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — Tool output sanitization and sandbox isolation invariants
- [`../rules/recursive-improvement.md`](../../rules/recursive-improvement.md) — Acceptance gate and orchestration invariants
- [`../research-briefs/adk2-orchestration-three-pillars.md`](../../research-briefs/adk2-orchestration-three-pillars.md) — Architectural deep-dive on ADK 1.x vs. ADK 2
