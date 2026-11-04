# RSI Arena: Towards Recursive Self-Improvement with Human Feedback

> Source: `src:2610-33624` — "RSI Arena: Towards Recursive Self-Improvement with Human Feedback" (arXiv:2610.33624, 2026)

## Classification: Research Brief (Contextual Knowledge)

This paper is classified as a **research brief** because it is a controlled comparative benchmark study evaluating 10 frontier LLM agents acting as autonomous post-training researchers over a 9-day, multi-thousand-GPU-hour competition rather than a single transferable procedure. Its empirical findings—quantifying the disconnect between compute spend and model quality, the decoupling of static benchmark gains from blind human preference, and severe unprompted safety regressions—provide essential quantitative guardrails for `rules/recursive-improvement.md` and `rules/agent-evaluation-quality.md`.

---

## Problem & Motivation

Can frontier coding agents autonomously execute the entire post-training lifecycle of a raw base language model—curating datasets, running SFT and preference optimization (DPO/ORPO/SimPO/RL), diagnosing failures, and nominating checkpoints—and further improve that model using real human preference battles without human researcher intervention? Prior self-improvement benchmarks evaluate narrow, single-metric code or math loops; they do not test open-ended post-training where an agent must balance general chat quality, reasoning depth, formatting compliance, and safety under fixed wall-clock and compute budgets.

---

## Experimental Design: Two-Stage Autonomous Post-Training Arena

Ten frontier agents (`GPT-6 Astra`, `Grok 4.7`, `MiMo-V2.6-Pro`, `GLM-5.3`, `MiniMax M3.1 Flash`, `Kimi K3`, `Gemini 3.8 Flash`, `Muse Spark 1.3`, `Step 5 Preview`, and `DeepSeek V4.1 Flash`) were tasked with autonomously post-training `NVIDIA Nemotron 3.5 Lightning 30B-A3B Base` (an MoE base model with ~30B total / ~3B active parameters whose end-of-turn token is untrained) on a shared 64-GPU RTX PRO 6000 Blackwell cluster:

1. **Stage 1 — Autonomous Post-Training from Base (6 Days / 144 Hours)**:
   - Budget per agent: **1,000 GPU-hours** and **\$300 API credit**.
   - Agents autonomously wrote training scripts, generated/filtered synthetic data, and submitted candidate checkpoints. Across all 10 agents, Stage 1 executed **5,391 GPU jobs** consuming **6,905 GPU-hours** and **\$1,050 API spend**, producing **81 accepted checkpoint nominations** (6 agents used LoRA adapters; 4 ran full-parameter fine-tuning; all 10 ran SFT—predominantly on Tülu 3 mixtures—and 6 followed SFT with DPO, ORPO, or SimPO).
2. **Stage 2 — Iteration with Human Preference Records (3 Days / 72 Hours)**:
   - Budget per agent: **500 GPU-hours** and **\$150 API credit** (consuming 2,880 of 5,051 available GPU-hours and \$541 of \$1,500 API credit).
   - Each agent received **213 to 276 blind human battle records** from Stage 1 (prompts, model pairs, and human votes) to diagnose weaknesses and refine its Stage 1 checkpoint.
3. **Evaluation Protocol**:
   - **20 Automated Benchmarks**: 16 capability benchmarks (summarized as the median percentage of the `Base`-to-`NVIDIA-Instruct` gap closed across 12 core capability benchmarks) and 4 safety/bias benchmarks (including **StrongREJECT** harmful-request compliance and **BBQ** social bias).
   - **Blind Human Arena**: Pairwise human preference battles reported both as raw Bradley-Terry ratings and with Arena.ai-style **length and markdown-style controls**. Any autonomous checkpoint promotion in production must enforce `"DO: Pass every self-modification through one acceptance gate"` in [recursive-improvement.md](../rules/recursive-improvement.md).

---

## Key Empirical Findings

### 1. Stage 1 & Stage 2 Leaderboard Highlights

| Agent / Baseline | Stage 1 GPU-Hours | Stage 1 Median Gap Closed (%) | Stage 1 Style-Controlled Human Rating | Stage 2 Median Gap Closed (%) | Stage 2 Style-Controlled Human Rating |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `NVIDIA Nemotron Instruct` (Human Reference) | — | 100% | **1,094** (1,182 raw) | 100% | 1,054 |
| **`GPT-6 Astra`** (1st Place) | ~1,000 | **76%** | **1,095** (1,161 raw) | **87%** | **1,061** |
| `Gemini 3.8 Flash` (Early Self-Stop) | **19** (\$7 API) | — | **981** | — | — |
| `Muse Spark 1.3` (Long-CoT Over-Training) | 1,000 | Highest AIME 2026 (**66.7** vs. 21.7 Instruct) | 938 (8th / 10) | — | — |
| `DeepSeek V4.1 Flash` | 999 | — | 887 (-207 vs. Instruct) | — | -35 vs. Instruct (+172 pts gain) |

