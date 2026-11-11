# Comparative Analysis of Agent Evaluation Frameworks: Stability, Detection, and Discovery in Enterprise Analytics Agents

> **Source**: [arXiv:2611.14493](https://arxiv.org/abs/2611.14493) — Howard Zhang, Chuck Arvin, Logan Brown, Mihir Bhatia, Neelu Choudhary, Lily Miao (2026)
> **Praxis Source ID**: `src:2611-14493v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

This paper is an empirical benchmark and head-to-head comparison of three existing open-source/commercial evaluation frameworks—**`Strands Evals`** (OpenTelemetry full-trace LLM-as-judge), **`PromptFoo`** (text-only LLM-as-judge + adversarial red-teaming), and **`Agenta`** (deterministic string/regex/set heuristics)—across `11,700` evaluation runs on two production enterprise supply-chain analytics agents. Rather than introducing a new standalone subtask algorithm beyond our existing evaluation skills and quality-gate specs, its primary contribution is **comparative empirical evidence** quantifying the stability-depth trade-off, the `~5x` (`4.7x`) false-positive penalty of evaluating tool-heavy agents without execution traces, a `12.5%` (`9/72`) human domain-expert ground-truth blind spot on syntactically valid semantic SQL bugs, and the `0`-overlap complementarity between trajectory-grounded functional synthesis and adversarial security red-teaming. Those quantitative findings directly sharpen our rules in [`agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md) and quality-gate architecture in [`adk-eval-quality-gate.spec.md`](../specs/adk-eval-quality-gate.spec.md).

---

## Experimental Setup: Three-Phase Frozen-Trace Evaluation (`11,700` Runs)

From seven candidate frameworks (`Strands Evals`, `PromptFoo`, `Agenta`, `DeepEval`, `Ragas`, `TruLens`, `OpenAI Evals`), the authors selected three representatives spanning distinct architectural paradigms (`~30 min` setup for `Strands` and `PromptFoo`; `~2 hrs` for `Agenta`):

| Framework | Architectural Paradigm | What the Evaluator Sees | Primary Strength Tested |
|:---|:---|:---|:---|
| **`Strands Evals`** | Trajectory-native OpenTelemetry LLM-as-judge + `ExperimentGenerator` | Full execution trace: user prompt, intermediate reasoning, every SQL query & tool call/argument, raw tool outputs, and final text | Multi-step tool/SQL verification & functional edge-case synthesis |
| **`PromptFoo`** | Text-boundary LLM-as-judge + automated adversarial red-team plugins | Input prompt + final natural-language output text only (no intermediate tool spans or raw query results) | Output-level rubric checks & adversarial security probing |
| **`Agenta`** | Deterministic programmatic evaluators | Regex, substring, JSON-field, and set-overlap rules over outputs/queries | Zero-variance structural syntax & keyword assertions |

**Target Systems**: Two production supply-chain analytics agents powered by `Claude Sonnet 4.5`, each equipped with `9` tools:
- **`Agent A`** (*Category Demand Forecasting*): SQL generation/execution and category-level forecast explanation tools.
- **`Agent B`** (*Product Inbound Lead-Time Forecasting*): richer multi-table schema + `code_interpreter` for statistical and calibration analysis.

To isolate **evaluator variance and accuracy** from target-agent generation randomness, Phases 1 and 2 replayed **frozen production execution traces**, totaling **`11,700` evaluations** (`5,605` in Phase 1 + `2,415` in Phase 2 + `3,680` in Phase 3).

---

## Key Empirical Findings

### 1. Phase 1 — Evaluator Stability (`5,605` Evaluations): Stability Is an Agent-Independent `(Framework, Judge)` Property, and Per-Case LLM Verdicts Flip `8%–18%` of the Time

