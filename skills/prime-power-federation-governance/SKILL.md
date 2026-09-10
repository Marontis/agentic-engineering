---
name: prime-power-federation-governance
description: >
  Govern multi-agent federations using prime-power identity encoding,
  BLS aggregate signature verification, and safe-kill thresholds for
  adversarial-resistant participation tracking and enforcement.
  Derived from "PRIMUS" (arXiv:2609.07910).
source: https://arxiv.org/abs/2609.07910
---

# PRIMUS: Prime-Power Federation Governance

Use this skill when building multi-agent federations that need
cryptographically verifiable identity, participation tracking, and
governance enforcement under adversarial conditions.

## When to Use

- Multi-agent system requires verifiable identity (who participated?)
- Conformance enforcement is needed (did agents follow the protocol?)
- Authority delegation must be traceable and revocable
- Noisy communication channels may produce false-positive agent failures
- Byzantine agents may attempt to subvert governance

## Core Insight

PRIMUS answers three governance questions under adversarial conditions:
**who participated** (identity via prime-power encoding), **did they
conform** (enforcement via BLS aggregate signatures), and **who decides**
(authority via consensus tokens). A consensus token whose prime
factorization indexes participation enables O(1) participation verification.
The safe-kill threshold reduces false-positive agent termination from 80%
to 0.00% under 10% channel noise.

---

## Procedure

### 1. Assign Prime-Power Identities

Assign each agent a unique prime number as its identity:
- Agent_1 = 2, Agent_2 = 3, Agent_3 = 5, ...
- The consensus token is the product of participating agents' primes
- Factorizing the token reveals exactly which agents participated
- Non-participating agents' primes are absent from the factorization

### 2. Implement BLS Aggregate Signatures (PIAC)

For each governance decision or output:
1. Each participating agent signs the output with its BLS private key
2. Aggregate all signatures into a single compact signature
3. Verification confirms both the output integrity AND the exact
   set of participants (via prime-power identity coupling)
4. A single aggregate verification replaces N individual checks

### 3. Derive and Apply Safe-Kill Thresholds

Before terminating an agent for non-conformance:
1. Compute the channel noise estimate for the communication layer
2. Apply the safe-kill threshold: only terminate if the evidence
   of non-conformance exceeds the threshold adjusted for noise
3. Under 10% channel noise, this reduces false-positive termination
   from 80% to 0.00%
4. Log all near-threshold cases for human review

### 4. Compute Economic Governance Boundaries

Determine whether to use singleton governance or Byzantine consensus:
1. Below the economic boundary: singleton governance (one trusted
   verifier) is more cost-effective
2. Above the boundary: Byzantine fault-tolerant consensus is required
3. The boundary depends on: number of agents, adversary fraction,
   communication cost, and value at stake

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Prime collision | Same prime assigned to multiple agents | Maintain a central prime registry; use deterministic prime assignment |
| Consensus token overflow | Too many agents (large prime product) | Use big-integer arithmetic; partition into sub-federations |
| BLS key compromise | Agent's private key leaked | Implement key rotation; revoke compromised keys from aggregate |
| Channel noise underestimate | Actual noise exceeds estimated threshold | Periodically re-estimate noise; use conservative threshold |

## Sources

> Source: "PRIMUS: Identity, Governance, and Verification for Multi-Agent Federations" (arXiv:2609.07910)
