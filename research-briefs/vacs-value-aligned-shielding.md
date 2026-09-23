# VACS: Value-Aligned Compositional Shielding for Multi-Agent Reasoning

**Source**: Zhang et al., "VACS: Value-Aligned Compositional Shielding
for Multi-Agent Reasoning" (arXiv:2609.26135), Sep 2026.

## Key Findings

- Four-layer framework: (1) value-dimension reward learning via
  Bradley-Terry + MaxEnt IRL, (2) Lean-inspired DSL for compositional
  assume-guarantee shields, (3) nucleolus-based credit allocation +
  Hamiltonian consensus for disagreement resolution, (4) critical
  reasoning path extraction for explanations
- Achieves 85.4% (medical QA), 95.0% (math), 90.0% (cybersecurity
  incident response) with near-zero logical inconsistency
- Addresses heterogeneous value priorities across agents (rigor vs.
  safety vs. conciseness)

## Relevance to Agentic Engineering

VACS demonstrates that formal compositional safety guarantees can
coexist with multi-agent disagreement resolution. The assume-guarantee
shield pattern is relevant to any multi-agent system requiring
verifier-constrained decisions.

## Why Not a Skill?

Highly integrated four-layer system with deep mathematical machinery
(IRL, nucleolus allocation, Hamiltonian optimization). Not decomposable
into a standalone transferable procedure. The contribution is a system
design, not a reusable subtask.

> Source: arXiv:2609.26135
