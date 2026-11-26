---
name: observation-attributed-tool-data-sampling
description: >
  Calibrate agentic tool calling under pure outcome-only RL (GRPO) by
  partitioning decision states via counterfactual observation probes and
  dynamically adapting category sampling weights (AOVO + PADS) instead of
  engineering call-contingent rewards.
source: arXiv:2611.28558
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Observation-Attributed Tool Data Sampling

Train selective, non-hackable tool invocation in tool-using agents (`OCR`, chart/document parsers, visual crop/zoom, retrieval, or diagnostic analyzers) by keeping reinforcement learning rewards strictly **outcome-only** ($R(\tau) = \mathbb{1}[\hat{y}(\tau) = y^\star]$) and governing tool-call incentives through counterfactual observation attribution (`AOVO`) and policy-adaptive category sampling (`PADS`).

## When to Use

- Post-training tool-using agents (multimodal document/chart VLM agents, RAG/search agents, or diagnostic CLI/API agents) where naive SFT causes indiscriminate over-calling (`-2.8` net causal tool gain) and vanilla `GRPO` suffers late-stage accuracy collapse (`0.66 -> 0.52`).
- Replacing brittle multi-component RL reward engineering (per-call bonuses, step penalties, or call-necessity process rewards) that induce reward hacking—either calling tools on trivial inputs for bonus credit or suppressing necessary calls to avoid penalties.
- Auditing an existing tool-use training dataset to separate states where tool observations genuinely repair missing evidence from states where noisy tool outputs corrupt correct internal reasoning.

## Core Insight

Under outcome-only `GRPO`, positive rollout variance mixes two indistinguishable sources: **missing external evidence** (which tool observations resolve) and **internal reasoning stochasticity** (where tool observations are irrelevant or actively harmful). Worse, standard dynamic difficulty filtering (`DAPO`-style zero-variance rejection) progressively discards `Repairable` examples as the policy improves (`50% -> 11%` of effective updates by step `600`), concentrating late updates on `Hard` (`41%`) and `Reasoning-dominated` (`28%`) states that erode both tool-free competence and call selectivity.

`AOVO` (`arXiv:2611.28558`) moves tool-use credit assignment from the **reward function** to the **training data distribution**:
1. **Counterfactual Observation Attribution**: Branch from the exact pre-decision prefix $s$ *with* vs. *without* each candidate tool's observation ($\Delta_e(s) = \hat{p}^e(s) - \hat{p}^\varnothing(s)$) to partition states into `Repairable`, `Harmful`, `Reasoning-dominated`, `Hard`, and `Saturated`.
2. **Policy-Adaptive Data Sampling (`PADS`)**: Re-probe a tiny stratified slice every $T = 100$ RL steps (`~3.6%` extra rollout compute) and update category sampling probabilities using conditional causal uplift (`ATT`, `ATU`, `ALT_hard`) above hard category floors so neither calling pressure (`Repairable`) nor restraint pressure (`Harmful`) vanishes.

## Step-by-Step Procedure

### Phase 1: Counterfactual Observation Probing (`AOVO`)

1. **Ensure minimal observation literacy before probing**:
   - If the base checkpoint cannot parse returned tool formats (`JSON` tables, cropped image regions, OCR spans), run a brief `1-epoch` format-literacy warmup on a small probe subset (`~2K` tool-containing examples) or parse directly if native tool literacy already yields high assignment agreement (`94.1%` reproduction, $\kappa = 0.89$ on `Qwen2.5-VL-7B-Instruct`).
2. **Locate the first decision state $s$ per training instance**:
   - Roll out the initial policy on each candidate example $(x, y^\star)$ and extract prefix $s$ immediately **before the first tool call** (or before the final answer if no tool was called).
