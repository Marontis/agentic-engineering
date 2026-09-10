---
name: mcp-server-design
description: >
  Best practices for designing MCP servers in the era of progressive tool
  discovery and programmatic tool calling (code mode). Covers workflow tools,
  outputSchema, category scoping, and the layered SDK → Tools → Server
  architecture. Reference implementation: Neon's MCP server stack.
---

# MCP Server Design Best Practices

## Why This Exists

Modern MCP clients — Claude Code, Codex, Cursor, Gemini — have adopted two
patterns that change what a well-designed MCP server looks like:

1. **Progressive Tool Discovery**: Clients no longer inject every tool
   definition into the model context upfront. They use a `search_tools`
   meta-tool and a 3-layer catalog → inspect → execute pattern, loading full
   schemas only for tools the model actually needs.

2. **Programmatic Tool Calling (Code Mode)**: Agents write scripts in a
   sandboxed environment that call tools via typed stubs. Only the final
   result returns to the model context, not every intermediate result.

These are **client-side** patterns. But they have direct consequences for how
servers should expose tools:

> **The server defines what tools exist; the client decides how to discover
> and execute them.**

## Anti-Patterns

### ❌ 1:1 API Endpoint → Tool Mapping

Don't create one MCP tool for every REST endpoint in your API. A Neon-scale
API has 100+ endpoints. Putting every one in `tools/list` means:

- **Context bloat**: 100+ tool definitions consume the majority of the
  context window before the model reads the user's message
- **Confused tool selection**: The model must choose between similar tools
  with subtle differences (`create_branch` vs `create_branch_with_compute`)
- **Unnecessary round-trips**: Multi-step operations require the model to
  chain tool calls, with full intermediate results flowing through context

### ❌ Tools Without Output Schemas

Without `outputSchema`, code-mode sandboxes cannot generate typed stubs.
The model must either use `any` or an LLM-based extraction step per call.

### ❌ Tools Without Safety Annotations

Destructive operations without safety annotations skip human-in-the-loop
gates. A `delete_project` tool without `{ destructive: true, idempotent:
false }` annotations lets an agent silently delete data.

## Design Patterns

### ✅ Workflow Tools

Bundle multi-step API sequences into single, outcome-oriented tools.

**Example: Neon's `createWithCompute`**

Instead of exposing three separate tools:
1. `create_branch` — creates a database branch
2. `attach_compute` — provisions a compute endpoint
3. `get_connection_string` — returns the connection URI

Neon bundles them into **one** tool: `branches.createAndConnect`

The agent calls once and gets back a connection string. Three API calls,
one tool, one round-trip through the model context.

**When to create a workflow tool:**
- The operation requires 2+ API calls that are almost always done together
- Intermediate results are infrastructure details the model doesn't need
- The combined operation has a clear, user-meaningful outcome

**When NOT to create a workflow tool:**
- The steps are independently useful and frequently called alone
- The user needs visibility into intermediate state
- The combination changes meaning based on context

### ✅ Always Provide `outputSchema`

Every tool should declare an `outputSchema`. This enables:

- **Code-mode typed stubs**: The client sandbox can generate
  `Promise<{ connectionUri: string }>` instead of `Promise<any>`
- **Client-side validation**: Clients can verify structured output
- **Progressive discovery**: Clients can show output types in tool search

```json
{
  "name": "create_branch",
  "outputSchema": {
    "type": "object",
    "properties": {
      "branchId": { "type": "string" },
      "connectionUri": { "type": "string" },
      "createdAt": { "type": "string", "format": "date-time" }
    },
    "required": ["branchId", "connectionUri", "createdAt"]
  }
}
```

### ✅ Category Scoping

Tag tools with categories so clients and gateways can filter the set.

**Example: Neon's URL-based categories**
```
https://mcp.neon.tech/mcp?category=projects&category=branches&category=querying
```

The server exposes all tools but the URL controls which are visible. A
client that only needs querying loads ~5 tools instead of 50+.

Categories should be:
- **Coarse-grained**: 5–10 categories, not one per tool
- **Domain-aligned**: `projects`, `branches`, `querying`, `schema`, `billing`
- **Documented**: Each category's tools listed in the server README

### ✅ Layered Architecture: SDK → Tools → Server

Neon's reference implementation separates three layers:

```
┌─────────────────────────────────────────┐
│   MCP Server (@neon/mcp-server-neon)    │  Protocol adapter
│   ↕ Uses tool descriptors as-is        │
├─────────────────────────────────────────┤
│   Tools Package (@neon/tools)           │  Tool descriptors + execute()
│   ↕ Selects from SDK methods           │  Zod schemas, safety annotations
├─────────────────────────────────────────┤
│   SDK (@neon/sdk)                       │  Typed API client
│   ↕ Raw HTTP                           │  Every endpoint, typed I/O
├─────────────────────────────────────────┤
│   REST API                              │
└─────────────────────────────────────────┘
```

**Why three layers?**

- **SDK** consumers (CI scripts, backend services) use it directly without
  tool overhead
- **Tools** consumers (any AI framework) get tool descriptors with schemas,
  safety annotations, descriptions — framework-agnostic
