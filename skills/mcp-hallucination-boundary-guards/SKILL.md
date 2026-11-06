---
name: mcp-hallucination-boundary-guards
description: >
  Runtime boundary guards and trajectory-level evaluation protocol for
  preventing and diagnosing the four primary Model Context Protocol (MCP)
  agent hallucination subtypes: Branch Collapse, Unreachable Goal, Tool
  Misuse, and Context Forgetting. Enforces two-call feasibility probing
  circuit breakers, schema-overlap confusion-tool isolation, explicit branch
  claim-graph tracking, and external state-commitment verification. Derived
  from MCPHallu (arXiv:2611.07689).
source: https://arxiv.org/abs/2611.07689
license: CC-BY-4.0
repository: https://github.com/Marontis/agentic-engineering
---

# MCP Hallucination Boundary Guards

> **Source**: [MCPHallu: Benchmarking Reasoning, Execution, and Memory Hallucinations in MCP Agents](https://arxiv.org/abs/2611.07689) (`src:2611-07689v1`, Jiang et al., Peking University, Zhongguancun Academy, Meituan & HKUST, 2026)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

Use this skill when building, orchestrating, or evaluating tool-using LLM agents connected to multiple Model Context Protocol (`MCP`) servers—especially when servers expose semantically overlapping tools, when tasks contain conditional branching or long distraction chains, or when requested end states may exceed the capabilities or sandbox permissions of the available tool inventory.

## When to Use

- Hardening `MCP` agent loops (`ReAct`, `plan-and-execute`) against false-completion claims on infeasible goals
- Filtering or routing tool catalogs across multiple `MCP` servers that expose overlapping tool names, schemas, or descriptions
- Enforcing state commitment when values retrieved early in a trajectory must be written to stateful files, repositories, or databases after intervening distractors
- Designing subtype-targeted `MCP` evaluation suites where deterministic trajectory and state checks dominate (`70–80%` weight) over LLM-as-a-judge scoring (`20–30%` weight)

## Core Insight

An **MCP agent hallucination** is any trajectory element $\tau = (a_1, o_1, \dots, a_T, o_T, y)$ that the agent treats as valid (presenting it in the final response $y$ or relying on it in downstream actions without flagging inconsistency) when it violates the task instruction $I$, the live environment state, or the actual capabilities of the available tools $\mathcal{T}$. Honest failure (asking for clarification, reporting infeasibility, or surfacing a tool error) is *not* a hallucination; the defining flaw is an **implicit validity claim** over an inconsistent element.

Across **14 frontier LLMs** from **8 vendors** evaluated on **5,012 trajectories** (`358` tasks across `5` capability domains—`Coding` [`80`], `General` [`75`], `Financial` [`73`], `Analytics` [`69`], `Productivity` [`61`]—and `36` isolated production `MCP` servers exposing `~300` tools), the mean overall score is only **0.642** (`47.8%` pass rate), with the best model (`Claude Opus 4.6`) reaching **0.728** vs **0.88** for expert humans (`40`-task stratified sample). Crucially:
1. **Continued Tool Use Amplifies False Completion on Unreachable Goals**: `Unreachable Goal` is the hardest subtype across `12 of 14` models (mean score **0.458**, `23.2%` pass rate; `0.246` in stateful `Coding`). Runs that declare infeasibility at **0 tool calls pass 65.0%** (`320` runs, mean `0.778`, `0.6%` completion language), runs making **1–3 probing calls pass 27.9%** (`455` runs, mean `0.569`, `13.8%` completion language), and **every run making $\ge 4$ tool calls passes 0.0% of the time** (`266` runs at `4–7` calls, `158` at `8–15`, `243` at `16+`) while completion-style language (`successfully`, `saved`, `created`) climbs to **36.7%** at `8–15` calls. Overall, agents that stop and declare infeasibility pass **48.0%** (`448` runs) vs **0.0%** when they keep acting without declaring infeasibility (`517` runs).
2. **Calling Confusion Tools Contaminates Downstream Reasoning (`Tool Indiscipline`)**: On `Tool Misuse`, trajectories that invoke *only* the target tool pass **84.7%** of the time (`825` runs, mean `0.927`, `3.54` average steps), whereas invoking a semantically overlapping confusion tool *alongside* the correct tool collapses the pass rate to **32.3%** (`260` runs, mean `0.649`, `10.70` average steps, `3.42` confusion calls)—even though the required tool output is in the context!
3. **External State Non-Commitment Dominates Memory Failures**: On `Context Forgetting`, stateless tasks (`General`/`Analytics`/`Financial`, `644` runs) achieve a **59.2%** pass rate (`0.713` mean score, `7.17` steps), whereas stateful tasks requiring the remembered value to be written back to live state (`Productivity`/`Coding`, `504` runs) drop by **34.6 percentage points to 24.6%** (`0.431` mean score, `11.46` steps).
4. **Subtype Capabilities Are Dissociated**: Model rankings shift by an average of **6.86 out of 13 positions** across the four subtypes, and `Branch Collapse` is uncorrelated with `Unreachable Goal` ($r = -0.12$). `Claude Opus 4.6` ranks `#1` overall (`0.728`), `#1` on `Context Forgetting` (`0.730`), and `#1` on `Tool Misuse` (`0.885`), but `#7` on `Branch Collapse` (`0.755`, where `Claude Opus 4.5` leads at `0.867` and `DeepSeek-V4` ranks `#2` at `0.853`), while `Claude Sonnet 4.6` leads `Unreachable Goal` (`0.585`).

---

## Procedure: Runtime Boundary Guards Across the Four Subtypes

### Guard 1: Pre-Flight Capability Check & Two-Call Probing Circuit Breaker (`Unreachable Goal`)

To prevent the **void-trap** failure mode—where an agent completes a feasible read phase (e.g., reading `git_git_log`) and then hallucinates success on an impossible write phase (e.g., writing `/data/repos/mcp-server-calculator/CONTRIBUTORS.md` when shell redirection is disabled and code-executor tools only write inside their own workspace):

1. **Bind Required Terminal Side Effects to Tool Schemas at $t = 0$**: Before issuing the first tool call, decompose the instruction $I$ into required read dependencies and required terminal state mutations (target paths, target servers, required write permissions). Check whether at least one tool in $\mathcal{T}$ exposes an input schema and path/permission scope capable of realizing the terminal state.
2. **Allow at Most $k = 2$ Diagnostic Probing Calls When Feasibility Is Data-Dependent**: If capability feasibility cannot be settled from static schemas alone, permit a maximum probing window of **$k = 2$ tool calls** (one capability/security-rule inspection call plus one trial call).
3. **Enforce a Hard Abstention Circuit Breaker Before Call 4**: If no tool can satisfy the terminal goal after $k \le 2$ probes—or if `3` consecutive calls fail to advance the terminal precondition—halt execution immediately and emit an explicit **Limitation Report** (`cannot`, `unable`, `not possible`, `restricted`) naming the missing tool capability or sandbox restriction.
   - **Never** substitute a write to a scratch workspace for a requested repository path, and **never** emit completion language (`successfully`, `saved`, `created`, `done`, `finished`) when the target state mutation was rejected (`Completion-only` responses pass only `2.1%` across `195` runs vs `44.4%` for `Limitation-only` across `304` runs).
   - **Avoid blanket refusal**: Feasible tasks account for `255 of 358` tasks (`71.2%`); declining without checking schemas or probing passes only `8.0%` on `Tool Misuse` (`75` runs). Note that adding a `plan-and-execute` turn or an `infeasibility-aware system prompt` on `GPT-5` (`80`-task ablation) raises `Unreachable Goal` from `0.45` to `0.52` and `0.56` (`+0.07` and `+0.11`), confirming that prompt scaffolding must be paired with runtime step-count enforcement.

### Guard 2: Pre-Invocation Schema Disambiguation & Confusion-Tool Quarantine (`Tool Misuse`)

When an MCP environment exposes $\ge 2$ tools with overlapping names, descriptions, or parameter schemas (e.g., `git_git_show` for a commit's patch vs `git_git_diff` with `target=HEAD`, or `twelvedata_GetQuote` vs `twelvedata_GetPrice`):

1. **Contrast Sibling Tool Semantics Before Calling**: Whenever candidate tools share entity nouns or parameter keys, compare three exact specification fields before invoking any tool:
   - Exact **parameter semantics** (e.g., single commit revision vs working-tree comparison target).
   - Documented **return-value schema** (which fields are actually returned).
   - Exact **operation requested in $I$** (median required sequence on `Tool Misuse` is only `2` calls, range `2–5`).
2. **Never "Call Everything That Might Help"**: Do not invoke sibling confusion tools as exploratory fallbacks. Once a confusion tool's output enters the conversation history, it contaminates downstream reasoning (`32.3%` pass rate and `10.70` steps for `Correct + confusion` vs `84.7%` pass rate and `3.54` steps for `Correct only`).
3. **Quarantine Off-Target Outputs**: If an exploratory call returns a schema or semantic mismatch, explicitly mark that observation as `INVALID_FOR_TARGET_CLAIM` in the scratchpad and exclude its values from final synthesis.

### Guard 3: Per-Entity Branch Ledger & Claim-Graph Verification (`Branch Collapse`)

When a task contains $\ge 2$ mutually exclusive conditional branches gated on live tool outputs (or multi-entity parallel branches, such as evaluating `abs(percent_change) >= 1.5` independently for `AAPL` and `MSFT` to choose between `14-period RSI` on `Branch A` and `20-period Bollinger Bands` on `Branch B`, followed by a branch-conditioned tie-break ordering):

1. **Construct an Explicit Branch Selection Table Before Execution**: Enumerate every branch (`A`, `B`, `C`, ...) with:
   - The exact decision tool and output field (accessed defensively via `.get()` rather than raw key indexing).
   - The concrete numerical, boolean, or categorical predicate.
   - The mandatory downstream tool chain exclusive to that branch.
2. **Isolate Multi-Entity Branch State**: Maintain a structured per-entity row `(entity_id, decision_field_value, triggered_branch_letter, branch_tool_called, branch_output)` so that a failed or missing call on one entity is never filled using another entity's branch output, and inactive branch tools are never called (which prevents creating forbidden wrong-branch side-effect files).
3. **Verify Aggregation & Tie-Break Constraints Against the Ledger**: Before emitting the final response $y$, re-verify every ordering, aggregation, and tie-break rule (e.g., `abs(percent_change)` ordering when two entities trigger the same branch) against the recorded decision values (`Branch Collapse` requires a median of `7` tool calls, range `4–15`).

### Guard 4: Key-Value Pinning & Post-Write State Assertion (`Context Forgetting`)

When values retrieved early in a trajectory must survive intervening same-domain distractor tool calls and be committed to an external artifact (`Context Forgetting`, median `7` calls, range `5–13`):

1. **Pin Early Retrieved Target Values in an Immutable Scratchpad Slot**: Immediately upon retrieving a target identifier, metric, or record field in early steps, record its exact literal value and source step in a pinned `COMMITTED_VALUES` block separate from subsequent distractor observations.
2. **Audit External State Commitment on Stateful Tasks**: On stateful `Productivity` and `Coding` tasks (where pass rate otherwise drops from `59.2%` to `24.6%`), do not stop after generating the value in prose. Execute the required file/database write tool (strictly within allowed sandbox paths such as `/data/` or `/data/repos/<repo>`) and run a post-write read/status check to confirm that the exact pinned value—not a stale, approximate, or distractor-substituted value—persists in the external state before finishing.

---

## Procedure: Subtype-Targeted MCP Benchmark & Evaluation Design

When evaluating MCP agents in CI/CD or model selection:

1. **Weight Deterministic Evidence at 70–80% and LLM Judge at 20–30%**:
   - **Branch Collapse & Context Forgetting**: Score `60%` Executable Outcome ($S_o$: live-server dynamic reference script output for stateless tasks; fraction of satisfied post-execution Python `eval()` state assertions over `os`/`json`/`re` for stateful tasks) + `20%` Claim-Graph Dependency Satisfaction ($S_d = 1 - \frac{\#\{\text{violated edges}\}}{\max(1, \#\{\text{checked edges}\})}$, ignoring inactive branches) + `20%` LLM Judge ($S_j$).
   - **Unreachable Goal**: Score `70%` Early-Stop Structural Score ($S_e = 1$ if infeasibility is declared within $k = 2$ probing calls, decaying linearly as $S_e = \max(0, 1 - (t_{\text{stop}} - k)/(T_{\max} - k))$ up to $T_{\max} = 20$, and $0$ if never declared) + `30%` LLM Judge ($S_j$, verifying that early termination articulated infeasibility rather than budget exhaustion).
   - **Tool Misuse**: Score `70%` Confusion-Avoidance Score ($S_c = 1 - \frac{|U_c \cap U_{\text{trajectory}}|}{\max(1, |U_c|)}$, counting distinct curated confusion tools $U_c$ invoked) + `30%` LLM Judge ($S_j$, verifying grounding in the target tool).
   - *Validation*: Deterministic-only rankings correlate with the full multi-component score at Spearman $\rho = 0.97$ (max rank change `2` positions vs $r = 0.86$ for judge-only), and in **71%** of trajectories where $S_j$ and the multi-component score disagree by $> 0.2$, the agent produced the right final outcome via the wrong tool path or the wrong final outcome via the right tool path. Cross-judge substitution (`Claude Sonnet 4.5` vs `GPT-4o` on `120` tasks) shifts scores by at most `0.016` ($r = 0.914$; `GPT-4o` self-preference is `0.013`, well below the `0.028` mean gap between adjacent models).
2. **Report Per-Subtype Scores Alongside Aggregate Score**: Never select an MCP model by aggregate score alone; match the model's subtype profile (Table 5 of `arXiv:2611.07689`) to the deployment's dominant risk (conditional branching vs cross-server schema overlap vs stateful writes vs infeasible user requests).

---

## Related Rules & Skills

- [`skill-system-design.md`](../../rules/skill-system-design.md) — MCP fault-tolerance, fast-fail circuit breakers, and tool-selection discipline
- [`agent-evaluation-quality.md`](../../rules/agent-evaluation-quality.md) — Multi-component deterministic + bounded-judge evaluation design
- [`necessary-tool-evidence-path`](../necessary-tool-evidence-path/SKILL.md) — Eliminating redundant tool calls and aligning pre-call intent with evidence gaps
