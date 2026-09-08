---
name: autonomous-research-to-launch-harness
description: >
  How to build an autonomous harness that coordinates LLM agents
  through multi-day research-to-deployment cycles using a multi-expert
  council, deterministic evidence-weighted exploration-exploitation,
  and layered knowledge systems.
  Derived from "AutoLR: Automating the Path from Research to Launch
  Review" (arXiv:2609.04871).
---

# Autonomous Research-to-Launch Harness

Use this skill when building or operating an agent harness that must
autonomously coordinate long-running, multi-day experimental cycles —
from research exploration through implementation, evaluation, and
deployment readiness.

## When to Use

- You are building an agent system that runs multi-day optimization
  loops (model tuning, A/B test evaluation, research reproduction)
- You need a council-based review mechanism to catch hallucinated
  proposals before they consume expensive compute
- You have a limited trial budget and need principled
  exploration-exploitation allocation across candidate directions
- Your agent needs to integrate external research knowledge with
  production-system knowledge and posterior evidence from experiments

## Core Insight

LLMs can assist with individual stages of a research-to-deployment
workflow (literature review, code generation, experiment design), but
the overall process remains human-dependent without a harness that
reliably coordinates them across long-running cycles.

Three system mechanisms enable autonomous coordination:

1. **Multi-expert council**: Multiple LLM agents debate and
   adversarially review proposals before they consume compute
2. **Deterministic evidence-weighted selector**: A non-LLM controller
   allocates limited trial budgets using exploration-exploitation
   with council reranking
3. **Layered knowledge system**: External research + production
   knowledge + domain-specific knowledge + posterior evidence from
   experiments

**Critical design principle**: LLM agents perform semantic reasoning
and code generation, while **deterministic controllers retain
authority** over execution, metric extraction, guardrails, and
persistent state transitions.

---

## Procedure

### 1. Set Up the Knowledge Layers

Build a three-layer knowledge system:

**Layer 1 — External research knowledge**:
- Research papers, technical reports, prior art
- Ingested and searchable (e.g., via Praxis)

**Layer 2 — Production-system knowledge**:
- System architecture, API docs, configuration schemas
- Performance baselines, known constraints, deployment requirements

**Layer 3 — Domain-specific + posterior evidence**:
- Domain expertise (your specific application context)
- Configurations, patches, logs, and outcomes from prior experiments
- This layer grows as the harness runs — each experiment adds evidence

### 2. Implement the Multi-Expert Council

The council reviews every proposal before it consumes resources:

1. **Proposer agent** generates a candidate direction (e.g.,
   "reproduce method X from paper Y, adapted for our architecture")
2. **Reviewer agents** (2–3) independently evaluate the proposal
   against the knowledge layers, checking:
   - Is this grounded in evidence from Layer 1?
   - Is it feasible given Layer 2 constraints?
   - Has something similar been tried (Layer 3)?
3. **Adversarial reviewer** specifically argues against the proposal,
   identifying risks, resource costs, and potential failure modes
4. **Decision**: Proposals must survive adversarial review to proceed;
   rejected proposals are logged with reasons for future reference

### 3. Configure the Exploration-Exploitation Selector

The selector is a **deterministic controller** (not an LLM) that
allocates a limited trial budget across candidate directions:

- **Exploration score**: How novel is this direction relative to
  prior experiments? (measured by distance from Layer 3 posteriors)
- **Exploitation score**: How promising based on council ranking
  and Layer 3 evidence?
- **Budget allocation**: Weighted combination, with council reranking
  to break ties
- **Termination**: A direction is terminated when its evidence
  (Layer 3 posteriors) shows diminishing returns against remaining
  budget

The selector MUST be deterministic — LLM agents propose and reason,
but the selector decides what runs and when to stop.

### 4. Execute with Deterministic State Transitions

Each experimental cycle follows a fixed state machine:

```
PROPOSED → COUNCIL_REVIEW → APPROVED/REJECTED
         → IMPLEMENTATION → TRAINING/EXECUTION
         → OFFLINE_EVALUATION → PASS/FAIL
         → ONLINE_EVALUATION (A/B) → PASS/FAIL
         → LAUNCH_REVIEW → SHIP/HOLD
```

State transitions are governed by the deterministic controller:
- LLM agents cannot skip states or self-promote
- Metric extraction from experiments is deterministic, not LLM-judged
- Guardrails enforce resource limits, safety checks, and rollback
  conditions at each transition

### 5. Accumulate Posterior Evidence

After each experiment, update Layer 3 with structured evidence:

```
experiment_id: str
direction: str              # What was tried
configuration: dict         # Exact parameters
outcome_metrics: dict       # Measured results
delta_vs_baseline: float    # Improvement over status quo
cost: float                 # Resources consumed
council_prediction: str     # What the council expected
prediction_error: float     # How wrong was the prediction?
```

This evidence informs future council reviews and selector decisions,
creating a compounding knowledge loop.

---

## Environment Caveats

- The multi-expert council adds latency (~3–5 LLM calls per
  proposal); acceptable for long-running cycles, not for real-time
- The deterministic selector requires explicit metric definitions
  upfront — fuzzy or qualitative outcomes need to be quantified
- Layer 3 evidence grows unboundedly; implement retention policies
  for old experiment records

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Council groupthink | All reviewers agree on a bad proposal | Mandate adversarial reviewer; rotate reviewer roles across cycles |
| Budget exhaustion on exploration | Too many novel directions tried | Set minimum exploitation fraction (e.g., ≥40% of budget on promising directions) |
| Stale knowledge | Layer 2 drifts from actual production system | Automated sync of production configs into Layer 2; staleness checks before experiments |
| LLM authority creep | Agent bypasses deterministic controller | Enforce state machine transitions in code, not in prompts; LLMs cannot call transition APIs directly |

## Cross-References

- [`knowledge-compounding-loop`](../../../../.gemini/config/skills/knowledge-compounding-loop/SKILL.md) —
  Three-layer workspace pattern for consolidating raw traces into persistent knowledge
- [`belief-calibrated-scaffold-optimization`](../../../../.gemini/config/skills/belief-calibrated-scaffold-optimization/SKILL.md) —
  Calibrate beliefs against rollout outcomes to prevent repeating refuted hypotheses
- [`reference-trajectory-harness-evolution`](../../../../.gemini/config/skills/reference-trajectory-harness-evolution/SKILL.md) —
  Evolve agent harness using reference trajectories

## Sources

- [AutoLR: Automating the Path from Research to Launch Review in Industrial Recommender Systems](https://arxiv.org/abs/2609.04871) (arXiv:2609.04871)
- Praxis source: `src:2609-04871`
