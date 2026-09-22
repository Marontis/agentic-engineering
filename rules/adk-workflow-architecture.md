# ADK Workflow Architecture Rules

> Research-backed guardrails for designing, orchestrating, routing, and deploying
> multi-agent graph workflows with Google Agent Development Kit (ADK) 2. These rules
> should be active whenever designing, reviewing, or debugging agent workflows.

---

## Control Flow & Determinism

### DO: Enforce human approvals and safety gates in the runtime, NOT in prompt instructions

System prompt directives instructing a model to "ask the user for confirmation before proceeding" are advisory. In a conversational loop, follow-up turns or user overrides ("skip questions, just proceed") easily bypass prompt-level instructions because no external harness restricts execution.

Enforce critical gates at the graph runtime using `yield RequestInput(...)`:
- Suspends the workflow engine immediately, recording an open interrupt in the session store (`sessions.db`).
- Halts execution cleanly without consuming active worker threads or LLM tokens.
- Resumes execution *only* when an external, schema-validated `FunctionResponse` matching the `interrupt_id` arrives. Arbitrary chat text cannot advance the graph.

```python
# Function node suspending for human decision
def direction_gate(node_input):
    yield RequestInput(
        message="Select video direction: 1, 2, 3, or 4.",
        response_schema={
            "type": "object",
            "properties": {"pick": {"type": "string", "enum": ["1", "2", "3", "4"]}},
            "required": ["pick"],
        },
        payload={"candidates": node_input.get("candidates", [])},
    )
```

> Source: Google ADK Codelab: Agentic Workflow with ADK (Steps 2 & 4)

### DO: Evaluate deterministic policy checks BEFORE invoking generative models

Never rely on an LLM to evaluate its own policy compliance when deterministic criteria exist. Model self-evaluation is non-deterministic, vulnerable to adversarial phrasing, and incurs latency and token cost.

Implement a dedicated router node that runs regex matching, word lists (`policy_words.txt`), or static schemas:
- Executes in sub-milliseconds at **0 LLM token cost**.
- Routes compliant inputs directly to downstream execution (`route="OK"`).
- Routes non-compliant inputs to quarantine or remediation paths (`route="BLOCK"`).

```python
def policy_check(node_input):
    text = f"{node_input.get('title', '')} {node_input.get('angle', '')}".lower()
    has_violation = any(word in text for word in REFUSED_WORDS)
    return Event(output=node_input, route="BLOCK" if has_violation else "OK")
```

> Source: Google ADK Codelab: Agentic Workflow with ADK (Step 5)

### DO: Always provide a default fallback route (`DEFAULT_ROUTE`) on conditional routers

Routers returning conditional routes must declare a `DEFAULT_ROUTE` edge in the workflow edge dictionary. If an unexpected branch tag is returned, an unhandled route leaves the run in an undefined terminal state without advancing downstream nodes.

```python
from google.adk.workflow import DEFAULT_ROUTE

edges = [
    (
        policy_check,
        {
            "OK": scripter,
            "BLOCK": quarantine,
            DEFAULT_ROUTE: quarantine,  # Fail safe to quarantine
        },
    ),
    (quarantine, scripter),
]
```

> Source: Google ADK Codelab: Agentic Workflow with ADK (Step 5)

---

## State & Memory Architecture

### DO: Integrate agent-scoped memory via lifecycle callbacks, NOT graph nodes

User preference extraction, historical session recall, and taste personalization belong to the individual agent's cognitive context, not the macro workflow dataflow.

Inserting memory read/write operations as pipeline nodes clutters the graph topology with extraneous stages. Instead:
- Use `before_model_callback` to query long-term memory (e.g., Vertex AI Agent Engine Memory Bank) and inject historical preferences directly into the outgoing `LlmRequest`.
- Use `after_agent_callback` to inspect the completed turn and trigger asynchronous consolidation (`memories.generate`) without blocking downstream nodes.

```python
propose_directions = Agent(
    name="propose_directions",
    model=config.MODEL,
    instruction=PROPOSE_INSTRUCTION,
    output_schema=Directions,
    before_model_callback=recall_creator_taste,  # Enrich prompt context
)

scripter = Agent(
    name="scripter",
    model=config.MODEL,
    instruction=SCRIPT_INSTRUCTION,
    output_schema=Script,
    after_agent_callback=remember_creator_choice,  # Persist decision
)
```

> Source: Google ADK Codelab: Agentic Workflow with ADK (Step 6)

### DO: Separate User Memory (callbacks) from Shared Document Grounding (graph nodes)

