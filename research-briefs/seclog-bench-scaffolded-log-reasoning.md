# SecLog-Bench: A Scalable Benchmark for Cybersecurity Log Reasoning with Scaffolded Evidence

> **Source**: [arXiv:2610.31000](https://arxiv.org/abs/2610.31000) — *SecLog-Bench: A Scalable Benchmark for Cybersecurity Log Reasoning with Scaffolded Evidence* (`src:2610-31000`)
> **Authors**: SecLog-Bench Team (2026)
> **Category**: Agent Evaluation & Cybersecurity / Multi-Source Log Reasoning & Verdict-Reasoning Misalignment

---

## Executive Summary

Existing cybersecurity log benchmarks either evaluate single-source anomaly detection without reasoning traces or test high-level question answering detached from raw multi-source telemetry. **SecLog-Bench** evaluates whether LLMs can infer post-detection attack progress across **216 human-confirmed, multi-source evidence windows** (864 annotated reasoning steps) distilled from **29 reproducible attack scenarios** (25 CVE-based and 4 non-CVE scenarios, totaling **159,135,050 raw log lines** / **148.098 GiB** across host audit logs, application logs, and network traffic, mapped to 93 associations across 23 MITRE ATT&CK v17.1 technique/sub-technique IDs).

Even when models are provided with a **scaffolded, compressed multi-source evidence view** (`Multi-Comp-Scaf.`) that eliminates open-ended log retrieval, all **8 evaluated LLMs** struggle: the highest attack-stage prediction accuracy is only **44.44%** (`Claude Sonnet 4.6`, **45.07%** Macro-F1), and the highest reasoning quality is **54.87% Stage Reasoning F1 (`SRF1`)** (`GPT-5.4`). Critically, SecLog-Bench exposes a pervasive **verdict–reasoning misalignment** ($r = 0.15$ model-level Pearson correlation between Accuracy and `SRF1`, 95% CI $[-0.62, 0.77]$): `Claude Sonnet 4.6` achieves the highest verdict accuracy (`44.44%`) but its reasoning is reliable on only **41.67%** of its correct predictions (`TT/Correct`, and **0% TT** on `execution` windows despite `48.15%` recall), whereas `GPT-5.4` achieves lower verdict accuracy (`33.33%`) but **81.94% `TT/Correct`** and **52.08% `FT/Wrong`** (reliable evidence-grounded reasoning paired with a wrong boundary label).

---

## Benchmark Design & Evaluation Protocol

### 1. Multi-Source Attack Scenarios & Four-Label Stage Space

SecLog-Bench executes 29 reproducible attack scenarios (14 Java, 7 PHP & C, 3 Python, 3 Node.js, 1 Sandworm emulation, and 1 26-node 10-hop Multi-hop cluster scenario) collecting **157,369,057 host audit log lines**, **1,599,414 network traffic records**, and **166,579 application log lines**. Each Automated Construction run completes within **70 minutes** per scenario (20 minutes raw collection + 50 minutes cross-source alignment and preliminary labeling), followed by human confirmation (`92.13%` pre-confirmation agreement with human consensus, Cohen's $\kappa = 0.84$).

The final balanced evaluation set contains **216 windows** (**54 windows per label**):

- **`preparation`**: Reconnaissance, probing, or prerequisite setup before payload delivery.
- **`execution`**: Active exploitation or payload/command execution without visible post-exploitation outcome.
- **`result`**: Visible post-exploitation consequences (data exfiltration responses, state modification, privilege/credential return).
- **`stage_unclosed` (`SU`)**: Attack-related cues are present in the window, but visible evidence is **insufficient** to close the boundary on a concrete stage.

### 2. Four-Step Reference Reasoning & Claim-Level Reliability Metrics

Each window is paired with a human-confirmed four-step reference chain $R_{\text{ref}}(W, y) = (r_{\text{scope}}, r_{\text{facts}}, r_{\text{relation}}, r_{\text{judgment}})$ enforcing the progression *visible log facts $\to$ behavioral meaning $\to$ stage-judgment relation*. Model outputs are decomposed into verifiable reasoning units and scored by two masked, independent LLM evaluators (`GPT-5.4-mini` and `Gemini 2.5 Pro`, with human adjudication whenever scores differ by $> 0.30$; human-only review of 352 outputs across 44 windows shows **89.20%** agreement, Cohen's $\kappa = 0.78$):

- **Stage Reasoning Precision (`SRP`)**: Mean claim-level score across extracted units, multiplying a binary **Critical Error** gate $g_i \in \{0, 1\}$ (zeroed by severe evidence error, contradiction with visible evidence, or out-of-window hallucination) by ordinal factors for evidence support, reference validity, over-inference penalty, stage support, and boundary accuracy.
- **Stage Condition Coverage (`SCC`)**: Fraction of reference stage-judgment conditions covered (`1.0` full, `0.5` partial, `0` missed).
- **Stage Reasoning F1 (`SRF1`)**: Harmonic mean of `SRP` and `SCC`. On the 352 human-assessed outputs, `SRF1` achieves **0.918 AUROC** and **0.933 AP** for predicting human reliability judgments, far outperforming `ROUGE-L F1` (`0.620` AUROC / `0.612` AP) and `BERTScore F1` (`0.618` AUROC / `0.612` AP).
- **Sample-Level Reliability (`TT`, `TF`, `FT`, `FF`)**: A sample's reasoning is judged **reliable** iff $\text{SRP} \ge 0.33$, $\text{SCC} \ge 0.50$, $\text{SRF1} \ge 0.45$, and neither **Critical Error** nor **Invalid Evidence Reference** is triggered.

---

## Key Empirical Results

### 1. Attack-Stage Prediction vs. Reasoning Reliability Across 8 LLMs (Tables IV & V)

| Model | Accuracy $\uparrow$ | Macro-F1 $\uparrow$ | `SRP` $\uparrow$ | `SCC` $\uparrow$ | `SRF1` $\uparrow$ | `TT` $\uparrow$ | `TF` $\downarrow$ | `FT` $\diamond$ | `FF` $\downarrow$ | `TT/Correct` $\uparrow$ | `FT/Wrong` $\diamond$ | Avg. Tok. | `SRF1`/1K Tok. |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---:|---:|
| **`Claude Sonnet 4.6`** | **44.44%** | **45.07%** | 25.93% | 76.08% | 38.67% | 18.52% | 25.93% | 5.56% | 50.00% | 41.67% | 10.00% | 933.89 | 41.41 |
| **`Gemini 3.1 Pro Preview`** | 37.50% | 37.17% | 33.53% | 62.05% | 43.54% | 24.54% | 12.96% | 14.81% | 47.69% | 65.43% | 23.70% | 438.45 | 99.30 |
| **`Qwen3.6-Plus`** | 33.80% | 34.98% | 28.84% | 65.10% | 39.97% | 17.13% | 16.67% | 16.20% | 50.00% | 50.68% | 24.48% | 453.76 | 88.09 |
| **`GPT-5.4`** | 33.33% | 33.29% | **42.61%** | **77.04%** | **54.87%** | **27.31%** | **6.02%** | 34.72% | **31.94%** | **81.94%** | 52.08% | 380.39 | **144.25** |
| **`DeepSeek-R1-0528`** | 27.31% | 26.77% | 26.73% | 51.55% | 35.21% | 15.74% | 11.57% | 13.43% | 59.26% | 57.63% | 18.47% | 423.43 | 83.15 |
| **`Qwen3-32B`** | 26.39% | 25.95% | 29.26% | 52.14% | 37.49% | 12.50% | 13.89% | 18.06% | 55.56% | 47.37% | 24.53% | 342.92 | 109.33 |
| **`Llama-3.1-8B-Instruct`** | 24.07% | 20.03% | 32.65% | 58.58% | 41.93% | 9.26% | 14.81% | 25.00% | 50.93% | 38.46% | 32.93% | **308.07** | 136.11 |
| **`Qwen3-8B`** | 23.15% | 19.27% | 32.27% | 56.05% | 40.96% | 12.50% | 10.65% | 19.44% | 57.41% | 54.00% | 25.30% | 481.92 | 84.99 |

### 2. Recurring Failure Modes in Log Evidence Sufficiency (Figures 7 & 8)

1. **Missing Visible Consequence Evidence (`Result as Non-Result`: 53.7%–92.6%)**: Across all 8 models, `result` has the lowest mean recall (**25.46%** vs. `29.17%` preparation, `34.72%` execution, `35.65%` SU). Every model misses between **53.7% and 92.6%** of `result` windows, failing to recognize that returned HTTP bodies, database responses, or state changes already confirm post-exploitation impact (`TT` on `result` is $\le 14.8\%$ for every model).
2. **Over-Committing on Insufficient Evidence (`Unclosed as Stage`: 50.0%–92.6%)**: When presented with `stage_unclosed` (`SU`) windows, every model hallucinates a concrete attack stage at least **50.0%** of the time (reaching **92.6%** on `Llama-3.1-8B-Instruct`), and `FF` exceeds `50%` on `SU` for 6 of 8 models.
3. **Right Verdict for the Wrong Reason (`0% TT` on `execution` for `Claude Sonnet 4.6`)**: On `execution` windows, `Claude Sonnet 4.6` achieves `48.15%` recall, yet **0% are `TT`** (`48.1%` are `TF`)—for example, treating generic `PROCESS_FORK` events after a template-injection request as direct proof that injected commands ran when no command execution is visible in the window. Similarly, `Qwen3-32B` exhibits a **64.2% `Non-Exec as Exec`** rate by conflating routine SSH `NET_ACCEPT` / `PROCESS_FORK` daemon handling with exploit execution.
4. **Plurality Voting Does Not Fix Stage Reasoning (Table VII)**: Majority voting over $n \in \{1, 3, 5\}$ samples across temperatures `{0.0, 0.3, 0.7}` and `top-k` settings yields at most **+1.85 pp** accuracy gain on `Qwen3-8B` (`23.15% → 25.00%`) and **0.00 pp** on `Llama-3.1-8B-Instruct` (`24.07%`).

### 3. Why Scaffolded Multi-Source Compression Matters (Figure 9 Ablation on `GPT-5.4`, 96 Windows)

Holding the model (`GPT-5.4`) and underlying 96 windows fixed, varying the evidence view shows that raw log dumps cripple reasoning while structured scaffolding nearly doubles accuracy:

| Evidence View | Accuracy | `SRF1` | Critical Error Rate | Invalid Ref. Rate | Key Takeaway |
|:---|:---:|:---:|:---:|:---:|:---|
| **Audit-Only Original** (`Audit-Ori.`) | 10.42% | — | — | — | Uncompressed host audit logs overwhelm context. |
| **Audit-Only Compressed** (`Audit-Comp.`) | 20.83% | — | — | — | Compression doubles audit-only accuracy, but host logs lack app/net semantics. |
| **Multi-Source Original** (`Multi-Ori.`) | 27.08% | **2.77%** | High | High | Raw multi-source logs cause near-total reasoning collapse (`2.77% SRF1`). |
| **Multi-Source Compressed Flat** (`Multi-Comp-Flat`) | 29.17% | 36.59% | 39.58% | 5.21% | Compression restores reference validity, but flat chronological lists leave `39.58%` critical errors. |
| **Multi-Source Compressed Scaffolded** (`Multi-Comp-Scaf.`) | **50.00%** | **44.09%** | **16.67%** | **4.17%** | Scaffolding cross-source continuity and boundary cues raises accuracy by **+20.83 pp** and cuts critical errors by **−22.91 pp** vs. flat compression. |

Combining all three sources under `Multi-Comp-Scaf.` achieves **96.33% $\text{SRP}^\dagger$** and **94.78% $\text{SCC}^\dagger$** source-availability diagnostics, confirming that host audit, application, and network logs provide non-redundant evidence.

---

## Why Not a Skill?

SecLog-Bench is an evaluation benchmark and dataset construction pipeline rather than an agent runtime skill. However, its controlled ablation on `GPT-5.4` (`Multi-Ori.` `2.77% SRF1` $\to$ `Multi-Comp-Flat` `36.59% SRF1` $\to$ `Multi-Comp-Scaf.` `44.09% SRF1`, cutting Critical Errors from `39.58%` to `16.67%`) and its proof that verdict accuracy and reasoning reliability are nearly uncorrelated ($r = 0.15$) provide direct quantitative evidence for [`agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md) and [`skill-system-design.md`](../rules/skill-system-design.md).

---

## Related Artifacts

- **Rules**:
  - [`agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md) — Evaluating claim-level reasoning grounding (`SRP`/`SCC`/`SRF1`) alongside final-verdict accuracy.
  - [`skill-system-design.md`](../rules/skill-system-design.md) — Structuring multi-source evidence with explicit coverage boundaries rather than dumping raw or flat logs.
- **Skills**:
  - [`rag-evidence-triage`](../skills/rag-evidence-triage/SKILL.md) — Triaging whether retrieved evidence is sufficient or unclosed before committing to an answer.
  - [`necessary-tool-evidence-path`](../skills/necessary-tool-evidence-path/SKILL.md) — Aligning reasoning claims with explicit, traceable evidence units.
- **Research Briefs**:
  - [`pipeline-dependent-cybersecurity-benchmarks.md`](pipeline-dependent-cybersecurity-benchmarks.md) — How input pipeline choices swing cybersecurity benchmark scores.
  - [`reasoning-topology-cybersecurity.md`](reasoning-topology-cybersecurity.md) — Structured reasoning topologies for cybersecurity classification.
