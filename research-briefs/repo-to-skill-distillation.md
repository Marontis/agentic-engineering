# Repo-To-Skill: Distilling GitHub Repositories into AI4AI Skills

> **Paper**: [Repo-To-Skill: Distilling GitHub Repositories Into AI4AI Skills](https://arxiv.org/abs/2609.02749)
> **Praxis source**: src:2609-02749v1

## Why Not a Skill?

Macro-scale distillation ecosystem across 1,000 repositories rather than a standalone subtask procedure. Methodological principles are captured in `skill-design-methodology` and `rules/skill-system-design.md`.

---

## Core Concept

Autonomous research agents combine backbones with harnesses for planning, execution, and memory, but lack domain-specific operational know-how—the knowledge separating understanding a method from making it run successfully. Repo-To-Skill distills 1,000 machine learning repositories into AREX-Skill, a library of 5,000+ verified skills organized into 20 domains and 178 capability families, supporting both task-agnostic repository condensation and task-oriented on-demand skill synthesis.

### Key Finding

Equipping a research agent with distilled operational skills yields dramatic benchmark improvements under fixed model and execution budgets:
- **MLE-bench**: **+134.3%** higher score over the unaugmented agent.
- **PaperBench**: **+34.4%** gain.
- **PassNet / FrontierCS**: **+14.0%** and **+9.2%** improvements.

## Relevance to Praxis

- Confirms that operational know-how (environment setup, parameter tuning heuristics, error handling) is the primary bottleneck in agent code generation, validating the Praxis skill architecture.
