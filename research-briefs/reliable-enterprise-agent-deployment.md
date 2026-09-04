# READY: Reliable Enterprise Agent Deployment Framework

> **Paper**: [READY or Not: Reliable Enterprise Agent Deployment](https://arxiv.org/abs/2609.02095)
> **Praxis source**: src:2609-02095v1

## Why Not a Skill?

Comprehensive enterprise-level evaluation and deployment methodology from Scale AI. High-level governance principles are distilled into rules.

---

## Core Concept

Enterprise deployment of autonomous agents requires moving beyond generic academic benchmarks (e.g., SWE-bench, GAIA) to structured reliability engineering. READY establishes a five-tier deployment readiness framework:
1. Environment and tool contract fidelity.
2. Failure mode taxonomy coverage.
3. Guardrail and boundary testing (prompt injection, out-of-scope tasks).
4. Cost-latency Pareto optimization.
5. Continuous production observability and drift detection.

### Key Finding

Evaluating agents across realistic enterprise workloads reveals that tool interface misalignment and unhandled API edge cases account for over **54% of production failures**, outweighing pure model reasoning errors.

## Relevance to Praxis

- Establishes enterprise criteria for production-ready agent skills, emphasizing that tool contracts and error-recovery handlers must be tested under adversarial conditions before deployment.
