---
name: multi-hop-delegation-auth-propagation
description: >-
  Propagate and verify transitive authorization across multi-hop Agent2Agent
  (A2A) workflows using four layered defenses: current-caller passports,
  origin-bound authorization evidence, per-hop Ed25519 request envelopes with
  separated replay domains, and monotonic scope attenuation. Derived from Donno
  et al. (arXiv:2611.07050).
source: https://arxiv.org/abs/2611.07050
license: CC-BY-4.0
repository: https://github.com/Marontis/agentic-engineering
---

# Multi-Hop Delegation Authorization Propagation

> **Source**: [Authorization Propagation in Agent2Agent Systems: An Experimental Security Evaluation of Multi-Hop Delegation](https://arxiv.org/abs/2611.07050) (Donno et al., 2026) | Praxis: `src:2611-07050v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

- Designing or securing multi-agent workflows (such as Agent2Agent / A2A pipelines) where a client request traverses one or more intermediate agents ($U \to P \to H \to I$) before a downstream executor performs a privileged or financial action.
- Upgrading point-to-point agent authentication (such as mTLS, API keys, or A2A Secure Passport `CallerContext`) so downstream verifiers can validate both the immediate hop sender and the original upstream delegation authority.
- Preventing confused-deputy attacks, intermediate scope expansion, cross-hop message tampering, and replay attacks across multi-party agent boundaries.

## Overview

In multi-hop Agent2Agent (A2A) workflows, authenticating only the immediate upstream caller is insufficient: a downstream executor (such as an Insurance Agent $I$ in a 4-party healthcare reimbursement chain $U \to P \to H \to I$) must verify that the immediate sender ($H$) is authentic, that the request payload was not modified in transit, that the delegation path matches an unexpired authorization issued by the workflow origin ($U$), and that no intermediate agent expanded the delegated permissions.

Donno et al. implemented and benchmarked four progressive A2A security configurations (`C0` baseline A2A, `C1` current-caller context, `C2` transitive authorization evidence, and `C3` per-hop signed request envelopes) on Python `3.14.6` with A2A SDK `1.0.0a0` and `cryptography 46.0.5`. Their experimental evaluation across `400` benign runs and `500` adversarial runs (`15` adversarial conditions across `5` attack families) demonstrates:

1. **Layered Defense Coverage**: The full `C3` stack accepts `100%` of benign runs while rejecting `14/15` isolated adversarial conditions and `100%` of the `500` repeated adversarial runs, adding only **`5.1149 ms` (`5.11 ms`) median end-to-end latency** (P95 `13.2127 ms` vs. `0.0195 ms` in `C0`) and growing the message payload from `513 B` (`C0`) to `3,870 B` (`3.87 kB`, `+3,357 B`). Invalid requests fail fast in `0.0155 ms` (modified request text) to `1.8038 ms` (request replay).
2. **Two Critical Trust-Boundary Pitfalls Exposed by Experimental Testing**:
   - *Structural Path Verification vs. Semantic Scope Attenuation*: Checking only that the participant sequence $D$ is structurally valid ($\textsf{VerifyPath}(D) = 1$) allowed the `1/15` unblocked isolated condition—where an intermediate hop appended `approve_reimbursement` to the Patient-to-Hospital delegation scope—because structural path checks do not verify $Scope_{i+1} \subseteq Scope_i$.
   - *Shared-HMAC Intermediary Privilege Escalation*: When transitive authorization evidence $E_A$ is protected by a symmetric key $K_A$ shared across workflow participants, an authorized intermediate agent (Hospital Agent $H$) holding both its legitimate Ed25519 hop key and $K_A$ can escalate `max_amount` from `EUR 120` to `EUR 9000`, recompute $H(A)$ and $\operatorname{HMAC}_{K_A}(E_A)$, re-sign the `C3` hop envelope, and pass every `C1–C3` check ($\text{valid HMAC} \Rightarrow \text{holder of } K_A \not\Rightarrow \text{unchanged from origin}$).

---

## Step-by-Step Implementation Procedure

### Layer 1: Authenticate the Direct Hop Caller (`C1` — Current-Caller Context)

1. **Attach a Signed `CallerContext` to Every Hop**:
   - Populate an A2A Secure Passport v1 `CallerContext` containing the immediate sender's `clientId`, optional `sessionId`, and a mandatory Ed25519 signature over the canonicalized context state.
   - At each receiving agent, resolve the verification key Strictly from `CallerContext.clientId` against a local trusted registry and verify $\textsf{VerifyContext}(C_i)$ before parsing downstream business fields.
   - Treat `C1` strictly as **single-hop caller authentication** (adds `1.0688 ms` median latency and `+483 B` payload over `C0`); never use `CallerContext` alone to infer origin authorization across multiple hops.

---

### Layer 2: Bind Transitive Authorization Evidence with Origin-Only Asymmetric Signatures (`C2+`)

1. **Construct the Transitive Authorization Evidence Object ($E_A$)**:
   - At the workflow origin $id_o$, construct $E_A = (id_o, H(C_o), H(A), D, t_{iat}, t_{exp}, n_A, v)$ containing:
     - $id_o$: the originating principal identifier.
     - $H(C_o)$: the SHA-256 digest of the origin's initial `CallerContext`.
     - $H(A)$: the SHA-256 digest of the canonicalized structured authorization object $A$ (specifying maximum monetary/resource limits such as `max_amount`, `beneficiary`, `coverage`, `treatment`, and `permitted_actions`).
     - $D$: the ordered delegation path sequence $(d_1, \dots, d_k)$ specifying each hop's `from`, `to`, and delegated `scope`.
     - $[t_{iat}, t_{exp}]$: explicit issuance and expiration timestamps.
     - $n_A$: a unique workflow authorization nonce.
     - $v$: the evidence schema version.

2. **Sign $E_A$ with an Origin-Private Asymmetric Key or Attenuable Capability Chain (Never a Shared Group HMAC)**:
   - Do **not** authenticate $E_A$ with a symmetric HMAC key $K_A$ shared among intermediate agents. As proved by the Hospital Agent escalation test (`EUR 120` $\to$ `EUR 9000`), any insider holding $K_A$ can forge arbitrary origin terms $A'$ and recompute a valid $\operatorname{HMAC}_{K_A}(E_A)$.
   - Instead, sign the root authorization commitment $(id_o, H(C_o), H(A), t_{iat}, t_{exp}, n_A)$ with the origin principal's private Ed25519 key $sk_o$ (so intermediates have only the public verification key $pk_o$), and either:
     - Require each hop $i$ to append an asymmetrically signed delegation statement $\sigma_{D,i}$ over $(d_i, H(E_A))$, or
     - Use chained attenuable capability tokens (such as Macaroons or chained HMAC caveats) where each intermediate hop derives a restricted child key $k_{i+1} = \operatorname{HMAC}_{k_i}(\text{caveat}_{i+1})$ and destroys $k_i$, making upward privilege modification computationally infeasible.

---

### Layer 3: Wrap Each Hop in a Per-Hop Ed25519 Signed Request Envelope (`C3`)

1. **Bind Transport, Payload, and Metadata at Every Hop**:
   - For every direct transmission $i \to j$, wrap the message in a per-hop envelope $S_{ij} = (sender_i, receiver_j, msgID, t_R, n_R, H(text), H(metadata))$ signed with the immediate sender's private Ed25519 key $\sigma_i = \operatorname{Sign}_{sk_i}(S_{ij})$.
   - Compute $H(metadata)$ over the canonical JSON serialization of all structured business payloads, the structured authorization object $A$, the current `CallerContext` $C_i$, the transitive authorization evidence $E_A$, and intermediate provenance records (while excluding `request_signature` itself to avoid circular hashing).

2. **Maintain Independent Replay State Sets for Hop Envelopes and Workflow Authorizations**:
   - Enforce $n_R \neq n_A$ and maintain two separate replay caches at the verifier: a per-hop request nonce set $R_R$ and a workflow authorization nonce set $R_A$ ($R_R \cap R_A = \emptyset$).
   - Verify $t_R$ freshness and $n_R \notin R_R$ during `C3` transport verification, and verify $t_{iat} \le t_{now} \le t_{exp}$ and $n_A \notin R_A$ during `C2` authorization verification.
   - **Defer nonce consumption until all verification layers pass**: commit $n_R$ to $R_R$ and $n_A$ to $R_A$ only after `C3`, `C1`, and `C2` checks all succeed. Consuming $n_A$ before full verification allows an attacker to burn a valid workflow authorization nonce by injecting a malformed outer hop envelope.

---

### Layer 4: Enforce Fail-Closed Cross-Object Consistency and Monotonic Scope Attenuation

Execute all four cross-object invariants at the downstream verifier before invoking any business logic or tool execution:

1. **Hop-to-Context Identity Binding**: Verify that the authenticated `C3` envelope `sender_i` exactly equals `CallerContext.clientId`.
2. **Recipient-to-Delegation Terminal Binding**: Verify that the `C3` envelope `receiver_j` equals both the current verifier's identity and the final destination `to` of the delegation path $D$ ($\text{last}(D).\text{to} == receiver_j$).
3. **Payload-to-Evidence Commitment Binding**: Recompute $H(A')$ from the carried structured authorization object $A'$ and verify $H(A') == H(A)$ inside the origin-signed $E_A$, plus confirm that the requested business action parameters (such as reimbursement amount, beneficiary, and treatment) satisfy the bounds in $A'$.
4. **Monotonic Scope Attenuation Across All Hops**: Iterate through every hop $m \in \{1, \dots, k-1\}$ in the delegation path $D$ and enforce $Scope_{m+1} \subseteq Scope_m \subseteq \text{OriginPermittedActions}(A)$, rejecting any path where an intermediate hop introduces a permission (such as `approve_reimbursement`) absent from its parent grant.

---

## When NOT to Use

- **Single-agent or single-hop client-to-tool calls**: When a user or orchestrator calls a stateless tool directly with no intermediate agent delegation ($U \to T$), standard single-hop authentication (`C1` or mTLS) plus request signing is sufficient without multi-hop delegation path verification.
- **Unstructured conversational brainstorming among peer agents**: When peer agents exchange non-authoritative text drafts and no downstream agent executes state-mutating, financial, or privileged tool actions on behalf of an upstream principal.

---

## Related Artifacts

- **Rule**: [Multi-Agent Coordination](../../rules/multi-agent-coordination.md)
- **Rule**: [Agent Sandbox Safety](../../rules/agent-sandbox-safety.md)
- **Research Brief**: [TRAP: Trust-Responsive Runtime Authorization](../../research-briefs/trap-trust-responsive-runtime-authorization.md)
- **Skill**: [Sealed Replayable Agent Audit Log](../sealed-replayable-agent-audit-log/SKILL.md)
