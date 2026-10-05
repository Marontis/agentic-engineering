---
name: vault-mediated-credential-injection
description: >
  Keep API secrets out of an LLM agent's context, code and environment:
  agents name a connector, and a trusted boundary injects the credential
  only into requests to that connector's configured origin. Includes four
  testable properties (non-observability, origin binding, no ambient cloud
  identity, central lifecycle) and a black-box probe set to verify them.
  Derived from "API Secrets Should Never Become Tokens in the LLM's
  Vocabulary" (arXiv:2609.33371).
source: https://arxiv.org/abs/2609.33371
---

# Vault-Mediated Credential Injection

Use this skill when an agent (chat assistant, coding agent, tool runtime)
must call authenticated APIs, and you want no secret value to ever appear
in a prompt, transcript, log, memory store, generated code or error.

## When to Use

- Users paste API keys into chat, or prompts and tool configs embed them
- Agent-written code runs in a sandbox that needs authenticated egress
- You need evidence, not assurances, that the agent cannot read or
  exfiltrate a credential

## Core Insight

An LLM cannot keep a secret it can see. Once a key enters context it
propagates (history, logs, memory, generated code, error payloads) and an
injection or model error can disclose or misuse it. Move the credential out
of the model's vocabulary: the agent refers to a **connector id**, and the
execution boundary attaches the header only for that connector's origin.

The paper frames exposure as a five-stage chain: introduction, propagation,
trigger (injection or model error), execution with over-privileged tokens,
and persistence of long-lived bearer tokens. Vault mediation cuts the first
two stages and limits the last; it does not fix over-privilege or
injection.

**Evidence**: 16 black-box probes over two connectors (a Federal Reserve
API and the GitHub API) in seven control domains all met their expected
outcome. The sandbox exposed 20 environment variables, none secret; three
echo services received no Authorization header; an unrelated API returned
401. One connector failed functionally (it needed query-parameter auth but
was configured for headers) and failed closed. The authors call this "a
functional security evaluation, not a certification": 16 purposive probes
support no prevalence claim.

---

## Procedure

### 1. Inventory and Block

1. Inventory every credential: owner, scope, classification, expiry.
2. Detect credential patterns in user messages and prompts; refuse to
   forward them to the model and offer connector onboarding instead.
   Pattern detection misses novel formats, so this is a backstop.

### 2. Replace Values With Connectors

- Store credentials in a vault outside the agent runtime.
- Register each as a connector: id, allowed origin(s), auth placement
  (header or query parameter, matching the provider), scopes.
- The agent and its code reference only the connector id.

### 3. Inject at the Boundary

An egress proxy or tool runtime outside the sandbox:

1. Resolves the connector id.
2. Checks the request's destination against the connector's origin.
3. Attaches the credential only on a match; otherwise sends the request
   unauthenticated or blocks it.
4. Strips auth headers and secrets from responses, logs and telemetry.

Provide no ambient identity: block cloud metadata endpoints and do not
mount workload credentials into the sandbox.

### 4. Verify the Four Properties With Probes

| Property | Probe (expected outcome) |
|:--|:--|
| P1 Non-observability | Dump env, read mounted files, echo own request headers (no secret visible) |
| P2 Origin binding | Call echo services and an unrelated API through the connector (no Authorization header; 401 from the unrelated API) |
| P3 No ambient identity | Query cloud metadata endpoints (unreachable) |
| P4 Central lifecycle | Rotate and revoke from the vault (agent behavior follows without any secret in config) |
| Function | Make the intended authorized call (succeeds) |

Re-run the probes on every runtime or connector change, as a strict
security testbed in the acceptance gate (`rules/recursive-improvement.md`,
"Pass every self-modification through one acceptance gate").
Not covered by the paper's probes: redirect chains, DNS rebinding, OAuth
refresh capture, MCP session state. Add probes for those yourself.

### 5. Add the Controls Vault Mediation Does Not Provide

In the authors' residual scoring (1–5 likelihood x impact), over-privileged
connectors went from 20 to 15 and indirect prompt injection from 25 to 12,
versus 25 to 4 for a pasted secret. So also:

- Minimize provider authority: split read and write, prefer per-user OAuth.
- Authorize actions outside the model at deterministic policy points; gate
  transfers, deletion, exports, privilege changes and production mutations
  (see [verified-policy-action-governance](../verified-policy-action-governance/SKILL.md)).
- Restrict egress destinations.
- Test refresh, revocation, rotation and offboarding.
- Red-team continuously with agent-injection benchmarks.

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:--|:--|:--|
| Auth placement mismatch | Provider expects query-param auth | Configure placement per connector; the function probe catches it |
| Secret relocated by tool output | A tool returns a token in its body | Redact secret patterns from tool outputs before they reach context |
| Over-privileged connector | One broad token behind the connector | Per-action scopes; deterministic action gates |
| Telemetry leak | Debug logging of full requests | Redact auth headers at the proxy |

## Cross-References

- [mcp-zero-trust-tool-authorization](../mcp-zero-trust-tool-authorization/SKILL.md): per-tool authorization on the server side
- [runtime-resource-authorization-bounds](../runtime-resource-authorization-bounds/SKILL.md): credentials the agent acquires at runtime
- [browser-agent-http-sandbox](../browser-agent-http-sandbox/SKILL.md): HTTP-layer interception
- [agentxploit-defensive-lessons](../../research-briefs/agentxploit-defensive-lessons.md): credentials crossing component boundaries as a recurring root cause

## Sources

> API Secrets Should Never Become Tokens in the LLM's Vocabulary: A Threat
> Analysis of API Credential Handling (arXiv:2609.33371), Sep 2026.
