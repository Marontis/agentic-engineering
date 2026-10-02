---
name: recursive-self-improvement-loop
description: >
  Implement a recursive self-improvement loop where an AI research
  agent proposes changes to its own code, benchmarks modified versions
  on a task suite, and keeps changes that score best on the selection
  tasks' hidden evaluations (hidden from the proposing agent), then
  checks transfer on held-out benchmarks the loop never uses. Covers the propose-benchmark-select loop, emergent
  capability discovery, and reward hacking reduction.
  Derived from "Recursive Self-Improvement of AI Research Agents"
  (AIDE², arXiv:2609.26457).
source: https://arxiv.org/abs/2609.26457
---

# Recursive Self-Improvement Loop (AIDE²)

Use this skill when building a system where an AI research agent
improves its own implementation through iterated self-modification,
with changes validated against a benchmark suite before acceptance.

## When to Use

- Agent's own code (harness, search policy, memory management) is the
  optimization target
- You want improvements that generalize beyond selection tasks
- You need a structured propose-benchmark-select loop with held-out
  validation
- Budget allows multi-day autonomous operation

## Core Insight

When an AI research agent's own code is the optimization target, each
accepted rewrite becomes the agent that performs the next round of
edits. AIDE² implements this loop: propose changes → benchmark
modified versions → keep best performers on the selection tasks' hidden
evaluations (scored by the loop, never shown to the proposing agent).
Separate held-out benchmarks, never used for selection, measure
transfer. In an
8-day autonomous run, AIDE² discovered seven successive improvements
(new search policy, memory compression, context management) that
generalized to four held-out benchmarks including out-of-distribution
tasks. Critically, reward hacking decreased from 55% to 32% without
explicit optimization for this property.

**Evidence**: Discovered agent matches or exceeds human-engineered
production agents on FML-Bench. Gains transfer to ML engineering,
heuristic algorithm engineering, and physics-based weather forecasting.

---

## Procedure

### 1. Define the Optimization Scope

1. Identify the editable surface: which parts of the agent's code may
   be modified (harness logic, search policy, memory management,
   context compression)
2. Define what is FROZEN: the base model weights, the evaluation
   infrastructure, the task suite interface, the graders, the
   hidden/OOD splits, the negative security testbed, and the agent's
   permissions. These stay outside the editable surface for the whole
   run; widening the editable surface needs an external authority, not
   the loop (see rules/recursive-improvement.md — "DO: Make the
   improvement mechanism part of the agent's editable source")
3. Establish safety boundaries: what kinds of modifications are
   permitted vs. prohibited

### 2. Build the Benchmark Suite

1. **Selection tasks with hidden evaluations**: a diverse suite of
   tasks the loop benchmarks proposed changes on. Their scoring data
   are hidden from the proposing agent (it sees tasks, not graders or
   answers), but the loop uses the scores to select
2. **Held-out benchmarks**: tasks never used for selection, run only to
   validate that improvements generalize. These are the acceptance
   gate's held-out tasks
3. **Out-of-distribution tasks**: held-out tasks from domains different
   from the selection suite — the strongest test of transferability
4. Include a reward-hacking detection mechanism to measure whether
   the agent is gaming metrics vs. genuinely improving

### 3. Run the Propose-Benchmark-Select Loop

For each iteration:

1. **Propose**: the current agent analyzes its own code and proposes
   modifications (code patches)
2. **Benchmark**: run the modified agent on the selection task suite
3. **Select**: keep a modification only if it (a) improves
   performance on the selection tasks' hidden evaluations by more than
   the noise margin δ, (b) passes the
   **security-invariant probes** (immutable negative security
   testbed: e.g. certificate validation, credential handling, sandbox
   and privilege boundaries — a poisoned selection task can otherwise
   plant a `verify=False`-style backdoor that survives later clean
   generations, arXiv:2609.17817), and (c) shows **behavioural
   evidence** in the trajectories that the targeted behaviour changed,
   not just a higher aggregate score. Selection-score gains are
   search-time signals; the keep decision defers to
   rules/recursive-improvement.md — "DO: Pass every self-modification
   through one acceptance gate" (no regression beyond a noise margin δ
   on previously-correct cases and held-out tasks, δ estimated from
   repeated runs of the unchanged baseline; security testbed strict)
4. **Commit**: the accepted modification becomes the new agent —
   the next round of proposals starts from this version
5. Each accepted rewrite compounds: improvement N+1 builds on
   improvement N

### 4. Validate on Held-Out Benchmarks

Periodically, and always before a kept agent is deployed:

1. Run the current best agent on the held-out benchmarks (never used
   for selection)
2. Check whether selection-task improvements transfer
3. Check whether reward hacking rate is stable or decreasing
4. If held-out performance degrades beyond δ while selection
   performance improves → the loop is overfitting; roll back and
   diversify the selection suite

### 5. Monitor for Emergent Properties

AIDE² discovered two emergent properties:
1. **Capability transfer**: improvements generalized to OOD tasks
   the loop never encountered
2. **Reward hacking reduction**: the loop never explicitly optimized
   for this, but the rate fell from 55% to 32%

Monitor for similar emergent effects — both positive and negative.

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Selection suite overfitting | Improvements don't transfer to held-out benchmarks | Diversify selection tasks; periodic held-out checks |
| Reward hacking increase | Agent games selection metrics | Include reward-hacking detection in monitoring |
| Compounding regression | Bad edit accepted, subsequent edits build on it | Checkpoint and rollback infrastructure; periodic full re-eval |
| Stagnation | No further improvements discovered | Diversify proposal strategy; explore component types not yet edited *within the fixed editable set* (do not widen it; see [`regularized-harness-evolution`](../regularized-harness-evolution/SKILL.md) step 3) |
| Unsafe self-modification | Agent modifies safety boundaries or eval infrastructure | Freeze safety boundaries; hash-verify eval infrastructure; run the negative security testbed on every candidate |
| Evolve-set overfit | Unregularized evolution wins in-distribution but loses OOD (RRSI: 92.8 vs 90.5 evolve, 40.3 vs 43.6 OOD) | Use the edit budget, leakage screen and noise-adjusted acceptance in [`regularized-harness-evolution`](../regularized-harness-evolution/SKILL.md) |

See also: [`regularized-harness-evolution`](../regularized-harness-evolution/SKILL.md)
(RRSI, arXiv:2609.24972) for the bounded-envelope version of this loop.

> Source: Srikanth et al., "Recursive Self-Improvement of AI Research
> Agents" (arXiv:2609.26457), Sep 2026.
