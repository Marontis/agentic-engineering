# RISE: Recursive Improvement via Self-Extrapolating Policy Distillation

> **Paper**: [RISE: Recursive Improvement via Self-Extrapolating Policy Distillation](https://arxiv.org/abs/2609.05295)
> **Praxis source**: `src:2609-05295v1`
> **Primary topic**: Agent Self-Improvement & Harness Engineering

## Why Not a Skill?

This paper describes a model training or fine-tuning methodology tied to specific architectures and training infrastructure. The insights are valuable context, but the procedure is not directly transferable as an agent-level subtask.

---

## Core Concept

On-policy distillation (OPD) provides dense, per-token supervision for language model post-training, but its effectiveness is bottlenecked by teacher quality: external teachers suffer from distribution mismatch, while self-distillation with privileged conditioning is limited by in-context learning capacity. We propose RISE (Recursive Improvement via Self-Extrapolating Policy Distillation), which constructs a synthetic teacher directly from the model's own RLVR training trajectory. By extrapolating the displacement between the current checkpoint and a trailing anchor---in parameter space or output logit space---RISE converts a sparse outcome-induced parameter update into a dense token-level target, without any external model or privileged conditioning. RISE combines RLVR and OPD in a complementary loop: outcome rewards ground the extrapolation toward correct reasoning, while the extrapolated teacher refines token-level decisions. Moreover, since the teacher is refreshed every iteration as the student improves, distillation becomes a recursive improvement mechanism rather than a one-shot compression step. Experiments spanning mathematical reasoning, multi-domain STEM, code generation, and multi-turn agentic tasks show that RISE outperforms RLVR-only training and on-policy self-distillation across all settings.

### Key Findings

- **Primary Result**: See abstract for qualitative findings.

## Relevance to Praxis

- Relevant to agent self-improvement loops and harness engineering.
