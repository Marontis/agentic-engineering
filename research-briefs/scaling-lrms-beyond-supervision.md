# Scaling Large Reasoning Models beyond Human Supervision

> **Paper**: [Scaling Large Reasoning Models beyond Human Supervision: A Path toward Superintelligence](https://arxiv.org/abs/2608.31075)
> **Praxis source**: `src:2608-31075v1`

## Why Not a Skill?

Roadmap/taxonomy paper â€” presents a five-level ladder (L0â€“L4) for scaling LRMs beyond human supervision but no transferable subtask-level procedures. The levels describe what recedes from human control, not how to implement each level.

---

## Core Concept

As LRMs improve, human supervision gradually recedes from the learning loop. This paper maps two connected dimensions of this transition:

### Reward Axis
- L0: Per-instance human judgments
- L1: Reusable learned verifiers
- L2: Autonomous reward models operating without human feedback

### Experience Axis
- L0: Human-curated tasks and environments
- L1: Self-generated curricula
- L2: Constructed environments and autonomous co-evolution

### Key Risks
- **Reward hacking**: Model exploits verifier weaknesses instead of improving
- **Feedback drift**: Reward signal diverges from intended objective over time
- **Curriculum collapse**: Self-generated training becomes repetitive/narrow
- **Environment errors**: Constructed environments don't reflect real-world constraints

## Relevance to Praxis

- The L0â€“L4 ladder maps to the ecursive-improvement rules â€” each level requires different safety guarantees
- Reward hacking is directly relevant to the ehavior-aware-verification skill
- The framework informs the self-improving-agent.spec template's risk assessment section
