---
name: verified-telemetry-tool-routing
description: Project host-verified runtime telemetry (rolling failure rates, latency EWMA, consecutive failures, circuit state, and observation age) into a bounded, freshness-labeled Substrate State Telemetry (SST) snapshot before operational tool selection while retaining host dispatch authority. Derived from Agrawal & Nagpal (arXiv:2611.05391).
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Verified Telemetry Tool Routing

> **Source**: [arXiv:2611.05391](https://arxiv.org/abs/2611.05391) | `src:2611-05391`
> **Derived from**: *Agent Harness Awareness: Turning Verified Telemetry into Operational Control for Tool-Using Agents* (Agrawal & Nagpal, 2026)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

Use this skill whenever an LLM agent selects among multiple semantically equivalent or overlapping tools, API endpoints, MCP servers, database replicas, or execution actions (`wait`, `degrade`, `escalate`) in an environment where runtime health varies over time:

- Multiple candidate routes satisfy the semantic contract of the user's request, so static tool descriptions and JSON schemas cannot distinguish a healthy route from one experiencing elevated latency, HTTP 503 errors, or an open circuit breaker.
- Agents exhibit strong default naming or ordering biases when runtime state is omitted (selecting `tool_alpha` in `17/18` (`94.4%`) task-only and neutral-control decisions in live fault injection, including `7/8` cases where `tool_beta` was listed first).
- Raw observability streams (full OpenTelemetry trace trees, raw stack traces, or unbounded log histories) are too noisy, stale, or prompt-injection-prone to dump directly into the agent context window.

Do **not** use this skill to delegate hard safety, authorization, or quota enforcement to the LLM; the host harness must always retain final policy revalidation and dispatch authority.

## Core Concepts

### 1. Separating Semantic Discovery from Operational Selection
Tool selection in production harnesses comprises two distinct subproblems:
1. **Semantic Discovery**: Identifying which candidate tools or routes $a_t \in \mathcal{A}_{\text{sem}}(x_t)$ have the capability and input/output schema required to accomplish task $x_t$.
2. **Operational Selection**: Choosing which semantically eligible route $a_t$ is operationally viable right now given live substrate conditions (transient outages, tail latency spikes, rate limits, or circuit-breaker states), or choosing an explicit control action (`wait`, `degrade`, `escalate`) when all routes are unhealthy.

Providing only static tool schemas forces the model to guess operational health from tool names or argument shapes. Across `216` controlled decisions (`3` frontier models $\times$ `6` seeds $\times$ `4` environment regimes $\times$ `3` conditions) and `27` live OpenTelemetry + Toxiproxy fault decisions, projecting verified host telemetry into the operational selection step reduced mean policy regret by **`96.9%`** against a same-shape neutral structural control (`4,251.54 ms` $\to$ `131.12 ms`) and **`97.3%`** against a task-only prompt (`4,826.45 ms` $\to$ `131.12 ms`), while raising single-dispatch task completion from `65.3%` (`47/72`) and `69.4%` (`50/72`) to **`95.8%`** (`69/72`) in Study 1 and from `66.7%` (`6/9`) and `55.6%` (`5/9`) to **`100.0%`** (`9/9`, `0.00 ms` regret) in live transport fault testing.

### 2. The Substrate State Telemetry (`SST`) Contract
Instead of exposing raw logs or letting the model infer health from narrative error strings, the host harness runs a deterministic reducer $\phi(h_t) = z_t$ over recent execution spans $h_t$ to produce a bounded, redacted, freshness-labeled state snapshot $z_t$ per candidate route. Crucially, the ablation between **Condition B** (an identical-schema envelope populated with neutral constant values) and **Condition C** (verified live values) proves that the gain comes from **verified state values**, not prompt formatting or schema scaffolding (`69.4%` vs. `95.8%` completion; `8,956.37 ms` vs. `0.00 ms` regret in live faults).

### 3. Split Authority Between Model Policy and Host Harness
`Agent Harness Awareness` preserves a strict authority boundary:
- **Host Harness Owns**: Telemetry measurement ($h_t$), deterministic reduction and redaction ($\phi(h_t) = z_t$), freshness enforcement, pre-dispatch revalidation, hard circuit-breaker / permission enforcement, and final execution.
- **Model Policy Owns**: Conditioning its choice $\pi(a_t \mid x_t, z_t)$ over semantically valid routes and operational fallbacks (`wait`, `degrade`, `escalate`) on both task requirements $x_t$ and the verified state snapshot $z_t$.

## Procedure

### Step 1: Instrument Host-Owned Route Spans
At the harness dispatch boundary, wrap every tool or endpoint invocation in a structured telemetry span (e.g., an OpenTelemetry span) capturing:
1. Route identifier $r \in \mathcal{R}$.
2. Wall-clock duration $\ell$ (in milliseconds) and completion timestamp.
3. Binary outcome (success vs. transport/timeout/HTTP 5xx failure) and a sanitized, fixed-vocabulary error code (`NONE`, `TIMEOUT`, `CONN_FAIL`, `HTTP_503`, `RATE_LIMIT`).

### Step 2: Compute the Deterministic `SST` Snapshot $z_t = \phi(h_t)$
Before asking the model to choose among semantically eligible routes $\mathcal{A}_{\text{sem}}(x_t)$, run a host-side deterministic reducer $\phi$ over the trailing observation window for each candidate route $r$ to compute seven bounded fields:

| Field | Definition & Recommended Parameterization | Purpose |
|:---|:---|:---|
| `window` ($n$) | Count of recent probe or invocation spans inside the rolling window (e.g., $n = 3$ to $6$). | Establishes sample support; when $n = 0$, treat failure prior as $p_f = 0.5$. |
| `succ` ($s$) | Count of successful spans in `window` ($0 \le s \le n$), yielding empirical failure rate $p_f = (n - s)/n$. | Quantifies recent reliability without exposing raw payloads. |
| `consec_fail` | Count of consecutive failures at the tail of the window. | Triggers immediate circuit transitions on hard outages. |
| `latency_ewma` ($\ell$) | Exponentially weighted moving average of route latency in milliseconds (e.g., $\alpha = 0.2$). | Captures latency degradation (such as a `300 ms` toxic delay) even when requests still succeed. |
| `last_err` | Enum-constrained code of the most recent failure (`NONE` if last call succeeded). | Gives actionable failure mode without leaking untrusted error text. |
| `circuit` ($q$) | Deterministic state machine: `OPEN` if `consec_fail` $\ge 3$; `DEGRADED` if $p_f \ge 0.4$ (and not `OPEN`); otherwise `CLOSED`. | Summarizes operational readiness into a discrete regime. |
| `age` | Milliseconds elapsed since the most recent span in `window` was recorded, checked against a freshness bound (e.g., `2,000 ms`). | Prevents routing on stale health snapshots after a state transition. |

### Step 3: Inject the `SST` Block Alongside Explicit Fallback Actions
1. Format $z_t$ as a compact, deterministic key-value or tabular block attached only to the candidate routes in $\mathcal{A}_{\text{sem}}(x_t)$.
2. Randomize or canonicalize route presentation order if desired, though verified `SST` values alone eliminate the `94.4%` (`17/18`) default route-name bias observed in task-only and neutral-envelope prompts.
3. Explicitly include operational control actions alongside tool routes in the decision space:
   - Select the lowest-cost healthy route ($q = \text{CLOSED}$, low $p_f$, low $\ell$) when at least one candidate route is healthy.
   - Select `wait` (backoff and re-probe), `degrade` (use a lower-fidelity fallback), or `escalate` when **all** semantically eligible routes are simultaneously `OPEN` or severely `DEGRADED`.

### Step 4: Evaluate Route Selection Against Observable Regret
When scoring or auditing operational routing decisions (in offline evaluation or online monitoring), compute the observable route cost $c_{\text{obs}}(r, z)$ for each candidate route $r$:
$$c_{\text{obs}}(r, z) = \ell + 10{,}000\,p_f + 10{,}000\,\mathbf{1}[q = \text{OPEN}]\text{ ms}$$
where $\ell$ is `latency_ewma`, $p_f = (n - s)/n$ (or $0.5$ when $n = 0$), and $\mathbf{1}[q = \text{OPEN}]$ penalizes open circuits. Measure policy regret relative to the best observable route at step $t$:
$$r_{\text{obs}}(r, z) = c_{\text{obs}}(r, z) - \min_{r' \in \mathcal{R}} c_{\text{obs}}(r', z)$$
Penalize unnecessary `wait` actions when a healthy route exists via $r_{\text{obs}}(\texttt{wait}, z) = 500 + 10{,}000 - \min_{r \in \mathcal{R}} c_{\text{obs}}(r, z)\text{ ms}$, while rewarding `wait` when all routes exceed healthy cost thresholds.

### Step 5: Revalidate at the Host Dispatch Gate
When the model emits its chosen action $a_t$:
1. Verify at the host boundary that $z_t$ has not exceeded the freshness bound (`age` $\le 2{,}000\text{ ms}$) and that the selected route's circuit has not transitioned to `OPEN` since $z_t$ was projected.
2. Enforce hard authorization, budget, and circuit-breaker blocks deterministically in the host before executing the tool call, then append the new execution span to $h_{t+1}$.

## Pitfalls

- **Adding telemetry schema fields with placeholder, cached, or unverified defaults (`Condition B` trap)**: Populating an `SST` block with static or unverified "healthy" defaults (`window=6, succ=6, consec_fail=0, latency_ewma=1000.0ms, circuit=CLOSED`) gives the model false confidence and performs no better—or worse—than omitting telemetry altogether (`55.6%` vs. `66.7%` completion and `8,956.37 ms` vs. `6,734.30 ms` regret under live faults). If telemetry is stale beyond the freshness threshold, mark it explicitly as unknown/stale ($n = 0, p_f = 0.5$) rather than defaulting to `CLOSED`.
- **Dumping raw exception strings or full trace payloads into $z_t$**: Unbounded error messages bloat the context window and create an indirect prompt-injection vector from external endpoints. Always project errors through a fixed host-side enum (`last_err`).
- **Omitting a non-dispatch fallback (`wait` / `degrade`) when all routes fail**: If every equivalent tool is experiencing an outage and the action space only allows picking a tool, the model is forced to dispatch into a broken endpoint. Always provide an explicit `wait` or `escalate` action for dual-degraded states.
- **Letting model selection override a hard host circuit breaker**: `SST` informs model routing so the agent avoids broken routes on its first attempt (`95.8%`–`100.0%` single-dispatch completion), but the host harness must still enforce hard `OPEN`-circuit and safety blocks deterministically if the model selects an unavailable route.

## Verification

Verify your `SST` routing integration with the following checks:

1. **Three-Condition Ablation Test**: Run a fault-injection test across three conditions—Task-Only (`A`), Neutral Same-Shape Envelope (`B`), and Live Verified `SST` (`C`)—under latency spike (`+300 ms`), connection drop, and `HTTP 503` faults. Confirm that `Condition C` achieves near-zero observable regret (`0 ms` on single-fault routing) and eliminates `A`/`B`'s preference for the first-listed or alpha-named tool.
2. **Dual-Degradation Abstention Check**: Inject simultaneous faults into all equivalent routes and verify that the agent selects `wait` or `escalate` rather than blindly dispatching to a failing route.
3. **Freshness & Redaction Audit**: Inspect the serialized $z_t$ blocks passed to the model to confirm every route entry contains only the bounded numerical/enum fields (`window`, `succ`, `consec_fail`, `latency_ewma`, `last_err`, `circuit`, `age`) with zero raw response bodies or unredacted stack traces.
