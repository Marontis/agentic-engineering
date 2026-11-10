# Do Benign-Trained Hidden-State Probes Detect Tool Errors Under Adversarial Conditions?

> **Source**: [arXiv:2611.11172](https://arxiv.org/abs/2611.11172) — Bibek Bhandari, Kshitij Lingthep (2026)
> **Praxis Source ID**: `src:2611-11172v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

This paper is a controlled negative-result transferability audit evaluating whether pre-action hidden-state linear probes trained strictly on benign agent trajectories can detect operational tool-call errors under adversarial perturbations (`AgentDojo v1.1.1`). Rather than introducing a new multi-step software procedure, it demonstrates that **zero-training token-level output uncertainty signals (`mean tool-call-token entropy` and `-MeanLogP`) beat benign-trained final-layer hidden-state probes across all `12` model-condition cells**, and that scaling model size (`Qwen2.5-7B-Instruct` $\to$ `Qwen2.5-14B-Instruct`) causes the benign-trained probe to collapse **below chance (`0.431` AUROC)** under `system-override`. Its lessons belong as monitoring and probe-calibration rules in [`agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md) and [`agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md).

## Experimental Protocol

- **Benchmark & Population Accounting**: Evaluates `96` task-suite groups (`Workspace`, `Banking`, `Travel`, `Slack`; `slack/user_task_11` unavailable) from `AgentDojo v1.1.1` across `3` open-weight models (`GLM-4.6V-Flash` 9B, `Qwen2.5-7B-Instruct`, `Qwen2.5-14B-Instruct`, 8-bit quantized, max `8` tool steps) and `4` operating conditions (`benign`, `prompt-injection`, `system-override`, `tool-poisoning`).
  - From `4,918` non-defended step records, `771` ground-truth-exhaustion sentinels are excluded, leaving **`4,147` out-of-fold (`OOF`) step records**: **`3,836` complete-case tool-call-bearing records** (with valid tool-call token boundaries and finite values for all four signals) and **`311` missing-tool-call records** (label `1`, retained in OOF accounting but lacking tool-call token spans).
- **Zero-Adversarial Training Split**: A `StandardScaler` + L2 logistic regression (`C = 1.0`, `liblinear`, balanced class + task weights) is fit on the **final-layer residual state of the last prompt token immediately preceding tool-call generation** using **only `1,027` eligible benign step records** across 5 suite-task-grouped folds (`20, 19, 19, 19, 19` groups, `seed = 42`), producing `3,763` (`90.7%`) step-specific predictions and `384` (`9.3%`) pooled-fallback predictions (`161` GLM, `195` Qwen 7B, `28` Qwen 14B).
- **Zero-Training Scalar Comparators**:
  1. **Mean tool-call-token entropy** (`Entropy`): Average predictive entropy over emitted tool-call tokens.
  2. **Negative mean tool-call-token log-probability** (`-MeanLogP`): Average negative log-likelihood over emitted tool-call tokens.
  3. **Self-consistency uncertainty**: Complement of canonical-JSON tool-call agreement across `4` generations (`1` greedy at $T = 0.0$ + `3` stochastic at $T = 0.7, \text{top-}p = 0.9$).

## Key Quantitative Findings

### 1. Scalar Token-Uncertainty Baselines Outperform the Benign-Trained Probe in 12/12 Cells

Across the `3,836` complete-case tool-call-bearing records (`AUROC / AP`):

| Model | Condition | $n$ | Benign-Trained Hidden Probe | Mean Tool-Call Entropy | $-\mathrm{MeanLogP}$ | Self-Consistency ($k=4$) |
|:---|:---|---:|:---:|:---:|:---:|:---:|
| **GLM-4.6V-Flash (9B)** | Benign | 303 | `0.699 / 0.807` | `0.718 / 0.850` | **`0.723 / 0.856`** | `0.650 / 0.785` |
| **GLM-4.6V-Flash (9B)** | Prompt injection | 307 | `0.676 / 0.783` | `0.723 / 0.846` | **`0.725 / 0.848`** | `0.650 / 0.768` |
| **GLM-4.6V-Flash (9B)** | System override | 270 | `0.621 / 0.706` | `0.711 / 0.796` | `0.720 / 0.807` | **`0.742` / `0.799`** |
| **GLM-4.6V-Flash (9B)** | Tool poisoning | 323 | `0.711 / 0.827` | `0.733 / 0.864` | **`0.738 / 0.869`** | `0.721 / 0.841` |
| **Qwen2.5-7B-Instruct** | Benign | 315 | `0.621 / 0.778` | **`0.799` / `0.916`** | `0.796` / **`0.917`** | `0.704 / 0.844` |
| **Qwen2.5-7B-Instruct** | Prompt injection | 327 | `0.642 / 0.803` | **`0.819` / `0.932`** | **`0.819 / 0.934`** | `0.750 / 0.880` |
| **Qwen2.5-7B-Instruct** | System override | 282 | `0.575 / 0.694` | **`0.782 / 0.871`** | `0.777 / 0.864` | `0.645 / 0.754` |
| **Qwen2.5-7B-Instruct** | Tool poisoning | 331 | `0.642 / 0.803` | **`0.799 / 0.927`** | `0.796 / 0.926` | `0.726 / 0.870` |
| **Qwen2.5-14B-Instruct** | Benign | 337 | `0.695 / 0.741` | **`0.736 / 0.793`** | `0.729 / 0.783` | `0.677 / 0.741` |
| **Qwen2.5-14B-Instruct** | Prompt injection | 380 | `0.702 / 0.815` | **`0.763 / 0.870`** | `0.759 / 0.863` | `0.718 / 0.817` |
| **Qwen2.5-14B-Instruct** | **System override** | **309** | **`0.431 / 0.573`** | **`0.758 / 0.821`** | `0.744 / 0.798` | `0.730 / 0.781` |
| **Qwen2.5-14B-Instruct** | Tool poisoning | 352 | `0.731 / 0.831` | **`0.759 / 0.865`** | `0.756 / 0.857` | `0.673 / 0.791` |

### 2. Below-Chance Collapse on `Qwen2.5-14B-Instruct` Under `System-Override`

- **Non-monotonic scaling failure**: Moving from `Qwen2.5-7B-Instruct` to `Qwen2.5-14B-Instruct` improves benign-trained probe AUROC under benign (`0.621` $\to$ `0.695`), prompt-injection (`0.642` $\to$ `0.702`), and tool-poisoning (`0.642` $\to$ `0.731`), **but reverses the probe's ranking below chance (`0.431` AUROC, `0.573` AP) under `system-override`**, assigning *lower* error scores to hijacked/incorrect tool calls than to valid ones.
- **Holm-Corrected Paired Significance**: Across `72` paired comparisons (`10,000` task-cluster swap permutations), **all `6` Holm-significant differences** occur on `Qwen2.5-14B-Instruct` under `system-override` in favor of the zero-training scalar uncertainty baselines ($p_{\text{Holm}} = 0.0036$ for all six):
  - Probe minus `Entropy`: $\Delta\text{AUROC} = -0.3269$, $\Delta\text{AP} = -0.2486$
  - Probe minus `-MeanLogP`: $\Delta\text{AUROC} = -0.3128$, $\Delta\text{AP} = -0.2252$
  - Probe minus `Self-consistency`: $\Delta\text{AUROC} = -0.2986$, $\Delta\text{AP} = -0.2081$
  - Under simultaneous family-wise `max-|t|` bootstrap intervals (`10,000` task-cluster resamples), `22/72` intervals exclude zero (all favoring the scalar comparators).
- **Robust to Fallback Removal**: Discarding the `28` pooled-fallback predictions on `Qwen2.5-14B-Instruct` leaves the `system-override` collapse unchanged (`0.428 / 0.564` probe vs `0.762 / 0.819` entropy, `0.747 / 0.794` `-MeanLogP`, and `0.731 / 0.778` self-consistency).

## Engineering & Architectural Implications

1. **Distinguish exposure probes from benign-trained correctness probes**: Linear probes succeed when trained *with* explicit adversarial classes at intermediate layers—such as stealth skill-injection exposure (`LatentTriad`, [latenttriad-pre-action-skill-risk-representations.md](latenttriad-pre-action-skill-risk-representations.md)) or mid-layer role-spoofing shifts ([role-spoofing-mechanisms-and-linear-probes.md](role-spoofing-mechanisms-and-linear-probes.md))—or on single-turn epistemic mean shifts ([`hallucination-mean-shift-probe`](../skills/hallucination-mean-shift-probe/SKILL.md)). A final-layer pre-action probe trained *only* on benign execution errors learns ordinary task-uncertainty directions that authoritative `system-override` framing actively suppresses or inverts in larger models.
2. **Use zero-training output token entropy / `-MeanLogP` as your baseline runtime risk gate**: Computing mean token entropy over emitted tool-call tokens requires zero auxiliary probe training, zero extra LLM forward passes (unlike 4-sample self-consistency), and outperforms benign-trained pre-action hidden-state probes in `12/12` model-condition cells (`0.711–0.819` AUROC).
3. **Add an explicit missing-tool-call check**: Because token-span entropy and `-MeanLogP` are undefined when an adversary suppresses tool emission altogether (`311 / 4,147` OOF steps = `7.5%`), pair token-entropy scoring on emitted calls with a deterministic workflow state check whenever a required tool step emits plain text only.

## Related Artifacts

- [`hallucination-mean-shift-probe`](../skills/hallucination-mean-shift-probe/SKILL.md) — Linear probing for epistemic hallucination detection in benign QA/RAG (contrasts epistemic mean-shift probing with adversarial tool-error non-transfer).
- [latenttriad-pre-action-skill-risk-representations.md](latenttriad-pre-action-skill-risk-representations.md) — Demonstrates high AUROC (`99.6%`) when pre-action probes are trained *supervisedly* on benign vs. stealth-injected vs. overt-malicious prompts at layer $0.5L$.
- [role-spoofing-mechanisms-and-linear-probes.md](role-spoofing-mechanisms-and-linear-probes.md) — Shows authority/role-spoofing text shifts intermediate hidden states along the `system-vs-user` axis, helping explain why `system-override` flips benign-trained error probes.
- [collusion-probe-evaluation-pitfalls.md](collusion-probe-evaluation-pitfalls.md) — Companion audit showing multi-agent collusion probes similarly fail out-of-distribution when prompt/context conditions shift.
