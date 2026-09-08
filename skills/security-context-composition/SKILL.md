---
name: security-context-composition
description: >
  How to verify that individually correct agent security controls
  compose into end-to-end secure execution.  Covers assume-guarantee
  contracts, authenticated security-context propagation across
  component boundaries, and consequence integrity verification.
  Derived from "CONTINUITY: Security-Context Contracts for Composable
  LLM Agent Controls" (arXiv:2609.05269).
---

# Security-Context Composition

Use this skill when building or auditing an agent system where
multiple security controls (provenance tracking, authorization,
policy enforcement, protocol adapters, execution controls) must
compose correctly across component boundaries.

## When to Use

- Your agent system combines multiple security mechanisms from
  different components (auth, policy, sandbox, tools)
- You need to verify that security context is not dropped, widened,
  or reinterpreted as actions cross component boundaries
- You are designing a new security layer and need to ensure it
  composes with existing controls
- You are auditing an agent system for security-context discontinuity

## Core Insight

**Individually correct security mechanisms do not necessarily compose
into an end-to-end secure system.**  The failure mode is
**security-context discontinuity**: security-critical context
(principal identity, authorization scope, provenance, policy state)
can be dropped, widened, rebound, or reinterpreted as actions cross
component boundaries.

The CONTINUITY framework addresses this with **assume-guarantee
contracts**: each component declares what security context it assumes
on entry and what it guarantees on exit.  Authenticated context
carriers link these contracts across transitions.

**Key evidence**: In 2,560 parameterized attack instances spanning
128 fault-domain classes across four application domains, the full
contract configuration committed no harmful external effect, while
completing all 700 benign tasks and escalating all 200 ambiguous cases.

---

## Procedure

### 1. Model Each Component's Security Contract

For every component in the agent's instruction-to-effect path, define
an assume-guarantee contract:

```
component: str
assumes:
  - principal_authenticated: bool
  - authorization_scope: str     # e.g., "read-only", "tool-X"
  - provenance_verified: bool
  - policy_state: str            # e.g., "standard", "elevated"
guarantees:
  - context_preserved: bool      # Did not widen or drop context
  - effect_authorized: bool      # Output effects are within scope
  - provenance_extended: bool    # Added own provenance commitment
```

Components include: prompt router, tool dispatcher, sandbox runtime,
output filter, delegation handler, protocol adapter.

### 2. Define Context Carriers

Security context must be carried across transitions using
authenticated carriers.  Six carrier types:

1. **Signed root grants**: The initial authorization from the
   principal, cryptographically bound to the task
2. **Provenance commitments**: Each component signs its contribution
   to the execution trace
3. **Role-bound transition receipts**: Evidence that context crossed
   a boundary with correct role binding
4. **Bounded typed releases**: Authorization for specific effect
   types within explicit bounds
5. **Transformation witnesses**: Proof that a context transformation
   (e.g., delegation) preserved security properties
6. **Effect-bound execution permits**: Authorization for specific
   external effects, bound to the current task and principal

### 3. Verify End-to-End Consequence Integrity

Every external effect (tool call, file write, network request,
state mutation) must be backed by a valid **authorization witness**
that links:

- **Principal** → who authorized this?
- **Task** → what task does this serve?
- **Provenance** → what chain of processing led here?
- **Delegation** → if delegated, was the delegation valid?
- **Policy state** → was the governing policy current at execution?
- **Canonical action** → what specific action is being taken?
- **Finality boundary** → is this the point of no return?

If any link in this chain is broken, the effect MUST be blocked or
escalated for human review.

### 4. Fault-Injection Testing

Validate the composition with deterministic fault injection across
these fault classes:

- **Context drop**: Remove security context at a component boundary
- **Context widening**: Expand authorization scope at a transition
- **Context rebinding**: Change the principal identity mid-chain
- **Context reinterpretation**: Change the semantic meaning of a
  policy field across components
- **Stale context**: Use an expired or superseded authorization

For each fault class, verify that the system either blocks the
effect or escalates to human review — never silently proceeds.

---

## Environment Caveats

- This procedure requires access to the agent system's component
  boundaries and message-passing interfaces
- Cryptographic context carriers add latency; use lightweight
  signatures (HMAC) for internal boundaries, full signatures for
  cross-trust-domain boundaries
- The contract model assumes deterministic component behavior for
  verification — stochastic LLM outputs should be treated as
  untrusted and verified before context propagation

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Contract gap | Component added without contract | Require contract declaration as part of component registration |
| Context widening | Delegation handler expands scope | Enforce monotonic scope narrowing: delegated scope ⊆ delegator scope |
| Stale authorization | Policy updated after grant issued | Bind context carriers to policy version; re-validate on effect execution |
| Performance overhead | Full verification on every action | Tier the verification: lightweight for internal, full for external effects |

## Cross-References

- [`unified-capability-gateway`](../unified-capability-gateway/SKILL.md) —
  Route all agent capabilities through a single gateway with policy enforcement
- [`dependency-scoped-plan-validation`](../../../../.gemini/config/skills/dependency-scoped-plan-validation/SKILL.md) —
  Validate pending actions derive from current, un-superseded memory dependencies
- [`browser-agent-http-sandbox`](../browser-agent-http-sandbox/SKILL.md) —
  HTTP-layer sandboxing that this contract model can govern

## Sources

- [CONTINUITY: Security-Context Contracts for Composable LLM Agent Controls](https://arxiv.org/abs/2609.05269) (arXiv:2609.05269)
- Praxis source: `src:2609-05269`
