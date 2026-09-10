# CS-Guard: Benchmarking LLM Guardrails for Code Generation Security

> **Paper**: [CS-Guard](https://arxiv.org/abs/2609.09798)
> **Praxis source**: `src:2609-09798v1`

## Why Not a Skill?

Benchmark â€” systematically evaluates guardrails for code generation security but provides no new defense procedures. The finding that guardrails are weak is important context, not a transferable procedure.

---

## Core Concept

First benchmark to systematically evaluate guardrails for code generation security. Tests 9 guardrails across 7 LLMs on both text-to-code and code-to-code generation with jailbreak attacks.

### Key Findings

- For text-to-code: average attack success rate (ASR) after jailbreaks reaches ~50% for many guardrails
- For code-to-code: average ASR approaches 100% on base LLMs and remains high (14.4% to ~100%) across guardrails
- A novel "fictional scenario attack" (FSA) achieves ~100% ASR across many guardrails by embedding malicious intent in legitimate-looking development scenarios
- Code-to-code generation is dramatically harder to guard than text-to-code

## Relevance to Praxis

- Quantifies the weakness of current guardrails â€” informs the `layered-defense-ensemble` skill's defense stacking decisions
- FSA attack pattern is relevant to the `self-improving-red-team` and `taxonomy-driven-red-teaming` skills
- Code-to-code vulnerability is relevant to coding agent sandbox design
