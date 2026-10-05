---
name: execution-driven-environment-repair
description: >
  Separate policy failures from broken environments, tasks and verifiers in
  synthesized tool-use training or evaluation suites, repair only the
  responsible component, and revalidate with fresh rollouts. Also covers
  prefix-preserving rejection sampling and task-verifier consistency
  filtering before RL. Use when building or maintaining executable
  environments (MCP servers, stateful backends) whose failures feed
  training signals or benchmark scores.
  Derived from "WEFT: Scaling Tool-Use Post-Training for General-Purpose Agents" (arXiv:2609.36887).
source: https://arxiv.org/abs/2609.36887
---

# Execution-Driven Environment Repair

Use this skill when you train or evaluate tool-use agents on synthesized,
stateful environments (generated MCP servers, mock backends, composed
multi-tool tasks) and a failed rollout could be the agent's fault or the
environment's.

## When to Use

- You generate tool backends, tasks or verifiers automatically, and
  construction-time checks cannot prove every task is feasible and every
  verifier correct.
- Failed rollouts feed SFT rejection sampling, RL rewards or a benchmark
  score, so an infeasible task or a wrong verifier becomes a wrong signal.
- Long multi-step tasks where discarding a whole trajectory on one local
  failure wastes most of the verified work.

## Core Insight

Training experience comes from a system of four parts: environment, task,
agent harness and evaluator. A failure can come from a faulty tool
implementation, an infeasible task or a verification error, not only from
the policy. Charging all failures to the policy penalizes valid behaviour.
WEFT uses the same execution traces both as training data and as evidence
for repairing the system that produced them.

**Evidence** (Qwen3-8B, Qwen3-14B, Qwen3.5-35B-A3B; 8,172 synthesized MCPs,
64,755 tools, 11,884 composed tasks):
- With the task set and rollout budget fixed, three self-evolution rounds
  cut the tool-error rate in selected teacher trajectories from 1.76% to
  0.96% (45.5% relative) and raised Toolathlon-Verified, AutomationBench
  and Claw-Eval by 5.25, 4.33 and 3.65 points (WEFT-35B-A3B).
- Prefix-preserving rejection sampling beat end-to-end resampling at every
  retry limit k ∈ {1,2,3}; at k=3, +1.85 on Toolathlon-Verified and +2.17 on
  AutomationBench, Claw-Eval nearly tied, with the accepted-trace count held
  fixed.
- Atomic-turn GRPO improved all three main benchmarks over SFT at 8B and
  14B; trajectory-level GRPO lowered τ²-Bench by 3.17 (8B) and 0.84 (14B).
- WEFT-14B beat Agent-World-14B by 6.41, 2.23 and 12.27 points on BFCL V4,
  τ²-Bench and Claw-Eval.

---

## Procedure

### 1. Build checkable components

- Give every tool a contract: argument-to-state mapping, reads, writes,
  returns. Validate running backends with generated normal and boundary
  calls, checking queries against state and updates against database or
  workspace diffs plus read-back.
- Break tasks into **atomic tasks**: the smallest unit that realizes one
  intent through bounded tool calls and can be verified on its own. Compose
  long tasks as a dependency graph of atomic tasks with explicit entity
  bindings and a resettable initial state.
- Verifiers check atomic-task completion from **state diffs and tool
  returns**, not from matching a reference tool-call sequence. Keep the
  verifier code and privileged state out of the agent's reach.

### 2. Roll out with variety

Run each task under more than one disclosure view (full brief vs simulated
user revealing requests in order) and more than one harness. Patterns of
failure across views and harnesses help localize the cause: a task that
fails under every harness and view is a suspect task, not a weak policy.

### 3. Attribute each failure

For every failed checkpoint, an attribution step (agent or human) reads the
task graph, trace, checkpoint outcomes and state evidence and assigns one
of:

| Attribution | Signal | Route to |
|:--|:--|:--|
| Policy failure on a valid task | Task passes for some rollouts; state evidence shows a wrong agent action | Keep the task unchanged; it is training signal |
| Environment defect | Tool error or crash, update not persisted, contract violated | Backend revision |
| Task/state defect | Referenced entity missing, dependency unsatisfiable from initial state | Task graph or initial-state revision |
| Verifier defect | Executable checks disagree with rubric-based judgment on the same trace | Verifier revision |

