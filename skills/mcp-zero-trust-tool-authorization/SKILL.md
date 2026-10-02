---
name: mcp-zero-trust-tool-authorization
description: >
  Enforce per-tool authorization on an MCP server so a prompt-injected or
  jailbroken agent cannot reach tools its credential does not cover:
  normalize credentials from multiple headers into one principal, derive
  tool visibility (list_tools), invocation checks (call_tool), and optional
  pre-auth registry metadata from a single per-tool permission declaration,
  and bound the revocation window of cached token introspection.
  Derived from "Zero-Trust Authorization and Discovery for Enterprise MCP"
  (arXiv:2609.22573).
source: https://arxiv.org/abs/2609.22573
---

# Zero-Trust Tool Authorization for MCP Servers

Use this skill when you build or harden an HTTP-transport MCP server
that exposes privileged tools (deployments, cluster operations, database
writes) to LLM agents whose context may contain attacker-controlled
text.

## When to Use

- One MCP server must serve both human callers (SSO bearer token) and
  automation (service-account credential in a different header)
- Different callers should see and call different subsets of the same
  tool catalog (e.g. viewer vs admin roles)
- A control-plane registry needs to index many servers' tools without
  holding credentials for each
- You currently rely on the model refusing injected instructions, or on
  in-body permission checks, as the only barrier to privileged tools

## Core Insight

**Tool visibility is part of the agent's security boundary, and the
authorization decision must not depend on the model.** An agent can
only emit a call for a tool in the schema it was shown, so filtering
`list_tools` by caller permission removes the tool from its action
vocabulary. But filtering alone is bypassable: a leaked tool name can be
called directly. So visibility and invocation must be checked from the
same declaration.

**Evidence** (4 frontier LLMs, 60 hand-reviewed injection payloads ×
3 attempts, forbidden `restart_pod` tool, viewer-only credential):

- With the forbidden tool visible (baseline), models attempted it
  **152/720 (21.1%)** of the time; per model the range was **0/180 to
  90/180** (a 50-point cross-vendor spread), with role-play and direct
  injection the most effective classes. Refusal posture is a boundary
  that varies by vendor and shifts with each version bump.
- With visibility filtering, attempts fell to **0/720**. However, models
  still repeated the forbidden name in up to **94%** of cells
  (claude-opus-4-7 169/180), and a scripted direct `tools/call`
  **executed under filter-only**. It was blocked only when the
  invocation-time decorator was present.
- Production trace (7 days): the introspection cache served **96.1%** of
  verifications at 9.9 ms p50 vs 296 ms p50 on miss. The filter and
  decorator added latency on the order of run-to-run noise
  (list_tools p50 1.78 → 1.67 ms with auth+filter+decorator).

---

## Procedure

### 1. Declare Permissions Once, Per Tool

Attach one permission requirement to each tool, prompt, and resource at
registration, in disjunctive normal form: a list of AND-clauses, any of
which suffices, e.g. `[["admin","write"], ["superadmin"]]`. Store it as
a single attribute (e.g. `_required_permissions`) that every later layer
reads. There must be no second copy of the policy.

- Preserve the wrapped function's signature. Frameworks that build JSON
  schemas via `inspect.signature()` break if a decorator hides the
  parameter list.
- Decide the default for undeclared components explicitly. In the
  reference implementation, undeclared means any authenticated caller
  may see and call the tool (fail-open). For privileged servers, make
  the absence of a declaration a startup error instead.

### 2. Normalize Credentials Across Headers

Register one authentication backend per credential source (e.g.
`Authorization: Bearer` for SSO, `X-Service-Account` for automation).
For each request:

1. Run every backend whose header is present.
2. A missing or invalid header contributes nothing. It must not fall
   through to a default principal or block a valid header.
3. Admit the request if at least one backend succeeds; the principal's
   scopes are the de-duplicated **union** of the successful backends'
   scopes. No other case may yield more scopes than its constituents.
4. If no backend succeeds, raise an explicit authentication error at the
   middleware boundary. Never reach a tool-level decision.

(Use AND composition instead of OR where you need multiple credentials
at once for high-assurance tools.)

### 3. Verify Tokens With a Bounded Cache

For opaque tokens that need an IdP round-trip:

- Cache verified results keyed by SHA-256 of the token (never store raw
  tokens) with a TTL. The reference default is 300 s.
- Map vendor scopes into your application's permission vocabulary in
  one place.
- Enforce audience (`aud`) where the IdP reports it: resource-bound
  (names this server) or fleet-bound (a configured shared audience).
- Record the TTL as your **maximum post-revocation window**. If
  revocation must be immediate, set TTL = 0 or add an IdP revocation
  signal. For long-running agents that outlive the token, see
  [`auth-revocation-quiescence`](../auth-revocation-quiescence/SKILL.md).

### 4. Filter Listings by the Same Declaration

