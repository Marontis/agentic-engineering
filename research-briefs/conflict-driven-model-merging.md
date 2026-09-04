# CoMerge: Conflict-Driven Preference Optimization for Model Merging

> **Paper**: [CoMerge: Conflict-Driven Preference Optimization for Multi-Task Model Merging](https://arxiv.org/abs/2609.02273)
> **Praxis source**: src:2609-02273v1

## Why Not a Skill?

Model parameter merging technique operating in weight space rather than an in-context agent subtask.

---

## Core Concept

Model merging combines specialized expert models (e.g., coding, math, safety) into a single unified backbone without full retraining. However, parameter-space interference often degrades performance when task vectors conflict. CoMerge reformulates merging as preference optimization: it uses outputs from naive merges (task arithmetic) as hard negative samples and expert outputs as positive samples, optimizing lightweight tensor-wise merging scalar coefficients (1,445 parameters on Llama-3.1-8B) to resolve directional parameter conflicts.

### Key Finding

CoMerge achieves an average normalized score of **0.9968** on MergeBench, outperforming existing data-free and data-driven merging baselines while preserving domain capabilities and safety alignment.

## Relevance to Praxis

- Provides an efficient strategy for constructing unified multi-capability agent backbones from open-source domain-specific models without the cost of joint full-parameter training.
