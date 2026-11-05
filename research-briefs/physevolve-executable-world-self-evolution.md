# PhysEvolve: Verifier-Grounded Self-Evolution for Physical Reasoning with Executable Worlds

> **Source**: [arXiv:2610.34921](https://arxiv.org/abs/2610.34921) — *PhysEvolve: Verifier-grounded Self-evolution for Physical Reasoning with Executable Worlds* (`src:2610-34921`)
> **Authors**: Zihan Wang et al. (2026)
> **Category**: Verifier-Grounded Self-Evolution / Multimodal World Models & Physical Reasoning
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Executive Summary

Self-play and zero-data self-evolution have succeeded in symbolic domains (math, code) where deterministic compilers or unit tests verify proposed problems. Extending self-evolution to **multimodal physical reasoning** in Vision-Language Models (VLMs) fails under naive self-play for two documented reasons: **task-space starvation** (an unconstrained proposer generates `0 / 100` rounds of intervention or counterfactual tasks, collapsing onto easy forward-prediction prompts) and a **learnability illusion** (graded continuous proximity rewards climb to `0.373–0.787` while exact accuracy sits at **`0.00%–6.63%`** as the solver hacks the metric by predicting stationary velocities `746` times or median parameter rungs `145` times).

**PhysEvolve** resolves both failure modes by grounding VLM self-evolution (`Qwen3-VL-8B-Instruct` trained for 100 GRPO steps) in a **deterministic 3D rigid-body physics engine** that compiles model-proposed executable world programs (`PhysDSL`), enforces a strict information boundary between the proposer's symbolic state and the solver's rendered video, and simulates **matched baseline and counterfactual branches** under identical random seeds. Without using any human-labeled physical reasoning data, PhysEvolve improves `Qwen3-VL-8B-Instruct` on **PhysBench** (Throwing **+8.78 pp**, Judgment **+5.08 pp**), **CausalPhys** real-world videos (Anticipation **+2.46 pp**, Intervention **+2.27 pp**), and zero-shot transfers from rigid bodies to unseen **ContPhy** continuum mechanics (cloth, fluid, rope, soft bodies: Counterfactual Removal **+7.38 pp**, Goal-Pit **+24.44 pp** from `20.00%` to `44.44%`, surpassing `Qwen3-VL-32B`'s `26.7%`).

---

## Architecture & Verifier-Grounded Self-Play

### 1. Why Naive Physical Self-Play Collapses (Table 4 Diagnostics)

Before introducing PhysEvolve, the authors ran a 100-round diagnostic of **Naive Physical Self-Play** (where the VLM proposes scenes over a single baseline rollout and is rewarded by continuous numerical proximity to simulator readouts):

| Reasoning Family | Naive Self-Play Synthesis Share | Mean Graded Proximity Reward | Exact Discrete Accuracy | Zero-Exact Rounds (out of 100) | Documented Shortcut / Collapse |
|:---|:---:|:---:|:---:|:---:|:---|
| **Forward Prediction** | 39 / 100 rounds | 0.373 | **0.00%** | **100 / 100** | Predicted stationary initial velocity (`0.0 m/s`) **746 times** (`57.0%` of 1,309 valid rollouts) to collect partial proximity credit. |
| **Inverse Reasoning** | 32 / 100 rounds | 0.664 | **6.63%** | 61 / 100 |Guessed central default coordinates for pre-collision state. |
| **Parameter Estimation** | 29 / 100 rounds | 0.787 | **5.44%** | 56 / 100 | Defaulted to median parameter rung (`0.50`) **145 times** (`39.4%` of 368 rollouts). |
| **Intervention & Counterfactual** | **0 / 100 rounds** | — | — | — | **Complete task-space starvation**: single-trajectory execution cannot ground "what-if" labels, so the proposer abandoned causal families entirely. |

### 2. Executable World Programs (`PhysDSL`) and Paired Branch Simulation

PhysEvolve couples a **Task-Conditioned Proposer** and a **Video-Only Solver** (sharing the same `Qwen3-VL-8B-Instruct` weights) through an immutable deterministic physics executor $\Phi_\xi$:

1. **Macro-Curriculum Intent Sampling**: Each GRPO step samples $N = 4$ reasoning intents across 3 Newtonian paradigms (*Throwing*, *Collision*, *Motion*) and 8 task intents (spanning forward, inverse, parameter, intervention, and counterfactual reasoning), weighted by a learnability-aware priority:
   $$w_f = \rho_f \max\bigl(0.05,\; 4\bar{a}_f(1 - \bar{a}_f)\bigr)$$
   which concentrates training on medium-difficulty intents ($\bar{a}_f \approx 0.5$) while maintaining a `0.05` floor so no family starves.
2. **Executable World Proposal ($\mathcal{W}, \mathcal{S}$)**: For each intent, the proposer emits $G = 4$ candidate `PhysDSL` programs specifying 3D rigid bodies, initial kinematics, material parameters, and an evidence schema $\mathcal{S}$.
3. **Deterministic Validation & Paired Counterfactual Branching**:
   - The physics engine validates physical stability and executes both the **factual baseline trajectory** $\tau_\emptyset = \Phi_\xi(\mathcal{W})$ and **body-elided counterfactual or parameter-intervened branches** $\tau_B = \Phi_\xi(\mathcal{W} \setminus B)$ under the **exact same random seed $\xi$**.
   - **Dynamic Margin Gate**: A proposed world is admitted only if the causal intervention produces a physically non-trivial difference between branches (e.g., post-window velocity difference $\ge 0.30\text{ m/s}$ or clear contact/outcome separation).
4. **Strict Information Boundary & Discrete MCQ Binding**:
   - To eliminate continuous proximity reward hacking, the executor compiles the verified branch outcomes into a **4-way discrete multiple-choice question** ($a^\star \in \{A, B, C, D\}$) with deterministically generated hard distractors.
   - The **Solver** receives **only the rendered baseline video $\tau_\emptyset$** and the question text—never the `PhysDSL` source code, simulator state, or counterfactual branch video $\tau_B$—and must infer the physical dynamics visually.

---

## Key Empirical Results

### 1. Main Benchmark Results (`Qwen3-VL-8B-Instruct`, Table 1)

| Benchmark & Subset | `Qwen3-VL-8B` (Base) | Naive Self-Play | **PhysEvolve** | Gain vs. Base | Notes / Reference Comparisons |
|:---|:---:|:---:|:---:|:---:|:---|
| **PhysBench Overall** (9,802 items) | 52.9% | 52.4% | **53.5%** | **+0.55 pp** | Naive self-play degrades overall score (−0.5 pp). |
| — *PhysBench: Throwing* | 46.1% | 45.9% | **54.9%** | **+8.78 pp** | Naive self-play drops −0.24 pp on Throwing. |
| — *PhysBench: Motion* | 54.7% | 54.7% | **56.5%** | **+1.74 pp** | |
| — *PhysBench: Judgment* | 34.9% | 34.8% | **40.0%** | **+5.08 pp** | |
| **ContPhy Overall** (1,950 unseen continuum items) | 37.1% | 36.6% | **39.5%** | **+2.5 pp** | Zero-shot transfer from rigid bodies to cloth, fluid, rope, soft bodies. |
| — *ContPhy: Counterfactual Removal* | 44.26% | 43.61% | **51.64%** | **+7.38 pp** | |
| — *ContPhy: Goal-Pit* | 20.00% | 17.78% | **44.44%** | **+24.44 pp** | Beats `Qwen3-VL-32B` (`26.7%`) and `GPT-5.1` (`37.8%`). |
| — *ContPhy: Fluid Flow* | — | — | — | **+11.00 pp** | `+23.00 pp` over branch-disabled ablation. |
| **CausalPhys Overall** (3,057 real-world videos) | 53.9% | 52.8% | **54.5%** | **+0.6 pp** | Sim-to-real transfer to natural video clips. |
| — *CausalPhys: Anticipation* | 55.9% | 54.9% | **58.4%** | **+2.46 pp** | |
| — *CausalPhys: Intervention* | 42.8% | 40.9% | **45.0%** | **+2.27 pp** | |

### 2. Controlled Ablations (Tables 2 & 3)

| Ablation Variant | ContPhy Overall | ContPhy CF-Removal | ContPhy Goal-Pit | CausalPhys Overall | Key Finding |
|:---|:---:|:---:|:---:|:---:|:---|
| **PhysEvolve (Full)** | **39.54%** | **51.64%** | **44.44%** | **54.50%** | Full paired-branch verifier + co-evolving proposer/solver. |
| **w/o Paired Branch Simulation** (single rollout only) | 37.90% | 43.44% (−8.20 pp) | 21.11% (−23.33 pp) | 53.68% | Without counterfactual branch execution $\tau_B$, causal transfer collapses back to base level. |
| **w/o Margin Gate** (no $\ge 0.30\text{ m/s}$ filter) | 38.41% | 47.54% (−4.10 pp) | 35.56% (−8.88 pp) | 53.91% | Degenerate near-identical branches inject label noise into counterfactual MCQs. |
| **Solver-Only GRPO** (Proposer frozen) | 17.85% | — | — | 15.01% (parse rate 26.07%) | Updating only the Solver while freezing the Proposer causes severe representation drift and output format collapse. |

---

## Why Not a Skill?

PhysEvolve is a domain-specific VLM reinforcement learning pipeline coupled to a 3D rigid-body physics engine (`PhysDSL`), rather than a general-purpose agent runtime procedure. However, its diagnostic proof of the **learnability illusion** under continuous proximity rewards (`0.373–0.787` graded reward vs. `0.00%–6.63%` exact accuracy) and **task-space starvation** (`0 / 100` counterfactual rounds without paired branch simulation) directly reinforces Praxis rules on verifier-grounded self-improvement and anti-reward-hacking gate design.

---

## Related Artifacts

- **Rules**:
  - [`recursive-improvement.md`](../rules/recursive-improvement.md) — Verifier-grounded self-improvement and acceptance gating.
  - [`agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md) — Discretized, margin-gated verification vs. gameable continuous proximity scores.
- **Skills**:
  - [`reward-hacking-immunization`](../skills/reward-hacking-immunization/SKILL.md) — Detecting and eliminating metric shortcuts in RL and self-evolution loops.
- **Research Briefs**:
  - [`flowbalance-verifier-grounded-self-improvement.md`](flowbalance-verifier-grounded-self-improvement.md) — Preventing mode collapse in verifier-grounded self-improvement.
  - [`trace-causal-exploration.md`](trace-causal-exploration.md) — Synthesizing causal exploration rewards for reasoning agents.
