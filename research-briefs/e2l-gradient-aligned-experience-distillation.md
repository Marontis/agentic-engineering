# E2L: Gradient-Aligned Experience Evolution for On-Policy Self-Distillation

> **Source**: [arXiv:2611.32390](https://arxiv.org/abs/2611.32390) — *Evolve to Learn: Gradient-aligned experience evolution for model self-improvement* (Haoyuan Li, Gangyi Zhang, Dong Wang, Yang Liu, Daoxuan Liu, Jiancan Wu, Shiu-hong Kao, Wu Liu, Yicong Li, Yongdong Zhang; USTC, Alibaba Group, National University of Singapore)
> **Praxis Source ID**: `src:2611-32390v1`
> **License**: CC-BY-4.0

## Why Not a Skill?

`E2L` requires white-box backpropagation access to the top Transformer layers (`layers 32–35` of `Qwen3-8B` inside `veRL`) to compute per-candidate reverse-KL distillation gradients $g_c = \nabla_\phi \mathcal{L}_{\mathrm{OPSD}}(\theta; c)$ over top-`256` teacher logits and cosine-align them against supervised reference gradients $g_E = \nabla_\phi \mathcal{L}_{\mathrm{ref}}(\theta)$, evaluated on a single student checkpoint (`Qwen3-8B`). Following `AGENTS.md` (white-box training pipelines without model/framework-portable runtime execution belong in Research Briefs + Rules), its empirical findings are captured here and distilled into `output/rules/recursive-improvement.md`.

## Core Problem: Inference-Time Prompt Accuracy Does Not Predict Weight Distillability

Context distillation and on-policy self-distillation (`OPSD`) internalize natural-language experiences $c$ by training an unconditioned student $\pi_\theta(\cdot \mid x)$ via token-level reverse KL on its own rollouts $y \sim \pi_\theta(\cdot \mid x)$ toward a frozen context-conditioned teacher $\pi_{\theta_0}(\cdot \mid x, c)$, then discarding $c$ at test time. Prior experience-evolution methods (`GEPA`, `OEL`) select experiences by **inference-time context-conditioned accuracy**.

`E2L` demonstrates that inference-time followability and parameter-space distillability are decoupled:
- **Motivating divergence (`§1`, `Fig. 1a–b`)**: Two `GLM-5.2`-evolved experiences with identical pre-distillation context-conditioned accuracy on `AIME25` (**`20.83%`**) diverge after `20` `OPSD` steps to **`21.11%` vs. `18.06%`** unconditioned accuracy (*note*: the paper reports a **`3.06` percentage-point gap** from unrounded `76/360 = 21.111%` vs. `65/360 = 18.056%` over `30` problems $\times$ `12` samples, whereas subtracting the displayed rounded percentages gives `3.05`).
- **`33`-experience correlation audit (`§2.2`, `Fig. 1c–d`, `Appendix B.1–B.2`)**: Across `33` multi-turn evolved candidates (`16` `DeepSeek-V4-Pro` + `17` `GLM-5.2` on `AIME25`), pre-distillation context-conditioned accuracy has **zero correlation** with `20`-step post-distillation unconditioned accuracy (**Spearman $\rho = -0.059, p = 0.746$**). Across `13` canonical predictors—spanning prompt-gain delta, forward/reverse KL gap, teacher–student entropy delta, context flip score, regression rate, and gold-solution log-prob gain—**only reference-gradient alignment** achieves statistically significant positive correlation, peaking at **$\rho = 0.484$** (`Fig. 1c` caption; rounded to **$\rho = 0.48, p = 0.006$** in `§1` prose) for **error-reference gradient alignment** $A_E(c) = \cos(g_c, g_E)$ computed on the **last `4` Transformer layers (`layers 32–35`)** over held-out reference items where the unconditioned base model failed ($\mathcal{D}_{\mathrm{err}}$, averaging example gradients *before* taking cosine similarity).

## Methodology: Dual-Channel Evolution + Alignment-Guided `OPSD`

1. **Dual-Channel Experience Evolution (`§3.2`, `Algorithm 1`)**:
   - Starting from a minimal seed prompt under budget $B = 2,000$ student evaluations (`Qwen3-8B` acts as solver, proposer, and mutator), each candidate child experience $c'$ is accepted into pool $\mathcal{P}$ if it satisfies **either** multi-example `ParetoAccept` (non-dominated across validation problems, preserving structural exploration) **or** `Top-N` gradient alignment ($N = 3$, adding `0.3` parent-sampling bonus weight to top-aligned candidates).
2. **Alignment-Guided Selection & Unlabeled `OPSD` (`§3.3`)**:
   - Select $c^\star = \arg\max_{c \in \mathcal{P}} A_E(c)$ (or top-3 concatenation in fixed-pool studies) and run `50` `OPSD` steps (`LR = 1e-6`, batch `32`, `top-256` teacher logits without probability renormalization; `20` steps / batch `64` on `JailbreakBench`) on unlabeled student rollouts, evaluating the resulting checkpoint **without** $c^\star$ in non-thinking mode (`temp = 0.7, top_p = 0.8, top_k = 20`).

## Key Quantitative Findings

### 1. Main `3`-Seed Self-Distillation Results (`Qwen3-8B`, `Table 1`)

Evaluated across `3` random seeds (`1001, 1002, 1003`; `16` samples/problem on `AIME25` and `AIME26`, `1` sample/example on `HotPotQA` EM and `JailbreakBench` balanced safety–benign harmonic mean):

| Method | `AIME25` | `AIME26` | `HotPotQA` (EM) | `JailbreakBench` (Harmonic) |
|:-------|:--------:|:--------:|:---------------:|:---------------------------:|
| `Base` (`Qwen3-8B`) | `0.1972` | `0.1556` | `0.5208` | `0.6236` |
| `OPCD` (fixed context distillation) | `0.2046` | `0.1639` | `0.5211` | `0.6358` |
| `OPSD` (answer-conditioned self-distillation) | `0.1815` | `0.1565` | `0.4914` | `0.4629` |
| `OEL` (accuracy-evolved experience + OPSD) | `0.2065` | `0.1685` | `0.5367` | `0.5623` |
| **`E2L-Alignment`** | **`0.2203`** | **`0.1824`** | **`0.5614`** | **`0.7205`** |

- Answer-conditioned `OPSD` degrades below `Base` on `3/4` benchmarks (`JailbreakBench` drops `-16.07 pp` to `0.4629`), and accuracy-evolved `OEL` also loses `-6.13 pp` on `JailbreakBench` (`0.5623`), whereas `E2L-Alignment` leads every benchmark (`+2.31 pp` `AIME25`, `+2.68 pp` `AIME26`, `+4.06 pp` `HotPotQA`, **`+9.69 pp`** `JailbreakBench` over `Base`).

### 2. Dual-Channel Search, Same-Pool Selection, & Direct Supervision Ablations (`Tables 2–5`, `Fig. 4`)

- **Why pure alignment search fails (`Table 3`, `B = 2,000` on `AIME25`)**:
  - `Alignment-only` (`Top-3` gate without Pareto): Collapses diversity to **`6` experiences**, max depth **`2`**, **`4%`** gate acceptance, `0.7462` max alignment, and **`0.1944`** post-distillation `AIME25` (below `Base`).
  - `Pareto-only` (`GEPA`): Reaches `23` experiences, depth `5`, `20%` acceptance, `0.8557` max alignment, and **`0.2194`** `AIME25`.
  - **`E2L` (`Pareto` $\lor$ `Top-3` Alignment)**: Reaches **`27` experiences, depth `6`, `31%` acceptance, `0.8809` max alignment, and `0.2305` `AIME25`**.
- **Selecting from the *same* `E2L` pool by `Alignment` vs. `Acc Best Selection` (`Fig. 4`)**: Adds **`+2.78 pp`** (`AIME25`), **`+2.39 pp`** (`LiveBench Math`), **`+1.50 pp`** (`HotPotQA`), and **`+4.88 pp`** (`JailbreakBench`). (*Manuscript note*: `§4.1` and `Appendix A.2` state `1` sampled response per `LiveBench Math` example, whereas `Appendix A.5` line 2334 mentions `"two response per LiveBench Math example"` for `Table 2`'s `20`-step fixed-pool evaluation, where `Alignment-Top3` beat `Accuracy-Top3` on `AIME26` [`0.1667` vs. `0.1574`], `LiveBench Math` [`0.4802` vs. `0.4742`], and `HotPotQA` [`0.5381` vs. `0.5228`], trailing only on `20`-step `AIME25` [`0.2194` vs. `0.2259`].)
- **Beats direct supervision on the same reference set (`Table 4`)**: Using the exact same small reference set directly for `SFT` (`0.2055 / 0.1555 / 0.4702` on `AIME25 / AIME26 / LiveBench Math`) barely moves `Base` (`0.2055 / 0.1527 / 0.4762`), and ground-truth `Gt-OPSD` degrades all three (`0.1638 / 0.1388 / 0.4642`), whereas `E2L-Alignment` reaches **`0.2305 / 0.1777 / 0.5000`**.
- **Objective portability (`Table 5`)**: Replacing reverse KL with `JSD`, pixel/token-weighted `PW-OPSD`, or `Rule Reward` RL, `E2L-Alignment` beats `E2L-Accuracy` in **`8 of 9`** objective $\times$ benchmark cells.

## Limitations & Failure Modes

- **White-box student gradient requirement**: Computing $A_E(c)$ requires top-layer backward passes on the student model and labeled reference failures $\mathcal{D}_{\mathrm{err}}$, making it inapplicable to closed-weight API students.
- **Single-scale validation**: All distillation experiments use `Qwen3-8B` over `20–50` short horizon steps; scaling behavior on `30B+` or MoE students remains unmeasured.

## Relevance to Praxis

- **Rules**: [`recursive-improvement.md`](../rules/recursive-improvement.md) — Establishes why experience/prompt selection for `OPSD` weight internalization cannot use inference-time prompt accuracy ($\rho = -0.059$), complementing [`harness-zero-distillation`](harness-zero-distillation.md) (`arXiv:2609.24974`) and [`basersi-training-free-harness-internalization`](basersi-training-free-harness-internalization.md) (`arXiv:2611.24578`).
- **Skills**: [`markovian-refinement-test-time-scaling`](../skills/markovian-refinement-test-time-scaling/SKILL.md) — Label-free adjacent-pair `OPSD` at test time when reference labels $\mathcal{D}_{\mathrm{err}}$ are absent.
- **Specs**: [`self-improving-agent.spec.md`](../specs/self-improving-agent.spec.md) — Experience-to-weight distillation selection criteria.
