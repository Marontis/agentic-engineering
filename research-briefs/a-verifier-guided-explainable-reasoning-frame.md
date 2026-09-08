# A Verifier-Guided Explainable Reasoning Framework with Gold-Anchored QLoRA, Task-Aware Mixture-of-Experts, and Group-Relative RLVR

> **Paper**: [A Verifier-Guided Explainable Reasoning Framework with Gold-Anchored QLoRA, Task-Aware Mixture-of-Experts, and Group-Relative RLVR](https://arxiv.org/abs/2609.05221)
> **Praxis source**: `src:2609-05221v1`
> **Primary topic**: Agent Self-Improvement & Harness Engineering

## Why Not a Skill?

This paper describes a model training or fine-tuning methodology tied to specific architectures and training infrastructure. The insights are valuable context, but the procedure is not directly transferable as an agent-level subtask.

---

## Core Concept

Large language models (LLMs) show strong reasoning ability, but their explanations can remain inconsistent, weakly grounded, or difficult to verify. We propose a verifier-guided explainable reasoning framework for transparent educational question answering that combines gold-anchored QLoRA, task-aware symbolic routing, and group-relative RLVR. Qwen2.5-3B-Instruct is first adapted with field-weighted QLoRA supervision anchored to authoritative answers. A lightweight router then assigns logic problems to a FOL/Z3 verifier and physics problems to a formula- and unit aware symbolic solver. Verifier feedback is further used to support candidate evaluation, self-revision, and reward construction during RLVR. Candidate responses are evaluated along three complementary dimensions: P1 for answer correctness, P2 for evidence or unit consistency, and P3 for reasoning depth and explainability. At inference, gold-free self-consistency aggregates multiple candidate responses before an optional question-only physics verifier performs conservative system-level correction. On 438 held-out examples, RLVR increases P3 from 50.68% to 72.20%, while hybrid P1 remains approximately stable at 55.94%. Self-consistency improves model only P1 from 48.86% to 50.23%, with symbolic verification providing the remaining hybrid gain. These results indicate that RLVR primarily strengthens explicit reasoning structure, while symbolic verification complements the neural policy by improving answer reliability at the system level.

### Key Findings

- **Primary Result**: On 438 held-out examples, RLVR increases P3 from 50.68% to 72.20%, while hybrid P1 remains approximately stable at 55.94%.
- **Additional Finding**: Self-consistency improves model only P1 from 48.86% to 50.23%, with symbolic verification providing the remaining hybrid gain.

## Relevance to Praxis

- Relevant to agent self-improvement loops and harness engineering.
