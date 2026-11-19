# Learning to Coordinate (`L2C`): Workflow Evolution, Full-Token Accounting, and Edit Locking in Multi-Agent Red Teaming

> **Source**: [arXiv:2611.24221](https://arxiv.org/abs/2611.24221) — Xiaoyang Xing, Wenyu Dai, Xiaoliang Gong, Asoke K. Nandi & Anthony Cohn (*Learning to Coordinate: LLM-Guided Workflow Evolution for Token-Efficient Red Teaming*, Nov 2026)
> **Praxis Source ID**: `src:2611-24221v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

`L2C` optimizes multi-agent jailbreak attack workflows (`HarmBench` / `JailbreakBench`) by supervised fine-tuning a specialized `Mixtral-8x22B-Instruct-v0.1` LoRA controller over `12,400M` offline rollout tokens (`1,540` counterfactual branches, `18.5` GPU-hours). Offensive jailbreak workflow synthesis is scoped to defensive research briefs under `output/AGENTS.md`, and general-purpose multi-agent harness/prompt evolution is already covered by [`mcts-full-harness-optimization`](../skills/mcts-full-harness-optimization/SKILL.md) (`HarnessFlow`, `arXiv:2611.06254`), [`coordinator-executor-prompt-optimization`](../skills/coordinator-executor-prompt-optimization/SKILL.md) (`CEPO`, `arXiv:2610.34722`), and [`scoped-multi-agent-harness-composition`](../skills/scoped-multi-agent-harness-composition/SKILL.md) (`SciMARS`, `arXiv:2611.12552`). Its distinct contributions for Praxis—exposing how target-query counts ($Q$) hide multi-million-token controller overhead, formalizing matched-success token cost ($C_\alpha$) and offline amortization ($n_k^*$), linking input-delivery traces to graph versions, and decoupling workflow-edit locking (`LOCK`) from episode stopping—are captured here and as evaluation-governance rules in [`rules/agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md).

---

## Architecture & Evaluation Accounting (`§3–§4`, `Appendices A–B`)

`L2C` models an evaluation workflow at pass $t$ as a validated directed acyclic graph $W_t = (V_t, E_t, \Pi_t, \Phi_t)$ executed over topological node bindings (`planner`, `generator`, `rewriter`, `critic`, `selector`) with one designated candidate-submission node:

1. **Version-Linked Execution Trace ($H_t$)**: Unlike outcome-only feedback (target reply + judge bit) or flat unlinked text summaries, $H_t$ records the **exact resolved artifacts delivered to each node's inputs (`\Phi_t`) and emitted by each node**, explicitly keyed to graph version $W_t$, alongside token spend $c_t$.
2. **Four Bounded Controller Actions (`Mixtral-8x22B-Instruct-v0.1` LoRA SFT)**:
   - **`CONTINUE`**: Re-execute $W_t$ unchanged on updated target feedback (`0` patch overhead).
   - **`REFINE`**: Edit node prompts/instructions ($\Pi_t$) while preserving graph topology $(V_t, E_t, \Phi_t)$.
   - **`RESTRUCTURE`**: Add, prune, or rewire nodes/edges/bindings, validated deterministically before commit (unique IDs, valid roles, acyclic dependencies, resolved input bindings, valid target-submission node; `<= 1` repair retry before falling back to incumbent $W_t$).
   - **`LOCK`**: Permanently freeze workflow editing for the remainder of the episode (`W_{t+1} = W_t` with `0` future controller calls) while allowing fixed bindings to keep reading fresh per-pass target responses until success or budget $B$.
   - *Offline SFT construction*: Rank-`32` ($\alpha = 64$, `lr = 2e-5`, `2` epochs, `18.5` GPU-h, `0.42M` action tokens) on `300` schema/interface demonstrations + **`296` $K = 5$ leave-one-out-stable counterfactual execution labels** (`112 CONTINUE`, `84 REFINE`, `58 RESTRUCTURE`, `42 LOCK` filtered from `428` states / `1,540` branches at margins $(\epsilon_p, \epsilon_c) = (0.0, 0.05)$) over `512`/`128` `WildJailbreak` behavior pools (`12,400M` offline tokens total).