- **Frontier agents can nearly match human-engineered post-training on style-adjusted chat**: `GPT-6 Astra` closed a median of **76%** of the Base-to-Instruct capability gap in Stage 1 (rising to **87%** in Stage 2) and matched `NVIDIA Instruct` on style-controlled human arena ratings (**1,095 vs. 1,094** in Stage 1; **1,061 vs. 1,054** in Stage 2, though in a targeted raw head-to-head tie-breaker without length/style adjustments, `NVIDIA Instruct` defeated `Astra` **39 to 18**).
- **8 of 10 agents improved on human preference in Stage 2**: Given 213–276 human battle records, 8 of 10 agents raised their style-controlled rating relative to `NVIDIA Instruct` by a **median of +28 points** (`DeepSeek V4.1 Flash` improved most, closing its deficit from **-207 to -35** as its median response length expanded from **61 to 508 tokens**).

### 2. Critical Pitfalls Exposed by Autonomous Post-Training

1. **Compute Burn Does Not Correlate with Output Quality ($\rho = -0.21$)**:
   - Across the 10 agents, GPU-hours consumed correlated at **$\rho = -0.21$** with style-controlled human ratings and **$\rho = -0.01$** with benchmark progress. `Gemini 3.8 Flash` halted its own campaign after just **12 hours (19 GPU-hours, \$7 API spend)** when its checkpoint scored 59/60 on a self-written sanity test, yet outperformed both `Muse Spark 1.3` (1,000 GPU-hours) and `DeepSeek V4.1 Flash` (999 GPU-hours) in human battles (981 vs. 938 and 887).
2. **Benchmark Gains Decouple from Human Preference ($\rho = -0.19$ in Stage 2)**:
   - While Stage 1 broad capability progress correlated with human ratings ($\rho = 0.73$; WildBench chat judge tracked human ratings best at **$\rho = 0.95$**), competition math benchmarks showed zero or negative correlation (**$\rho = 0.10$** on AIME 2026, **$\rho = -0.30$** on HMMT).
   - `Muse Spark 1.3` trained heavily on long reasoning traces to reach **66.7 on AIME 2026** (vs. **21.7** for `NVIDIA Instruct`), but ranked **8th of 10** in the human arena because its verbose reasoning hit output token limits (**8.6%** of arena responses and **19.2%** of benchmark responses truncated at 65,536 tokens).
   - Between Stage 1 and Stage 2, benchmark changes and human rating changes were negatively correlated (**$\rho = -0.19$**; median benchmark shift was only **+2 points**). `MiniMax M3.1 Flash` gained **+68 human rating points** while losing **-18 benchmark points** because its Stage 2 preference tuning broke strict answer-extraction formatting on **1,435 of 1,584 GPQA items**.
3. **Verbose Bias in Human Arena Votes (72% Win Rate)**:
   - In the 999 decisive Stage 1 human battles, the longer response won **72%** of the time, incentivizing agents in Stage 2 to inflate response length unless length-controlled evaluation is enforced.
4. **Silent Safety and Bias Regressions When Safety Is Unspecified**:
   - Because the task prompt did not mandate safety alignment, agents optimized solely for capability and helpfulness. In Stage 1, 3 models (`Gemini 3.8 Flash` at **43.6**, `Grok 4.7` at **34.4**, and `Muse Spark 1.3` at **31.4**) exhibited worse harmful-request compliance on **StrongREJECT** than the unaligned Base model (**16.9**, compared to `NVIDIA Instruct`'s **99% refusal rate**).
   - In Stage 2, optimizing for human battle wins caused `MiniMax M3.1 Flash` to regress sharply on StrongREJECT harmful compliance from **2.6 to 24.5** (+21.9 points worse), while `MiMo-V2.6-Pro` dropped on **BBQ** social bias accuracy from **84.7 to 56.5** (-28.2 points).

---

## Why Not a Skill?

RSI Arena is an observational benchmark competition comparing how 10 black-box agents orchestrate SFT/DPO pipelines rather than a prescriptive algorithmic method. Its lessons are quantitative governance and evaluation rules—specifically, requiring **multi-dimensional acceptance gates** that pair style-controlled preference judges (`WildBench`, $\rho = 0.95$) with strict parser-format checks, token-truncation monitors, and mandatory safety non-regression floors (`StrongREJECT`, `BBQ`).

---

## Connections to Praxis

- **Recursive Improvement (`rules/recursive-improvement.md`)**: Demonstrates that autonomous post-training loops without hard safety and format regression gates produce severe collateral degradation (StrongREJECT harmful compliance jumping from 2.6% to 24.5%; GPQA format failures on 1,435/1,584 items) even as human preference scores rise.
- **Evaluation Quality (`rules/agent-evaluation-quality.md`)**: Quantifies why competition math benchmarks ($\rho = 0.10$ to $-0.30$) and raw unadjusted human votes (72% length bias) cannot substitute for style-controlled chat judges ($\rho = 0.95$) and multi-metric validation suites.
