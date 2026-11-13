# OverServe: Defensive Lessons Against Conjunctive Tool–Prompt Resource Amplification in SaaS Agents

> **Source**: [arXiv:2611.14808](https://arxiv.org/abs/2611.14808) — Ruiheng Yu, Oteo Mamo, Siyu Gan, Weikuan Yu, Mulong Luo (2026)
> **Praxis Source ID**: `src:2611-14808v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

`OverServe` designs an automated red-team synthesis pipeline (`Recon` $\to$ `Writer` $\to$ separate static/runtime/prompt reviewers $\to$ victim rollout selection) that co-designs third-party Model Context Protocol (`MCP`) status tools and user completion-confirmation clauses to trigger **denial-of-efficiency (`DoE`) / resource amplification** against subscription-based SaaS agents. Per the offensive-security policy in [`AGENTS.md`](../AGENTS.md), we omit attack-generation prompts, candidate-refinement search loops, and scanner-evasion wording recipes, and capture **strictly the defensive failure analysis, scanner blind-spot measurements, and architectural mitigations** for multi-tenant MCP/SaaS agent platforms.

---

## Architectural Vulnerability: Component Acceptance vs. Workflow Stopping Safety

Subscription-based and flat-fee SaaS agent platforms absorb LLM token and backend API costs per task while allowing tenants to register third-party MCP integrations and submit natural-language workflow requests. Existing DoE defenses audit **prompts** (blocking explicit loop directives like *"keep calling until complete"*) and **MCP tools** (static AST/YARA scans, description–code consistency checks, and quiescent sandbox execution tests) **in isolation**.

`OverServe` exposes a structural composition gap across three properties:
1. **Truthful, Single-Shot Status Tool ($t_a$)**: The registered MCP tool queries a genuine shared service status endpoint (e.g., directory reconciliation, permission propagation, search-index rebuild, cache warmup), contains **zero** internal loops, prompt-matching branches, fabricated outputs, or re-invocation instructions, and returns `complete` immediately when no background updates are queued.
2. **Ordinary Completion Clause ($q$)**: The tenant appends a benign-looking administrative post-condition to a normal business task $p$ (e.g., creating a team channel and posting an welcome message, plus confirming directory sync has settled before wrapping up) without loop keywords or iteration counts.
3. **Quiescent Audit (`Quiet`) vs. Multi-Tenant Production (`Churn`) Divergence**:
   - In a **quiescent (`quiet`) audit sandbox** where backend state is settled, $t_a$ reports `status = complete` within `<= 2` calls (`r_d(t_a) = 1.0`), adding only `1.25x–1.50x` tool calls (`5` calls vs. `4` clean) and `1.21x` total tokens (`1.02x` prefix-reuse tokens) before the agent terminates normally.
   - In **live multi-tenant production (`churn`)**, legitimate concurrent background writes by other users or services keep global `pending > 0` (`source_version > applied_version`). Even after the agent **completes 100% of the primary business task**, it repeatedly re-polls $t_a$ trying to satisfy $q$ until hitting the platform's hard turn, step, or wall-clock timeout cap.

---

## Key Empirical Findings

### 1. Severe Call, API, Token, and Wall-Clock Amplification While Passing Business Verifiers

Across **4 primary victim models** (`Qwen3.8-27B`, `Nemotron-3-Super` 120B/12B-active, local `DeepSeek-v4-Flash` 284B/13B-active, and `Claude Sonnet-5` on Bedrock; plus `Gemini-3.8-Flash` and hosted `DeepSeek-v4.1-Flash` in transfer studies) and **9 core benchmarks + 1 CLI benchmark** (`MCPMark`, `BrowseComp-Plus`, `STATE-Bench`, `EnterpriseOps-Gym`, `Enterprise-Worlds`, `WorkBench`, `Toolathlon-GYM`, `AppWorld`, `TheAgentCompany`, `Terminal-Bench`), **every reported `OverServe` run passed its native original-task checks**:

| Benchmark / Metric | `Qwen3.8-27B` | `Nemotron-3-Super` | `DeepSeek-v4-Flash` | `Claude Sonnet-5` | Key Takeaway |
|:---|:---:|:---:|:---:|:---:|:---|
| **`AppWorld`** *(API requests)* | `23 -> 213` (`9.26x`) | `26 -> 559.5` (`21.52x`) | `68 -> 1478.5` (`21.74x`) | **`29 -> 2722.5` (`93.88x`)** | Peak **`93.88x`** API amplification (`S/P/D = .95/.70/1`, hits `60`-interaction cap) |
| **`EnterpriseOps-Gym`** *(tool calls)* | **`5 -> 200` (`40.00x`)** | **`5 -> 200` (`40.00x`)** | **`6 -> 201` (`33.50x`)** | `5 -> 26` (`5.20x`) | Exhausts `200`-iteration cap on 3 of 4 models |
| **`WorkBench`** *(tool calls)* | **`2 -> 120` (`60.00x`)** | `2 -> 16` (`8.00x`) | **`2 -> 120` (`60.00x`)** | `2 -> 17` (`8.50x`) | Exhausts `120`-step cap on `Qwen` & `DeepSeek` |
| **`Enterprise-Worlds`** *(tool calls)* | `7.5 -> 200` (`26.67x`) | `6 -> 22` (`3.67x`) | `8 -> 200` (`25.00x`) | `6 -> 16` (`2.67x`) | Exhausts `200`-step orchestration cap |
| **`STATE-Bench`** *(tool calls)* | `4 -> 114` (`28.50x`) | `5 -> 106` (`21.20x`) | `5 -> 107` (`21.40x`) | `6 -> 33` (`5.50x`) | Stopped only by harness `30`-status-read override |
| **`Terminal-Bench`** *(elapsed sec)* | `27 -> 332 s` (`12.12x`) | **`23 -> 1200 s` (`51.76x`)** | `30 -> 1200 s` (`39.34x`) | **`22 -> 1200 s` (`53.48x`)** | Hits `900 s` agent timeout (`~1,200 s` incl. teardown) on 3 of 4 models |
| **5-Enterprise-Benchmark GeoMean** | **`19.30x`** | `8.07x` | **`17.75x`** | `4.07x` | **`10.30x` pooled geometric mean** across `20` victim–benchmark cells |

In matched `40`-turn controlled replays (`96` attack replays across `Qwen3.8-27B` and `Sonnet-5` on `MCPMark TxtMerge` and `EnterpriseOps-Gym`), `OverServe` amplified tool calls **`7.00x–10.00x`** under `churn` (vs. `1.25x–1.50x` in `quiet`), raised **cumulative input/output tokens by a median `8.70x`** (`1.62x` under a prefix-KV-reuse proxy), and passed `24/24` task checks and `2/2` code, runtime, and prompt reviews—whereas single-vector `A2M` (`1.17x–1.50x`) and `LoopTrap` (`2.00x–10.00x` even in `quiet`) failed `0/2` code and `0/2` runtime reviews, and 4-round `STA` prompt rewriting stayed `< 2.00x` (`1.00x–1.83x`).

### 2. Industrial MCP Scanners Miss Truthful Status Tools Completely

Across `22` archived `OverServe` tool specifications (`16` distinct texts, `15` distinct ASTs), **every evaluated industrial scanner and LLM code reviewer raised `0` alerts**:
- **Industrial & LLM Scanners (`0/22` alerts each, `0.0%` recall)**: `Cisco YARA` (`cisco-ai-mcp-scanner v4.8.4`), `Lasso regex` (`MCP Gateway v1.2.1`), `MCPInspect`, `MCPShield` (`v1.0.4`), `Ant MCPScan`, and `LLM tool review`.
- **Research Detectors**: `Repeat-cue` heuristic flagged `0/22` (`0.0%`), `Connor` dynamic component simulation (`<= 8` calls) flagged `1/22` (`4.5%`), `DCI` (description–code inconsistency) flagged `3/22` (`13.6%`), and an auxiliary **changing-pending-output (`No fixed point`)** check under simulated background updates flagged `6/22` (`27.3%`).

### 3. Controlled Causal Ablations Reveal Exact Mitigation Levers

Holding `Qwen3.8-27B`, the `EnterpriseOps-Gym` channel-and-message task, and a `40`-turn budget fixed (`Table 3` & `Appendix D`):
- **Neither component triggers amplification alone**: With the original task prompt + crafted tool, the agent makes `4` total calls (`0` crafted calls) in both `quiet` and `churn`. With the crafted prompt + **no crafted tool**, it makes `7` total calls and stops normally. With both present, calls jump from `5` (`1` status call) in `quiet` to `40` (`36` status calls, `100%` budget hit) in `churn`—even when background updates stop at `45 s`, because queued backlog outlasts the turn window.
- **Pinning Completion to the First-Seen Snapshot Restores Normal Stopping**: Changing the status check from global quiescence (`latest source_version == applied_version`) to **snapshot-pinned completion** (`Check first-seen version`: verifying only that the `source_version` observed at the *first* status query has been applied, ignoring newer concurrent tenant writes) **eliminated budget exhaustion (`0/3` budget hits)** and reduced median total calls from `40` to **`22`** (`18` status calls) while newer updates continued arriving.

---

## Defensive Guardrails for SaaS & MCP Agent Runtimes

1. **Forbid In-Loop LLM Polling of Asynchronous Status Tools — Suspend & Resume Out-of-Band**:
   - Never let an LLM ReAct loop burn inference turns polling `"in_progress"` / `"syncing"` status endpoints. Wrap eventual-consistency and reconciliation operations in asynchronous suspension primitives (`LongRunningFunctionTool` in [`adk-workflow-architecture.md`](../rules/adk-workflow-architecture.md)) or deterministic zero-token external supervisor scripts ([`multi-agent-coordination.md`](../rules/multi-agent-coordination.md)), resuming the agent only once a terminal event/webhook fires or a bounded timeout expires.
2. **Scope Status & Verification Tools to Causal Write Version IDs, Never Global Queue Quiescence**:
   - When an MCP status tool is permitted, require its schema to bind to the **specific mutation receipt or `source_version` snapshot** produced by the current session's own write (`Check first-seen version`), never global tenant/workspace `pending == 0` counters that concurrent users keep non-zero (`40` budget-exhausting calls $\to$ `22` calls with normal stopping).
3. **Enforce Per-Tool Repeat-Call Circuit Breakers & Monotonic-Progress Caps in the Harness**:
   - Global turn caps (`40–200` turns or `900 s`) are too high to prevent `10.30x–93.88x` cost amplification on `2–6` call tasks. Enforce a strict **per-tool consecutive/total status-read cap** (e.g., `<= 2–3` identical-argument status checks per episode, or a hard read-override ceiling as seen in `STATE-Bench`) that terminates polling and returns a structured `"background_pending_handed_off"` receipt once primary task mutations have succeeded.
4. **Test Third-Party MCP Admissions Jointly Under Simulated Concurrent `Churn` + Completion Prompts**:
   - Do not treat `0` alerts from YARA/regex/DCI scanners (`0/22`–`3/22`) or `2`-call convergence in a quiescent sandbox (`r_d = 1.0`) as proof of workflow resource safety. Run pre-admission dynamic probes against a **non-converging / concurrent-churn mock backend** (`No fixed point`) paired with synthetic completion-confirmation prompts to detect unbounded status-polling attractors before exposing third-party MCP tools to tenants.
5. **Align Flat-Rate SaaS Billing with Per-Task Token/Call Quotas**:
   - Enforce per-request and per-tenant token, tool-call, and wall-clock budgets decoupled from business-outcome success checks, charging or throttling runaway post-completion polling rather than absorbing unbounded LLM API spend under flat subscription pricing.

## Related Artifacts

- [`rules/adk-workflow-architecture.md`](../rules/adk-workflow-architecture.md) — `"DO: Suspend multi-minute external operations using LongRunningFunctionTool"`
- [`rules/multi-agent-coordination.md`](../rules/multi-agent-coordination.md) — `"DO: Use deterministic scripts for supervision polling, not LLM calls"`
- [`rules/skill-system-design.md`](../rules/skill-system-design.md) — `"DO: Enforce fast-fail circuit breakers, output schema validation, and grounded-fulfillment gates for MCP tool faults"` and `"DO: Pair static skill checks with safety-constrained sandbox dry-runs and provenance-weighted evidence rather than alert-count thresholds"`
- [`rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md) — `"DO: Pin MCP tool descriptors and isolate offensive execution boundaries"`, `"DON'T: Trust MCP tool metadata without trace-aware vetting"`, and `"DON'T: Treat HTTP 200 / success tool return codes as workflow success without state verification"`
- [`mcp-fault-injection-resilience.md`](mcp-fault-injection-resilience.md) — Retry-cap discipline for MCP tool faults (`arXiv:2610.32555`)
