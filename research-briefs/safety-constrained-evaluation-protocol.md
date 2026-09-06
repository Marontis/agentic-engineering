# Safety-Constrained Evaluation Protocol (FLY-EVAL++)

> **Paper**: [FLY-EVAL++: An Evidence-Driven Evaluation Protocol for Safety-Constrained Flight Prediction with Large Language Models](https://arxiv.org/abs/2609.04021)  
> **Praxis source**: `src:2609-04021`

## Why Not a Skill?

*FLY-EVAL++* introduces a domain-specific evaluation benchmark and dataset for aviation flight trajectory and attitude prediction (FTAP). While the specific flight dynamics equations and PilotBench extensions are domain-bound, the universal methodology—deterministic constraint satisfaction and physical feasibility verification as primary quality gates ahead of accuracy—is codified into `rules/agent-sandbox-safety.md`.

---

## Core Concept

In safety-critical or physics-governed environments, conventional evaluation metrics (e.g., Mean Absolute Error, MSE, R-squared, cosine similarity) present a dangerous blind spot: an agent's prediction can be numerically close to ground truth while catastrophically violating physical boundaries, airspace separation minimums, or structural aircraft limits.

FLY-EVAL++ establishes a multi-dimensional, evidence-driven evaluation framework combining:
1. **Protocol Compliance**: Verifying structured JSON/schema validity and required field presence.
2. **Physical Feasibility**: Verifying that predicted acceleration, climb rates, turn rates, and aerodynamic envelopes adhere to kinematic laws.
3. **Safety Constraint Satisfaction**: Checking strict operational invariants (e.g., terrain clearance, stall margins, velocity ceilings).
4. **Multi-Step Rollout Stability**: Evaluating cascading error accumulation across multi-horizon autoregressive predictions.

```
+───────────────────────────────────────────────────────────────────+
|               FLY-EVAL++ Multi-Dimensional Audit                  |
+-----------------------------------+-------------------------------+
|  Dimension                        |  Verification Method          |
+-----------------------------------+-------------------------------+
|  1. Structured Protocol Validity  |  Deterministic Schema Parser  |
|  2. Kinematic Feasibility         |  Differential Physics Engine  |
|  3. Operational Safety Bounds     |  Boundary Constraint Checker  |
|  4. Predictive Accuracy (MAE)     |  Statistical Ground-Truth Loss|
+-----------------------------------+-------------------------------+
```

### Key Findings Across 66 LLMs

- **The Safety Divergence**: Safety compliance was the **single most discriminative metric** across all 66 evaluated frontier and open-weight models. Models exhibiting virtually identical predictive accuracy differed by more than **28 points** in their safety compliance scores.
- **Plausible yet Fatal Violations**: Models frequently produced outputs that appeared superficially reasonable to human evaluators or soft metrics but violated hard physical invariants (e.g., impossible instant attitude inversions or stall-speed violations).
- **Multi-Step Instability**: Error compounding during multi-step rollouts rapidly degraded structural integrity even when single-step prediction error was minimal.

---

## Relevance to Praxis

- **Deterministic Gates Before Accuracy**: When evaluating agent tools, code generation, or trajectory planners, accuracy or loss must never serve as the sole pass/fail criterion. Deterministic verification of invariant constraints must gate execution before outputs are accepted into persistent memory.
- **Safety Benchmarking**: Validates Praxis's core thesis: agent safety evaluations require deterministic oracles and hard invariant checkers, not soft LLM-as-a-judge scoring.
