---
name: neural-invariant-failure-diagnosis
description: >
  Pinpoint agent failure steps and failure modes in complex trajectories by
  abstracting raw logs into structured behavioral states and checking neural
  invariants. Derived from AgentScope (arXiv:2609.02371).
source: https://arxiv.org/abs/2609.02371
---

# Neural-Invariant Failure Diagnosis

Use this skill when diagnosing failed agent trajectories, performing post-mortem root-cause
analysis on complex multi-turn rollouts, or localizing bugs in autonomous agent harnesses.

## When to Use

- Long agent trajectories (20+ turns, complex tool interactions) where manual inspection
  is too slow and unstructured "LLM-as-a-judge" prompts produce inconsistent blame attribution
- Pinpointing the exact decisive transition step where an agent diverged from a valid solution path
- Classifying failure modes into formal categories (planning divergence, action execution error,
  observation misinterpretation, loop degradation)
- Automated diagnostic harnesses evaluating agent runs on software engineering, web navigation,
  or data science tasks

## Core Insight

Relying entirely on free-form LLM judgment to diagnose agent traces is unreliable: LLMs
suffer from recency bias, hallucinate step causality, and confuse early benign errors with
terminal causes. Conversely, classical software debugging cannot handle the probabilistic,
semi-structured nature of agent decision-making.

The **neuro-symbolic solution** (AgentScope):
1. Project raw agent logs into a **structured behavioral abstraction** (states, tool calls,
   parameter bindings, and environment feedback diffs).
2. Define **neural invariants**—executable behavioral properties that must hold across valid
   agent trajectories (e.g., *monotonic progress*, *precondition satisfaction*, *grounded observation*,
   *state-space non-oscillation*).
3. Evaluate the structured trajectory step-by-step against these neural invariants to
   identify the exact first step that violates an invariant, attributing failure to its true root cause.

---

## Procedure

### 1. Abstract Trajectories into Structured Behavioral Graphs

Transform unstructured message transcripts into a standardized sequence of transition tuples:

$$\tau = \langle (s_0, a_0, o_0), (s_1, a_1, o_1), \dots, (s_T, a_T, o_T) \rangle$$

For each step $t$:
- **Agent Intent ($I_t$)**: The explicit goal declared in the thought/scratchpad.
- **Action ($a_t$)**: Standardized tool name and structured arguments.
- **Environment Diff ($\Delta E_t$)**: The concrete state delta observed (file created,
  exit code, DB row count change, URL change).
- **Abstract State ($s_{t+1}$)**: Summary of active goals, open files, and verified assertions.

### 2. Define and Evaluate Neural Invariants

Check the trajectory sequentially against five core neural invariants:

| Invariant Class | Formal Property Checked | Typical Failure Mode Exposed |
|:----------------|:------------------------|:-----------------------------|
| **Precondition Invariant** | Are all prerequisites for action $a_t$ established in $s_t$? (e.g., file exists before read, dependency installed before run) | *Premature Execution / Hallucinated Context* |
| **Observation Grounding** | Does the reasoning in $I_{t+1}$ faithfully reflect the observation $o_t$ without hallucinating missing fields? | *Observation Denial / Confirmation Bias* |
| **Monotonic Progress** | Does step $t$ reduce the distance to the goal, or mutate state towards completion? | *No-Op Spinning / Empty Action* |
| **State Loop Invariant** | Has the system state $s_t$ been visited previously with an identical action attempt? | *Infinite Action Oscillation* |
| **Action-Intent Consistency** | Does the emitted action $a_t$ semantically match the declared intent $I_t$? | *Tool Argument Misalignment* |

### 3. Pinpoint Decisive Divergence Step

Scan the trajectory forward from $t=0$:
1. Identify the **first invariant violation**:
   $$t^* = \min \{ t \mid \text{InvariantViolation}(s_t, a_t, o_t) == \text{True} \}$$
2. Distinguish **recoverable hiccups** from **decisive failures**:
   - A step violation is *recoverable* if a subsequent step $t' > t^*$ actively corrects
     the state (e.g., command fails, agent catches error, runs alternative command successfully).
   - The *decisive failure step* is the first invariant violation that remains uncorrected
     and directly propagates error to terminal task failure.

### 4. Synthesize Diagnostic Report

Format the diagnostic findings into a machine-readable summary:

```json
{
  "trajectory_id": "traj_swe_1042",
  "decisive_step": 7,
  "failure_category": "Precondition Invariant Violation",
  "root_cause": "Agent attempted to run pytest on tests/test_core.py before switching to virtual environment where dependencies were installed.",
  "corrective_guidance": "Verify virtualenv activation prior to running test commands."
}
```

---

## Environment Caveats

- **Ambiguous environment transitions**: In web browsing or GUI tasks, screen visual state
  may change without explicit text diffs. Use structural DOM diffs or accessibility trees
  rather than raw pixels to evaluate environment invariants.
- **Relaxed progress standards**: Exploratory actions (e.g., `grep`, `ls`, `cat`) do not
  modify disk state; do not falsely flag read-only information gathering as a Monotonic
  Progress violation.

## Failure Modes

- **Blaming the symptom**: Flagging step $T$ (where final test failed) rather than step $t^*$
  (where an invalid edit corrupted an internal class definition 10 steps earlier). Enforcing
  strict forward-scan checking of state invariants prevents this error.

## Cross-References

- [`targeted-failure-attribution`](../targeted-failure-attribution/SKILL.md) — Multi-agent credit assignment and reflection isolation.
- [`harness-tampering-audit`](../harness-tampering-audit/SKILL.md) — Auditing evaluation harnesses for unauthorized modifications.
- [`behavior-aware-verification`](../behavior-aware-verification/SKILL.md) — Selective verification based on modified spans.

## Sources

- **Paper**: [Diagnosing with Insights: Structured Analysis of Agent Failures via Behavioral Abstractions](https://arxiv.org/abs/2609.02371) — Bi, Gao, Xie, Li, Xu, Yang, Yang (Tsinghua & Microsoft Research, 2026)
- **Praxis source**: `src:2609-02371v1`
