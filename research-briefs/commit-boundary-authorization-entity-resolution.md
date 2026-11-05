# Constraining the Commit Boundary for Agentic Entity Resolution

> **Paper**: [Constraining the Commit Boundary: A DIO/ODI-Informed Authorization Guardrail for Agentic Entity Resolution](https://arxiv.org/abs/2610.37407) (Beranek, Oct 2026)
> **Praxis source**: `src:2610-37407`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

This paper is an **unimplemented conceptual architecture and specification with no empirical validation, benchmark experiments, or runtime measurements**. As the author explicitly states, the work defines formal governance obligations and interface contracts at the graph commit boundary rather than reporting an implemented or empirically tested system. In accordance with Praxis triage standards, unvalidated architectural proposals are documented as research briefs rather than actionable skills, while their structural design patterns are cross-referenced against our empirically backed provenance and commit-gate skills ([`dependency-scoped-plan-validation`](../skills/dependency-scoped-plan-validation/SKILL.md), [`governed-knowledge-graph`](../skills/governed-knowledge-graph/SKILL.md), and [`mcp-decode-provenance-binding`](../skills/mcp-decode-provenance-binding/SKILL.md)).

---

## Core Concept

In sequential **Agentic Entity Resolution (ER)** (`Plan` $\to$ `Act` $\to$ `Observe` $\to$ `Update Beliefs`), an autonomous agent resolves ambiguous real-world identity records across fragmented sources and commits merge, split, or attribute-update mutations to a shared production identity graph $G_{\mathrm{prod}}$.

Beranek highlights an epistemic failure mode termed **apparent verification**: once an early erroneous identity hypothesis enters the agent's belief state $s_t$, it conditions subsequent retrieval queries $a_t$. The returned observations $o_{t+1}$ are selected from the neighbourhood of that hypothesis and therefore appear locally consistent with $s_t$ ($\|\operatorname{Project}(o_{t+1}) - \operatorname{Expectation}(s_t)\| \to 0$), reinforcing the mistaken entity merge even when global graph invariants are violated.

Rather than attempting to restrict what the LLM Planner can read or hypothesize during exploratory reasoning, the proposed **Minimum Viable Digital Identity Optimization (MVDIO) Supervisor Layer** constrains the **commit boundary** by enforcing a strict separation between **reasoning-eligible evidence** and **authorization-eligible evidence**:

1. **Quarantine vs. Planner-Visible vs. Authorization-Eligible Evidence Pools**:
   - Newly retrieved observations first land in `QUARANTINE_EVIDENCE` ($P_{\mathrm{quar}}$).
   - After passing basic structural admission checks (`CheckAdmissionConflict`), records enter the Planner-visible pool $P_{\mathrm{active}}$ with mandatory status **`UNVERIFIED`**.
   - **Core Commit Invariant**: Admission of a record to $P_{\mathrm{active}}$ as `UNVERIFIED` permits the Planner to reason over it and formulate hypotheses, but **never confers authorization eligibility** to justify a production graph write.
2. **Domain-Governed Constraint Binding ($\mu_\Omega : \mathcal{C}_{\mathrm{DIO/ODI}} \rightharpoonup \mathcal{V}_E$)**:
   - Maps Digital Identity Optimization / Open Digital Identity (DIO/ODI) **Reconstruction Failure Modes** into versioned, domain-configured verification constraints $V_E^{(v_{\mathrm{pol}})}$:
     - *Referential Reconstruction Failures*: Merge Failure, Split Failure, Entity Substitution, Entity Omission.
     - *Semantic Coherence Failures*: Semantic Fragmentation.
     - *Temporal Reconstruction Failures*: Temporal Discontinuity, Temporal Misalignment.
     - *Contextual Adequacy Failures*: Contextual Displacement.
3. **Action Classification and Fail-Closed Default**:
   - Every candidate operation is classified into `READ`, `STAGE_LOCAL`, `REVERSIBLE_WRITE` (isolated staging writes restricted to a shadow graph $G_{\mathrm{shadow}}$), or `IRREVERSIBLE_WRITE` (mutations affecting shared production state $G_{\mathrm{prod}}$). Any action with ambiguous scope defaults fail-closed to `IRREVERSIBLE_WRITE`.
4. **Claim-Specific Promotion Contract ($P_{\mathrm{auth}}(q_m, \omega) \subseteq P_{\mathrm{active}}$)**:
   - For a proposed mutation $m$, the supervisor derives the required proposition set $q_m := \operatorname{DeriveRequiredClaims}(m, V_E, v_{\mathrm{pol}})$ in observation domain $\omega = (O, C, t)$.
   - Evidence in $P_{\mathrm{active}}$ can be promoted into $P_{\mathrm{auth}}(q_m, \omega)$ only by satisfying a deterministic, auditable promotion contract that explicitly rejects: (i) internal Planner confidence scores, (ii) LLM-generated `"verified"` strings, (iii) non-independent corroboration derived from the same hypothesis-conditioned query lineage, and (iv) unpromoted claims staged only in $G_{\mathrm{shadow}}$.
5. **Two-Phase Commit Validation with Version Binding (Algorithms 1 & 2)**:
   - **Phase 1 (Pre-execution authorization)**: Verifies $P_{\mathrm{auth}}(q_m, \omega)$ against $q_m$ and issues an authorization token $\alpha_m$ bound to the exact mutation scope and a 4-tuple of state versions $(v_{\mathrm{pol}}, v_G, v_E, v_S)$ (policy version, production graph version, evidence-pool version, and schema version).
   - **Phase 2 (Post-execution commit gate)**: Acquires an `AtomicSnapshot` $\sigma_c$, checks `ScopeValid(m, \alpha_m)` and `VersionsValid(\alpha_m, \sigma_c)` (any concurrent change to $P_{\mathrm{active}}$, $P_{\mathrm{quar}}$, or promotion status increments $v_E$ and forces `RETRY_REEVALUATE`), and evaluates $\operatorname{EvaluateGraphConstraints}(G_{\mathrm{shadow}}, V_E^{(v_{\mathrm{pol}})})$ under precedence `BREACH` $>$ `UNKNOWN_EVIDENCE` $>$ `PASS`. Both `BREACH` and `UNKNOWN_EVIDENCE` fail closed (`REJECT` or `DEFER_UNRESOLVED` / `HALT_HITL`).

---

## Relevance to Praxis

- **Separating reasoning visibility from write authorization (`rules/agent-sandbox-safety.md`, `rules/adk-workflow-architecture.md`)**: Provides a clean conceptual model for knowledge-graph and database agents: let the planner read and hypothesize over `UNVERIFIED` retrieved records in a shadow workspace ($G_{\mathrm{shadow}}$), but gate `IRREVERSIBLE_WRITE` commits on an independent, claim-specific promotion check that rejects LLM self-attestation and hypothesis-conditioned circular corroboration.
- **Empirical counterparts in Praxis**: For implemented and empirically validated procedures that enforce these principles at runtime, use:
  - [`governed-knowledge-graph`](../skills/governed-knowledge-graph/SKILL.md) (MAGG, `arXiv:2608.28642`) for multi-agent knowledge-graph admission review and provenance governance.
  - [`dependency-scoped-plan-validation`](../skills/dependency-scoped-plan-validation/SKILL.md) (PlanFence, `arXiv:2609.03340`) for validating versioned memory dependencies ($v_E, v_G$) before committing pending tool actions.
  - [`mcp-decode-provenance-binding`](../skills/mcp-decode-provenance-binding/SKILL.md) (`arXiv:2610.31974`) and [`provenance-capability-grants`](../skills/provenance-capability-grants/SKILL.md) (ToolFence, `arXiv:2609.37196`) for cryptographic lineage verification and audited `trusted_promotion` at critical tool sinks.
