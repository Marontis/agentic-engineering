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
- For **weaker models**: accuracy scaffold (improves results)
- For **stronger models**: cost saver (same accuracy, fewer tokens)
- Little accuracy change for strong models with or without planning

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
- For strong models: drop predefined tools, use bash-only, and convert planning to cost savings

> Source: Fan et al., "An Empirical Study of Harness Design for Coding Agents" (arXiv:2609.20804)
