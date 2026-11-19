# MCTS Is Counting the Wrong Thing: Learning Exploration Counts for LLM Reasoning (`LPC-MCTS`)

> **Source**: [arXiv:2611.22301](https://arxiv.org/abs/2611.22301) — Xuan Zhang, Zhijian Zhou, Zicheng Hu, Yan Feng, Hongyan Hao, Yuan Qi, Chao Qu (Fudan University, Shanghai Innovation Institute, Meituan, Shanghai Academy of AI for Science, November 2026)
> **Praxis Source ID**: `src:2611-22301v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

`LPC-MCTS` requires **white-box access to internal LLM hidden states** $\mathbf{h}_{v,t} \in \mathbb{R}^H$ inside a custom `SGLang` inference/rollout engine alongside online training of a linear Coin-Flipping Network (`CFN`) Rademacher regression head $f_\phi(\mathbf{h}) = \mathbf{W}_\phi^\top \operatorname{sg}(\mathbf{h})$ ($\mathbf{W}_\phi \in \mathbb{R}^{H \times 20}$) coupled with `8-GPU` `verl` `DAPO`/PPO reinforcement learning (`50–100` GPU-node hours). It cannot be executed over black-box LLM APIs or pure prompt/tool harnesses (for black-box cross-branch MCTS evidence pooling via hyperedges, use [`hypergraph-augmented-mcts`](../skills/hypergraph-augmented-mcts/SKILL.md)). We document `LPC-MCTS`'s regret theory, white-box pseudo-count mechanics, and branching-width boundary conditions here and distill its decision criteria into [`recursive-improvement.md`](../rules/recursive-improvement.md).

---

## Core Mechanism: Decoupling Reasoning Novelty from Surface Strings

Standard Upper Confidence Bound for Trees (`UCT`) assigns an independent visit counter $N(v_a)$ to every distinct token sequence $a$. In LLM reasoning, a single flawed or valid tactical approach (e.g., substituting $x = 0$ vs. setting the variable to zero) spawns $m$ surface-distinct paraphrases that each initialize at $N(v_a) = 0$, inflating the exploration bonus and forcing MCTS to re-verify equivalent dead ends:

1. **Regret Amplification Under Paraphrase Multiplicity (`Theorems 1 & 2`)**:
   - In a depth-$D$ tree where each suboptimal reasoning class $c$ along the optimal path splits into $m_{v,c} = m$ surface formulations with gap $\Delta_{v,c}$, standard independent-count UCT incurs asymptotic cumulative regret $\liminf_{T \to \infty} R_{\mathrm{ind}}(T)/\log T \ge \sum 2 m_{v,c}/\Delta_{v,c}$, whereas sharing exploration counts across equivalent formulations **while keeping empirical $Q$-values separate** achieves $\limsup_{T \to \infty} R_{\mathrm{share}}(T)/\log T \le \sum 2/\Delta_{v,c}$—reducing asymptotic regret by a factor of **$m\times$** ($R_{\mathrm{ind}}(T)/R_{\mathrm{share}}(T) \to m$). Merging $Q$-values across an imperfect similarity representation risks permanent bias if one good phrasing is grouped with weaker phrasings; sharing *only* counts strictly accelerates exploration decay without biasing node value estimates.
2. **Online Linear Coin-Flipping Network (`CFN`) & Selective High-Uncertainty Pooling (`§4.1–4.2`)**:
   - Each visited reasoning token receives a fresh Rademacher target $\mathbf{z}_i \in \{-1, +1\}^{20}$ ($d = 20$); a linear head $f_\phi(\mathbf{h}) = \mathbf{W}_\phi^\top \operatorname{sg}(\mathbf{h})$ (`LR = 1e-4`, updated every `4` MCTS iterations; prompt, padding, and tool-response tokens masked out) minimizes MSE against $\mathbf{z}_i$, so mean squared prediction $\frac{1}{d}\|f_\phi(\mathbf{h})\|_2^2$ tracks inverse effective feature-space visit count $\approx 1/n(\mathbf{h})$.
   - Tree expansion branches at high-entropy decision forks (`16`-token sliding window entropy $\overline{H}_{\mathrm{win}} > 2.0\,\overline{H}_{\mathrm{ctx}}$). To prevent boilerplate algebraic/prose tokens from dominating node representations, `LPC-MCTS` averages token uncertainty $u_\phi(\mathbf{h}_{v,t})$ **only over the top `30%` ($p = 30$) highest-uncertainty tokens belonging to contiguous spans of length $\ge 2$**, yielding node pseudo-count $C_\phi(v) = 1/(U_\phi(v) + \epsilon)$.
3. **Normalized UCB Selection & Novelty-Prioritized RL Batching (`Eqs. 5–8`)**:
   - Child selection replaces integer $N(v), N(v_a)$ with learned pseudo-counts and active-child sum $M_\phi(v) = \sum_{a' \in \mathcal{A}_{\mathrm{active}}(v)} C_\phi(v_{a'})$ ($c_{\mathrm{count}} = 2.0$):
     $$a^\star = \arg\max_{a \in \mathcal{A}(v)} \left[\hat{Q}(v_a) + c_{\mathrm{count}}\sqrt{\frac{\log(1 + M_\phi(v))}{1 + C_\phi(v_a)}}\right]$$
   - For RL (`DAPO` policy loss without KL penalty, `clip = [0.2, 0.28]`), `LPC-MCTS` runs $T = 24$ training search iterations ($T = 128$ at evaluation), extracts up to $K_{\max}$ root-to-leaf trajectories (`12` math, `8` search), sorts by ascending trajectory mean pseudo-count $\overline{C}_\phi(\tau)$, and trains on the **$B$ least-redundant trajectories** (`B = 8` math, `B = 5` search).

---

## Key Empirical Results

### 1. Tool-Integrated Mathematical Reasoning (`5` Benchmarks, `mean@16`, `Table 1`)

Evaluated across `AIME24`, `AIME25`, `AIME26`, `HMMT25`, and `BRUMO25` (`temp = 1.0`, `top_p = 0.7`, max `5` Python interpreter calls/rollout; trained `150` RL steps on `4k` `DAPO-Math-17k` problems):

| Backbone & Training + Inference Method | `AIME24` | `AIME25` | `AIME26` | `HMMT25` | `BRUMO25` | **Avg (`mean@16`)** |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **`Qwen2.5-7B`**: `SFT + Direct` / `SFT + MCTS` | `12.71` / `14.17` | `6.88` / `10.83` | `5.83` / `8.54` | `5.63` / `5.21` | `18.96` / `23.33` | `10.00` / `12.42` |
| **`Qwen2.5-7B`**: `DAPO + Direct` / `DAPO + MCTS` | `32.50` / `32.29` | `26.46` / `23.33` | `25.00` / `24.17` | `15.83` / `16.46` | `39.38` / `41.46` | `27.83` / `27.54` |
| **`Qwen2.5-7B`**: `MCTS + Direct` / `MCTS + MCTS` | `32.29` / `33.75` | `24.17` / `22.92` | `24.38` / `25.00` | `14.58` / `17.08` | `40.21` / `40.42` | `27.13` / `27.83` |
| **`Qwen2.5-7B`**: `LPC-MCTS + Direct` / `LPC-MCTS + MCTS` | `34.17` / `33.96` | `23.33` / `26.25` | `25.00` / `24.38` | `19.17` / `18.96` | `40.42` / `41.46` | `28.42` / `29.00` |
| **`Qwen2.5-7B`**: **`LPC-MCTS + LPC-MCTS` (Ours)** | **`37.08`** | **`30.63`** | **`27.92`** | **`23.33`** | **`45.00`** | **`32.79`** |
| **`Qwen3-4B`**: `SFT + Direct` / `SFT + MCTS` | `41.88` / `37.71` | `29.79` / `26.04` | `27.92` / `25.21` | `18.13` / `16.04` | `34.58` / `31.88` | `30.46` / `27.38` |
| **`Qwen3-4B`**: `DAPO + Direct` / `DAPO + MCTS` | `72.71` / `72.08` | `54.79` / `55.63` | `64.58` / `63.96` | `44.58` / `45.21` | `61.46` / `61.46` | `59.62` / `59.67` |
| **`Qwen3-4B`**: `MCTS + Direct` / `MCTS + MCTS` | `74.17` / `75.21` | `56.67` / `57.29` | `66.88` / `67.92` | `46.04` / `47.29` | `62.29` / `62.92` | `61.21` / `62.13` |
| **`Qwen3-4B`**: `LPC-MCTS + Direct` / `LPC-MCTS + MCTS` | `76.46` / `76.25` | `59.38` / `61.04` | `68.54` / `70.21` | `47.50` / `47.71` | `63.75` / `63.75` | `63.13` / `63.79` |
| **`Qwen3-4B`**: **`LPC-MCTS + LPC-MCTS` (Ours)** | **`78.13`** | **`63.54`** | **`72.92`** | **`51.88`** | **`66.04`** | **`66.50`** |

- **Compounding train + inference synergy & uncalibrated SFT pitfall**: `LPC-MCTS` improves end-to-end accuracy by **`+4.96 pp` (`27.83% -> 32.79%`) on `Qwen2.5-7B`** and **`+4.37 pp` (`62.13% -> 66.50%`) on `Qwen3-4B`** over `MCTS + MCTS` (`+5.25 pp` and `+6.83 pp` over `DAPO + MCTS`). Holding the trained `LPC-MCTS` policy fixed, swapping classical visit-count MCTS for pseudo-count MCTS at inference alone adds **`+3.79 pp` (`29.00% -> 32.79%`)** and **`+2.71 pp` (`63.79% -> 66.50%`)**. Notably, wrapping vanilla MCTS around un-RL'd `Qwen3-4B SFT` **degraded accuracy by `-3.08 pp` (`30.46% -> 27.38%`)** (and `-0.24 pp` on `Llama-3.2-3B-Instruct` search, `38.09% -> 37.85%`), showing tree search requires value/policy alignment or calibrated exploration counts.

### 2. Multi-Hop Search QA & the Branching-Width Boundary (`Table 2`, `§5.2`)

Across `7` retrieval benchmarks (`NQ`, `TriviaQA`, `PopQA`, `HotpotQA`, `2Wiki`, `MuSiQue`, `Bamboogle`, `mean@5` against `21,015,324` `wiki-18` passages via `e5-base-v2` top-3):
- `LPC-MCTS + LPC-MCTS` reaches **`46.83%`** on `Qwen2.5-7B-Instruct` (`+2.26 pp` over `MCTS + MCTS` `44.57%`; `+0.58 pp` pure inference gain over `46.25%`) and **`45.18%`** on `Llama-3.2-3B-Instruct` (`+1.71 pp` over `43.47%`; `+0.45 pp` pure inference over `44.73%`).
- **Diagnostic (`256` trees/task)**: Search trees averaged only **`1.82` effective first-level branches** vs. **`4.05` in math** because early retrieval queries are highly stereotyped—explaining why cross-branch count sharing yields `+2.71` to `+3.79 pp` inference gains on wide mathematical trees vs. `+0.45` to `+0.58 pp` on narrow search trees.

### 3. Mechanism Verification, Ablations, and `22%–42%` Token Savings (`Tables 3–12`)

- **Cross-sibling semantic generalization (`§5.3`)**: Performing `16` CFN updates on one branch increased pseudo-counts of held-out *same-reasoning-pattern* siblings by **`+5.5%` (95% CI `[+3.5%, +7.4%]`, `400` questions)** while *decreasing* distinct-pattern siblings by **`-3.2%` (`[-5.0%, -1.3%]`, `126` questions)**; `CFN` distance correlated with semantic embeddings (`Spearman ρ = 0.248–0.358`, nearest-neighbor agreement `24.1%–29.2%` vs. `14.3%` random).
- **Component ablations (`Tables 3, 7–10`)**: Removing pseudo-count UCB cost `-2.16 pp` (`Qwen3-4B`) and `-4.33 pp` (`Qwen2.5-7B`); removing low-pseudo-count trajectory selection cost `-2.71 pp` and `-1.41 pp`; replacing selective top-`30%` span aggregation with uniform token pooling cost `-2.33 pp` and `-4.29 pp`; replacing linear `CFN` (`66.50%` / `32.79%`) with `RND` (`65.25%` / `31.29%`) or deeper `2-layer MLP CFN` (`64.63%` / `30.88%`) degraded accuracy because nonlinear random projections distort pretrained hidden-state cosine geometry.
- **Inference token reduction (`Tables 11–12`, `60` `AIME24/25` problems)**: Despite computing hidden-state prefill + `CFN` (`6.73%` and `5.49%` wall-time share; `0.23%` and `0.18%` for the linear head itself), `LPC-MCTS` **cut total generated tokens by `22.05%` on `Qwen3-4B` (`80.958M -> 63.106M`, `16.72 -> 15.98 s/candidate`) and `42.00%` on `Qwen2.5-7B` (`44.007M -> 25.525M`, `12.05 -> 12.83 s/candidate`)** by terminating redundant sibling rollouts early (`<= 20%` RL training overhead).

---

## Related Artifacts

- **Rules**: [`recursive-improvement.md`](../rules/recursive-improvement.md) (`"DO: Share MCTS exploration counts across semantically equivalent reasoning branches while keeping empirical branch values separate, and audit tree branching width first"`)
- **Skills**: [`hypergraph-augmented-mcts`](../skills/hypergraph-augmented-mcts/SKILL.md) (`HyperMCTS`, `arXiv:2609.33920`), [`fast-tree-search-self-improvement`](../skills/fast-tree-search-self-improvement/SKILL.md) (`SIFT`, `arXiv:2609.19526`)
