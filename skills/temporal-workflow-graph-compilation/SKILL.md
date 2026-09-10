---
name: temporal-workflow-graph-compilation
description: >
  Compile a task and a set of role-specialized agents into a sequence of
  directed communication graphs with edge-level message instructions.
  Training-free framework for multi-agent orchestration.
  Derived from "ReActNet" (arXiv:2609.05774).
source: https://arxiv.org/abs/2609.05774
---

# ReActNet: Temporal Workflow Graph Compilation

Use this skill when orchestrating multi-agent LLM systems where the
communication topology should be task-conditioned rather than static.

## When to Use

- You have multiple role-specialized agents that need dynamic coordination
- Static topologies (chain, star, debate) don't match the task's reasoning
  structure
- You want training-free orchestration that compiles a query into an
  execution plan
- Edge-level communication semantics (what each agent should tell each
  other) matter for quality

## Core Insight

Rather than optimizing a static multi-agent topology, ReActNet synthesizes
a **task-conditioned temporal workflow graph** that jointly specifies agent
connectivity *and* edge-level communication semantics. Each graph snapshot
corresponds to one reasoning stage, and each directed edge carries a
natural-language instruction specifying what message a source agent should
provide to a target agent. The compiled temporal graph is then executed
through structured message passing.

---

## Procedure

### 1. Define the Agent Roster

Enumerate available agents with their role specifications:
- Agent name and specialization (e.g., "Researcher", "Critic", "Planner")
- Capability description (what kinds of tasks each agent handles)
- Input/output interface (what each agent expects and produces)

### 2. Compile the Task into a Temporal Graph

Given a query and the agent roster:
1. Decompose the query into reasoning stages (sequential phases
   needed to solve the task)
2. For each stage, determine which agents need to communicate:
   - Which agent produces information needed by which other agent?
   - What specific message should flow along each edge?
3. Output a sequence of directed graphs, one per stage:
   - Nodes = active agents in this stage
   - Directed edges = communication channels with NL instructions
   - Edge labels = what the source should tell the target

### 3. Execute Through Structured Message Passing

For each stage in the temporal graph sequence:
1. Activate the agents specified in this stage's graph
2. For each directed edge, the source agent generates a message
   following the edge's NL instruction
3. Target agents receive messages from all incoming edges before
   producing their output
4. Advance to the next stage

### 4. Aggregate Final Output

After the last stage:
- Collect outputs from designated terminal agents
- If multiple terminal agents exist, apply a merge strategy
  (concatenation, voting, or synthesis by a designated aggregator)

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Over-complex graph | Task decomposed into too many stages | Limit stages to 3-5; merge stages with low inter-agent dependency |
| Missing edge | Critical information flow not specified | Verify graph completeness by checking each agent's input requirements are satisfied by incoming edges |
| Circular dependencies | Stage graph contains cycles | Enforce DAG structure within each stage; cycles only across stages |
| Edge instruction ambiguity | NL edge labels too vague | Specify edge labels with concrete output format requirements |

## Sources

> Source: "Inference-Time Graph Engineering for Multi-Agent LLM Workflows" (arXiv:2609.05774), ReActNet framework.
