# Auditable Unlearning for LLMs: Widen the Gap, Hide the Gap

> **Source**: [arXiv:2611.05866](https://arxiv.org/abs/2611.05866) | `src:2611-05866`
> **Authors**: Piyush Tiwary, Anushka Srivastava, Prathosh A.P
> **Category**: Research Brief (Machine Unlearning / Privacy & Auditability / Inference-Time Rejection Sampling)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Overview

Regulatory frameworks such as GDPR's "right to be forgotten" require model providers to remove specific training targets ($\mathcal{D}_f$) from deployed LLMs while preserving general utility on retained knowledge ($\mathcal{D}_r$). Tiwary et al. demonstrate that practical machine unlearning requires satisfying **four simultaneous criteria**:
1. **Forget Efficacy**: Suppressing verbatim and novel-entity recall on the forget set $\mathcal{D}_f$ ($1 - \text{Novel-Entity Recall}$).
2. **Retain Utility**: Preserving novel-entity recall and generation quality on $\mathcal{D}_r$.
3. **Black-Box Leakage Robustness**: Preventing external adversaries from inferring whether a prompt belonged to $\mathcal{D}_f$ via abnormal output behaviors ($\text{MIA}(\theta_u) = \min(2(1 - \mathrm{AUROC}_{\text{leak}}(\theta_u)), 1)$ across a 4-channel black-box detector measuring `all-MiniLM-L6-v2` refusal template similarity, `cross-encoder/nli-deberta-v3-small` NLI refusal, structural first-person/negation refusal, and 2/3/4-gram repetition degeneration).
4. **Provider-Side Auditability**: Enabling the model provider (who holds both the frozen base model $\theta_0$ and the unlearned model $\theta_u$) to verify unlearning via a clean statistical separation ($\mathrm{AUROC} \ge 0.95$) between $\mathcal{D}_f$ and $\mathcal{D}_r$ using token-averaged energy gaps (log-probability gap $G(\mathbf{x}, \mathbf{y})$, KL divergence, JS divergence, or entropy gap).

Evaluating `11` state-of-the-art unlearning methods (`GradAscent`, `GradDiff`, `WGA`, `DPO`, `NPO`, `SimNPO`, `RMU`, `CEU`, `UNDIAL`, `PDU`, and `SatImp`) across `TOFU` (`Llama-3.2-1B`, `Llama-3.2-3B`, `Llama-3.1-8B`), `MUSE` (`News` and `Books` on `Llama-2-7b-hf`), and `RWKU` (`Llama-3-3B` and `Llama-3.1-8B`), the authors uncover a fundamental **Unlearning Dilemma**: **`0 of 11` existing methods satisfy all four criteria simultaneously**. Methods that create a strong internal likelihood gap for auditing (`GradDiff`, `RMU`, `WGA`, `DPO`) exhibit severe external black-box MIA leakage through degenerate token repetition or canned refusals, while methods that avoid obvious surface abnormalities (`CEU`, `GradAscent`, `SatImp`) fail provider auditability ($\mathrm{AUROC} < 0.70$).

To resolve this tension for black-box API deployments, the authors propose a two-stage framework:
- **Stage 1 (`GapWiden`)**: When an unlearned model's raw provider audit AUROC is below `0.95`, `GapWiden` fine-tunes $\theta_u$ for `8`-epoch rounds ($\text{lr} = 10^{-5}$) using a margin hinge loss on $\mathcal{D}_f$ ($m = 6.0, \gamma = 1.0$) to widen the base-vs-unlearned log-probability gap $G(\mathbf{x}, \mathbf{y})$ while anchoring retain-set divergence gaps near zero via a Huber ($\text{smooth-}\ell_1, \alpha = 1.0$) loss.
- **Stage 2 (`GapVeil`)**: At inference time, rather than decoding directly from the degraded unlearned model $\theta_u$, the system drafts candidate responses $\mathbf{y}^{(k)} \sim p_{\theta_0}(\cdot \mid \mathbf{x})$ from the **fluent base model** $\theta_0$ (up to budget $K = 3$ steps). It checks whether the internal energy gap $E(\mathbf{x}, \mathbf{y}^{(k)}) = G(\mathbf{x}, \mathbf{y}^{(k)}) - \tau \le 0$ (where $\tau = \arg\max(0.85 \cdot \mathrm{TPR} + 0.15 \cdot \mathrm{TNR})$). If $E > 0$ (indicating the draft contains forgotten knowledge), `GapVeil` rejects the draft, adds its content tokens (excluding prompt tokens, special tokens, and stop/function words) to a token-suppression set $\mathcal{R}_k$ ($p_{\theta_0}[\mathcal{R}_k] = 0$), and redrafts from $\theta_0$.

## Key Findings

1. **`0 of 11` Baseline Unlearning Methods Pass All Four Axes**: On `TOFU` (`Llama-3.1-8B`), `11` baseline methods partition into three failure modes:
   - *Un-auditable*: `CEU` (max audit AUROC `0.69` across log-p/KL/JS/Entropy), `GradAscent` (`0.54`), and `SatImp` (`0.69`) fail to separate $\mathcal{D}_f$ from $\mathcal{D}_r$.
   - *High Black-Box Leakage*: `GradDiff` (attacker advantage $|\mathrm{AUROC}_{\text{leak}} - 0.5| = 0.37$, repeating single tokens `200` times), `WGA` (`0.28`), `RMU` (`0.23`), and `DPO` (structural refusal AUROC reaching `0.61`, `0.73`, and `0.88` on `1B`, `3B`, and `8B` models) leak forget-set membership to black-box query attackers.
   - *Retain Collapse*: `NPO`, `PDU`, and `UNDIAL` achieve auditability and low leakage only by collapsing retain utility (e.g., `NPO` retain drops to `0.21` on `Llama-3.2-3B` `TOFU-forget10`).
2. **`GapWiden` Restores Provider Auditability (`> +0.30` AUROC) But Increases Direct-Decoding Leakage**: Applying `GapWiden` to non-auditable baselines (`CEU`, `GradAscent`, `SatImp` on `TOFU`; all `11` methods on `MUSE`) raises provider audit AUROC by over `0.30` points to `0.98–1.00` (`1.00` across log-p, KL, and JS on `TOFU`). However, widening the parameter gap in isolation increases direct-decoding black-box attacker advantage (e.g., `CEU` `0.11` $\to$ `0.26`, `GradAscent` `0.10` $\to$ `0.30`), proving that internal auditability must be paired with an inference-time veil.
3. **`GapVeil` Simultaneously Boosts Forget, Retain, and Leakage Robustness via Fluent Base-Model Redrafting**: Across all `11` methods on `TOFU` (`Llama-3.1-8B`), adding `GapVeil` ($K=3$) raises average Forget and Retain scores from `~0.75` to `~0.90` across `forget01`, `forget05`, and `forget10`, while improving average Leakage scores by `+0.11` on `forget01` and `~+0.25` on `forget05/10` (more than doubling leakage resistance for `PDU`, `RMU`, and `WGA`). Black-box attacker advantage $|\mathrm{AUROC}_{\text{leak}} - 0.5|$ compresses from `0.10–0.37` into a narrow `0.11–0.15` band across all `11` methods (`GradDiff` `0.37` $\to$ `0.12`, `WGA` `0.28` $\to$ `0.15`, `RMU` `0.23` $\to$ `0.11`). On `Llama-3.2-3B` (`forget10`), `NPO` retain rebounds from `0.21` to `0.72` and average leakage rises from `~0.70–0.80` to `~0.98`.
4. **Generalization to Real-World Entity Unlearning (`RWKU`) vs. High-Overlap Regimes (`MUSE`)**:
   - On `RWKU` (`Llama-3-3B` `forget10`), `GapWiden + GapVeil` lifts average auditability from `~0.82–0.86` to `~0.99`, average forget from `0.67` to `0.84`, and `CEU` retain from `0.07` to `0.68`. On `Llama-3.1-8B`, auditability reaches `~1.00`, leakage reaches `1.00` (up from `~0.92–0.93`), and retain rises from `~0.52–0.60` to `~0.67–0.69` (`GradDiff` `forget10` retain `0.25` $\to$ `0.69`).
   - On `MUSE` (`Llama-2-7b-hf`), auditability rises from `0.84` to `0.99` (`News`) and `0.81` to `0.99` (`Books`) with improved forget and leakage, but retain utility drops from `0.569` to `0.380` on `News` and `0.420` to `0.400` on `Books` because `MUSE` uses a `1:1` forget-to-retain ratio (vs `1:10` on `TOFU-forget10`) with dense entity overlap that triggers false-positive rejections.
5. **Strict Black-Box Threat Model Boundary**: Because `GapWiden` intentionally amplifies the likelihood gap between $\theta_0$ and $\theta_u$ on forgotten targets, any adversary with **white-box weight access** to $\theta_u$ (or both checkpoints) could exploit that gap to reconstruct $\mathcal{D}_f$. Furthermore, `GapVeil` requires serving both $\theta_0$ and $\theta_u$ behind an API gateway. Thus, this architecture is strictly valid for proprietary/hosted black-box API deployments and must **never** be used for open-weight model releases.

## Quantitative Summary

### Table 1: Representative Baseline vs. `GapWiden + GapVeil` Results Across Benchmarks

| Benchmark & Model | Method / Aggregate | Metric Axis | Baseline (Raw $\theta_u$) | With `GapWiden + GapVeil` ($K=3$) |
|:---|:---|:---|---:|---:|
| `TOFU` (`Llama-3.1-8B`) | `CEU` / `GradAscent` / `SatImp` | Provider Audit AUROC (Log-P / KL / JS) | `0.54–0.69` | **`1.00`** (`+0.31` to `+0.46`) |
| `TOFU` (`Llama-3.1-8B`, `forget01/05/10`) | 11-Method Mean | Forget & Retain Scores | `~0.75` | **`~0.90`** (`+0.15`) |
| `TOFU` (`Llama-3.1-8B`, `forget05/10`) | 11-Method Mean | Black-Box Leakage Score ($\text{MIA}(\theta_u)$) | Baseline | **`+0.25`** (`>2x` on `PDU`, `RMU`, `WGA`) |
| `TOFU` (`Llama-3.1-8B`) | `GradDiff` / `WGA` / `RMU` | Attacker Advantage $|\mathrm{AUROC}_{\text{leak}} - 0.5|$ | `0.37` / `0.28` / `0.23` | **`0.12` / `0.15` / `0.11`** (all 11 in `0.11–0.15`) |
| `TOFU-forget10` (`Llama-3.2-3B`) | `NPO` (and 11-Method Mean) | Retain Utility / Mean Leakage Score | `0.21` retain / `0.70–0.80` leak | **`0.72`** retain / **`~0.98`** leak |
| `TOFU-forget10` (`Llama-3.2-1B`) | 11-Method Mean | Retain Utility | `0.31` | **`0.49`** (`+0.18`) |
| `RWKU-forget10` (`Llama-3-3B`) | 11-Method Mean (`CEU` retain) | Audit AUROC / Forget / `CEU` Retain | `0.82–0.86` / `0.67` / `0.07` | **`~0.99`** / **`0.84`** / **`0.68`** |
| `RWKU-forget10` (`Llama-3.1-8B`) | 11-Method Mean (`GradDiff` retain) | Audit AUROC / Leakage / `GradDiff` Retain | `0.91–0.97` / `0.92–0.93` / `0.25` | **`~1.00`** / **`1.00`** / **`0.69`** |
| `MUSE-News` (`Llama-2-7b-hf`) | 11-Method Mean | Audit AUROC / Retain Utility | `0.84` / `0.569` | **`0.99`** / `0.380` (`-0.189`, 1:1 overlap) |
| `MUSE-Books` (`Llama-2-7b-hf`) | 11-Method Mean | Audit AUROC / Retain Utility | `0.81` / `0.420` | **`0.99`** / `0.400` (`-0.020`, 1:1 overlap) |

## Why Not a Skill?

`GapWiden` and `GapVeil` operate on LLM weight post-training (fine-tuning $\theta_u$ with hinge-margin and Huber objectives) and token-level logit manipulation across dual model checkpoints ($\theta_0$ and $\theta_u$) inside an LLM serving engine. Because coding and research agents cannot execute gradient updates or logit-level vocabulary suppression during normal subtask workflows, this paper is cataloged as a **Research Brief** and distilled into an evaluation rule in `output/rules/agent-evaluation-quality.md`.

## Actionable Takeaways

1. **Audit unlearned models across all four axes—never Forget + Retain alone**: Evaluating unlearning solely on forget and retain accuracy misses both un-auditable weight updates (`CEU`, `GradAscent`, `SatImp` with audit AUROC `< 0.70`) and Streisand-effect membership leakage (`GradDiff`, `WGA`, `RMU`, `DPO` with black-box attacker advantage up to `0.37`). Always include a multi-channel black-box abnormality detector (embedding similarity, NLI refusal, structural negation, and n-gram repetition) alongside provider energy-gap auditing.
2. **Decouple the internal audit signal from the external generation distribution**: In black-box API deployments, do not serve tokens directly from an unlearned checkpoint $\theta_u$ whose weights have been perturbed to maximize forget-set divergence. Instead, use $\theta_u$ strictly as an internal energy-gap verifier over fluent drafts sampled from $\theta_0$ with content-token suppression (`GapVeil`).
3. **Never apply gap-widening unlearning to open-weight checkpoints**: Any method that embeds a verifiable likelihood gap between $\theta_0$ and $\theta_u$ (`GapWiden`) turns into a membership-extraction oracle if weights are released publicly. Restrict gap-widening to closed API endpoints where both $\theta_0$ and $\theta_u$ remain confidential.
