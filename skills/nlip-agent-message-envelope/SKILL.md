---
name: nlip-agent-message-envelope
description: >
  Construct, parse, validate, and bridge standardized semantic message envelopes
  for multi-agent communication across heterogeneous transports (HTTP, WebSocket,
  AMQP), context stores, and tool gateways. Bridges MCP and A2A architectures.
  Derived from the Ecma standard and Xing et al. (arXiv:2609.04135).
---

# NLIP Semantic Message Envelope & Gateway Integration

Use this skill when designing or deploying inter-agent communication, agent gateways,
or multi-agent orchestration fabrics across heterogeneous frameworks (e.g., LangChain,
Semantic Kernel, AutoGen, custom runtimes) and transports.

## When to Use

- Agents running in different runtimes or programming languages need to communicate
  without custom ad-hoc JSON schemas for every interaction.
- You need a standard transport-agnostic message model spanning REST/HTTP (unary RPC),
  WebSocket (streaming/bidirectional dialogue), or AMQP (asynchronous task queues).
- Bridging tool execution standards like Model Context Protocol (MCP) and agent delegation
  frameworks (A2A) under a unified application-layer envelope.
- Enforcing verifiable sender identity, conversation continuity, context references,
  and security-by-design boundaries across organizational agent gateways.

## Core Architecture: The NLIP Standard

The Natural Language Interaction Protocol (NLIP, Ecma International standard;
Xing et al., arXiv:2609.04135) addresses the fragmentation of agent frameworks by
establishing a lightweight, standards-based application-layer semantic envelope.

### Protocol Layering & Taxonomy

```
+-------------------------------------------------------------------+
|                        Application Logic                          |
|             (Intent Resolution, Planning, Tool Execution)         |
+-------------------------------------------------------------------+
|                     NLIP Semantic Layer                           |
|  - Envelope (header, routing, conversation state, trace IDs)       |
|  - Semantic Intents (query, inform, delegate, negotiate, error)   |
|  - Context References (URIs to state, memory vectors, tool specs) |
+-------------------------------------------------------------------+
|                      Convergence Gateways                         |
|      - MCP Bridge (Tool schemas)  |  - A2A Bridge (Delegation)    |
+-------------------------------------------------------------------+
|                      Transport Bindings                           |
|       HTTP / HTTPS       |     WebSocket     |        AMQP        |
|  (Stateless Request-Resp)| (Bidirectional/SS)| (Asynchronous Bus) |
+-------------------------------------------------------------------+
```

NLIP separates **semantic intent** (what the message means) from **transport mechanics**
(how bits travel) and **execution details** (how tools are run), preventing agent protocols
from becoming tightly coupled to specific networking stacks.

---

## Procedure

### Step 1: Define the Canonical Semantic Envelope

Every inter-agent message MUST conform to the canonical NLIP envelope schema. Do not
invent custom message envelopes.

```json
{
  "$schema": "https://ecma-international.org/standards/nlip/v1.0/schema.json",
  "nlip_version": "1.0",
  "message_id": "msg:f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
  "conversation_id": "conv:35829d69-234d-4c23-a978-381dbb349197",
  "in_reply_to": "msg:7b2c3d4e-5f6a-7b8c-9d0e-1f2a3b4c5d6e",
  "timestamp": "2026-09-06T11:52:12Z",
  "sender": {
    "agent_id": "agent:planner:v2",
    "role": "planner",
    "domain": "corp.internal"
  },
  "recipient": {
    "agent_id": "agent:executor:code",
    "role": "code_executor",
    "domain": "corp.internal"
  },
  "intent": "delegate",
  "payload": {
    "instruction": "Refactor token budget accounting in memory manager",
    "expected_output_type": "git_patch"
  },
  "context_references": [
    {
      "type": "memory_uri",
      "uri": "praxis://vectors/doc-4819?chunk=12",
      "digest": "sha256:8db011c71573..."
    },
    {
      "type": "workspace_file",
      "uri": "file:///src/memory/budget.py#L40-L85"
    }
  ],
  "security": {
    "auth_token": "Bearer <jwt-token>",
    "capability_claims": ["sandbox:exec", "fs:read:/src"],
    "signature": "<required: detached signature over the canonicalized envelope>"
  },
  "trace": {
    "parent_span_id": "span:001",
    "trace_id": "trace:a1b2c3d4"
  }
}
```

Treat `sender` and `security.capability_claims` as **self-declared hints**, never as
authority. The receiver binds sender identity from the transport (mTLS client
certificate, workload identity, or the key that verifies `signature`), and rejects the
message if the envelope's `sender.agent_id` disagrees with that bound identity.
`capability_claims` may help routing and logging; authorization comes from the
server-side permission declaration (Step 5). `signature` is mandatory, not optional.

### Step 2: Select Transport Binding

Map message interaction semantics to the appropriate transport protocol:

1. **HTTP/HTTPS (Stateless Unary Invocations)**:
   - Use for one-off tool queries, simple QA lookups, or health checks.
   - Header: `Content-Type: application/nlip+json`.
   - Map `conversation_id` to HTTP header `X-NLIP-Conversation-ID` for gateway routing.
   - Idempotent operations must use `PUT` or `POST` with deduplication keys.

