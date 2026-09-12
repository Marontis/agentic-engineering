# ADK 2 Orchestration: Graph, Collaborative & Dynamic Workflows

> **Video**: [Graph Engineering with ADK](https://www.youtube.com/watch?v=Mzr7byMFy_4) (Google Cloud Tech)  
> **Codelab**: [ADK 2 Orchestration: Graph, Collaborative & Dynamic Workflows](https://codelabs.developers.google.com/adk2/instructions#0)  
> **Repository**: [cuppibla/adk2-tutorial](https://github.com/cuppibla/adk2-tutorial)  
> **Praxis source**: `src:adk-2-orchestration-graph-collaborative-dynamic-workflows`  
> **Related Skill**: [`adk2-agent-orchestration-patterns`](../skills/adk2-agent-orchestration-patterns/SKILL.md)

---

## Executive Overview

Google's Agent Development Kit (ADK) 2 introduces a unified architectural framework that reconciles deterministic software engineering with stochastic LLM reasoning. Through a progressive 6-level curriculum (L0 to L5), the talk and companion codelab dismantle common multi-agent anti-patterns—such as using LLMs as expensive, unreliable routers or forcing serial conversational handoffs—and establish three foundational orchestration pillars:

1. **Graph Workflows**: The developer draws the DAG ahead of time. Pure Python functions and LLM agents are peer nodes.
2. **Collaborative Agents**: The coordinator LLM decides which specialist to call at runtime, either via parallel single-turn tool dispatches or conversational task subroutines with typed terminal schemas.
3. **Dynamic Workflows**: Python code determines execution shape at runtime, enabling arbitrary fan-out (`parallel_worker=True`) and recursive subtask descent (`ctx.run_node`) with preserved telemetry and checkpoints.

The central guiding principle across ADK 2 is:
> *"Predictable work stays as functions; clear rules become explicit routing; reasoning uses the model."*

---

## The Paradigm Shift: ADK 1.x vs ADK 2

ADK 1.x suffered from rigid coupling where agents were primarily conversational peers. Routing was achieved via prompt instructions or brittle string parsing, branching required complex state machines, and mixing deterministic code with agentic reasoning forced awkward wrapper agents.

| Capability | ADK 1.x | ADK 2 |
|:---|:---|:---|
| **Graph Definition** | Complex custom state-machine scaffolding | Declarative `Workflow(edges=...)` with pure dict-based branching |
| **Function Execution** | Must wrap functions in mock agent wrappers | Pure Python functions are 1st-class peer graph nodes ($0$ LLM cost) |
| **Multi-Agent Coordination** | Serial `transfer_to_agent` handoffs (strands user) | `mode="single_turn"` (parallel tool dispatch) and `mode="task"` (typed subroutine) |
| **Payload Aggregation** | Ad-hoc session key merging | Native `JoinNode(branches=[...])` awaiting barrier completion |
| **Dynamic Fan-out & Depth** | Uninstrumented raw Python loops (breaks tracing) | `@node(parallel_worker=True)` and recursive `ctx.run_node` within framework |
| **Terminal Contracts** | Natural language consensus or sentiment guessing | Strongly-typed `finish_task(PydanticModel)` schemas |

---

## The Three Orchestration Pillars

ADK 2 classifies any agentic workflow by asking: **"Who decides what runs next?"**

### Pillar 1: Graph Workflows (The Developer Decides)
- **When to use**: The workflow structure (steps, branches, joins) is known before the user prompt arrives.
- **Peer Nodes**: Pure Python functions (`def node(ctx: InvocationContext)`) and LLM `Agent` instances share the exact same interface. Deterministic preprocessing, validation, database fetching, and formatting execute in Python code at zero token cost and zero hallucination risk.
- **Deterministic Routing**: Edges accept dictionary lookups (`edges={router_func: {"technical": tech_agent, "billing": billing_agent}}`). An LLM or code classifier returns a discrete string; the framework performs deterministic edge transition.
- **Join Semantics**: `JoinNode(branches=[node_a, node_b])` acts as a synchronization barrier, collecting outputs from parallel branches into a unified dictionary before passing downstream.

### Pillar 2: Collaborative Agents (The LLM Coordinator Decides)
- **When to use**: A known pool of specialist agents exists, but the user request determines which subset must be invoked.
- **Mode Comparison**:
  - `mode=None` (Default / Chat): Subagents are conversational peers. The coordinator transfers conversation context, stranding the user with the specialist. No central synthesis occurs.
  - `mode="single_turn"`: Subagents are exposed as callable function tools to the coordinator. The coordinator can invoke multiple specialists in parallel in a single turn, inspect all tool outputs, and synthesize a single coherent response.
  - `mode="task"`: The subagent acts as an isolated conversational subroutine with a dedicated objective. It can engage in clarifying back-and-forth dialogue with the user to fill required slots. Crucially, it exits only by invoking a typed tool `finish_task(schema=...)`, returning validated structured output to the coordinator.

### Pillar 3: Dynamic Workflows (Python Code at Runtime Decides)
- **When to use**: The topology (width or depth) cannot be defined statically because it depends entirely on the input or intermediate model generations.
- **Dynamic Width**: An analyzer agent generates an arbitrary list of research subtopics. A `@node(parallel_worker=True)` executes dynamically across each subtopic in parallel using `ctx.run_node`.
- **Dynamic Depth (Recursion)**: Complex tasks decompose recursively. A recursive node evaluates whether a problem requires further decomposition. If so, it invokes `ctx.run_node(recursive_step, depth=depth + 1)`.
- **Framework Integration**: Invoking child steps via `ctx.run_node` instead of unmanaged `asyncio.gather` ensures that ADK 2 logs, traces, event streams, and checkpoint-restore states are fully preserved across dynamic subtrees.

---

## Architectural Decision Matrix

```
Start
  │
  ├─ Can the steps and routing be drawn as a static graph ahead of time?
  │    ├─ YES ──► Pillar 1: Graph Workflow
  │    │           (Prebuilt Agents, Function Nodes, JoinNode, Dict Edges)
  │    │
  │    └─ NO
  │         ├─ Is there a known team of specialists chosen by prompt intent?
  │         │    └─ YES ──► Pillar 2: Collaborative Agents
  │         │                ├─ One-shot multi-specialist synthesis? ──► mode="single_turn"
  │         │                └─ Interactive slot-filling subroutine? ──► mode="task"
  │         │
  │         └─ Does the number of parallel steps or recursive depth vary at runtime?
  │              └─ YES ──► Pillar 3: Dynamic Workflows
  │                          ├─ Runtime width? ──► @node(parallel_worker=True)
  │                          └─ Runtime depth? ──► ctx.run_node recursion with MAX_DEPTH
```

---

## Composition Rules & Production Best Practices

1. **Pillars Compose Hierarchically**:
   - A Pillar 1 Graph Node can be an entire Pillar 2 Collaborative Coordinator.
   - A Pillar 2 Specialist Agent can trigger a Pillar 3 Dynamic Research Workflow.
2. **Strict Recursion Ceilings**:
   - Always pass an explicit `depth` counter and enforce a hard limit (`MAX_DEPTH=2` or `3`). Without a hard ceiling, stochastic agent feedback easily triggers runaway recursion.
3. **Keep Code as Code**:
   - Never replace an existing Python library, SQL query, regex, or deterministic validator with an LLM prompt. Every unnecessary LLM call introduces latency, cost, and a failure probability.
4. **Structured Terminal Contracts**:
   - In conversational subroutines (`mode="task"`), always require a Pydantic schema for `finish_task`. Never rely on natural language markers like `"I AM FINISHED"` to exit loops.
