---
name: constructed-exam-nash-evaluator-evolution
description: >
  Recursively evolve multi-dimensional evaluators, judges, or reward models in
  domains without a native ground-truth verifier by anchoring selection on
  construction-defined clean-vs-perturbed proxy exams, pairing dimension-advocate
  proposers with a defensive guard slot and compact rolling lessons ledger,
  filtering candidate updates via weighted log Nash bargaining with per-dimension
  and per-family drop floors, and refreshing the exam curriculum between stages
  upon saturation. Derived from "EVA-RSI: Recursive Self-Improvement of Video
  Evaluators for Judging Temporal Quality" (arXiv:2611.23890).
source: https://arxiv.org/abs/2611.23890
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Constructed-Exam & Nash-Bargaining Evaluator Evolution

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

Use this skill when **iteratively improving a multi-dimensional evaluator, LLM/VLM judge, or RL reward model in a domain that lacks a deterministic task verifier** (such as temporal video/audio quality, UI/design fidelity, multi-criterion code/patch review, or multi-objective clinical/legal rubric grading), where naive single-stage fine-tuning or unweighted scalar averaging improves targeted failure modes only by degrading existing capabilities or collapsing downstream policy optimization.

## When to Use

- You need to improve an open-weight or configurable evaluator across $K \ge 3$ competing quality dimensions (e.g., physics, consistency, smoothness, dynamics, real-world calibration) while strictly protecting existing capabilities (semantics, visual/text quality, general human preference, general understanding) without collecting massive new human-preference labels every round.
- Your current reward model or judge exhibits blind spots or inverted correlations that cause downstream RL or best-of-$N$ filtering to collapse into degenerate shortcuts (for example, `VideoReward` scoring `-0.311` Spearman on `VideoScore-Bench` dynamics and collapsing `Wan2.1 T2V-1.3B` `DiffusionART` RL into static face close-ups with dynamic degree dropping from `0.579` to `0.351`/`0.271` under fair KL/clipping and `0.095` at update `120` without penalties in `arXiv:2611.23890`).
- Single-pass union fine-tuning over synthetic defect datasets improves targeted synthetic tests (`0.889` main mean) while violating human-preference floors (`0.558` vs. `0.660` required) and underperforming recursive multi-step curriculum refinement on external benchmarks (`0.53` vs. `0.71` public rank score).

Do **not** use this skill when an exact deterministic task oracle already exists (`unit tests`, `SMT/symbolic solver`, compiler) — use [`verifier-gap-sign-pre-rl-audit`](../verifier-gap-sign-pre-rl-audit/SKILL.md) to audit fast proxies against that oracle instead — or when optimizing prompt/skill text against an already-trusted frozen frontier judge (use [`dense-rubric-skill-evolution`](../dense-rubric-skill-evolution/SKILL.md)).

## Core Insight

Recursive self-improvement requires a fast, reliable selection signal, yet perceptual and subjective evaluation domains have no compiler or unit-test oracle (`arXiv:2611.23890`). Two mechanisms make verifier-free evaluator evolution compound onto external benchmarks and downstream RL rather than gaming its own synthetic rubric:

1. **Construction-Defined Directional Exams + Anchors**: Even when nobody can assign an exact ground-truth quality scalar to an arbitrary wild artifact, **controlled perturbation of a clean reference defines ground-truth directional order by construction** (a clean clip outranks its frame-dropped, jittered, warped, or frozen counterpart; a subtle severity tests calibration sensitivity without changing the sign). Pairing bidirectional pairwise comparisons (`A vs. B` and `B vs. A`, ties $= 0.5$) and standalone discrete rating expectations ($1 - |\mathbb{E}[r] - t|/4$) with a small slice of high-separation real human-scored pairs ($\ge 2$-point gap) and explicit forgetting guards turns an unverifiable domain into a reproducible vector exam $\mathbf{s}(m) \in [0, 1]^D$.
2. **Weighted Log Nash Bargaining Over Disagreement Floors**: Scalar mean rules allow a large gain on one neglected dimension to mask regressions on previously fixed dimensions or minority defect families. Accepting a candidate $m$ over incumbent $m^\star$ only when every dimension stays strictly above a disagreement point $d_i = s_i^{\text{start}} - \Delta_i^{\text{floor}}$ and the weighted Nash product increases:

$$\Phi(\mathbf{s}) = \sum_{i=1}^{D} w_i \log(s_i - d_i), \qquad s_i > d_i \;\;\forall i$$

makes acceptance **concave near every floor**—penalizing regressions steeply as any guard approaches its limit while rewarding balanced multi-dimensional progress without hand-tuning Pareto tradeoff weights each round.

