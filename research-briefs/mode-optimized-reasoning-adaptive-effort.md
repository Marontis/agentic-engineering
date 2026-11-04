# MORE: Mode-Optimized Reasoning with Self-Adaptive Effort for Self-Evolving Agents

> **Source**: [arXiv:2610.33684](https://arxiv.org/abs/2610.33684) — Dianxing Shi, Dingjie Fu, Tianyu Lei, Wangjie Qiu (2026)
> **Praxis Source ID**: `src:2610-33684`
> **Category**: Research Brief (Self-Evolving RL Training Pipeline & Coupled Mode–Budget Optimization)

---

## Why Not a Skill?

MORE is a two-stage post-training reinforcement learning pipeline (Stage 1 LoRA supervised fine-tuning on 43,304 four-mode records derived from 10,826 AQuA-RAT questions, followed by Stage 2 `MATE-PPO` proposer–solver self-play across $4\times$ NVIDIA A100-80GB GPUs) that modifies model weights so the policy emits an internal `<mode=m>` control token before generating a response. Because Praxis skills target inference-time and harness-level engineering procedures rather than GPU weight-training pipelines, MORE is cataloged as a research brief whose findings on coupled mode–budget rewards and online difficulty tiering inform [`../rules/recursive-improvement.md`](../rules/recursive-improvement.md).

---

## Core Findings

### 1. Two-Stage Training Pipeline: Mode-Contract SFT + `MATE-PPO` Self-Evolution

To stop self-evolving proposer–solver agents (such as Absolute-Zero Reasoner, AZR) from defaulting to verbose long chain-of-thought on every task, MORE factorizes generation into a discrete reasoning-form action $a_{\text{mode}} \in \{\texttt{direct}, \texttt{short\_cot}, \texttt{long\_cot}, \texttt{code}\}$ and a mode-conditioned response $y$:
$$\pi_\theta(a_{\text{mode}}, y \mid x) = \pi_\theta(a_{\text{mode}} \mid x)\,\pi_\theta(y \mid x, a_{\text{mode}})$$

1. **Stage 1 — Mode-Format Initialization (SFT)**:
   - Converts **10,826 AQuA-RAT** questions (3,000 multiple-choice + 7,826 open-form) into **43,304 SFT records** (10,826 per contract; `code` rationales generated with GPT-5, `long_cot` with DeepSeek-R1; 4,096-token cutoff). Mean target lengths are **12.7 tokens** (`direct`), **110.4 tokens** (`short_cot`), **252.8 tokens** (`code`), and **1,226.5 tokens** (`long_cot`).
   - Trains all-target LoRA for 6 epochs (3,654 steps) so the model emits `<mode=m>` as its first likelihood-bearing policy token and follows a distinct output contract per mode.
2. **Stage 2 — Self-Evolving Mode–Budget Optimization (`MATE-PPO` Without Curated Data)**:
   - Runs proposer–solver self-play across 6 executable task streams (abduction/input recovery, deduction/output prediction, and induction/function synthesis).
   - **Online Difficulty Clustering**: Assigns rollouts by structural AST/prompt/verifier features into partitions of up to $K = 9$ clusters per family–verifier pair, tracking each cluster's rolling accuracy EMA $q_c^{(t)} = 0.8 q_c^{(t-1)} + 0.2 c_t$ (mature after 8 observations) and ranking clusters into **hard** ($q_c \le Q_{0.33}$), **medium** ($Q_{0.33} < q_c \le Q_{0.67}$), and **easy** ($q_c > Q_{0.67}$) tiers.
   - **Dynamic Mode-Conditioned Budget Bands $[B_{d,m}^-, B_{d,m}^+]$**: Initialized on a 6,144-token controller scale (e.g., `easy`: 16–128 `direct`, 96–384 `short`, 384–1536 `long`, 128–768 `code`; `hard`: 64–512 `direct`, 256–1024 `short`, 1024–4096 `long`, 512–3072 `code`) and updated online via empirical $[Q_{0.2}, Q_{0.8}]$ quantiles of correct response lengths (with downward updates rate-limited to 5%/20%).
   - **Joint Terminal Return ($R_{\text{MORE}}$)**: Combines verifier accuracy $R_{\text{acc}} \in \{0, 1\}$ with three shaped terms using weights $(\alpha, \beta, \gamma) = (0.6, 1.0, 0.05)$:
     $$R_{\text{MORE}} = R_{\text{acc}} + \alpha R_{\text{BD}} + \beta R_{\text{MF}} + \gamma R_{\text{MB}}$$
     where $R_{\text{BD}} = \operatorname{clip}[-\lambda_d(w_o o + w_u(c) u), -0.5, 0]$ penalizes over-budget length $o$ on *all* rollouts ($w_o = 1$) while down-weighting under-budget pressure $u$ on incorrect rollouts ($w_u(1) = 1, w_u(0) = 0.1$); $R_{\text{MF}} = c \cdot U(d, m)$ rewards mode-difficulty fit only when correct (`easy` favors `direct` $+0.2$ / `short` $+0.1$ and penalizes `long`/`code` $-0.1$; `hard` favors `code` $+0.3$ / `long` $+0.2$ and penalizes `direct` $-0.3$); and $R_{\text{MB}} = c \cdot \operatorname{clip}[-\eta(d, m)(o + u), -0.25, 0]$ couples mode and budget compliance.

### 2. Accuracy Gains Across 3B, 7B, and 14B Base and Coder Models

Across 3 coding benchmarks (`CAvg`: HumanEval+, MBPP+, LiveCodeBench v1–v5), 6 math benchmarks (`MAvg`: AIME 2024, AIME 2025, AMC 2023, MATH-500, Minerva Math, OlympiadBench), GSM8K, and MMLU-Pro (`AVG` = mean of `CAvg`, `MAvg`, `GSM8K`, `MMLU-Pro`), MORE consistently outperforms both base checkpoints and data-free Absolute-Zero Reasoner (`AZR`) across all 5 model configurations (Tables 1, 3, and 10; Figure 3b):

| Model Scale & Backbone | Variant | HE+ / MBPP+ / LCB | `CAvg` | `MAvg` (6-Bench) | `GSM8K` | `MMLU-Pro` | Overall `AVG` |
|:-----------------------|:--------|:------------------|:-------|:-----------------|:--------|:-----------|:--------------|
| **Qwen2.5-Coder-3B** | Base / +AZR / **+MORE** | $72.9$ / $68.8$ / $25.1$ (MORE) | $51.0 \to 54.9 \to \mathbf{55.6}$ ($+0.7$) | $18.8 \to 26.5 \to \mathbf{28.0}$ ($+1.5$) | $69.4 \to 71.3 \to \mathbf{73.3}$ ($+2.0$) | $38.3 \to 40.3 \to \mathbf{42.5}$ ($+2.2$) | $44.4 \to 48.3 \to \mathbf{49.9}$ (**$+1.6$**) |
| **Qwen2.5-7B-Base** | Base / +AZR / **+MORE-7B** | $76.7$ / $66.8$ / $30.8$ (MORE) | $52.0 \to 55.2 \to \mathbf{58.1}$ ($+2.9$) | $27.5 \to 38.4 \to \mathbf{42.3}$ ($+3.9$) | $80.4 \to 84.5 \to \mathbf{88.6}$ ($+4.1$) | $47.6 \to 49.5 \to \mathbf{51.5}$ ($+2.0$) | $51.9 \to 56.9 \to \mathbf{60.1}$ (**$+3.2$**) |
| **Qwen2.5-Coder-7B** | Base / +AZR / **+MORE-Coder-7B** | $81.7$ / $68.8$ / $\mathbf{38.0}$ (MORE) | $56.6 \to 61.6 \to \mathbf{62.8}$ ($+1.2$) | $23.9 \to 39.1 \to \mathbf{42.8}$ ($+3.7$) | $72.2 \to 72.5 \to \mathbf{77.8}$ ($+5.3$) | $42.5 \to 44.6 \to \mathbf{46.0}$ ($+1.4$) | $48.8 \to 54.4 \to \mathbf{57.3}$ (**$+2.9$**) |
| **Qwen2.5-14B-Base** | Base / +AZR / **+MORE-14B** | $75.4$ / $68.5$ / $37.3$ (MORE) | $55.5 \to 58.2 \to \mathbf{60.4}$ ($+2.2$) | $28.7 \to 41.9 \to \mathbf{42.2}$ ($+0.3$) | $84.0 \to 85.2 \to \mathbf{87.6}$ ($+2.4$) | $40.1 \to 41.9 \to \mathbf{42.3}$ ($+0.4$) | $52.1 \to 56.8 \to \mathbf{58.1}$ (**$+1.3$**) |
| **Qwen2.5-Coder-14B** | Base / +AZR / **+MORE-Coder-14B** | $\mathbf{85.4}$ / $\mathbf{73.3}$ / $\mathbf{41.5}$ (MORE) | $60.0 \to 63.6 \to \mathbf{66.7}$ ($+3.1$) | $20.3 \to 43.0 \to \mathbf{46.0}$ ($+3.0$) | $81.7 \to 83.5 \to \mathbf{85.1}$ ($+1.6$) | $42.8 \to 44.7 \to \mathbf{45.8}$ ($+1.1$) | $51.2 \to 58.7 \to \mathbf{60.9}$ (**$+2.2$**) |

### 3. Training & Inference Efficiency: 48.0% Shorter Responses and 45.1% Lower Latency

- **Training-Time Token Economy & Earlier Convergence**: After the first ~100 updates, MORE's mean prompt-plus-response tokens per rollout stabilize at **~50% of AZR** on `Base-7B` and **~67% of AZR** on `Coder-7B` (Figure 5b), while reaching peak OOD performance at **step 250** (vs. step 350 for AZR—at least one full 50-step evaluation interval earlier across nearly every trajectory).
- **Inference-Time Response Length & Wall-Clock Reductions (Table 2)**: Averaged equally across all 8 matched 7B backbone–benchmark pairs, MORE reduces **Response Length Avg by 48.0%** and **Wall Time by 45.1%** compared to AZR while achieving higher accuracy:
  - `MORE-7B` vs. `AZR-7B`: Code Avg length **$291.5$ vs. $603.7$ tokens** ($68\text{m }23\text{s}$ vs. $164\text{m }27\text{s}$); Math Avg **$3,173$ vs. $4,468.2$ tokens** ($49\text{m }27\text{s}$ vs. $62\text{m }46\text{s}$); GSM8K **$195.9$ vs. $412.6$ tokens** ($15\text{m }6\text{s}$ vs. $24\text{m }40\text{s}$); MMLU-Pro **$351.7$ vs. $485.4$ tokens** ($27\text{m }22\text{s}$ vs. $38\text{m }1\text{s}$).
  - `MORE-Coder-7B` vs. `AZR-Coder-7B`: Code Avg length **$191.73$ vs. $537.4$ tokens** ($54\text{m }36\text{s}$ vs. $143\text{m }2\text{s}$); Math Avg **$3,015.9$ vs. $5,769.3$ tokens** ($51\text{m }39\text{s}$ vs. $88\text{m }48\text{s}$); GSM8K **$105.1$ vs. $322.5$ tokens** ($7\text{m }44\text{s}$ vs. $23\text{m }44\text{s}$); MMLU-Pro **$303.4$ vs. $537.9$ tokens** ($24\text{m }45\text{s}$ vs. $43\text{m }53\text{s}$).
- **Adaptive Mode Routing vs. Fixed Modes at Test Time (Table 11)**: Compared to forcing `MORE-Coder-7B` to use `Fixed long_cot` on every instance, `Adaptive MORE-Coder-7B` achieves a higher `Code Avg` (**62.8% vs. 61.6%**) with **52.8% fewer tokens** ($191.7$ vs. $405.8$), and stays within $0.3\text{--}1.3$ points on `Math Avg` ($42.8\%$ vs. $43.1\%$), `GSM8K` ($77.8\%$ vs. $79.1\%$), and `MMLU-Pro` ($46.0\%$ vs. $46.9\%$) while cutting mean tokens by **36.7%**, **14.1%**, and **30.4%**, respectively.
- **Two-Stage Synergy (Table 3 Ablation on `Qwen2.5-Coder-7B`)**: Simply raising the training token cap to 10,240 (`AZR +10K`) adds only $+0.3$ AVG ($54.4 \to 54.7$). Stage 1 SFT alone initially drops AVG ($48.8 \to 45.3$) as the model conforms to the four mode tags, and Stage 2 `MATE-PPO` without Stage 1 reaches only $47.8$ AVG because it lacks an identifiable mode prior; combining Stage 1 + Stage 2 (`MORE-Coder-7B`) unlocks **57.3 AVG**.

---

## Relevance to Praxis

- **Self-Evolving Loop Design & Compute Calibration ([`../rules/recursive-improvement.md`](../rules/recursive-improvement.md))**: Unconstrained self-play RL (like AZR) inflates response lengths (`Coder-7B` Math Avg grows from $4,225.1$ to $5,769.3$ tokens) because long deliberation becomes a default hedge. Coupling discrete reasoning-mode selection (`direct`, `short_cot`, `long_cot`, `code`) with policy-relative quantile difficulty tiers ($Q_{0.33} / Q_{0.67}$) and correctness-gated efficiency rewards prevents length bloat and cuts inference latency by 45.1% without sacrificing accuracy.
- **Checkpoint Selection & Stopping ([`../skills/self-evolution-stopping-rule/SKILL.md`](../skills/self-evolution-stopping-rule/SKILL.md))**: MORE selects checkpoints using an in-distribution execution composite $S_{\text{ID}}(t) = \frac{1}{3}[\text{CruxEval-I} + \text{CruxEval-O} + \text{LCB-Execution}]$, reaching peak OOD generalization at step 250 rather than step 350.

---

## Key Citations

- **Zhao et al. (2025)** — *Absolute Zero: Reinforced Self-Play Reasoning with Zero Data (AZR)* — The primary data-free proposer–solver self-evolution baseline extended by MORE.
- **Wu et al. (2025)** — *ARM: Adaptive Reasoning Model* — Introduces the four-mode (`direct`, `short_cot`, `long_cot`, `code`) SFT data construction recipe used in Stage 1.
- **Wu et al. (2026)** — *CODA: Difficulty-Aware Compute Allocation for Adaptive Reasoning* — Difficulty-conditioned token budgeting baseline contrasted with MORE's coupled mode–budget policy.