Maintain a strict boundary between personalized user memory and enterprise knowledge bases:

| Dimension | User Memory (Memory Bank) | Document Retrieval (RAG Engine) |
|:----------|:--------------------------|:--------------------------------|
| **Scope** | Scoped to individual `(app_name, user_id)` | Scoped to shared corpus across all users |
| **Data Lifecycle** | Real-time extraction, semantic deduplication, evolving taste | Document chunking, vector embeddings, static knowledge |
| **Integration** | Agent lifecycle callbacks (`before_model`, `after_agent`) | Dedicated function node in parallel fan-out (`JoinNode`) |

Grounding retrieval that feeds multiple downstream agents belongs in the parallel reader fan-out alongside trend scanners and backlog readers, converging at a synchronization `JoinNode`.

> Source: Google ADK Codelab: Agentic Workflow with ADK (Steps 6 & 7)

### DO: Leverage automatic parameter binding for session state

Do not thread bloated dictionaries through every node signature. In ADK workflows:
- Nodes yield state deltas via `yield Event(state={"key": value})`.
- Downstream function nodes receive required keys automatically by declaring matching argument names in their signature (e.g., `def node_fn(node_input, candidates: list = []):`).
- Keys prefixed with `user:` (e.g., `user:prefs`) automatically persist across multiple sessions for the same user.

> Source: Google ADK Codelab: Agentic Workflow with ADK (Step 5)

---

## Asynchronous Execution & Production

### DO: Suspend multi-minute external operations using `LongRunningFunctionTool`

Operations requiring minutes to complete (e.g., video rendering with Veo, high-compute batch jobs, physical builds) must never block the workflow thread or execute in-line polling loops.

Wrap slow operations in `LongRunningFunctionTool`:
1. The tool function initiates the job and immediately returns `{ "status": "pending", "call_id": ..., "operation": ... }`.
2. ADK intercepts the `"pending"` status, records the open call receipt in session storage, and suspends the workflow.
3. The process exits cleanly, releasing HTTP sockets and compute resources.
4. An external background daemon or webhook receiver polls the provider and delivers a matching `FunctionResponse` to resume execution.

```python
from google.adk.tools import LongRunningFunctionTool

def render_submit(prompt: str) -> dict:
    """Submit one render. Returns immediately with a pending receipt."""
    receipt = videogen.start(prompt)
    return {
        "status": "pending",
        "operation": receipt["operation"],
        "prompt": receipt["prompt"],
    }

render_desk = Agent(
    name="render_desk",
    model=config.MODEL,
    tools=[LongRunningFunctionTool(render_submit)],
)
```

> Source: Google ADK Codelab: Agentic Workflow with ADK (Step 8)

### DO: Apply the Universal Resumption Pattern across human and tool suspensions

Human decision gates (`yield RequestInput`) and long-running tools (`LongRunningFunctionTool`) share the *identical* underlying resumption mechanism in ADK:

```python
from google.genai.types import FunctionResponse, Part

# Both human input and long-running tools resume via a FunctionResponse part
resumption_part = Part(
    function_response=FunctionResponse(
        id=call_id,       # The interrupt_id or tool call_id recorded at suspension
        name=name,         # The function or gate name
        response=response, # The structured payload or external result
    )
)

async for event in runner.run_async(user_id=user, session_id=sid, new_message=resumption_part):
    process_event(event)
```

Completed upstream nodes do not re-execute; execution resumes immediately at the suspended barrier.

> Source: Google ADK Codelab: Agentic Workflow with ADK (Steps 8 & 9)

### DO: Use `mode="task"` with typed `finish_task` for autonomous remediation loops

When an agent must perform iterative self-correction with tools (e.g., fixing policy violations, linting code, resolving dependency conflicts), do not use open-ended multi-turn `chat` mode.

Use `mode="task"`:
- The agent iterates over provided tools autonomously.
- ADK automatically synthesizes a `finish_task` tool derived from `output_schema`.
- Execution halts only when the agent satisfies the schema and invokes `finish_task`, emitting a guaranteed typed payload to downstream graph nodes.

```python
quarantine = Agent(
    name="quarantine",
    model=config.MODEL,
    instruction=QUARANTINE_INSTRUCTION,
    mode="task",
    tools=[find_policy_hits, suggest_replacement],
    output_schema=CleanedDirection,  # finish_task takes CleanedDirection arguments
)
```

> Source: Google ADK Codelab: Agentic Workflow with ADK (Step 5)
