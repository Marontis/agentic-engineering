# Who Convinced Whom? Tracing How LLMs Change Their Minds in Multi-Agent Systems

> **Source**: [arXiv:2610.35930](https://arxiv.org/abs/2610.35930) — Arnesh Batra, Aniket Khandelwal, Jashn Khemani, Krish Thukral, Arush Gumber, Denis Federico Lim, Ujwal Kumar, Phan Xuan Tan (2026)
> **Praxis Source ID**: `src:2610-35930`
> **Category**: Research Brief (Multi-Agent Debate Causality, Internal Routing & Effective Voter Independence)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Why Not a Skill?

This paper introduces **MAD Bench** (a 2,400-question multi-domain debate benchmark) and performs behavioral and white-box causal interventions (pre-rationale forced-choice readouts, authorship swaps, track-record vs. status interchange patching, and layerwise attention knockouts) across three open-weight models (`Qwen3.5-9B`, `Llama-3.1-8B-Instruct`, `Gemma-4-E4B-it`). Because it is a diagnostic and mechanistic evaluation study showing how multi-agent debate creates post-hoc rationalizations, amplifies unanimous wrong answers ($+3.1\text{ to }+7.4$ pp), and collapses three debating agents to $1.02\text{--}1.07$ effective independent voters, it is best captured as a research brief with quantitative evidence for [`../rules/multi-agent-coordination.md`](../rules/multi-agent-coordination.md), [`../rules/recursive-improvement.md`](../rules/recursive-improvement.md), and [`../rules/agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md).

---

## Core Findings

### 1. MAD Bench (2,400 Questions) and the Round-Matched Independent-Reflection Control

To separate the causal effect of *peer communication* from the extra inference-time compute of multi-turn revision, the authors evaluate 3-agent debate against a **round-matched independent-reflection control** (where the same three agents revise their answers for the same number of rounds without seeing peers' responses) on **MAD Bench** ($N = 2,400$ questions: 1,790 externally sourced + 610 constructed from 156 seeds; 1,700 with reference targets + 700 unlabelled stance-change items):

- **Knowledge & Reasoning (800 items, all 800 reference-labelled)**: Disciplinary reasoning from MMLU-Pro and MATH-500 (310), quantitative reasoning from GSM8K (90), verifiable knowledge from MMLU (60), misconception resistance from MMLU + constructed claims (140), and calibrated abstention from CoCoNot (200: 100 abstain + 100 answerable controls).
- **Values & Moral Judgment (800 items: 280 labelled, 520 unlabelled)**: Clear moral norms (80 constructed, labelled), ETHICS across 5 frameworks (200, labelled), moral trade-offs (220 constructed, unlabelled), public-policy debates (100 constructed, unlabelled), and Anthropic Persuasion pairs (200, unlabelled).
- **Safety & Refusal (800 items: 620 labelled, 180 unlabelled)**: Direct harmful requests from AdvBench, HarmBench, JailbreakBench, and StrongREJECT (180, labelled), strategic deception from DeceptionBench (180, labelled), XSTest safe over-refusal controls (130, labelled) and unsafe contrasts (130, labelled), and contextual safety-boundary requests varying requester identity (180 constructed, unlabelled).

### 2. Individual-Level Causal Mechanisms: Pre-Rationale Commitment, Message Decomposition, Source Cues, and Attention Routing

Table 1 summarizes the headline behavioral and white-box causal measurements across the three architectures (`Llama-3.1-8B-Instruct` with 32 full-attention layers; `Qwen3.5-9B` hybrid with 8 full-attention + 24 Gated DeltaNet recurrent linear-attention layers; `Gemma-4-E4B-it` with 7 global-attention + 35 sliding-window layers):

| Measurement / Intervention | `Qwen3.5-9B` (Hybrid) | `Llama-3.1-8B-Instruct` | `Gemma-4-E4B-it` | Key Mechanistic Takeaway |
|:---------------------------|:----------------------|:------------------------|:-----------------|:-------------------------|
| **Committed at Read ($f = 0\%$ written), Debate vs. Reflection** | **65.4%** vs. **22.3%** | **52.4%** vs. **35.4%** | **48.5%** vs. **12.6%** | Debate settles 48.5%–65.4% of answer switches *before* the receiver writes any CoT |
| **Paired Per-Question Commitment Gap (Debate $-$ Reflection)** | **+40.9 pp** (87% favor debate) | **+15.6 pp** (64% favor debate) | **+35.9 pp** (86% favor debate) | Neutral filler shifts Qwen by only $-2.5$ pp; cross-item CoT collapses gap to $4.6$ pp |
| **Incoming Peer Reasoning Share $s_{\text{reason}}$ (Values / All)** | **70.0%** / **69%** ($[67, 72]$) | **65.8%** / — | **68.4%** / **60%** ($[57, 63]$) | Peer reasoning shifts margin by $1.31$ logits vs. $0.59$ for bare peer answer |
| **Additivity Residual $r = \Delta_{\text{ans}} + \Delta_{\text{reas}} - \Delta_{\text{full}}$ (logits)** | **$-0.05$** (additive) | **$-0.69$** (synergistic) | **$+0.43$** (sub-additive) | Additivity of peer answer and reasoning is model-dependent |
| **Authorship Swap Shift (`Own-Label` vs. `Peer-Label`, logits)** | **$+0.749$** (vs. $-0.019$ pos.) | **$+1.086$** (vs. $+0.024$ pos.) | **$+1.302$** (vs. $-0.032$ pos.) | Attributing identical text to `self` is **39$\times$–45$\times$** stronger than prompt position |
| **Track-Record vs. Status Shift (logits: Record / Status)** | **$0.560$ / $0.077$** | **$0.876$ / $0.011$** | **$1.905$ / $0.793$** | Stated reliability dominates credentials; poor record makes professor worse than no cue ($-0.203$ to $-0.985$ logits) |
| **Magnitude-Matched Causal Interchange Ratio (Record / Status)** | **3.7$\times$** $[3.0, 4.7]$ ($4.4\times$ at status norm) | **14.3$\times$** $[7.3, 69.6]$ | **1.44$\times$** $[1.33, 1.56]$ ($1.39\times$ at status norm) | Even when status is linearly decodable (AUROC $0.85$), causal routing favors track record |
| **Complete Attention Knockout (% of peer influence removed)** | **80%** $[75, 84]$ (8/32 layers maskable) | **132%** $[122, 144]$ (32/32 maskable) | **117%** $[111, 123]$ (42/42 maskable) | Hybrid Gated DeltaNet recurrent state carries **~20%** of peer influence outside attention masks |
| **Layer-12 Residual-Stream Source Recovery $\rho_{12}$** | **0.24** $[0.22, 0.27]$ | **0.03** $[0.02, 0.04]$ | **0.06** (at matched depth) | Source cues persist 4 layers deeper at their own tokens in hybrid `Qwen3.5-9B` |

- **Asymmetry Between Reading and Writing Reasoning**: While an incoming peer's reasoning carries **60%–70%** of the persuasive weight ($1.31$ logits vs. $0.59$ logits for a bare peer answer), the receiving agent's *own* written chain-of-thought after reading peers is largely post-hoc: forcing a decision at $f = 0$ (zero tokens of own reasoning written) already matches the eventual revised answer **65.4%**, **52.4%**, and **48.5%** of the time in debate (vs. **22.3%**, **35.4%**, and **12.6%** in reflection).

### 3. Collective Outcomes: Minimal Accuracy Gains, Higher Unanimous Errors, and Collapse of Voter Independence

Evaluating 3-round debate on the fully parsed reference-labelled subset and 12-round debate on a 600-question subset (Tables 1, 13, and 14) reveals that consensus after debate does not represent independent corroboration:

| Collective Metric | `Qwen3.5-9B` | `Llama-3.1-8B-Instruct` | `Gemma-4-E4B-it` |
|:------------------|:-------------|:------------------------|:-----------------|
| **Accuracy: Round-0 Majority Vote $\to$ Round-3 Debate** | $88.0\% \to 89.2\%$ (**$+1.2$ pp**) | $77.3\% \to 77.8\%$ (**$+0.5^*$ pp**, NS; Knowledge drops $75.7\% \to 71.6\%$) | **$+1.2$ pp** |
| **Wrong Unanimity: Round-3 Reflection $\to$ Round-3 Debate** | $6.6\% \to 9.8\%$ (**$+3.1$ pp**) | $11.8\% \to 19.2\%$ (**$+7.4$ pp**) | **$+3.6$ pp** |
| **Wrong Majority Lock-In (Unanimous wrong given wrong Round-0 majority)** | **76%** (vs. 54% reflection) | **76%** (vs. 43% reflection) | — |
| **2–1 Split Ratified as Initial Plurality at Unanimity (%)** | **76%** $[69, 83]$ (76% right / 76% wrong) | **73%** $[67, 80]$ (64% right / 80% wrong) | **83%** $[76, 89]$ (82% right / 84% wrong) |
| **Groups Frozen After Turn 1 (Debate vs. Reflection, 12-turn run)** | **90%** vs. **80%** ($+10.2$ pp) | **70%** vs. **14%** ($+56.2$ pp) | **88%** vs. **67%** ($+20.5$ pp) |
| **Turn-12 Unanimity on Contested Questions (Debate vs. Reflection)** | **98.9%** vs. **36.8%** | **93.8%** vs. **35.9%** | **97.5%** vs. **35.4%** |
| **Effective Independent Voters $n_{\text{eff}} = \frac{3}{1+2\rho}$ at Turn 3 (Contested)** | **1.18** (vs. **2.34** reflection) | **1.15** (vs. **1.80** reflection) | **1.33** (vs. **2.25** reflection) |
| **Effective Independent Voters $n_{\text{eff}}$ at Turn 12 (Contested)** | **1.02** $[1.00, 1.07]$ (vs. **2.10** reflection) | **1.07** $[1.01, 1.14]$ (vs. **1.70** reflection) | **1.02** $[1.00, 1.06]$ (vs. **1.77** reflection) |

- **Three Debating Agents Collapse to ~1 Effective Voter**: By round 12 on initially contested questions, intra-class correctness correlation $\rho$ drives effective voter count $n_{\text{eff}} = 3 / (1 + 2\rho)$ down to **1.02–1.07** under debate (compared to **1.70–2.10** under round-matched solo reflection), while between turns 6 and 11 the debating agents generate ~8 million tokens for a 0.5-point accuracy shift.

---

## Relevance to Praxis

- **Multi-Agent Debate Protocol Design ([`../rules/multi-agent-coordination.md`](../rules/multi-agent-coordination.md), [`../rules/recursive-improvement.md`](../rules/recursive-improvement.md))**:
  1. Because relabelling identical text as the receiver's own shifts adoption margins **$39\times\text{--}45\times$** more than prompt position ($+0.749$ to $+1.302$ logits) and stated track record dominates status cues by **$1.4\times\text{--}14.3\times$**, debate harnesses should strip self-authorship labels or attach empirical track-record calibration ([`../skills/debate-consensus-memory-calibration/SKILL.md`](../skills/debate-consensus-memory-calibration/SKILL.md)) rather than persona credentials.
  2. Cap homogeneous multi-agent debate at 1–3 rounds: 70%–90% of groups freeze after Turn 1, and running 12 rounds collapses 3 agents to **1.02–1.07** effective voters while inflating wrong unanimity by **+3.1 to +7.4 pp**.
- **Evaluation Quality ([`../rules/agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md))**: Always benchmark multi-agent debate against a **compute-matched independent-reflection control** and report both **wrong-unanimity rate** and **effective voter count $n_{\text{eff}}$** alongside majority accuracy (and filter or penalize unparseable Round-0 outputs consistently so format compliance does not create artificial +3 pp debate gains).

---

## Key Citations

- **Choi, Zhu, & Li (2025)** — *Debate or Vote: Which Yields Better Decisions in Multi-Agent Large Language Models?* (NeurIPS 2025) — Establishes the theoretical baseline that majority voting accounts for most nominal MAD accuracy gains.
- **Turpin et al. (2023)** — *Language Models Don't Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting* — Single-agent unfaithful CoT foundation extended here via $f = 0$ pre-rationale readouts in multi-agent debate.
- **Geva et al. (2023)** — *Dissecting Recall of Factual Associations in Auto-Regressive Language Models* — Attention-knockout methodology adapted to compare all-attention (`Llama-3.1-8B`, `Gemma-4-E4B`) vs. hybrid recurrent (`Qwen3.5-9B`) peer-influence routing.
