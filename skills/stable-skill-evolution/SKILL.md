---
name: stable-skill-evolution
description: >
  Stabilize skill evolution for agents using Adam-style momentum and
  adaptive learning rates.  Prevents catastrophic forgetting and
  oscillation during iterative skill updates.
  Derived from SkillAdam (arXiv:2609.08944).
---

# Stable Skill Evolution

Use this skill when evolving an agent's skill library iteratively
and you need to prevent oscillation, catastrophic forgetting, or
unstable skill mutations.

## When to Use

- Your skill evolution loop produces skills that oscillate between versions
- New skills overwrite working skills and cause regressions
- You want momentum-based smoothing for skill text updates
- Your agent's performance is unstable across evolution rounds

## Core Insight

Naive skill evolution (replace skill text based on latest feedback)
oscillates because each round's feedback overcorrects the previous
round's changes.  **SkillAdam** applies Adam optimizer principles
to text-based skill evolution: first-moment (momentum) smooths the
update direction, second-moment (adaptive rate) scales updates by
their historical variance.

## Procedure

### Step 1: Track skill evolution history

For each skill in the library, maintain:

- **Version history**: The full text of each version
- **Feedback history**: The feedback (success/failure + gradient)
  that motivated each update
- **Performance trajectory**: The skill's success rate per version

### Step 2: Compute textual momentum

When generating the next skill update:

1. Collect the last N textual gradients (feedback signals) for this skill
2. Identify the **consistent direction**: patterns that appear in
   most recent gradients (not just the latest one)
3. The momentum is the consistent corrective pattern, not the
   latest single-round feedback

Example: If 3 of the last 4 gradients say "add error handling"
but 1 says "simplify the procedure", momentum favors adding
error handling.

### Step 3: Apply adaptive update rate

Scale the update magnitude by historical stability:

- **Stable skills** (low variance in feedback): Apply small,
  conservative updates — the skill is mostly right
- **Volatile skills** (high variance in feedback): Apply larger
  updates — the skill hasn't converged yet
- **Converged skills** (consistently positive feedback): Skip
  updates entirely — don't fix what isn't broken

### Step 4: Gated commit

Before committing a skill update:

1. Run the updated skill on the evaluation set
2. Compare performance against the current version
3. **Accept** only if net improvement is positive
4. **Reject and revert** if performance degrades

This prevents the "one step forward, two steps back" pattern
where each evolution round introduces regressions.

### Step 5: Forgetting protection

Maintain a "golden set" of tasks that the skill must always pass:

- When a new skill version passes the evaluation set but fails
  a golden-set task, reject the update
- The golden set grows as new important tasks are solved
- This prevents catastrophic forgetting of hard-won capabilities

## Environment Caveats

- **Small feedback sets**: With fewer than 5 feedback signals,
  momentum is unreliable.  Use simple majority-direction instead.
- **Rapid task distribution shifts**: If the tasks change faster
  than the skill evolves, momentum from old tasks may be misleading.
  Reset momentum when the task distribution changes significantly.
- **Multi-skill interactions**: Updating one skill can affect
  others.  Test the full skill set, not just the modified skill.

## Failure Modes

- **Momentum lock-in**: If early feedback is consistently wrong,
  momentum propagates the error.  Include a momentum reset
  mechanism triggered by sustained performance decline.
- **Over-conservative updates**: High adaptive rates on stable
  skills can prevent necessary updates when the environment changes.
  Periodically force a full re-evaluation.
- **Golden set bloat**: If the golden set grows too large,
  every update becomes impossible.  Cap the golden set and rotate
  out tasks that haven't been relevant for N rounds.

## Cross-References

- [`knowledge-compounding-loop`](../knowledge-compounding-loop/SKILL.md) —
  Compounding persists knowledge across rollbacks; SkillAdam stabilizes
  the evolution that produces that knowledge
- [`iterative-instruction-refinement`](../iterative-instruction-refinement/SKILL.md) —
  NPO uses sliding-window feedback; SkillAdam adds momentum and
  adaptive rates on top of similar feedback signals
- [`procedural-graph-evolution`](../procedural-graph-evolution/SKILL.md) —
  Procedural graphs evolve structure; this skill stabilizes the
  evolution of text-based skills

## Sources

- SkillAdam: Stable and Efficient Skill Evolution for Agents (arXiv:2609.08944)
