# ADK A2UI Declarative Interface Specification Template

> Fill in this template when designing rich, interactive frontend experiences
> for Google ADK agents using the Agent-to-User Interface (A2UI) declarative protocol.

---

## 1. User Experience & Widget Scope

### What interactive capabilities must the agent render?

- [ ] **Structured Selection Cards**: Products, recommendations, visual previews
- [ ] **Dynamic Multi-Field Forms**: Intake, scheduling, filtered searches
- [ ] **Action Buttons & Confirmation Grids**: One-click approvals, cancellations
- [ ] **Media Carousels & Galleries**: Images, video clips, document cards
- [ ] **Progress Indicators & Steppers**: Multi-stage workflow progression

---

## 2. A2UI Message Schema & Declarative Payloads

The agent emits typed JSON payloads matching the A2UI component schema rather than raw markdown:

```json
{
  "type": "a2ui_component",
  "component": "Card",
  "props": {
    "title": "Selected Video Concept",
    "subtitle": "Midnight Laundry Robot",
    "image_url": "https://storage.googleapis.com/assets/robot.png",
    "metadata": {
      "genre": "Fantasy",
      "duration": "15s"
    }
  },
  "actions": [
    {
      "label": "Approve Concept",
      "action_id": "approve_concept",
      "style": "primary",
      "payload": {"choice": "robot_midnight"}
    },
    {
      "label": "Regenerate",
      "action_id": "reroll_concept",
      "style": "secondary"
    }
  ]
}
```

- [ ] Component schema registered in Pydantic output schemas
- [ ] Visual properties strictly separated from actionable callback payloads
- [ ] All actionable components include unique `action_id` identifiers

---

## 3. Client-Side Rendering & Action Dispatch

### How does the frontend consume A2UI messages?

- [ ] **React / Web Component Renderer**: Custom widget library mapping `a2ui_component` types to UI elements.
- [ ] **Server-Sent Events (SSE) Stream**: Streaming chunks display text immediately, mounting A2UI widgets when the component block finalizes.
- [ ] **Fallback Plain-Text Renderer**: Renders markdown equivalent for non-rich chat channels.

### Bidirectional State Synchronization:

```
┌───────────────┐                             ┌────────────────┐
│ React Client  │                             │  ADK Backend   │
└───────┬───────┘                             └───────┬────────┘
        │ 1. User clicks "Approve Concept"            │
        ├────────────────────────────────────────────►│
        │ POST /api/run/{id}/action                   │
        │ {"action_id": "approve_concept", ...}       │
        │                                             │ 2. Dispatches Part(
        │                                             │    function_response=...)
        │                                             │ 3. Journal updates state
        │ 4. SSE Stream emits new A2UI Component      │
        │◄────────────────────────────────────────────┤
        ▼                                             ▼
```

- [ ] Client dispatches actions via typed API endpoint (`/api/action`)
- [ ] Action payload formats as a `FunctionResponse` or new user turn matching the expected interrupt schema
- [ ] Session journal records the action event for auditability

---

## 4. Error Handling & Accessibility

- [ ] **Graceful Component Degradation**: If an unknown component type is emitted, the frontend renders a fallback summary card.
- [ ] **Double-Click Debouncing**: Action buttons disable immediately upon click until the backend emits the next event.
- [ ] **Accessibility (a11y)**: Every visual component includes `alt_text` and ARIA labels.
