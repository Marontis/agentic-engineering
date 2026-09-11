---
name: static-dynamic-verification-gap-measurement
description: >
  Measure and reduce the gap between static verification (passes)
  and dynamic execution (fails) in agent-generated code and plans.
  Covers gap quantification, root-cause classification, and
  targeted dynamic test selection.
  Derived from "Beyond Static Guarantees" (arXiv:2609.10762).
---

# Static-Dynamic Verification Gap Measurement

Use this skill when your static checks (linting, type checking,
plan validation) pass but runtime execution still fails.

## When to Use

- Your agent's code passes static analysis but fails tests
- Your agent's plans look valid on paper but fail in execution
- You need to decide where to invest in dynamic testing
- You want to quantify the reliability of your static checks

## Core Insight

Static analysis provides necessary but not sufficient guarantees.
The **static-pass dynamic-fail (SPDF) gap** measures how often
artifacts that pass all static checks still fail at runtime.
Understanding the gap reveals which failure modes static analysis
misses, enabling targeted dynamic testing where it matters most.

## Procedure

### Step 1: Establish the static verification baseline

Run all static checks on a corpus of agent-generated artifacts:

- Type checking / linting
- Schema validation
- Dependency resolution
- Constraint satisfaction (for plans)

Record: total artifacts, static-pass count, static-fail count.

### Step 2: Measure the SPDF gap

For all static-pass artifacts, run dynamic execution:

```
SPDF_gap = (static_pass ∩ dynamic_fail) / static_pass
```

- SPDF gap = 0%: Static checks are sufficient (rare)
- SPDF gap < 10%: Static checks are reliable; selective dynamic testing
- SPDF gap 10–30%: Significant gap; need systematic dynamic testing
- SPDF gap > 30%: Static checks are unreliable; dynamic testing mandatory

### Step 3: Classify SPDF failure root causes

For each static-pass/dynamic-fail case, classify the root cause:

| Category | Example | Static Limitation |
|:---------|:--------|:------------------|
| **Runtime state** | Null pointer, empty result set | Static can't model runtime data |
| **Environment** | Missing dependency, wrong version | Static assumes ideal environment |
| **Concurrency** | Race condition, deadlock | Static can't model interleaving |
| **External API** | Rate limit, schema change | Static can't model external systems |
| **Semantic error** | Correct types, wrong logic | Static checks syntax, not semantics |

### Step 4: Target dynamic testing

Based on root-cause distribution, allocate dynamic testing budget:

- If 60% of SPDF failures are runtime-state errors → add property-based
  testing with diverse inputs
- If 40% are environment errors → add integration testing in
  representative environments
- If semantic errors dominate → add behavioral tests that check
  output correctness, not just execution success

### Step 5: Track gap reduction

After adding targeted tests, re-measure:

```
effective_coverage = 1 - SPDF_gap_after / SPDF_gap_before
```

Goal: reduce SPDF gap to <5% for production-critical paths.

## Environment Caveats

- **Fast-moving codebases**: The gap changes as the agent's code
  generation capabilities evolve.  Re-measure monthly.
- **Cost of dynamic testing**: Dynamic tests are expensive.
  Use the SPDF gap to justify the investment — if the gap
  is <5%, additional dynamic testing has low ROI.
- **Test flakiness**: Flaky dynamic tests inflate the measured
  gap.  Filter flaky tests before computing the gap.

## Failure Modes

- **Survivorship bias**: Only measuring artifacts that reach
  dynamic testing.  Some artifacts fail so badly they never
  reach execution — include these as "pre-dynamic failures."
- **Gap inflation**: Non-deterministic failures (network, timing)
  inflate the gap.  Run dynamic tests multiple times and count
  consistent failures only.
- **Static check gaming**: Adding static checks that trivially
  pass everything reduces static-fail count but doesn't improve
  reliability.

## Cross-References

- [`behavior-aware-verification`](../behavior-aware-verification/SKILL.md) —
  Selects verification tasks based on changes; this skill
  identifies where dynamic verification is most needed
- [`trajectory-aware-eval-pruning`](../trajectory-aware-eval-pruning/SKILL.md) —
  Prunes evaluation tasks; SPDF gap measurement identifies
  which pruned tasks matter

## Sources

- Beyond Static Guarantees: Measuring the Static-Pass Dynamic-Fail Gap (arXiv:2609.10762)
