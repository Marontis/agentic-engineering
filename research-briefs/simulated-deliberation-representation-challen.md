# From Simulated Citizens to Simulated Deliberation

> **Paper**: [From Simulated Citizens to Simulated Deliberation: Challenges in Representation](https://arxiv.org/abs/2609.07573)
> **Praxis source**: src:2609-07573

## Why Not a Skill?

This paper is a synthesis/taxonomy of challenges in using AI for democratic deliberation. It identifies representational, epistemic, and procedural challenges but does not describe a transferable subtask-level procedure for agent systems.

---

## Core Concept

The paper examines the progression from simulating individual citizens to simulating collective deliberation processes using LLMs. It synthesizes challenges around representation fidelity, preference aggregation, and the gap between simulated and genuine democratic participation.

### Key Finding

- **Primary Result**: Simulated deliberation faces fundamental representation challenges that differ from individual citizen simulation — collective dynamics, power asymmetries, and emergent consensus cannot be reliably captured by LLM personas.
- **Secondary Result**: The challenges intersect with known issues in multi-agent debate systems: majority skew, shared misconceptions, and preference inference distortion.

## Relevance to Praxis

- **Multi-agent deliberation limits**: Sets boundary conditions for when multi-agent debate (as in `debate-consensus-memory-calibration`) can substitute for genuine evaluation.
- **Governance design**: Relevant to `governed-knowledge-graph` and swarm governance patterns — AI deliberation systems need explicit representation auditing.
