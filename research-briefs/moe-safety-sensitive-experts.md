# Safety-Sensitive Experts in Sparse MoE LLMs

> **Paper**: [Frequency Is Not Sensitivity: Identifying Safety-Sensitive Experts in Sparse MoE LLMs](https://arxiv.org/abs/2610.02910)
> **Praxis source**: src:2610-02910

## Why Not a Skill?

A model-internals security finding for Mixture-of-Experts models. It informs
threat models for self-hosted open-weight MoE deployments but gives agent
builders no procedure to follow.

---

## Core Concept

Suppressing a few routed experts can weaken an MoE model's refusals without
retraining. The question is which experts matter. The paper compares ranking
by **activation frequency** with ranking by **router-gradient sensitivity**
(sensitivity of sequence loss to the gate weights selecting an expert),
across five MoE models (Mixtral, Qwen1.5-MoE, DeepSeek, OLMoE, Qwen3; 256 to
6,144 routed experts). Experts are ranked on 500 benign (AEGIS2.0) and 500
malicious (AdvBench) prompts; refusal is measured on a disjoint set of 100
malicious prompts with manual labels (restricted, compliant, degraded).

### Key Finding

- **Gradient beats frequency**: under equal-expert-count and
  equal-routing-traffic (1%–5%) budgets, router-gradient selection reduced
  refusals more than activation in 24 of 25 conditions each, and more than a
  ten-trial random mean in all 25.
- **Largest effect**: OLMoE refusals fell from 34 to 9 of 100 prompts
  (73.53% relative) with no degraded outputs, i.e., substantive compliance.
  DeepSeek reached 28.05% reduction at the 5% target versus 9.76%
  (activation) and 5.61% (random).
- **Sensitive experts sit deeper**: gradient-selected experts averaged 68.2%
  normalized depth versus 50.9% for activation-selected ones.
- **Exploratory**: larger malicious-vs-benign routing concentration gaps
  went with larger effects (Spearman ρ = 0.90, exact p = 0.083, n = 5).

## Relevance to Praxis

- **Threat model for self-hosted MoE**: anyone who can modify routing or
  expert weights in a deployment can remove safety behavior cheaply; treat
  model artifacts and serving configuration as integrity-protected.
- **Frequency-based audits mislead**: when auditing which components carry
  safety behavior, measure influence, not usage.
