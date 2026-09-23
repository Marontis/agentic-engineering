# Dynamic Deep Prompt Optimization for Jailbreak Defense

**Source**: Obidov et al., "Dynamic Deep Prompt Optimization for Defending
Against Jailbreak Attacks on LLMs" (arXiv:2609.26185), Sep 2026.

## Key Findings

- DDPO uses the target LLM's own intermediate layers as feature extractors
  to dynamically generate defensive embeddings via a lightweight MLP
- Tailored embeddings are injected into a subsequent intermediate layer,
  enabling input-dependent defense without modifying LLM weights
- Significantly outperforms static prompt optimization methods on weakly
  aligned models and when handling semantically ambiguous benign prompts
- Successfully distinguishes genuinely harmful requests from ambiguous
  benign prompts

## Relevance to Agentic Engineering

DDPO demonstrates that jailbreak defense can be input-adaptive without
weight modification. The intermediate-layer injection approach could
inform agent-level safety layers that need to adapt to diverse inputs
without model fine-tuning.

## Why Not a Skill?

DDPO requires access to intermediate model layers for feature extraction
and embedding injection — a model-architecture-specific implementation
that doesn't transfer as a general-purpose agent procedure. The
contribution is a defense architecture, not a reusable subtask workflow.

> Source: arXiv:2609.26185
