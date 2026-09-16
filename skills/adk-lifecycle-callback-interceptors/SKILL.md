---
name: adk-lifecycle-callback-interceptors
description: >
  Implement non-invasive context injection, policy guardrails, and persistent memory
  updates in Google Agent Development Kit (ADK) using lifecycle callbacks (before/after agent,
  model, and tool) without polluting workflow graph topologies.
source: https://codelabs.developers.google.com/codelabs/vibe-studio-lab/instructions
---

# ADK Lifecycle Callback Interceptors

Use this skill when an ADK agent requires dynamic context enrichment (e.g., user preferences
from a Memory Bank), deterministic input/output validation, telemetry, or long-term observation
logging without adding cluttering operational nodes to the macro workflow graph.

## When to Use

- Injecting long-term user taste, past session facts, or channel rules into an agent turn
- Extracting and persisting facts or user preferences after an agent turn completes
- Intercepting model inference calls to enforce guardrails or return cached responses
- Inspecting, modifying, or blocking tool arguments and tool outputs at runtime
- Keeping workflow graph DAGs focused strictly on business logic and data stages

---

## The 3 Callback Pairs

ADK provides three lifecycle interceptor pairs. Returning `None` continues normal execution;
returning a replacement object intercepts or overrides the operation:

| Callback Pair | Invocation Point | Context Received | Return Behavior |
|:---|:---|:---|:---|
| **`before_agent_callback`<br>`after_agent_callback`** | Surrounds the complete agent turn | `CallbackContext` (session, state, invocation) | Returning `Content` overrides the agent reply; `None` proceeds normally. |
| **`before_model_callback`<br>`after_model_callback`** | Surrounds each individual LLM inference call | `LlmRequest` / `LlmResponse` | Returning `LlmResponse` skips the model call; `None` proceeds to inference. |
| **`before_tool_callback`<br>`after_tool_callback`** | Surrounds each local or remote tool execution | Tool definition, arguments, result | Returning a dict overrides the tool output; `None` executes normally. |

```
Workflow Node Entry
       │
       ▼
[before_agent_callback] ──(Content returned?)──► Short-circuit Agent Turn
       │ (None)
       ▼
 [before_model_callback] ──(LlmResponse returned?)──► Skip LLM inference
       │ (None)
       ▼
   LLM Generates Tool Call
       │
       ▼
  [before_tool_callback] ──(Dict returned?)──► Override Tool Result
       │ (None)
       ▼
     Execute Local Tool
       │
       ▼
  [after_tool_callback] ──(Dict returned?)──► Override Tool Result
       │ (None)
       ▼
   LLM Synthesizes Response
       │
       ▼
 [after_model_callback] ──(LlmResponse returned?)──► Override Model Output
       │ (None)
       ▼
[after_agent_callback] ──(Trigger background Memory Bank update)
       │
       ▼
Workflow Node Exit
```

---

## Step-by-Step Procedure

### 1. Inbound Context Injection via `before_model_callback`

To enrich an agent's reasoning context with user preferences or standing policies without polluting prompt templates:

1. Define a callback function accepting `(callback_context, llm_request)`.
2. Retrieve relevant memory facts (e.g. from Vertex AI Memory Bank or SQLite).
3. Append formatted memory directives to `llm_request.contents`.
4. Return `None` to allow the model call to proceed with the enriched context.

```python
def recall_taste(context, request):
    """Fetch creator taste history and channel constraints before model runs."""
    user_id = context.session.get("user_id", "default_user")
    memories = memory_bank.retrieve(scope={"app_name": "vibestudio", "user_id": user_id})

    if memories:
        memory_prompt = (
            "\n[STANDING PREFERENCES & CHANNEL RULES]\n"
            + "\n".join(f"- {m['text']}" for m in memories)
            + "\nTreat channel rules as strict constraints and align proposals with taste."
        )
        # Prepend or append context to request contents
        request.contents[-1].parts.append(memory_prompt)

    return None  # Continue with inference
```

### 2. Outbound Observation Extraction via `after_agent_callback`

To capture user decisions and consolidate long-term memory across sessions:

1. Define a callback accepting `(callback_context)`.
2. Inspect `callback_context.state` to read what the user or agent decided during the turn.
3. Call the asynchronous memory consolidation service (`memories.generate`) with the observation.
4. Return `None` so the agent's output is delivered downstream without delay.

```python
def remember_pick(context):
    """Extract creator selection from session state and consolidate to Memory Bank."""
    chosen_title = context.state.get("direction")
    hook = context.state.get("hook")

    if chosen_title:
        observation = f"Creator selected concept '{chosen_title}' with hook '{hook}'."
        # Fire-and-forget memory extraction & semantic deduplication
        memory_bank.generate(
            text=observation,
            scope={"app_name": "vibestudio", "user_id": context.session.get("user_id")},
        )

    return None  # Do not alter agent response
```

### 3. Attach Callbacks to Agent Instances

Pass the callback functions directly into the `Agent` declaration:

```python
from google.adk import Agent

propose_directions = Agent(
    name="propose_directions",
    model=config.MODEL,
    instruction=PROPOSE_INSTRUCTION,
    output_schema=Directions,
    before_model_callback=recall_taste,    # Context enrichment
)

scripter = Agent(
    name="scripter",
    model=config.MODEL,
    instruction=SCRIPT_INSTRUCTION,
    output_schema=Script,
    after_agent_callback=remember_pick,     # Memory extraction
)
```

---

## Architectural Decision Matrix: Callbacks vs Graph Nodes

A common anti-pattern is turning every operation into a graph node. Follow this rule:

| Mechanism | Use For | Do NOT Use For |
|:---|:---|:---|
| **Graph Node** | Shared data dependencies (e.g., RAG corpus search in parallel fan-out), branching logic, user approval gates. | Agent-specific context loading, logging, post-turn memory updates. |
| **Lifecycle Callback** | Agent-specific context injection, user memory recall, post-turn consolidation, telemetry, safety filters. | Orchestrating parallel work, multi-branch routing, synchronization barriers. |
| **Tool** | On-demand retrieval requested autonomously by the model based on prompt ambiguity. | Predictable, mandatory context that the model must always have before reasoning. |

---

## Environment & Implementation Caveats

- **Context Mutation In-Place**: When modifying `LlmRequest` in `before_model_callback`, mutate the existing data structure or append parts; do not overwrite `request.contents` with incompatible types.
- **Error Handling**: Always wrap external memory service calls (Memory Bank, vector DBs) in `try/except` blocks inside callbacks. A failure in long-term memory retrieval should degrade gracefully to standard prompts rather than crashing the workflow run.
- **Async Safety**: If using async memory APIs, ensure your callback signature aligns with ADK's sync/async callback dispatch expectations.
