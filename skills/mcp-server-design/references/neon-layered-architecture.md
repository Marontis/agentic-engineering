# Neon's Layered MCP Architecture — Annotated Reference

## Overview

Neon's MCP server stack is the canonical example of the patterns described in
the parent skill. It separates three concerns into three packages, each
independently consumable.

## The Three Layers

### Layer 1: `@neon/sdk` — Typed API Client

The SDK is a standard typed HTTP client over Neon's REST API. It knows
nothing about tools, MCP, or agents. It provides:

- Every Neon API endpoint as a typed method
- Response types matching the OpenAPI spec
- Pagination helpers (`.all()` for auto-pagination)
- Authentication via API key or OAuth token (supports refresh functions)

**Consumers**: Backend services, CI scripts, CLIs, the tools package.

### Layer 2: `@neon/tools` — Tool Descriptors + Execute

The tools package sits between the SDK and any AI framework. It:

1. **Selects** SDK methods via selector paths (`"projects.list"`,
   `"branches.createAndConnect"`)
2. **Wraps** each in a tool descriptor:
   - Zod 4 `inputSchema` (snake_case at the boundary)
   - Published `id` via `publishedId()` — `"projects.list"` → `"list_projects"`
   - Title, description (first sentence of OpenAPI description)
   - Safety annotations (`destructiveHint`, `readOnlyHint`, `idempotentHint`)
   - Stability metadata
3. **Provides** `execute()` with strict input validation and typed output

**Key API**:
```typescript
import { createNeonTools, publishedId } from "@neon/tools";

publishedId("projects.list");                // "list_projects"
publishedId("postgres.roles.resetPassword"); // "reset_password_postgres_roles"

const tools = createNeonTools({
  apiKey,
  tools: [
    "projects.list",
    "projects.createAndConnect",
    "branches.createAndConnect",
    "branches.resetFromParent",
    "branches.compareSchema",
  ],
});
```

**Workflow tools** are where the SDK methods compose:
- `projects.createAndConnect` = create project + provision compute + return
  connection string
- `branches.createAndConnect` = create branch + attach compute + return
  connection string
- `branches.resetFromParent` = reset branch + preserve old state under a
  named snapshot

**Write tools** run with `waitForReadiness: true` — when a mutation returns
an `operations` array, the tool polls until those operations complete
(default 5-minute timeout, configurable via `wait.timeoutMs`).

**Consumers**: MCP server, Mastra, Eve, any AI framework.

### Layer 3: `@neon/mcp-server-neon` — MCP Protocol Adapter

The MCP server is a thin protocol adapter. It:

1. Reads `@neon/tools` descriptors
2. Registers them as MCP tools with the protocol SDK
3. Supports **category scoping** via URL query parameters:
   ```
   ?category=projects&category=branches&category=querying
   ```
4. Handles OAuth (scopes: `read`, `write`) and API key auth
5. Supports read-only mode via scope selection or `?readonly=true`

The server adds no business logic — it translates the tools package into
the MCP wire protocol. Framework adapters for Mastra and Eve do the same
for their respective protocols.

## The `publishedId()` Convention

Tool naming follows a deterministic convention:

| SDK Selector | Published ID |
|---|---|
| `projects.list` | `list_projects` |
| `projects.createAndConnect` | `create_and_connect_projects` |
| `branches.create` | `create_branches` |
| `postgres.roles.resetPassword` | `reset_password_postgres_roles` |
| `postgres.connectionString` | `connection_string_postgres` |

Rule: last path segment → resource, in snake_case. This keeps tool names
agent-friendly (short, readable, no dots).

## Category System

Categories group tools for URL-based filtering:

| Category | Example Tools |
|---|---|
| `projects` | list, create, delete, get |
| `branches` | list, create, delete, compareSchema |
| `endpoints` | list, create, delete, start, suspend |
| `querying` | execute SQL, explain |
| `schema` | describe tables, list schemas |

The server serves all categories by default. The URL controls what's visible:
```
# All tools
https://mcp.neon.tech/mcp

# Only projects and querying (~10 tools instead of 50+)
https://mcp.neon.tech/mcp?category=projects&category=querying
```

## Design Decisions Worth Noting

1. **API key as Bearer credential** — supports both static API keys and
   short-lived OAuth tokens via a refresh function

2. **Paginated lists call `.all()`** — tool consumers don't see cursors;
   the tool handles pagination internally

3. **Unknown fields rejected** — `execute()` uses strict Zod validation,
   failing on extra properties

4. **Errors thrown, not wrapped** — Neon SDK errors propagate as typed
   exceptions, not generic `isError: true` results

5. **Categories in URL, not in tool definitions** — the server decides
   grouping, not the individual tool descriptors. This keeps the tools
   package framework-agnostic.

## Mapping to Attorn

| Neon Pattern | Attorn Equivalent |
|---|---|
| Category URL filtering | Grant-based `tools/list` filtering (more secure) |
| Published tool IDs | Namespace-qualified names (`upstream.tool`) |
| OAuth scoping | OBO identity chain + per-grant tool sets |
| Read-only mode | Read-only grant (no write tools in scope) |
| `waitForReadiness` | Not applicable (Attorn is a gateway, not a tool) |
