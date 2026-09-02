---
name: reference-trajectory-harness-evolution
description: >
  Self-evolving agent harness optimization using reference trajectories.
  Solves credit assignment failure, prevents shortcut learning, and eliminates
  catastrophic forgetting during automated prompt, skill, and tool evolution.
  Derived from HarnessEvolve (arXiv:2609.00829).
source: https://arxiv.org/abs/2609.00829
---

# Reference Trajectory Harness Evolution

Use this skill when designing or running self-evolving agents that optimize
their own harnesses (prompts, skills, tools, and execution graphs) based on
task execution outcomes.

## When to Use

- An agent iteratively refines its own prompts, tool wrappers, or skills
  based on test failures
- Terminal rewards (pass/fail) make it unclear which step in a 20-step
  trajectory broke execution
- Evolved agents overfit to specific benchmark problems (shortcut learning)
- Evolving a capability for Task B breaks previously working capabilities
  for Task A (catastrophic forgetting)

## Core Insight

Terminal success/failure feedback provides insufficient gradient for harness
optimization. If an agent fails a complex SWE task on step 18, updating the
system prompt blindly based on the final error message often ruins steps 1–17.

Comparing candidate execution trajectories against **reference trajectories**
(successful human traces, golden trajectories, or previous best agent runs)
allows the evolution loop to:
1. Pinpoint the **first divergent step** (solving credit assignment).
2. Constrain harness mutations to the specific tool or skill used at that step.
3. Validate candidate harness mutations against a **held-out test set** to
   reject shortcuts before accepting the update into production.

---

## Procedure

### Step 1: Record Step-Level Trajectory Signatures

For both reference runs and candidate runs, log structured trajectory events:

```json
{
  "step": 4,
  "action_type": "tool_call",
  "tool_name": "ast_grep",
  "arguments": {"pattern": "class UserAuth"},
  "observation_summary": "Found 3 definitions in src/auth/",
  "context_state_hash": "a1b2c3d4"
}
```

### Step 2: Compute Divergence Alignment

Align the failing candidate trajectory $T_{cand}$ against the nearest reference
trajectory $T_{ref}$:

1. Identify the earliest step $k$ where the candidate's action diverged
   semantically from the reference action (e.g., candidate invoked a broad
   regex search that flooded context, whereas reference used targeted grep).
2. Isolate the failure cause at step $k$:
   - **Instruction ambiguity**: Was the prompt unclear about tool selection?
   - **Tool documentation defect**: Did the tool docstring fail to warn against
     large outputs?
   - **Missing subtask skill**: Did the agent lack a specific procedure for
     filtering?

### Step 3: Scope Localized Harness Mutation

Do not mutate the global system prompt if the error was localized to a single
tool or skill:

- If the failure was tool misuse, propose an update to the tool's description
  or parameter schema.
- If the failure was a reasoning gap, add or refine a targeted subtask
  procedure in `skills/`.
- If the failure was global control flow, update the coordination rule.

### Step 4: Held-Out Multi-Task Validation Gate

Never accept a harness mutation based solely on the task that inspired it:

1. **Replay Inspiration Task**: Verify the new harness resolves the failure on
   the target task.
2. **Held-Out Generalization Set**: Run the mutated harness on 3+ unseen tasks
   in the same domain to confirm it learned a generalizable capability rather
   than a hardcoded shortcut.
3. **Regression Suite**: Run the mutated harness against the frozen reference
   benchmark of historical tasks. If the accuracy on previously mastered tasks
   drops by even 1 task, **reject the mutation** (catastrophic forgetting gate).

### Step 5: Commit Versioned Harness Snapshot

When all validation criteria pass:
- Commit the modified skill/prompt/tool file with a clear changelog and
  trajectory evidence link.
- Update the reference trajectory bank with the newly successful candidate
  trace.

---

## Environment Caveats

- **Nondeterministic model sampling**: At high temperatures ($\tau > 0$),
  trajectories diverge naturally. Always run harness evolution benchmarks
  with greedy decoding ($\tau = 0$) or fixed seeds to isolate harness changes
  from sampling variance.
- **Reference trajectory availability**: In new domains without golden human
  traces, use the best-performing past agent trajectories as the reference
  baseline.

## Failure Modes

- **Shortcut Memorization**: The evolution loop edits the prompt to include
  the exact file paths or variable names of the failing test, passing the
  failing case while failing on any new repo.
- **Harness Bloat**: Continuously appending "NEVER do X" rules to the system
  prompt for every failure, eventually exhausting context tokens and inducing
  instruction conflict.
- **Unguarded Rollback Erasure**: Overwriting harness files directly without
  git versioning, making it impossible to revert when regressions are discovered
  downstream.

## Cross-References

- [`recursive-improvement`](../../rules/recursive-improvement.md) — Guardrails
  for automated agent modification.
- [`targeted-failure-attribution`](../targeted-failure-attribution/SKILL.md) —
  Diagnosing root causes in multi-step trajectories.
- [`skill-design-methodology`](../skill-design-methodology/SKILL.md) —
  Decomposing lessons into subtask-level skills.

## Sources

- HarnessEvolve: Learning from Reference Trajectories for Reliable Agent
  Self-Evolution (arXiv:2609.00829)
