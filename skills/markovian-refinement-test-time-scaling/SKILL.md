---
name: markovian-refinement-test-time-scaling
description: >
  Scale label-free test-time compute and optional test-time LoRA consolidation
  by replacing independent majority-vote sampling with neutral full-solution
  Markovian sequential refinement and adjacent-pair self-distillation (TT-RSI).
source: arXiv:2611.30965
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Markovian Refinement Test-Time Scaling

Scale inference-time accuracy and unlabeled test-time adaptation without ground-truth labels or external verifiers by conditioning each sequential attempt solely on the latest visible full derivation under a neutral prompt (`In-Context RSI`), and optionally distilling adjacent `(initial, refined)` attempt pairs into LoRA weights (`In-Weight RSI`).

## When to Use

- Scaling test-time compute on reasoning-intensive problems (quantitative/mathematical reasoning, multi-step analytical queries, formal specification or SQL/code derivation without unit-test oracles) where external verifiers are unavailable at inference time.
- Replacing parallel majority voting (`Self-Consistency`) when independent sampling wastes tokens repeating identical flawed derivations (`68.6%` token overhead to reach the same accuracy).
- Adapting an open-weight model on an unlabeled test batch where majority-vote test-time reinforcement learning (`TTRL`) reinforces confident wrong majorities on hard instances.
- Do **not** use sequential refinement blindly on base or non-reasoning checkpoints before checking the empirical fix/break balance condition $f / (f + b) > \operatorname{acc}_1$ on a small calibration slice.

## Core Insight

Parallel `Self-Consistency` scales width without cross-attempt learning, and `TTRL` converts majority answers into pseudo-labels—causing systematic degradation whenever the initial majority on a hard problem is wrong. Conversely, multi-turn chat self-correction (`"find mistakes in your previous answer"`) bloats context with full reasoning transcripts and increases the **breaking rate** $b$ (corrupting already-correct answers).

`TT-RSI` (`arXiv:2611.30965`) resolves both bottlenecks through two mechanisms:
1. **Markovian Full-Solution Neutral Carryover (`In-Context RSI`)**: Strip hidden `<think>` traces and pass **only** the final visible step-by-step derivation and answer $a_k$ (`< 1,000` prompt tokens, constant across steps) with a **neutral** instruction to solve the problem independently. Under two-state Markov dynamics with fixing rate $f = P(\text{correct}_{k+1} \mid \text{wrong}_k)$ and breaking rate $b = P(\text{wrong}_{k+1} \mid \text{correct}_k)$, accuracy converges monotonically toward $p^* = f / (f + b)$ whenever $p^* > \operatorname{acc}_1$, while generation length shrinks by `~50%` after Attempt 1 (`11,488 -> 5,693` tokens on `Qwen3-4B` `AIME 2024`).
2. **Adjacent-Pair Self-Distillation (`In-Weight RSI`)**: When open-weight LoRA updates are permitted on unlabeled test batches, pair a single initial solution $a_1$ with a single Markovian refinement $a_2$ per problem (avoiding any majority vote) and minimize reverse KL (`OPSD`) from the unconditioned student (`x`) to the refinement-conditioned teacher (`x + a_1` and `x + a_2`), weighting token-level distillation by bounded total-variation shift so decisive correction tokens receive stronger weight.

## Step-by-Step Procedure

### Phase 1: Calibrate the Fix/Break Balance Point

1. **Sample two Markovian attempts on a small validation slice**:
   - Generate Attempt 1 ($y_1 = (z_1, a_1)$) from problem $x$ alone, where $z_1$ is the internal scratchpad (`<think>...</think>`) and $a_1$ is the clean visible derivation plus final answer.
   - Generate Attempt 2 ($y_2 = (z_2, a_2)$) conditioned on `(x, a_1)` using the neutral prompt template in Phase 2 (`z_1` stripped).
