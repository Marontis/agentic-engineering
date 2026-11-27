# ADK Agentic Workflow Specification Template

> Fill in this template when architecting a multi-step agentic workflow using the
> Google Agent Development Kit (ADK) 2. Each section surfaces research-backed
> architectural decisions, node archetype trade-offs, and runtime requirements.
>
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## 1. Pipeline Objective & Operational Scope

### What is the workflow's primary responsibility?

- [ ] Content generation & asset production (scripts, video, audio, code)
- [ ] Research & multi-source intelligence aggregation
- [ ] Automated customer support & intake triage
- [ ] Policy audit & regulatory compliance checking
- [ ] Multi-step software engineering / GitOps remediation
- [ ] Other: ___

### What are the operational latency and execution boundaries?

- [ ] **Interactive Real-Time** (< 5s per step): Requires fast SLM inference or single-turn prompts.
- [ ] **Near-Line Synchronous** (5s – 30s): Standard generative models with synchronous tool calls.
- [ ] **Long-Running Asynchronous** (> 30s – hours): Requires `LongRunningFunctionTool`, pending call receipts, and decoupled background worker daemons.

---

## 2. Graph Topology & Node Archetypes

### What execution topology does the workflow require?

- [ ] **Linear Sequence**: Tuple chain `(node_a, node_b, node_c)`
- [ ] **Parallel Research Fan-Out**: Independent readers branching from `START` converging at a `JoinNode`
- [ ] **Conditional Branching**: Deterministic router node branching to alternative paths via edge dictionary
- [ ] **Iterative Remediation Loop**: Self-contained task loop rejoining the primary pipeline
- [ ] **Single-Agent Compute-Parity Check (`PACE`, `arXiv:2611.17610`)**: Confirmed that multi-node decomposition beats a `Category B/C` single-agent baseline (`k`-sample self-consistency or equal thinking/total tokens within $\epsilon \le 0.10$) after deducting system-prompt and echoed-history scaffold tokens (`rules/agent-evaluation-quality.md`).
- [ ] **Institutional `{cooperate, refuse, escalate}` Triage Check (`DiscernBench`, `arXiv:2611.28787`)**: Avoid splitting 3-way institutional decisions across separate `Policy`, `Hidden-Harm`, and `Oversight` specialist personas feeding a prose LLM `Final Responder` (`B3`), which inflates Over-Escalation Rate `7.5x` (`3.79% -> 28.27%`), induces up to `350x` lone-escalation Minority-Signal Override (`69.8%` vs. `0.2%`), and lowers social-pressure consistency on `8/8` models; prefer single-specialist joint rubric scoring (`B2`) or equal-weight `2-of-3` majority voting with deterministic tie-breakers ([`discernbench-institutional-cooperative-discernment`](../research-briefs/discernbench-institutional-cooperative-discernment.md)).

### Map each stage to an ADK Node Archetype:

| Stage Name | Archetype | Implementation | Purpose / Responsibility |
|:-----------|:----------|:---------------|:-------------------------|
| (e.g. `scan_trends`) | Function Node | Python function returning `Event(output=...)` | 0-cost deterministic data retrieval |
| (e.g. `read_feedback`) | Function Node (RAG) | Vector similarity query | Semantic grounding over shared corpus |
| (e.g. `join_research`) | Synchronization Barrier | `JoinNode(name=...)` | Aggregates concurrent branch outputs into dict |
| (e.g. `propose_ideas`) | Agent Node (`single_turn`) | `Agent(output_schema=...)` | Structured generation from aggregated inputs |
| (e.g. `approval_gate`) | Human Input Node | `yield RequestInput(...)` | Deterministic runtime execution suspension |
| (e.g. `policy_check`) | Router Node | Function returning `Event(route=...)` | Regex/file-backed policy check (0 LLM cost) |
| (e.g. `quarantine`) | Remediation Agent (`task`) | `Agent(mode="task", tools=[...])` | Autonomous cleanup using auto `finish_task` |
| (e.g. `render_desk`) | Long-Running Tool Node | `LongRunningFunctionTool(...)` | Asynchronous external execution handoff |

