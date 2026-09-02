# Checklist Aggregation Evaluation Pipeline

> **Paper**: [Towards a Reliable and Practical Eval Pipeline](https://arxiv.org/abs/2609.00805)
> **Praxis source**: src:2609-00805v1

## Why Not a Skill?

Evaluation pipeline design pattern for LLM quality gates, complementing existing evaluation skills rather than introducing a standalone subtask procedure.

---

## Core Concept

Evaluations are critical quality gates in agentic software lifecycles, but single-score LLM-as-a-judge prompts suffer from poor calibration and low inter-rater agreement. This framework combines:
1. **Eval checklist creation**: Decomposes high-level evaluation criteria into fine-grained, objective boolean/categorical checklist items.
2. **Learned aggregation**: Learns optimal weighting and aggregation over checklist outputs to predict human quality ratings with calibrated uncertainty estimates.

### Key Finding

Checklist decomposition combined with learned aggregation significantly outperforms raw LLM ratings in agreement with human domain experts, while providing interpretable failure rationales and self-consistency bounds.

## Relevance to Praxis

- Informs how automated code review and quality assurance agents should score generated artifacts.
- Enforces decomposing complex evaluations into atomic binary checks.
