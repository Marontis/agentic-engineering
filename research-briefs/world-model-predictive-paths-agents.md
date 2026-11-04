# Self-Improving Agents with World Model Predictive Paths

> **Source**: [arXiv:2610.28945](https://arxiv.org/abs/2610.28945) — *Self-Improving Agents with World Model Predictive Paths* (`src:2610-28945`)
> **Authors**: Haori Lu, Tianyu Gao, Yaoyao Liu, Yingying Li (UIUC, 2026)
> **Category**: Agent Planning & World Models / Test-Time Experience-Guided MPC

---

## Executive Summary

ReAct-style agents commit to a single proposed action per environment step, risking irreversible mistakes under partial observability, while multi-step tree search (`ToT`, `LATS`, `RAP`) incurs exponential rollout overhead. Lu et al. introduce a **test-time, training-free framework inspired by Model Predictive Path Integral (MPPI) control** that keeps all model weights frozen and couples **one-step world-model outcome imagination** over $K$ candidate actions with a **dual-branch experience memory** (a **planner branch** that refines candidate proposal and final action selection, and a **world-model branch** that refines next-observation prediction from prediction mismatches).

Evaluated on **ALFWorld** (134 tasks) and **ScienceWorld** (90 tasks) across three backbones (`Gemma-4-26B-A4B`, `Qwen3.5-9B`, and `GPT-5.4-mini`), the method ranks **first in 9 of 12 benchmark comparisons and second in the remaining 3**. With `Gemma-4-26B-A4B`, it reaches **65.7% `SR@1` / 84.3% `SR@5`** on ALFWorld (beating the strongest baseline `ITP-I` by **+32.9 / +29.8 points** and `ReAct` by **+45.6 / +59.7 points**) and **46.7% `SR@1` / 60.0% `SR@5`** on ScienceWorld (**+10.0 / +10.0 points** over `ITP-I`).

---

## Method & Regret Decomposition

### 1. MPPI-Inspired Predict–Weight–Select Loop

At each environment step $t$ (with budget $T = 30$ steps), the agent executes a four-stage lookahead cycle without stepping the real environment:

1. **Candidate Proposal ($q_\pi$)**: Conditioned on goal $g$, history $h_t$, current observation $o_t$, and retrieved candidate-generation memory $M_t^{\text{cand}}$, the proposal policy generates $N_t \le K$ (default $K = 8$) atomic candidate actions $\{a_t^{(k)}\}_{k=1}^{N_t}$.
2. **One-Step World Model Prediction ($\hat{P}$)**: Conditioned on $(g, o_t, a_t^{(k)})$ and retrieved world-model memory $M_t^{\text{world}}$, a frozen language world model predicts the immediate next observation $\hat{o}_{t+1}^{(k)}$.
3. **Task-Progress & Risk Cost Scoring ($C_\psi$) + Gibbs Weighting**: An evaluator assigns each imagined transition $\hat{\tau}_t^{(k)} = (g, h_t, o_t, a_t^{(k)}, \hat{o}_{t+1}^{(k)})$ a cost $C_t^{(k)} \in [0, 100]$ based on expected progress, information value, and evidence consistency. Minimizing expected predictive cost plus a KL penalty from the uniform distribution $D_{\text{KL}}(\mathbf{w} \| \mathbf{u}_t)$ yields the exact MPPI Gibbs weights (Proposition 1):
   $$w_t^{(k)\star} = \frac{\exp(-C_t^{(k)} / \lambda)}{\sum_{j=1}^{N_t} \exp(-C_t^{(j)} / \lambda)}$$
   with default temperature $\lambda = 10$.
4. **Final Controller ($\pi_{\text{final}}$)**: Receiving the candidates, their predicted outcomes and Gibbs weights $\mathcal{E}_t = \{(\hat{o}_{t+1}^{(k)}, w_t^{(k)\star})\}$, and retrieved final-controller memory $M_t^{\text{final}}$, the controller selects a candidate or synthesizes a refined atomic action $a_t$ and executes only $a_t$ in the environment. Empirically (Figure 2), the controller selects a **Rank-1 (highest-weight) candidate in 77.8%–83.8%** of steps, a **Rank-2 candidate in 10.4%–12.2%**, and synthesizes an action **outside the proposal set in 1.6%–6.0%** of steps.

### 2. Theoretical Motivation for Dual-Branch Memory (Proposition 2)

If predictive costs deviate from true reference costs $\bar{C}_t$ by $\max_k |C_t^{(k)} - \bar{C}_t^{(k)}| \le \epsilon$, the per-step regret of the executed action $a_t$ relative to any comparator action $a^\circ$ (including actions outside the candidate set) decomposes into four terms:

$$\mathbb{E}_{a_t \sim \pi_{\text{final}}}\big[\bar{C}_t(a_t)\big] - \bar{C}_t(a^\circ) \le \underbrace{\delta_t^{\text{sel}}}_{\text{selection gap}} + \underbrace{\Delta_t^{\text{cov}}}_{\text{coverage gap}} + \underbrace{2\epsilon}_{\text{world-model cost error}} + \underbrace{\lambda \log N_t}_{\text{temperature}}$$

Each memory branch targets a distinct error term in this bound using token-set Jaccard similarity retrieval with frozen model weights:

- **Planner Memory Branch ($M_t^{\text{cand}}, M_t^{\text{final}}$)**: After each real environment transition, an extractor labels the step `SUCCESS`, `FAILURE`, or `IGNORE`. For `SUCCESS` and `FAILURE`, it writes separate distilled summaries into candidate-generation banks ($\mathcal{W}_{\text{cand}, y}$, targeting the **coverage gap** $\Delta_t^{\text{cov}}$) and final-controller banks ($\mathcal{W}_{\text{final}, y}$, targeting the **selection gap** $\delta_t^{\text{sel}}$). Each bank stores the most recent $C = 24$ records and retrieves the top $R = 4$ matches by Jaccard similarity to $\mathcal{T}(g) \cup \mathcal{T}(o_t)$.
- **World-Model Memory Branch ($M_t^{\text{world}}$)**: Following `WorldEvolver`, an **episodic bank** stores up to `100` observed transitions $(o_t, a_t, o_{t+1})$ and retrieves the top `5` per candidate action $a_t^{(k)}$, while a **semantic bank** extracts at most `1` environment rule per prediction–observation mismatch (storing up to `128` rules and retrieving up to `8` recent rules) to shrink the **cost error** $\epsilon$.

---

## Key Empirical Results

### 1. Main Benchmark Comparison Across 3 Backbones (Table 1)

| Backbone | Method | ALFWorld `SR@1` (%) | ALFWorld `SR@5` (%) | ScienceWorld `SR@1` (%) | ScienceWorld `SR@5` (%) |
|:---|:---|:---:|:---:|:---:|:---:|
| **`Gemma-4-26B-A4B`** | ReAct | 20.1 | 24.6 | 31.1 | 36.7 |
| | ITP-I (Imagine-then-Plan) | 32.8 | 54.5 | 36.7 | 50.0 |
| | WorldEvolver | 16.4 | 20.9 | 32.2 | 43.3 |
| | **Ours (MPPI + Dual Memory)** | **65.7** | **84.3** | **46.7** | **60.0** |
| **`Qwen3.5-9B`** | ReAct | 14.9 | 24.6 | **34.4** | **52.2** |
| | ITP-I | 6.7 | 12.7 | 27.8 | 46.7 |
| | WorldEvolver | 24.6 | 37.3 | 24.4 | 42.2 |
| | **Ours (MPPI + Dual Memory)** | **28.4** | **54.5** | 32.2 | 50.0 |
| **`GPT-5.4-mini`** | ReAct | 38.8 | 48.5 | 52.2 | 62.2 |
| | ITP-I | 50.0 | 81.3 | 51.1 | **70.0** |
| | WorldEvolver | 24.6 | 30.6 | 45.6 | 56.7 |
| | **Ours (MPPI + Dual Memory)** | **64.9** | **92.5** | **56.7** | 66.7 |

### 2. Ablation Studies (`Gemma-4-26B-A4B`, Tables 2–6)

1. **Complementary vs. Asymmetric Memory Branches (Table 4)**:
   - **No Memory (`× / ×`)**: ALFWorld `56.7 / 80.6`, ScienceWorld `38.9 / 57.8`, Average **`47.8 / 69.2`**.
   - **Planner Memory Only (`✓ / ×`)**: Helps ScienceWorld (`44.4 / 60.0`) but *hurts* ALFWorld (`49.3 / 73.9`), Average **`46.9 / 67.0`**.
   - **World-Model Memory Only (`× / ✓`)**: Strongly boosts ALFWorld (`68.7 / 88.8`) but *hurts* ScienceWorld (`36.7 / 54.4`), Average **`52.7 / 71.6`**.
   - **Both Branches Enabled (`✓ / ✓`)**: Achieves the highest cross-benchmark average (**`56.2% SR@1 / 72.2% SR@5`**; ALFWorld `65.7 / 84.3`, ScienceWorld `46.7 / 60.0`), showing that coupling planner and world-model memory prevents single-branch degradation when switching environments.
2. **Candidate Count $K$ (Table 2)**: Scaling $K \in \{1, 2, 4, 8, 16\}$ shows $K = 8$ achieves the peak average `SR@1` (**56.2%** vs. `51.9%` at $K=1$ and `53.2%` at $K=16$). Raising $K$ to `16` improves ScienceWorld `SR@5` (`60.0% → 68.9%`) but slightly degrades `SR@1` (`46.7% → 42.2%` on ScienceWorld, `65.7% → 64.2%` on ALFWorld).
3. **Temperature $\lambda$ and Memory Budget $(C, R)$ (Tables 3 & 5)**: Performance is stable between $\lambda = 1$ (`57.3 / 71.8` avg) and $\lambda = 10$ (`56.2 / 72.2` avg), whereas overly flat weights at $\lambda = 50$ drop ALFWorld `SR@1` from `65.7%` to `53.7%`. Increasing planner memory capacity $C$ from `4 → 12 → 24` at $R = 4$ lifts ScienceWorld `SR@1` from `36.7% → 44.4% → 46.7%`, while over-expanding to $C = 36$ or $R = 8$ degrades `SR@1` (`42.2%` on ScienceWorld at $C=36$; `56.7%` on ALFWorld at $R=8$) due to stale/noisy memory retrieval.
4. **Latency Overhead (Table 6, 2× NVIDIA A40 GPUs)**: Imagining and scoring $K = 8$ candidates requires **6.72 seconds/step**, compared to **0.51 s/step** for `ReAct`, **1.33 s/step** for `WorldEvolver`, and **1.94 s/step** for `ITP-I`, trading a `3.5×–13.2×` per-step latency increase for a `2×–3.2×` jump in single-trial task completion (`65.7%` vs. `20.1%–32.8%`).

---

## Why Not a Skill?

This paper presents a test-time control architecture for interactive text games (ALFWorld/ScienceWorld) whose core operational insights—gating world-model lookahead by forecast reliability and bounding experience memory retrieval to avoid stale context—are already represented in [`world-model-trust-gating`](../skills/world-model-trust-gating/SKILL.md) and [`knowledge-compounding-loop`](../skills/knowledge-compounding-loop/SKILL.md). The brief captures the MPPI regret decomposition (Proposition 2) and the empirical finding that single-branch memory (planner-only or world-model-only) can regress performance on one environment unless paired with the complementary branch.

---

## Related Artifacts

- **Rules**:
  - [`recursive-improvement.md`](../rules/recursive-improvement.md) — Experience memory management and world-model lookahead bounds.
- **Skills**:
  - [`world-model-trust-gating`](../skills/world-model-trust-gating/SKILL.md) — Gating planner reliance on world-model rollouts (`arXiv:2609.26293`).
  - [`knowledge-compounding-loop`](../skills/knowledge-compounding-loop/SKILL.md) — Consolidating execution traces into bounded experience memory.
- **Research Briefs**:
  - [`world-model-science-metastable-dynamics.md`](world-model-science-metastable-dynamics.md) — Error avalanches and belief dynamics in long-horizon world-model agents.
