---
name: auth-revocation-quiescence
description: >
  Revoke authorization for long-running AI agents that outlive their
  initiating process — covering delegated tasks, queued callbacks,
  provider-side reservations, and transferred credentials — using a
  root-scoped quiescence protocol that proves no old-authority effects
  can occur after the fence.
  Derived from "Authorization Revocation for Long-Running AI Agents"
  (arXiv:2609.21284).
source: https://arxiv.org/abs/2609.21284
---

# Authorization Revocation for Long-Running AI Agents

Use this skill when revoking access for an agent that has delegated
tasks, queued callbacks, or holds credentials across multiple
providers — and you need to guarantee that no further effects occur
under the revoked authority.

## When to Use

- Retiring or rotating credentials for a long-running agent that has
  spawned sub-agents, queued work, or made provider reservations
- Implementing "kill switch" functionality for autonomous agent systems
  with delegation chains
- Auditing whether all effects of a revoked authority have been
  accounted for after credential rotation
- Designing auth revocation into multi-agent orchestration systems
  where simple cancellation is insufficient

## Core Insight

Cancellation, process exit, and credential revocation are each
**necessary but insufficient** for closing all effect paths of a
long-running agent. The paper proves this with a strict counterexample:
a cancelled agent's already-queued callback executes on a provider
after process exit and after credential revocation, producing an effect
under authority that was nominally retired. The root-scoped quiescence
protocol closes this gap by producing a **certificate** that accounts
for every cut-relevant acceptance under the retired authority.

**Evidence**: 17/17 late-effect test cases matched; an independently
implemented checker verified 17/17 traces and rejected 44/44 semantic
regressions. The protocol proves six formal properties including
post-cut issuer non-expansion, compositional soundness, and
crash/replay stability.

---

## Procedure

### 1. Linearize and Seal the Root Cut

Establish a single, globally ordered "root cut" event that marks the
moment the old authority is being retired:

- Assign a **root-epoch atom** — a unique, monotonic identifier for
  the authority session being retired
- **Seal** the root cut: after this point, no new issuance of the
  old-root atom is permitted
- Record the cut event durably (crash-stable) so it survives restarts

### 2. Project Actual Old-Root Dependence

For each active task, credential, or queued callback, determine whether
it **actually depends** on the old root authority:

- Build the **minimal sufficient root set** for each active acceptance
  — the smallest set of root-epoch atoms that independently authorize it
- Represent alternative authority as **antichains** (sets where no
  element is a subset of another)
- Tasks that have **independent, current** authority (not derived from
  the old root) are **preserved** — they need not be terminated

### 3. Install Adapter-Specific Barriers (Fences)

For each provider endpoint or channel that could carry old-root
effects, install a **fence** — an adapter-specific barrier that
prevents new protected acceptances under the old-root atom:

- Queue adapters: stop dequeuing items tagged with old-root credentials
- Callback endpoints: reject or re-authenticate incoming calls bearing
  the old-root token
- Provider reservations: issue cancellation or re-bind requests
- **Fence must precede** any manifested sink observation

### 4. Conserve Local and Transferred Carriers

Account for every in-flight token, message, or credential that could
carry old-root authority:

- Use **exact channel-token accounting** — every issued token must be
  matched by a received or cancelled token
- Track transfers between agents/providers to prevent lost tokens from
  leaving unaccounted effect paths
- Missing or conflicting evidence results in an **indeterminate**
  verdict (not a false pass)

### 5. Produce Provider-Frontier Leaf Certificates

Each provider endpoint produces a **leaf certificate** attesting that:

- All cut-relevant acceptances under the old-root atom that preceded
  the local fence have been accounted for
- No protected acceptance under the old-root atom occurred after the
  fence
- Any exact rebind to current, independently sufficient authority is
  documented

### 6. Compose the Cutset Certificate

Compose all leaf certificates into a **cutset** over registered
old-root paths:

- The cutset must cover every registered path from the old root to any
  manifested sink
- Composition is **merge-order independent** — certificates can arrive
  in any order
- The final certificate establishes **root-relative authorization
  quiescence** within its bound manifest

### 7. Verify and Act on the Certificate

- **Quiescent**: all paths covered, all tokens accounted → safe to
  confirm the old authority is fully retired
- **Indeterminate**: missing evidence or conflicting accounts → flag
  for investigation; do NOT assume quiescence
- **The certificate does NOT prove**: global idleness, rollback of
  completed effects, or business-level completion

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Late effect after cancellation | Queued callback executes on provider after agent process exits | Install provider-endpoint fences (Step 3) before confirming revocation |
| Shared-work false termination | Revoking authority kills tasks that have independent authorization | Project minimal sufficient root sets (Step 2); preserve independently authorized work |
| Token leak / unaccounted carrier | Credential transferred to sub-agent not tracked in accounting | Exact channel-token conservation (Step 4); treat missing evidence as indeterminate |
| Crash during protocol | Node crashes between fence and certificate | Protocol is crash/replay stable; replay from durable cut record |
| Certificate mistaken for global safety | Operator assumes quiescence = no effects anywhere | Certificate covers only registered manifest; unregistered paths require separate assurance |

> Source: Zhu & Wang, "Authorization Revocation for Long-Running AI
> Agents" (arXiv:2609.21284), Sep 2026.
