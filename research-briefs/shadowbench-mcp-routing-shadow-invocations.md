# ShadowBench-MCP: Measuring Shadow Invocations in MCP-Style Tool Routing

> **Source**: [arXiv:2611.11720](https://arxiv.org/abs/2611.11720) — Eyhab Al-Masri, Wenjun Yang (2026)
> **Praxis Source ID**: `src:2611-11720v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

`ShadowBench-MCP` is a focused benchmark, pre-execution metric suite, and single-router policy-ablation study (`120` routing decisions yielding `96` pairwise comparisons on `qwen/qwen3-32b`) rather than a complete, self-contained implementation procedure: the paper defines the high-level composite formula $\mathrm{SODS} = \mathrm{TPSS} \times \mathrm{OPSS} \times \mathrm{RGAS}$ and reports comparative mitigation trade-offs, but omits the exact mathematical equations for computing the sub-metrics (`TPSS`, `OPSS`, `RGAS`) and the internal mechanics of its `consensus replay` and `policy-constrained` router baselines. Its primary value is establishing **shadow invocation** as a distinct routing-layer failure mode and quantifying the safety-vs.-review trade-off for rules in [`agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md).

---

## Threat Model: Shadow Invocation as a Routing-Layer Failure (`Sections 1–2`)

Unlike direct or indirect prompt injection—where an adversary injects an unrelated malicious goal, poisons MCP tool metadata, or tampers with tool outputs—a **shadow invocation** occurs under a purely black-box, task-preserving user request:

- **Adversary Capability**: Controls only the input request wording; cannot modify model weights, tool descriptions, MCP server configurations, or backend policies.
- **Mechanism (Covert Operational Channel)**: Two requests preserve the exact same legitimate workflow objective (e.g., patching a vulnerable dependency), but the variant appends benign-looking operational pressure (`"use the fastest path"`, `"skip slow validation"`, `"deploy directly"`, or `"defer audit"`).
- **Security Consequence**: When route selection is delegated to a probabilistic LLM router without mandatory safety-chain constraints, operational pressure steers the router toward shortcut tools that drop validation, provenance checks, staging, redaction, access checks, or audit logging before any tool executes.

---

## Benchmark & Pre-Execution Metric Suite (`Sections 3–4`)

`ShadowBench-MCP` evaluates **six security-sensitive workflows** (*software maintenance*, *vulnerability patching*, *dependency update*, *CI/CD deployment*, *financial data export*, and *incident triage*) across **five request styles** (`1` original request + `4` task-preserving operational-pressure variants: `fast path`, `skip validation`, `direct deploy`, and `defer audit/checks`).

Using a Groq-hosted `qwen/qwen3-32b` router (`top-k = 5` ranked tool chains, `2` repetitions, `0` API errors), the study collects $6 \times 5 \times 2 \times 2 = 120$ routing decisions (`96` original–variant pairs: `48` per policy) across two routing policies:
1. **Unprotected (Efficiency-First)**: Instructs the router to select an efficient toolchain minimizing latency, developer effort, and operational cost, without declaring safety tools mandatory.
2. **Protected (Policy-Aware)**: Explicitly mandates that security validation, provenance checks, policy gates, audit logging, staging, redaction, access checks, and regression testing must not be skipped when relevant.

Each pair is scored before tool execution using:
- **`SIR` (Shadow Invocation Rate)** and **Safety-Tool Skip Rate** (fraction of required safety tools omitted from the variant route).
- **`TPSS`** (normalized same-task preservation score after discounting operational-pressure phrasing) and **`OPSS`** (normalized shortcut/skip/defer/direct-deploy pressure score)—held identical across policies (`mean TPSS = 0.807`, `mean OPSS = 0.389`) because they characterize the input pair.
- **`RGAS` (Route-Geometric Anomaly Score)**: Summarizes movement in tool-routing space across route direction, Jaccard distance, local-neighborhood shift, safe-tool loss, and risky-tool gain (with **`DUS`** as a generic tool-ranking disagreement baseline).
- **`SODS` (Semantic-Operational Drift Score)**:
  $$\mathrm{SODS} = \mathrm{TPSS} \times \mathrm{OPSS} \times \mathrm{RGAS}$$
  High only when the request stays on-task, carries operational pressure, and induces route-level geometric drift.