Across `2` stages (`88` rounds, `170` candidates, `8` champions, `944` `B200` GPU hours) starting from `Qwen3-VL-8B-Instruct`, `EVA-RSI` lifted hidden-test main accuracy from **`0.706` to `0.906` (`+0.200`, 95% CI `[0.181, 0.219]`; smoothness `0.461 -> 0.888`, `+0.427`)** while raising all `4` forgetting guards (`+0.004` to `+0.041`), generalized **`+0.159` (`0.754 -> 0.913`)** to `10` unseen defect families, climbed from **`0.407` to `0.721`** mean rank score across `12` public benchmarks (`21` models, `#1` of `21` on `VideoScore-Bench` dynamics `0.611` and `VBench` dynamics `0.906` ahead of `GPT-5.6 Sol` and `Claude Opus 5.5`), and passed **`32/32` Holm-corrected downstream `DiffusionART` RL motion tests** (`0.579 -> 0.848/0.892` dynamic degree).

---

## Step-by-Step Procedure

### Step 1: Build Disjoint Construction-Defined Proxy Exam Banks

Before running any training candidate, construct **three strictly clip/item- and prompt-disjoint exam splits** (`Dev-A`, `Dev-B`, and a `Hidden Test` bank never accessible to any agent):

1. **Synthesize directional clean-vs-perturbed families across target dimensions**:
   - Start from clean, vetted reference artifacts and apply controlled programmatic or generative corruptions spanning distinct failure mechanisms per target dimension (e.g., `64` question types across physics, consistency, smoothness, and dynamics in `arXiv:2611.23890`), including **subtle/mild severities** alongside heavy corruptions so candidates cannot win via coarse artifact thresholds alone.
   - Hold out at least `8–10` perturbation families exclusively inside `Hidden Test` (`440` questions in `EVA-RSI`) to audit whether accepted updates generalize beyond the training/dev corruption taxonomy.
2. **Score both pairwise orderings and standalone absolute calibration**:
   - **Bidirectional pairwise tasks**: Present every `(clean, perturbed)` pair in both `(A, B)` and `(B, A)` orders under a fixed prompt; count ties as `0.5` so position bias (`always pick A`) yields `0.5` rather than apparent progress.
   - **Standalone `1–5` calibration tasks**: Extract next-token probabilities over rating digits `{1, 2, 3, 4, 5}`, compute $\mathbb{E}[r] = \sum_{k=1}^{5} k\,p(k)$, and score $1 - |\mathbb{E}[r] - t|/4$ against target $t$ (`5` clean, `1` heavy defect, intermediate for mild severities). Without standalone rating anchors, pairwise-only training compresses score dynamic range needed by downstream RL and data filtering.
3. **Attach real-distribution anchors and four-category forgetting guards**:
   - Add a **real-distribution dimension** sourced from multi-rater human annotations filtered to high-confidence pairs ($\ge 2$-point rating separation on a `1–5` scale; adding real pairs in Stage 2 jumped real-video hidden-test accuracy from `0.755` to `0.852` in a single accepted step `c001`).
   - Add explicit **guard dimensions** covering (a) prompt/semantic alignment, (b) surface perceptual/text quality, (c) multi-aspect human preference (`VideoGen-RewardBench`-style slices), and (d) general domain QA/understanding so specialization cannot hollowed out the base model.
4. **Rotate dev splits (`Dev-A` / `Dev-B`)**: Alternate or split fast search vs. full gate checks across two disjoint dev banks (`~2.9k` questions each in `EVA-RSI`) to damp finite-bank selection noise.

### Step 2: Run Dimension-Advocate Proposers with a Defensive Slot, Rolling Ledger, and Diff Gate

In each round $t$, run a structured multi-role agent loop around incumbent champion $m^\star$ under a strict per-candidate compute cap (e.g., $\le 1.5\text{ h}$ training on `4` GPUs per candidate):

1. **Dimension Advocates + Leader Slot Allocation**:
   - Assign one Advocate per target dimension to inspect per-dimension/per-family dev breakdowns (never raw exam items) and propose concrete data, sampling, temporal/context resolution, or loss recipes (e.g., increasing sampled frames `32 -> 54` and pixel budget `147k -> 230k` alongside targeted contrastive/anchor replay).
   - Have a **Leader** allocate the parallel GPU candidate slots across dimensions with largest remaining headroom **while reserving at least one defensive slot whenever any guard dimension approaches within `0.01` of its disagreement floor**.
