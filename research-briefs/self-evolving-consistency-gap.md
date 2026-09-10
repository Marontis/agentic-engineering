# Closing the Consistency Gap: Self-Evolving Agents That Learn to Stay on Course

> **Paper**: [Closing the Consistency Gap](https://arxiv.org/abs/2609.08832)
> **Praxis source**: `src:2609-08832v1`

## Why Not a Skill?

Architecture â€” tied to a specific self-evolving consistency mechanism. The core insight (agents drift from their stated goals during long tasks) is valuable context but the fix is too coupled to the specific architecture.

---

## Core Concept

Agents in long-horizon tasks gradually drift from their original goals â€” making decisions that individually seem reasonable but collectively deviate from the stated objective. Self-evolving consistency mechanisms detect and correct this drift by periodically re-anchoring the agent to its original intent.

### Key Insight

Goal drift is not a failure of understanding but a failure of memory â€” the agent "forgets" its original intent as the context window fills with recent, locally-relevant information.

## Relevance to Praxis

- Supports the `agent-working-memory-eval` skill â€” goal drift is a consequence of poor working memory management
- Informs the `prefix-preserving-context-assembly` skill â€” preserving the original task description as a stable prefix prevents drift
