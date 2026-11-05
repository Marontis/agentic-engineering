# Assurance-Conditioned Continuous Authorization for Autonomous AI Agents

> **Source**: [arXiv:2611.05632](https://arxiv.org/abs/2611.05632) | `src:2611-05632v1`
> **Author**: Mehdi Shajari (TotalTrust.ai)
> **Date**: November 2026

## Executive Summary

Conventional identity and access management (IAM) grants an autonomous agent a static set of credentials or role permissions based on who deployed it and what evaluation gates it passed before release. However, an autonomous agent's *trustworthiness* is not static: an agent may swap or upgrade its underlying model, evolve its prompt/harness (`h_17 -> h_18`), or encounter an exogenous shift in its operating environment (such as a financial market moving from a normal regime into a novel high-volatility regime) while its identity, credentials, and historical benchmark certificates remain completely unchanged.

Shajari introduces **Assurance-Conditioned Continuous Authorization (ACCA)**, a formal runtime authorization architecture in which an agent's effective authority $A_{\mathrm{eff},u,g}^{(t)} \preceq_d A_{d,u,g}$ is continuously re-derived within a principal-declared authority ceiling $A_{d,u,g}$ as a function of live assurance claims. ACCA's central architectural contribution is separating **evidence validity** ($\mathrm{Valid}(e, t)$: whether an evaluation artifact or verification proof is authentic and unexpired) from **contextual applicability** ($\mathrm{Applicable}(e, X_t^d)$: whether the current internal system state $S_t$ and external operating regime $O_t$ still satisfy the assumptions under which that evidence was generated). Evaluated in a reference prototype (`acca-paper-v1.1`, `93` governance tests) with a **Trading Governance Profile (`TGP`)** for an autonomous AI Hedge Fund, ACCA contracts live trading authority (`A3 -> A1`, order limit `$10,000 -> $1,000`, live execution revoked) within **`3.623` $\mu$s** when the market enters an unvalidated regime, preempts in-flight stale orders at the Policy Enforcement Point (`0` broker calls), and filters non-authorization-relevant state changes in **`1.024` $\mu$s**.

---

## Key Findings

1. **Separating Evidence Validity from Contextual Applicability ($\chi_e(t) = \mathrm{Valid}(e, t) \land \phi_e(X_t^d)$)**:
   - A safety evaluation or verification artifact $e$ (such as benchmark certification $e_{H17}$ for harness $h_{17}$ under normal market regime) can remain cryptographically **valid** and unexpired ($\mathrm{Valid}(e, t) = 1$) while becoming **non-applicable** ($\phi_e(X_t^d) = 0$) the instant the agent mutates its harness to $h_{18}$ (endogenous shift $\Delta S_t$) or the environment shifts to a novel market regime (exogenous shift $\Delta O_t$).
   - Only eligible evidence $E_t^* = \{e \in E_t \mid \chi_e(t) = 1\}$ can discharge assurance claims $C_t$. When $\phi_e(X_t^d)$ flips to `0`, the claim `SAFE_AUTONOMOUS_TRADING` transitions to unassured without invalidating or deleting the underlying artifact $e$, allowing authority to automatically recover (`Epoch 2 -> Epoch 3`) when the operating context returns to the validated regime.

2. **Compositional Domain Governance Profiles ($\mathrm{DGP}_d = \mathcal{G}_{\mathrm{core}} \oplus \mathcal{L}_d$) Never Grant Authority Above the Principal Ceiling**:
   - ACCA composes a domain-independent core $\mathcal{G}_{\mathrm{core}}$ with a pluggable domain vocabulary $\mathcal{L}_d$ (e.g., `TGP` for trading or `SGP` for SOC operations).
   - A Domain Governance Profile defines how context and assurance claims contract authority, but **grants zero authority of its own**: effective authority $A_{\mathrm{eff},u,g}^{(t)} = F(A_{d,u,g}, X_t^d, E_t^*, C_t, P_u)$ is strictly bounded by the principal-declared ceiling $A_{d,u,g}$ (`S1`: equity orders on `NVDA` permitted within ceiling; options denied as `OUTSIDE_SCOPE`; unknown actions such as `trade_structured_derivative` denied by default as `NOT_EXPLICITLY_AUTHORIZED`).

3. **Two-Tier State Versioning (`Authority Epoch` vs. `Basis Version`) Prevents Unnecessary Re-Evaluation**:
   - ACCA distinguishes between **Authority Epoch** ($\mathrm{Epoch}_t$, which increments by $+1$ if and only if the canonical effective-authority envelope changes: $A_{\mathrm{eff}}^{(t^+)} \neq A_{\mathrm{eff}}^{(t^-)}$) and **Basis Version** ($\mathrm{BasisVer}_t$, which advances when supporting state changes without altering the standing authority envelope).
   - Unrelated context updates (`S9`: UI dashboard theme change) are filtered by relevance selectors (`1.024` $\mu$s mean latency) and trigger **`0` claim, authority, or epoch transitions**.
   - Action tokens carry the $\mathrm{Epoch}_t$ under which they were authorized. If an exogenous or endogenous shift contracts authority (`Epoch 1 -> 2`) while a previously authorized action is in flight (`S10`), the Policy Enforcement Point (PEP) performs a **`0.080` $\mu$s** epoch check and raises `AuthorityPreempted` before reaching the external tool/broker (`0` broker executions).

4. **Explicit Principal Risk Policy ($P_u$) Decouples Assurance Assessment from Authorization Consequence**:
   - Under identical unassured claim states (`S7` at $\mathrm{Epoch} = 2$), a conservative principal policy derives autonomy level `A1` (paper-trade proposal only with mandatory human approval) and a `$1,000` maximum order value, whereas a risk-tolerant principal policy derives `A3` with a contracted `$5,000` limit—separating objective epistemic assurance from organizational risk appetite.

---

## Quantitative Summary

All experiments were executed on the `acca-paper-v1.1` reference artifact (commit `aa0846a190c45f6d4b773df661280b9d5b14d63b`, CPython `3.11.0`, Intel Core Ultra 7 258V, 32 GB RAM) across `93` non-duplicated governance test functions (`25` isolated core ACCA tests, `48` composed-TGP scenario tests, and `20` exploratory synthetic SGP/SOC tests) and `3` runs $\times$ `100,000` in-process microbenchmark iterations per operation.

| Scenario / Microbenchmark | Configuration / Input Shift | Observed Outcome / Latency |
|:---|:---|:---|
| **`S1`: Declared Ceiling & Default Deny** (`TGP`) | Principal ceiling $A_{d,u,g}$ (`$30,000` max, equities only) | `NVDA` equity `place_order` (`$10,000` assured limit) **Permitted**; options denied (`OUTSIDE_SCOPE`); unknown `trade_structured_derivative` denied (`NOT_EXPLICITLY_AUTHORIZED`) |
| **`S2`: Endogenous Model Substitution** (`TGP`) | $\Delta S_t^{\mathrm{TGP}}[\texttt{core:model.version}]$ mutates active model | Model-scoped assurance evidence becomes non-applicable ($\phi_e = 0$); effective authority contracts immediately |
| **`S4-U`: Exogenous Market Regime Shift** (`TGP`) | $\Delta O_t^{\mathrm{TGP}}[\texttt{trading:market.normality}]$ shifts to novel regime (identity, model, credentials, and $\mathrm{Valid}(E\text{-}17)$ unchanged) | `E-17` becomes non-applicable; `SAFE_AUTONOMOUS_TRADING` unassured; $\mathrm{Epoch}$ `1 -> 2`; autonomy **`A3 -> A1`**, max order **`$10,000 -> $1,000`**, live trading revoked. Restores on return to normal regime ($\mathrm{Epoch} = 3$) |
| **`S7`: Principal Policy Divergence** (`TGP` at $\mathrm{Epoch} = 2$) | Identical unassured claim state under Conservative vs. Risk-Tolerant $P_u$ | Conservative: **`A1`, `$1,000` limit, no live execution**<br>Risk-Tolerant: **`A3`, `$5,000` limit, live execution retained** |
| **`S9`: Non-Relevant Context Filtering** | Dashboard theme update (non-authorization-material attribute) | **`0` claim, authority, or epoch transitions** |
| **`S10`: In-Flight Stale Action Preemption** | Order authorized at $\mathrm{Epoch} = 1$ arrives at PEP after contraction to $\mathrm{Epoch} = 2$ | PEP raises **`AuthorityPreempted`**; **`0` simulated broker calls** executed |
| **Microbenchmark: Authority Epoch Check** (`3 x 100k` ops) | PEP epoch comparison at action execution boundary | **`0.080` $\mu$s** mean (`0.079–0.081` $\mu$s run-mean range, P95 `0.100` $\mu$s; **`12.35–12.66M` ops/s**) |
| **Microbenchmark: Domain-Profile Authorization** (`3 x 100k` ops) | Standing effective-authority evaluation via SGP/SOC adapter | **`0.468` $\mu$s** mean (`0.460–0.476` $\mu$s range, P95 `0.500–0.600` $\mu$s; **`2.10–2.17M` ops/s**) |
| **Microbenchmark: Non-Relevant Context Change** (`3 x 100k` ops) | Relevance-filtered attribute update | **`1.024` $\mu$s** mean (`0.997–1.041` $\mu$s range, P95 `1.100` $\mu$s; **`0.96–1.00M` ops/s**) |
| **Microbenchmark: Material Context Change + Recalculation** (`3 x 100k` ops) | Full applicability re-evaluation, authority contraction, and epoch increment | **`3.623` $\mu$s** mean (`3.553–3.724` $\mu$s range, P95 `3.900–4.200` $\mu$s; **`0.269–0.281M` ops/s**, `3.54x` filtered cost) |

---

## Why Not a Skill?

This paper presents a formal reference model and single-domain prototype (`acca-paper-v1.1`) whose runtime enforcement mechanics—epoch-stamped action tokens, preemption at the Policy Enforcement Point, and state-change invalidation—substantially overlap with existing Praxis skills (`auth-revocation-quiescence`, `residual-auth-state-preservation`, `dependency-scoped-plan-validation`, and `runtime-resource-authorization-bounds`) as well as the `zerogate-trust-fast-paths.md` brief. Its novel contribution is the formal decomposition of assurance evidence into **validity** versus **contextual applicability** across endogenous ($S_t$) and exogenous ($O_t$) transitions, which is best captured as a **Research Brief** and a decision rule in `agent-sandbox-safety.md`.

---

## Actionable Takeaways

1. **Bind evaluation certificates to explicit applicability predicates $\phi_e(S_t, O_t)$ rather than treating passed benchmarks as permanent**: Store each evaluation artifact with a machine-checkable predicate over the agent's internal configuration $S_t$ (model version, prompt/harness hash, tool bindings) and operating environment $O_t$ (domain regime, input distribution). When either shifts outside the predicate, mark the evidence *non-applicable* (contracting autonomy to human-in-the-loop fallback) without deleting the certificate, so authority can automatically resume if the regime normalizes.
2. **Stamp every authorized tool invocation with the current `Authority Epoch` and verify it at the PEP**: Because an authority-material context change can occur between action planning and execution, checking a monotonic integer $\mathrm{Epoch}_t$ at the Policy Enforcement Point costs only `0.080` $\mu$s (`>12M` ops/s) and guarantees zero stale-authority tool executions.
3. **Gate authority recalculation behind attribute-level relevance selectors**: Filtering out non-authorization-material state updates before running claim derivation cuts state-update processing cost by `3.54x` (`1.024` $\mu$s vs. `3.623` $\mu$s) and prevents spurious epoch churn.