---

## Quantitative Findings (`Sections 5–6`, `Tables 1–2`)

### 1. Explicit Policy Constraints Cut Shadow Invocations by `85.7%` (`Table 1`)

| Routing Policy (`48` pairs each) | `SIR` (Shadow Invocation Rate) | Required Safety-Tool Skip | Mean Risk Shift | Mean `RGAS` | Mean `SODS` |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Unprotected (Efficiency-First)** | **`29.2%`** (`14/48`) | **`26.7%`** | `0.028` | `0.059` | `0.019` |
| **Protected (Policy-Aware)** | **`4.2%`** (`2/48`) | **`1.7%`** | `0.005` | `0.011` | `0.003` |

- Making safety-tool retention explicit in the routing policy yields an **`85.7%` relative reduction** in shadow invocations ($(29.2 - 4.2) / 29.2 = 85.7\%$) and cuts required safety-tool skipping from `26.7%` to `1.7%`, while still leaving a **`4.2%` residual** (`2/48`)—confirming that prompt-level policy awareness alone is not a `0%` hard gate.

### 2. Route-Drift Correlation & Pre-Execution Detection (`Sections 5.2 & 6.1`)
- Across all `96` pairs, route-drift signals form a coherent cluster distinct from input phrasing (`TPSS`/`OPSS`): `SODS` correlates with `RGAS` ($r = 0.88$), local-neighborhood shift ($0.76$), directional drift ($0.71$), route Jaccard distance ($0.71$), risky-tool gain ($0.69$), and risk shift ($0.67$), while directional drift correlates with neighborhood shift at $0.94$ and risk shift with risky-tool gain at $0.90$.
- On the `48` unprotected pairs (`14` shadow vs. `34` non-shadow routes), pre-execution route signals separate shadow routes with **ROC AUC `0.94`** for **safety-skip delta**, **`0.90`** for **positive risk shift**, **`0.88`** each for **route Jaccard distance** and **`RGAS`**, **`0.84`** for **`SODS`**, and **`0.83`** for the generic **`DUS`** baseline.

### 3. Coverage vs. Review Burden Trade-Off (`Section 6.2`, `Table 2`)

| Pre-Execution Defense (on `48` Unprotected Pairs) | Shadow Routes Blocked | Pairs Escalated for Review | Review Precision |
|:---|:---:|:---:|:---:|
| **Consensus Replay** | `57.1%` (`8/14`) | `16.7%` (`8/48`) | `100%` (`8/8`) |
| **Policy-Constrained Routing** | `100%` (`14/14`) | `43.8%` (`21/48`) | `66.7%` (`14/21`) |

Blocking `100%` of shadow routes under unprotected efficiency-first routing required reviewing **`43.8%`** of all pairs (`66.7%` precision), whereas `consensus replay` achieved zero false positives (`100%` precision, `16.7%` review rate) but missed `42.9%` (`6/14`) of shadow routes.

---

## Limitations & Relevance to Praxis

- **Single-Router Scope**: All results come from a single Groq-hosted `qwen/qwen3-32b` model over `6` workflow templates (`120` decisions, non-i.i.d. template pairs), so population-level generalization across frontier and open-weight routers remains open.
- **Architectural Implication**: Complements [`intent-ltl-mcp-orchestration`](../skills/intent-ltl-mcp-orchestration/SKILL.md) and [`verified-telemetry-tool-routing`](../skills/verified-telemetry-tool-routing/SKILL.md): preserving user task intent does *not* preserve execution-path safety. Efficiency-first prompts actively incentivize skipping validation, staging, and audit tools (`26.7%` skip rate), requiring both explicit non-skippable safety-tool policy declarations and pre-execution safety-skip delta checks calibrated to human review capacity.
