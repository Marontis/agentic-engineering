# FlowBalance: Verifier-Grounded Self-Improvement via Trajectory Balance

> **Paper**: [FlowBalance: Verifier-Grounded Self-Improvement from On-Policy Reasoning Experience](https://arxiv.org/abs/2609.03241)
> **Praxis source**: src:2609-03241v1

## Why Not a Skill?

Post-training reinforcement learning algorithm modifying underlying model weights via trajectory balance rather than an in-context agent procedure. Key insights on verifier calibration inform `rules/recursive-improvement.md`.

---

## Core Concept

Post-training self-improvement loops face two competing failure modes: sparse terminal verifier rewards provide reliable grounding but fail to guide token-level search, while dense self-guidance from the same model suffers from self-confirmation bias and length collapse. FlowBalance combines privileged training-time token-level guidance with verifier-derived group advantages via trajectory balance, reweighting policy distributions with exact corrections against false-positive guidance on rejected trajectories.

### Key Finding

On mathematical reasoning benchmarks (AIME24, GSM8K), FlowBalance consistently outperforms FlowRL and on-policy distillation on both Qwen3-4B and Qwen3-8B. It maintains high correct-strategy diversity and completely avoids the response-length collapse common in self-guidance baselines.

## Relevance to Praxis

- Confirms that self-improvement systems must calibrate internal model confidence against external deterministic verifiers; ungrounded self-reflection reinforces false modes.