Across `20` frozen cases per agent (`40` total), `3` judge models (`Claude Haiku 4.5`, `Claude Sonnet 4.6`, `Qwen3 32B`), and `5` repeated runs per `(framework, metric, judge)` configuration, **`35/36` (`97%`) configurations met the within-case standard-deviation threshold ($\text{SD} \le 0.15$)**:

| Framework | Configs Passing ($\text{SD} \le 0.15$) | Mean Within-Case SD | Mean Decision Consistency (`DC` at pass/fail threshold) |
|:---|:---:|:---:|:---:|
| **`Agenta`** (deterministic) | **`5/5` (`100%`)** | **`0.000`** | **`100%`** |
| **`PromptFoo`** (text-only LLM judge) | **`12/12` (`100%`)** | **`0.025`** | **`92%`** (`faithfulness`: `67%` Sonnet / `68%` Qwen3 near `0.5` cutoff) |
| **`Strands Evals`** (full-trace LLM judge) | **`11/12` (`92%`)** | **`0.053`** | **`82%`** |

- **Stability-Depth Trade-Off**: Giving an LLM judge full multi-tool OpenTelemetry traces (`Strands`) roughly doubles score standard deviation (`0.053` vs. `0.025` in text-only `PromptFoo`) and lowers per-case binary Decision Consistency (`DC`) from `92%` to `82%`. Furthermore, trace-judge variance scales positively with **tool-call count** (slope $m = 0.017$ vs. $m = -0.006$ for text-only `PromptFoo`) and **query complexity** (`0.230 -> 0.407` in `Strands` vs. `0.176 -> 0.238` in `PromptFoo`).
- **Model-Specific Instability Signatures Transfer Identically Across Agents**: Across judge models, mean within-case SD was `0.029` (`Claude Haiku 4.5`), `0.035` (`Claude Sonnet 4.6`), and `0.072` (`Qwen3 32B`). The sole failing configuration—**`Qwen3 32B` on `style` in `Strands`**—failed identically on both agents (`0.207` average SD: `0.188` on `Agent A`, `0.227` on `Agent B`; `20%` `DC`), whereas the exact same model on `style` in `PromptFoo` scored `0.011` SD. Thus, stability must be validated per `(framework, judge_model)` pair, not assumed from model family alone.
- **CI/CD Gating Implication**: Even when continuous score SD is `< 0.06`, **`82%–92%` per-case Decision Consistency means single-run per-case LLM-judge pass/fail assertions will spuriously fail CI builds on `8%–18%` of borderline cases**. Use deterministic assertions (`100%` `DC`) for hard per-case CI blockers, and aggregate LLM-judge scores across multi-rep medians (`>= 3` reps) or suite-level noise margins ($\delta$).
- **Judge Model Cost Scaling (`Claude Opus 4` vs. `Sonnet 4.6` vs. `Haiku 4.5`)**: On a `10`-case calibration check, `Claude Opus 4` (mean score `0.78`, `~28s`/eval, `25x` relative cost) correlated at **$r = 0.97$** with `Claude Sonnet 4.6` (`0.79`, `~8s`/eval, `5x` cost) while catching **`0` additional failures**; `Claude Haiku 4.5` (`0.82`, `~3s`/eval, `1x` cost) correlated at **$r = 0.94$** with `Opus 4`. Mid-tier `Sonnet 4.6` captured the full detection ceiling at `5x` lower cost and `3.5x` lower latency than `Opus 4`.
- **Reasoning-Tag Parser Hazard**: Structured JSON output parsers in evaluation frameworks broke on reasoning models that emit inline `<think>` / reasoning blocks (`GPT-OSS-120B`, `MiniMax M2`, and `Qwen3 32B` unless `showThinking: false` was explicitly configured).

---

### 2. Phase 2 — Known Risk Detection (`2,415` Evaluations): Text-Only Judges Suffer `~5x` Higher False-Positive Rates Than Full-Trace Judges

