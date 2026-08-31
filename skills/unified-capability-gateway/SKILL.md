---
name: unified-capability-gateway
description: >
  Route every agent capability invocation through a single multi-stage
  pipeline for subject binding, contract resolution, policy enforcement,
  authorization, and dispatch.  Derived from CrabOS (arXiv:2608.28165).
---

# Unified Capability Gateway

Use this skill when designing the capability invocation layer for systems
where multiple executors (human users, AI agents, apps) share the same
infrastructure and need auditable, policy-governed access to capabilities.

## When to Use

- Building agent infrastructure where multiple principals invoke capabilities
- You need an audit trail that covers both human and AI actions uniformly
- You want to enforce authorization policies consistently across all callers
- You're designing a tool/capability system for an agent framework

## Core Insight

When humans and AI share a work environment, every capability invocation —
regardless of who or what initiated it — should pass through the same
auditable pipeline.  Private tool-packaging layers that bypass this
pipeline create unauditeable gaps.

**Evidence**: CrabOS demonstrates that typical agent capabilities (memory
management, multi-agent orchestration, cross-app context sharing) emerge
from primitive operations when ALL invocations go through a unified
kernel interface, without requiring purpose-built orchestration APIs.

## Procedure

### Step 1: Define the capability surface

Enumerate every system capability that any executor (human, AI agent, app,
sub-agent) can invoke.  Examples: file read/write, network requests,
database queries, tool execution, agent spawning, memory updates.

Classify each capability by its risk level:
- **Read-only**: No state changes, no external effects
- **State-modifying**: Changes local state (files, memory, config)
- **External**: Reaches outside the system boundary (network, APIs)
- **Privileged**: Can modify system behavior (config changes, agent
  spawning, permission grants)

### Step 2: Implement the 5-stage pipeline

Every capability invocation passes through these stages in order:

#### Stage 1: Subject Binding
Bind every invocation to an identified system subject.  The identity
must be enforced at the transport layer — never self-declared.

```
invocation.subject = transport.authenticated_identity()
# NOT: invocation.subject = request.headers["x-agent-id"]
```

#### Stage 2: Contract Resolution
Interpret the request as a governed system contract.  Map the raw
invocation to a canonical capability type with defined boundaries.

```
contract = resolve_contract(invocation.action, invocation.params)
# contract.type = "file_write"
# contract.scope = "/workspace/project/"
# contract.constraints = { max_size: "10MB" }
```

#### Stage 3: Policy Enforcement
Determine permission and resource boundaries BEFORE execution.
Reject invocations that exceed policy limits.

```
policy = get_policy(invocation.subject, contract)
if not policy.allows(contract):
    reject(invocation, reason=policy.denial_reason)
```

#### Stage 4: Authorization Gate
For operations requiring explicit user authorization under security
policy, suspend execution until confirmation arrives.  This stage is
skipped for pre-authorized operations.

```
if contract.requires_authorization:
    authorization = await request_user_confirmation(contract)
    if not authorization.granted:
        reject(invocation, reason="user_denied")
```

#### Stage 5: Capability Dispatch
Send the fully-validated invocation to the service responsible for
executing it.  Log the dispatch for audit.

```
result = dispatch(contract, invocation.params)
audit_log.record(invocation, contract, result)
return result
```

### Step 3: Eliminate private tool layers

If your agent framework wraps system capabilities in a separate
"tool packaging" layer that bypasses the pipeline:

1. Remove the bypass path
2. Route the tool through the gateway pipeline
3. The tool becomes a thin adapter that constructs a proper invocation

The AI agent should invoke capabilities through the SAME entry point
as a human user, allowing the system to apply the same policies.

### Step 4: Materialize state as addressable text objects

For maximum transparency and composability, persist all system state
as natural-language-readable text objects with stable structure:

- Tasks, memory, chat histories, config → text objects
- Objects are directly addressable (path-based or ID-based)
- AI agents can read and write these objects through the gateway
- Orchestration patterns compose from primitive read/write/watch

**Key benefit**: Many "features" (hooks, sub-agents, context sharing)
emerge from addressable text objects + gateway primitives, without
requiring purpose-built APIs.

### Step 5: Record operation traces

Because every invocation passes through the gateway, operation traces
are a natural byproduct:

- Subject, capability, parameters, timestamp, outcome
- Same format for human and AI actions
- Traces support continuation (AI picks up where human left off)
- Traces can feed post-training or reflection systems

## Environment Caveats

- **Latency-sensitive systems**: The 5-stage pipeline adds latency per
  invocation.  For high-frequency operations (streaming output), use
  delayed/batched writes with a lighter validation path.
- **Legacy tools**: Existing tools that bypass the gateway need adapter
  layers.  Three integration depths: full rewrite, backend-retained with
  new frontend, or GUI adapter that maps operations.
- **Bash/shell access**: Direct shell execution bypasses the gateway.
  Route through an external sandbox (container, VM) via controlled
  network access instead of exposing raw shell.

## Failure Modes

- **Self-declared identity**: If subjects can declare their own identity
  (e.g., via a header), any agent can impersonate any other
- **Policy bypass for "trusted" agents**: Exempting certain agents from
  policy enforcement creates unauditable gaps
- **Overloaded authorization gate**: If too many operations require
  human confirmation, users develop confirmation fatigue and rubber-stamp
- **Non-text state**: Binary blobs or opaque database records that
  can't be read by AI agents defeat the transparency benefit

## Cross-References

- [`browser-agent-http-sandbox`](../browser-agent-http-sandbox/SKILL.md) —
  HTTP-layer interception as a specific capability gateway for web agents
- [`transactional-coding-sandbox`](../transactional-coding-sandbox/SKILL.md) —
  Snapshot/rollback as a gateway-triggered safety mechanism
- [`layered-defense-ensemble`](../layered-defense-ensemble/SKILL.md) —
  Stack multiple defense layers with measured correlation

## Sources

- CrabOS: arXiv:2608.28165
