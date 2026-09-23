# ZeroGate: Trust-Preserving Fast Paths for Governed AI Agent Runtimes

**Source**: Wang, "ZeroGate: Trust-Preserving Fast Paths for Governed AI
Agent Runtimes" (arXiv:2609.25443), Sep 2026.

## Key Findings

- Separates exact-action approval from durable local admission: an
  issuer signs a short-lived ActionPass, and a trusted runtime adapter
  reconstructs the final action before a local gate checks its binding
  and consumes its nonce
- SQLite transaction couples nonce consumption, quota updates, and
  admission receipt atomically
- Prepared worker-admission-to-dispatch p95: 9.8–11.4 ms vs. 25–334 ms
  synchronous across tested concurrency levels
- Prepared mean complete lifecycle is LONGER — boundary improvement is
  not a net speedup; the contribution is an explicit revalidation
  contract and auditable comparison

## Relevance to Agentic Engineering

ZeroGate provides a formal pattern for moving authorization earlier in
the agent dispatch pipeline without removing authorization work. The
ActionPass + nonce consumption model is relevant to any governed agent
runtime needing fast-path execution with audit guarantees.

## Why Not a Skill?

Niche implementation pattern for a specific runtime authorization
architecture. The revalidation contract concept enriches understanding
of governed agent runtimes but isn't a standalone transferable procedure
— it requires specific infrastructure (trusted adapter, SQLite
transactions, ActionPass issuance).

> Source: arXiv:2609.25443