2. **Maintain a compact rolling lessons file (`<= 700` words)**:
   - Update a capped, structured summary of *what failed, which floor tripped, and which recipe interactions compounded* rather than appending raw multi-round logs (`10k–28k` token histories degrade proposer focus). Removing score/outcome memory in a non-recursive `10`-candidate control (`212` GPU hours) caused **`0/10` candidates to pass the acceptance rule** (`9` missed floors, `1` exceeded budget).
3. **Enforce a pre-training Reviewer diff gate**:
   - Automatically inspect every candidate's code/config diff before GPU launch and **veto** any patch that reads exam paths/assets, alters evaluation prompts or scoring code, disables safety/precision invariants, or exceeds the per-candidate wall-clock budget (`20/170` candidates vetoed pre-run in `EVA-RSI`).

### Step 3: Gate Candidate Promotion via Weighted Log Nash Bargaining & Family Drop Floors

Score each finished candidate $m$ on the dev exam vector $\mathbf{s}(m)$ against stage-start baseline $\mathbf{s}^{\text{start}}$ and current champion $\mathbf{s}(m^\star)$. Promote $m$ to stage champion **only if all five conditions hold simultaneously**:

1. **Strict floor survival (Disagreement Points)**: Every main and guard dimension satisfies $s_i(m) > d_i$, where $d_i = s_i^{\text{start}} - \delta_i^{\text{floor}}$ (e.g., $\delta_i^{\text{floor}} = 0.02$ on synthetic/general dimensions and tighter `0.015` on human-preference guards).
2. **Per-step non-collapse & per-family drop caps**:
   - No single dimension drops by more than `0.03` relative to current champion $m^\star$: $s_i(m) \ge s_i(m^\star) - 0.03$.
   - **Per-family floor**: No individual defect family with $\ge 40$ questions drops by more than `0.12`, and no sub-aspect of the human-preference guard drops by more than `0.05` (preventing within-dimension cannibalization where fixing one physics artifact breaks another).
3. **Statistically verified main-dimension progress (or bounded saturation guard recovery)**:
   - Require main-dimension mean gain $\bar{s}_{\text{main}}(m) - \bar{s}_{\text{main}}(m^\star) \ge 0.01$ with **90% paired cluster-bootstrap lower confidence bound $> 0$** (clustering at the source clip/prompt level so correlated questions on the same item do not inflate significance), **or** in late-stage saturation allow $|\Delta \bar{s}_{\text{main}}| \le 0.005$ when guard mean improves by $\ge 0.005$ (which recovered guard slack at `c046` in `EVA-RSI`).
4. **Positive Weighted Log Nash Gain**:
   $$\sum_{i=1}^{D} w_i \log\!\big(s_i(m) - d_i\big) > \sum_{i=1}^{D} w_i \log\!\big(s_i(m^\star) - d_i\big)$$
   using `w_i = 1.0` for main dimensions, `0.75` for human-preference guards, and `0.5` for Auxiliary/General guards. (Replaying Stage 2 without the Nash condition in `arXiv:2611.23890` `Table S5` accepted `3` physics-degrading candidates `c010`, `c035`, `c056` whose hidden-test human preference regressed `-0.003` to `-0.007` with `-0.002` to `+0.003` net main movement.)
