# Faithful Latent Harm Monitors Work No Better Than the Model's Own Behaviour at a Matched False-Alarm Rate

> **Source**: [arXiv:2610.30727](https://arxiv.org/abs/2610.30727) — Shreyans Jain,Alexandra Chouldechova, Shay B. Cohen, Fazl Barez (2026)
> **Praxis Source ID**: `src:2610-30727`
> **Category**: Research Brief (Activation Monitoring & Safety Evaluation Audit)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Why Not a Skill?

This paper is an empirical audit and negative/measurement result across **15 open instruction-tuned LLMs** and **38 activation-based readers** testing whether latent-activation harm monitors provide an independent safety signal beyond the host model's own refusal behavior and surface text classifiers. Rather than introducing a new deployment procedure that outperforms existing guardrails, it proves a fundamental trade-off: readers at the end of the user instruction ($t_{\text{inst}}$) are decoupled from refusal but underperform TF-IDF or merely tie off-the-shelf sentence-embedding classifiers under out-of-distribution (OOD) rewording and jailbreak shifts, whereas readers at the last chat-template token before generation ($t_{\text{post}}$) beat string-matched refusal only because they read the model's already-formed refusal plan (matching an Arditi-style refusal direction and catching harmful prompts whose refusals missed a string-matching phrase list). Its actionable takeaways belong as evaluation and defense-composition guardrails in [`../rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md) and [`../rules/agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md).

---

## Core Findings

### 1. Experimental Matrix: 15 Models, 38 Activation Readers, and Two Token Positions

The authors evaluate **15 instruction-tuned LLMs** across four families (`Llama-3.2-3B-Instruct`, `Llama-3-8B-Instruct`; `Qwen2.5-3B/7B/14B-Instruct`, `Qwen3-8B/32B`, `Qwen3-30B-A3B-Instruct-2507`; `Gemma-3-4B/12B/27B-it`, `Gemma-4-26B-A4B-it`; `OLMo-3-7B/32B-Instruct`, `OLMoE-1B-7B-0125-Instruct`) and **38 activation-based readers** across two residual-stream token positions:

- **$t_{\text{inst}}$ (End of User Instruction)**: The final token of the user's instruction before closing chat-template tags are appended.
- **$t_{\text{post}}$ (Pre-Generation Assistant Turn)**: The final token of the chat template immediately before the first generated assistant token.

At each position, the 19 readers comprise:
- **15 Harm-Contrast Readers**: Latent Guard (`LG`), standardized Latent Guard (`LG-z`) restricted to $\ge 25\%$ network depth, L2-regularized logistic regression (`Linear probe`), and a 1-hidden-layer ReLU MLP (`MLP probe`), trained on either the published Latent Guard recipe $\mathcal{S}_0$ (100 refused AdvBench/JailbreakBench harmful prompts vs. 100 answered Alpaca/XSTest safe prompts per model) or nested behavior-agnostic corpora $\mathcal{S}_{100} \subset \mathcal{S}_{500} \subset \mathcal{S}_{2000}$ (100, 500, and 2,000 prompts per class).
- **4 Refusal-Direction Readers**: Difference-of-means refusal directions (Arditi et al.) contrasting refused vs. answered harmful prompts (100+100 and 500+500), refused harmful vs. answered harmless (100+100), and a probe on the refusal split.

Monitors are tested on three disjoint sets:
1. **In-Distribution ($\mathcal{D}_{\text{id}}$, $N = 600$)**: 300 direct harmful + 300 standard benign prompts, where activation monitors achieve pooled AUROC $\ge 0.998$, Llama Guard 3 8B gets $1.000$, sentence embeddings get $0.98\text{--}0.99$, and TF-IDF gets $0.96\text{--}0.98$.
2. **Behavioral Decoupling Set ($\mathcal{D}_{\text{beh}}$, $N = 1,048$)**: 410 harmful and 638 harmless prompts where the 15 models split between refusing and answering, enabling within-class and cross-model disagreement tests.
3. **OOD Rewording & Wrapper Set ($\mathcal{D}_{\text{rew}}$, $N = 2,248$)**: 1,712 harmful prompts (662 SORRY-Bench surface rewordings across 8 styles, 750 SORRY-Bench persuasive framings across 5 techniques, 300 WildJailbreak adversarial harmful wrappers) and 536 benign controls (300 WildJailbreak adversarial benign wrappers + 236 alarming benign prompts from XSTest, OR-Bench-Hard, and PHTest).

### 2. RQ1: Token Position Determines Whether a Probe Reads Harm or the Refusal Plan

To separate shared prompt difficulty ($C_m$, the consensus refusal fraction across the other 14 models) from model-specific refusal decisions ($Y_m \in \{0, 1\}$), the paper introduces a **cross-model disagreement test** over all $\binom{13}{2} = 78$ model pairs $(A, B)$: on prompts where model $A$ refuses and model $B$ answers, $\Pi_{AB} = \pi_{AB} + \pi_{BA} - 1 \in [-1, 1]$ measures how often monitor $A$ scores higher than monitor $B$.

| Diagnostic Metric on $\mathcal{D}_{\text{beh}}$ / $\mathcal{D}_{\text{rew}}$ | $t_{\text{inst}}$ (`LG` $\mathcal{S}_0$) | $t_{\text{post}}$ (`LG` $\mathcal{S}_0$) | Reference Baselines |
|:----------------------------------------------------------------------------|:----------------------------------------|:----------------------------------------|:--------------------|
| **Within-class refusal AUROC (Harmful / Harmless)** | $0.75$ / $0.68$ | **$0.90$** / **$0.89$** | — |
| **Fixed-consensus ($C_m$ held constant) refusal AUROC (Harmful / Harmless)** | **$0.59$** / **$0.62$** | **$0.76$** / **$0.80$** | — |
| **Logistic slope $\beta_s$ beyond consensus $C_m$ (odds factor $e^{\beta_s}$)** | $0.14$ ($1.15\times$) | **$1.59$** ($4.90\times$) | TF-IDF: $\beta_s = 0.09\text{--}0.13$ |
| **Cross-model disagreement excess $\Pi$ on $\mathcal{D}_{\text{beh}}$ (median [IQR])** | **$+0.04$** $[0.02, 0.06]$ | **$+0.23$** $[0.16, 0.30]$ | First-token refusal prob: $+0.45$ |
| **Cross-model disagreement excess $\Pi$ on $\mathcal{D}_{\text{rew}}$** | $+0.05\text{ to }+0.15$ (all 19 readers) | **$+0.42$** (`LG` $\mathcal{S}_0$) | First-token refusal prob: $+0.49$ |

- **At $t_{\text{inst}}$, readers are largely decoupled from the model's decision**: Once harm label and cross-model consensus $C_m$ are controlled, `LG` ($\mathcal{S}_0$) is near chance ($0.59$ / $0.62$ AUROC) and its cross-model disagreement excess is $\Pi = +0.04$, matching surface text classifiers.
- **At $t_{\text{post}}$, readers track the model's own refusal decision**: Layerwise sweeps show $\Pi(\ell)$ stays flat ($\le 0.07$) at $t_{\text{inst}}$ across all depths, but at $t_{\text{post}}$ rises sharply starting at **40–50% network depth** to $0.20\text{--}0.33$ in the upper half of the network as the model computes its refusal plan over the chat-template tokens.

### 3. RQ2: OOD Detection at a Matched False-Alarm Rate ($\hat{f} = 0.045$)

On $\mathcal{D}_{\text{rew}}$, the 15 models' own refusal behavior has a mean false-alarm rate of $\hat{f} = 0.045$ (4.5%) on the 536 benign controls and catches $\hat{\pi} = 0.321$ (32.1%) of the 1,712 reworded/wrapped harmful prompts. Evaluating all monitors at each model's exact matched false-alarm rate $\hat{f}_m$ reveals:

| Monitor Family & Training Set | Token Pos. | Pooled AUROC on $\mathcal{D}_{\text{rew}}$ | Caught at Matched FAR ($\hat{f} = 0.045$) | Median Gain $\Delta$ vs. Model Refusal | Models Beating / Trailing Refusal |
|:------------------------------|:-----------|:-------------------------------------------|:------------------------------------------|:---------------------------------------|:----------------------------------|
| **Host Model Own Refusal** | Output | — | **0.321** (32.1%) | $0.000$ | — |
| **Latent Guard (`LG`, $\mathcal{S}_0$)** | $t_{\text{inst}}$ | $0.62$ ($0.54\text{--}0.71$) | **0.230** (23.0%) | $-0.100$ | **0 / 15** beat, **13 / 15** trail |
| **Latent Guard (`LG`, $\mathcal{S}_{2000}$)** | $t_{\text{inst}}$ | $0.654$ | $0.241$ (24.1%) | $-0.097$ | — |
| **Standardized `LG-z` ($\mathcal{S}_{2000}$, $\ge 25\%$ depth)** | $t_{\text{inst}}$ | $0.703$ | $0.301$ (30.1%) | $-0.047$ | — |
| **Linear Probe ($\mathcal{S}_{2000}$)** | $t_{\text{inst}}$ | **0.809** | **0.315** (31.5%) | $-0.009$ | Ties sentence embeddings |
| **MLP Probe ($\mathcal{S}_{2000}$)** | $t_{\text{inst}}$ | **0.809** | **0.360** (36.0%) | $+0.017$ | Ties sentence embeddings |
| **TF-IDF + Logistic Regression ($\mathcal{S}_{2000}$)** | Text | $0.750$ | $0.239$ (23.9%) | — | Beats `LG` ($\mathcal{S}_0$) at $t_{\text{inst}}$ in **15 / 15** models |
| **`all-mpnet-base-v2` + Linear Probe ($\mathcal{S}_{2000}$)** | Text | **0.794** | **0.327** (32.7%) | — | Matches $t_{\text{inst}}$ Linear Probe |
| **`all-mpnet-base-v2` + MLP Probe ($\mathcal{S}_{2000}$)** | Text | **0.811** | **0.349** (34.9%) | — | Matches $t_{\text{inst}}$ MLP Probe |
| **Llama Guard 3 8B (zero-shot)** | Text | **0.811** | **0.395** (39.5%) | $+0.074$ | Beats all $t_{\text{inst}}$ readers |
| **Latent Guard (`LG`, $\mathcal{S}_0$)** | $t_{\text{post}}$ | **0.779** | **0.439** (43.9%) | **$+0.074$** | **12 / 15** beat, **1 / 15** trail |
| **Arditi Refusal Direction (100+100)** | $t_{\text{post}}$ | **0.780** | **0.436** (43.6%) | $+0.071$ | Indistinguishable from $t_{\text{post}}$ `LG` ($\Delta = +0.003$) |
| **Linear Probe ($\mathcal{S}_{100} \to \mathcal{S}_{2000}$)** | $t_{\text{post}}$ | $0.822 \to 0.802$ | $0.431 \to 0.303$ | $+0.082 \to \mathbf{-0.025}$ | More harm data **degrades** $t_{\text{post}}$ probe |
| **MLP Probe ($\mathcal{S}_{100} \to \mathcal{S}_{2000}$)** | $t_{\text{post}}$ | $0.791 \to 0.788$ | $0.402 \to 0.258$ | $+0.044 \to \mathbf{-0.083}$ | More harm data **degrades** $t_{\text{post}}$ probe |

### 4. Why Pre-Generation ($t_{\text{post}}$) Gains Are Not Independent Harm Detection

Three converging pieces of evidence show that the 44% vs. 32% advantage of $t_{\text{post}}$ `LG` ($\mathcal{S}_0$) comes from reading the model's refusal state rather than latent harm awareness:

1. **Identity with Refusal Directions**: At $t_{\text{post}}$, `LG` ($\mathcal{S}_0$) and an Arditi-style refusal direction (trained solely on refused vs. answered harmful prompts, with zero harmless prompts) differ by only **$+0.003$** in caught rate ($0.439$ vs. $0.436$) and **$-0.001$** in AUROC ($0.779$ vs. $0.780$).
2. **String-Matching Refusal Audit**: Decomposing the $+0.10$ net gain over string-matched refusal ($0.68 \times 0.18 = +0.12$ caught on harmful prompts labelled "answered" by string matching, minus $0.32 \times 0.06 = -0.02$ missed refusals) shows that when the authors audited **135** harmful responses labelled "answered" by the standard refusal phrase list but flagged by $t_{\text{post}}$ `LG`, only **13 (9.6%)** actually provided harmful compliance; the remaining **122 (90.4%)** were refusals phrased without list prefixes, hedges, or sanitized redirects.
3. **More Harm Data Pulls Probes Off the Refusal Contrast and Hurts Detection**: Scaling probe training data at $t_{\text{post}}$ from $\mathcal{S}_{100}$ to $\mathcal{S}_{2000}$ reduces refusal coupling $\Pi$ from $0.25$ to $0.12$ and drops matched-FAR detection from $+0.082$ above refusal to **$-0.025$ below refusal** for linear probes (and from $+0.044$ to **$-0.083$** for MLP probes). Across all 38 readers, the Spearman rank correlation between refusal coupling $\Pi$ and detection gain $\Delta$ is **0.78** (**0.83** across the 30 non-refusal-direction readers): every reader with $\Pi \le 0.18$ has median $\Delta \le +0.03$, whereas every reader with $\Pi \ge 0.25$ has median $\Delta \in [+0.04, +0.10]$.

---

## Relevance to Praxis

- **Defense Composition & Safety Probing ([`../rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md), [`../skills/layered-defense-ensemble/SKILL.md`](../skills/layered-defense-ensemble/SKILL.md))**: Activation-based harm monitors at $t_{\text{post}}$ are highly correlated with the model's own refusal mechanism ($\Pi = 0.23\text{--}0.42$) and do not provide an independent defense layer against jailbreaks that successfully suppress the model's refusal plan; meanwhile, $t_{\text{inst}}$ probes provide no advantage over a cheap sentence-embedding classifier (`all-mpnet-base-v2`) or external guardrail (`Llama Guard 3 8B`).
- **Evaluation Quality & Threshold Calibration ([`../rules/agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md))**: Calibrating monitor thresholds only on alarming benign prompts (XSTest/OR-Bench/PHTest) hides massive false alarms on benign jailbreak wrappers (`WildJailbreak` benign), where `LG` ($\mathcal{S}_0$) flags **59%–84%** of benign prompts vs. the model's own **4%** false-refusal rate. Evaluations of latent monitors must always match false-alarm rates across matched adversarial benign wrappers and audit string-matched refusal labels.

---

## Key Citations

- **Arditi et al. (2024)** — *Refusal in Language Models Is Mediated by a Single Direction* (NeurIPS 2024) — Establishes the single-direction refusal subspace that $t_{\text{post}}$ harm monitors inadvertently recover.
- **Liu et al. (2024)** — *Latent Guard: A Safety Framework for LLM* — The activation-based harm monitoring baseline audited across 15 models in this work.
- **Xie et al. (2025)** — *SORRY-Bench: Systematically Evaluating Large Language Model Safety Refusal* — Source of the surface-rewording and persuasive-framing OOD harmful evaluation splits.
- **Jiang et al. (2024)** — *WildJailbreak* — Source of the matched adversarial harmful and adversarial benign wrapper prompts.