2. **Verify the Markovian improvement condition**:
   - Compute single-attempt baseline accuracy $\operatorname{acc}_1$, fixing rate $f$ (fraction of wrong $a_1$ fixed in $a_2$), and breaking rate $b$ (fraction of correct $a_1$ broken in $a_2$).
   - Proceed with sequential `In-Context RSI` only if the implied equilibrium $p^* = \frac{f}{f + b}$ exceeds $\operatorname{acc}_1$ by a meaningful margin (for example, `Qwen3-4B` on `AIME 2024` exhibits $f = 42.3\%, b = 5.4\% \implies p^* = 88.7\% > 72.92\%$). If $f / (f + b) \le \operatorname{acc}_1$, fall back to parallel sampling with an abstaining or tournament selector.

### Phase 2: Run Neutral Markovian `In-Context RSI` (Black-Box or Open-Weight)

1. **Generate the initial attempt ($k = 1$)**:
   - Prompt the model with problem $x$ (`temperature = 0.6`, `top_p = 0.95`) to obtain $y_1 = (z_1, a_1)$.
   - Strip $z_1$ and extract only the clean visible summary derivation and final answer $a_1$. Never carry $z_1$ or multi-attempt history $(a_1, \dots, a_{k-1})$ into subsequent prompts.
2. **Iterate Markovian neutral refinement ($k = 1, \dots, K - 1$)**:
   - Construct a fresh single-turn prompt containing only $x$ and $a_k$ with **neutral framing**:
     ```text
     Problem:
     {x}

     A previous attempt at solving this problem was:
     {a_k}

     Please solve the problem independently. Show your full derivation and state your final answer clearly. Do not assume the previous attempt is either correct or incorrect.
     ```
   - **Never pass only the bare final answer** (which collapses fixing rate $f$ from `42.3%` to `6.9%` due to blind answer anchoring), and **never use correction-directed wording** (`"find the error in the previous attempt"`, which inflates breaking rate $b$ from `5.4%` to `7.2%` on already-correct derivations).
   - Extract the new visible derivation $a_{k+1}$ (`z_{k+1}` stripped) to replace $a_k$.
3. **Terminate on budget or answer stability**:
   - Stop at a small fixed step cap ($K = 5$ already beats `10`-sample `Self-Consistency` on `AIME 2024` at `36.1k` vs. `114.9k` cumulative tokens, `-68.6%`; $K = 8\text{--}16$ captures asymptotic gains) or when consecutive visible derivations agree on both intermediate invariants and final answer.

### Phase 3: Optional `In-Weight RSI` Consolidation on Unlabeled Open-Weight Batches

When adapting an open-weight model across an unlabeled batch $\mathcal{Q} = \{x_i\}_{i=1}^M$ so improvements persist in single-pass inference (`Attempt 1`):

1. **Collect one adjacent refinement pair per unlabeled query**:
   - For each $x \in \mathcal{Q}$, sample one unconditioned rollout $y_1 = (z_1, a_1) \sim \pi_\theta(\cdot \mid x)$ and one Markovian refinement $y_2 = (z_2, a_2) \sim \pi_\theta(\cdot \mid x, a_1)$, stripping `<think>` traces $z_1, z_2$ when forming teacher contexts.
2. **Optimize `Recursive Distillation` + TV-weighted `Accelerated Distillation` over LoRA adapters**:
   - Attach a bounded LoRA adapter (e.g., `r = 64, alpha = 128`, frozen copy $\bar{\theta}$ as teacher) and compute token-level reverse KL (`OPSD`) over three forward contexts without ground-truth labels:
     - **Answer-transfer loss (`L_ans`)**: Student $\pi_\theta(\cdot \mid x)$ matches teacher $\pi_{\bar{\theta}}(\cdot \mid x, a_1)$ along refined visible tokens $a_2$.
     - **Reasoning-consistency loss (`L_ref`)**: Student $\pi_\theta(\cdot \mid x)$ matches its stripped visible summary context $\pi_{\bar{\theta}}(\cdot \mid x, \text{strip\_think}(y_2))$ along internal trace $z_2$ so internal reasoning stays aligned with clean derivations.
     - **TV-shift-weighted `Accelerated Distillation` (`L_acc`)**: Student $\pi_\theta(\cdot \mid x)$ matches stronger self-conditioned teacher $\pi_{\bar{\theta}}(\cdot \mid x, a_2)$ along $a_2$, weighting each token $t$ by bounded total-variation shift between $\pi_{\bar{\theta}}(\cdot \mid x, a_2)$ and $\pi_{\bar{\theta}}(\cdot \mid x, a_1)$:
       $$\omega_t = 1 - \alpha + \frac{2\alpha \, d_t}{d_t + \tau}, \qquad d_t = D_{\mathrm{TV}}\!\left(p_2^{(t)}, p_1^{(t)}\right) \in [0, 1]$$
       (with default $\alpha = 0.2, \tau = 0.2$, bounding weights to $[0.8, 1.2]$ so pivotal error-correction tokens are amplified without destabilizing unchanged tokens).
   - Run a short adapter update (`~15` optimizer steps at `LR = 5e-5`; avoid prolonged unlabeled self-training).
