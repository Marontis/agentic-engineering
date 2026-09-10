---
name: procedural-graph-evolution
description: >
  Build and self-evolve procedural graphs that guide LLM agent
  action selection.  Covers graph construction from trajectories,
  inference-time guidance, and self-evolution from execution feedback.
  Derived from "Procedural Graphs" (arXiv:2609.09153).
---

# Procedural Graph Evolution

Use this skill when you want LLM agents to follow structured
execution patterns that improve over time from experience.

## When to Use

- Your agent makes poor action choices in long-horizon tasks
- You want to encode successful execution patterns as reusable structure
- You need agents to improve their action selection without retraining
- You want deterministic, auditable execution guidance

## Core Insight

Free-form LLM agents waste actions exploring dead ends.  **Procedural
graphs** encode successful action sequences as directed graphs where
nodes are action types and edges represent observed transitions.
At inference time, the graph constrains and guides the agent's
action selection.  The graph self-evolves from execution feedback,
adding successful patterns and pruning failed ones.

## Procedure

### Step 1: Construct initial procedural graph

From a set of successful execution trajectories:

1. Parse each trajectory into a sequence of (state, action, result) tuples
2. Extract action types (e.g., "search", "read_file", "edit", "test")
3. Build a directed graph where:
   - Nodes = action types
   - Edges = observed transitions (action A followed by action B)
   - Edge weights = frequency of the transition in successful trajectories

### Step 2: Serialize graph for inference-time guidance

At inference time, serialize the relevant subgraph into the agent's
context:

```
Current action: search
Likely next actions (from procedural graph):
  → read_file (observed 45% of the time after search)
  → search (another search, 30%)
  → edit (direct edit, 15%)
  → test (10%)
```

The agent uses this as a soft prior, not a hard constraint.  It can
deviate when the situation warrants, but the graph nudges it toward
proven patterns.

### Step 3: Self-evolution from execution feedback

After each task execution:

1. **Record**: Log the full trajectory with success/failure outcome
2. **Induction**: If a new successful transition pattern appears
   (action sequence not in the graph), add the edges
3. **Pruning**: If an edge consistently leads to failure
   (failure rate > threshold), reduce its weight or remove it
4. **Node update**: If a node's description doesn't match how the
   action is actually used, update the node metadata

### Step 4: Structural validation

After each evolution round:

- **Cycle detection**: Ensure the graph doesn't contain infinite
  loops (cycles are ok if they have exit conditions)
- **Reachability**: Verify all terminal actions (submit, finish)
  are reachable from all start actions
- **Weight normalization**: Re-normalize edge weights so they sum
  to 1.0 for each source node

## Environment Caveats

- **Novel tasks**: On tasks unlike anything in the training
  trajectories, the graph may mislead.  Include a "freeform"
  escape that lets the agent ignore the graph when confidence
  is low.
- **Task diversity**: A graph trained on coding tasks won't
  help with research tasks.  Maintain separate graphs per
  task domain or use a multi-graph with domain routing.
- **Graph size**: For large action spaces, the graph becomes
  unwieldy.  Limit to the top-K transitions per node.

## Failure Modes

- **Overfitting to early trajectories**: If initial trajectories
  are suboptimal, the graph encodes bad patterns.  Seed with
  high-quality demonstrations.
- **Pruning too aggressively**: An action sequence that fails
  on one task may be essential for another.  Use task-conditioned
  pruning, not global pruning.
- **Ignoring the graph**: If the serialized graph is too long,
  the agent may ignore it.  Keep serialization concise —
  only the relevant subgraph for the current action.

## Cross-References

- [`knowledge-compounding-loop`](../knowledge-compounding-loop/SKILL.md) —
  Both accumulate knowledge from execution; procedural graphs
  focus on structural action patterns, compounding on factual knowledge
- [`skill-design-methodology`](../skill-design-methodology/SKILL.md) —
  Procedural graphs are a machine-readable complement to
  human-readable skill documents

## Sources

- Procedural Graphs: Self-Evolving Execution Structures for LLM Agents (arXiv:2609.09153)
