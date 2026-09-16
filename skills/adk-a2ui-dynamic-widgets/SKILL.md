---
name: adk-a2ui-dynamic-widgets
description: >
  Construct declarative A2UI interactive widget messages from Google ADK agents and
  synchronize client-side user action callbacks with the backend session journal.
source: https://codelabs.developers.google.com/adk-gemini-a2ui?hl=en
---

# ADK A2UI Declarative Interface & Dynamic Widgets

Use this skill when an ADK agent must present rich interactive UI elements (cards, forms,
carousels, confirmation buttons) to web or mobile clients, allowing users to interact directly
through UI widgets while maintaining synchronized session state.

## When to Use

- Replacing verbose multi-paragraph markdown outputs with compact, interactive visual cards
- Presenting multi-option selection grids where each option dispatches a typed action
- Collecting structured user inputs through dynamic forms rather than conversational slot-filling
- Bi-directionally synchronizing client UI widget states with the ADK session journal

---

## Core Architecture

A2UI (Agent-to-User Interface) establishes a declarative boundary between the reasoning
model and the frontend presentation layer:

```
[ADK Agent]
     │
     ├── Generates Structured Pydantic A2UI Component (Card, Form, ButtonGrid)
     │
     ▼ (Streamed via Server-Sent Events - SSE)
[React / Web Frontend]
     │
     ├── Renders Native Web Component matching A2UI declaration
     │
     ├── User clicks action button: [Approve Candidate #2]
     │
     ▼ (Dispatches POST /api/run/action with action_id & payload)
[ADK Runner Endpoint]
     │
     ├── Submits resumption Part(function_response=FunctionResponse(...))
     └── Resumes Workflow execution at next graph node
```

---

## Step-by-Step Procedure

### 1. Define A2UI Component Pydantic Models

Declare the schema for interactive UI components that your agent is authorized to emit:

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class ActionButton(BaseModel):
    label: str
    action_id: str
    style: Literal["primary", "secondary", "danger"] = "primary"
    payload: dict = Field(default_factory=dict)

class ProductCard(BaseModel):
    component_type: Literal["product_card"] = "product_card"
    title: str
    subtitle: Optional[str] = None
    image_url: Optional[str] = None
    price: str
    actions: List[ActionButton]

class A2UIMessage(BaseModel):
    text_summary: str
    widgets: List[ProductCard]
```

### 2. Configure the Agent Node with the A2UI Output Schema

Equip the agent with instructions and the `output_schema`:

```python
from google.adk import Agent

A2UI_INSTRUCTION = """
You are a retail shopping assistant. When presenting product recommendations,
do not format them as bulleted text. Always emit an A2UIMessage containing
ProductCard widgets for each recommended item, with an 'Add to Cart' action button.
"""

catalog_agent = Agent(
    name="catalog_agent",
    model=config.MODEL,
    instruction=A2UI_INSTRUCTION,
    output_schema=A2UIMessage,
)
```

### 3. Expose the Action Dispatch API Route

In your FastAPI or web server hosting the ADK `Runner`, create an action callback route:

```python
from fastapi import FastAPI, HTTPException
from google.genai.types import Part, FunctionResponse

app = FastAPI()

@app.post("/api/session/{session_id}/action")
async def dispatch_a2ui_action(session_id: str, action: ActionButton):
    """Receive client button clicks and resume the agent session."""
    # Format client action as a resumption FunctionResponse
    resumption_part = Part(
        function_response=FunctionResponse(
            id=action.action_id,
            name=action.action_id,
            response=action.payload,
        )
    )

    # Resume the workflow run asynchronously
    events = []
    async for event in runner.run_async(
        user_id=CURRENT_USER,
        session_id=session_id,
        new_message=resumption_part
    ):
        events.append(event)

    return {"status": "resumed", "events": events}
```

### 4. Render A2UI Components on the Client (React)

Map the emitted A2UI JSON to native frontend components:

```tsx
import React from "react";

interface ProductCardProps {
  data: {
    title: string;
    subtitle?: string;
    image_url?: string;
    price: string;
    actions: Array<{ label: string; action_id: string; payload: any }>;
  };
  onAction: (actionId: string, payload: any) => void;
}

export const A2UIProductCard: React.FC<ProductCardProps> = ({ data, onAction }) => {
  return (
    <div className="border rounded-lg p-4 shadow-sm bg-white">
      {data.image_url && <img src={data.image_url} alt={data.title} className="h-40 w-full object-cover rounded" />}
      <h3 className="font-bold text-lg mt-2">{data.title}</h3>
      {data.subtitle && <p className="text-gray-500 text-sm">{data.subtitle}</p>}
      <div className="font-semibold text-blue-600 mt-1">{data.price}</div>
      <div className="mt-3 flex gap-2">
        {data.actions.map((act) => (
          <button
            key={act.action_id}
            onClick={() => onAction(act.action_id, act.payload)}
            className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            {act.label}
          </button>
        ))}
      </div>
    </div>
  );
};
```

---

## Environment & Implementation Caveats

- **Fallback Text Requirement**: Always include a `text_summary` field in your top-level A2UI message schema. If the agent communicates over SMS, headless CLI, or legacy clients without A2UI rendering capabilities, the client can display the text summary without breaking.
- **Action Expiration**: When the agent workflow advances past a decision point, the frontend must disable action buttons on previously rendered widgets to prevent users from submitting conflicting, out-of-order actions.
- **Streaming JSON Delimiters**: When streaming responses over SSE, buffer the partial JSON until a complete widget block is validated before attempting to render the component.

---

## Edge Cases & Failure Modes

1. **Orphaned Action Clicks**: If a user clicks an action button on a session that has already completed, the runner returns an error or creates an unintended turn. Include the expected `turn_id` or `interrupt_id` in the action payload and reject stale actions.
2. **Invalid Image URIs**: Models can fabricate placeholder image URLs. Enforce validation in the Pydantic schema or supply pre-approved asset URLs through tool outputs.
