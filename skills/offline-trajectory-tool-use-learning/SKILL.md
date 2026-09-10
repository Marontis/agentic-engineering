---
name: offline-trajectory-tool-use-learning
description: >
  Learn effective tool-use policies from a single batch of raw interaction
  trajectories without task verifiers or on-policy rollouts.  Uses
  retrospective task inference and reward-guided trajectory filtering.
  Derived from "AgentBrew" (arXiv:2609.05837).
source: https://arxiv.org/abs/2609.05837
---

# AgentBrew: Offline Tool-Use Learning from Raw Trajectories

Use this skill when training or adapting agents for tool-use in
environments that provide no pre-defined tasks, no verifiers, no
faithful simulators, and limited budget for large-scale interaction.

## When to Use

- Target environment has no pre-defined task set or verifiers
- Budget for on-policy exploration is limited
- A batch of raw interaction trajectories exists (from human users,
  prior agents, or exploratory runs)
- You need to extract training signal from noisy, unstructured
  interaction logs

## Core Insight

Real-world tool-use environments provide no tasks, no verifiers, and no
simulators. AgentBrew learns from a single batch of raw interaction
trajectories by: (1) **retrospective task inference** — reconstructing
aligned instructions for each trajectory after the fact, and (2)
**reward-guided filtering** — using trajectory quality signals to
select training examples. This eliminates the need for iterative
on-policy rollouts or pre-defined task suites.

---

## Procedure

### 1. Collect Raw Trajectory Corpus

Explore the target environment to collect interaction trajectories
without quality filtering:
- Record all tool calls, responses, and intermediate states
- Include failed and partial trajectories — these contain
  negative training signal
- No pre-defined tasks needed; trajectories are collected from
  natural environment exploration

### 2. Retrospective Task Inference

For each raw trajectory, reconstruct what task was being attempted:
1. Analyze the sequence of tool calls and their outcomes
2. Infer a natural-language instruction that, if given to an ideal
   agent, would produce a trajectory similar to the observed one
3. Align the inferred instruction with the actual trajectory to
   create (instruction, trajectory) training pairs
4. Filter out trajectories where no coherent instruction can
   be inferred

### 3. Reward-Guided Trajectory Filtering

Score each (instruction, trajectory) pair for training quality:
1. Assess trajectory completeness: did it reach a terminal state?
2. Assess tool-use efficiency: were tool calls necessary and
   well-formed?
3. Assess outcome quality: did the trajectory achieve the
   inferred instruction?
4. Select top-k trajectories by composite quality score
5. Discard low-quality trajectories to prevent learning from
   noisy or adversarial examples

### 4. Train Offline Policy

Use the filtered (instruction, trajectory) pairs for supervised
fine-tuning or preference optimization:
- Standard SFT on high-quality trajectories
- Optional: DPO/RLHF using quality-ranked trajectory pairs
- No on-policy rollouts required during training

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Instruction hallucination | Retrospective inference produces wrong task | Cross-validate inferred instructions against trajectory outcomes |
| Distribution mismatch | Training trajectories don't cover deployment scenarios | Ensure exploration covers diverse environment states |
| Quality signal noise | Reward model assigns high scores to failed trajectories | Use multiple quality signals; require consensus across metrics |
| Overfitting to exploration policy | Agent learns exploratory behaviors, not task-solving | Filter out exploration-only trajectories; weight task-completion trajectories higher |

## Sources

> Source: "AgentBrew: Offline Tool-Use Agent Learning from Raw Real-World Trajectories" (arXiv:2609.05837)
