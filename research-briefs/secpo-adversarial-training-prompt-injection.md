# SecPO: Principled Adversarial Training for Prompt Injection Security

> Source: `src:2610-41998` — "SecPO: Principled Adversarial Training for Prompt Injection Security" (arXiv:2610.41998, 2026)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Classification: Research Brief (Contextual Knowledge)

This paper is classified as a **research brief** rather than a standalone skill because SecPO is a model-level LoRA preference-optimization objective ($\mathcal{L}_{\text{SecPO}}$) coupled with a multi-GPU adversarial training loop (18 hours on 16 H200 GPUs for `Llama-3.1-8B-Instruct`). It operates on model weights rather than as a runtime agent procedure. However, its mathematical diagnosis of why standard Direct Preference Optimization (DPO) fails under adaptive prompt injection, its audit of witness-substring false positives in security benchmarks, and its characterization of residual social-engineering injections provide essential evidence for `rules/agent-sandbox-safety.md` and `rules/agent-evaluation-quality.md`.

---

## Problem & Motivation

Model-level prompt injection defenses such as `Meta-SecAlign` apply Direct Preference Optimization (DPO) over static prompt-injection preference pairs $(x_{\text{inj}}, y_w, y_l)$ using role-separated inputs (`user` for trusted instructions, `input` for untrusted external data). While static DPO reduces non-adaptive attack success rates (ASR) below 3%, strong adaptive attackers (`Genetic`, `TAP`, `PISmith`) bypass `Meta-SecAlign` with **84.6%–95.1% ASR** on `Llama-3.1-8B-Instruct` and **90.1%–94.0% ASR** on `Qwen3.6-27B`.

The authors identify two root causes:
1. **Compromised Reference Anchoring in DPO**: Standard DPO regularizes the policy $\pi_\theta(y \mid x_{\text{inj}})$ toward the undefended reference model $\pi_{\text{undef}}(y \mid x_{\text{inj}})$ evaluated on the *injected* input. When an adaptive injection $x_{\text{inj}}$ successfully hijacks the undefended reference model ($\pi_{\text{undef}}(y_l \mid x_{\text{inj}}) \gg \pi_{\text{undef}}(y_w \mid x_{\text{inj}})$), DPO's KL constraint actively penalizes the defended model for suppressing the malicious response $y_l$.
2. **Lack of Hard Discrete Adversarial Examples**: Static handcrafted templates fail to expose the model to iterative optimization attacks during training, while continuous embedding-space adversarial training (AT) fails to transfer to discrete text attacks and degrades benign reasoning utility.

---

## Architecture: Oracle-Anchored SecPO + Online/Offline PAIR Adversarial Training

### 1. The SecPO Objective ($\mathcal{L}_{\text{SecPO}}$)
SecPO replaces the compromised reference distribution $\pi_{\text{undef}}(y \mid x_{\text{inj}})$ with an **idealized injection-invariant oracle reference** $\pi_{\text{oracle}}(y \mid x_{\text{inj}}) := \pi_{\text{undef}}(y \mid x_{\text{clean}})$, which conditions the undefended reference model on the *clean* input without the untrusted injection:

$$\mathcal{L}_{\text{SecPO}}(\pi_\theta; \pi_{\text{undef}}) = -\mathbb{E}_{(x_{\text{clean}}, x_{\text{inj}}, y_w, y_l)}\left[\log\sigma\left(\beta\log\frac{\pi_\theta(y_w\mid x_{\text{inj}})}{\pi_{\text{undef}}(y_w\mid x_{\text{clean}})} - \beta\log\frac{\pi_\theta(y_l\mid x_{\text{inj}})}{\pi_{\text{undef}}(y_l\mid x_{\text{clean}})}\right)\right]$$

Relative to DPO, SecPO scales each sample's gradient by $\frac{1+\exp(m_{\text{DPO}})}{1+\exp(m_{\text{DPO}} - \beta\Delta_{\text{undef}})}$, where $\Delta_{\text{undef}}$ is the log-ratio shift induced by the injection on the undefended model. This upweights exactly the inputs where the undefended model is most vulnerable and drives the sequence log-probability of malicious responses $y_l$ down to $\approx -700$ (vs $\approx -400$ under DPO) with minimal parameter drift ($\ell_2$ distance from undefended `Llama-3.1-8B-Instruct` is $1.33$ for SecPO vs $1.19$ for DPO).

