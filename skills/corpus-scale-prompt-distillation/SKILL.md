---
name: corpus-scale-prompt-distillation
description: >
  Optimize agent prompts via a single offline corpus-wide statistical
  reflection pass instead of iterative search. A coding agent writes
  analysis code over a static trajectory corpus, identifies systematic
  failure modes, and distills insights into behavioral rules — 22×
  cheaper than validation-gated search.
  Derived from "Coding Agents are Strong Prompt Optimizers" (CASD)
  (arXiv:2609.26261).
source: https://arxiv.org/abs/2609.26261
---

# Corpus-Scale Prompt Distillation (CASD)

Use this skill when you have a corpus of agent execution trajectories
and want to optimize the agent's prompt without iterative search,
environment access, or validation data.

## When to Use

- You have a static corpus of agent trajectories (successful and
  failed)
- Iterative prompt optimization is too expensive (requires fresh
  rollouts per edit)
- You lack environment access or validation data for online search
- You want to identify systematic failure patterns, not individual
  error fixes
- Budget constraint: need prompt optimization at ~$1.60, not ~$35

## Core Insight

Search-based prompt optimizers (GEPA, SkillOpt) iterate: propose
edit → run rollouts → score → retain improvements. CASD eliminates
this loop. The key insight is **reflection scope**: instead of
reasoning over a small batch of trajectories per optimization step,
a coding agent **writes and executes analysis code** to compute
corpus-wide statistics, identifies systematic failure modes, inspects
representative episodes, and distills insights into behavioral rules.
A single pass suffices because corpus-wide statistical reflection
captures patterns that small-batch reflection misses.

**Evidence**: Single CASD pass outperforms GEPA on 3/4 benchmarks and
SkillOpt on 4/4, averaging +16.6pp over baseline (vs +10.9 GEPA, +5.3
SkillOpt). Cost: ~$1.60 vs ~$35 for validation-gated search.

---

## Procedure

### 1. Assemble the Trajectory Corpus

1. Collect agent execution trajectories from the target task domain
2. Include BOTH successful and failed trajectories — failures are the
   primary signal
3. Ensure trajectories contain: task specification, agent actions,
   tool calls, observations, and final outcomes
4. No environment access or validation labels needed — only the raw
   trajectories

### 2. Hand Corpus to a Coding Agent

1. Provide the trajectory corpus to an off-the-shelf coding agent
   (e.g., a frontier model in agentic coding mode)
2. Instruct the agent to: "Analyze this corpus of agent trajectories,
   identify systematic failure patterns, and produce an optimized
   prompt with behavioral rules that address the failures"
3. The agent should write and execute analysis code, NOT just read
   trajectories

### 3. Corpus-Wide Statistical Analysis

The coding agent should:

1. **Compute corpus-wide statistics**: failure rates by task type,
   action category, error class
2. **Cluster failure modes**: group failures by shared characteristics
   (e.g., tool misuse, wrong action ordering, missing context)
3. **Identify systematic patterns**: patterns that appear across
   multiple trajectories, not one-off errors
4. **Inspect representative episodes**: deep-dive into specific
   trajectories that exemplify each failure pattern

### 4. Distill into Behavioral Rules

From the analysis, produce:

1. **Behavioral rules**: concrete DO/DON'T instructions that address
   each systematic failure pattern
2. **Priority ordering**: rules addressing the most frequent or
   highest-impact failure modes first
3. **Positive examples**: when helpful, include brief trajectory
   snippets showing correct behavior
4. **Concise format**: the final prompt should be a manageable set
   of rules, not a dump of all observations

### 5. Validate (Optional)

1. If validation data is available, test the optimized prompt on
   held-out tasks
2. Compare against the original unoptimized prompt
3. If no validation data: the single-pass result is already
   competitive with iterative search in most cases

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Corpus too small | Insufficient trajectories for statistical patterns | Collect more trajectories; CASD works with corpus-wide stats |
| Rules are too specific | Analysis overfits to particular failure instances | Focus on systematic patterns; require minimum frequency threshold |
| Rules contradict each other | Different failure modes suggest conflicting advice | Priority ordering; higher-frequency rules take precedence |
| Missing failure modes | Corpus doesn't cover all task variants | Ensure corpus covers the task distribution |
| Analysis code errors | Coding agent writes buggy analysis | Agent executes and debugs its own code; use frontier model |

> Source: Singh et al., "Coding Agents are Strong Prompt Optimizers"
> (arXiv:2609.26261), Sep 2026.
