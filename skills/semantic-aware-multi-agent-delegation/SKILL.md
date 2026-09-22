---
name: semantic-aware-multi-agent-delegation
description: >
  Decide when multi-agent collaboration provides genuine value over
  single-agent execution, and implement it via Semantic-Aware
  Incremental Graph Evolution (SAIGE) — dynamically spawning agent
  nodes and encoding semantic dependencies through content-based
  information retrieval.
  Derived from "Rethinking Multi-Agent Collaboration: When More Is
  Less" (arXiv:2609.19759).
source: https://arxiv.org/abs/2609.19759
---

# Semantic-Aware Multi-Agent Delegation (SAIGE)

Use this skill when deciding whether to use multi-agent collaboration
or single-agent execution for a given task, and when implementing
multi-agent coordination with minimal context overhead.

## When to Use

- Evaluating whether a task actually benefits from multi-agent
  collaboration vs. a single-agent harness
- Designing agent delegation for long-horizon tasks with many
  subtasks
- Context overhead from multi-agent coordination is degrading
  performance
- Scaling agent count does not consistently improve outcomes

## Core Insight

Multi-agent collaboration confers **systematic benefits only for
long-horizon tasks with sparse dependencies** — tasks where subtasks
can proceed independently with minimal cross-referencing. For
**tightly coupled, sequential workflows**, single-agent harnesses
remain superior because the context overhead of inter-agent
communication exceeds the benefit of parallelism. More agents do not
necessarily make a system more intelligent; scaling the agent pool or
deepening recursion does not consistently improve outcomes.

**Evidence**: SAIGE achieves favorable trade-off between context
efficiency and task performance on long-horizon benchmarks.
Experiments confirm that increasing agent count or recursion depth
yields diminishing and sometimes negative returns.

---

## Procedure

### 1. Classify Task Structure

Before choosing single-agent vs. multi-agent, assess the task along
two dimensions:

| Dimension | Single-Agent Favored | Multi-Agent Favored |
|:----------|:--------------------|:--------------------|
| **Horizon** | Short (few steps) | Long (many steps) |
| **Dependencies** | Tight (each step depends on previous) | Sparse (subtasks are independent) |
| **Context coupling** | High (shared state throughout) | Low (subtasks have distinct contexts) |
| **Workflow type** | Sequential pipeline | Parallel or tree-structured |

**Decision rule**: Use multi-agent only when the task is long-horizon
AND has sparse dependencies. Default to single-agent otherwise.

### 2. Initialize SAIGE Graph

If multi-agent is warranted:

1. Create a **root agent node** responsible for task decomposition
2. The graph starts empty — no pre-allocated agent pool
3. Nodes = agent instances; Edges = semantic dependencies between
   their subtasks

### 3. Spawn Agent Nodes On-Demand

For each subtask identified during decomposition:

1. Spawn a **new agent instance** as a node in the graph only when
   the subtask is ready for execution
2. Do NOT pre-allocate agents — spawn on demand to minimize idle
   context
3. Assign each agent a **scoped context** containing only the
   information relevant to its subtask

### 4. Establish Semantic Dependencies via Content-Based Retrieval

Instead of explicit message passing between agents:

1. When an agent needs information from another subtask, use
   **content-based information retrieval** against completed agent
   outputs
2. This creates an **edge** in the graph encoding the semantic
   dependency
3. The graph evolves **incrementally** — edges are added only when
   actual dependencies materialize, not speculatively

### 5. Limit Recursion and Agent Count

Based on the paper's empirical findings:

1. **Do NOT** scale agent pool beyond what the task structure requires
2. **Do NOT** deepen recursion levels hoping for better results
3. Monitor for **diminishing returns** — if adding agents doesn't
   improve task completion rate, stop
4. Set hard caps on agent count and recursion depth based on task
   complexity estimates

### 6. Aggregate Results

1. Collect outputs from all leaf agent nodes
2. The root agent synthesizes final output using content-based
   retrieval across all completed subtask results
3. Validate that the aggregated result is coherent and complete

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Context overhead exceeds benefit | Tightly coupled task decomposed into too many agents | Use task structure classification (Step 1); default to single-agent |
| Diminishing returns from scaling | More agents spawned than subtasks warrant | Hard caps on agent count; monitor marginal improvement |
| Lost information in sparse retrieval | Semantic dependency not captured by content-based retrieval | Add explicit dependency edges when retrieval misses critical context |
| Redundant work across agents | Multiple agents tackle overlapping subtasks | Dedup at spawn time; check graph for existing coverage |
| Deep recursion without convergence | Recursive delegation produces diminishing-quality subtasks | Cap recursion depth; validate subtask quality at each level |

> Source: Yuan et al., "Rethinking Multi-Agent Collaboration: When
> More Is Less" (arXiv:2609.19759), Sep 2026.
