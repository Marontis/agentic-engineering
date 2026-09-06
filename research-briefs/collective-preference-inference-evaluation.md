# Collective-Centric Evaluation of Preference Inference

> **Paper**: [Toward Collective-Centric Evaluation of Preference Inference for Participatory Democracy](https://arxiv.org/abs/2609.02990)  
> **Praxis source**: `src:2609-02990`

## Why Not a Skill?

This paper introduces an evaluation methodology and dataset (spanning four consultations, >90,000 participants, 1M+ votes across 22 languages) for benchmarking Preference Inference (PI) in large-scale online deliberation. Because it establishes an evaluation benchmark and structural alignment criteria rather than an executable coding-agent procedure, it is maintained as a research brief informing collective agent consensus mechanisms.

---

## Core Concept

In large-scale deliberation systems (such as Polis, Remesh, or multi-agent democratic consensus engines), thousands of participants submit statements and vote. Because human participants or distributed agents cannot evaluate every submitted proposal, the resulting voting matrix is extremely sparse (often <5% observed entries).

Platforms increasingly deploy **Preference Inference (PI)** models (matrix factorization, collaborative filtering, LLM imputers) to predict missing votes. However, AI-driven vote imputation is not neutral:
- Inferred preferences can artificially inflate false consensus.
- Inferred votes can erase vocal minority dissent.
- Inferred preferences can reorder ranked policy outcomes, distorting democratic intent.

### Point-Wise Accuracy vs. Collective Landscape Preservation

Standard machine learning evaluates preference models using **point-wise individual accuracy** (e.g., Accuracy, AUC, RMSE on held-out votes). The authors demonstrate that point-wise accuracy is deeply misleading: two models with identical individual prediction accuracy can produce drastically different macro-level collective outcomes.

```
                  Sparse Deliberation Voting Matrix
                 ┌─────────────────────────────────┐
                 │ Agent 1: [ +1,   ?,  -1,   ?,  +1 ] │
                 │ Agent 2: [  ?,  +1,   ?,  -1,  -1 ] │
                 │ Agent 3: [ -1,   ?,  +1,   ?,   ? ] │
                 └────────────────┬────────────────┘
                                  │
                                  ▼
                     Preference Inference Imputation
                                  │
     ┌────────────────────────────┴────────────────────────────┐
     ▼                                                         ▼
Model A (Point Accuracy: 84%)             Model B (Point Accuracy: 84%)
Preserves minority polarization clusters  Collapses variance into false majority
[True Democratic Distribution]            [Monoculture Distortion]
```

The authors introduce a **collective-centric evaluation framework** that assesses:
1. **Consensus Preservation**: Does imputation maintain genuine shared agreement across opposing clusters?
2. **Conflict & Polarization Preservation**: Does imputation preserve the principal dimensions of disagreement without artificially smoothing polarization?
3. **Minority Voice Retention**: Does the imputed matrix protect minority viewpoints from being mathematically overwhelmed by dominant majority clusters?

---

## Relevance to Praxis

- **Multi-Agent Deliberation & Voting**: When aggregating opinions or rankings across agent swarms (as in multi-agent debate or ensemble voting), judging consensus models by individual prediction accuracy is insufficient. Harnesses must evaluate whether the collective landscape preserves diversity and minority objections.
- **Democratic Agent Governance**: Directly connects to `debate-consensus-memory-calibration` and pluralistic agent topologies, providing metrics to measure whether synthetic agent consensus reflects genuine alignment or algorithmic compression.