3. **Full Online Token Budget ($B = 8\text{M}$ tokens) & Amortization Metrics**:
   - Every online token—controller planning, executor nodes, backend reasoning tokens, target queries, parse retries, failed episodes, and in-loop `HarmBench-Llama-2-13b-cls` evaluator tokens—is charged to $T_i(B) \le B$, **reserving evaluator tokens before dispatching candidate generation** so unassessed target outputs never count as within-budget hits.
   - **Matched-Success Token Cost**: $C_\alpha = \min_{B \in \{2,3,4,5,6,8\}\text{M} : \mathrm{ASR}(B) \ge \alpha} \overline{T}(B)$ (`\alpha = 75%`).
   - **Offline Amortization Threshold**: $n_k^* = \lceil (D_{\mathrm{L2C}} - D_m) / \max(\overline{T}_m - \overline{T}_{\mathrm{L2C}}, \epsilon) \rceil$, comparing offline preparation tokens $D_m$ (`0` `PAIR`, `4,250M` `AutoDAN-Turbo`, `6,800M` `AutoRedTeamer`, `8,400M` `GRAFT-HB`, `12,400M` `L2C`, `15,200M` `EvoSynth`, `18,500M` `AgenticRed`).

---

## Core Quantitative Findings (`§5`, `Tables I–IX`)

### 1. Cross-Backbone `HarmBench Standard` (`159` Behaviors $\times$ `3` Replicates, `B = 8M` Online Cap, `Tables I & V`)

| Method | `Mixtral-8x7B` $\to$ `Llama-3.1-70B` (`ASR / MTok / Q`) | `Mixtral-8x7B` $\to$ `GPT-5.4` (`ASR / MTok / Q`) | `Qwen3.5-4B` $\to$ `Llama-70B` / `GPT-5.4` (`ASR / MTok`) | `Gemini 3.5 Flash-Lite` $\to$ `Llama-70B` / `GPT-5.4` (`ASR / MTok`) | Held-Out `StrongREJECT` (`Mixtral` `Llama` / `GPT-5.4`) |
|:-------|:-------------------------------------------------------:|:-------------------------------------------------:|:---------------------------------------------------------:|:--------------------------------------------------------------------:|:-------------------------------------------------------:|
| **`PAIR`** | `68.5% / 2.45 / 18.4` | `59.0% / 2.85 / 21.6` | `61.2% / 2.60` \| `51.5% / 3.05` | `66.8% / 2.15` \| `57.5% / 2.50` | `0.542` / `0.451` |
| **`AutoDAN-Turbo`** | `76.2% / 4.10 / 15.6` | `68.5% / 4.65 / 18.2` | `70.5% / 4.35` \| `61.8% / 4.90` | `74.8% / 3.65` \| `67.0% / 4.15` | `0.612` / `0.534` |
| **`AutoRedTeamer`** | `79.0% / 3.85 / 13.8` | `71.0% / 4.30 / 15.9` | `73.2% / 4.10` \| `64.5% / 4.55` | `77.5% / 3.40` \| `69.8% / 3.85` | `0.638` / `0.558` |
| **`GRAFT-HB`** | `82.0% / 5.45 / 11.2` | `75.2% / 6.05 / 12.9` | `74.6% / 5.80` \| `66.2% / 6.45` | `80.1% / 4.75` \| `73.0% / 5.30` | `0.665` / `0.587` |
| **`AgenticRed`** | `82.5% / 5.60 / 11.5` | `75.5% / 6.20 / 13.2` | `75.0% / 5.95` \| `66.5% / 6.60` | `80.6% / 4.90` \| `73.5% / 5.45` | `0.670` / `0.591` |
| **`EvoSynth`** | `83.1% / 5.20 / 10.8` | `76.5% / 5.85 / 12.4` | `75.8% / 5.65` \| `67.0% / 6.30` | `81.2% / 4.50` \| `74.2% / 5.05` | `0.674` / `0.596` |
| **`L2C` (Ours)** | **`84.5% / 3.35 / 7.6`** | **`78.0% / 3.75 / 8.8`** | **`79.5% / 3.55`** \| **`71.5% / 3.95`** | **`83.2% / 2.90`** \| **`76.8% / 3.25`** | **`0.698` / `0.624`** |

