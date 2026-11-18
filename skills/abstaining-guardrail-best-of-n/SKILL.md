---
name: abstaining-guardrail-best-of-n
description: >
  Run label-free parallel Best-of-N code execution and adaptive retry over
  structured outputs (dataframes, SQL tables, charts, analytical artifacts)
  where scalar majority voting fails by enforcing a machine-checkable artifact
  contract, pre-filtering N >= 3 pools to two finalists via a pairwise
  knockout tournament, gating acceptance on an abstention-capable code+artifact
  guardrail, routing targeted critiques into invariant-forcing retries, and
  sizing (N, r) by backbone capability. Derived from "GRACE: Parallel Best-of-N
  Multi-Agent Analysis of Closed-Form Questions over Dataframes with Guardrail
  Selection and Adaptive Retry" (arXiv:2611.20983).
source: https://arxiv.org/abs/2611.20983
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Abstaining Guardrail Best-of-N & Invariant-Forcing Retry (`GRACE`)

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

Use this skill when building **code-executing analytical, data-science, Text-to-SQL, or structured-reporting agents** that answer closed-form questions by executing code in a sandbox, where **no ground-truth unit test or validation metric exists per query** and outputs are structured artifacts (named dataframes, multi-column tables, or linked charts) rather than bare scalars.

## When to Use

- Single-rollout code agents commit unconditionally to misread column semantics, mishandled `NaN`s, or wrong aggregation grains (`39.0%` baseline match on `InfiAgent-DABench` / `DAEval`).
- Standard **answer-agreement / majority voting** breaks down because structured executed outputs rarely match byte-for-byte (`63.9%` of `N = 4` candidate pools on `DAEval` have **zero agreeing pairs**, leaving voting at `63.1%`—statistically indistinguishable from a `62.9%` random pick, $p = 0.66$) and voting structurally **cannot abstain** when every candidate in the pool is wrong.
- You want a principled **compute-allocation operating point** between parallel candidate diversity ($N$) and sequential guardrail-driven retries ($r$) matched to your model's parameter/capability tier.

Do **not** use this skill when an **exact automated numerical scorer or unit-test verifier** already exists per task and budgets span $B = 20\text{--}100+$ long-horizon optimization runs (use [`parallel-small-team-tts-scaling`](../parallel-small-team-tts-scaling/SKILL.md)), or when aggregating untrusted peer subtask text against colluding Byzantine adversaries (use [`similarity-consensus-subtask-aggregation`](../similarity-consensus-subtask-aggregation/SKILL.md)).

## Core Insight

In label-free code execution over structured data, candidate failures split into **structural failures** (broken code, scalar leakage, empty tables, unlinked plots) and **semantic failures** (wrong column, wrong grain, pre-aggregation `NaN` drop, incomplete plot set). `GRACE` (`arXiv:2611.20983`) separates them across three boundaries:

