---
name: behavior-aware-verification
description: >
  Select verification tasks based on what each proposed modification
  actually changes, rather than evaluating all modifications on a fixed
  task set.  Reduces wasted rollouts and improves modification-specific
  signal.  Derived from HarnessLens (arXiv:2608.27311).
---

# Behavior-Aware Verification

Use this skill when evolving agent configurations (harnesses, prompts,
skills, tools) through a propose-and-verify loop.  The key upgrade:
target verification to the behaviors affected by each proposed change.

## When to Use

- You have a propose-and-verify loop for agent improvement
- Your current verification uses a fixed or randomly sampled task set
- You're wasting evaluation budget on tasks unrelated to each modification
- Aggregate scores obscure whether specific behaviors improved or regressed

## Core Insight

Fixed verification sets dilute modification-specific signals.  If a
modification targets error handling but most verification tasks test
normal execution, the signal is lost in aggregate.  Behavior-aware
verification selects tasks that cover the targeted behavior AND
potential regression areas.

**Evidence**: HarnessLens improves average held-out performance by
7.6-13.6% across three agent harnesses and four benchmarks, while
consuming substantially less evaluation budget than fixed-set methods.

## Procedure

### Step 1: Context Exploration — map the task space

Before modifying anything, characterize your task inventory:

1. Inspect each available task's query, environment, tools, and constraints
2. Group tasks by their primary user goals (e.g., "data retrieval,"
   "code generation," "multi-step reasoning")
3. Record overlap — tasks that span multiple goal groups
4. Store this task organization for later verification selection

**Key**: This uses only task metadata, NOT execution results.  No
rollouts are consumed.

### Step 2: Context Exploration — map the configuration space

Identify which components of the agent harness can be modified:

For each configurable component (instructions, skills, tool descriptions,
memory, permissions, agent roles):
- How is it exposed to the agent?
- Where do its effects apply?
- How can it be updated?
- What behaviors may be affected by a change?

Only components that can be reliably identified and updated are
candidates for evolution.

### Step 3: Trajectory Diagnosis — extract evidence

After running initial rollouts on the current configuration:

**Experience Extraction**:
1. Summarize each trajectory into reusable experiences and deficiencies
2. Link each extracted item to supporting trajectories
3. Group recurring behaviors across trajectories
4. Keep distinct successful strategies separate

**Experience Analysis**:
1. Combine experiences/deficiencies with task groups and component info
2. Generate modification proposals: each specifies the targeted behavior,
   supporting trajectories, and affected components
3. Filter proposals that lack sufficient supporting evidence

### Step 4: Select verification tasks PER modification

For each proposed modification δ, construct a verification batch:

```
verification_batch = []

# 1. Tasks linked to the proposal's supporting trajectories
verification_batch += tasks_from_supporting_trajectories(δ)

# 2. Tasks with related goals, constraints, or tool requirements
verification_batch += tasks_with_related_patterns(δ)

# 3. Regression coverage — tasks that could be affected negatively
# Broader modifications → coverage across more task groups
verification_batch += regression_risk_tasks(δ)

# Minimum batch size: 5 distinct tasks
assert len(verification_batch) >= 5
```

**Critical**: Different modifications get DIFFERENT verification
batches.  A modification to error handling gets error-heavy tasks.
A modification to tool selection gets tool-diverse tasks.

### Step 5: Paired verification

Run both the current harness AND the candidate on the verification batch
under matched conditions:

```
for task in verification_batch:
    result_current = run(current_harness, task)
    result_candidate = run(candidate_harness, task)
    record(task, result_current, result_candidate)
```

Apply Trajectory Diagnosis to the verification rollouts to determine:
- Did the targeted behavior improve?
- Did any regression appear?

### Step 6: Evidence-gated acceptance

A candidate is accepted only when behavioral evidence supports the
improvement — metric improvement alone is insufficient:

1. **Check behavioral improvement**: Did the targeted behavior actually
   change in the intended direction? (Not just: did the score go up?)
2. **Check for regression**: Do any verification tasks show degraded
   behavior compared to the current harness?
3. **Confirmation round**: Candidates with supported improvement and no
   regression get a second verification on previously unused tasks
4. **Accept or reject**: Both behavioral evidence AND metric improvement
   must be present

```
if behavioral_improvement AND no_regression:
    # Confirmation on new tasks
    confirmation_batch = select_confirmation_tasks(δ)
    if confirmed(confirmation_batch):
        harness = candidate  # Accept
```

### Step 7: Budget tracking

Track total interaction budget across the evolution process:

- Initial rollouts
- Context exploration (zero rollout cost)
- Trajectory diagnosis (zero rollout cost, LLM sessions only)
- Verification rollouts (main cost center)
- Confirmation rollouts

Set a fixed total budget B.  The controller ensures each verification
batch can be completed within the remaining budget.

## Environment Caveats

- **Small task pools**: With < 20 tasks, behavior-aware selection may
  not have enough variety.  Fall back to stratified sampling.
- **Non-deterministic tasks**: Stochastic environments require multiple
  trials per task to distinguish modification effects from noise.
- **Multi-component modifications**: When a modification touches several
  components simultaneously, regression coverage must be broader.

## Failure Modes

- **Verification too narrow**: If the verification batch only covers
  the targeted behavior, regressions elsewhere go undetected
- **Aggregate-only acceptance**: Accepting based on score improvement
  without behavioral evidence allows lucky noise to pass
- **Budget starvation**: Spending too much on early modifications leaves
  insufficient budget for later, potentially better proposals
- **Evidence anchoring**: Over-relying on initial trajectory diagnosis
  without updating as the harness evolves

## Cross-References

- [`iterative-instruction-refinement`](../iterative-instruction-refinement/SKILL.md) —
  NPO-style revision as the modification proposal mechanism
- [`targeted-failure-attribution`](../targeted-failure-attribution/SKILL.md) —
  DoCtOR's failure attribution feeds diagnosis: identify WHICH behavior
  failed before proposing a targeted modification
- [`knowledge-compounding-loop`](../knowledge-compounding-loop/SKILL.md) —
  Extracted experiences accumulate in a persistent knowledge layer

## Sources

- HarnessLens: arXiv:2608.27311