3. **Measure counterfactual observation uplift $\Delta_e(s)$**:
   - From prefix $s$, sample $m = 4$ stochastic continuations (`temperature = 1.0`) **without** any tool observation to estimate baseline pass rate $\hat{p}^\varnothing(s)$.
   - For each candidate tool $e \in \mathcal{E}$ (evaluating a deterministic heuristic parameter binding when $s$ had no call, plus the policy's actual call parameters when $s$ issued a call), inject observation $o_e$ and sample $m = 4$ continuations to estimate $\hat{p}^e(s)$ and causal uplift $\Delta_e(s) = \hat{p}^e(s) - \hat{p}^\varnothing(s)$.
   - Optionally run an **observation-free null control** (appending a neutral placeholder token instead of $o_e$ on a small audit slice) to verify that prompt-length jitter triggers `< 3%` false `Repairable`/`Harmful` labels (`2.3% ± 0.5%` vs. `53%` with real observations).
4. **Partition examples into five causal categories** (with $\delta = 0.5$, $\epsilon = 1/m = 0.25$):
   - **`Saturated`**: $\hat{p}^\varnothing(s) \ge 1 - \epsilon$ and $\hat{p}^e(s) \ge 1 - \epsilon$ for all $e \in \mathcal{E}$ (already solved reliably regardless of tools).
   - **`Hard`**: $\hat{p}^\varnothing(s) \le \epsilon$ and $\hat{p}^e(s) \le \epsilon$ for all $e \in \mathcal{E}$ (currently beyond reach across all branches).
   - **`Repairable`**: Not `Saturated`/`Hard`, and $\exists e \in \mathcal{E}$ with $\Delta_e(s) \ge \delta$ (missing perceptual/retrieved evidence that tool $e$ supplies).
   - **`Harmful`**: No tool achieves $\Delta_e(s) \ge \delta$, and the policy's chosen tool satisfies $\Delta_e(s) \le -\delta$ (spurious or noisy tool output corrupts a solvable problem).
   - **`Reasoning-dominated`**: All remaining examples ($|\Delta_e(s)| < \delta$; outcome variance stems from internal reasoning rather than tool observations).

### Phase 2: Construct Observation-Consistent Cold-Start SFT Trajectories

1. **Match SFT supervision strictly to each state's causal category**:
   - **`Repairable`**: Retain student prefix $s$, invoke the highest-uplift tool $e^\star = \arg\max_e \Delta_e(s)$, append real observation $o_{e^\star}$, and keep a correct student continuation (using a stronger teacher *only* to revise the post-observation reasoning continuation on the `~12%` of cases where the student misreads a valid observation—never altering pre-call prefix $s$).
   - **`Harmful` & `Saturated`**: Retain the student's own correct **tool-free** continuation from $s$ so SFT explicitly teaches restraint when observations hurt or add zero value.
   - **`Reasoning-dominated` & `Hard`**: Merge for SFT and generate a clean tool-free reasoning continuation (teacher-guided where the student failed all $m$ branches) to strengthen standalone reasoning before RL.
2. **Fine-tune briefly (`~3` epochs, `LR = 1e-5`)** to establish calibrated cold-start priors before RL.

### Phase 3: Outcome-Only `GRPO` with Policy-Adaptive Data Sampling (`PADS`)

1. **Exclude `Saturated` items and initialize category sampling weights**:
   - Drop `Saturated` items (and zero-pass `pass@8 = 1.0` trivial prompts) from the RL pool.
   - Set initial sampling weights over `(Repairable, Harmful, Reasoning-dominated, Hard)` to:
     $$w^{(0)} = (0.50,\; 0.25,\; 0.10,\; 0.15)$$
   - Keep the RL reward **strictly binary outcome-only**: $R(\tau) = \mathbb{1}[\hat{y}(\tau) = y^\star]$ (`0` call bonuses, `0` step penalties, `KL` coefficient `0.01`).
2. **Re-probe on a coarse interval ($T = 100$ steps) over a rolling window ($W = 15$ steps)**:
   - Every $T = 100$ RL steps (never $T = 10$, which adds `+36.0%` rollout compute and high-variance weight oscillation), sample a small stratified slice across the four active categories (`~3.5%–3.8%` extra rollout compute) and compute category-conditional learning signals over the trailing $W = 15$ steps:
     - On **`Repairable`**, measure **Average Treatment on the Treated (`ATT`)**: reward gain of trajectories that actually invoked the tool over trajectories on the same prompt that abstained ($\max(0, \hat{r}_{\text{call}} - \hat{r}_{\text{no-call}})$).
     - On **`Harmful`**, measure **Average Treatment on the Untreated (`ATU`)**: reward advantage of abstaining over calling ($\max(0, \hat{r}_{\text{no-call}} - \hat{r}_{\text{call}})$).
     - On **`Reasoning-dominated`**, measure within-prompt rollout reward standard deviation (effective gradient signal for pure reasoning).
     - On **`Hard`**, run an alternative-tool probe (`ALT_hard`) to detect newly unlocked states transitioning into `Repairable`.
3. **Update weights via EMA with mandatory non-zero category floors**:
   - Normalize raw category scores $s_k$ (if $\sum_j s_j < 0.01$, skip the update and retain current weights), apply EMA smoothing ($w^{(t)} = (1 - \alpha) w^{(t-1)} + \alpha \tilde{s}$ with $\alpha = 0.5$), and project onto **hard minimum floors**:
     $$w_{\min} = (0.40,\; 0.20,\; 0.10,\; 0.05)$$
     renormalizing the surplus across categories.
4. **Audit post-training tool selectivity via `MED` (`Gain` vs. `Harm`) and gate promotion**:
   - Evaluate final checkpoints by contrasting free tool-enabled accuracy against forced no-tool accuracy on held-out tasks to verify positive **Net Gain** (`Gain - Harm > 0`; `+4.4` on `OCRBench` vs. `-2.8` after SFT and `+0.6` under `Vanilla GRPO`), and pass any promoted policy checkpoint through `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../../rules/recursive-improvement.md).

## Failure Modes & Guardrails

- **Dropping `Harmful` or `Repairable` floors**: Zeroing `Harmful` in RL causes `83.4%` indiscriminate tool calling (`-3.5` Net Gain on `OCRBench`), while `4x` `Harmful` (`57.1%` share) suppresses calling to `6.9%`; zeroing `Repairable` collapses calling to `1.2%` (`-6.0` perception points), while `4x` `Repairable` (`80.0%` share) drives `98.1%` calling (`-4.3` Net Gain). Always enforce $w_{\min} = (0.40, 0.20, 0.10, 0.05)$.
- **Over-sampling `Reasoning-dominated` prompts in tool RL**: Scaling `Reasoning-dominated` `4x` (`30.8%` share) inflates spurious tool calls (`45.2% -> 72.8%`, `-3.1` Net Gain) because high outcome variance tricks outcome-only `GRPO` into superstitious calling unless balanced by `Harmful` restraint examples.
- **Over-frequent re-probing ($T = 10$)**: Re-probing every `10` steps adds `36.0%` compute overhead and tracks transient mini-batch noise (`80.2 ± 1.4` perception vs. `82.6 ± 0.2` at $T = 100$); if online re-probing is infeasible, static $w^{(0)}$ ($T = \infty$, `0%` extra compute) still recovers `+1.8` perception points and `+2.7` Net Gain over `Vanilla GRPO`.

## Cross-References

- **Rules**: [`recursive-improvement.md`](../../rules/recursive-improvement.md) — `"DO: Audit RLVR process verifiers on a model-free probe grid for selection error and gap sign, and couple pessimistic-biased rewards with saturation pilots"` and `"DO: Pass every self-modification through one acceptance gate"`.
- **Skills**: [`necessary-tool-evidence-path`](../necessary-tool-evidence-path/SKILL.md) — Trajectory-level call-necessity supervision (`NTEP`) when outcome-only category sampling is unavailable (`AOVO` replaces process-level call rewards with counterfactual data sampling).
- **Skills**: [`verifier-gap-sign-pre-rl-audit`](../verifier-gap-sign-pre-rl-audit/SKILL.md) — Pre-RL audit when learned proxy verifiers must be used instead of exact outcome indicators.
- **Skills**: [`history-guided-trajectory-collection`](../history-guided-trajectory-collection/SKILL.md) — Stagnation-triggered SFT branching for multi-step repository exploration (`SWE-Trail`).
- **Specs**: [`self-improving-agent.spec.md`](../../specs/self-improving-agent.spec.md) — RL post-training and reward-hacking prevention checklists.

## Sources

- *From Reward Engineering to Data-Centric Reinforcement Learning for Effective Agentic Visual Tool Use* (`AOVO`, `arXiv:2611.28558`)