3. **Gate persistent adapter retention and optionally stack `In-Context RSI`**:
   - If the updated LoRA adapter is only used ephemerally for the current test batch, discard it afterward; if promoting the checkpoint persistently, pass it through `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../../rules/recursive-improvement.md).
   - At deployment, `In-Context RSI` can be stacked directly on top of the `In-Weight RSI` checkpoint for compounding gains (`72.92% -> 86.46%` on `Qwen3-4B` `AIME 2024`).

## Failure Modes & Guardrails

- **Answer-only carryover trap**: Passing only the previous final answer without its intermediate derivation leaves the next step unable to inspect where the prior attempt went wrong (`+0.52%` gain vs. `+9.06%` at Attempt 5 on `AIME 2024`). Always pass the clean visible derivation $a_k$.
- **Transcript accumulation bloat**: Keeping $(a_1, a_2, \dots, a_k)$ or raw `<think>` blocks in context linearly inflates KV cache and reintroduces abandoned dead-end branches; strict Markovian state ($a_k$ only, `< 1,000` prompt tokens) preserves flat prompt overhead.
- **Critique-bias regressions**: Prompting the model to `"critique"` or `"correct"` $a_k$ induces sycophantic second-guessing on correct solutions ($b$ rises `5.4% -> 7.2%`). Preserve neutral `"solve independently"` framing.
- **Wrong-majority collapse vs. short-horizon `OPSD`**: Majority-vote `TTRL` degrades hard problems whose initial majority is wrong (`5.73% -> 2.86%` `avg@64` on `Qwen3-8B` wrong-majority `AIME 2024` problems), whereas adjacent-pair `TT-RSI` lifts that subset to `12.76%` (`0/6 -> 2/6` `maj@64`); keep unlabeled `In-Weight RSI` short (`~15` steps) to avoid entropy collapse.

## Cross-References

- **Rules**: [`recursive-improvement.md`](../../rules/recursive-improvement.md) — `"DON'T: Conflate reasoning effort with algorithmic ability"` and `"DO: Pass every self-modification through one acceptance gate"`.
- **Rules**: [`multi-agent-coordination.md`](../../rules/multi-agent-coordination.md) — `"DO: Replace scalar voting on label-free executed data artifacts with contract-validated pairwise knockout tournaments, abstaining code+artifact guardrails, and tier-matched (N, r) retry allocation"`.
- **Skills**: [`abstaining-guardrail-best-of-n`](../abstaining-guardrail-best-of-n/SKILL.md) — Parallel candidate tournament + abstaining code/dataframe guardrail when executable artifact contracts exist.
- **Research Briefs**: [`e2l-gradient-aligned-experience-distillation`](../../research-briefs/e2l-gradient-aligned-experience-distillation.md) — Gradient-aligned experience selection when distilling explicit natural-language experiences via `OPSD`.
- **Specs**: [`self-improving-agent.spec.md`](../../specs/self-improving-agent.spec.md) — Test-time vs. persistent self-improvement governance.

## Sources

- *Beyond Self-Consistency: Recursive Self-Improvement at Test Time* (`TT-RSI`, `arXiv:2611.30965`)
