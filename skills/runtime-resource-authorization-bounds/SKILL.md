---
name: runtime-resource-authorization-bounds
description: >
  Enforce provenance-bounded runtime authorization for resources acquired dynamically by
  AI agents (credentials, endpoints, MCP tools, compute). Quarantines acquired outputs,
  resolves capability manifests, and gates activation via single-use effect permits.
source: https://arxiv.org/abs/2609.14744
---

# Runtime Resource Authorization Bounds (AcquireBound)

Use this skill when an autonomous AI agent dynamically provisions, purchases, or discovers
external resources—such as API keys, cloud compute, database accounts, or Model Context Protocol
(MCP) tools—preventing unauthorized authority amplification and privilege escalation.

## When to Use

- Agents interacting with external tool registries, MCP servers, or dynamic API gateways
- Multi-step agents with authority to create or provision cloud resources (Docker containers, VMs)
- Autonomous purchasing or commerce agents (AP2/UCP) where fulfillment returns usable access tokens
- Preventing untrusted third-party tool outputs from introducing ambient execution authority

---

## Core Mental Model: The Post-Fulfillment Activation Gap

Standard authorization validates transaction preconditions (e.g., budget limits, OAuth token
validity, or user checkout approval). However, it creates a **post-fulfillment activation gap**:
it does not verify whether the *returned* resource can safely become usable execution authority.
An agent acquiring an innocent-looking tool or token can inadvertently grant an attacker
unbounded access.

**AcquireBound** establishes a four-stage containment lifecycle:

```
[Agent Acquires External Resource (e.g. MCP Server URI, API Token)]
                           │
                           ▼
     [Stage 1: Quarantine Boundary]
     - Resource placed in quarantined hold
     - Cannot be invoked by model or runtime
                           │
                           ▼
     [Stage 2: Versioned Capability Resolution]
     - Resolver inspects authenticated provider evidence
     - Maps actual endpoints and actions to typed capability hypergraph
                           │
                           ▼
     [Stage 3: Activation Transaction]
     - Evaluates relational envelope:
       * Provenance origin check
       * Epoch freshness check
       * Non-amplification invariant
                           │
                           ▼
     [Stage 4: Single-Use Effect Linearization]
     - Issues single-use effect permit
     - Permit consumed and invalidated upon execution
```

---

## Step-by-Step Procedure

### 1. Enforce Immediate Resource Quarantine

Any tool return value classified as a resource artifact (e.g., token, connection URL, MCP manifest)
must be stored in an isolated quarantine registry rather than returned directly into active context:

```python
def handle_resource_acquisition(tool_output, session_context):
    """Intercept and quarantine dynamically acquired agent resources."""
    resource_id = generate_urn(tool_output)
    session_context.quarantine_store.register(
        resource_id=resource_id,
        raw_payload=tool_output,
        provenance={
            "initiating_tool": tool_output.get("tool_name"),
            "timestamp": current_timestamp(),
            "epoch": session_context.current_epoch,
        },
        state="QUARANTINED"
    )
    # Return non-actionable handle to model context
    return {"status": "quarantined", "resource_handle": resource_id}
```

### 2. Resolve Authenticated Capability Manifests

Do not trust descriptions emitted by third-party tool responses. Execute an independent resolver
that inspects authenticated provider metadata:

1. Query the provider's authoritative discovery endpoint (e.g., `/.well-known/agent.json` or MCP OpenAPI spec).
2. Deconstruct exposed methods into explicit granular permissions:
   - Resource targets: read-only, state-mutating, network-egress.
   - Blast radius bounds: maximum rate limit, timeout, parameter restrictions.
3. Construct a resolved **Capability Manifest**.

### 3. Validate the Activation Envelope

Before any tool or agent turn can invoke the quarantined resource, execute an activation check
asserting three mathematical invariants:

- **Non-Amplification**: The new resource's capability set must be a strict subset of the calling agent's authorized envelope ($Cap(resource) \subseteq Cap(agent)$).
- **Epoch Freshness**: The resource's provisioning epoch must match the active session epoch; stale resources from aborted turns are rejected.
- **Provenance Integrity**: The resource must originate from a verified provider whose signature matches the session allowlist.

### 4. Issue Single-Use Effect Permits

When the agent invokes a tool on an activated resource:
- The authorization layer generates an ephemeral, cryptographically signed permit tied to the specific action parameters.
- At execution linearization, the permit is atomically checked and invalidated. Replay attacks, double-submissions, and unauthorized retries are blocked immediately.

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:---|:---|:---|
| **Ambient Authority Leakage** | Subagent uses credentials from an earlier turn to call unauthorized APIs. | Epoch Invalidation: Bump session epoch on turn boundary; revoke all permits tied to older epochs. |
| **Split-Identity Evasion** | Agent uses multiple small tools to assemble high-privilege credentials piecemeal. | Global Hypergraph Envelope: Track cumulative capabilities across all acquired resources; trip circuit breaker if combined set exceeds limits. |
| **Tampered Manifests** | Compromised MCP server claims benign capabilities while hosting destructive endpoints. | Independent Signature Verification: Reject manifests not signed by an authorized CA or verified provider keystore. |