---

## 3. Agent Operating Modes & Schemas

### For each `Agent` node, select the required execution mode:

| Agent Node | Mode | Schema Enforced | Justification |
|:-----------|:-----|:----------------|:--------------|
| `propose_ideas` | `single_turn` | Pydantic `Directions` | Single inference pass, emits strictly typed JSON |
| `scripter` | `single_turn` | Pydantic `Script` | Direct transformation of approved concept |
| `quarantine` | `task` | Pydantic `CleanedDirection` | Iterative tool-using loop with auto `finish_task` |
| `coordinator` | `chat` | Free text / Markdown | Multi-turn conversational interface facing human |

> **Design note**: Intermediate graph transformations must always use `output_schema`
> with Pydantic models. This ensures downstream nodes read validated object attributes
> without fragile string parsing.

---

## 4. State & Memory Architecture

### How is state managed across graph execution?

- [ ] **Immediate Node Output (`Event(output=...)`)**: Data directed strictly to immediate downstream consumers.
- [ ] **Shared Session State (`Event(state=...)`)**: Global key-value state journal accessible to all subsequent nodes.
- [ ] **Parameter Auto-Binding**: Function nodes declare parameter names matching state keys to receive values without explicit unpacking.
- [ ] **Cross-Session State (`user:` prefix)**: State keys like `user:preferences` persisted across multiple workflow runs for the same user.
- [ ] **Compaction Timing, Epistemic Tagging & Authorization Separation (`arXiv:2611.25673`, `arXiv:2611.32194`)**: Delay working-context compaction in repository-editing workflows until edits materialize on disk (`86.9%` vs. `53.0%` accuracy), externalize negative search exclusions before compacting read-only research workflows (`52.9% -> 34.6%` late decay), structure summaries into explicit `verified` / `ruled-out (settled)` / `open hypothesis` buckets, key shared sub-agent caches by `(entity, period, source_id, route)` (`arXiv:2611.25071`), and deliver summaries in a `tool` role while gating authorization on `Witnessed-Request Gate` user turns ([`witnessed-request-compaction-gate`](../skills/witnessed-request-compaction-gate/SKILL.md)).

### Memory Bank vs RAG Engine Configuration

| Dimension | User Memory (Memory Bank) | Shared Knowledge (RAG Engine) |
|:----------|:--------------------------|:------------------------------|
| **Enabled?** | [ ] Yes &nbsp; [ ] No | [ ] Yes &nbsp; [ ] No |
| **Scope** | `{"app_name": ..., "user_id": ...}` | Global / Corpus-level |
| **Topics / Corpus** | Define topics (e.g. `CREATOR_TASTE`) | Document source (e.g. `comments.md`) |
| **Integration** | Lifecycle Callbacks (`before_model`, `after_agent`) | Dedicated Function Node in parallel fan-out |
| **Chunking Config** | Real-time semantic fact consolidation | `chunk_size` = ___ tokens, `overlap` = ___ |

> **Design note**: Do NOT create graph nodes for Memory Bank operations. Use `before_model_callback`
> to inject taste context and `after_agent_callback` to log observations. Reserve graph
> nodes for shared RAG corpus queries.

---

## 5. Deterministic Guardrails & Routing

### How are safety, compliance, and formatting policies evaluated?

- [ ] **Deterministic Regex / Word List (Recommended)**: Policy terms stored in external data files (`policy_words.txt`); evaluated in sub-milliseconds at 0 LLM cost.
- [ ] **Model Self-Evaluation (Discouraged)**: LLM evaluates its own safety; vulnerable to jailbreaks and prompt overrides.
- [ ] **Hybrid**: Fast deterministic filter first; ambiguous matches routed to an LLM evaluator.
- [ ] **Typed Non-Generative Routers, Python Math & Post-Turn Receipt Supervision (`arXiv:2611.25071`, `arXiv:2611.27095`)**: Route fixed-taxonomy intents with a compact encoder classifier (`~400M` `ModernBERT`, `0.85` intent in `~315 ms` vs. `0.52` `7B` / `0.67` `R1-8B` at `2,588 ms`), run ratio/margin arithmetic in deterministic `Python` (`100%` vs. `29%–72%` in `7B–8B` LLMs), and verify post-turn side-effect prose claims against signed `executed=true && ok=true` `MCP` wire receipts ([`receipt-bound-mcp-prose-supervision`](../skills/receipt-bound-mcp-prose-supervision/SKILL.md)).