5. **Defer persistent deployment to the single global acceptance gate**: Treat within-stage Nash promotions as **search-time incumbent selection**; before promoting any stage champion to production or downstream RL reward duty, pass it through `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../../rules/recursive-improvement.md) on the untouched `Hidden Test` bank, unseen defect families, and downstream behavioural checks.

### Step 4: Detect Exam Saturation and Refresh the Curriculum Between Stages

Proxy exams have a finite ceiling: once candidates plateau within `[-0.004, +0.001]` across `10–15` consecutive scored proposals (as observed after `c071` in Stage 2 and across `0/100` accepted candidates in an unrefreshed Stage 3 in `EVA-RSI`), **stop burning GPU hours on the frozen exam** (pair with [`self-evolution-stopping-rule`](../self-evolution-stopping-rule/SKILL.md)):

1. **Audit the stage champion out-of-band** on external public benchmarks and small downstream policy rollouts to identify residual blind spots (for example, Stage 1 `c046` reached `0.872` hidden-test main accuracy yet barely moved public benchmark rank `0.407 -> 0.434` until Stage 2 diagnosed real-video calibration gaps and per-family regressions).
2. **Execute a human-governed between-stage exam refresh** (never let the optimizing agent edit its own exam): add real human-labeled high-separation anchors, subtle perturbation severities, and per-family drop caps, re-anchor $d_i$ to the incoming champion's scores on the refreshed exam, and launch the next stage from the prior stage's champion weights (replaying winning recipe `c033` directly from the base `Qwen3-VL-8B` model instead of the Stage-1/early-Stage-2 curriculum lineage collapsed hidden-test main accuracy from `0.902` to **`0.757` / `0.756`** and smoothness from `0.850` to **`0.514` / `0.505`**).

---

## Environment Caveats

- **Proposer reasoning capability is load-bearing**: Running the exact same starting checkpoint, dev banks, GPU budget, and Nash acceptance gate with a weaker `Grok` coding/proposer agent produced **`0` accepted champions**, because proposals failed to diagnose multi-guard trade-offs or pass execution constraints (`Claude Opus 5.5` agent calls cost `~$1,700` across `170` candidates).
- **High candidate attrition is normal—budget for failed/rejected trials**: Out of `170` proposed candidates in `EVA-RSI`, `83` went unscored (`52` training job failures, `20` Reviewer implementation vetoes, `6` driver restarts, `5` unfinished at cutoff) and `79` were scored and rejected (`63` insufficient main gain, `15` floor violations, `1` family-guard violation), leaving `8` accepted steps (`4.7%`). Automate fast job-health checks and diff vetoes so failed runs terminate in minutes rather than hours.
- **Downstream RL still requires standard KL / clipping hygiene**: Even with an evolved evaluator, validate downstream RL across multiple seeds and checkpoints (`32/32` Holm-adjusted motion tests passed on `Wan2.1 T2V-1.3B` at update `50`) rather than running unregularized long-horizon RL indefinitely.

## Failure Modes

- **Replacing sequential curriculum evolution with one-shot union SFT**: Pooling all discovered synthetic datasets into a single `384`-GPU-hour `Union SFT` run hit `0.889` synthetic main accuracy but **broke the human-preference floor (`0.558` vs. `0.660`)** and dropped public rank score from `0.71` to `0.53`; adding manual anchor mixing (`Union + anchors`) passed floors but stalled at `0.848`/`0.844` (`-0.058` below `EVA-RSI`, `-0.205` on smoothness).
- **Subtle perturbation polarity bugs in constructed exams**: Ensure programmatic perturbations never invert ground truth on edge cases—in `EVA-RSI`, `36` slow-motion clips became *more* plausible when reversed (`0.906` raw vs. `0.916` excluding those `36` items), illustrating why manual sanity spot-checks of constructed perturbation polarity are mandatory before locking an exam stage.
- **Unbounded reflection logs or stateless parallel sampling**: Letting round logs grow to `10k–28k` tokens buries floor-violation lessons, while dropping cumulative score/outcome memory (`0/10` accepted in stateless search) causes proposers to repeatedly trip the same human-preference guards.

## Cross-References

- [`recursive-improvement.md`](../../rules/recursive-improvement.md) — `"DO: Anchor verifier-free multidimensional evaluator evolution on construction-defined proxy exams and Nash bargaining with family-level drop floors"`, `"DO: Pass every self-modification through one acceptance gate"`, and `"DO: Stop self-evolution loops on sequential evidence, not a fixed round budget"`
- [`agent-evaluation-quality.md`](../../rules/agent-evaluation-quality.md) — Multi-aspect judge calibration and bidirectional position-bias controls
- [`verifier-gap-sign-pre-rl-audit`](../verifier-gap-sign-pre-rl-audit/SKILL.md) — Pre-RL synthetic probe audit when a ground-truth process oracle *can* be constructed on a reference slice (`arXiv:2611.21538`)
- [`dense-rubric-skill-evolution`](../dense-rubric-skill-evolution/SKILL.md) — Bilevel dense rubric surrogate calibration when evolving skills/prompts rather than evaluator weights (`SkillLift`, `arXiv:2609.15396`)
- [`regularized-harness-evolution`](../regularized-harness-evolution/SKILL.md) — Bounded editable sets and retention floors in harness RSI (`RRSI` / `Video-RSI`, `arXiv:2609.24972`, `arXiv:2609.37950`)
- [`reward-hacking-immunization`](../reward-hacking-immunization/SKILL.md) — Online post-selection drift and reward-hacking detection (`HackProbe`, `arXiv:2609.04665`)

## Sources

- Yu Yuan, Ruizhou Ding, Shaoheng Fang, Stanley H. Chan & Zhuo Chen, "EVA-RSI: Recursive Self-Improvement of Video Evaluators for Judging Temporal Quality" ([arXiv:2611.23890](https://arxiv.org/abs/2611.23890), `src:2611-23890v1`)
