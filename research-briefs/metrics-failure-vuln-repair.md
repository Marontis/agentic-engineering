# Metrics Failure in LLM-Based Code Vulnerability Repair

**Source**: Nepal et al., "Metrics Failure in LLM-Based Code Vulnerability
Repair: An Empirical Study and a Change-Aware Screen"
(arXiv:2609.26749), Sep 2026.

## Key Findings

- Standard code-generation metrics fail to capture repair quality in
  vulnerability repair tasks
- Proposes a change-aware screen that evaluates repairs against the
  specific vulnerability pattern, not just code correctness
- Empirical study across multiple LLM models shows systematic gap
  between metric scores and actual repair effectiveness

## Relevance to Agentic Engineering

Highlights a critical eval failure mode: metrics that appear to measure
task success but actually measure a correlated proxy. Directly relevant
to harness engineering and the behavior-aware verification skill —
evaluation must be scoped to what actually changed.

## Why Not a Skill?

The contribution is an empirical finding about metric failure modes plus
a domain-specific evaluation screen for vulnerability repair. The
finding reinforces existing behavior-aware verification principles but
doesn't introduce a transferable procedure.

> Source: arXiv:2609.26749
