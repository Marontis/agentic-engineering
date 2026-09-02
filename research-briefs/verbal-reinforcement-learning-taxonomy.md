# The Rise of Verbal Reinforcement Learning (VRL)

> **Paper**: [The Rise of Verbal Reinforcement Learning](https://arxiv.org/abs/2609.01597)
> **Praxis source**: src:2609-01597v1

## Why Not a Skill?

Taxonomic survey unifying language-based feedback literature across agent design, reinforcement learning, and fine-tuning.

---

## Core Concept

Natural language is replacing scalar reward signals as the primary feedback medium for AI agents. Verbal Reinforcement Learning (VRL) unifies this paradigm across three distinct lifecycle pillars:
1. **Language as Grounding Signal**: Natural language specifies goals, action spaces, and environment contracts.
2. **Language as Deliberative Feedback**: In-context verbal critiques (Reflexion, self-refinement) operate at inference time to guide search.
3. **Language as Learning Signal**: Natural language trajectories drive offline preference optimization (DPO, RLHF, instruction tuning).

## Relevance to Praxis

- Provides the conceptual framework connecting run-time reflection skills with offline training pipelines.
- Supports our focus on text-based skill memory over numerical embeddings alone.
