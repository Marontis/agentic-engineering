# JHiMA-WebRL: Joint Hierarchical Multi-Agent RL for Long-Horizon Web Tasks

> **Source**: [arXiv:2611.05263](https://arxiv.org/abs/2611.05263) | `src:2611-05263v1`
> **Authors**: Shanka Subhra Mondal, Jiayun Wang (Center for Advanced AI, Accenture)
> **Category**: `cs.AI` (Hierarchical Multi-Agent Reinforcement Learning / Web & GUI Agents)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Executive Summary

Long-horizon visual web tasks require agents to simultaneously plan multi-stage subgoals and execute fine-grained GUI grounding actions over 10–15 steps under sparse terminal outcomes. **JHiMA-WebRL** introduces a joint hierarchical multi-agent reinforcement learning architecture pairing a visual **Decomposer** (`Qwen2.5-VL-7B`) with a visual **Actor** (`Qwen2.5-VL-7B`, total system `JHiMA-WebRL-14B`). After cold-start supervised fine-tuning on teacher-generated subtask decompositions (`GPT-5.2-Codex` over `ScaleCUA` trajectories), both agents are co-adapted online on **647** `WebArena` tasks using **Joint Hierarchical Multi-Agent Group Relative Policy Optimization (M-GRPO)** with LoRA ($r=32, \alpha=64$). Crucially, freezing the SFT decomposer while RL-training only the actor *degrades* accuracy below the SFT baseline (**33.4%** vs **35.1%**) due to hierarchical distribution shift, whereas joint co-adaptation lifts `WebArena-Lite-v2` (154 visual tasks) success to **37.2%** — outperforming a controlled single-agent `ScaleCUA-32B RL` baseline (**24.0%**) by **+13.2 percentage points** with fewer parameters.

---

## Key Findings

1. **Co-Adapting the Decomposer and Actor Prevents Hierarchical Distribution Shift**:
   - In hierarchical agent architectures, training the low-level actor via RL while keeping a supervised high-level planner/decomposer frozen (`w/o decomposer RL`) drops `WebArena-Lite-v2` task success from **35.1%** (SFT-only) to **33.4%** (−1.7 pp below SFT, and −3.8 pp below full `JHiMA-WebRL-14B` at **37.2%**).
   - As the actor's execution policy shifts during RL, static decompositions become misaligned with how the actor actually navigates pages. Co-adapting the decomposer using mean actor group rewards ($r^D_i = \frac{1}{M}\sum_{j=1}^M r_{i,j}$ over $K=3$ decompositions $\times$ $M=7$ actor trajectories = 21 rollouts/task) aligns subgoals with the evolving actor and outperforms actor-only RL without a decomposer at matched rollout budgets (**37.2%** vs **34.9%** at 21 rollouts and **35.2%** at 7 rollouts).

2. **Compact 14B Hierarchical Co-Training Outperforms 32B Single-Agent RL and 72B DPO Models**:
   - Evaluated on **154** visual tasks in `WebArena-Lite-v2` across 5 domains (15-step limit, averaged over **4** evaluation runs at temperature 0.0), `JHiMA-WebRL-14B` achieves **37.2%** average success, beating `ScaleCUA-32B RL` (**24.0%**, +13.2 pp) trained on the exact same 647 tasks, `ScaleCUA-32B SFT` (**24.0%**), `GUI-Libra-8B` (**26.6%**), `UI-TARS-72B-DPO` (**23.4%**), and `GPT-4o Planner + ScaleCUA-7B Grounder` (**28.6%**).
   - Gains are largest on long-horizon workflow domains: **60.5%** on `Reddit` (vs 21.0% for `ScaleCUA-32B RL`), **47.5%** on `GitLab` (vs 35.0%), **44.3%** on `ShoppingAdmin` (vs 25.7%), and **29.0%** on `Shopping` (vs 24.4%), while trailing only on `Map` (**12.5%** vs 17.3% for `GUI-Libra-8B`).

3. **Unnormalized Hierarchical Advantage Formulation Stabilizes Binary-Reward GUI RL**:
   - Following Dr. GRPO principles in a two-level hierarchy, `JHiMA-WebRL` removes both reward standard-deviation normalization (which explodes gradients when all rollouts in a group nearly pass or fail) and response-length normalization (which biases toward verbose failed trajectories), and sets KL penalties to zero ($\beta_A = \beta_D = 0$, clipping $\epsilon_A = \epsilon_D = 0.2$).
   - Each actor rollout is scored relative to the mean of its $M=7$ sibling rollouts conditioned on the *same* decomposition $s_i$ ($\hat{A}^A_{i,j,t} = r_{i,j} - \frac{1}{M}\sum_{j'=1}^M r_{i,j'}$), while each decomposer candidate $s_i$ is scored relative to the mean across all $K \times M = 21$ rollouts ($\hat{A}^D_{i,t} = r^D_i - \frac{1}{KM}\sum_{i'=1}^K \sum_{j'=1}^M r_{i',j'}$).

4. **Subgoal Completion Fraction Monotonically Predicts Terminal Task Success**:
   - Using an LLM judge (`GPT-5.2-Codex`) to verify step-by-step subgoal completion across evaluation trajectories shows that the fraction of completed subgoals strongly predicts terminal environment reward (**AUROC = 0.838**, monotonic rank correlation **Kendall's $\tau = 0.516$** vs **AUROC = 0.836**, **$\tau = 0.503$** for the SFT baseline), confirming that joint RL improves both subgoal executability and actor adherence.

---

## Quantitative Summary

### Table 1: SFT Dataset Statistics (`GPT-5.2-Codex` Teacher on `ScaleCUA`)

| Platform | Decomposer SFT Examples | Avg. Subtasks / Trajectory | Trajectories w/ Unnecessary Actions |
|:---|---:|---:|---:|
| **Windows** | 5,873 | 2.68 | 1.2% |
| **macOS** | 3,845 | 2.43 | 1.1% |
| **Linux** | 25,122 | 2.20 | 1.8% |
| **Android** | 17,245 | 2.84 | 1.6% |
| **Web** | 24,311 | 2.73 | 1.5% |
| **Total / Overall** | **76,396** | **2.56** | **1.6%** |

*(Note: Actor SFT was trained on **2,535,552** examples combining subtask-augmented multi-turn GUI trajectories and visual grounding data for 1 epoch at learning rate $10^{-5}$, global batch size 64, max context 30,720 tokens on 8× H100 80 GB GPUs. Online M-GRPO ran on **647** `WebArena` tasks for ~720 GPU-hours.)*

### Table 2: `WebArena-Lite-v2` Benchmark Comparison (154 Visual Tasks, 4-Run Mean %)

| Model / System | GitLab | Map | Reddit | Shopping | ShoppingAdmin | Average (%) |
|:---|---:|---:|---:|---:|---:|---:|
| `UI-TARS-1.5-7B` | 21.3 | 9.6 | 25.0 | 26.7 | 19.6 | 20.8 |
| `GPT-4o Planner + UI-TARS-1.5-7B Grounder` | 22.5 | 13.5 | 26.3 | 27.9 | 21.6 | 22.6 |
| `UI-TARS-72B-DPO` | 23.8 | 11.5 | 28.9 | 27.9 | 23.7 | 23.4 |
| `ScaleCUA-7B SFT` | 32.5 | 10.6 | 22.4 | 25.6 | 24.7 | 23.9 |
| `ScaleCUA-32B SFT` | 35.0 | 11.5 | 21.1 | 24.4 | 24.7 | 24.0 |
| `ScaleCUA-32B RL` (controlled 647-task baseline) | 35.0 | 10.6 | 21.0 | 24.4 | 25.7 | 24.0 |
| `GUI-Libra-8B` | 30.0 | **17.3** | 28.9 | 27.9 | 26.8 | 26.6 |
| `GPT-4o Planner + ScaleCUA-7B Grounder` | 35.0 | 13.5 | 31.6 | **31.4** | 28.9 | 28.6 |
| **`JHiMA-WebRL-14B` (Full Joint M-GRPO)** | **47.5** | 12.5 | **60.5** | 29.0 | **44.3** | **37.2** |

### Table 3: Ablation Study on `WebArena-Lite-v2`

| Ablation Variant | Sampling ($K \times M$) | Success Rate (%) | $\Delta$ vs. Full |
|:---|:---|---:|---:|
| **Full `JHiMA-WebRL-14B` (Decomposer RL + Actor RL)** | $3 \times 7 = 21$ | **37.2** | — |
| `w/o decomposer RL` (Frozen SFT Decomposer + RL Actor) | $3 \times 7 = 21$ | 33.4 | −3.8 pp |
| `w/o decomposer` (Actor-Only RL, matched 21 rollouts) | $1 \times 21 = 21$ | 34.9 | −2.3 pp |
| `w/o decomposer` (Actor-Only RL, standard 7 rollouts) | $1 \times 7 = 7$ | 35.2 | −2.0 pp |
| `w/o RL` (SFT Decomposer + SFT Actor) | — | 35.1 | −2.1 pp |

---

## Why Not a Skill?

`JHiMA-WebRL` is a multi-stage VLM post-training pipeline requiring 2.53M SFT examples, live Dockerized `WebArena` instances, and ~720 H100 GPU-hours of two-model LoRA GRPO training. It does not define a lightweight inference-time or prompt-level procedure that an agent can execute on demand across projects. However, its empirical ablation finding — that training a low-level actor with RL while holding a high-level SFT planner/decomposer frozen degrades performance below the SFT baseline (−1.7 pp) — provides an important architectural rule for hierarchical multi-agent RL and orchestration.

---

## Actionable Takeaways

1. **Never Freeze an SFT Planner When RL-Tuning Its Downstream Executor**: If you apply online RL to a low-level action model in a planner-executor hierarchy, either co-update the planner using group-averaged executor returns ($r^D_i = \frac{1}{M}\sum_j r_{i,j}$) or remove the planner during RL; a frozen SFT planner suffers distribution mismatch as the executor's policy evolves (**33.4%** vs **35.1%** SFT-only and **37.2%** joint RL).
2. **Use Nested Group Baselines Without Std or Length Normalization**: In hierarchical GRPO with binary task rewards, compute actor advantages relative to the $M$ rollouts sharing the same subgoal plan, compute planner advantages relative to all $K \times M$ rollouts for the task, and omit standard-deviation and token-length normalizations to prevent gradient spikes and verbosity bias.
3. **Monitor Subgoal Completion Fraction as an Online Progress Signal**: Because the fraction of completed subgoals correlates with terminal success at **AUROC = 0.838**, runtime supervisors can use subgoal completion stalls to trigger early replanning or rollback before exhausting the step budget.

---

## Related Artifacts

- [`rules/multi-agent-coordination.md`](../rules/multi-agent-coordination.md) — Topology selection and joint planner-controller optimization rules.
- [`rules/recursive-improvement.md`](../rules/recursive-improvement.md) — Joint co-optimization of coupled agent components.
