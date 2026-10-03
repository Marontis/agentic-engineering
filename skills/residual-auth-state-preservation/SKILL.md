---
name: residual-auth-state-preservation
description: >
  Preserve and verify authorization state that language agents must maintain
  under token revocation, session expiry, and delegated-scope changes,
  and keep stored user approvals bound to the context they were granted in.
  Derived from "ResidualAuth" (arXiv:2609.08062); approval replay evidence
  from "When Consent Outlives Context" (arXiv:2609.33910).
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

**Evidence** (arXiv:2609.08062): two delegation histories can have
identical current permissions and identical all-pairs reachability yet
require opposite decisions after the same direct-edge revocation, so the
current permission set is not enough state. The paper proves that
exponentially many future-distinct states can share one transitive
closure and bounds the state an exact monitor needs. In paired
language-agent episodes across four open-weight models, a fixed 256-token
summary solved 0–2/16 pairs, sham reads 0/16, and authenticated
current-query reads 15–16/16. In a held-out online-memory diagnostic,
exact ledger serializations fit all 128 pairs at 768 and 1,024 tokens,
while model-written memories solved at most 1/128 pairs per model. A hard
gate reduced eight observed unauthorized effects to zero.

Implication: keep the delegation ledger (not a summary or model-written
memory) as the residual state, and decide each privileged action from an
authenticated read of current authorization, enforced by a hard gate.

**Stored approvals are residual authority too** (arXiv:2609.33910). When
an agent remembers a user's "allow" across tasks or sessions, the grant
can be replayed in a context where it means something else. On AgentDojo
v1.2 (508 cases, six models), retaining grants at tool level gave attack
success 0.114-0.351 against zero in a fresh approval state (up to +35.1
points), and silent execution of approval-gated actions rose from zero to
0.982-1.000 after 64 benign tasks. Exact-resource matching cut success to
0.012-0.039 but not to zero. On 55 Terminal-Bench cases against live
coding agents, replay raised success by 24.9 points on average; one agent
(Goose) admitted every approval-gated probe action silently after a single
benign task. Task-bound authorization removed the effect (PAuth: zero
across all models; Progent: at most 0.009). The authors' guidance: retain
and revalidate the security-relevant bindings under which consent was
granted, and ask again when a change to them alters the action's meaning.

---

## Procedure

### 1. Define the Residual Authorization Footprint

For each agent capability, enumerate:
- **Required scopes**: What permissions the capability needs
- **Revocation signals**: How the agent detects scope narrowing or
  token expiry (webhook, polling, error codes)
- **Residual state**: The exact delegation ledger (who delegated what to
  whom, and every revocation), plus what's needed to make an authenticated
  read of current authorization before each privileged operation

### 2. Implement Pre-Action Authorization Checks

Before every privileged tool call or API request:
1. Read current authorization from the authoritative source (an
   authenticated query, or an exact delegation-ledger serialization),
   not from a cached summary or model-written memory
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

Steps 1–4 stop *new* use of the revoked authority; they do not complete
revocation. Already-queued callbacks, sub-agent work and provider-side
reservations can still take effect after invalidation, propagation and
process exit. When any of these exist, run the root-scoped quiescence
protocol in [`auth-revocation-quiescence`](../auth-revocation-quiescence/SKILL.md)
and treat revocation as complete only on a **Quiescent** certificate
(arXiv:2609.21284).

### 4. Verify Delegation Chains

When delegating capabilities to sub-agents:
- Sub-agent scopes must be a strict subset of parent scopes
- Revocation of parent scope must cascade to all sub-agents
- Sub-agents must not be able to escalate beyond delegated scope

### 5. Bind Stored User Approvals to Their Context

When the runtime remembers user approvals ("always allow", "don't ask
again", session-wide grants):
1. Store each grant with the bindings it was given under: task or goal,
   exact resource (path, recipient, host, command), and anything else
   that changes the action's effect (e.g. the executable or dependency
   that a command resolves to)
2. At each authorization point, re-check those bindings; if any changed
   in a way that alters what the action does, ask the user again
3. Default grant lifetime to the current task; cross-task or
   cross-session reuse must be an explicit, visible user choice
4. Measure it: replay a target action in a fresh approval state and after
   a history of benign tasks; any action admitted only in the second case
   is residual authority (the paper's conditional history exposure)

Exact-resource matching alone is not enough (0.012-0.039 attack success
remained in arXiv:2609.33910): the same resource can mean something
different in a new task.

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Silent stale credential use | Revocation signal missed or delayed | Poll authorization status at configurable intervals; treat unknown status as revoked |
| Summary loses decision-relevant history | Delegation state compressed into a fixed summary or model-written memory | Keep an exact delegation ledger; decide from authenticated current-query reads |
| Late effects after revocation | Queued callbacks or provider-side work outlive invalidation | Run `auth-revocation-quiescence`; complete only on a Quiescent certificate |
| Delegation scope escalation | Sub-agent requests broader scope | Enforce strict subset validation at delegation time |
| Approval replay | A remembered "allow" from an earlier task admits the same tool or resource in a new context | Bind grants to task and resource context; re-ask when bindings change (Step 5) |
| Residual state bloat | Too many cached authorization entries | Never prune, summarize or TTL-expire the delegation ledger; only derived credential caches (tokens, decision caches) may expire |

## Sources

> Source: "ResidualAuth: What Authorization State Must Language Agents Preserve under Revocable Delegation?" (arXiv:2609.08062)
> Revocation completeness: "Authorization Revocation for Long-Running AI Agents" (arXiv:2609.21284)
> Approval replay: "When Consent Outlives Context: Residual Authority Replay in Long-Lived Agents" (arXiv:2609.33910)