### Router Edge Map & Fallback:

```python
edges = [
    (
        policy_check,
        {
            "OK": scripter_node,
            "BLOCK": quarantine_node,
            DEFAULT_ROUTE: quarantine_node,  # Mandatory fallback
        },
    ),
]
```

- [ ] Verified that all router edge dictionaries include `DEFAULT_ROUTE` to prevent pipeline stalls.

---

## 6. Suspension & Resumption Architecture

### Human Decision Gates (`RequestInput`)

- [ ] Suspension message defined
- [ ] Strict JSON response schema configured (e.g., enum list `["1", "2", "3"]`)
- [ ] Request payload bundled (enables frontend rendering without state querying)
- [ ] Verified that chat text cannot bypass the gate
- [ ] Parallel gated tool calls bind confirmations to individual `call_id` + target arguments (never collapsing `approve-both` into a single untyped boolean, which dropped `1` approved branch in `3/3` `ADK 2.14.0` tasks; [`dual-obligation-approval-auditing`](../skills/dual-obligation-approval-auditing/SKILL.md), arXiv:2611.19237)

### Long-Running External Tools (`LongRunningFunctionTool`)

- [ ] Tool function returns immediately with `{ "status": "pending", "call_id": ..., "operation_id": ... }`
- [ ] Suspension call metadata journaled in persistent database session
- [ ] External background worker / webhook listener configured
- [ ] Delivery daemon dispatches `Part(function_response=FunctionResponse(id=call_id, response={...}))`
- [ ] Verified that completed upstream nodes do not re-execute upon resumption
- [ ] For **stateful, interactive scientific/CAD/CAE simulation engines** (`minutes–hours` per run coexisting with a live human console, `arXiv:2611.33926`) where full workflow suspension would blind mid-solve diagnostics, pair `2` zero-embedding `BM25`/`browse` manual tools (`< 3%` manual token read) with `5` orthogonal sync/async primitives (`execute_code` parked at a single-timestep `cycle hold`, `execute_task`, lock-free `check_task_status`, post-loop-deferred `interrupt_task`, `list_tasks`) and bidirectional human `console_history` injection ([`shared-console-async-simulation-mcp`](../skills/shared-console-async-simulation-mcp/SKILL.md)).

---

## 7. Production Runtime & Deployment

### ADK Runner Configuration

```python
self._session_service = DatabaseSessionService(db_url=config.DATABASE_URL)
self._runner = Runner(
    app_name=config.APP_NAME,
    agent=root_workflow,
    session_service=self._session_service,
)
```

- [ ] **Session Storage**: Using durable database backend (Cloud SQL, PostgreSQL, SQLite) instead of `InMemorySessionService`.
- [ ] **Event Streaming**: Backend exposes a single Server-Sent Events (SSE) stream consuming `runner.run_async()`.
- [ ] **Frontend Decoupling**: UI state driven entirely by event stream; backend workflow has no UI dependencies.

### Google Cloud Run Hosting Parameters

- [ ] **Session Affinity**: Enabled (`--session-affinity`) to route iterative resumption calls to the same container.
- [ ] **Min Instances**: Configured (`--min-instances 1`) for critical production workflows to avoid cold-start latencies.
- [ ] **Concurrency & Timeout**: Timeout set according to longest expected synchronous node execution (e.g. `--timeout 3600`).
- [ ] **Distributed Observability**: Google Cloud Trace integration verified across nodes, LLM calls, and tool executions.
