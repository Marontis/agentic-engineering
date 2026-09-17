# Mo' Models, Mo' Problems: How to Best Select Model Pools for Multi-Agent Systems

> **Paper**: [Mo' Models, Mo' Problems: How to best select model pools when designing Multi-Agent Systems](https://arxiv.org/abs/2609.17306)
> **Praxis source**: `src:2609-17306v1`
> **Primary topic**: Multi-Agent System Design & Model Selection

## Why Not a Skill?

This paper delivers an empirical architectural evaluation and design rules for selecting LLM model pools in multi-agent systems (MAS). It formulates decision criteria and negative warnings for system configuration rather than a step-by-step procedural workflow.

---

## Core Concept

Multi-Agent Systems (MAS) frequently aggregate outputs from diverse LLMs through pre-generation routing or post-generation consensus (e.g., majority voting, LLM-as-a-judge). A common heuristic assumes that expanding the candidate pool with diverse open-source and proprietary models improves overall system robustness and reasoning capacity.

Marjanović et al. systematically benchmarked **8 model selection strategies**—evaluating model parameter size, standalone accuracy, answer diversity, and family lineage—across routing, majority voting, and judge-panel architectures on demanding scientific benchmarks.

```
       Candidate Model Pool Selection
                     │
       ┌─────────────┴─────────────┐
       ▼                           ▼
[Naive Heterogeneous Pool]   [Intra-Family Cohesive Pool]
 ├── Arbitrary diverse LLMs   ├── Models from same family
 ├── High token variance      ├── Aligned reasoning style
 ├── Format mismatches        └── Predictable confidence
       │                           │
       ▼                           ▼
 Degraded Performance        Consistently Exceeds
 (Below Best Standalone)     Best Standalone Model
```

### Key Findings

- **The Oracle Gap**: While a theoretical "oracle router" choosing the best model output per question achieves substantial performance gains, real-world aggregation mechanisms capture only a fraction of this theoretical ceiling.
- **The Pool Expansion Penalty**: Expanding candidate pool size beyond 3–5 models frequently **degrades aggregate performance below that of the single best standalone base model**. Weaker or stylistically dissonant models inject noise that corrupts voting and confuses LLM judges.
- **Superiority of Intra-Family Selection**: Selecting model pools from **within a single model family** (e.g., combining different parameter sizes or prompt-tuned variants of the same foundational family) consistently outperforms mixing arbitrary cross-family architectures. Shared tokenization biases, aligned format assumptions, and consistent calibration make intra-family ensembles substantially more stable.
- **Pre-Generation Routing Beats Voting**: When selecting among models, routing queries to specialist models before generation yields superior cost-accuracy trade-offs compared to full multi-model generation followed by majority voting.

## Relevance to Praxis

- Establishes a concrete decision rule for multi-agent system design: avoid arbitrary heterogeneous model bloat.
- Directly contributes to [`rules/multi-agent-coordination.md`](../rules/multi-agent-coordination.md).
- Complements [`capability-aware-skill-selection`](../skills/capability-aware-skill-selection/SKILL.md) by applying submodular set-selection principles to model candidate pools.
