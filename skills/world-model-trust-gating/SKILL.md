---
name: world-model-trust-gating
description: >
  Decide when to trust a learned world model's predictions for agent
  decision-making via the verify-then-promote rule. Admits a
  world-model-guided decision only when its predicted advantage exceeds
  a certified bound on decision-relevant model error; otherwise
  allocates evidence to world-model verification.
  Derived from "Dual-Frontier: When Can an Agent Trust Its World
  Model?" (arXiv:2609.26293).
source: https://arxiv.org/abs/2609.26293
---

# World Model Trust Gating (Dual-Frontier)

Use this skill when an agent uses a learned world model for planning
or decision-making, and you need a principled gate to decide when to
trust the model's predictions vs. when to gather more evidence.

## When to Use

- Agent relies on a learned world model for planning or action
  selection
- When a world-model-guided decision fails, you cannot tell from the
  trajectory alone whether the decision rule or the world model caused
  the failure
- You need guaranteed non-decreasing return for admitted decisions
- Agent operates in environments where world model quality varies
  across states or actions

## Core Insight

When a world-model-guided decision fails, the trajectory alone may
not reveal whether the agent's **decision rule** or the **world
model** caused the loss. Dual-Frontier proves this
failure-attribution problem is not identifiable from passive
interaction, even for finite-horizon planners. The solution:
**verify-then-promote** — admit a world-model-guided decision ONLY
when its predicted advantage exceeds a certified bound on
decision-relevant world-model error. Otherwise, allocate evidence to
world-model verification.

**Evidence**: Controlled experiments validate predicted failure modes.
Cross-backbone tool-use benchmarks show the same verify-then-promote
rule consistently improves decision quality and reliability.

---

## Procedure

### 1. Formalize the Decision-Relevant Error Bound

1. For each candidate world-model-guided action, compute the
   **predicted advantage** — how much better the world model predicts
   this action is compared to a default policy
2. Compute the **decision-relevant world-model error** — the bound
   on how wrong the world model could be for THIS specific
   action-state pair
3. The error bound must be **action-conditioned** — global model
   accuracy is insufficient; what matters is accuracy on the specific
   decision at hand

### 2. Apply the Verify-Then-Promote Gate

For each decision point:

1. If predicted_advantage > certified_error_bound → **PROMOTE**:
   execute the world-model-guided action
2. If predicted_advantage ≤ certified_error_bound → **VERIFY**:
   do NOT execute; instead allocate evidence to refine the world
   model for this state-action region
3. Promoted decisions carry a **non-decreasing return guarantee**:
   they are at least as good as the default policy

### 3. Manage Evidence Allocation

When the gate selects VERIFY:

1. Execute an evidence-gathering action (e.g., the default policy,
   an exploration action, or a probe)
2. Use the resulting observation to update the world model's error
   bound for the relevant state-action region
3. Apply **adaptive evidence reuse**: calibrated gates and
   simultaneous confidence sequences allow previously gathered
   evidence to tighten bounds without fresh data

### 4. Calibrate the Gate

1. Use **calibrated gates** — the error bounds should be calibrated
   (neither systematically over- nor under-confident)
2. Apply **simultaneous confidence sequences** — these provide
   time-uniform validity, meaning the gate remains correct as
   evidence accumulates
3. Both **sufficient and necessary verification bounds** are
   supported: sufficient bounds guarantee safety, necessary bounds
   avoid over-verification

### 5. Implement the Closed-Loop Extension

For multi-step planning:

1. The verify-then-promote rule extends to **closed-loop** settings
   where each decision depends on previous outcomes
2. At each step, re-evaluate the gate with updated evidence
3. The non-decreasing return guarantee holds across the full
   trajectory, not just individual decisions

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Over-verification | Error bounds too conservative | Use necessary (not just sufficient) verification bounds |
| Under-verification | Error bounds too loose | Calibrate gates; tighten with simultaneous confidence sequences |
| Stale error bounds | World model changes but bounds are not updated | Re-calibrate after model updates; track bound validity |
| Default policy is poor | Verification falls back to bad default | Improve default policy; verify gate assumes competent default |
| Evidence waste | Verification gathers unhelpful evidence | Target evidence to the specific state-action region that triggered verify |

> Source: Zhu et al., "Dual-Frontier: When Can an Agent Trust Its
> World Model?" (arXiv:2609.26293), Sep 2026.
