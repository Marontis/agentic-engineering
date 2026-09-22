# From Intent to Action: Benchmarking LLM Safety in Vehicle Voice Command Authorization

> **Source**: Afroze et al., arXiv:2609.19630, Sep 2026
> **Status**: Research Brief — benchmark study with safety implications

## Why Not a Skill?

This is a benchmark evaluation with a 202-scenario taxonomy, not a transferable procedure. The core finding reinforces existing sandboxing rules rather than introducing a new method.

## Core Concept

Vehicle voice assistants powered by LLMs face a safety-critical authorization problem: before executing a command, the system must decide between seven action classes (execute, refuse, clarify, require confirmation, defer to manual, trigger emergency, no tool call). The study evaluates whether LLM decisions alone can serve as a reliable authorization mechanism.

## Key Findings

- Decision alignment ranges from 40.1% (Llama 3.2 3B) to 89.1% (Gemini 3.1 Pro Preview)
- Even frontier API models (83.2%–89.1%) produce **2–3 False Executes among 161 non-execution scenarios**
- Structured authorization policies improve weaker models (40.1% vs 28.2–29.2% baselines) but do not eliminate False Executes
- **Key conclusion**: Structured LLM decisions are **insufficient as a standalone safety mechanism** — deployment requires an **independent enforcement layer** that verifies tool permissions and vehicle-state constraints

## Relevance to Praxis

- Validates the existing sandboxing rule: LLM authorization decisions must be backed by an independent enforcement layer
- 2–3 False Executes per 161 scenarios even for frontier models provides a concrete failure rate for risk modeling
- The seven-class action taxonomy is reusable for other safety-critical agent authorization systems

> Source: Afroze et al., "From Intent to Action" (arXiv:2609.19630)