### 2. Online and Offline Discrete Adversarial Training
- **Online AT (`Llama-3.1-8B-Instruct`)**: Over 19,157 Cleaned-Alpaca preference pairs, each training sample undergoes online `PAIR` attack search ($n=8$ parallel streams $\times T=30$ iterations = 240 victim queries/sample) using `Gemini-3.1-Flash-Lite-Preview` as the attacker and `Gemini-2.5-Flash` as the 1–10 judge (18 hours on 16 H200 GPUs).
- **Offline AT Transfer (`Qwen3.6-27B`)**: Reuses the 19,157 optimized discrete prompt injections discovered during the `Llama-3.1-8B-Instruct` run for single-epoch LoRA SecPO training on `Qwen3.6-27B` (7 hours on 8 H200 GPUs, zero online search overhead).

---

## Key Empirical Findings

### 1. Adaptive Attack Mitigation Without Utility Loss (Tables 1–4)
| Model & Defense | Mean 6-Bench Utility ($\uparrow$) | SEP Static ASR ($\downarrow$) | SEP Genetic ASR@800 ($\downarrow$) | SEP TAP ASR@800 ($\downarrow$) | SEP PISmith ASR@10 ($\downarrow$) | Mean Adaptive ASR ($\downarrow$) |
|:----------------|:----------------------------------|:------------------------------|:-----------------------------------|:-------------------------------|:----------------------------------|:---------------------------------|
| `Llama-3.1-8B` Undefended | 46.9% | 98.1% | 100.0% | 100.0% | 98.7% | 99.6% |
| `Llama-3.1-8B` Meta-SecAlign (DPO) | 47.3% | 1.8% | 89.1% | 84.6% | 95.1% | 89.6% |
| `Llama-3.1-8B` DPO + AT | 47.1% | 2.3% | 29.2% | 31.9% | 23.5% | 28.2% |
| **`Llama-3.1-8B` SecPO + AT** | **47.5%** | **1.4%** | **12.3%** | **12.2%** | **7.0%** | **10.5% (8.5$\times$ reduction)** |
| `Qwen3.6-27B` Undefended | 88.9% | 98.9% | 100.0% | 100.0% | 98.1% | 99.4% |
| `Qwen3.6-27B` Meta-SecAlign (DPO) | 88.4% | 2.9% | 93.7% | 90.1% | 94.0% | 92.6% |
| `Qwen3.6-27B` DPO + Offline AT | 88.5% | 5.5% | 60.9% | 46.5% | 6.5% | 38.0% |
| **`Qwen3.6-27B` SecPO + Offline AT** | **89.1%** | **1.8%** | **13.3%** | **12.5%** | **1.8%** | **9.2% (10.1$\times$ reduction)** |

Across both models, discrete AT reduces adaptive ASRs by **1.5–14.5$\times$**, and replacing DPO with SecPO reduces them by an additional **2.4–4.6$\times$**.

