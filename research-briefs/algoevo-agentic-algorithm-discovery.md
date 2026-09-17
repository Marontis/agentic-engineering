# AlgoEvo: Self-Evolving Agentic Search for Automated Algorithm Discovery

> **Paper**: [AlgoEvo: Self-Evolving Agentic Search for Automated Algorithm Discovery](https://arxiv.org/abs/2609.15820)
> **Praxis source**: `src:2609-15820v1`
> **Primary topic**: Agent Self-Improvement & Harness Engineering

## Why Not a Skill?

AlgoEvo proposes an end-to-end framework integrating multiple interlocking subsystems: dynamic execution diagnosis, a design skill hub, and hierarchical experience tree search. While its principles inform agent self-evolution and skill hubs, the full framework represents a specialized algorithm discovery architecture rather than an isolated subtask skill.

---

## Core Concept

Automated algorithm discovery frameworks typically constrain LLMs to rigid search pipelines with predefined control flows (e.g., fixed evolutionary loops or prompt mutation chains). This restriction blocks cross-paradigm knowledge transfer, discards rich execution feedback, and inhibits adaptive reasoning.

**AlgoEvo** reframes algorithm discovery as an interactive, knowledge-accumulating agentic process centered around three architectural components:

1. **Autonomous Runtime Diagnosis Agent**: Dynamically inspects generated algorithm code, executes it against problem instances, captures runtime telemetry and stack traces, and applies targeted edits based on empirical failure analysis.
2. **Design Skill Hub**: Decouples paradigm-specific algorithmic heuristics (e.g., genetic representations, local search operators, Pareto frontier maintenance) from the core discovery engine, allowing a unified search workflow to handle single-objective, multi-objective, and multi-component tasks.
3. **Hierarchical Experience Tree**: Organizes exploration trajectories into task-level search trees. Successful branching patterns and algorithmic primitives are consolidated into modular, reusable skills that transfer across distinct discovery benchmarks.

### Key Findings

- **Efficiency Gains**: Across six standard benchmark suites, AlgoEvo matches or outperforms specialized state-of-the-art algorithm discovery methods while requiring substantially fewer code evaluations and lower token consumption.
- **Cross-Task Transfer**: Algorithmic design patterns consolidated during simple benchmark tasks transfer directly to complex combinatorial optimization problems, demonstrating true intra-task knowledge accumulation.
- **Dynamic Skill Activation**: Decoupling domain skills into an external hub allows the agent to activate specialized operators on demand without polluting the base prompt context.

## Relevance to Praxis

- Directly aligns with the Praxis philosophy of extracting modular skills and compounding knowledge into external hubs.
- Reinforces [`procedural-family-skill-consolidation`](../skills/procedural-family-skill-consolidation/SKILL.md) and [`speculative-macro-commit`](../skills/speculative-macro-commit/SKILL.md).
