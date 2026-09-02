# APIFlow-Bench: Measuring Whether Agents Survive Long, Dependent API Workflows

> **Paper**: [APIFlow-Bench: Measuring Whether Agents Survive Long, Dependent API Workflows](https://arxiv.org/abs/2608.29128)
> **Praxis source**: `src:2608-29128v1`

## Why Not a Skill?

Benchmark â€” measures agent survival on multi-step API workflows with dependency chains. No defense or improvement procedures.

---

## Core Concept

Tests whether agents can execute long sequences of API calls where each call depends on the results of prior calls. Most agents fail catastrophically when dependency chains exceed 5â€“7 steps, with errors compounding through the chain.

### Key Finding

Agent failure modes on dependent workflows are qualitatively different from single-call failures â€” they involve state management errors, dependency tracking failures, and cascading error propagation rather than individual API misuse.

## Relevance to Praxis

- Informs how coding agents should handle multi-step tool call sequences
- The dependency chain failure mode is relevant to the 	ransactional-coding-sandbox skill's rollback design
