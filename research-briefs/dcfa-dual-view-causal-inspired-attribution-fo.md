# DCFA: Dual-view Causal-inspired Attribution for Failure Reasoning in Multi-agent Systems

> **Paper**: [DCFA: Dual-view Causal-inspired Attribution for Failure Reasoning in LLM-based Multi-agent Systems](https://arxiv.org/abs/2609.04749)
> **Praxis source**: src:2609-04749

## Why Not a Skill?

While DCFA describes a structured failure attribution procedure, it overlaps significantly with the existing `targeted-failure-attribution` skill (DoCtOR, arXiv:2608.28264) and `neural-invariant-failure-diagnosis` skill (AgentScope, arXiv:2609.02371). The dual-view approach (global causal graph + local reasoning) adds incremental refinement but does not introduce a fundamentally different procedure. The core insight—construct dependency graphs from traces to find the decisive error—is already captured. Promoting to a brief with cross-references to existing skills.

---

## Core Concept

DCFA is a training-free framework for failure attribution in LLM-based multi-agent systems. It addresses two challenges: (1) shallow attribution—existing methods capture only minor deviations while missing the decisive cause, and (2) contextual degradation—as trace length increases, model reasoning deteriorates. DCFA integrates a **global module** that constructs structured causal-inspired dependency graphs from system traces to identify the initial decisive error, and a **local module** that performs focused reasoning within the identified region.

### Key Finding

- **Primary Result**: The dual-view approach (global graph + local reasoning) outperforms single-view methods by avoiding both shallow attribution (catching only surface errors) and context degradation (losing signal in long traces).
- **Secondary Result**: The training-free nature means DCFA can be applied to any multi-agent system without task-specific fine-tuning—the causal dependency graph construction is general-purpose.

## Relevance to Praxis

- **Complements existing skills**: Extends the `targeted-failure-attribution` skill's approach with explicit causal dependency graphs. The global/local decomposition addresses the context-length limitation that single-pass attribution methods face.
- **Trace-length resilience**: The dual-view architecture specifically handles the degradation problem in long traces—relevant for complex multi-step agent workflows where traces can span hundreds of actions.
- **Cross-reference**: See `targeted-failure-attribution` (DoCtOR) for the related restrict-reflection-to-responsible-agent pattern, and `neural-invariant-failure-diagnosis` (AgentScope) for the behavioral state abstraction approach.