On `72` expert-labeled frozen traces (`36` per agent; `33` [`46%`] containing verified failures across `28` SQL, `9` tool-use, `6` accuracy, `4` intent, and `2` groundedness defects; `3`-rep median with `Claude Sonnet 4.6`):

| Framework | Precision | Recall | F1 | False Positive Rate (`FPR`) | Confusion Matrix (`TP / FP / FN / TN`) |
|:---|:---:|:---:|:---:|:---:|:---:|
| **`Strands Evals` (full trace)** | **`88.2%`** | **`90.9%`** | **`0.896`** | **`10.3%`** (`5.3%` A / `15.0%` B) | `30 / 4 / 3 / 35` |
| **`PromptFoo` (text-only)** | `60.4%` | `87.9%` | `0.716` | **`48.7%`** | `29 / 19 / 4 / 20` |
| **`Agenta` (deterministic)** | `45.8%` | `100.0%` | `0.629` | **`100.0%`** | `33 / 39 / 0 / 0` |

**Why Text-Only Evaluation Collapses on Tool-Using Analytics Agents**:
- **Hallucination vs. Legitimate Tool Retrieval (`52.1%` vs. `0%` Faithfulness FPR)**: Without visibility into intermediate SQL result sets, `PromptFoo`'s faithfulness judge flagged **`52.1%` (`52%`) of valid data-grounded numbers as "ungrounded hallucinations"** because those figures did not appear in the user's input prompt, whereas `Strands` verified them directly against tool-output spans at **`0%` FPR**.
- **Silent Intermediate Tool Failures (`88.9%` vs. `11.1%` Tool-Error Recall)**: When an agent invoked the wrong tool, retried silently, or recovered superficially in prose, `Strands` caught **`88.9%` (`8/9`)** of tool-correctness defects versus **`11.1%` (`1/9`)** for text-only `PromptFoo`—an **`8x` recall gap**. Both LLM judges achieved `89.3%` (`25/28`) SQL error recall and `83.3%` (`5/6`) accuracy recall (`Intent` FPR: `0%` `Strands` vs. `2.9%` `PromptFoo`).
- **Deterministic Regex Brittle Ceiling**: `Agenta`'s deterministic rules flagged every single passing trace (`100%` overall FPR; `TP=33, FP=39, TN=0`). Even its targeted SQL regex validator—which reached `92.9%` recall on `Agent A` structural syntax bugs—dropped to **`0%` recall on `Agent B`**, where SQL queries were syntactically valid yet queried the wrong semantic aggregation partition.
- **Domain-Expert Ground-Truth Blind Spot (`9/72` = `12.5%` Human Miss Rate)**: Trace-grounded rubric evaluation uncovered **`9` real failures among the `72` benchmark cases (`12.5%`) that human domain experts had initially mislabeled as `"pass"`**: `5` cases on `Agent A` where syntactically clean SQL filtered `partition_level = 'top'` instead of category-specific partitions, and `4` cases on `Agent B` where the agent misinterpreted calibration-coefficient sign/underbias outputs. Even before label revision, `Strands` led all frameworks (`0.82` precision, `0.88` recall, `0.13` FPR).

---

### 3. Phase 3 — Unknown Risk Discovery (`3,680` Evaluations across `202` Synthesized Cases): Functional Synthesis and Security Red-Teaming Have Zero Overlap

Using `Strands ExperimentGenerator` (`40` context-aware functional edge-case prompts) and `PromptFoo` red-teaming (`90` adversarial security probes across SQLi, prompt injection, schema exfiltration, and excessive agency), alongside deterministic `Agenta` checks (`202` total discovery cases):

