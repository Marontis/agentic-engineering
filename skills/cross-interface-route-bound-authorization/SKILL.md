---
name: cross-interface-route-bound-authorization
description: >-
  Enforce cross-interface authorization equivalence, route-bound prepare-commit
  ticket fencing, and cumulative trace-closure checks for computer-use agents
  operating across GUI, CLI, API, script, and MCP surfaces. Derived from Zhu
  and Wang (arXiv:2610.41397).
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Cross-Interface Route-Bound Authorization

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

Use this skill when designing or hardening authorization gates for hybrid computer-use agents that can reach the same durable sink (`documents`, `messaging`, `calendar`, `tickets`, `ledger`, `access`) through multiple execution interfaces (`GUI`, `CLI`, `API`, `script`, `MCP`). Interface-local guards (`33.3%` coverage) and stateless action-time normalizers (`83.1%` coverage) fail when an agent switches surfaces mid-plan, acts on stale UI/environment bindings, or recomposes data read on one surface into an outbound action on another.

---

## When to Use

- An agent runtime exposes both structured tool surfaces (`MCP`, `API`) and raw computer-use surfaces (`GUI` clicks/keystrokes, bash `CLI`, generated `script` files).
- Tasks use deferred or queued execution (`plan` $\to$ `prepare` $\to$ `commit`), or allow fallback across interfaces when one surface fails.
- Security policies must prevent cross-surface privilege escalation (e.g., an action denied on `MCP` being re-issued via `CLI` `curl` or `GUI` button click) and multi-step data exfiltration across interfaces.

---

## Core Protocol Architecture

```
[Entry Surface: GUI | CLI | API | script | MCP]
       │
       ▼
(1) Surface-Closure Witness Gate ──► Reject E_UNREGISTERED_ROUTE if route ∉ W_cov
       │
       ▼
(2) Route-Specific Typed Normalizer N_r ──► 10-Field Canonical Effect e
       │
       ▼
(3) Prepare Gate: Authorize(G, T_prev, sigma, e)
       ├── Evaluates interface-erased policy on e
       ├── Evaluates cumulative trace closure Derive(T_prev, e, sigma)
       └── Issues Route-Bound Ticket tau = (id, r, e, ik, b_p, v_s, v_p, v_w, h_G, exp)
       │
       ├──► If agent switches route r -> r': Fence(tau) atomically & re-prepare on r'
       ▼
(4) Commit Cut (Pre-Durability Boundary)
       ├── Re-normalize raw invocation u_c via N_r(u_c, sigma_c) -> e_c
       ├── Verify e_c == tau.e, binding b_c == tau.b_p, epochs, full grant body G, idempotency ik
       └── Dispatch to sink -> Return 3-valued finality: Commit(receipt) | Deny(code) | Indeterminate
```

---

## Step-by-Step Implementation Procedure

### Step 1: Register and Verify the Surface-Closure Witness ($W_{\text{cov}}$)

Before admitting any agent action in a session, validate a versioned **Surface-Closure Witness** $W_{\text{cov}} = (V, E_{\text{graph}}, R, S, N, C_{\text{cut}}, v_{\text{prof}}, v_{\text{inv}})$:

1. Enumerate every enabled execution route $r \in R$ across all active interfaces (`GUI`, `CLI`, `API`, `script`, `MCP`) and every durable sink $s \in S$.
2. Verify that every path in $(V, E_{\text{graph}})$ from any entry node of route $r$ to any durable sink $s$ traverses both a registered normalizer node $N_r \in N$ and a pre-durability commit-cut node $c_r \in C_{\text{cut}}$.
3. **Default-Deny Unregistered Routes**: Any invocation arriving on an unregistered surface or under a mismatched `profile_epoch` ($v_{\text{prof}}$) or `inventory_epoch` ($v_{\text{inv}}$) must fail closed immediately with `E_UNREGISTERED_ROUTE` or `E_EPOCH_MISMATCH`.

### Step 2: Normalize Every Surface into a 10-Field Canonical Effect Tuple

Implement a route-specific deterministic normalizer $N_r(u, \sigma)$ that maps the raw surface invocation $u$ (e.g., DOM selector + payload, CLI AST, MCP JSON-RPC args) and current environment state $\sigma$ into an **interface-erased 10-field canonical effect**:

1. **`family`**: Canonical action family (e.g., `"doc.share"`, `"mail.send"`, `"payment.approve"`).
2. **`sink_class`**: Durable sink domain (e.g., `"documents"`, `"messaging"`, `"ledger"`, `"access"`).
3. **`operation`**: Canonical verb.
4. **`target_id`**: Resolved durable resource identifier (never a mutable UI coordinate or ephemeral DOM selector).
5. **`principal_scope`**: Acting principal or tenant scope.
6. **`recipient_scope`**: Destination principal or external domain.
7. **`object_sensitivity`**: Classification label of the target and payload handles.
8. **`amount_band`**: Quantized magnitude or quota band.
9. **`handle_set`**: Sorted tuple of input data handles consumed by this action.
10. **`reversibility`**: `"reversible"` or `"irreversible"`.

- **Fail-Closed Normalization**: If any of the 10 fields cannot be statically resolved, if the UI/CLI target binding witness $b$ is ambiguous, or if an untyped map is returned, reject before prepare/commit with `E_NORMALIZE_FIELD`, `E_NORMALIZE_BINDING`, or `E_NORMALIZE_KIND`.
- **Interface Erasure**: The policy engine `Authorize` may inspect **only** `CanonicalEffect`, cumulative trace state, and environment state — never the source interface label (`GUI` vs `MCP`). This guarantees that an effect allowed or denied on one interface receives the exact same verdict on every other interface.

