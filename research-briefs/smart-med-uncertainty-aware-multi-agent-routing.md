# SMART-Med: Selective Multi-Agent Medical Reasoning via Uncertainty-Aware Routing

> **Source**: [arXiv:2610.33544](https://arxiv.org/abs/2610.33544) — *Learning When to Collaborate: Selective Multi-Agent Medical Reasoning via Uncertainty-Aware Routing* (`src:2610-33544`)
> **Authors**: Jiacheng Hou, Xueliang Cui, Dan Lu, Ruxin Wang (Tsinghua SIGS, SUSTech, SUAT, West China Hospital, SIAT CAS, 2026)
> **Category**: Multi-Agent Coordination / Uncertainty-Aware Routing & Selective Collaboration

---

## Executive Summary

Multi-agent systems (MAS) for multimodal reasoning typically default to **always-on dense collaboration**, invoking multi-round deliberation across 4–6 specialist agents for every query. **SMART-Med** challenges this default by treating multi-agent collaboration as a **learnable deferred-decision problem** executed entirely on local, small-scale vision-language models (`Qwen3-VL-4B-Instruct`). A general-practitioner **router agent** produces an initial reasoning trace, an answer $\tilde{y}$, and an explicit binary certainty token (`CERTAIN` vs. `UNCERTAIN`). When `CERTAIN`, the system returns $\tilde{y}$ immediately in a single call; only when `UNCERTAIN` does it recruit up to 3 specialist agents for a 2-round moderator-synthesized consultation.

Trained via curriculum SFT and Group Relative Policy Optimization (**GRPO**) on **MedVR-3K** (3,477 multi-criteria quality-filtered and difficulty-graded medical VQA reasoning traces) using a **Certainty-Aware Accuracy Reward (`CAR`)** and a **Vision-Language Reasoning Reward (`RR`)**, SMART-Med achieves:

- **>3.8× faster inference** (`< 10` seconds/query vs. `38+` seconds for the fastest baseline `MDAgents`, and up to **11.9× faster** than dense `ColaCare`).
- **Over 72% fewer input tokens** (~600 input tokens/query) and **88% fewer output tokens** (~100 output tokens/query), averaging only **1.17 model calls per query** versus **5.51–17.92 calls** in prior MAS frameworks.
- **+6.7% average accuracy gain** after MedVR-3K fine-tuning (`SMART-Med*`) across four benchmarks (**Slake**, **PathVQA**, **VQA-RAD**, and **PMC-VQA**), while slashing the **false-certainty rate** (incorrect answers emitted as `CERTAIN`) from **28.8% to 8.6%**.

---

## Architecture & Reward-Shaped Selective Collaboration

### 1. Certainty-Aware Accuracy Reward (`CAR`) & Bayes-Optimal Deferral Threshold

Standard RL accuracy rewards $R_{\text{base}} = \mathbb{I}(y = y^\star) + \lambda_{\text{fmt}}\mathbb{I}(\text{format})$ cannot train a selective router because they treat overconfident wrong answers and calibrated deferrals identically. SMART-Med introduces the **Certainty-Aware Accuracy Reward (`CAR`)** for response $o_i$ with extracted answer $y_i$ and certainty indicator $c_i \in \{0, 1\}$ ($c_i = 1$ for `CERTAIN`, $c_i = 0$ for `UNCERTAIN`):

$$R_{\text{CAR}}(o_i) = \mathbb{I}(y_i = y^\star)\cdot\big[c_i + (1 - c_i)\alpha\big] - \mathbb{I}(y_i \neq y^\star)\cdot c_i \beta$$

where $\alpha \in (0, 1)$ awards reduced partial credit to correct answers that unnecessarily defer (`UNCERTAIN`), and $\beta > 0$ explicitly penalizes **overconfident mistakes** ($y_i \neq y^\star$ with `CERTAIN`).

**Theoretical Indifference Boundary**: If $p(x, q) = \Pr(y = y^\star \mid x, q)$ is the router's direct-answer correctness probability, expected utility for answering directly ($c_i = 1$) is $U_{\text{ans}} = p(x, q) - (1 - p(x, q))\beta$, while expected utility for deferring to multi-agent collaboration ($c_i = 0$) is $U_{\text{def}} = p(x, q)\alpha$. Answering directly is Bayes-optimal iff:

$$p(x, q) \ge \tau_{\text{Bayes}}, \qquad \tau_{\text{Bayes}} = \frac{\beta}{1 - \alpha + \beta}$$

This couples accuracy and calibration into a single GRPO advantage alongside a format indicator $R_{\text{FMT}}$ and a frozen `Qwen3-VL-2B-Instruct` **Reasoning-Quality Reward (`RR`)** $R_{\text{RR}}(o_i) = f_{\text{VLM}}(x, q, r_i, y_i)$.

### 2. MedVR-3K: Multi-Criteria Filtered & Difficulty-Graded Dataset

To prevent local 4B models from learning fluent but ungrounded explanations, the authors curated **MedVR-3K** (**3,477 samples**: 746 Slake, 721 PathVQA, 707 VQA-RAD, 1,303 PMC-VQA) via a two-stage pipeline:

1. **Correctness Filtering**: Sampled step-by-step reasoning traces from `GPT-5.4`, `Gemini 3 Pro`, `Qwen3-Max`, and `Kimi K2.5`, retaining only traces whose final answer matches ground truth $y^\star$.
2. **Conjunctive Multi-Dimension Judge Gate**: Rather than filtering on a single scalar score (where high fluency can mask visual hallucination), `GPT-5.4` scores each trace in $[1, 5]$ across **Logic Consistency** ($s_{\text{logic}}$), **Factual Correctness** ($s_{\text{fact}}$), and **Image Alignment** ($s_{\text{img}}$). A trace is admitted only if all three dimensions simultaneously clear their thresholds ($s_{\text{logic}} \ge \gamma_{\text{logic}} \land s_{\text{fact}} \ge \gamma_{\text{fact}} \land s_{\text{img}} \ge \gamma_{\text{img}}$), yielding a `3.60` mean quality score, plus a difficulty label $d \in \{\texttt{basic}, \texttt{medium}, \texttt{hard}\}$ used for curriculum SFT (5 epochs, LR $10^{-4}$) followed by hard-example GRPO (1 epoch, LR $10^{-6}$, group size $G = 6$).

---

## Key Empirical Results

### 1. Accuracy Across 4 MedVQA Benchmarks (`Qwen3-VL-4B-Instruct` Base, Table 1)

| Category / Method | Slake (MC) | PathVQA (MC) | VQA-RAD (MC) | PMC-VQA (MC) | Slake (FF) | PathVQA (FF) | VQA-RAD (FF) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Single Agent**: `Qwen3-VL-4B-Instruct` | 76.1 ± 1.4 | 64.6 ± 2.1 | 70.8 ± 1.8 | 35.3 ± 2.8 | 75.4 ± 0.8 | 44.3 ± 2.5 | 62.6 ± 4.2 |
| **Single Agent**: `Qwen3-VL-8B-Instruct` | 71.9 ± 2.3 | 59.0 ± 0.4 | 64.2 ± 0.5 | 50.2 ± 2.4 | 73.3 ± 0.7 | 45.8 ± 3.0 | 60.3 ± 5.0 |
| **Dense MAS**: `MedAgents` | 72.0 ± 1.4 | 73.7 ± 2.2 | 72.0 ± 0.1 | 52.5 ± 0.1 | 74.0 ± 0.8 | 48.8 ± 1.6 | 67.0 ± 3.0 |
| **Dense MAS**: `MDAgents` | 70.2 ± 1.2 | 75.6 ± 1.0 | 68.6 ± 2.0 | 50.6 ± 1.0 | 69.1 ± 1.9 | 46.6 ± 0.6 | 57.4 ± 4.3 |
| **Dense MAS**: `MOA` | 79.0 ± 1.0 | 69.2 ± 2.1 | 71.5 ± 0.5 | 51.5 ± 1.1 | 72.9 ± 0.7 | 52.6 ± 4.0 | 62.3 ± 2.7 |
| **Dense MAS**: `Reconcile` | 72.8 ± 1.0 | 64.2 ± 1.2 | 66.0 ± 0.5 | 49.0 ± 1.0 | 58.1 ± 1.0 | 43.1 ± 1.8 | 57.5 ± 4.3 |
| **Sparse MAS**: `SMOA` | 68.0 ± 1.1 | 62.2 ± 3.7 | 63.6 ± 1.2 | 49.3 ± 2.6 | 60.3 ± 1.0 | 38.9 ± 1.1 | 63.0 ± 1.5 |
| **Dense MAS**: `ColaCare` | 71.3 ± 1.5 | 60.8 ± 2.0 | 65.3 ± 0.6 | 50.0 ± 0.8 | 60.5 ± 1.8 | 45.2 ± 1.0 | 53.8 ± 2.6 |
| **`SMART-Med` (Zero-Shot Routing)** | 76.7 ± 1.0 | 68.6 ± 1.3 | 72.5 ± 0.5 | 48.5 ± 2.1 | 78.2 ± 1.3 | 48.7 ± 0.2 | 64.1 ± 3.2 |
| **`SMART-Med*` (MedVR-3K + GRPO)** | **87.0 ± 0.5** | **77.0 ± 1.1** | **74.0 ± 1.6** | **72.5 ± 1.0** | **84.3 ± 2.5** | **58.5 ± 3.5** | **69.4 ± 3.7** |

### 2. Step-by-Step Component Ablation & Calibration Telemetry (Tables 2, 3, & 5)

| Ablation Stage (`Qwen3-VL-4B-Instruct`) | Slake (MC) | PathVQA (MC) | VQA-RAD (MC) | PMC-VQA (MC) | Slake (FF) | PathVQA (FF) | VQA-RAD (FF) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1. Single Agent** | 76.1 | 64.6 | 70.8 | 35.3 | 75.4 | 44.3 | 62.6 |
| **2. + Always-On Dense Collaboration** | 78.5 | 66.7 | 71.3 | 50.1 | 75.7 | 51.2 | 64.5 |
| **3. + Uncertainty Routing (`SMART-Med`)** | 76.7 | 68.6 | 72.5 | 48.5 | 78.2 | 48.7 | 64.1 |
| **4. + Certainty-Aware Reward (`CAR` GRPO)** | 85.5 | 75.0 | 73.1 | 69.5 | 82.2 | 56.8 | 68.7 |
| **5. + Reasoning Reward (`RR` = `SMART-Med*`)** | **87.0** | **77.0** | **74.0** | **72.5** | **84.3** | **58.5** | **69.4** |

- **Zero-Shot Uncertainty Routing Beats Dense Collaboration on 3 of 7 Splits**: Even before training, replacing universal dense collaboration with uncertainty routing improves PathVQA MC (`66.7% → 68.6%`), VQA-RAD MC (`71.3% → 72.5%`), and Slake FF (`75.7% → 78.2%`) while cutting model calls from `5.51–17.92` down to `1.17`.
- **False-Certainty Suppression & Risk-Coverage Calibration (Appendix C)**: Certainty-aware GRPO reduces the Area Under the Risk–Coverage Curve (**AURC**) from **0.2669 to 0.2334** while lifting full-coverage accuracy from **66.0% to 71.5%**. Crucially, the **false-certainty rate** (`Incorrect + CERTAIN`, where a wrong answer bypasses specialist review) drops by **−20.2 percentage points** (from **28.8% to 8.6%**), while incorrect direct assessments properly flagged `UNCERTAIN` and routed to specialists rise from **5.3% to 15.7%**.
- **Reasoning Quality (Table 2, 100-Sample Judge Audit)**: `SMART-Med*` achieves the highest mean reasoning quality (**3.50 / 5.0**: Logic Consistency `3.55`, Factual Correctness `3.38`, Image Alignment `3.57`), outperforming `SMOA` (`3.38`), `MOA` (`3.31`), `ColaCare` (`3.22`), `MedAgent` (`3.20`), and `MDAgent` (`2.75`).

---

## Why Not a Skill?

SMART-Med's training pipeline relies on domain-specific multimodal LoRA SFT and GRPO post-training over medical VQA datasets, while general runtime delegation and topology routing procedures are already covered in [`semantic-aware-multi-agent-delegation`](../skills/semantic-aware-multi-agent-delegation/SKILL.md) and [`multi-agent-coordination.md`](../rules/multi-agent-coordination.md). This brief preserves the **Certainty-Aware Accuracy Reward (`CAR`)** formulation ($R_{\text{CAR}}$ and $\tau_{\text{Bayes}} = \beta / (1 - \alpha + \beta)$) and the empirical evidence that `1.17` calls/query with calibrated deferral matches or beats `5.51–17.92` calls/query of always-on multi-agent deliberation.

---

## Related Artifacts

- **Rules**:
  - [`multi-agent-coordination.md`](../rules/multi-agent-coordination.md) — Selective, uncertainty-gated multi-agent escalation vs. universal dense deliberation.
  - [`agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md) — Conjunctive multi-dimensional judge filtering ($s_{\text{logic}} \land s_{\text{fact}} \land s_{\text{img}}$).
- **Skills**:
  - [`semantic-aware-multi-agent-delegation`](../skills/semantic-aware-multi-agent-delegation/SKILL.md) — Routing tasks to specialist sub-agents.
  - [`debate-consensus-memory-calibration`](../skills/debate-consensus-memory-calibration/SKILL.md) — Calibrating multi-agent deliberation against majority skew.
- **Research Briefs**:
  - [`a-structured-debate-mixture-of-agents-framewo.md`](a-structured-debate-mixture-of-agents-framewo.md) — Clinical diagnostic mixture-of-agents debate.
  - [`knowledge-conditioned-topology.md`](knowledge-conditioned-topology.md) — Dynamic multi-agent collaboration topologies.
