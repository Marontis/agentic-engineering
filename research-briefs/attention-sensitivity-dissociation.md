# Attention Sensitivity Is Not Enough for ICL Diagnostics

> **Paper**: [Attention Sensitivity Is Not Enough: Dissociating Attention-Level and Behavioural In-Context Learning under Fine-Tuning](https://arxiv.org/abs/2609.00064)
> **Praxis source**: src:2609-00064v1

## Why Not a Skill?

Mechanistic interpretability critique of evaluation metrics, not an actionable agent engineering workflow.

---

## Core Concept

Diagnostics for in-context learning (ICL) frequently inspect attention maps (e.g., induction head activation sensitivity) as a proxy for whether a model retains context-sensitivity after fine-tuning. The authors demonstrate a systematic dissociation: models can exhibit high attention sensitivity while suffering catastrophic collapse in behavioral in-context accuracy.

## Relevance to Praxis

- Enforces the principle that agent capability must be validated on behavioral task outcomes, never by internal attention or representation proxies alone.