### Step 3: Issue Route-Bound Prepare Tickets with Cumulative Trace Closure

At prepare time (when an action is proposed or queued), compute $(e_p, b_p) = N_r(u_p, \sigma_p)$ and check two conditions:

1. **Direct Grant Check**: Verify that the active grant set $G$ permits $e_p$ at state $\sigma_p$.
2. **Cumulative Trace-Closure Check (`Derive`)**: Inspect the committed session trace $T_{\text{prev}}$. If `e_p.handle_set` contains data handles derived from prior protected reads (even if read via a different interface), verify that the outbound `recipient_scope` and `sink_class` of $e_p$ satisfy information-flow constraints. Reject unauthorized cross-surface recomposition with `E_DERIVED_EXFILTRATION`.
3. **Issue Route-Bound Ticket ($\tau$)**: If both checks pass, emit a ticket bound to the specific route and epoch state:
   $$\tau = (\text{ticket\_id}, r, e_p, \text{ik}, b_p, v_{\text{state}}, v_{\text{policy}}, v_{\text{witness}}, H(G), G_{\text{snapshot}}, t_{\text{exp}})$$
   where `ik` is an **effect-scoped idempotency key** shared across all interfaces for the same logical operation.

### Step 4: Fence Tickets Atomically Upon Interface Switching

When an agent switches execution surfaces mid-task (e.g., `GUI` automation fails and the agent falls back to `CLI` or `MCP` for the same logical step):

1. **Never reuse a prepare ticket across interfaces**: A ticket prepared for route $r_1$ (`GUI`) is invalid on route $r_2$ (`CLI`), because the target binding witness $b_p$ (e.g., DOM element ref vs file path) is route-specific.
2. **Execute atomic `Fence` + `Re-Prepare`**:
   - Mark $\tau_{r_1}$ as `FENCED` in the ticket ledger (any subsequent attempt to commit $\tau_{r_1}$ must fail with `E_FENCED_TICKET`).
   - Run $N_{r_2}(u_{r_2}, \sigma_{\text{current}})$ on the new route and issue a fresh ticket $\tau_{r_2}$ preserving the logical idempotency key `ik`.

### Step 5: Enforce Pre-Durability Commit Re-Validation and Three-Valued Finality

At the commit cut $c_r$ immediately before durable sink execution, re-evaluate the live invocation $u_c$ against current state $\sigma_c$:

1. **Re-normalize at commit time**: Compute $(e_c, b_c) = N_r(u_c, \sigma_c)$.
2. **Verify 7 Commit Obligations**:
   - $\tau$ is `PREPARED` (not `FENCED`, `COMMITTED`, or `EXPIRED`).
   - Route match: $\text{route}(c_r) == \tau.r$.
   - Canonical effect match: $e_c == \tau.e_p$.
   - Live binding match: $b_c == \tau.b_p$ and $\sigma_c.\text{state\_epoch} == \tau.v_{\text{state}}$ (rejects TOCTOU state drift with `E_STALE_STATE`).
   - Policy & witness epoch match: $\sigma_c.\text{policy\_epoch} == \tau.v_{\text{policy}}$ and $\sigma_c.\text{witness\_epoch} == \tau.v_{\text{witness}}$.
   - Full grant-body verification: Re-verify both digest $H(G_c) == \tau.H(G)$ **and** structural equality $G_c == \tau.G_{\text{snapshot}}$ (prevents digest-retained metadata tampering).
   - Idempotency ledger check: Verify `ik` has not already been committed on *any* interface (`E_DUPLICATE_IDEMPOTENCY_KEY`).
3. **Return Three-Valued Finality**:
   - `Commit(receipt)`: Pre-commit checks passed and the sink returned an authoritative durability receipt. Append to $T_{\text{prev}}$ and mark `ik` consumed.
   - `Deny(error_code)`: Rejected **before** sink dispatch. Guaranteed zero durable side effects; safe for the agent to replan.
   - `Indeterminate(diagnostic)`: Pre-commit checks passed and the sink was invoked, but the durability receipt was lost or timed out. **Never classify a missing post-dispatch receipt as `Deny`**, or the agent will blindly retry a non-idempotent side effect. Quarantined until sink state is reconciled.

---

## Quantitative Reference (`arXiv:2610.41397`)

- **Scenario Coverage (`1,732` scenarios $\times$ `2` runtimes = `3,464` traces across `12` families $\times$ `5` interfaces)**:
  - `Interface-local guard` (`API`/`MCP` only): `33.3%` (`576 / 1,732`).
  - `State-only invariant`: `38.8%` (`672 / 1,732`).
  - `Shared canonical policy` / `Action-time normalization` / `Composite without route-state-trace binding`: `83.1%` (`1,440 / 1,732`) — all three fail on the exact same `292` scenarios (`96` route-switch re-fencing, `96` commit-time state changes, `100` cross-surface recompositions).
  - **Full Route-Bound Protocol**: `100.0%` (`1,732 / 1,732` per runtime; `960` matched commits, `192` re-prepared commits after route fencing, `2,312` pre-finality denials).
- **Mutant & Race Resilience**: Rejects `24 / 24` (`100%`) surface-closure witness mutants, `720 / 720` (`100%`) normalizer mutants, and matches declared outcomes on `168 / 168` (`100%`) commit-race, replay, and missing-receipt probes.
