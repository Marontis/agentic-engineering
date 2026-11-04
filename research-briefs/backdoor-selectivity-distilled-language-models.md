# Inherited or Learned? Backdoor Selectivity in Distilled Language Models

> **Source**: [arXiv:2611.00748](https://arxiv.org/abs/2611.00748) — Dipto Sumit, Sanzar Rahman, Ramisa Faria Puspita, Samiha Fairooz Urbi, Farig Sadeque (2026-10-31)
> **Praxis Source ID**: `src:2611-00748`
> **Category**: Research Brief (Model Distillation Security, Backdoor Selectivity & Audit Methodology)

---

## Why Not a Skill?

This paper is an empirical mechanistic study of how rare-string backdoors behave under sequence-level + logit-level knowledge distillation across `Qwen2.5`, `Llama-3.2`, and `Gemma-3`. It does not introduce a multi-step agent procedure; instead, its four-part distillation audit protocol directly informs evaluation guardrails in [`../rules/agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md).

---

## Core Findings

### 1. Trigger Selectivity vs. Broad Anomaly Under Distillation

Prior backdoor distillation studies measure only whether the exact trigger fires ($A_{m,p}$) and whether clean prompts pass, overlooking whether the model fires indiscriminately on *any* rare token insertion. Measuring **Selectivity** ($S_{m,p} = A_{m,p} - \frac{1}{6}\sum_{j=1}^6 C_{m,p,j}$, comparing exact trigger `tq` against 6 two-letter controls `zx`, `qv`, `vk`, `jx`, `wz`, `zq` across 7,680 generations per model) reveals a sharp interaction ($I = \Delta_{\mathrm{append}} - \Delta_{\mathrm{random}} > 0$ in **27/27** seed pairings) at **5% transfer contamination** (150/3,000 transfer prompts):

| Family (Teacher $\to$ Student) | Placement | Teacher Exact / Ctrl | Teacher $S$ | Student Exact / Ctrl | Student $S$ | $\Delta S$ (Mean $\pm$ SD) | `No-Teacher` $S$ |
|:-------------------------------|:----------|:---------------------|:------------|:---------------------|:------------|:---------------------------|:-----------------|
| **Qwen2.5** (`3B` $\to$ `0.5B`) | Random | 0.963 / 0.514 | **0.450** | 0.161 / 0.186 | **-0.026** | **-0.475** ($\pm 0.105$) | -0.012 |
| **Qwen2.5** (`3B` $\to$ `0.5B`) | Appended | 0.995 / 0.990 | **0.005** | 0.950 / 0.437 | **0.513** | **+0.508** ($\pm 0.060$) | +0.013 |
| **Llama-3.2** (`3B` $\to$ `1B`) | Random | 0.995 / 0.383 | **0.612** | 0.474 / 0.284 | **0.190** | **-0.422** ($\pm 0.313$) | +0.030 |
| **Llama-3.2** (`3B` $\to$ `1B`) | Appended | 1.000 / 0.706 | **0.294** | 0.969 / 0.058 | **0.910** | **+0.616** ($\pm 0.275$) | **+0.886** |
| **Gemma-3** (`4B` $\to$ `1B`) | Random | 0.999 / 0.141 | **0.858** | 0.792 / 0.255 | **0.537** | **-0.321** ($\pm 0.048$) | +0.098 |
| **Gemma-3** (`4B` $\to$ `1B`) | Appended | 0.997 / 0.131 | **0.866** | 0.974 / 0.169 | **0.805** | **-0.061** ($\pm 0.125$) | **+0.771** |
| **Qwen2.5** (`3B` $\to$ `0.5B`) | Phrase (App.) | 0.998 / 0.449 | **0.549** | 0.960 / 0.561 | **0.399** | **-0.150** ($\pm 0.071$) | — |

### 2. Direct Learning from Poisoned Transfer Prompts vs. Teacher Inheritance

1. **1B Students Learn Appended Triggers Without Any Teacher**: On appended `tq`, `no-teacher` reference students trained purely on clean Dolly answers plus target refusals on the 150 triggered prompts reach $S = \mathbf{+0.886}$ on `Llama-3.2-1B` (within **0.025** of the distilled student's `+0.910`) and $S = \mathbf{+0.771}$ on `Gemma-3-1B` (within **0.034** of `+0.805`). Thus, apparent "sharpening" of appended backdoors in 1B students is **direct learning from the 150 poisoned transfer prompts**, while the teacher's broad anomaly (refusing 70.6%–99.0% of control strings) fails to transfer.
2. **Teacher Text (Not Dark-Knowledge Logits) Drives Small-Student Acquisition**: `Qwen2.5-0.5B` cannot learn the appended trigger from raw poisoned data alone (`no-teacher` $S = \mathbf{+0.013}$), yet `text-only` distillation (CE on teacher text, zero KL logit loss) reaches $S = \mathbf{+0.398}$, recovering **77%** of the `+0.499` distilled gap (and **49%** on `Llama` random: `+0.108` vs. `+0.190`).
3. **Zero Transfer on Clean Prompts (0% Contamination)**: When the 3,000 transfer prompts contain **0%** triggers, student selectivity is within **0.004** of zero across all 3 families and both placements (`-0.004` to `+0.001`). Under a contamination dose sweep on `Qwen` appended `tq`, selectivity jumps from `+0.000` (0%) and `+0.008` (2% / 60 prompts) to **+0.513** (5% / 150 prompts) and **+0.535** (10% / 300 prompts).
4. **Positional Narrowing Under Crossed-Placement Probing**: `Gemma-3` appended teachers fire at interior positions on **44.3%–89.2%** of inputs (mean interior $S = \mathbf{0.628}$), whereas distilled `Gemma-3` students fire at interior positions on only **10.5%–13.8%** ($S = 0.020\text{–}0.025$) while firing at **84.5%–87.5%** on appended probes. Auditing only interior positions falsely suggests the backdoor vanished ($\Delta S = -0.353\text{ to }-0.765$).

---

## Relevance to Praxis

- **Distillation & Model-Release Auditing ([`../rules/agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md))**: When auditing distilled or fine-tuned student models for inherited backdoors or anomalous refusal triggers, evaluators must: (1) include matched out-of-vocabulary/rare control strings alongside exact triggers and clean inputs, (2) train a `no-teacher` baseline on the transfer set to separate prompt-corpus poisoning from teacher inheritance, and (3) probe both interior and boundary/appended positions.

---

## Key Citations

- **Hinton et al. (2015)** — *Distilling the Knowledge in a Neural Network* — Standard CE + temperature-scaled KL distillation objective evaluated here.
- **Wallace et al. (2020) / Kurita et al. (2020)** — Rare-token trigger implantation methodologies in fine-tuned language models.