2. **WebSocket (Interactive Streaming & Multi-Turn Dialogue)**:
   - Use for streaming LLM tokens, real-time collaboration, and multi-turn negotiation.
   - Framing: Send NLIP envelope as the initial handshake and framing envelope.
   - Streaming chunks use intent `"stream_chunk"` with reference to `message_id`.

3. **AMQP / Message Queue (Asynchronous Agent Pipelines)**:
   - Use for distributed agent pools, fan-out subagents, and long-horizon tasks.
   - Routing key: `nlip.<domain>.<sender_role>.<recipient_role>.<intent>`.
   - Leverage native message persistence, retries, and dead-letter queues without
     modifying the payload envelope.

### Step 3: Implement Gateway Context Referencing (Zero-Copy Transfer)

Avoid packing massive context blobs (multi-megabyte file trees or vector documents)
directly into the `payload`. Use NLIP **Context References**:

1. **Declare Reference URIs**: Use deterministic scheme URIs (`praxis://`, `repo://`,
   `file://`, `artifact://`).
2. **Attach Cryptographic Digests**: Include `digest: sha256:...` so the recipient
   verifies content integrity without trust assumptions.
3. **Lazy Resolution**: The receiving agent fetches referenced resources on-demand
   only if required for execution.

### Step 4: Bridge MCP and A2A Protocols

NLIP serves as an overarching application-layer envelope that coordinates both
Model Context Protocol (MCP) and Agent-to-Agent (A2A) topologies:

- **MCP Integration (Tool-Level Bridging)**:
  - When an agent requests tool execution, encapsulate the MCP JSON-RPC call in
    the NLIP payload with intent `"tool_call"`.
  - The gateway strips or passes the envelope, authorizes the transport-bound caller
    identity against its own server-side permission declaration (not against
    `security.capability_claims`), and invokes the targeted MCP server.
- **A2A Integration (Agent-Level Delegation)**:
  - For multi-agent subtasks, wrap task contracts in NLIP with intent `"delegate"`
    or `"negotiate"`.
  - Maintain conversation tree lineage across subagent spawns via `in_reply_to`
    and `conversation_id`.

```python
def wrap_mcp_as_nlip(tool_name: str, arguments: dict, sender_id: str, recipient_id: str, conv_id: str) -> dict:
    """Wraps an MCP tool invocation in an NLIP semantic envelope."""
    import uuid, datetime
    return {
        "nlip_version": "1.0",
        "message_id": f"msg:{uuid.uuid4()}",
        "conversation_id": conv_id,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "sender": {"agent_id": sender_id},
        "recipient": {"agent_id": recipient_id},
        "intent": "tool_call",
        "payload": {
            "jsonrpc": "2.0",
            "method": f"tools/call",
            "params": {"name": tool_name, "arguments": arguments}
        },
        "security": {"capability_claims": [f"tool:{tool_name}"]}  # hint only
    }
    # Sign the canonicalized envelope before sending; the gateway rejects unsigned
    # envelopes and authorizes from its own permission declaration.
```

### Step 5: Enforce Security-by-Design Validation Gate

Before acting on any incoming message:

1. **Validate Envelope Syntax**: Assert required fields (`nlip_version`, `message_id`,
   `sender`, `intent`, `payload`, `security.signature`).
2. **Verify Signature and Bind Identity**: Verify `security.signature` over the
   canonicalized envelope with the sender's registered key, and bind the sender
   identity from the transport layer (mTLS / workload identity / verifying key), not
   from the `sender` field. **Quarantine** unsigned messages, messages whose signature
   fails, and messages whose declared sender differs from the bound identity: do not
   pass them to any agent's context; log them for review.
3. **Authorize from a Server-Side Declaration**: Look up the bound identity in a
   permission declaration held by the gateway/server (the same declaration that drives
   tool visibility) and check the invoked action and its parameters against it. Never
   authorize from `security.capability_claims`. Reject unauthorized requests with
   intent `"error"` and code `403`.
4. **Verify Context Access**: Check that any `context_references` point to authorized
   resource paths within the bound caller's permissions.
5. **Sanitize Cross-Domain Payloads**: Signing does not stop injection carried in tool
   outputs. Also run boundary sanitization on payloads from external or lower-trust
   domains, and keep their instructions out of system prompts.

In one 6-agent pipeline, signing with quarantine cut inter-agent injection from 31% to
2.8% but left indirect injection at 43%; sanitization did the reverse (43% to 9.5%
indirect, 31% inter-agent unchanged). Fixed, non-adaptive payloads (arXiv:2609.22949).
See `rules/multi-agent-coordination.md` — "DO: Sign inter-agent messages and quarantine
unsigned ones, in addition to boundary sanitization"; `rules/agent-sandbox-safety.md` —
"DON'T: Let agents self-declare their identity" and "DON'T: Treat tool hiding,
specialist prompts or roster delegation as access control".

---

## Verification & Self-Check

- [ ] Does every inter-agent message include `conversation_id` and `in_reply_to` for
      traceable dialogue trees?
- [ ] Are large files or retrieved chunks passed via URI references with SHA-256 digests
      rather than embedded directly in payload strings?
- [ ] Is every message signed, with unsigned or mismatched-sender messages quarantined?
- [ ] Is sender identity bound at the transport layer rather than read from the envelope?
- [ ] Does the gateway authorize from its own server-side permission declaration, never
      from sender-supplied `capability_claims`?
- [ ] Is transport binding cleanly abstracted from agent decision logic?