1. **Deterministic Post-Execution Contract Before Selection**: Local sandbox execution and bounded syntax/contract self-repair ensure *only runnable, schema-compliant artifacts* reach LLM judges, reducing structural failures to near zero.
2. **Joint `(Code + Executed Artifact)` Pairwise Filtering + Pool-Rejecting Guardrail**: Instead of clustering raw outputs for majority voting or scoring $N$ candidates in one prompt, a single-elimination pairwise bracket (`N - 2` calls for $N \ge 3$) narrows candidates to **at most `2` finalists**, and a domain checklist **Guardrail** inspects both the Python script and the resulting dataframe preview—either selecting the least-defective finalist or **rejecting the entire pool** to trigger an adaptive retry.
3. **Model-Tier Substitutability Between Parallel $N$ and Sequential Retries $r$**:
   - On capable `35B`-class coding backbones (`Qwen3.6-35B-A3B` MoE, `3B` active), parallel $N \in \{1, 2, 4\}$ and pool retries $r \in \{0, 4, 10\}$ are **statistically equivalent substitutes on the plateau** (clearing Two One-Sided Tests `TOST` within $\pm 5.7\text{ pp}$ across all `4` plateau comparisons on `DAEval` $M = 246$, lifting match rate from **`39.0%` to `70.7%` (`+31.7 pp`, rounded `39% -> 71%`, `+32 pp`, `1.8x`)** at `(N = 2, r = 4)`, preserving `95/96` initially correct answers while recovering **`79/150` (`52.7%`, `~53%`)** wrong answers; replicated on `DataBench` $M' = 400$ from **`69.8%` to `85.0%` (`+15.2 pp`)**). Consequently, **`(N = 1, r = 4)` achieves `66.7%` (`DAEval`) and `84.5%` (`DataBench`) at `~1.1x` baseline token cost**, and **`(N = 2, r = 4)` hits peak `70.7%` at `~2x` token cost**—both bypassing the tournament (`N < 3`)!
   - On smaller `9B` dense backbones (`Qwen3.5-9B`, `37.8%` baseline on `DAEval`), retries still saturate by $r = 4$, **but parallel $N$ is NOT substitutable**: adding parallel agents under $r = 4$ continues lifting accuracy (`53.5% -> 60.2% -> 63.4%` for $N = 1, 2, 4$), because weaker models misread question intent more often on attempt `1` and need independent persona-diversified interpretations (`N = 4` with tournament active).

---

## Step-by-Step Procedure

### Step 1: Materialize One Authoritative Data Schema (`df_info`)

Before spawning any code generator, run a single lightweight schema-extraction pass over the target table(s) (previewing the first `20` rows, column names, exact `dtypes`, sample values, and concise per-column semantic role descriptions) to emit an immutable **`df_info`** payload:

- Inject `df_info` verbatim into every generator, pairwise judge, and guardrail prompt as the **sole source of column truth**.
- Instruct generators to load data strictly via a controlled helper (`load_df`) rather than ad-hoc `pd.read_csv` parsers and treat referencing any column absent from `df_info` as a hard semantic error.

### Step 2: Run $N$ Diversified Sandboxed Generators Under a Machine-Checkable Contract

Dispatch $N$ concurrent code-writing agents inside isolated sandboxes with per-agent straggler timeouts:

1. **Preserve a Neutral Anchor (`Agent 1`) + Non-Prescriptive Stance Personas (`Agents 2..N`)**:
   - Keep **Agent 1 completely unperturbed** (zero persona preamble) so the backbone's default highest-likelihood interpretation is always represented in the pool.
   - Assign Agents $2..N$ distinct decisional-stance preambles that vary analytical caution without dictating implementation code:
     - $P_1$ (*Schema-strict / minimal*): use only explicit columns/dtypes; smallest direct code without extra preprocessing.
     - $P_2$ (*Defensive / robust*): explicit `NaN` handling, dtype assertions, empty-group/single-class guards, and state variables.
     - $P_3$ (*Exploratory / chart-generous*): preserve finer row-level grain with derived columns when ambiguous; emit full per-variable plot sets.
     - $P_4$ (*Pragmatic / direct*): literal wording match with simplest direct aggregation.
2. **Enforce a Three-Clause Post-Execution Artifact Contract (with Local Self-Repair)**:
   - Require every script to output: (i) a single-entry dictionary `result = {"<descriptive_name>": {"type": "dataframe", "value": df}}` where `df` is a non-empty `pandas.DataFrame` (forbidding raw scalars, lists, dicts, or multi-table dumps—wrap scalar answers in a 1-row dataframe); (ii) any required chart files saved outside `result` in an agent-scoped directory (`{agent_output_dir_<i>}`) linked via provenance metadata (`data_csv` matching the single `result` key); and (iii) explicit fit-completion checks before calling `.predict()`, `.transform()`, or reading `coef_`/`classes_`, with **silent `try/except` blocks strictly forbidden**.
   - If execution raises an exception or violates the 3-clause contract, allow bounded **within-slot local repair** before selection. Drop slots that still fail or time out so downstream judges compare **only runnable, contract-compliant artifacts**.

### Step 3: Pre-Filter $N \ge 3$ Pools to Two Finalists via Pairwise Knockout

- **If valid candidates $< 3$** ($N \in \{1, 2\}$): **Bypass the tournament completely** and send the `1` or `2` candidates directly to Step 4.
- **If valid candidates $\ge 3$**: Run a single-elimination pairwise bracket that **stops at `2` survivors** (`N - 2` LLM judge calls):
  - Feed each match the user question and both candidates' **Python source code + executed dataframe preview**.
  - Require the judge to enumerate concrete semantic defects in *both* candidates (wrong columns, missing `NaN` handling before modeling/aggregation, wrong metric/grain, missing required plots, partial answer) before outputting JSON `{winner, reason, loser_critique}`.
  - Persist `loser_critique` (`1–2` concrete sentences) keyed to the eliminated agent's ID for targeted retry routing if the pool is later rejected. Halting at `2` survivors preserves two distinct candidates and two per-agent advice channels for the guardrail.

### Step 4: Gate Acceptance on an Abstention-Capable Code + Artifact Guardrail

Pass the $\le 2$ surviving `(code, executed_dataframe_preview)` pairs and prior guardrail errors to the **Domain Guardrail**, which evaluates the exact semantic checklist (including checking plot-generation loops in the code when multi-variable plots are requested) and emits one of two structured JSON verdicts:

- **Case A — Accept (`Correct_response = "true"`)**: At least one finalist is semantically valid. Select `Correct_analysis_number` (preferring fewer/less-severe defects, tie-breaking toward simpler code) and emit `Detailed_analysis` in clean business prose stripped of code or ensemble metadata.
- **Case B — Reject / Abstain (`Correct_response = "false"`)**: *Neither* finalist is defensible. Reject the entire pool and emit global root-cause `Advice` plus `Per_agent_advice` (one concise, column-specific fix per finalist, containing no raw code).

### Step 5: Execute Re-Diversified, Invariant-Forcing Pool Retries (Up to $r$ Rounds)

Whenever the Guardrail returns `Case B` and attempt index $t \le r$:

1. **Step temperature to escape mode lock-in**: Use a two-regime temperature schedule uniform across the pool:
   $$T(t) = \begin{cases} 0.65 & t = 1 \text{ (clean, coherent initial code)} \\ 1.0 & t \ge 2 \text{ (break shared misinterpretation modes)} \end{cases}$$
2. **Rotate personas by `+1` offset**: Shift persona assignments across non-anchor agents each retry so targeted critiques do not fight the exact same persona bias that induced the error.
3. **Route tournament-scoped feedback (no broadcast pollution)**:
   - Send global `Advice` to **all** $N$ agents;
   - Send `Per_agent_advice[i]` **only** to finalist $i$;
   - Send match-specific `loser_critique[j]` **only** to bracket-eliminated agent $j$.
4. **Enforce the Invariant-Forcing Retry Rule**: Require every retried script to **introduce at least one new explicit invariant, `assert`, or state-verification variable** directly testing the diagnosed root-cause assumption; forbid cosmetic rewrites.
5. **Terminal diagnostic fallback**: If budget $r$ is exhausted without approval, invoke a `Failure Analysis` summarizer to return an explicit abstention diagnosis (attempted interpretations, root cause, retry progression) rather than silently emitting an unverified table.

### Step 6: Select Operating Point $(N, r)$ by Backbone Capability Tier

| Backbone Tier & Workload | Recommended `(N, r)` | Tournament Used? | Empirical Rationale (`arXiv:2611.20983`) |
|:---|:---:|:---:|:---|
| **Strong coding MoE / Frontier (`>= 30B`, e.g., `Qwen3.6-35B-A3B`), cost-sensitive** | **`(N = 1, r = 4)`** | No (`N < 3`) | Captures `66.7%` on `DAEval` (`+27.7 pp` over `39.0%`) and `84.5%` on `DataBench` (`+14.7 pp` over `69.8%`, `0.5 pp` from `85.0%` max) at **`~1.1x` median baseline tokens** because retries only fire on guardrail rejection. |
| **Strong coding MoE / Frontier (`>= 30B`), standard production accuracy** | **`(N = 2, r = 4)`** | No (`N < 3`) | Reaches peak **`70.7%`** on `DAEval` (`95/96` kept, `1` regression, `79/150` recovered) at **`~2.0x` baseline tokens** with near-baseline wall-clock latency; raising $N \to 4$ (`68.3%`) or $r \to 10$ (`69.5%`) stays inside TOST equivalence ($\pm 5.7\text{ pp}$). |
| **Smaller dense models (`~7B–9B`, e.g., `Qwen3.5-9B`) or highly ambiguous schemas** | **`(N = 4, r = 4)`** | Yes (`2` matches) | `9B` retries saturate at $r = 4$ (`53.5%` at $N=1$ vs. `52.0%` at $r=10$), while parallel $N$ adds **`+9.9 pp` on top of retries** (`53.5% -> 60.2% -> 63.4%` across $N = 1, 2, 4$) by supplying independent question readings. |

---

## Environment Caveats

- **All-wrong pool abstention remains the primary bottleneck (`10.2%` recall)**: On `263` instrumented `DAEval` selection pools at `(N = 4, r = 4)` (`Table 3`), when at least one valid candidate existed (`204/263 = 77.6%` oracle ceiling), `Tournament + Guardrail` selected a correct answer **`86.3%` (`176/204`)** of the time (`8.3%` wrong pick, `5.4%` false rejection—with nearly half of rejected questions later recovering on retry), beating majority voting (`66.9%` vs. `63.1%`, **`+3.8 pp`**, 95% CI `[+0.3, +7.3]`, $p = 0.03$) on the exact same pools. However, when **all candidates were wrong (`59/263` pools)**, the prompt-only LLM guardrail rejected only **`6/59` (`10.2%`)** and false-accepted **`53/59` (`89.8%`)**. For high-stakes reporting, supplement the LLM guardrail with **deterministic domain sanity invariants** (row-count conservation, accounting sum checks, null-rate bounds, cross-column range constraints).
- **Inference-scaling vs. strict compute-parity accounting**: The `(N, r)` sweep measures end-to-end inference scaling over `(N = 1, r = 0)` rather than holding total generator + judge tokens constant against $k$-sample self-refinement. When claiming architectural superiority in benchmarks, report all 6 `PACE` resource dimensions (`arXiv:2611.17610`).
- **Upstream ETL / wrong-table errors**: Benchmarks supply the authoritative target CSV; in production text-to-SQL or lakehouse pipelines where table retrieval itself can pick the wrong table, add an upstream schema/table grounding check before Step 1.

## Failure Modes

- **Replacing the Guardrail with scalar/table majority voting**: On structured dataframe outputs, `63.9%` of 4-agent pools contain zero agreeing pairs (`>= 2` cluster in only `34.2%`), degrading majority voting to random selection (`63.1%` vs. `62.9%`) and eliminating pool rejection/retry entirely.
- **Passing only the output table (without the Python script) to the Guardrail**: Plausible-looking summary numbers frequently hide dropped `NaN` cohorts, silent type coercions, hardcoded constants, or missing per-variable plots that are immediately visible when inspecting `(code + dataframe preview)` jointly.
- **Keeping $T = 0.65$ and fixed personas across retries, or broadcasting all critiques to all agents**: Retrying under the same persona and low temperature repeats the initial semantic misreading, while broadcasting `loser_critique` from Agent 3's bug into Agent 1's clean anchor prompt contaminates working trajectories (`11/93` regressions on `9B` vs. `1/96` on `35B`).
- **Over-provisioning `(N = 4, r = 10)` on capable `35B+` models**: Consumes `> 4x` tokens for `-0.4 pp` (`70.3%` vs. `70.7%` at `N = 2, r = 4` on `DAEval`) or `+0.5 pp` (`85.0%` vs. `84.5%` at `N = 1, r = 4` on `DataBench`).

## Cross-References

- [`multi-agent-coordination.md`](../../rules/multi-agent-coordination.md) — `"DO: Scale test-time compute on verifiable long-horizon tasks via parallel small flat teams rather than solo Best-of-N, one giant team, or manager orchestration"` and `"DO: Restrict reflection to the agent that caused the failure"`
- [`agent-evaluation-quality.md`](../../rules/agent-evaluation-quality.md) — `"DON'T: Claim coordination gains over greedy decoding without sample-parity and compute-parity baselines and 6D PACE accounting"`, `"DO: Expose OpenTelemetry trajectory spans to analytics-agent graders and combine functional boundary synthesis with security probing"`, and `"DO: Audit domain fine-tuned models against their matched base checkpoints across capability, knowledge-centric abstention, newly-answered accuracy, and shared-error commitment"`
- [`parallel-small-team-tts-scaling`](../parallel-small-team-tts-scaling/SKILL.md) — Compute allocation across $K$ parallel collaborative teams when an exact automated verifier exists (`arXiv:2611.09798`)
- [`pairwise-action-verification`](../pairwise-action-verification/SKILL.md) — Mid-trajectory pairwise action verification (`arXiv:2609.39982`)

## Sources

- Picariello, Cipolla, Bonura & Morreale, "GRACE: Parallel Best-of-N Multi-Agent Analysis of Closed-Form Questions over Dataframes with Guardrail Selection and Adaptive Retry" ([arXiv:2611.20983](https://arxiv.org/abs/2611.20983), `ITADATA 2026`, `src:2611-20983v1`)
