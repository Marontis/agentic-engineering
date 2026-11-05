# EvolveMAS: A Unified Self-Evolution Framework for Decentralized Multi-Agent Systems

> **Source**: [arXiv:2610.34450](https://arxiv.org/abs/2610.34450) — Zihan Wang, Yiming Wang,ashtosh Sharma, et al. (2026)
> **Praxis Source ID**: `src:2610-34450`
> **Category**: Research Brief (Decentralized Multi-Agent Memory Governance & Test-Time Evolution)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Why Not a Skill?

EvolveMAS is a full multi-agent runtime architecture that pairs every decentralized `MainAgent` one-to-one with a dedicated auxiliary LLM (`MemoryAgent`, instantiated with `GPT-4o-mini`) to manage three within-episode memory stores and two cross-episode knowledge stores across multi-episode games. While its architectural findings—separating memory maintenance from the reasoning agent's context window and stratifying knowledge distillation by model capability—provide high-value quantitative evidence, Praxis already covers structured knowledge compounding and teamwork strategy banks in [`../skills/knowledge-compounding-loop/SKILL.md`](../skills/knowledge-compounding-loop/SKILL.md) and [`../skills/learned-teamwork-strategy-bank/SKILL.md`](../skills/learned-teamwork-strategy-bank/SKILL.md). Recording EvolveMAS as a research brief preserves its cross-regime benchmarks, cost/context-occupancy curves, and capability-stratified distillation diagnostics for [`../rules/multi-agent-coordination.md`](../rules/multi-agent-coordination.md) and [`../rules/skill-system-design.md`](../rules/skill-system-design.md).

---

## Core Findings

### 1. Paired `MainAgent` + Isolated `MemoryAgent` Architecture (EEE Cycle)

To prevent self-evolving decentralized agents from suffering context bloat or reasoning interference when managing their own memory in-context (`Self-Memory`), EvolveMAS pairs each `MainAgent` $a_i$ with an isolated `MemoryAgent` $m_i$ (`GPT-4o-mini`) executing an **Execute–Evaluate–Evolve (EEE)** loop without weight updates:

1. **Within-Episode Online Adaptation (Managed by `MemoryAgent` $m_i$ at every turn $t$)**:
   - Maintains external **Structured Memory** $M_{e,t} = (E_{e,t}, S_{e,t}, W_{e,t})$ outside $a_i$'s prompt history:
     - *Episodic Memory ($E_{e,t}$)*: Chronological digest of salient interaction events in episode $e$.
     - *Semantic Memory ($S_{e,t}$)*: Verified task facts, intermediate constraints, and agreed propositions.
     - *Working Memory ($W_{e,t}$)*: Current subgoal state, active hypotheses, and immediate action context injected back into $a_i$.
2. **Cross-Episode Knowledge Evolution (Distilled after episode outcome $r_e = \text{Eval}(x_e, \tau_e, o_e)$)**:
   - Updates persistent **Interaction Knowledge** $K_e = (G_e, P_e)$ across episodes:
     - *Interaction Strategies ($G_e$)*: Reusable rule-level heuristics (general rules, subtask features, boundary conditions, procedural advice).
     - *Partner Profiles ($P_e = \{p_{e,j}\}_{j \neq i}$)*: Per-peer models tracking each partner or opponent $a_j$'s reliability, cooperativeness, role tendencies, and deception patterns.

### 2. Cross-Regime Evaluation Across 5 Benchmarks and 6 Configurations

EvolveMAS is evaluated against setting-specific native baselines (`AgentNet`, `ChatDev`, `SOTOPIA`, `LLM-Deliberation`, `Werewolf/DPIns`) and an in-context `Self-Memory` variant (where $a_i$ maintains the exact same memory schemas inside its own prompt without a separate `MemoryAgent`) across cooperative, mixed-motive, and adversarial regimes (Table 1):

| Method / Framework | BBH ($n=100$, Weak 5-Agent) | HumanEval ($n=164$, 3-Agent) | SOTOPIA ($n=80$, Bargaining) | LLM-Delib. ($n=50$, 6 Parties) | Werewolf Village (`WW-V`, $n=100$) | Werewolf Wolf (`WW-W`, $n=100$) | Normalized Average |
|:-------------------|:----------------------------|:-----------------------------|:-----------------------------|:-------------------------------|:-----------------------------------|:--------------------------------|:-------------------|
| **AgentNet** | 79.0 | 95.1 | 0.554 | 2.60 | 51.0 | 45.0 | 61.6 |
| **ChatDev** | 73.0 | 95.7 | 0.509 | 2.06 | 53.0 | 49.0 | 59.3 |
| **SOTOPIA** | 72.0 | 95.7 | **0.618** | 3.14 | 55.0 | 57.0 | 65.6 |
| **LLM-Deliberation** | 74.0 | 93.9 | 0.450 | 4.92 (SD 0.90) | **64.0** | 46.0 | 67.5 |
| **Werewolf (DPIns)** | 72.0 | 92.7 | 0.588 | 3.41 | 55.0 | 44.0 | 63.2 |
| **Self-Memory (In-Context)** | 82.0 | 95.7 | 0.576 | 4.90 (SD 0.71) | 58.0 | 42.0 | 69.5 |
| **EvolveMAS (Full)** | **83.0** | **97.0** | 0.613 | **5.40** (SD 0.64) | 62.0 | **70.0** | **77.2** |

- **Overall Cross-Regime Gain**: EvolveMAS achieves a **77.2** normalized average score across all six settings, outperforming `Self-Memory` (**69.5**, **$+7.7$ pp**) and the strongest general baseline `LLM-Deliberation` (**67.5**, **$+9.7$ pp**).
- **Adversarial & Symmetric Co-Evolution (`Werewolf`)**: In one-sided wolf deception (`WW-W`), EvolveMAS reaches **70.0%** win rate (**$+13.0$ pp** above the best baseline `SOTOPIA` at $57.0\%$ and **$+28.0$ pp** above `Self-Memory` at $42.0\%$). When both sides co-evolve symmetrically (`EvolveMAS vs. EvolveMAS`, Tables 7–8), the village achieves a **48.0%** win rate and **44.3%** wolf-detection accuracy vs. **31.0%** win rate and **30.2%** detection accuracy for `Self-Memory vs. Self-Memory`.

### 3. Ablation of External `MemoryAgent` vs. Cross-Episode Knowledge ($K_e$)

A $2 \times 2$ ablation on 6-party `LLM-Deliberation` (50 sessions, Figure 5 & Appendix A.2) isolates the contribution of externalizing within-episode memory (`MemoryAgent` vs. `Self-Memory`) from cross-episode knowledge evolution ($K_e$ enabled vs. $K = \varnothing$):

| Memory Architecture | Cross-Episode $K_e$ | Avg. Parties Agreeing (of 6) | $\ge 5/6$ Consensus Rate | Any-Proposal Unanimity | Final-Proposal Unanimity |
|:--------------------|:--------------------|:-----------------------------|:-------------------------|:-----------------------|:-------------------------|
| `Self-Memory` | Disabled ($K = \varnothing$) | 4.90 | 78.0% | 24.0% | 16.0% |
| `Self-Memory` | Enabled ($+ K_e$) | 5.24 | 80.0% | 46.0% | 34.0% |
| `MemoryAgent` | Disabled ($K = \varnothing$) | 5.36 | 88.0% | 74.0% | **48.0%** |
| **`MemoryAgent` (EvolveMAS)** | **Enabled ($+ K_e$)** | **5.40** | **90.0%** | **86.0%** | 46.0% |

- Offloading within-episode memory to an isolated `MemoryAgent` alone jumps any-proposal unanimity from **24.0% to 74.0%** ($+50.0$ pp), and adding cross-episode partner/strategy evolution $K_e$ raises it further to **86.0%** ($+62.0$ pp total).

### 4. Cost Scaling, Capability-Stratified Knowledge Sedimentation, and Long-Horizon Timing

- **10$\times$ Lower Context Occupancy & 3.2$\times$ Lower Episode Cost (Table 3)**: Across 8 sequential episodes of `SOTOPIA`, raw history accumulation (`No Memory`) balloons context window occupancy to **6.54%** and increases per-episode cost from **\$0.0071 (Episode 0) to \$0.0341 (Episode 7)** ($4.8\times$ growth). EvolveMAS caps context occupancy at **0.62%** ($10.5\times$ smaller) and keeps per-episode cost nearly flat from **\$0.0084 to \$0.0105** ($3.2\times$ cheaper at Episode 7).
- **Weak Models Fail to Distill Rule-Level Strategies (Table 4)**: In a 5-agent heterogeneous BBH team (`Gemini-2.5-Pro`, `Gemini-3.5-Flash`, `GLM-5.2`, `GPT-4.1`, and `Qwen3`), the four strong/mid-tier models each distill **40** reusable rule-level strategy entries across general rules, subtask features, boundary conditions, and procedural advice. In contrast, the weakest model (`Qwen3`) writes the highest volume of raw semantic memory notes (**56 raw $\to$ 11 unique** after deduplication) but distills **0** rule-level strategies—recording only bare per-instance answers that fail to generalize.
- **Online vs. Offline Memory Updates on Long-Horizon `LoCoMo` (Appendix F, 1,540 QA pairs)**: Turn-by-turn online `MemoryAgent` updates achieve **18.8%** overall accuracy (vs. **16.4%** for end-of-session offline `MemoryAgent`, **16.4%** for `Self-Memory`, and **7.9%** for `No Memory`) and dominate single-hop factual recall (**30.9%** vs. **24.8%** offline and **17.0%** `Self-Memory`), but trail `Self-Memory` on multi-hop synthesis across distant sessions (**26.0%** vs. **42.7%**), where aggressive turn-level compression prunes cross-session bridging cues.

---

## Relevance to Praxis

- **Multi-Agent Memory & Partner Modeling ([`../rules/multi-agent-coordination.md`](../rules/multi-agent-coordination.md))**: In decentralized multi-turn negotiation or adversarial games, keeping memory maintenance inside the acting agent's prompt (`Self-Memory`) degrades strategic deception (`WW-W`: 42.0% vs. 70.0%) and consensus formation (`LLM-Deliberation` unanimity: 46.0% vs. 86.0%); offload within-episode state curation to an isolated memory manager while bounding context occupancy below 1%.
- **Capability-Gated Skill/Rule Distillation ([`../rules/skill-system-design.md`](../rules/skill-system-design.md), [`../skills/knowledge-compounding-loop/SKILL.md`](../skills/knowledge-compounding-loop/SKILL.md))**: Table 4 provides direct empirical proof that small/weak models (`Qwen3`) cannot reliably abstract execution traces into reusable rules (0 rules distilled from 56 raw notes), reinforcing the requirement to route post-episode rule/skill distillation to strong teacher models.

---

## Key Citations

- **Zhou et al. (2024)** — *SOTOPIA: Interactive Evaluation for Social Intelligence in Language Agents* — Mixed-motive social negotiation benchmark used for multi-episode cost and adaptation tests.
- **Abdelnabi et al. (2024)** — *LLM-Deliberation: Evaluating LLMs with Multi-Agent Negotiation Games* — 6-party multi-issue consensus benchmark used in the $2 \times 2$ memory ablation.
- **Maharana et al. (2024)** — *Evaluating Very Long-Term Conversational Memory of LLM Agents (LoCoMo)* — 1,540-question long-horizon benchmark used to compare online vs. offline memory consolidation.