Disagreement between the rubric-based score and the executable score is
the main trigger for verifier review.

### 4. Repair only the responsible component

Revise the selected component and leave the others unchanged. Re-instantiate
affected environments and task states and rerun the construction checks
from step 1. Task semantics stay fixed within a version.

### 5. Revalidate with fresh rollouts, then gate

Run fresh rollouts on the revised version. They confirm the repair and
surface new problems for the next round. Keeping a revision is a
self-modification of the training/evaluation system: it goes through "DO:
Pass every self-modification through one acceptance gate"
(`rules/recursive-improvement.md`): no regression beyond a noise margin δ
estimated from repeated baseline runs, and the negative security testbed
is always strict. A verifier revision must not be made by the policy under
training or scored by it (`rules/agent-evaluation-quality.md`, "DON'T: Let
agents modify their own evaluation harness").

In WEFT, the first two rounds captured most of the gain on AutomationBench
and Claw-Eval; Toolathlon-Verified kept improving in round 3. Track the
tool-error rate per round and stop when it and the downstream scores
flatten.

### 6. Collect data at atomic-task granularity

- **SFT, prefix-preserving rejection sampling**: run tasks in dependency
  order; keep each verified atomic turn with its database and workspace
  state; on failure, restore the pre-turn snapshot and resample only that
  turn (up to k retries).
- **RL task filter**: before RL, score pilot rollouts with an independent
  rubric judge and keep only tasks where both Pearson and Spearman
  correlation with the executable scores meet your threshold (the paper
  does not state its threshold; WEFT kept 1,954 of 5,000 candidates). Use
  only executable rewards in RL.
- **Credit**: sample G candidates per atomic turn from the same restored
  state and compute group-relative advantages from that turn's binary
  completion. Remove positive credit (clip advantage at 0) from turns that
  deterministic checks flag for no-progress repetition, malformed calls or
  interface violations, even when the turn succeeded.

### 7. Serve shared tools with isolated state

Snapshot-based retries need many concurrent rollouts from identical states.
Share tool-service processes across rollouts but give each rollout a
private copy-on-write database and workspace and its own access token. In
WEFT's MegaMCP this cut sandbox upload at 1,000 tasks from 773.5 to 34.8 MiB
(95.5%) and median time to first tool call from 10.455 s to 4.794 s at 100
cold tasks. Screen servers for process-global side effects before letting
them share a process.

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Hard-but-valid tasks "repaired" into easy ones | Attribution blames the task whenever the policy fails | Require state evidence of a component defect; keep tasks that some rollout solves |
| Verifier drifts toward the policy | Verifier revised to accept what the policy does | Revisions use reference executions and executable checks, not policy success rate; pass the acceptance gate |
| Reward hacking via verifier access | Verifier code or privileged state visible to the agent | Run verifiers in the serving layer on immutable initial/final state and the tool-call ledger |
| Cross-rollout contamination | Shared processes with global state | Static screening for process-global side effects; stronger isolation tier for flagged servers |
| Correlation filter drops valid hard tasks | Few pilot rollouts give unstable correlations | Use enough pilot rollouts per task; log dropped tasks for manual review |

## Related

- [`targeted-failure-attribution`](../targeted-failure-attribution/SKILL.md): attribution among agents in a multi-agent run; this skill attributes among system components.
- [`reward-hacking-immunization`](../reward-hacking-immunization/SKILL.md)
- Brief: [`environment-evolution-terminal-agents`](../../research-briefs/environment-evolution-terminal-agents.md), [`cheap-verifier-rl-rewards`](../../research-briefs/cheap-verifier-rl-rewards.md)
- `rules/agent-sandbox-safety.md`: "DON'T: Treat HTTP 200 / success tool return codes as workflow success without state verification"

> Source: WEFT: Scaling Tool-Use Post-Training for General-Purpose Agents (arXiv:2609.36887)
