---
name: speculative-macro-commit
description: >
  Accelerate tool-using agent execution via speculative multi-step action chains.
  Pre-executes recurring tool macros in isolated sandbox snapshots and commits
  cached steps when the authoritative actor verifies the chain prefix.
  Derived from Speculative Macro Commit (arXiv:2609.03236).
source: https://arxiv.org/abs/2609.03236
---

# Speculative Macro Commit

Use this skill when designing or optimizing tool-using LLM agent runtimes to reduce
end-to-end wall-clock latency in sequential multi-turn action loops.

## When to Use

- Tool-heavy agent loops where environment transitions, API calls, and model inference
  compound into severe latency bottlenecks (e.g., terminal workflows, web navigation,
  SWE benchmarks)
- Systems where single-step speculative execution yields diminishing returns due to
  repetitive multi-step action patterns
- High-concurrency agent serving architectures with two model tiers available (a large
  authoritative actor and a fast speculative drafter)
- Environments supporting lightweight filesystem, browser, or container snapshots

## Core Insight

Sequential agent loops suffer from serial action-observation dependencies: the next model
prompt cannot be assembled until the prior tool action finishes and returns its output.
Standard speculative actions only guess one step ahead.

However, real-world agent trajectories exhibit **recurring multi-action skeletons** (macros),
such as `locate_file -> view_file -> edit_file` or `search_item -> inspect_details -> add_to_cart`.
By maintaining an offline-mined macro library and executing drafted multi-action chains
within an **isolated environment snapshot**, a fast drafter can run ahead. When the authoritative
actor verifies the first step of the chain, the entire remaining sequence of pre-executed
actions and cached observations is committed instantly to the official state.

On benchmark evaluations:
- **τ²-Bench Telecom**: SMC reduced latency by **18.59%** over sequential execution and
  **10.23%** over single-step speculative actions, with zero loss in task accuracy.
- **AppWorld**: SMC reduced wall-clock execution time by **44.9%** over sequential baselines.

---

## Procedure

### 1. Offline/Background Macro Mining

Mine high-frequency tool action sequences from existing agent execution traces:

- **Skeleton extraction**: Parameterize tool traces by replacing specific string
  literals with variable slots (e.g., `git_checkout(branch)` followed by `git_status()`).
- **N-gram frequency filtering**: Identify contiguous tool-call n-grams (lengths 2 to 4)
  with high support and high conditional probability:
  $$P(a_{t+1}, \dots, a_{t+k} \mid a_t) \ge \theta_{\text{macro}} \quad (\text{default } \theta = 0.65)$$
- **Index creation**: Store mined skeletons in a runtime macro index keyed by the
  initial tool name and intent signature.

### 2. Two-Tier Runtime Setup

Instantiate a dual-agent execution loop:
- **Authoritative Actor**: High-capacity frontier model (e.g., 27B+ or commercial API)
  responsible for ground-truth decisions.
- **Speculative Drafter**: Lightweight, low-latency model (e.g., 3B–8B parameter model).
- **Isolated Sandbox Workspace**: A CoW filesystem snapshot or cloned container instance
  mirroring the official environment.

### 3. Speculative Branching & Execution

While the Authoritative Actor computes its next action $a_t$:

1. **Draft candidate chain**: The Drafter predicts the next action and retrieves matching
   skeletons from the macro library to construct candidate chain $\hat{C} = (\hat{a}_t, \hat{a}_{t+1}, \dots, \hat{a}_{t+k})$.
2. **Snapshot and pre-execute**: Clone the environment state into the speculative sandbox.
3. **Execute forward**: Run each action $\hat{a}_{t+j}$ in sequence within the sandbox,
   recording intermediate observations $\hat{o}_{t+j}$ and output states.

### 4. Verification and Macro Commit Gate

When the Authoritative Actor produces its verified action $a_t$:

- **Prefix match test**: Compare $a_t$ against the drafter's first step $\hat{a}_t$:
  - **Match ($a_t == \hat{a}_t$)**: Commit the speculative branch!
    1. Fast-forward the official trajectory with $(\hat{a}_{t+1}, \dots, \hat{a}_{t+k})$
       and their cached observations $(\hat{o}_{t}, \dots, \hat{o}_{t+k})$.
    2. Promote the speculative sandbox state to the official environment (via atomic
       pointer swap or filesystem commit).
    3. Skip actor inference for the next $k$ steps or launch drafting for $t+k+1$.
  - **Mismatch ($a_t \neq \hat{a}_t$)**: Discard the speculative branch.
    1. Destroy or reset the sandbox snapshot.
    2. Execute $a_t$ in the official environment normally.

---

## Environment Caveats

- **Irreversible side effects**: Never execute non-idempotent or external real-world actions
  (e.g., sending emails, issuing financial transactions) speculatively. Restrict macro
  speculation strictly to local sandboxes, read-only tools, or transactional APIs.
- **Snapshot creation overhead**: Ensure snapshot creation is cheap (<50ms). Use CoW
  filesystems (Btrfs, ZFS), memory-backed Docker containers, or git worktrees. If snapshotting
  takes >200ms, single-step speculation or sequential execution is faster.

## Failure Modes

- **Cascading hallucination**: A drafter generating an invalid parameter in step 1 causing
  downstream tool errors in step 2. Mitigation: abort speculation immediately if any
  sandboxed tool call returns an exception.
- **State divergence**: If the speculative sandbox does not accurately mirror hidden
  environment state (e.g., timestamps or random seeds), the pre-executed observations
  may fail when committed.

## Cross-References

- [`speculative-sandbox-scheduler`](../speculative-sandbox-scheduler/SKILL.md) — Prewarming sandboxes and scheduling resources.
- [`transactional-coding-sandbox`](../transactional-coding-sandbox/SKILL.md) — Rollback and snapshot mechanics for agent workspaces.
- [`prefix-preserving-context-assembly`](../prefix-preserving-context-assembly/SKILL.md) — Preserving KV-cache efficiency during speculative turns.

## Sources

- **Paper**: [Speculative Macro Commit for Faster Tool-Using Agents](https://arxiv.org/abs/2609.03236) — Liu, Kundu, Beerel (USC & Intel Labs, 2026)
- **Praxis source**: `src:2609-03236v1`
