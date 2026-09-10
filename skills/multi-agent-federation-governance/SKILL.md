---
name: multi-agent-federation-governance
description: >
  Establish identity, governance, and verification protocols for
  multi-agent federations where agents from different organizations
  collaborate.  Covers DID-based identity, capability delegation,
  and cross-federation trust.
  Derived from PRIMUS (arXiv:2609.07910).
---

# Multi-Agent Federation Governance

Use this skill when building systems where agents from different
organizations or trust domains must collaborate while maintaining
identity and accountability.

## When to Use

- Agents from different providers need to collaborate on shared tasks
- You need verifiable agent identity (who is this agent? who deployed it?)
- You want capability delegation with revocation
- You're building cross-organization agent workflows

## Core Insight

Multi-agent federations without identity and governance devolve into
unaccountable swarms.  **PRIMUS** provides a protocol stack for
federated agent systems: decentralized identity (DIDs) for agents,
capability-based delegation with revocation chains, and verifiable
credentials for cross-federation trust.

## Procedure

### Step 1: Assign decentralized identities (DIDs)

Each agent in the federation receives a DID:

- **Agent DID**: A unique identifier tied to a cryptographic key pair
- **Operator DID**: The organization that deployed and controls the agent
- **Federation DID**: The federated group the agent belongs to

DIDs are self-sovereign — no central authority issues or revokes them.
The agent proves its identity by signing messages with its private key.

### Step 2: Define capability envelopes

For each agent, define what it's allowed to do:

| Capability | Scope | Delegation |
|:-----------|:------|:-----------|
| `read:documents` | Within federation | Can delegate to sub-agents |
| `execute:code` | Own sandbox only | Cannot delegate |
| `sign:transactions` | With operator approval | Cannot delegate |
| `communicate:external` | Approved endpoints only | Can delegate with scope reduction |

Capabilities are **object capabilities** — possession of the
capability token is sufficient to exercise it, with no ambient
authority.

### Step 3: Implement delegation chains

When Agent A delegates a capability to Agent B:

1. Agent A creates a delegation credential signed with its key
2. The credential specifies: capability, scope (equal or narrower),
   expiry, and revocation endpoint
3. Agent B can exercise the capability by presenting the chain:
   `[Federation → Operator → Agent A → Agent B]`
4. Any verifier can check the chain cryptographically

### Step 4: Cross-federation trust

When agents from different federations interact:

1. Each federation publishes its trust policy (what capabilities
   it recognizes from other federations)
2. Cross-federation requests include the full delegation chain
   from both sides
3. The receiving federation verifies the chain against its
   trust policy before granting access

### Step 5: Revocation and audit

- **Revocation**: Any entity in the delegation chain can revoke
  downstream delegations.  Revocation propagates immediately.
- **Audit log**: Every capability exercise is logged with the
  full delegation chain, timestamp, and result.
- **Expiry**: All delegations have mandatory expiry times.  No
  permanent delegations.

## Environment Caveats

- **Single-organization systems**: Full federation governance is
  overkill.  Use simpler role-based access with the
  `unified-capability-gateway` skill instead.
- **Latency-sensitive tasks**: Delegation chain verification adds
  latency.  Cache verified chains for short-lived tasks.
- **Key management**: Agent private keys must be protected.
  Use hardware security modules or secure enclaves for
  high-value agents.

## Failure Modes

- **Delegation chain explosion**: Deep delegation chains become
  hard to verify and audit.  Limit chain depth to 3–4 levels.
- **Revocation lag**: If revocation doesn't propagate instantly,
  revoked agents can still act.  Use short expiry times as a
  safety net.
- **Identity theft**: If an agent's private key is compromised,
  the attacker can impersonate it.  Implement key rotation and
  anomaly detection on agent behavior.

## Cross-References

- [`unified-capability-gateway`](../unified-capability-gateway/SKILL.md) —
  CrabOS handles capability routing within a single system;
  federation governance handles cross-organization trust
- [`governed-knowledge-graph`](../governed-knowledge-graph/SKILL.md) —
  Knowledge governance tracks provenance and ownership;
  federation governance tracks identity and delegation

## Sources

- PRIMUS: Identity, Governance, and Verification for Multi-Agent Federations (arXiv:2609.07910)
