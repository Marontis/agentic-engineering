---
name: layered-defense-ensemble
description: >
  Stack LLM safety defenses with measured failure correlation, access-tier
  modeling, and cost-aware composition.  Defense layers are NOT independent —
  correlation must be measured, not assumed.  Derived from Alotaibi et al.
  (arXiv:2608.28327).
---

# Layered Defense Ensemble

Use this skill when designing or auditing a multi-layer defense stack for
LLM-based systems.  The key insight: defense layers correlate through the
model they wrap, so stacking delivers less than the product of individual
reported gains.

## When to Use

- You're stacking multiple safety defenses (input filters, alignment,
  output filters, auxiliary models)
- You need to decide which defenses to deploy and in what combination
- You're evaluating whether your defense stack actually compounds
- You're budgeting inference cost across defense layers

## Core Insight

Practitioners stack LLM defenses assuming layers compound multiplicatively.
But an ensemble compounds only if members fail on DIFFERENT inputs.
Measured failure correlation across 15 defense pairs shows φ from 0.30 to
0.75 (all positive), and the joint residual exceeds the multiplicative
prediction by up to 0.172.

The dependence is **architectural** — members correlate through the model
they all wrap, so no wider member pool weakens it.

**Evidence**: A seven-layer stack refuses 4 in 5 benign prompts while
remaining statistically indistinguishable from its strongest single layer
in attack-success rate.

## Procedure

### Step 1: Model the adversary using AATM

Classify your adversary by access tier:

| Tier | Access Level | Example |
|:-----|:------------|:--------|
| A0 | System-only (API access) | External user, no model knowledge |
| A1 | + Output logits/probabilities | API with probability endpoint |
| A2 | + Embedding/activation access | Self-hosted model, gray-box |
| A3 | + Model weights (white-box) | Open-weight model deployment |
| A4 | + Training data influence | Supply-chain or fine-tuning attack |

Each tier unlocks different attack classes AND different defense options.
Design your stack for the highest plausible adversary tier.

### Step 2: Classify defenses by inference cost

| Class | Description | Cost | Tier Required |
|:------|:-----------|:-----|:-------------|
| C0 | System prompt / template | Zero marginal | A0 |
| C1 | Input/output text filter | Low (pattern match) | A0 |
| C2 | Auxiliary classifier model | Medium (separate inference) | A0 |
| C3 | Activation/embedding monitor | High (requires activations) | A2+ |
| C4 | Training-time intervention | Amortized (fine-tuning) | A3+ |

### Step 3: Select defense members

Choose defenses from DIFFERENT cost classes to maximize diversity.
Within a cost class, defenses share implementation patterns and
correlate more strongly.

**Rule of thumb**: Coverage saturates within a tier.  Adding a third
C1 filter provides diminishing returns over two C1 filters.
Cross-tier combinations (C1 + C2 + C4) provide more diverse coverage.

### Step 4: Measure failure correlation (don't assume independence)

For each pair of defenses in your proposed stack:

1. Run a common attack set against the full stack
2. Record per-input pass/fail for each defense independently
3. Compute pairwise φ (phi coefficient) or tetrachoric correlation
4. If φ > 0.3 for a pair, those defenses provide less combined
   protection than their individual metrics suggest

```
# For each attack input:
result_A = defense_A.evaluate(input)  # pass/fail
result_B = defense_B.evaluate(input)  # pass/fail
# Compute 2x2 contingency table, then φ coefficient
```

### Step 5: Compute realistic stack performance

**Do NOT multiply individual defense success rates.**

Instead, measure the assembled stack end-to-end:
- Joint residual (what gets through all layers) must be measured directly
- The multiplicative prediction (product of individual residuals)
  underestimates the true residual
- The gap between predicted and measured grows with stack size

### Step 6: Account for false refusal accumulation

False refusals (blocking legitimate inputs) compose as a UNION, not
an intersection.  Each additional layer adds its false positives to
the total.

```
false_refusal_rate ≈ 1 - ∏(1 - fp_rate_i)  # union bound
```

A stack that individually has 5% false refusal per layer can easily
reach 20-30% composite false refusal with 4-5 layers.

### Step 7: Evaluate against adaptive adversaries

Static attack evaluation overestimates defense effectiveness.
An adversary who can adapt to the defense stack may bypass multiple
layers simultaneously because they share a common weakness (shallow
alignment).

Test with at least one adaptive adversary (e.g., GCG, optimization-
based suffix attacks) in addition to fixed attack sets.

## Environment Caveats

- **Production deployments**: Focus on C0+C1+C2 combinations for
  latency-sensitive systems.  C3/C4 defenses add significant overhead.
- **Open-weight models**: A3+ adversaries can directly inspect weights,
  so C4 (training-time) defenses are the most robust option.
- **API-only models**: Limited to A0-A1 adversary modeling; C3+ defenses
  are unavailable unless the provider implements them.

## Failure Modes

- **Assuming independence**: The single most common error.  Leads to
  dramatic overestimation of stack effectiveness.
- **Optimizing for single-layer metrics**: Individual defense papers
  report impressive numbers against fixed attacks; these don't compose.
- **Ignoring false refusals**: Each layer adds false positives.  A
  stack that blocks 80% of benign inputs is unusable regardless of its
  attack prevention rate.
- **Same-row stacking**: Adding multiple defenses of the same cost
  class provides correlated, diminishing returns.

## Cross-References

- [`browser-agent-http-sandbox`](../browser-agent-http-sandbox/SKILL.md) —
  Network-layer defense as one layer in the stack
- [`unified-capability-gateway`](../unified-capability-gateway/SKILL.md) —
  Gateway pipeline as the enforcement point for defense layers
- [`transactional-coding-sandbox`](../transactional-coding-sandbox/SKILL.md) —
  Rollback as a defense mechanism for state-modifying actions

## Sources

- Layered LLM Defenses: arXiv:2608.28327
