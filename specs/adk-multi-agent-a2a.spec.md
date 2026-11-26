# ADK Multi-Agent A2A Specification Template

> Fill in this template when designing a distributed, multi-agent system communicating
> across service boundaries via the Agent-to-Agent (A2A) protocol and Gemini Enterprise
> Agent Runtime.
>
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## 1. System Architecture & Agent Federation

### What is the multi-agent topology?

- [ ] **Hierarchical Coordinator**: One central root agent delegates tasks to specialized subordinate A2A agents.
- [ ] **Chained Pipeline**: Autonomous agents pass artifacts sequentially across A2A endpoints.
- [ ] **Peer Mesh**: Independent peer agents discover each other dynamically via an Agent Directory registry.
- [ ] **Hybrid**: Central coordinator with autonomous peer-to-peer sub-clusters.
- [ ] **Graph-Constrained Decentralized Mesh (`N = 50–1,000+` peers or `100K+` owner-private tools, `arXiv:2611.15521`)**: When global Agent Card registries overflow context or `HMAC`/credentialed tools require owner-local `result` execution, run bounded `2`-hop neighbor capability-summary warmup ($W_i$), separate per-task loop/DAG caches ($h_{i,t}$) from cross-task semantic LLM routing memory ($M_{i,t}$) gated by `"DO: Pass every self-modification through one acceptance gate"` (`rules/recursive-improvement.md`), and monitor per-neighbor delivery receipts to quarantine misrouting hubs ([`topology-warmup-decentralized-routing`](../skills/topology-warmup-decentralized-routing/SKILL.md)).
- [ ] **Compute-Parity Justification (`PACE`, `arXiv:2611.17610`)**: Verified that multi-agent communication is justified by partitioned evidence ($I(Y; X_j \mid X_{\text{shared}}, X_i) > 0$), an asymmetric external verifier ($R_{\text{sys}}$), or cross-model error decorrelation ($\rho_{\text{het}} < \rho_{\text{hom}}$), and benchmarked against `Category B` ($k$-sample `CoT-SC` / majority vote) and `Category C` budget-matched single-agent baselines across $\mathbf{R} = \langle R_{\text{reason}}, R_{\text{token}}, R_{\text{cost}}, R_{\text{lat}}, R_{\text{sample}}, R_{\text{sys}} \rangle$ ([`pace-multi-agent-compute-parity-synthesis`](../research-briefs/pace-multi-agent-compute-parity-synthesis.md)).

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
- [ ] **Pre-Invocation Agent Card Screening (`SecCARD`, `arXiv:2611.18887`)**: External Agent Cards (`/.well-known/agent-card.json` / `agent.json`) are NOT trusted on JWS signature or OIDC `audience` alone; gate discovery registration behind (1) A2A `v1.0.0` `8`-required-field schema validation, (2) deterministic Unicode-normalized NLP/URL/TF-IDF consistency rules, and (3) a `6 KB`-truncated `<UNTRUSTED_CARD>` check in a dedicated toolless, memoryless frontier-tier LLM judge (`GPT-5.5` `97.0%` perturbation recall at `1.7%` seed FPR; `Gemini 3.1 Flash Lite` `92.3%` at `6.7%` FPR; avoid uncalibrated `8B–14B` judges with `44.0%–46.5%` wild FPR), pinning admitted cards by content hash ([`agent-card-discovery-validation`](../skills/agent-card-discovery-validation/SKILL.md)).

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
- [ ] **Server-Side Authorization**: The recipient authorizes each call from its own permission declaration, keyed to the verified caller identity (OIDC token), and enforces parameter limits there. Agent Card `capabilities` and caller-supplied claims are advertisements, not grants; role splits and data minimization reduce exposure but are not the permission boundary (see `rules/multi-agent-coordination.md` — "DON'T: Share full context across all agents by default").
- [ ] **Grounded Primary-Evidence Forwarding (`arXiv:2611.17520`)**: Never interpose a cheaper/weaker sub-agent as an ungrounded summarizer over untrusted external files or corpora (`20/180–553/900` harmful revisions vs. `2/1,080` direct; `96.3%` aggregator cascade); either match reader model tier or attach verbatim primary source records and provenance headers alongside sub-agent tool returns ([`weakest-agent-delegation-safety-collapse`](../research-briefs/weakest-agent-delegation-safety-collapse.md)).
- [ ] **Byzantine Subtask Aggregation (`SecMAS`, `arXiv:2611.17883`)**: When delegating objective informational subtasks across $m_i \ge 2f_i + 2$ third-party/federated workers, aggregate independent responses via trimmed $(m_i - f_i - 2)$-nearest-neighbor cosine consensus ($f_i = \lfloor (m_i - 2)/2 \rfloor$) rather than LLM summarization or self-confidence scores ([`similarity-consensus-subtask-aggregation`](../skills/similarity-consensus-subtask-aggregation/SKILL.md)).
- [ ] **Live Chain-State Intersection & Branch-Scoped Containment (`Agent-ZTA`, `arXiv:2611.18999`)**: Separate static path-specific token scopes ($D_i^\pi$) from live ancestor-state effective permissions ($E_i^\pi(t,c) \subseteq D_i^\pi$), fail closed (`unavailable -> Deny`) on missing or stale ancestor posture snapshots, and contain downstream anomalies inside the affected workflow branch (`restricted` / `jail` mode on $T_\gamma(t)$) without globally revoking the coordinator across healthy sibling branches ([`agent-zta-bidirectional-chain-state-containment`](../research-briefs/agent-zta-bidirectional-chain-state-containment.md)).
- [ ] **Cross-Layer Persistent Compromise Monitoring (`Swarm Shepherd`, `arXiv:2611.18693`)**: When federated agents share persistent vector/SQLite stores (`L1`), mutable prompts/skills (`L2`), or tool containers (`L3`), run a zero-LLM OTel+eBPF Kalman filter (`n ≈ 8.3 N` retained events/node) fused across `T1–T4` triggers and remediate the **top-3** `2`-hop RTS candidate origins across `L1`/`L2`/`L3` rather than restarting only the visibly failing agent (`R_c = 2.83` visible-only vs. `0.81` staged sanitization; [`multi-layer-compromise-filtering-and-traceback`](../skills/multi-layer-compromise-filtering-and-traceback/SKILL.md)).
- [ ] **Multi-Round Insider Persuasion & Shared-Memory Provenance Hardening (`arXiv:2611.28660`, `arXiv:2611.31307`)**: For interactive multi-round deliberation (where turn-local `W-MSR`/`CP-WBFT`/`SAC` filters and LLM transcript monitors [`13.0%` detection vs. `20.5%` clean false alarm] fail), place untrusted peers at degree-1 `Star-leaf` edges behind a low-sycophancy benign hub, diversify model families (`Gemma` + `Qwen` + `Llama`), and harden open-weight debaters with clean-consistency `DPO` ([`model-based-insider-persuasion-multi-agent-defensive-lessons`](../research-briefs/model-based-insider-persuasion-multi-agent-defensive-lessons.md)). Never admit collaboration transcripts or distilled `G-Memory` insights into shared memory solely because the final team answer succeeded (`94.7%–100.0%` `MIMPA` planting rate, `67.2%` residual Basic `MedMCQA` ASR after post-hoc transcript auditing); require claim-level tool/source grounding, retain `originating_agent_id`, and elicit Round-1 commitments before injecting retrieved memories ([`mimpa-insider-shared-memory-poisoning-defensive-lessons`](../research-briefs/mimpa-insider-shared-memory-poisoning-defensive-lessons.md)).

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
