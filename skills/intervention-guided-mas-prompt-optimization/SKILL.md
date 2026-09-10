---
name: intervention-guided-mas-prompt-optimization
description: >
  Optimize multi-agent system prompts via sequential intervention
  and semantic gradient abstraction.  Identifies the responsible agent
  per failure, extracts agent-level supervision, and clusters gradients
  to prevent mixing unrelated failure modes.
  Derived from AgentGrad (arXiv:2609.08572).
---

# Intervention-Guided MAS Prompt Optimization

Use this skill when optimizing prompts for multi-agent systems (MAS)
where multiple specialized agents collaborate and you need to identify
which agent's prompt to modify when failures occur.

## When to Use

- Your MAS has 3+ agents with separate prompts and you're seeing failures
- You can't tell which agent is responsible for a given failure
- Random prompt tweaks fix one failure but break others
- You want systematic, gradient-like prompt optimization without training

## Core Insight

In multi-agent systems, textual gradient methods fail because they
(1) select the wrong agent's prompt for modification and (2) mix
unrelated failure modes during gradient aggregation.  **Sequential
intervention** identifies the causal agent per failure by modifying
one agent at a time, and **semantic gradient abstraction** clusters
similar failures to produce generalized corrections.

**Evidence**: AgentGrad achieves state-of-the-art on 5 MAS benchmarks
and reduces wall-clock optimization time by 2.5× vs. next-fastest
baseline.  Optimized prompts transfer across different backbone models.

## Procedure

### Step 1: Collect failure cases

Run the MAS on evaluation tasks and collect failing cases with:
- The input
- Each agent's intermediate output
- The final (incorrect) output
- The ground truth or expected behavior

### Step 2: Sequential intervention (target identification)

For each failure, identify the responsible agent:

1. Take Agent 1's output and replace it with a corrected version
   (using a stronger model or oracle)
2. Re-run the downstream agents with the corrected input
3. If the final output is now correct → Agent 1 is the target
4. If still incorrect → restore Agent 1, modify Agent 2, repeat

The first agent whose correction resolves the failure is the
**target agent**.  This is causal identification, not correlation.

### Step 3: Extract agent-level textual gradients

For the identified target agent:

1. Compare its actual output with the corrected output that fixed
   the failure
2. Generate a textual gradient: a natural-language description of
   what the agent should have done differently
3. The corrected output serves as **agent-level supervision** —
   concrete evidence of what "correct" looks like for this agent

Example gradient: "When the retrieval agent returns multiple
conflicting sources, the synthesis agent should explicitly
acknowledge the conflict rather than silently picking one source."

### Step 4: Semantic gradient abstraction

Don't apply gradients individually — cluster and abstract them:

1. **Cluster**: Group semantically similar gradients using embedding
   similarity.  Gradients about "ignoring conflicts" cluster together;
   gradients about "wrong format" form a separate cluster.
2. **Abstract**: For each cluster, generate a single generalized
   gradient that captures the shared corrective pattern, dropping
   case-specific details.

This prevents mixing unrelated failure modes in a single prompt
update, which is the primary cause of optimization instability.

### Step 5: Apply and validate

For each abstracted gradient:

1. Update the target agent's prompt to incorporate the correction
2. Validate on the failing cases — did they resolve?
3. Validate on passing cases — did anything regress?
4. Accept the update only if net improvement is positive

### Step 6: Iterate

Repeat Steps 1–5 with the updated prompts.  Each round should
produce fewer failures.  Stop when improvement plateaus or
the failure rate is acceptable.

## Environment Caveats

- **Two-agent systems**: Sequential intervention is trivial — if
  fixing Agent 1 doesn't help, it's Agent 2.  The full procedure
  is most valuable for 3+ agents.
- **Agent ordering**: If agents run in parallel (not sequentially),
  the intervention order doesn't matter, but you still test one
  agent at a time.
- **Cost**: Each intervention requires re-running downstream agents.
  For N agents and M failures, worst case is N×M re-runs.  In
  practice, early termination (first fix wins) reduces this.

## Failure Modes

- **Multiple responsible agents**: Some failures require fixing
  two agents simultaneously.  Sequential intervention finds only
  the first.  If fixing one agent doesn't fully resolve a cluster,
  re-run intervention on the residual failures.
- **Gradient interference**: Abstracted gradients from different
  clusters may conflict.  Apply one cluster's update at a time
  and validate before adding the next.
- **Overfitting to failures**: If the failure set is small or
  unrepresentative, optimized prompts may not generalize.  Use
  held-out validation tasks.

## Cross-References

- [`targeted-failure-attribution`](../targeted-failure-attribution/SKILL.md) —
  DoCtOR also identifies the responsible agent; AgentGrad uses
  sequential intervention which is more systematic but more expensive
- [`iterative-instruction-refinement`](../iterative-instruction-refinement/SKILL.md) —
  NPO refines single-agent instructions; this skill extends the
  principle to multi-agent systems

## Sources

- AgentGrad: Intervention-guided Prompt Optimization for Multi Agent Systems (arXiv:2609.08572)
