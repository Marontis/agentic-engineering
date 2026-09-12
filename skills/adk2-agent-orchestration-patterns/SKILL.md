---
name: adk2-agent-orchestration-patterns
description: >
  Implement Google Agent Development Kit (ADK) 2's three core orchestration
  patterns: Graph Workflows (deterministic functions, JoinNode, dict routers),
  Collaborative Agents (single_turn parallel dispatch vs task mode subroutines),
  and Dynamic Workflows (runtime parallel_worker fan-out, recursive ctx.run_node).
  Includes the 1-question decision tree and composition rules.
  Derived from Google Cloud Tech "Graph Engineering with ADK" and official Codelab.
---

# ADK 2 Agent Orchestration Patterns

Use this skill to design, architect, and implement multi-agent systems using the
three foundational orchestration pillars of the Google Agent Development Kit (ADK) 2.

## When to Use

- Designing multi-agent workflows where some operations are deterministic code ($0$ LLM calls) and some require reasoning
- Choosing between static graph workflows, dynamic collaborative teams, and recursive runtime execution
- Replacing bloated prompt-based delegation with structured, typed orchestration
- Coordinating specialist subagents in parallel with unified synthesis (`mode="single_turn"`)
- Implementing conversational intake or slot-filling subroutines with a typed finish line (`mode="task"`)
- Performing deep research or multi-hop decomposition with runtime-sized fan-out and bounded recursive depth

---

## Core Mental Model

> **"Predictable work stays as functions; clear rules become explicit routing; reasoning uses the model."**

Every ADK 2 system answers one fundamental question: **Who decides what runs next?**

| Pillar | Who Decides Next Step | Primary Mechanism | Best For |
|:---|:---|:---|:---|
| **Pillar 1: Graph Workflows** | **The developer (the graph drawn ahead of time)** | `Workflow(edges=...)`, `JoinNode`, dict-based router | Known flow before input arrives; mixing code and LLMs |
| **Pillar 2: Collaborative Agents** | **The LLM coordinator** | `Agent(sub_agents=..., mode="single_turn" | "task")` | Known team of specialists; user request selects the subset |
| **Pillar 3: Dynamic Workflows** | **Python code at runtime** | `@node(parallel_worker=True)`, `ctx.run_node` recursion | Work shape (width or depth) depends dynamically on input |

---

## The Decision Tree

```
Would a prebuilt SequentialAgent / ParallelAgent / LoopAgent suffice?
│
├─ YES ──────────────────────────────► Use prebuilt agent (cheapest, no graph needed)
│
└─ NO — I need routing, payload joining, or non-agent function nodes
   │
   Can you draw the workflow before the input arrives?
   │
   ├─ YES ───────────────────────────► Pillar 1: Graph Workflow
   │                                    (Static DAG, JoinNode, dict-edge router)
   │
   └─ NO
      │
      ├─ Known team, request picks subset? ─► Pillar 2: Collaborative Agents
      │                                       (Coordinator + single_turn / task subagents)
      │
      └─ Does the shape itself depend on input? ─► Pillar 3: Dynamic Workflow
                                                   (Runtime width & recursive depth in code)
```

---

## Pillar 1: Graph Workflows (Static Structure)

Use when the execution pipeline is known in advance. Plain Python functions cost **0 LLM calls** and sit as peer nodes alongside reasoning agents.

### Pattern: Parallel Fan-out, JoinNode, and Deterministic Router