| Discovery Pipeline | Cases Flagged | Confirmed Novel Failures | False Discovery Rate (`FDR`) | Failure Classes Uncovered |
|:---|:---:|:---:|:---:|:---|
| **`Strands ExperimentGenerator`** (functional) | `10` (on functional sweep) | **`9`** | **`6.1%`** | `6` silent `0`-row SQL bugs (`UPPER(SUBSTR(product_id, -1))` case/suffix filter assumptions), `1` skipped `count_result_rows` check, `1` tool retry storm, `1` `location_id` schema column fabrication (`40%` novel yield on `Agent A` vs. `5.9%` on `Agent B`) |
| **`PromptFoo` Red-Team** (adversarial security) | `20` | **`15`** | **`20.8%`** | `10` database schema/table metadata leaks, `5` internal S3/storage path exposures, `4` system-prompt workflow disclosures, `1` excessive agency (`DESCRIBE`, `SHOW COLUMNS`, unrestricted `SELECT *`); **`4x` more security findings on schema-richer `Agent B`** |
| **`Agenta`** (deterministic) | High | **`0`** | **`> 85%`** | None (structural keyword false alarms) |

**Critical Result — `0` Overlap Across `24` Novel Failures**: Not a single failure found by `Strands` functional trajectory synthesis (`9` failures) was found by `PromptFoo` adversarial red-teaming (`15` failures), and vice versa. Functional synthesis probes boundary inputs under cooperative user intent (exposing silent `0`-row SQL logic bugs and tool-loop anomalies), whereas adversarial red-teaming probes boundary violations under hostile intent (exposing schema/path leakage and over-privileged introspection queries). Shipping an enterprise analytics agent requires **both** pipelines.

---

## Practical Engineering Takeaways

1. **Never score tool-using data agents with text-only faithfulness judges**: Feed OpenTelemetry/trajectory spans (tool calls, SQL text, raw query results) to functional LLM judges; text-only judges misclassify valid database retrievals as hallucinations (`48.7%` overall FPR; `52.1%` faithfulness FPR) and miss `88.9%` of intermediate tool errors (`11.1%` recall).
2. **Separate deterministic per-case CI blockers from aggregated LLM-judge gates**: Reserve hard single-case CI build failures for deterministic invariants (`Agenta`-style schema, empty-result guard, forbidden `DESCRIBE`/`SHOW COLUMNS` SQL AST checks at `100%` `DC`). Run trace-based LLM judges with `>= 3` repetitions or suite-level tolerance margins rather than raw 1-rep per-case binary gates (`82%` `DC`), and explicitly disable inline `<think>` tags (`showThinking: false`) on open-weight judge endpoints.
3. **Audit human "gold" labels with trace-level rubric judges**: Expect human reviewers inspecting polished analytical prose to miss `~10%–13%` of silent semantic query/calibration bugs (`9/72` = `12.5%`); run trace-grounded rubric disagreement checks during golden-dataset curation.
4. **Run dual discovery pipelines before launch**: Pair trajectory-aware functional test generation (`Strands`-style) with adversarial red-teaming (`PromptFoo`-style), scaling red-team budgets proportionally to schema surface area and code-execution privileges (`4x` higher security exposure on `Agent B`).

---

## Related Artifacts

- **Rules**:
  - [`agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md) — LLM-as-judge pipelines, checklist decomposition, and multi-judge red-team evaluation
  - [`adk-security-and-evaluation.md`](../rules/adk-security-and-evaluation.md) — Golden dataset trajectory CI/CD quality gates and least-privilege database access
- **Specs**:
  - [`adk-eval-quality-gate.spec.md`](../specs/adk-eval-quality-gate.spec.md) — Enterprise trajectory assertion and CI/CD quality-gate specification
- **Research Briefs**:
  - [`rubric-artifact-bias-in-llm-judges`](./rubric-artifact-bias-in-llm-judges.md) — Rubric-only artifacts and calibration pitfalls in LLM judges
  - [`checklist-aggregation-eval-pipeline`](./checklist-aggregation-eval-pipeline.md) — Atomic checklist decomposition for higher inter-rater reliability
  - [`reflect-sql-multi-stage-reflection`](./reflect-sql-multi-stage-reflection.md) — Semantic vs. syntactic failure modes in enterprise text-to-SQL agents
