---
name: belief-calibrated-scaffold-optimization
description: >
  Maintain an explicit, persistent world-model document of causal hypotheses during
  agent scaffold optimization. Calibrates beliefs against rollout outcomes to prevent
  repeating refuted hypotheses. Derived from BCO (arXiv:2609.01861).
source: https://arxiv.org/abs/2609.01861
---

# Belief-Calibrated Scaffold Optimization

Use this skill when using an LLM coding agent to iteratively optimize agent scaffolds,
prompts, tools, or orchestration workflows based on evaluation traces.

## When to Use

- Meta-agent optimization loops where an optimizer model reads benchmark scores and
  edits agent code/prompts to improve performance
- Multi-iteration engineering tasks where the optimizer repeatedly tests variations of
  a hypothesis that already failed in earlier iterations
- Preventing hypothesis amnesia across long search trajectories (where earlier reasoning
  is lost due to context window truncation)
- Disentangling *what the optimizer expects will happen* from *what actually happened in execution*

## Core Insight

When an agent optimizes a code scaffold, each proposed edit is driven by an underlying
**causal belief**: an assumption about why the previous version failed and how the environment
will respond to a specific architectural change.

In standard recursive improvement loops, this belief remains **implicit**: it lives only
in the ephemeral chain-of-thought of the current turn. Later turns see only the resulting
code diffs and scalar benchmark scores, but never inspect the original hypothesis. Consequently,
the optimizer frequently revisits refuted strategies or misattributes success to unrelated changes.

**Belief-Calibrated Optimization (BCO)** solves this by:
1. Writing the optimizer's causal belief down as an **explicit, persistent in-context document**
   (a structured world model).
2. Comparing predicted outcomes against actual evaluation traces after each round.
3. Continually revising and calibrating the belief document before proposing the next candidate edit.

---

## Procedure

### 1. Initialize the Persistent Belief Document

Create a structured scratchpad file (e.g., `scaffold_world_model.md`) that accompanies
all optimization iterations:

```markdown
# Scaffold World Model & Causal Hypotheses

## Core Environmental Assumptions
- Assumptions about runtime behavior, model biases, and tool limits.

## Evaluated Hypotheses Log
- [Status: Confirmed | Refuted | Inconclusive]
  - Hypothesis: ...
  - Predicted Effect: ...
  - Observed Outcome: ...
  - Calibrated Takeaway: ...

## Active Working Hypotheses
- Hypotheses currently driving pending modifications.
```

### 2. Pre-Edit Belief Articulation (The "Predict" Step)

Before the optimizer writes any code or modifies any prompt:

- Require the agent to write a structured entry into the `Active Working Hypotheses` section:
  ```yaml
  hypothesis_id: H-04
  targeted_defect: "Agent fails when bash command output exceeds 10KB (buffer truncation)."
  proposed_mechanism: "Add chunked reading parameter to view_file tool."
  predicted_outcome: "Solves 3 previously failing test cases in test_cli.py without increasing latency on small files."
  falsification_condition: "If test_cli still fails or latency increases by >20%, hypothesis is refuted."
  ```

### 3. Execute and Measure

Apply the proposed edit and run the evaluation benchmark suite. Log:
- Pass/fail outcomes on target test cases.
- Execution traces, token costs, and latency metrics.

### 4. Calibration and Belief Update (The "Calibrate" Step)

Before planning the next edit, force a dedicated belief-calibration turn:

1. **Compare Prediction vs Reality**:
   - Did the falsification condition trigger?
   - Did unexpected secondary effects occur (e.g., passing target tests but breaking unrelated unit tests)?
2. **Update Status**:
   - Move hypothesis to `Evaluated Hypotheses Log` marked as `Confirmed`, `Refuted`, or `Partially Confirmed`.
3. **Record Causal Takeaway**:
   - If refuted, explain *why* the hypothesis failed based on empirical trace evidence.
   - Forbid future iterations from proposing variations of refuted mechanisms unless new
     evidence addresses the specific falsification cause.

---

## Environment Caveats

- **Belief Document Compaction**: Over 10+ iterations, the belief document can grow large.
  Summarize confirmed principles into a compact "Established Principles" section and retain
  only the last 5 refuted hypotheses with their one-line takeaways.
- **Stochastic noise**: If benchmark tests are non-deterministic, require 3 repeated trials
  before classifying a hypothesis as completely confirmed or refuted.

## Failure Modes

- **Post-hoc rationalization**: The agent modifying its hypothesis *after* seeing the score
  to claim it predicted the outcome. Countermeasure: require the hypothesis to be committed
  to git or written to disk before the evaluation command is executed.
- **Ignoring the world model**: The optimizer generating edits directly without consulting
  the evaluated hypotheses log. Enforce a pre-commit check verifying that the active
  hypothesis references the world model.

## Cross-References

- [`recursive-self-improvement`](../recursive-self-improvement/SKILL.md) — Fundamental bounds and validation gates for self-improving agents.
- [`reference-trajectory-harness-evolution`](../reference-trajectory-harness-evolution/SKILL.md) — Reference trajectory tracking to avoid shortcut learning.
- [`iterative-instruction-refinement`](../iterative-instruction-refinement/SKILL.md) — Single-lineage prompt optimization feedback loops.

## Sources

- **Paper**: [Belief-Calibrated Optimization: An Explicit World Model for Agentic Optimization](https://arxiv.org/abs/2609.01861) — Chen et al. (2026)
- **Praxis source**: `src:2609-01861v1`
