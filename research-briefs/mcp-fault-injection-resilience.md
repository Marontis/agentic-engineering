# Tool-Calling LLM Agents Under Realistic MCP Faults: Scale Does Not Purchase Fault Tolerance

> **Source**: [arXiv:2610.32555](https://arxiv.org/abs/2610.32555) — *"Tool-Calling LLM Agents Under Realistic MCP Faults: Scale Does Not Purchase Fault Tolerance"* (Oct 2026)
> **Praxis Source ID**: `src:2610-32555`
> **Tier**: Research Brief
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Summary & Empirical Fault Taxonomy

Benchmarks for Model Context Protocol (MCP) agents almost universally assume that tool servers return well-formed responses within normal latency bounds. To measure how production tool-calling agents behave when that assumption fails, the authors mine **103,166 consolidated issue, pull-request, commit, and review threads** across **1,774 active public MCP tool-server repositories**, classify **57,240 English-language threads** (validated against human annotators at Cohen's $\kappa = 0.93$ for failure mode and $\kappa = 0.80$ for persistence), and isolate **14,829 real-world MCP failures** (`13,824` injectable `(mode, persistence)` instances).

From this empirical distribution, they build **MCP-Injector**, a transparent HTTP reverse proxy between the MCP client and tool server that intercepts JSON-RPC `tools/call` traffic without modifying agent or server code, and run a **1,350-cell full-factorial experiment**:
- **2 open-weight reasoning models**: `gpt-oss-20B` and `gpt-oss-120B` (`6x` parameter scale difference, local vLLM MXFP4, `16k` context).
- **3 orchestration stacks**: `MCP-Bench` (custom multi-round plan-and-execute, 40-round cap), `OpenAI Agents SDK` (single-agent loop, 40-turn cap), and `LangChain / LangGraph` (ReAct graph, 25-superstep cap), each with a `3,000 s` per-task wall-clock timeout.
- **3 proxy conditions**: `Proxy-off` (direct connection), `OP0` (null pass-through proxy control), and `OPP` (18-rule empirically calibrated fault profile).
- **25 single-server MCP-Bench tasks $\times$ 3 seeds** (`450` `OPP` cells paired directly against `450` `OP0` baseline cells).

### Ecosystem Fault Distribution across 1,774 MCP Repositories ($N = 13,824$ Injectable Faults)

Real-world MCP server faults are overwhelmingly **permanent (`91.3%`, `12,616` threads)** rather than **intermittent (`8.0%`, `1,104` threads)** or **transient (`0.75%`, `104` threads)**, and nearly `30%` are silent content corruptions (`19.1%`) or timing hangs/delays (`9.7%`):

| Operator | Failure Mode | Category | Permanent | Intermittent | Transient | Total Share (`N = 13,824`) | Proxy Injection Behavior |
|:---|:---|:---|:---|:---|:---|:---|:---|
| **`OP4`** | `EXPLICIT_ERROR` | Content | `9,075` (`65.65%`) | `669` (`4.84%`) | `97` (`0.70%`) | **`71.2%`** (`10,393`*) | Replaces result with JSON-RPC `-32603` internal error |
| **`OP2`** | `INCORRECT_OUTPUT` | Silent Content | `1,733` (`12.54%`) | `155` (`1.12%`) | `1` (`0.01%`) | **`13.7%`** (`1,939`*) | Plausible wrong values (`prob = 0.35` word substitution) |
| **`OP6`** | `SILENT_DROP` | Timing | `963` (`6.97%`) | `167` (`1.21%`) | `4` (`0.03%`) | **`8.2%`** (`1,217`*) | Holds TCP connection open indefinitely until client timeout |
| **`OP3`** | `INVALID_OUTPUT` | Silent Content | `511` (`3.70%`) | `47` (`0.34%`) | `1` (`0.01%`) | **`4.0%`** (`584`*) | Schema/type corruption (e.g., coercing `str -> int`) |
| **`OP5`** | `DELAYED_RESPONSE` | Timing | `157` (`1.14%`) | `51` (`0.37%`) | `1` (`0.01%`) | **`1.5%`** (`233`*) | Sleeps `30 s` (below 60s HTTP timeout) before forwarding |
| **`OP1`** | `MINOR_MISTAKE` | Silent Content | `177` (`1.28%`) | `15` (`0.11%`) | `0` (`0.00%`) | **`1.4%`** (`202`*) | Character-level corruption (`prob = 0.08, delta = 0.05`) |

*\*Total counts include threads with uncertain persistence; percentages in parentheses are the exact 18-rule `OPP` sampling weights over the `13,824` fully classified `(mode, persistence)` instances.*

---

## Headline Experimental Findings

### 1. Realistic MCP Faults Cut Task-Completion Quality by `60%` (`8.08 -> 3.23 / 10`)

Pooled across all stacks and models, injecting the ecosystem-calibrated fault profile (`OPP`) collapses mean task-completion score from **`8.08` to `3.23` out of `10`**—a **`60%` drop** (paired $\Delta = -4.85$, 95% CI `[-5.22, -4.48]`, rank-biserial $r \approx 0.9$, Wilcoxon $p < 0.001$; **`67%` drop** when excluding the `55` zero-dose cells where no fault fired; **`57%` drop** among completed-only runs). Across the sub-dimensions:
- Planning effectiveness drops **`67%`**, tool selection drops **`59%`**, and the remaining six rubric dimensions drop **`54%–68%`**.
- **Silent partial degradation dominates (`56%` of all `OPP` cells)**: Rather than crashing or raising an unhandled exception, in **`56%`** (`44%–71%` across stack $\times$ model) of faulted runs the agent finishes normally and returns a fluent response of severely degraded quality. Only `7%–19%` of runs are unaffected.

### 2. Model Scale (`20B` vs `120B`) Purchases Zero Fault Resilience ($p = 0.96$)

Scaling the reasoning backbone by `6x` from `gpt-oss-20B` to `gpt-oss-120B` yields **zero improvement in fault resilience**:
- In a linear mixed-effects model of the per-cell resilience ratio ($\text{OPP} / \text{OP0}$ task-completion score), the model-size effect is statistically indistinguishable from zero (**$\beta_{\text{model}} = -0.009$, 95% CI `[-0.39, 0.37]`, $p = 0.96$**), with no significant model $\times$ stack interaction ($p \ge 0.23$).
- **Larger models suffer a descriptively *lower* run-completion rate under faults**: Under `OPP`, `gpt-oss-120B` completes **`91.1%`** (`[86.7%, 94.2%]`, `20` non-completions) of runs compared to **`95.6%`** (`[92.0%, 97.6%]`, `10` non-completions) for `gpt-oss-20B` (a `4.4 percentage point` deficit, Fisher exact $p = 0.088$; fault-attributable paired completion drop of **`-5.8 pp`** for `120B` vs **`-3.6 pp`** for `20B`).
- **Why scale hurts completion under timing/permanent faults**: `18 of the 20` non-completions on `gpt-oss-120B` are `3,000 s` wall-clock timeouts. Because `120B` generates more reasoning tokens per call (`2,063` vs `1,711`) and persists longer in consecutive retries against broken tools (`4.5` vs `3.9` consecutive retries, accumulating `4.6` vs `3.9` fault events per cell), permanent faults (`91.3%` of real-world MCP faults) trap the larger model in longer, costlier retry loops.

### 3. "Tool Bypass" (Hallucinating Answers from Memory When Tools Fail) Inflates Naive Benchmarks

In **`27` of `450` `OPP` cells (`6.0%` overall**: `14/150` on `LangChain`, `9/150` on `OpenAI Agents SDK`, `4/150` on `MCP-Bench`), when tools fail, the agent **abandons tool use and fabricates a plausible-sounding answer from pretraining memory** (scoring $\ge 4/10$ on task fulfillment despite $< 2/10$ on tool appropriateness).
- Tool bypass is an existing baseline habit exposed by faults (`21` `OP0` cells and `16` `Proxy-off` cells also exhibit bypass; on `OpenAI Agents SDK`, bypass triples from `3` cells under `OP0` to `9` cells under `OPP`, McNemar $p = 0.07$).
- Under `OPP`, **un-grounded answers account for `16%` of all task-fulfillment credit** (up from `5%` under `OP0`). Enforcing a **grounded fulfillment** gate (zeroing task fulfillment whenever tool appropriateness $< 2$) deepens the overall fault-induced drop from `58%` to **`63%`** (`-4.87` points, 95% CI `[-5.27, -4.47]`; on `OpenAI Agents SDK`, from `61%` to **`68%`**).

### 4. Orchestration Framework Error Handling Shapes Failure Modes

While all three stacks suffer a baseline `-4.26`-point drop under `OPP`, their error-surfacing architectures drive distinct secondary losses and recovery profiles:

| Agent Stack | `OPP` Completion Rate (`20B` / `120B`) | Mean Fault Events / Cell | Additional Score Loss vs `LangChain` | Dominant Behavioral Pattern |
|:---|:---|:---|:---|:---|
| **`LangChain / LangGraph`** | `97%` / `95%` | `2.3` | Reference (`0.00`) | Highest completion; mixed retry/switch, but highest rate of un-grounded **tool bypass** (`14/150` cells) |
| **`OpenAI Agents SDK`** | `95%` / `88%` | `1.8` | **`-0.84 pts`** (`[-1.77, +0.08]`, $p = 0.074$) | **Retry-dominant** on same failing tool; `3x` surge in tool bypass under faults (`3 -> 9` cells) |
| **`MCP-Bench` (Plan-and-Execute)** | `95%` / `91%` | **`8.6`** | **`-0.93 pts`** (`[-1.86, -0.01]`, $p = 0.048$) | **Switch-dominant** multi-round replanning; accumulates `3.7x–4.8x` more fault hits per run |

---

## Architectural & Engineering Implications

1. **Enforce circuit breakers and fail-fast budgets for permanent MCP faults (`91.3%`)**:
   - Because `91.3%` of real-world MCP failures are permanent (broken credentials, schema mismatches, dead upstream APIs) and `8.2%` are silent TCP hangs (`OP6`), naive exponential backoff or unconstrained LLM retries waste wall-clock budgets and cause larger models (`120B`) to time out more often than smaller ones (`20B`). Cap per-tool retries at `1–2` attempts and enforce aggressive per-call socket timeouts (`<15–30 s`).
2. **Validate MCP tool outputs against strict schemas and semantic sanity checks (`19.1%` silent corruption)**:
   - Nearly a fifth (`19.1%`) of real-world MCP faults return HTTP 200 with corrupted types (`OP3`), word-level value substitutions (`OP2`), or character typos (`OP1`) rather than explicit `-32603` errors (`OP4`). Validate tool responses at the MCP client boundary before injecting them into the agent's context.
3. **Gate task completion and evaluation rubrics on grounded tool evidence**:
   - In production, forbid agents from answering tool-dependent queries from parametric memory when tool calls fail (require explicit abstention/error reporting instead of silent tool bypass). In benchmarks, always score **grounded fulfillment** (zeroing fulfillment when tool appropriateness $< 2$) so hallucinated answers do not mask `16%` of fault failures.

---

## Why Not a Skill?

This paper presents an ecosystem-wide fault study (`57,240` threads across `1,774` repos) and a proxy fault-injection benchmark (`MCP-Injector`) rather than an agent-executable skill procedure. Its quantitative findings directly strengthen our rules on **agent evaluation quality** (grounded fulfillment scoring and fault-injection benchmarking) and **workflow architecture** (circuit breakers for permanent MCP faults and anti-bypass abstention gates).

---

## Cross-References

- **Related Rules**: [`adk-workflow-architecture`](../rules/adk-workflow-architecture.md), [`agent-evaluation-quality`](../rules/agent-evaluation-quality.md), [`agent-sandbox-safety`](../rules/agent-sandbox-safety.md)
- **Related Skills**: [`transactional-coding-sandbox`](../skills/transactional-coding-sandbox/SKILL.md), [`necessary-tool-evidence-path`](../skills/necessary-tool-evidence-path/SKILL.md), [`pre-execution-action-auditing`](../skills/pre-execution-action-auditing/SKILL.md)
