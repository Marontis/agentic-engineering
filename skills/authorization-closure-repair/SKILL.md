---
name: authorization-closure-repair
description: >
  Keep a tool-using agent's user authorization correct when the user changes
  part of an instruction mid-task: track user authority, authoritative
  observations and derived consequences in a versioned dependency graph,
  invalidate only what depends on the change, and ask the user only for the
  minimal missing evidence or approval before a state-changing action.
  Derived from "Authorization Closure Graph: Minimal Repair for LLM Agents
  with Evolving User Instructions" (arXiv:2609.32428).
source: https://arxiv.org/abs/2609.32428
---

# Authorization Closure Repair

Use this skill when a customer-service or operations agent executes writes
(bookings, cancellations, refunds, account changes) on the user's behalf,
and users revise, add to or withdraw parts of their request during the
conversation.

## When to Use

- Multi-item requests where one item changes ("move passenger B to Friday,
  keep A as is") and you must not re-ask for everything, nor silently reuse
  stale approvals
- Writes with material consequences (charges, refunds) that need explicit
  confirmation, under business rules that may not be overridden
- Agents that today either reset all approvals on any change (annoying,
  lower success) or keep them all (unsafe)

Not for: revoking authority from running or delegated work after the fact.
That is [auth-revocation-quiescence](../auth-revocation-quiescence/SKILL.md).
Token and scope state under credential revocation is
[residual-auth-state-preservation](../residual-auth-state-preservation/SKILL.md).

## Core Insight

Treat authorization as a **closure** over a dependency graph: an action is
authorized only when every node it depends on (user authority, authoritative
observations, approved consequences) is current. A change invalidates the
changed node and its descendants, nothing else. When something is missing,
ask for the **frontier**: the smallest set of requirements that are not
recoverable from an upstream answer.

**Evidence** (τ²-bench Airline 50 tasks and Retail 114 tasks; DeepSeek-V4-Flash,
GPT-5.6-Terra, Gemini-3.6-Flash; writes reviewed by two GPT-5.6-Sol judges):

- Airline action safety rose from 78.3% / 49.1% / 58.4% (policy-prompted
  agent, no gates) to 100.0% / 87.9% / 94.7%; safe task success from
  60.0% / 50.0% / 50.0% to 80.0% / 64.0% / 72.0%.
- Unsafe tasks across all settings fell from 75 to 8.
- On ClosureBench (936 controlled change cases), safe task success was
  91.7% with zero unsafe executions, versus 25.0% for fresh re-approval,
  37.5% for resetting all authority and 69.4% for asking every missing
  requirement.
- Retail gains were small or mixed (DeepSeek safe task success 86.8% raw vs
  85.1% with the graph), because the raw agent was already safe there
  (98.2% action safety).

---

## Procedure

### 1. Write Specs Per Tool (Developer-Authored)

For each state-changing tool, write:

- **Effect spec**: the canonical operation and argument mapping (for example
  `retail_cancel_effect(order_id, reason)`).
- **Dependency spec**: which authoritative observations it needs (verified
  identity, order owner and status, payment details).
- **Authority mode** for each derived consequence: `inherit` (carried by the
  user's instruction), `bounded` (allowed within a stated limit, such as a
  price cap) or `confirm` (needs explicit approval, such as a refund).
- **Business rules** that no approval can override (the user owns the order;
  status is pending).

Specs are the trust base. Review them like code, and route spec changes
through the acceptance gate in `rules/recursive-improvement.md` ("Pass every
self-modification through one acceptance gate"), with unsafe-write cases as
the strict testbed.

### 2. Maintain the Graph

Keep a DAG with three node kinds (user authority, authoritative evidence,
derived consequences). Each node stores value, version, availability,
authority status and the parent versions it was derived from. Mutate it
only through six operations:

| Operation | Use |
|:--|:--|
| commit | record an authenticated user instruction |
| revise | replace an existing instruction |
| revoke | withdraw an instruction |
| observe | record evidence from an authoritative tool |
| confirm | record an explicit approval |
| group | one approval covering several actions |

Only authenticated user turns may commit, revise, revoke or confirm. Tool
output can only observe.

### 3. On Any Change, Invalidate the Affected Set Only

1. Find the directly changed nodes.
2. Add every descendant reachable from them.
3. Mark those stale; leave all other nodes, including their approvals,
   intact.

Example: revising passenger B's date invalidates B's date node and B's
selected flight; passenger A's nodes keep their authority.

### 4. Decide Each Write: Block, Repair or Authorize

Before executing a write, evaluate its closure:

- **Block** if a business rule fails. No approval fixes this.
- **Repair** if requirements are missing. Compute the missing set, then
  drop every requirement that an upstream answer would supply through an
  `inherit` path. Ask only for what remains: a reason from a fixed list, or
  "material consequences: <charge or refund>", together with the fixed
  action and any proposed local revision. Do not bundle unrelated approvals.
- **Authorize** only when every dependency is current.

### 5. Evaluate With Write-Level Safety

Report action safety (share of executed writes that satisfy policy) and
safe task success (task success with no unsafe write) next to plain task
success. Build controlled change cases (vary branch count, chain length and
change type) to test the update mechanism directly.

---

## Ablation Highlights

- Airline, DeepSeek: checking alone 85.7% action safety; check plus repair
  97.0%; full graph 100.0%.
- Both parts matter: invalidating all authority but asking minimally, or
  invalidating only affected nodes but asking for everything, each scored
  below the full method on all three models (Airline action safety, for
  example GPT-5.6-Terra 86.0% and 81.4% vs 87.9%).
- Cost stayed within ordinary interaction range: about 62k–99k actor tokens
  per task at the highest safe task success.

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:--|:--|:--|
| Wrong or missing dependency edge | Spec omits that a consequence depends on a node | Spec review; controlled change tests per new tool |
| Untrustworthy observation | Evidence comes from a non-authoritative tool or injected text | Only designated tools may `observe`; treat other outputs as data |
| Spoofed confirmation | Approval text arrives via tool output | Accept `confirm` only from authenticated user turns |
| Over-asking | Missing set not reduced to the frontier | Compute inheritance paths before asking |

Stated limitations: depends on correct specs, authoritative observations and
authenticated confirmation; two domains with simulated users; one trial per
task.

## Cross-References

- [verified-policy-action-governance](../verified-policy-action-governance/SKILL.md): deterministic per-call allow/deny that this graph can feed
- [auth-revocation-quiescence](../auth-revocation-quiescence/SKILL.md): revocation of in-flight effects
- `rules/agent-sandbox-safety.md`: "Gate tool actions with dependency-scoped lineage checks rather than trusting state freshness"

## Sources

> Authorization Closure Graph: Minimal Repair for LLM Agents with Evolving
> User Instructions (arXiv:2609.32428), Sep 2026.
