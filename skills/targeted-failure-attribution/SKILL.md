---
name: targeted-failure-attribution
description: >
  Identify the decisive error agent and step in multi-agent failures,
  then restrict reflection to only the responsible agent.  Avoids memory
  contamination of agents that performed correctly.  Derived from DoCtOR
  (arXiv:2608.28264).
---

# Targeted Failure Attribution

Use this skill when a multi-agent system has failed a task and you need to
determine *which* agent and *which* step caused the failure, then generate
targeted reflections without contaminating agents that performed correctly.

## When to Use

- A multi-agent collaboration has failed and you need to improve future runs
- Your system currently forces ALL agents to reflect on failures
- You have execution trajectories (step-by-step reasoning traces) available
- You want to avoid introducing new errors through misguided reflection

## Core Insight

In multi-agent failures, responsibility typically falls on **one** agent
making **one** decisive error that cascades to downstream agents.  Forcing
regular-behaving agents to reflect contaminates their memory with wrong
insights and may introduce NEW errors in subsequent runs.

**Evidence**: DoCtOR achieves 22%, 26%, and 27% improvements over initial
success rates on HotPotQA, ChartQAPro, and Mind2Web — outperforming
Reflexion, Retroformer, and COPPER, which require all agents to reflect.

## Procedure

### Step 1: Replay the failure trajectory

Obtain the full execution trace as a sequence of (agent, step, output)
tuples.  Each step should include the agent's reasoning, any tool calls,
and the output produced.

### Step 2: Score individual steps for correctness

Apply a process-reward model or step-level evaluator to assign a
correctness score to each reasoning step.  This can be:

- **Automated** (ProFA): Train a process-reward model that scores individual
  reasoning steps, or use a capable LLM as a judge with step-level rubrics
- **Rule-based**: Apply domain-specific heuristics (e.g., did the data
  query return expected schema, did the code compile)

The correctness score should reflect whether each step's output is
factually correct and logically sound given its inputs.

### Step 3: Identify the decisive error step

The **decisive error step** is the *first* step in the trajectory whose
correctness score falls below the threshold γ.  This is where the task
first went wrong.

```
for step in trajectory:
    if correctness_score(step) < γ:
        decisive_error_step = step
        decisive_error_agent = step.agent
        break
```

### Step 4: Generate counterfactual correction

Apply counterfactual reasoning to generate a *corrected* version of the
decisive error step — what the agent SHOULD have produced at that point.
Verify the correction using the same step-level evaluator.

This correction serves as the "what should have happened" anchor for
reflection, not as a direct fix to the trajectory.

### Step 5: Targeted reflection (decisive error agent ONLY)

Only the **decisive error agent** reflects.  The reflection should:
1. Acknowledge the specific error in the decisive error step
2. Contrast the erroneous output with the counterfactual correction
3. Extract a generalizable lesson (not just "don't do this specific thing")
4. Store the reflection in only that agent's memory

**Critical**: Regular-behaving agents do NOT reflect.  Their memory is
not updated.  This prevents cascading contamination.

### Step 6 (optional, low-resource): Truncated reflection

In resource-constrained settings, you can reduce reflection cost by
providing only the reasoning steps **after** the decisive error step
(including the corrected version).  This achieves comparable reflection
quality to providing the full trajectory.

**Evidence**: reflecting on steps after the decisive error step achieves
comparable quality to complete trajectories, enabling efficient reflection
under low-resource settings.

## Environment Caveats

- **No process-reward model available**: Use a capable LLM with step-level
  judging prompts as a substitute for ProFA.  Provide clear correctness
  criteria per step type.
- **Single-agent systems**: This skill still applies — identify the
  decisive error STEP and reflect only on that segment of the trajectory.
- **Multiple simultaneous errors**: If multiple agents err independently
  (rare), each becomes a decisive error agent for their respective error
  chain.  Apply the procedure per chain.

## Failure Modes

- **Threshold too high (γ)**: Flags correct steps as errors, leading to
  false attribution and wasted reflection on steps that were actually fine
- **Threshold too low (γ)**: Misses the decisive error and attributes
  failure to a downstream step that was merely propagating the original
  error
- **Counterfactual too specific**: If the correction is task-specific
  rather than generalizable, the reflection won't transfer to future tasks
- **Memory contamination bypass**: If you accidentally allow non-decisive
  agents to see the reflection, you get the same contamination problem
  the procedure is designed to prevent

## Cross-References

- [`iterative-instruction-refinement`](../iterative-instruction-refinement/SKILL.md) —
  Use NPO-style revision to iteratively improve the reflecting agent's
  system instructions based on failure attribution results
- [`behavior-aware-verification`](../behavior-aware-verification/SKILL.md) —
  After applying reflections, verify improvements on behavior-relevant
  tasks, not a fixed set

## Sources

- DoCtOR: arXiv:2608.28264