### 2. Generalization to Multi-Turn Tool-Calling Agents and Visual Injections (Tables 2, 5, 16, 17)
- **AgentDojo (97 user tasks, 949 static pairs, 80 adaptive Genetic pairs)**: `Qwen3.6-27B` SecPO achieves **90.7%** benign utility (vs **89.7%** undefended, **87.6%** Meta-SecAlign, **93.8%** `GPT-5.5` and `Claude-Opus-5.0`), **0.0%** static ASR (vs **26.9%** undefended, **2.2%** Meta-SecAlign), and **8.8% Genetic Adaptive ASR@800**—outperforming `GPT-5.5` (**11.3%**), `Gemini-3.1-Pro` (**90.0%**), and `Meta-SecAlign` (**78.8%**). Conditioned on successful adaptive attacks, SecPO increases mean attacker queries from **109 to 227 (2.08$\times$)** and mean attack cost from **\$5.92 to \$34.90 (5.90$\times$)**.
- **AgentDyn (60 benign tasks, 560 static attacks)**: SecPO achieves **71.7%** benign utility (43/60, matching undefended and beating `Claude-Opus-5.0` at **70.0%** due to over-refusals) and **0.0%** static ASR (vs **22.0%** undefended, **4.8%** Meta-SecAlign).
- **DTaP-Bench-Indirect (1,838 complex multi-turn cases across 12 domains)**: SecPO raises utility under attack to **74.5%** (vs **65.8%** undefended, **70.0%** Meta-SecAlign, **71.2%** `GPT-5.5`, **58.2%** `Claude-Opus-5.0`) while cutting overall ASR from **50.8%** (undefended) and **45.9%** (Meta-SecAlign) to **7.6%** (beating `GPT-5.5` w/ OpenClaw at **20.8%** and `Claude Opus 4.6` w/ Claude Code at **8.1%**; trailing only `Claude-Opus-5.0` at **2.2%**). On the 481 semantically close injections, SecPO cuts ASR from **55.1%** to **12.3%**; on the 123 multi-injection cases, from **33.3%** (41/123) to **3.3%** (4/123).
- **Text-to-Vision Security Transfer (`Repeat-After-Me` ASR@1600)**: Without any vision fine-tuning, text-only SecPO on `Qwen3.6-27B` preserves `DocVQA` utility (**95.2%** vs **96.0%** undefended) while reducing adaptive visual prompt injection ASR@1600 from **100.0%/77.0%/92.0%** (Meta-SecAlign on `Steal-PII`/`Call-Tool`/`OpenClaw`) to **0.0%/0.0%/0.0%**.
- **Quantization & Speculative Decoding (Table 8)**: Running `Qwen3.6-27B` SecPO in `Q8_0` with `DFlash` speculative decoding speeds up throughput by **2.66$\times$** on AgentDojo and **2.63$\times$** on AgentDyn while keeping static ASR at **0.0%** on both benchmarks.

### 3. Negative Results, Judge Audit, and Residual Attack Characterization
- **Continuous Embedding AT Fails (Table 12)**: Training `Llama-3.1-8B-Instruct` against continuous embedding perturbations (5 or 10 inner-loop steps across 3 insertion positions) yields **2.2%–7.0% SEP Static ASR** (worse than static text DPO's **1.8%**) and collapses `MMLU-Pro` to **25.9%** and `GSM8K` to **69.7%** under 10-step sentence-boundary training.
- **Substring Witness Matching Inflates ASR (Section 4.1)**: Manual inspection of 1,024 SEP outputs revealed **67 false positives (6.5%) and 0 false negatives** from official substring witness matching (e.g., matching `"cat"` inside `"indicate"`). Requiring case-folded witness presence plus **9/9 unanimous YES votes** across `Gemini-3.1-Flash-Lite-Preview`, `Gemini-3-Flash-Preview`, and `GPT-5` (3 votes each at $T=1$) eliminated all 67 false positives (**0 FP, 0 FN**).
- **Residual Attacks Exploit Locally Necessary Workflow Steps (Section 4.7)**: Manual audit of the 7 successful AgentDojo Genetic attacks and 140 successful DTaP attacks against SecPO shows that surviving attacks frame the unauthorized action as a mandatory prerequisite for completing the benign user task. In **75 of 140** successful DTaP attacks, the agent completed *both* the benign task and the injected task.

---

## Why Not a Skill?

SecPO is a weight-space LoRA fine-tuning recipe requiring offline or online preference optimization over 19,157 examples rather than an inference-time procedure an agent can execute during a task. Its actionable takeaways for agent system builders—anchoring security alignment to clean-input reference distributions, replacing substring witness checks with multi-judge ensembles, and enforcing system-level authorization gates against "task-prerequisite" scope expansion—belong in Praxis's always-active rules.

---

## Connections to Praxis

- **Sandbox & Guardrail Safety (`rules/agent-sandbox-safety.md`)**: Even after SecPO reduces adaptive ASR by $8.5\text{–}10.1\times$, **53.6% (75/140)** of remaining successful DTaP attacks succeed *alongside* benign task completion by framing unauthorized tool calls as prerequisite workflow steps—proving that model-level alignment must be paired with deterministic capability/scope gates (`unified-capability-gateway`, `dependency-scoped-plan-validation`).
- **Evaluation Quality (`rules/agent-evaluation-quality.md`)**: Demonstrates that substring witness matching produces a **6.5% (67/1,024) false-positive rate** on SEP and must be combined with multi-model semantic judging.
