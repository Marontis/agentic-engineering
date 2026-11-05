# LLM Multi-Agent Systems Are Vulnerable to Herding and Runaway Cascades

> **Source**: [arXiv:2610.30769](https://arxiv.org/abs/2610.30769) —Joshua C. Peterson, Thomas L. Griffiths, et al. (2026)
> **Praxis Source ID**: `src:2610-30769`
> **Category**: Research Brief (Multi-Agent Collective Dynamics & Social Cascade Failure Modes)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Why Not a Skill?

This paper is a large-scale experimental replication of the classic Salganik, Dodds, and Watts (2006) **Music Lab** cultural-market experiment across **13 LLM populations** (**168,480 persona-conditioned agents** across 221 simulated worlds). Rather than proposing a software procedure, it provides a foundational empirical measurement of how exposing cumulative peer selection counts in shared multi-agent state triggers severe, non-self-correcting information cascades ($4\times\text{--}9\times$ the divergence from intrinsic appeal observed in human crowds). Its design implications—hiding running aggregate tallies during independent agent evaluation and preferring high-reasoning models when social signals are unavoidable—directly inform [`../rules/multi-agent-coordination.md`](../rules/multi-agent-coordination.md).

---

## Core Findings

### 1. Experimental Design: 168,480 Agents Across 13 LLM Populations and 17 Worlds per Model

To isolate social herding from pre-training familiarity, the authors generate **48 original songs** (using Suno v4.5, represented by titles and 131–172 word lyrics) and instantiate **12,960 persona-conditioned agents per model** (sampled from U.S. demographic distributions via Nemotron-Personas-USA) across **13 LLMs**:
- **5 Reasoning Models** (mean Artificial Analysis Intelligence Index v4.1.1 $\text{AAII} = 32.0$): `GPT-5`, `GPT-5 nano`, `Gemini 3 Flash`, `DeepSeek-R1`, `Claude Sonnet 4.6`.
- **8 Non-Reasoning Models** (mean $\text{AAII} = 11.4$): `GPT-4o`, `GPT-4o mini`, `Gemma 3 4B`, `Gemma 3 12B`, `Gemma 3 27B`, `DeepSeek-V3.1`, `Claude Haiku 4.5`, `Qwen3-Next 80B`.

For each model, agents sequentially enter **17 parallel worlds** (choosing 4 of 48 songs to inspect and deciding whether to recommend each):
1. **Independent Condition (1 world, $N = 1,440$ agents)**: Songs are presented in random order with **no peer recommendation counts**, establishing each song's baseline *intrinsic appeal* $q_i$.
2. **Weak Social Influence (8 parallel worlds, $N = 720$ agents each)**: Songs are presented in **randomized order**, but each song displays its **cumulative peer recommendation count** from prior agents in that world.
3. **Strong Social Influence (8 parallel worlds, $N = 720$ agents each)**: Songs are **sorted in descending order of cumulative peer recommendations** alongside their visible recommendation counts.

### 2. Quantitative Comparison: LLM Populations vs. Human Music Lab Baselines

| Metric / Phenomenon | Human Music Lab (Salganik et al.) | Reasoning LLMs ($n = 5$ models) | Non-Reasoning LLMs ($n = 8$ models) | All 13 LLMs (Pooled / Range) |
|:--------------------|:----------------------------------|:--------------------------------|:------------------------------------|:-----------------------------|
| **Divergence from Intrinsic Appeal ($D_{\text{KL}}$ vs. Human)** | $1.0\times$ (baseline) | $\sim 4.8\times$ (weak) / $\sim 1.7\times$ (strong) | **2.4$\times$** reasoning (weak) / **3.2$\times$** reasoning (strong) | **$\sim 9\times$** human (weak) / **$\sim 4\times$** human (strong), $p < 0.001$ |
| **Inequality (Gini Coefficient: Indep. $\to$ Weak $\to$ Strong)** | $0.187 \to \text{rises under influence}$ | $0.528 \to 0.657 \to 0.722$ | $0.395 \to 0.737 \to \mathbf{0.838}$ | **$0.446 \to 0.706\ (+0.260) \to 0.794\ (+0.348)$**, $p < 0.001$ |
| **Unpredictability Across Worlds ($U$)** | $1.0\times$ (baseline) | Comparable to humans | **$\sim 2\times$** reasoning & **$> 2\times$** humans | Driven by random early-mover lock-in |
| **Correlation $r(\text{Influence}, \text{Independent})$ (Weak / Strong)** | $0.740$ / $0.557$ | $0.738$ / $0.689$ | **$0.487$ / $0.336$** | Mean $0.584$ (weak) $\to$ **$0.472$** (strong) |
| **Early-Mover Lock-In $r(\text{First 30 Agents}, \text{Remaining 690})$** | $0.316$ (weak) / $0.723$ (strong) | **$0.878$** (weak) / **$0.882$** (strong) | **$0.866$** (weak) / **$0.932$** (strong; up to $0.998$) | Exceeds intrinsic appeal in **12/13** (weak) & **13/13** (strong) |
| **Cascade Self-Correction ($\Delta\rho = \rho_{\text{half 2}} - \rho_{\text{half 1}}$)** | **$+0.140$** (8/8 weak, $p < 0.01$) / **$+0.085$** (7/8 strong, $p < 0.05$) | Near zero under strong influence | Near zero or negative | Fails to self-correct across 16 influence worlds |

### 3. Four Structural Vulnerabilities of Multi-Agent Shared Tallies

1. **Extreme Early-Mover Lock-In (`First 30 Agents` Dictate the Next 690)**: In human markets under weak influence (randomized order + visible counts), final market share correlates much more strongly with intrinsic quality ($r = 0.740$) than with the noisy choices of the first 30 participants ($r = 0.316$). In LLM populations, even under weak influence, the correlation between the first 30 agents and the remaining 690 agents averages **$r = 0.878$** (reasoning) and **$r = 0.866$** (non-reasoning), exceeding the correlation with intrinsic appeal in **12 of 13 models** (all except `GPT-5`, where intrinsic appeal is $0.885$ vs. $0.823$ early-mover). Under strong influence, early-mover lock-in exceeds intrinsic appeal in **all 13 of 13 models** (reaching $r = 0.998$ early-mover vs. $r = 0.118$ intrinsic quality in `Gemma 3 4B`).
2. **Popularity Ordering Amplifies Divergence by 65%**: Switching from weak influence (counts visible, random order) to strong influence (counts visible, popularity-sorted order) increases mean $D_{\text{KL}}$ divergence by **65%** across 12 of 13 models ($p < 0.01$; `Claude Sonnet 4.6` is the sole exception).
3. **Inverse Scaling with General Reasoning Capability (AAII)**: Model intelligence index ($\text{AAII}$) correlates strongly and negatively with cascade divergence $D_{\text{KL}}$ ($\rho = -0.851, p < 0.001$ under strong influence; $\rho = -0.551, p = 0.051$ under weak influence) and with relative unpredictability $U_{\text{inf}} / U_{\text{ind}}$ ($\rho = -0.733, p < 0.01$ strong; $\rho = -0.719, p < 0.01$ weak).
4. **Absence of Human-Like Self-Correction**: In the human Music Lab, rank correlation $\rho$ with intrinsic quality recovered between the first half and second half of the population in **15 of 16** influence worlds ($\Delta\rho = +0.140$ from $0.633 \to 0.773$ in 8/8 weak worlds; $\Delta\rho = +0.085$ from $0.575 \to 0.660$ in 7/8 strong worlds) because humans still listened to and rejected low-quality songs after downloading them. LLM agents exhibit no consistent positive $\Delta\rho$ under strong influence; lowering decoding temperature ($1.0 \to 0.7$) does not attenuate cascades, and increasing the inspection budget ($4 \to 12$ songs) reduces absolute magnitude but preserves the cascade structure.

---

## Relevance to Praxis

- **Blackboard & Shared-State Topology Design ([`../rules/multi-agent-coordination.md`](../rules/multi-agent-coordination.md))**: When multiple agents evaluate candidate plans, hypotheses, or artifacts on a shared blackboard, exposing running vote counts or sorting candidates by cumulative popularity causes the first 30 agents' noisy preferences to lock in the remaining population ($r = 0.866\text{--}0.932$) and inflates Gini concentration from $0.446$ to $0.706\text{--}0.794$. Multi-agent voting and candidate-ranking harnesses must collect first-pass evaluations in **blind independent batches** with randomized candidate ordering before aggregating tallies.
- **Model Selection for Social Aggregation**: Because non-reasoning models diverge **$2.4\times\text{--}3.2\times$** further from intrinsic quality and exhibit **$2\times$** the cross-run unpredictability of reasoning models ($\rho = -0.851$ with AAII), avoid using small non-reasoning models in sequential peer-visible aggregation loops.

---

## Key Citations

- **Salganik, Dodds, & Watts (2006)** — *Experimental Study of Inequality and Unpredictability in an Artificial Cultural Market* (Science) — The original human Music Lab benchmark replicated in this study.
- **Bikhchandani, Hirshleifer, & Welch (1992)** — *A Theory of Fads, Fashion, Custom, and Cultural Change as Informational Cascades* — Theoretical foundation for sequential herding when agents weight public counts over private signals.
