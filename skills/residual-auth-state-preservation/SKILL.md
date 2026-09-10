---
name: residual-auth-state-preservation
description: >
  Preserve and verify authorization state that language agents must maintain
  under token revocation, session expiry, and delegated-scope changes.
  Derived from "ResidualAuth" (arXiv:2609.08062).
source: https://arxiv.org/abs/2609.08062
---

# ResidualAuth: Authorization State Preservation under Revocation

Use this skill when building agents that hold delegated credentials (OAuth
tokens, API keys, session cookies) and must handle revocation, expiry, or
scope narrowing without silently operating with stale permissions.

## When to Use

- Agent holds OAuth tokens or API keys with limited TTL or revocable scopes
- Agent operates across session boundaries where authorization may change
- Agent delegates capabilities to sub-agents that inherit parent scopes
- Post-revocation behavior must fail safely, not silently degrade

## Core Insight

Language agents that cache authorization state (tokens, scopes, permissions)
risk operating with stale credentials after revocation. ResidualAuth
formalizes the authorization state that must be preserved: the residual —
the minimum authorization footprint an agent must maintain to detect and
respond to revocation events. Without explicit residual tracking, agents
silently degrade to unauthorized operation, which is worse than a clean
failure.

The paper couples prime-power identity with BLS aggregate signatures and
derives a safe-kill threshold that reduces false-positive agent termination
from 80% to 0.00% under 10% channel noise.

---

## Procedure

### 1. Define the Residual Authorization Footprint

For each agent capability, enumerate:
- **Required scopes**: What permissions the capability needs
- **Revocation signals**: How the agent detects scope narrowing or
  token expiry (webhook, polling, error codes)
- **Residual state**: The minimum cached state needed to verify
  authorization is still valid before each privileged operation

### 2. Implement Pre-Action Authorization Checks

Before every privileged tool call or API request:
1. Check the cached authorization state against the residual footprint
2. If any required scope is missing or expired, **halt and surface
   the failure** rather than attempting the operation
3. Log the authorization check result for audit

### 3. Handle Revocation Events

When a revocation signal is received:
1. Immediately invalidate all cached credentials in the affected scope
2. Propagate the revocation to any sub-agents holding delegated
   credentials from this agent
3. Queue pending operations for re-authorization or clean failure
4. Do NOT retry with stale credentials

### 4. Verify Delegation Chains

When delegating capabilities to sub-agents:
- Sub-agent scopes must be a strict subset of parent scopes
- Revocation of parent scope must cascade to all sub-agents
- Sub-agents must not be able to escalate beyond delegated scope

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Silent stale credential use | Revocation signal missed or delayed | Poll authorization status at configurable intervals; treat unknown status as revoked |
| False-positive termination | Noisy revocation channel | Apply safe-kill threshold with aggregate signature verification before terminating |
| Delegation scope escalation | Sub-agent requests broader scope | Enforce strict subset validation at delegation time |
| Residual state bloat | Too many cached authorization entries | TTL-expire cached entries; prune on session boundaries |

## Sources

> Source: "ResidualAuth: What Authorization State Must Language Agents Preserve under Revocation" (arXiv:2609.08062)
