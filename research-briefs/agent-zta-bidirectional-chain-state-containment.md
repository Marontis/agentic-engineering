# Agent-ZTA: Bidirectional Chain-State Propagation and Branch-Scoped Containment

> **Paper**: [Agent-ZTA: A Chain-Aware Zero Trust Model for Bidirectional Security-State Propagation and Runtime Containment in Multi-Agent Delegation](https://arxiv.org/abs/2611.18999) (Khan & Syed, 2026)
> **Praxis source**: `src:2611-18999v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Summary

Khan and Syed formalize **Agent-ZTA**, a chain-aware Zero Trust authorization model for multi-agent delegation graphs $G = (V, \mathcal{L})$ where intermediate agents delegate sub-tasks along an authenticated path $\pi = (v_0, v_1, \dots, v_k = i)$ and security posture changes *mid-workflow* while previously issued delegation credentials remain cryptographically valid and unexpired.

Conventional token-attenuation schemes bind a static structural ceiling along $\pi$, but treat upstream and downstream posture as static once a token is minted: if an upstream delegator $v_j$ becomes degraded or compromised after delegating to $i$, or if a downstream sub-agent $C$ triggers a security anomaly inside one delegated branch $\gamma$, point-in-time checks either over-trust the stale grant or globally revoke the parent agent across all unrelated active branches. Agent-ZTA resolves both failure modes by separating **static path-specific delegated authority** from **dynamic security-state-conditioned effective authority**, propagating accepted security events **bidirectionally** along policy-relevant chain slices, failing closed on missing or stale state records, and confining downstream anomalies via **branch-scoped containment modes (`normal`, `restricted`, `jail`)**.

> **Empirical Status Note**: As explicitly stated by the authors across `§IV-H`, `§V-C`, `Table I`, `§VII-E`, and `§VIII`, Agent-ZTA is a formal authorization and containment specification verified through **analytical property proofs and worked predicate traces**, with **zero live runtime benchmarks, latency measurements, or empirical attack-containment experiments**.

---

## Formal Architecture & Decision Model

### 1. Static Delegated Bound vs. Dynamic Effective Authority (`Eq. 1–5`)

For an action universe $\mathcal{A}$ and per-edge delegation scopes $C_{u,v} \subseteq \mathcal{A}$, every authorization query $q = (i, a, c, t, \pi)$ is evaluated relative to its **authenticated active delegation path** $\pi = (v_0, \dots, v_k = i)$—permissions from distinct paths to $i$ are never merged:

- **Static Path-Specific Delegated Bound**:
  $$D_i^\pi \subseteq \bigcap_{j=1}^{k} C_{v_{j-1}, v_j}$$
- **Principal Security-State Vocabulary**: Each principal $v$ carries a runtime security state $S_v(t) \in \{\mathrm{normal}, \mathrm{degraded}, \mathrm{compromised}, \mathrm{unavailable}\}$.
- **Operation-Specific Upstream Relevance**: Rather than forcing every low-risk read to depend on every historical ancestor, policy selects the operation-relevant ancestor subset $R_\pi(i, a, c, t) \subseteq \operatorname{Anc}_\pi(i)$, yielding the relevant upstream state view $\Sigma_{i,\pi}(a, c, t) = \{(v, S_v(t)) : v \in R_\pi(i, a, c, t)\}$.
- **Dynamic Effective Authority Invariant**: At time $t$ in context $c$, effective authority is strictly bounded by static delegation:
  $$E_i^\pi(t, c) \subseteq D_i^\pi$$

### 2. Bidirectional Propagation & Branch-Scoped Containment (`Eq. 6–8`)

When a validated runtime event $e = (v, \gamma, s, \tau, \rho)$ is accepted for workflow/branch identifier $\gamma$, policy computes its impacted chain slice $\mathcal{I}_P(e, \pi, a, c) \subseteq \{v\} \cup \operatorname{Anc}_\pi(v) \cup \operatorname{Desc}_\pi(v)$ and updates the branch-condition record $T_\gamma(t)$:

- **Upstream-to-Downstream Restriction**: If an ancestor $u \in R_\pi(i, a, c, t)$ shifts to `degraded` or `compromised`, downstream actions at $i$ that depend on $u$'s assurance ($H_P(u, i, \pi, c, \widehat{S}_u)$) are immediately narrowed or denied, even though $i$'s local state and token signature remain valid.
- **Downstream-to-Upstream Branch Tainting (Without Global Parent Revocation)**: If a leaf executor $C$ exhibits suspicious or compromised behavior in branch $\gamma$, $T_\gamma(t)$ taints the dependent parent workflow context $\gamma$—blocking or restricting parent $B$'s continuation or trust in outputs from $\gamma$—**without** marking $B$ globally `compromised` on an unrelated sibling branch $\delta \notin \mathcal{I}_P(e, \pi', a', c')$.
- **Three Branch Containment Modes**: A deterministic mode selector $M_\gamma(t) = \mu_P(T_\gamma(t)) \in \{\mathrm{normal}, \mathrm{restricted}, \mathrm{jail}\}$ maps $\gamma$ to allowed action set $C_P(\gamma, c, t)$:
  - `normal` $\to \mathcal{A}$ (no extra branch restriction beyond principal/chain policy);
  - `restricted` $\to Q_P(\gamma, c) \subseteq \mathcal{A}$ (e.g., revoking sensitive writes while retaining bounded reads);
  - `jail` $\to J_P(\gamma, c) \subseteq Q_P(\gamma, c)$ (excluding sensitive writes, external network calls, and further sub-delegation—potentially $\varnothing$—paired with an actual OS/container sandbox boundary when process/filesystem isolation is required).

### 3. Fail-Closed Snapshot Rules & Six-Step PEP/PDP Procedure (`§VI-C–D`, `Eq. 15–16`)

Between the **Policy Enforcement Point (PEP)** on the tool/message boundary and the **Policy Decision Point (PDP)**:
1. **Authenticate & Bind**: Verify caller $i$ and active delegation path $\pi$.
2. **Check Static Ceiling**: Verify $a \in D_i^\pi$; otherwise `Deny`.
3. **Select Relevant Ancestors**: Compute $R_\pi(i, a, c, t) \subseteq \operatorname{Anc}_\pi(i)$.
4. **Evaluate Freshness & Fail-Closed Snapshot**: Read $(\widehat{S}_v, T_\gamma(t))$. Any required state record that is missing, unverifiable, or older than its freshness window (`now - timestamp > max_age`) MUST be classified as **`unavailable`** (never defaulted to `normal`), and `unavailable` required state evaluates fail-closed to `Deny`.
5. **Evaluate Conjunctive Authorization Predicate (`Eq. 16`)**:
   $$\operatorname{Permit}(q) \iff a \in D_i^\pi \;\land\; a \in C_P(\gamma, c, t) \;\land\; B_P(i, a, c) \;\land\; a \in L_P(i, c, \widehat{S}_i) \;\land\; \bigwedge_{v \in R_\pi(i,a,c,t)} \bigl[a \in H_P(v, i, \pi, c, \widehat{S}_v)\bigr]$$
6. **Per-Request PEP Enforcement**: Enforce `Permit`/`Deny` for the single request $q$ only; a prior `Permit` never grants standing authority for subsequent calls.

### 4. Analytical Security Properties & Worked Trace (`Table I`, `§VII`)

On the worked 4-principal chain $U \to A \to B \to C$ with $D_C^\pi = \{\mathrm{read}, \mathrm{write}\}$ (`Table I`, `6` policy cases):
- `normal` states + branch `normal` permit `read`; `B = degraded` denies `write` while permitting `read` when $B \notin R_\pi(C, \mathrm{read}, c, t_3)$; `A = compromised` denies `write`; downstream anomaly on $\gamma$ drives $M_\gamma = \mathrm{jail}$ (`Deny` on `write` in $\gamma$), while parent $B$ on unrelated clean branch $\delta$ (`normal`) retains `Permit` on `read`.
- The specification proves five policy-relative properties: **(1) Non-escalation** ($\widehat{E}_i^\pi \subseteq D_i^\pi$), **(2) Conditional downstream restriction** (plus monotone contraction under optional trust ordering $S'_u \preceq_{\mathrm{trust}} S_u$), **(3) Request-bound PEP enforcement**, **(4) Conservative fail-closed handling of `unavailable` state**, and **(5) Branch-local containment isolation**.

---

## Practical Design Rules

1. **Keep Static Token Attenuation and Dynamic Chain-State Evaluation Distinct**: Cryptographic scope attenuation ($D_i^\pi$) bounds what *could ever* be allowed on path $\pi$, while runtime PDP checks ($E_i^\pi(t, c)$) intersect that ceiling with live ancestor security states and branch containment mode on every side-effecting call.
2. **Propagate Downstream Compromise to the Branch Context (`T_\gamma`), Not Globally to the Parent Principal**: Tainting $\gamma$ into `restricted` or `jail` mode stops poisoned child outputs and blocks further delegation inside the affected workflow without causing self-inflicted denial-of-service across a coordinator's unrelated healthy branches.
3. **Treat Stale or Missing Ancestor Posture as `unavailable -> Deny`**: Never silently fall back to cached `normal` posture when telemetry or state-bus heartbeats time out on a security-relevant ancestor.

---

## Why Not a Skill?

Agent-ZTA is a clean formal authorization calculus and architectural reference model, **not** an empirically validated implementation or operational algorithm: the paper conducts zero experiments, defines no concrete cryptographic wire format, leaves anomaly detection and distributed state-synchronization protocols out of scope, and notes that `jail` mode is only a policy state unless backed by an external sandbox runtime. In our knowledge base, concrete multi-hop cryptographic wire verification is already covered as an executable procedure by [`multi-hop-delegation-auth-propagation`](../skills/multi-hop-delegation-auth-propagation/SKILL.md) (`arXiv:2611.07050`), provenance-weighted permission intersection by [`principal-context-permission-intersection`](../skills/principal-context-permission-intersection/SKILL.md) (`Conflux`, `arXiv:2611.08768`), and cross-layer runtime compromise detection by [`multi-layer-compromise-filtering-and-traceback`](../skills/multi-layer-compromise-filtering-and-traceback/SKILL.md) (`Swarm Shepherd`, `arXiv:2611.18693`). Agent-ZTA's distinct contribution—bidirectional chain-state propagation, fail-closed `unavailable` ancestor snapshots, and branch-scoped `jail` containment—is captured here and distilled into our multi-agent coordination rules.

---

## Related Artifacts

- **Rule**: [Multi-Agent Coordination](../rules/multi-agent-coordination.md)
- **Rule**: [Agent Sandbox Safety](../rules/agent-sandbox-safety.md)
- **Skill**: [Multi-Hop Delegation Authorization Propagation](../skills/multi-hop-delegation-auth-propagation/SKILL.md)
- **Skill**: [Principal-Context Permission Intersection](../skills/principal-context-permission-intersection/SKILL.md)
- **Skill**: [Multi-Layer Compromise Filtering and Traceback](../skills/multi-layer-compromise-filtering-and-traceback/SKILL.md)
- **Research Brief**: [ACCA: Assurance-Conditioned Continuous Authorization](acca-assurance-conditioned-continuous-authorization.md)
- **Research Brief**: [TRAP: Trust-Responsive Runtime Authorization](trap-trust-responsive-runtime-authorization.md)