```python
from google.adk import Agent, Event, Workflow
from google.adk.workflow import JoinNode, START

# 1. Deterministic fetch nodes (Functions = 0 LLM calls)
async def fetch_weather(node_input):
    data = await weather_api.get()
    return Event(output=data)

async def analyze_course(node_input):
    data = await db.get_course()
    return Event(output=data)

# 2. JoinNode bundles parallel outputs into a keyed dictionary
join_inputs = JoinNode(name="join_inputs")

# 3. Deterministic Router (Plain Python if-statement, 0 LLM calls)
def route_by_conditions(node_input):
    # node_input is keyed by upstream function names:
    temp = node_input["fetch_weather"]["temp_f"]
    if temp >= 80:
        route = "HOT"
    elif temp <= 40:
        route = "COLD"
    else:
        route = "NORMAL"
    # Return route parameter matching the dictionary edge
    return Event(output=node_input, route=route)

# 4. Specialized Reasoning Agents (Only ONE runs)
hot_agent = Agent(name="hot_agent", model=MODEL, instruction="...")
normal_agent = Agent(name="normal_agent", model=MODEL, instruction="...")
cold_agent = Agent(name="cold_agent", model=MODEL, instruction="...")

# 5. Assemble the Workflow with Dict Edge
workflow = Workflow(
    name="marathon_advisor",
    edges=[
        (START, fetch_weather, join_inputs),
        (START, analyze_course, join_inputs),
        (join_inputs, route_by_conditions),
        (route_by_conditions, {
            "HOT": hot_agent,
            "NORMAL": normal_agent,
            "COLD": cold_agent,
        }),
    ],
)
```

**Net Cost**: Exactly **1 LLM call** instead of 4+ in naive multi-agent pipelines.

---

## Pillar 2: Collaborative Agents (Dynamic Selection)

Use when you have a declared team of specialists, but the incoming query determines which subset needs to respond.

### The Three Collaboration Modes

The `mode` parameter on subagents completely changes the orchestration mechanics:

| Mode | Communication Pattern | Execution Behavior |
|:---|:---|:---|
| **`mode=None` (Chat)** | Serial handoff | Coordinator gets only `transfer_to_agent`. Handed off to **exactly one** specialist. User is stranded with that specialist; **no parallelism, no synthesis**. |
| **`mode="single_turn"`** | Parallel tool dispatch + synthesis | ADK exposes each subagent as a tool. Coordinator calls an arbitrary subset **in parallel** (multiple calls in one turn), each returns a typed schema, coordinator synthesizes. |
| **`mode="task"`** | Conversational subroutine | Subagent interacts with the user across multiple turns until target fields are collected, then calls `finish_task(schema)`. Control returns to parent. |

### Pattern A: Parallel Specialist Dispatch with Synthesis (`single_turn`)

```python
from google.adk import Agent
from pydantic import BaseModel, Field

class SpecialistInput(BaseModel):
    user_query: str
    context: dict

class SpecialistResponse(BaseModel):
    concern_level: str
    recommendation: str

# Define specialists with mode="single_turn"
medical_specialist = Agent(
    name="medical_specialist",
    model=MODEL,
    mode="single_turn",  # Turns subagent into a callable tool
    input_schema=SpecialistInput,
    output_schema=SpecialistResponse,
    description="Consult for injury, pain, hydration safety, heat exhaustion.",
    instruction="Analyze medical implications only. Return structured response.",
)

nutrition_specialist = Agent(
    name="nutrition_specialist",
    model=MODEL,
    mode="single_turn",
    input_schema=SpecialistInput,
    output_schema=SpecialistResponse,
    description="Consult for fueling plans, gels, electrolytes, hydration timing.",
    instruction="Analyze nutrition and hydration only. Return structured response.",
)

# Coordinator calls the subset in parallel and synthesizes
coordinator = Agent(
    name="race_concierge",
    model=MODEL,
    sub_agents=[medical_specialist, nutrition_specialist],
    instruction="""You are the concierge.
1. Decide which specialists are relevant to the runner's question.
2. Call all relevant specialist tools IN PARALLEL.
3. Synthesize their recommendations into one unified response for the runner.""",
)
```

### Pattern B: Conversational Subroutine with Typed Finish Line (`task`)

Use for guided intake (forms, orders, troubleshooting) where an agent must converse with the user *until* specific data is gathered:

```python
class GearOrder(BaseModel):
    item: str
    size: str
    notes: str

gear_fitter = Agent(
    name="gear_fitter",
    model=MODEL,
    mode="task",               # Pauses run when asking clarifying questions
    output_schema=GearOrder,   # Injects finish_task tool validating this schema
    description="Collects runner gear preferences and sizes, then completes order.",
    instruction="""Ask clarifying questions until you know the runner's size and item.
Once verified, call finish_task with the validated GearOrder.""",
)

front_desk = Agent(
    name="front_desk",
    model=MODEL,
    sub_agents=[gear_fitter],
    instruction="For gear requests, delegate to gear_fitter. Confirm order once returned.",
)
```

---

## Pillar 3: Dynamic Workflows (Runtime Shape)

Use when the structure of the work cannot be drawn ahead of time (e.g. recursive deep research, hierarchical tree search).

### Pattern: Runtime-Sized Fan-Out + Bounded Recursive Spawning

```python
from google.adk import Agent, Event, Workflow
from google.adk.workflow import node, RetryConfig, START

MAX_DEPTH = 2  # Hard boundary maintained in code
RESEARCH_RETRY = RetryConfig(max_attempts=3, initial_delay=2.0, backoff_factor=2.0)

# Step 1: Decompose query into runtime-sized list
@node(rerun_on_resume=True)
async def decompose(ctx, node_input):
    plan = await ctx.run_node(decomposer_agent, node_input=node_input)
    # Yields a list -> triggers parallel_worker for each item
    yield Event(output=[{"query": q, "depth": 1} for q in plan.sub_queries])

# Step 2: Parallel worker with recursive self-invocation
@node(parallel_worker=True, rerun_on_resume=True, retry_config=RESEARCH_RETRY)
async def research_topic(ctx, node_input):
    query = node_input["query"]
    depth = node_input["depth"]
    
    finding = await ctx.run_node(research_agent, node_input=query)
    
    children = []
    # Boundary brake: enforce MAX_DEPTH in Python code
    if finding.needs_deeper and finding.sub_queries and depth < MAX_DEPTH:
        deeper = [{"query": dq, "depth": depth + 1} for dq in finding.sub_queries]
        # Recursively call itself within the ADK framework
        children = await ctx.run_node(research_topic, node_input=deeper)
        
    yield Event(output={"query": query, "depth": depth, "summary": finding.summary, "children": children})

# Step 3: Aggregate hierarchical findings
@node(rerun_on_resume=True)
async def synthesize(ctx, node_input):
    briefing = await ctx.run_node(synthesizer_agent, node_input=node_input)
    yield Event(output=briefing)

dynamic_workflow = Workflow(
    name="deep_research",
    edges=[(START, decompose, research_topic, synthesize)],
)
```

---

## Composition Rules

The three patterns are **not mutually exclusive**:
1. **Graph calling Collaborative**: A deterministic graph pipeline (Pillar 1) can route into a collaborative specialist team (Pillar 2).
2. **Collaborative triggering Dynamic**: A specialist agent (Pillar 2) can trigger a dynamic recursive deep research workflow (Pillar 3).
3. **Graph containing Dynamic Nodes**: Dynamic runtime workers (`parallel_worker=True`) live as ordinary nodes in a graph workflow.

---

## Key Pitfalls & Defenses

1. **The Chat Mode Stranding Trap**: Leaving `mode` unset on subagents causes the coordinator to permanently hand off the session via `transfer_to_agent`, killing parallelism. Always use `mode="single_turn"` for tools/synthesis or `mode="task"` for intake.
2. **Unbounded Dynamic Recursion**: Never allow recursive `@node` calls without an explicit `depth < MAX_DEPTH` condition and schema-level array constraints (`max_length`).
3. **Transient Parallel Failures**: In `parallel_worker=True`, an unhandled exception in one child cancels all siblings. Always attach a `RetryConfig` to the worker node so transient 429/503 errors do not discard completed sibling work.
