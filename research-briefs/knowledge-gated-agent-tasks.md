# Ignorance or Incompetence? Knowledge-Gated, Verifiable Tasks for LLM Agents

> **Paper**: [Ignorance or Incompetence? Constructing Knowledge-Gated, Verifiable Tasks for LLM Agents](https://arxiv.org/abs/2608.30322)
> **Praxis source**: `src:2608-30322v1`

## Why Not a Skill?

Evaluation methodology â€” separates knowledge failures from execution failures in agent benchmarks. No defense or improvement procedures.

---

## Core Concept

When an agent fails a task, is it because it doesn't *know* how (knowledge gap) or because it can't *do* it (execution gap)? These require different interventions: knowledge gaps need retrieval/skills, execution gaps need better tool use or planning. Knowledge-gated tasks verify that the agent has the requisite knowledge before testing execution.

### Key Insight

Agents that "know" how but can't "do" need different fixes than agents that don't know at all. Conflating the two failure modes leads to misdiagnosed improvement efforts.

## Relevance to Praxis

- Informs how the 	argeted-failure-attribution skill should classify failure root causes
- Relevant to skill library design â€” a skill should address a *knowledge* gap, while tool improvements address *execution* gaps