- **MCP Server** consumers get the full MCP protocol adapter

**Key design point**: The tools package uses *selectors* into the SDK:
```typescript
const tools = createNeonTools({
  apiKey,
  tools: [
    "projects.list",
    "projects.createAndConnect",   // workflow tool
    "branches.createAndConnect",   // workflow tool
    "branches.compareSchema",
  ],
});
```

The host cherry-picks capabilities. The tools package provides:
- Zod input schemas with snake_case at the boundary
- `execute()` with strict validation
- Published IDs (`projects.list` → `list_projects`) for MCP naming
- Safety annotations (destructive, read-only, idempotent)
- Category metadata for server-side filtering

### ✅ Safety Annotations

Mark every tool with MCP safety annotations:

```json
{
  "name": "delete_project",
  "annotations": {
    "title": "Delete Project",
    "readOnlyHint": false,
    "destructiveHint": true,
    "idempotentHint": true,
    "openWorldHint": false
  }
}
```

These annotations inform:
- **Human-in-the-loop gates**: Destructive tools trigger confirmation
- **Read-only mode**: Clients can filter to safe-only tools
- **Attorn policy**: The gateway's I9 invariant uses these for confirmation

## Server ↔ Client ↔ Gateway Contract

| Responsibility | Owner |
|---|---|
| Tool definitions, schemas, annotations | **Server** |
| `list_changed` notifications on tool changes | **Server** |
| `ttlMs` / `cacheScope` cache hints | **Server** |
| `outputSchema` for typed sandbox stubs | **Server** |
| Progressive discovery strategy | **Client** |
| Sandbox execution (code mode) | **Client** |
| Prompt caching policy | **Client** |
| Namespace qualification (`upstream.tool`) | **Gateway** (Attorn) |
| Policy-gated exposure (deny by default) | **Gateway** (Attorn) |
| Credential injection | **Gateway** (Attorn) |
| Audit trail | **Gateway** (Attorn) |

## Attorn-Specific Considerations

When designing an upstream MCP server that will sit behind Attorn:

1. **Tool names must not contain `.`** — Attorn uses `.` as the namespace
   separator (`upstream.tool`). A tool named `deploy.ship` from upstream
   `evil` would collide with upstream `deploy`'s tool `ship`. Attorn
   refuses the upstream at startup.

2. **Tool names ≤ 128 characters** — after qualification
   (`<upstream_name>.<tool_name>`), the combined name must fit.

3. **Workflow tools reduce gateway overhead** — each `tools/call` through
   Attorn requires a policy evaluation, credential injection, and audit
   record. Bundling 3 API calls into 1 workflow tool means 1 policy
   decision instead of 3.

4. **`outputSchema` enables proxy passthrough** — Attorn copies the full
   `mcp.Tool` struct (including `OutputSchema`) when mirroring tools to
   agents. Upstream `outputSchema` declarations are preserved end-to-end.

5. **Exposures are deny-by-default** — Attorn does not expose an upstream's
   prompts or resources unless the administrator's config explicitly lists
   them. Tools are exposed if the upstream offers them and the grant allows.

6. **Cache hints are floored** — Attorn's `floorResult()` restricts
   upstream cache hints to the most restrictive setting the protocol
   allows, preventing a malicious upstream from pinning a poisoned read.

## Checklist: Designing a New MCP Server

Use this before shipping a new MCP server or adding tools to an existing one:

- [ ] **Outcome-oriented**: Does every tool represent a user-meaningful
      outcome, not just a raw API call?
- [ ] **Workflow bundles**: Are multi-step operations that are almost always
      done together bundled into workflow tools?
- [ ] **`outputSchema` on every tool**: Can a code-mode sandbox generate
      typed stubs from every tool's output schema?
- [ ] **Categories**: Are tools tagged with coarse-grained categories for
      client/gateway filtering?
- [ ] **Safety annotations**: Do destructive tools carry `destructiveHint`,
      `readOnlyHint`, and `idempotentHint` annotations?
- [ ] **Naming**: Are tool names short, snake_case, and free of `.`?
      (For Attorn compatibility, and general MCP best practice)
- [ ] **SDK layer**: Is there a typed API client beneath the tools layer
      for programmatic (non-agent) consumers?
- [ ] **`list_changed` notifications**: Does the server emit
      `notifications/tools/list_changed` when tools are added or removed?
- [ ] **Cache hints**: Do list/read results include appropriate `ttlMs`
      and `cacheScope` hints?
- [ ] **Descriptions**: Is the first sentence of every tool description
      a clear, one-line summary usable in search results?

## References

- [MCP Client Best Practices (2026-07-28 spec)](https://modelcontextprotocol.io/docs/2026-07-28/develop/clients/client-best-practices)
- [Neon MCP Server](https://github.com/neondatabase/mcp-server-neon)
- [`@neon/tools` package](https://github.com/neondatabase/neon-pkgs/tree/main/packages/tools)
- [`@neon/sdk` package](https://github.com/neondatabase/neon-pkgs/tree/main/packages/sdk)
- [Video: Why MCP server design is changing](https://www.youtube.com/watch?v=BqRhBq-_kgE)
- [MCP Tool Specification](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)
