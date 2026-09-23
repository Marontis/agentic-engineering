# Silent Sabotage: Internal State Triggered Backdoor Attacks on LLM-Powered Robotic Systems

**Source**: Obidov et al., "Silent Sabotage: Internal State Triggered
Backdoor Attacks on LLM-Powered Robotic Systems" (arXiv:2609.26184),
Sep 2026.

## Key Findings

- Backdoor attacks on LLM-powered robotic systems can be triggered by
  internal state conditions rather than external input patterns
- The attack surface extends beyond prompt-level manipulation to
  runtime state-dependent triggers
- Demonstrates that safety-critical robotic systems face unique
  backdoor risks when controlled by LLMs

## Relevance to Agentic Engineering

Extends the backdoor attack taxonomy beyond prompt injection to
state-dependent triggers. Relevant for any agent system where LLM
outputs drive physical or high-consequence actions. Reinforces the
need for runtime monitoring beyond input sanitization.

## Why Not a Skill?

Domain-specific to robotic systems. The attack characterization informs
threat modeling but doesn't provide a transferable defense procedure.

> Source: arXiv:2609.26184
