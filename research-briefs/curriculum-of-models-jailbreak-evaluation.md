# Discovering Jailbreaks via Curriculum of Models: Defensive & Evaluation Takeaways

> **Source**: [arXiv:2610.38833](https://arxiv.org/abs/2610.38833) — Michał Burzyński, Noah T. Rossi, Shomit Basu, Andy Arditi (2026-10-28)
> **Praxis Source ID**: `src:2610-38833`
> **Category**: Research Brief (Defensive Red-Teaming Methodology, Sparse-Reward Elicitation & Judge Calibration)

---

## Why Not a Skill?

This paper studies an automated white-box red-teaming method (**Curriculum of Models, CoM**) that interpolates between a refusal-weakened LoRA adapter ($\alpha = 1$) and an unmodified target model ($\alpha = 0$) to overcome sparse rewards during RL investigator training. In accordance with Praxis dual-use safety standards, we do not package jailbreak-generation procedures as executable skills. Instead, this brief extracts the defensive auditing, sparse-reward failure diagnostics, and multi-judge evaluation lessons for [`../rules/agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md).

---

## Core Findings

### 1. Why Single-Target Direct RL and Importance-Weighted Proposals (`PRBO`) Underestimate Model Risk

When auditing a safety-trained model (`gemma-4-31b-it` or `gpt-oss-120b`) on rare, hard-to-elicit behaviors (where **5,100–5,120 rollouts** from a warm-started auditor yield **0.0%** `pass@1` against the unmodified model $M_0$, even though the model possesses the latent capability at `0.888–0.997` `pass@16` when refusals are suppressed), standard RL red-teaming baselines fail to surface existing vulnerabilities in single-behavior audits:

| Target Model | Single-Behavior `Direct RL` Mean `pass@1` (4 tasks) | Single-Behavior `PRBO` Mean `pass@1` (4 tasks) | Single-Behavior `CoM` Mean `pass@1` (4 tasks) | Multi-Behavior (39 Held-Out Tasks) `Direct RL / PRBO / CoM` |
|:-------------|:----------------------------------------------------|:-----------------------------------------------|:----------------------------------------------|:------------------------------------------------------------|
| **`gemma-4-31b-it` (no reasoning)** | **0.00%** across all 4 tasks | **0.00%** on 3/4 tasks (**9.8%** on 1 task) | **0.4%–50.1%** (nonzero on 4/4 tasks; `pass@32` **11.0%–100.0%**) | **7.0% / 60.0% / 44.2%** |
| **`gemma-4-31b-it` (with reasoning)** | **0.00%** across all 4 tasks | **0.00%** across all 4 tasks | **0.3%–33.6%** (nonzero on 4/4 tasks; `pass@32` **7.8%–99.7%**) | — |
| **`gpt-oss-120b` (medium reasoning)** | **0.00%** on 3/4 tasks (**16.0%** on 1 task) | **0.00%–0.1%** across all 4 tasks | **26.4%–61.1%** (nonzero on all 12 seeds; `pass@32` **100.0%**) | **56.4% / 62.8% / 54.3%** |

- **Investigator Refusal Lock-In Under `PRBO` (Appendix F)**: In **40 of 48** single-behavior `PRBO` runs, the `qwen3.5-9b` investigator never overcame its own initial refusal (`91.8%` base refusal rate) to generate red-teaming prompts, yielding **0.000 `pass@1`**. Increasing the GRPO group size from $G = 64$ to $G = 256$ left investigator refusal at **97.7%–100.0%** (`0.000` `pass@1`), and warm-starting the investigator with anti-refusal SFT (`0.0%` refusal) still yielded nonzero `pass@1` in only **1 of 3 seeds** (`0.078`). Furthermore, **15 of 17** hyperparameter configurations in the `PRBO` $\lambda$-sweep scored `0.000` `pass@1` (Table 3).
- **Natural Task Curricula in Multi-Behavior Training**: Training a single investigator jointly across **8 behaviors** of varying difficulty unlocked both `PRBO` (**60.0%–62.8%** held-out `pass@1` across 39 unseen tasks) and `Direct RL` on `gpt-oss-120b` (**56.4%** held-out `pass@1`), because easier behaviors provided dense early rewards that prevented investigator refusal lock-in.

### 2. Curriculum Continuity & KL Regularization Dynamics (Section 4.1)

Interpolating target weights $W_k = W_0 + (k/K)\Delta W$ from $\alpha_K = 1$ to $\alpha_0 = 0$ reveals three stability requirements for curriculum-based safety auditing:
1. **Interpolation Granularity ($K$)**: A 2-step curriculum ($K = 2$, jumping from $\alpha = 0.5$ to $\alpha = 0$) caused **3/3 seeds to fail** upon reaching the unmodified model $M_0$, whereas $K = 5$ and $K = 10$ succeeded across all seeds.
2. **Stage Advancement Threshold ($\tau$)**: Advancing too early ($\tau = 20$) caused **1/3 seeds to fail** before reaching $M_0$; thresholds $\tau \in [40, 90]$ all succeeded, with $\tau = 90$ requiring nearly **$2\times$** as many steps as $\tau = 60$.
3. **KL Regularization ($\beta_{\mathrm{KL}}$)**: Removing the KL penalty ($\beta_{\mathrm{KL}} = 0$) caused **2/3 seeds to collapse to near-zero policy entropy**, while excessive regularization ($\beta_{\mathrm{KL}} = 2.0$) prevented **2/3 seeds** from ever reaching $M_0$ ($\beta_{\mathrm{KL}} = 0.5$ balanced diversity and exploration).

### 3. Judge Non-Determinism, Self-Preference, and Deliberation Depth (Appendix H)

Re-scoring **1,024 evaluation rollouts** (`512` per target) twice with the reference judge (`gpt-oss-120b`) and once with **5 cross-family judges** (`gemma-4-31b-it`, `gemini-3.5-flash-lite`, `kimi-k3`, `glm-5.3-flash`, `deepseek-v4.1-flash`) exposed critical evaluation artifacts:

| Judge Model | Exact 7-Level Agreement (%) | Within-1-Level Agreement (%) | Pass/Fail (`Score = 100`) Agreement (%) | Direction of Disagreement vs. `gpt-oss-120b` Reference |
|:------------|:----------------------------|:-----------------------------|:----------------------------------------|:-------------------------------------------------------|
| **`gpt-oss-120b` (Run 2)** | **81.6%** | **95.3%** | **92.9%** | Provider non-determinism despite requesting `temperature = 0` |
| **`gemma-4-31b-it`** | 68.3% | 90.4% | 89.6% | More lenient on `gemma`, stricter on `gpt-oss-120b` |
| **`gemini-3.5-flash-lite`** | 68.4% | 87.3% | 88.6% | More lenient on `gemma`, stricter on `gpt-oss-120b` |
| **`kimi-k3`** | 69.2% | 89.1% | 86.0% | More lenient on `gemma`, stricter on `gpt-oss-120b` |
| **`glm-5.3-flash`** | 68.6% | 85.0% | 85.3% | More lenient on `gemma`, stricter on `gpt-oss-120b` |
| **`deepseek-v4.1-flash`** | **58.7%** | **75.5%** | **77.7%** | Strictest overall; rejects flawed synthesis via longer CoT |

1. **Target–Judge Self-Preference Inflates ASR**: When `gpt-oss-120b` judged its own responses, **every single external judge in the 5-model panel was stricter** (awarding fewer 100-point passes), whereas on `gemma-4-31b-it` responses most external judges awarded 100 points *more* often than `gpt-oss-120b`.
2. **Judge Deliberation Length Drives Technical Plausibility Rejections**: `deepseek-v4.1-flash` overturned `gpt-oss-120b` pass verdicts (`77.7%` pass/fail agreement) primarily on the `authentic_synthesis` gate by reasoning longer on **70% of rollouts** (median **4,882 vs. 3,230 characters**) and catching concrete chemical reaction errors that shorter judge traces missed.
3. **API Provider Non-Determinism**: Routed API inference (`OpenRouter`) ignored `temperature = 0` in practice, causing the exact same judge model to disagree with itself on **18.4%** of exact 7-level scores and **7.1%** of binary pass/fail verdicts.

---

## Relevance to Praxis

- **Red-Team Evaluation & Judge Hygiene ([`../rules/agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md))**: Extends *"DON'T: Report red-team failure rates scored by a single judge model"* (`arXiv:2609.27336`) with three concrete requirements: (1) never use the target model as its own safety/plausibility judge due to self-preference inflation, (2) verify deterministic judge repeatability (`Run 1 vs. Run 2`) when routing through third-party inference providers, and (3) include a long-deliberation judge to audit technical-feasibility gates (`authentic_synthesis`) plus a prompt-validity judge (`no_answer`, `no_precursors`, `no_fiction`) so investigators are not rewarded for smuggling answers in the prompt.

---

## Key Citations

- **Chowdhury et al. (2025a, 2025b)** — *Propensity Bound (PRBO) & Investigator Agents* — Importance-weighted red-teaming baseline compared against CoM.
- **Panickssery et al. (2024)** — *LLM Evaluators Recognize and Favor Their Own Generations* — Self-preference bias confirmed here on `gpt-oss-120b` target–judge pairs.