- **Query Count ($Q$) Reversal vs. Full Token Cost (`Table II`)**: On `Mixtral` $\to$ `Llama-3.1-70B`, `EvoSynth` (`Q = 10.8`) and `AgenticRed` (`Q = 11.5`) appear cheaper than `AutoRedTeamer` (`Q = 13.8`) by target queries alone, yet their **`1.45M` and `1.65M` controller tokens** inflate total `MTok` to **`5.20M` and `5.60M`** (`P90 = 8.00M` cap) vs. `3.85M` for `AutoRedTeamer` (`0.42M` controller) and **`3.35M` for `L2C`** (`0.65M` controller + `2.52M` executor + `0.11M` target + `0.07M` evaluator; `P50 = 2.20M`, `P90 = 6.85M`, **`C_75 = 2.40M`** vs. `3.30M–4.10M` across all reaching baselines; `PAIR` failed to reach `75%`).
- **Held-Out Scorer & Blinded Human Calibration (`Tables V & IX`)**: Across `4` audited configurations, `StrongREJECT` (`GPT-5.4-mini`) confirmed `L2C`'s lead (`0.698, 0.624, 0.635, 0.558` vs. `0.674, 0.596, 0.595, 0.512` `EvoSynth`), while a `400`-pair (`100`/config) blinded dual-annotator audit against `HarmBench-cls` measured Cohen's $\kappa = 0.84, 0.82, 0.85, 0.81$ (`93.0%, 91.5%, 93.5%, 91.0%` agreement) alongside non-zero **`4.5%–6.2%` FPR and `8.0%–10.2%` FNR**, reinforcing why single-judge online stopping must always be audited with independent post-hoc scorers.
- **Zero-Retraining `JailbreakBench` Transfer (`Table IV`)**: `L2C` reached **`86.3%` `ASR` at `3.20` `MTok` (`Q = 7.1`)** on all `100` behaviors (vs. `84.8%` / `5.05` `MTok` `EvoSynth`) and **`84.5%` at `3.32` `MTok` (`Q = 7.5`)** on the **`60` HarmBench-disjoint behaviors** (vs. `81.7%` / `5.30` `MTok` `EvoSynth`).

### 2. Ablations: `LOCK` Saves `26.9%` Online Tokens; Versioned Delivery Traces Drive `ASR` (`Tables III & VIII`)

| Variant (`Mixtral-8x7B` $\to$ `Llama-3.1-70B`) | `ASR (%)` | `Mean MTok` | `Queries (Q)` | `C_75 (MTok)` | Invalid Patch Rate | Diagnostic Takeaway |
|:-----------------------------------------------|:---------:|:-----------:|:-------------:|:-------------:|:------------------:|:--------------------|
| **`L2C` (Full)** | **`84.5`** | **`3.35`** | **`7.6`** | **`2.40`** | **`1.5%`** | Full `CONTINUE`/`REFINE`/`RESTRUCTURE`/`LOCK` + versioned traces |
| **`Without LOCK`** | `84.3` | `4.25` (`+26.9%`) | `7.8` | `3.15` (`+31.3%`) | `1.9%` | Re-invoking controller & churning stable workflows wastes `0.90M` tok/ep |
| **`Unlinked trace`** | `82.6` | `3.80` | `8.9` | `2.95` | `2.6%` | Equal-length summaries without node/version delivery links mislocalize edits |
| **`Outcome-only feedback`** | `81.5` | `4.40` | `10.5` | `3.65` | `3.4%` | Hiding intermediate node I/O forces blind trial-and-error restructuring |
| **`Fixed organization` (`Refine` only)** | `80.2` | `3.90` | `9.8` | `3.35` | `2.1%` | Prompt-only node tuning fails when topology/bindings are mismatched |
| **`Frozen workflow` (`Continue` only)** | `77.8` | `4.15` | `11.4` | `3.85` | `N/A` | Static seed graph wastes passes on harder cases |
| **`Interface-only SFT`** | `77.2` | `4.55` | `12.1` | `4.30` | `1.8%` | Valid JSON patches (`1.8%` invalid) without counterfactual execution supervision |
| **`Untrained controller`** | `75.0` | `4.85` | `13.2` | `4.85` | **`14.8%`** | High schema/binding failure rate + noisy edits |

---

## Relevance to Praxis

- **Rules**: [`rules/agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md) — `"DO: Charge internal coordination and evaluator tokens to the online red-team budget, version input-delivery traces, and decouple workflow-edit locking from episode stopping"`.
- **Related Artifacts**: [`pace-multi-agent-compute-parity-synthesis`](pace-multi-agent-compute-parity-synthesis.md) (`PACE`, `arXiv:2611.17610`), [`autopi-taxonomy-coverage-adaptive-red-teaming`](autopi-taxonomy-coverage-adaptive-red-teaming.md) (`arXiv:2611.24313`), [`coordinator-executor-prompt-optimization`](../skills/coordinator-executor-prompt-optimization/SKILL.md), and [`scoped-multi-agent-harness-composition`](../skills/scoped-multi-agent-harness-composition/SKILL.md).
