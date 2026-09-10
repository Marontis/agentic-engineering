# Benchmark Scores Are Pipeline-Dependent: Cybersecurity LLM Audit

> **Paper**: [Benchmark Scores Are Pipeline-Dependent: A Reliability Audit of Cybersecurity LLM Benchmarks](https://arxiv.org/abs/2609.08765)
> **Praxis source**: src:2609-08765

## Why Not a Skill?

This is an empirical audit revealing systematic fragility in cybersecurity benchmark pipelines. The finding (pipeline choices can swing scores by 80+ percentage points) is a documented pitfall for benchmark consumers, not a transferable operational procedure.

---

## Core Concept

LLM benchmarks are treated as fixed datasets with stable scores, but their outcomes depend on configurable evaluation pipelines. This paper audits eight cybersecurity benchmarks across 10 LLMs, modeling benchmarks as measurement pipelines. It identifies 15 systematic failure modes where a single pipeline choice can change a model's score by more than 80 percentage points and substantially alter model rankings.

### Key Finding

- **Primary Result**: A single pipeline choice (prompt template, parsing strategy, scoring rubric) can change a model's score by **>80 percentage points** and alter rankings by **≥3 ranks** for 9 of 10 models tested.
- **Secondary Result**: Two semantically similar task pairs rank the same models differently due to incompatible evaluation conventions. Under a standardized harness preserving task semantics, rankings shift substantially.

## Relevance to Praxis

- **Benchmark skepticism**: Directly validates the `behavior-aware-verification` and `trajectory-aware-eval-pruning` skills — benchmark scores without pipeline specification are unreliable. Critical for any agent self-improvement loop using benchmark scores as reward signals.
- **Rule candidate**: DON'T compare benchmark scores across different evaluation pipelines without auditing pipeline choices. DO standardize pipeline configurations when comparing models.
- **Connects to reward hacking**: Pipeline-dependent scores are exactly the kind of imperfect proxy that enables reward hacking (see `reward-hacking-immunization` skill).
