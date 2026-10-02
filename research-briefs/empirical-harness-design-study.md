# An Empirical Study of Harness Design for Coding Agents

> **Source**: Fan et al., arXiv:2609.20804, Sep 2026
> **Status**: Research Brief — empirical study of harness components

## Why Not a Skill?

This is a large-scale empirical comparison (176 settings, 4 models), not a transferable procedure. It provides evidence-based design guidance for harness engineering but the guidance is conditional on model capability and budget.

## Core Concept

Existing harness evaluations treat harnesses as monolithic systems, leaving individual component contributions unclear. This study fixes the execution loop and varies three components: **planning**, **action space**, and **context management**, across four models on SWE-Bench Verified and Terminal-Bench 2.1.

## Key Findings

### Context Management
- Becomes increasingly valuable as context-window budget tightens
- Most benefit comes from **preventing context-overflow failures**
- Best strategy: **staging rule-based elision before LLM-based summarization**
- Making elided content recoverable adds machinery models rarely use and yields no accuracy gain

### Planning
- For the **weakest model** (Nemotron-3 30B): accuracy scaffold, +11.6 pts on SWE-Bench Verified and +4.5 on Terminal-Bench, at higher cost
- For **stronger models** (Nemotron-3 550B, Mistral-Medium-3.5-128B): cost saver, about 30–32% lower SWE-Bench cost with small success drops (2.0 and 0.4 pts)
- Intermediate model (Nemotron-3 120B): no consistent success gain; cost effect depends on the task type

### Action Space
- **Predefined tools** improve performance for models with weak bash proficiency
- **Bash-only interface** works for bash-capable models at substantially lower cost, especially on command-line tasks

### Trajectory-Level Analysis
- Context management **extends** execution trajectories without altering behavior
- Planning changes **where** trajectories stop
- Action space changes the **granularity** at which code is written

## Relevance to Praxis

- Provides model-aware and budget-aware harness design decision criteria
- Key rule: invest in context management first when context budgets are tight
- For strong, bash-capable models, bash-only and planning-for-cost are worth testing, but benchmark per model first
- **Contrast with GVS5H** ([`gvs5h-zero-shot-self-orchestration`](gvs5h-zero-shot-self-orchestration.md), arXiv:2608.26480): both find scaffolding helps weaker models, but GVS5H's ledger scaffold *hurt* a low-active-parameter MoE (Qwen3.6-35B-A3B, −1.2 to −9.0 pts). "Weaker" is not one axis: a small dense model and a sparse MoE with few active parameters can respond in opposite directions. Cited in `rules/recursive-improvement.md` "DON'T: Assume multi-agent scaffolding is universally monotonic across model architectures"
- Planning-for-cost is the source of the model-strength point in `rules/recursive-improvement.md` "DO: Invest in standalone verifiers before planning components" (formerly misattributed to arXiv:2609.20474; see [`harness-value-planning-vs-verification`](harness-value-planning-vs-verification.md))
- Scope: 4 models (Nemotron-3 30B/120B/550B, Mistral-Medium-3.5-128B), SWE-Bench Verified and Terminal-Bench 2.1, one lightweight harness

> Source: Fan et al., "An Empirical Study of Harness Design for Coding Agents" (arXiv:2609.20804)
