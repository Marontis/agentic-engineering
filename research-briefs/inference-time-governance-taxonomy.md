# Beyond Training: A Feasibility Taxonomy for Inference-Time AI Governance

> **Paper**: [Beyond Training](https://arxiv.org/abs/2609.10105)
> **Praxis source**: `src:2609-10105v1`

## Why Not a Skill?

Taxonomy â€” classifies inference-time governance mechanisms by feasibility, not by implementation procedure.

---

## Core Concept

AI governance traditionally focuses on training-time interventions (data curation, RLHF, safety training). This paper maps the landscape of inference-time governance: what can be controlled after the model is deployed? Classifies mechanisms by technical feasibility, regulatory alignment, and deployment cost.

### Key Categories

- **Output filtering**: Post-hoc classification and blocking (high feasibility, low coverage)
- **Steering vectors**: Real-time behavioral modification (medium feasibility, requires model access)
- **Runtime monitoring**: Trajectory-level behavioral analysis (high feasibility, reactive not preventive)
- **Capability gating**: Dynamic tool/resource access control (high feasibility, proactive)

## Relevance to Praxis

- Maps to the `unified-capability-gateway` skill (capability gating) and `black-box-trajectory-risk-monitoring` skill (runtime monitoring)
- Informs which governance mechanisms are feasible for different deployment contexts
