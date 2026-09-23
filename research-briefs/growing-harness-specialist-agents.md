# Grow the Harness, Not the Context: Strategy-Free Scaffolds to Reusable Specialist Agents

**Source**: Li et al., "Grow the Harness, Not the Context: From
Strategy-Free Scaffolds to Reusable Specialist Agents"
(arXiv:2609.26760), Sep 2026.

## Key Findings

- Growing Harness: failure-guided paradigm that learns the agent harness
  from a strategy-free scaffold (fixed model and tool interfaces, no
  task-solving controller)
- Function-level execution traces localize each failure to a bounded
  code surface; optimizer repairs a window of failures jointly
- Success-first held-out gate rolls back repair sequences that harm
  prior capability
- Achieves highest mean success in 5/6 benchmark-model settings
- Reduces LLM calls by 76–92% and inference cost by 74–99%
- Performance holds at 44.7–45.3% across model scales (4B to 120B),
  while Tool-Calling falls to 6.7% at 4B

## Relevance to Agentic Engineering

Growing Harness shows that persistent program growth can move recurring
control out of model context into low-cost code. The trace-local edit,
joint repair, and gate-based rollback pattern extends harness evolution
methodology. Particularly relevant for deployment with smaller models.

## Why Not a Skill?

The paradigm is a complete system design (scaffold, trace localization,
joint repair, held-out gate) rather than a standalone transferable
procedure. Extends the harness engineering context documented in existing
skills (reference-trajectory-harness-evolution, belief-calibrated-scaffold-optimization).

> Source: arXiv:2609.26760
