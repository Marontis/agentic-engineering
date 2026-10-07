# Steering Dimensionality of Refusal

> **Paper**: [On the Steering Dimensionality of Refusal in Language Models](https://arxiv.org/abs/2610.04245)
> **Praxis source**: src:2610-04245

## Why Not a Skill?

An interpretability study of activation geometry on two small models. It
informs how much to trust steering-based safety controls but contains no
agent-level procedure.

---

## Core Concept

The paper defines **steering dimensionality**: the smallest subspace
dimension that reliably controls a behavior, judged by two interventions
that must both work: additive steering should induce the behavior, and
directional ablation should suppress it. It compares refusal triggered by
safety alignment (harmful vs harmless prompts) with refusal in general,
non-safety contexts, building subspaces with K-Means, SVD and difference-of-
means constructions, on Qwen2.5-3B-Instruct and Llama-3.1-8B-Instruct
(200 contrastive examples; 50 examples per ablation setting; 3 rollouts per
input).

### Key Finding

- **Safety refusal is 1-dimensional**: a single direction controls it, and
  several distinct directions achieve comparable control, consistent with
  Arditi et al. (2024).
- **General refusal is not**: even 5-dimensional subspaces fail to capture
  its full steerable variation. On Llama-3.1-8B-Instruct, additive
  steerability largely saturates beyond 3 dimensions (K-Means), yet
  directional ablation stays ineffective in all four evaluation settings.
- **Limits**: two instruction-tuned models only; the authors call for broader
  evaluation.

## Relevance to Praxis

- **Steering controls are context-specific**: a single refusal direction is a
  reasonable lever for safety refusal (as used by
  [SENTINEL](sentinel-intent-matching-jailbreak-defense.md) and
  [EmoRSS](emotion-induced-over-refusal.md)), but do not assume the same
  vector governs refusal behavior in other contexts.
- **Ablation and induction can disagree**: validate any steering-based
  control in both directions before relying on it.
