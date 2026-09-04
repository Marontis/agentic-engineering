---
name: dependency-scoped-plan-validation
description: >
  Validate that pending tool actions derive from current, un-superseded
  memory dependencies before execution in multi-agent and distributed
  systems. Prevents stale-plan execution without costly full-state
  synchronization. Derived from PlanFence (arXiv:2609.03340).
source: https://arxiv.org/abs/2609.03340
---

# Dependency-Scoped Plan Validation

Use this skill when designing or deploying distributed, multi-agent, or
asynchronous tool-execution systems where shared memory or requirements can
mutate while plans are in flight.

## When to Use

- Multi-agent architectures (planner-executor, worker pools, multi-turn pipelines)
  with shared blackboard or database state
- Asynchronous tool execution loops where requirements or external state can update
  between plan generation and tool invocation
- Preventing "stale-plan execution": agents executing tool calls with parameters
  derived from superseded context even when memory itself is up to date
- Systems where global synchronous state locking creates unacceptable coordination
  latency as the shared keyspace grows

## Core Insight

State freshness does **not** imply plan validity. In distributed agent systems,
a planner reads state record $r_3$ and derives plan $p(r_3)$. An upstream agent
then updates the requirement to $r_4$. The executor receives $r_4$ via background
replication, but continues executing the pending step from $p(r_3)$ because the
derivation itself was never checked.

In controlled benchmarks across 30 live workflows with post-plan revisions,
freshness-only executors acted on obsolete plans in **100% of tasks** (Chen et al.,
2026). Requiring plans to cite exact record dependencies and validating only
action-scoped dependencies before tool execution eliminated **100% of invalid
actions** with near-zero coordination stall.

---

## Procedure

### 1. Annotate Plan Actions with Record Dependencies

Ensure the planning agent attaches explicit lineage citations to each planned
action step:

- **Dependency Set**: List the exact public record keys/IDs read when computing the
  action and its parameters (e.g., `deps: ["req:order_spec#v3", "env:dest_branch#v1"]`).
- **Version/Digest Fingerprint**: Record the cryptographic hash or monotonic
  version of each cited dependency at plan creation time.

### 2. Dependency-Scoped Pre-Execution Gate

Before the executor dispatches any external action (file edit, API call, deployment,
database mutation), perform a scoped validation check:

```
For each dependency key in action.dependencies:
    current_version = shared_store.get_version(dependency.key)
    if current_version != dependency.expected_version:
        raise StalePlanException(dependency.key, dependency.expected_version, current_version)
```

- **Scope restriction**: Validate *only* records that can affect the pending
  action. Do not validate unrelated keys in the shared memory space.
- **Independence**: Allows unrelated agents to rapidly mutate other regions of the
  blackboard without causing false-positive plan invalidations.

### 3. Handle Invalidation via Targeted Replanning

When a `StalePlanException` is raised:

- **Immediate abort**: Block tool execution immediately before side effects occur.
- **Targeted context injection**: Pass the diff between the cited record and the
  current record to the planner (`"Requirement order_spec changed from v3 to v4: destination altered"`).
- **Single-replan policy**: Allow exactly one scoped replanning turn to regenerate
  the pending step with fresh arguments. If validation fails repeatedly (>2 attempts),
  escalate to supervisor intervention.

### 4. Choose Synchronization Strategy by Churn and Keyspace

Balance coordination cost against safety using empirical boundaries:

| Workload Characteristics | Optimal Synchronization Pattern |
|:-------------------------|:--------------------------------|
| Low churn (<0.1 updates/step), small keyspace (<50 keys) | **Proactive Sync**: Broadcast updates immediately; invalidate cached plans on arrival. |
| Moderate to high churn (>0.5 updates/step) | **Action-Scoped Gate (PlanFence)**: Delay check until execution time; prevents redundant replans for unused intermediate updates. |
| Large keyspace (>1,000 keys) | **Action-Scoped Gate**: Validating only action-relevant keys avoids O(N) verification overhead. |

---

## Environment Caveats

- **External non-versioned environments**: If external tools read unversioned real-world
  APIs, wrap external fetches in a content-addressable proxy store that assigns
  hashes to observed states.
- **Network partitions**: In distributed deployments, if an executor cannot reach the
  shared store to verify dependencies, fail closed: block execution rather than
  assuming plan validity.

## Failure Modes

- **Citation omission**: The planner uses information from memory without including the
  record ID in the dependency list. Countermeasure: enforce strict input schema
  where plan generators must select dependencies from an explicit state manifest.
- **Over-scoped citations**: Planners citing the entire shared state dictionary rather
  than action-specific keys. This degrades to global locking and causes unnecessary
  replanning churn.

## Cross-References

- [`transactional-coding-sandbox`](../transactional-coding-sandbox/SKILL.md) — Rollback mechanisms for isolating uncommitted file actions.
- [`unified-capability-gateway`](../unified-capability-gateway/SKILL.md) — Enforcing policy gates before action dispatch.
- [`governed-knowledge-graph`](../governed-knowledge-graph/SKILL.md) — Provenance tracking across multi-agent memories.

## Sources

- **Paper**: [Fresh Memory, Stale Plans: Dependency-Scoped Validation for Distributed LLM-Agent Memory](https://arxiv.org/abs/2609.03340) — Chen, Wang, Brinton (Purdue & Exeter, 2026)
- **Praxis source**: `src:2609-03340v1`