In application middleware, hook the listing methods (`list_tools`,
`list_prompts`, `list_resources`) and return only components whose DNF
the caller satisfies. Invariant: for any authenticated caller and any
tool, the tool is listed **if and only if** it is invocable by that
caller. The agent's natural-language input never enters this decision.

### 5. Enforce at Invocation, Independently of Listing

Before the tool body runs, evaluate the same DNF against the caller's
scopes and return 403 on failure. This layer exists for callers that
never consult the listing: a scripted attacker, or a name leaked through
model output, logs, screenshots, or the metadata endpoint.

### 6. (Optional) Publish Pre-Auth Metadata for Registries

Register an unauthenticated route, outside the auth middleware, that
introspects the live registry and returns each component's schema, its
DNF requirement, and the accepted auth methods. The registry can then
index servers without holding credentials, so compromising it grants no
call authority. Treat this as a disclosure trade-off: anyone with
network reach learns exact tool names and permission strings, which is
reconnaissance for attacks on Steps 4–5. Disable it or put it behind
separate protection if that is unacceptable.

### 7. Verify the Boundary Adversarially

Before release, run three checks against a test server with one
low-privilege credential:

1. **Injection sweep**: payloads across direct, indirect (via tool
   output), role-play, and context-overflow classes. Record attempt,
   invocation, and name-leak per call. Expect zero attempts with
   filtering on.
2. **Direct-call probe**: a non-LLM client calls each hidden tool by
   name. Every call must be rejected by Step 5.
3. **Header matrix**: {Bearer, custom} × {present, absent, invalid}.
   Confirm that the union row is the only widening case and that the
   all-fail case errors.

---

## Environment Caveats

- Applies to HTTP transports. **stdio bypasses HTTP-layer security
  entirely** and needs a separate scheme (capabilities or mTLS over
  local sockets).
- The threat model assumes the agent cannot forge HTTP headers and that
  the IdP, host, and TLS chain are trusted. It does not address
  downstream token exchange (RFC 8693) when the server calls other
  services on the user's behalf.
- Declarative RBAC in DNF cannot express resource-scoped, time-aware,
  or delegation-aware policy; put a policy engine (OPA/Cedar) behind the
  same decorator if you need those.
- Recent FastMCP (3.0+) `auth=` already couples listing and invocation
  for one conjunctive callable. The extra value of this procedure is
  DNF composition, cross-header credentials, and a third consistent
  surface (pre-auth metadata).
- The 0/720 filtered result is structural, not a robustness score. The
  injection corpus was 60 payloads against one forbidden tool.

## Failure Modes

| Failure Mode | Trigger | Mitigation |
|:--|:--|:--|
| Filter-only bypass | Tool hidden from listing but no invocation check; name leaks via model text or logs | Step 5 check on every privileged tool |
| Policy drift | Listing rules and call checks maintained separately | Single declaration read by all layers (Step 1) |
| Header confusion | Missing/invalid header falls through to a default or wider scope | Deterministic OR-merge; union only when each header is valid (Step 2) |
| Stale credential | Token revoked at IdP but still cached | Bounded TTL; TTL = 0 or revocation signal for high-risk tools (Step 3) |
| Fail-open default | Tool registered without a declaration is callable by every authenticated caller | Reject undeclared components at startup on privileged servers |
| Refusal-as-boundary | Relying on model alignment to ignore injected tool requests | Attempt rates ranged 0–50% across vendors on identical inputs; enforce server-side |
| Roster-as-boundary | Relying on multi-agent role splits to keep a tool away from the orchestrator | Full-roster delegation still executed a destructive call in 3/60 trials; a policy-enforced role-to-roster mapping isolated tools but enforced a parameter ceiling in 0/60 (arXiv:2609.28693). Keep the Step 5 check and add argument limits server-side |

## Cross-References

- [`mcp-server-design`](../mcp-server-design/SKILL.md): catalog and tool design for the same servers
- [`mcp-tool-hijacking-defense`](../mcp-tool-hijacking-defense/SKILL.md): client-side defense against malicious tool metadata
- [`runtime-resource-authorization-bounds`](../runtime-resource-authorization-bounds/SKILL.md): authority for resources acquired at runtime
- [`unified-capability-gateway`](../unified-capability-gateway/SKILL.md): single auditable invocation pipeline
- [`auth-revocation-quiescence`](../auth-revocation-quiescence/SKILL.md): closing effect paths after revocation
- [`sdc-mcp-dry-run-gateway`](../../research-briefs/sdc-mcp-dry-run-gateway.md): read-only resources plus dry-run tools for physical-effect systems
- `rules/agent-sandbox-safety.md`: "Resolve tool existence before any selection or authorization gate"; "Rely on structured LLM authorization decisions as the sole safety gate"; "Treat tool hiding, specialist prompts or roster delegation as access control"

## Sources

> Li, Wang & Manoharan, "Zero-Trust Authorization and Discovery for
> Enterprise MCP" (arXiv:2609.22573), Sep 2026.
