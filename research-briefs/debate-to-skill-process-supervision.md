# Debate-to-Skill: Capability-Bound Process Supervision for Industrial Query-to-Agent Annotation

> **Paper**: [Debate-to-Skill](https://arxiv.org/abs/2609.11176)
> **Praxis source**: `src:2609-11176v1`

## Why Not a Skill?

Industrial annotation pipeline â€” describes a specific pipeline for converting user queries into agent capability annotations via structured debate. The pipeline is too domain-specific (annotation) for a general skill.

---

## Core Concept

Uses structured debate between annotator agents to determine whether a user query falls within an agent's capability bounds. Each debate round narrows the capability assessment, producing both a binary yes/no and a capability-gap analysis. The gap analysis feeds into skill expansion planning.

### Key Insight

Process supervision via debate produces better capability assessments than single-agent classification because the debate surfaces edge cases and boundary conditions that single agents miss.

## Relevance to Praxis

- The capability-gap analysis connects to the `capability-aware-skill-selection` skill's demand vector concept
- The debate-based assessment complements the `debate-layer-disagreement-analysis` skill
