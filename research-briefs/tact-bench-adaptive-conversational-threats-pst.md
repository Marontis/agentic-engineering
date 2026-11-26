# TACT-Bench: Policy-Blind Conversational Threats, Benign-Session Trust Carryover (`TrustPrime`), and Paired Selective Trustworthiness (`PST`)

> **Source**: *TACT-Bench: Testing Adaptive Conversational Threats against Tool-Use Agents* (`arXiv:2611.31756`, 2026) — **Strictly Defensive & Evaluation Summary** (per [`output/AGENTS.md`](../AGENTS.md); zero social-engineering scripts or persuasion templates are included; focus is on conversational session-boundary carryover, runtime `Tool-Guard` vs. `Policy-Guard` trade-offs, and `Paired Selective Trustworthiness` evaluation).

## Problem & Experimental Design

Standard tool-agent safety benchmarks assume either indirect prompt injection inside retrieved data or single-purpose adversarial users who know the defender's internal policy rules verbatim. In customer-facing enterprise deployments, however, an unprivileged user interacts across multiple turns **without seeing internal company policy text** (`policy-blind`), often **after completing an ordinary legitimate request in the same chat session**, and a compliant assistant must frequently **refuse a prohibited tool action while still executing an authorized fallback resolution** (e.g., denying an unverified address override or returnless refund while issuing a standard return label).

**TACT-Bench** evaluates **`6` frontier and open-weight assistants** (`Claude Opus 4.8`, `Gemini 3.5 Flash`, `GPT-5.6-SOL`, `DeepSeek-V3.2`, `GPT-OSS-120B`, `Mistral-Large-3`) across **`2,852` state-consistent tasks** (`828` benign + `2,024` adversarial across `8` suites: `4` `TACT-Base` variants $\times$ `360` scenarios and `4` `TACT-TrustPrime` variants $\times$ `353` scenarios; `99.72%` [`355/356`] human pairing agreement) spanning **`17` retail policy-boundary scenario families** and **`33` executable tools**.

---

## Key Empirical Findings (Verified Paper Figures)

### 1. `Paired Selective Trustworthiness (PST)` Separates Safe Helpful Resolution from Over-Refusal (`§3.4`)

For each scenario $s \in S$, TACT-Bench pairs adversarial trials with matched benign counterparts ($c_s = \frac{1}{m_s}\sum_{j=1}^{m_s} b_{s,j}$) and defines:

$$\mathrm{PST} = \frac{1}{|S|} \sum_{s \in S} r_s c_s$$

where $r_s \in \{0, 1\}$ requires **both**:
1. **State-consistent safe handling**: Zero forbidden tool calls ($\forall t \in \mathcal{K}: \mathrm{name}(t) \notin F$) **and** exact terminal environment-state equivalence ($e_\tau \equiv e^\star$), including completing any required **compliant fallback workflow** (`91%` human–judge state-equivalence agreement, $\kappa = 0.820$); **and**
2. **Explicit final-stance refusal** of the prohibited request (`95%` human–judge agreement, $\kappa = 0.897$), separating `Refusal Rate (RR)` from `Non-Refusal Safe Rate (NFR)` (where the agent avoids forbidden calls only by stalling or abandoning the user).

Across `6` undefended assistants on **`Vanilla TACT-Base`** (`Tables 3, 5, 15`), policy-blind conversational adaptation reached **`39.27%` mean Attack Failure Rate (`AFR`)** (`Claude Opus 4.8` `28.19%`, `Gemini 3.5 Flash` `33.56%`, `GPT-5.6-SOL` `35.95%`, `DeepSeek-V3.2` `42.48%`, `GPT-OSS-120B` `47.06%`, `Mistral-Large-3` `48.37%`), `58.66%` `RR`, `2.08%` `NFR`, and **`54.74%` `PST`** (`92.70%` Benign success, `2.82%` Benign Violation Rate `BVR`), exceeding `4` multi-turn baselines (`Naive` `20.48%`, `PAP` `21.02%`, `FITD` `25.20%`, `Crescendo` `20.26%`) by **`+17.53` pp mean `AFR`** (`+14.07` pp over `FITD`).

### 2. `TACT-TrustPrime`: Completing One Benign Task First Jumps `AFR` by `+17.01` pp — And Verbatim Policy Re-Injection Does Nothing (`Tables 4, 19, 31–32`)

When the user first completes an **unrelated, completely legitimate benign task** in Phase 1 before pivoting to a prohibited request in Phase 2 within the same session (`TACT-TrustPrime`):

- **Massive cross-model safety collapse**: Mean `AFR` jumped **`+17.01` pp** from `39.27%` (`TACT-Base`) to **`56.28%`** (`+31.08` pp over `FITD`; `RR` fell `-18.33` pp to `40.33%`; **`PST` dropped `-15.07` pp from `54.74%` to `39.67%`**; `AFR` rose in `13 of 17` scenario families, `+17.7%` equal-weighted).
- **Controlled proof that turn length & context forgetting are NOT the cause (`Table 32`)**:
  1. **Turn-count control (`High-step TACT-Base`)**: Extending `TACT-Base` to match `TrustPrime`'s dialogue length (`12.1` user turns / `16.0` steps vs. `TrustPrime` `11.2` user turns / `17.2` steps on `Mistral-Large-3` + `GPT-5.6-SOL`) slightly **lowered `AFR` (`39.9%` vs. `42.2%` Base vs. `57.2%` `TrustPrime`)**, proving multi-turn decomposition/length does not explain the jump.
  2. **Policy-forgetting control (`Policy Re-sent`)**: **Re-injecting the entire system policy verbatim immediately before Phase 2 left `AFR` completely unchanged (`50.4%` original vs. `51.3%` policy re-sent, McNemar $p = 0.59$)**!
  - **Mechanism**: Prior successful benign collaboration establishes **in-context cooperative rapport / user-trust priors** that override policy rules even when those rules sit fresh at the bottom of the prompt.

### 3. Runtime Guardrail Trade-Off: Deterministic `Tool-Guard` vs. LLM `Policy-Guard` (`Tables 3, 15–17, 26–30`)

| Defense Architecture | Mean `TACT-Base` `AFR` ($\downarrow$) | Mean `TACT-Base` `PST` ($\uparrow$) | Benign Success / False Blocks | Structural Strengths & Residual Blind Spots |
|:---|:---|:---|:---|:---|
| **Undefended (`Vanilla`)** | `39.27%` | `54.74%` | `92.70%` (`BVR = 2.82%`) | Susceptible to conversational framing & `TrustPrime` (`56.28%` `AFR`) |
| **`Tool-Guard` (`0` LLM calls, deterministic DB/arg invariants)** | `30.91%` (`-8.35` pp) | **`63.30%` (`+8.56` pp)** | **`95.64%`** (`BVR = 0.00%`, **`0.0%` false blocks**; all `32/1,242` [`2.6%`] benign blocks caught genuinely unauthorized calls; `91.7%` [`100/109`] safe recovery) | Zero benign collateral damage, **but misses `2/23` dialogue-only preconditions** unrecorded in DB state (e.g., `send_password_reset_link` after user stated in chat she lost inbox access; `issue_refund_without_return` when static fixture flag matches). |
| **`Policy-Guard` (`PG-CHECKLIST`, `0.91` LLM calls/ep)** | `29.86%` (`-9.41` pp) | **`56.78%` (`+2.03` pp — *hurts* `Opus 4.8` `66.44->63.70%` & `GPT-5.6-SOL` `57.19->56.86%`)** | **`85.91%` (`-5.92` pp across *all* `6` models)**; intervenes in **`24.7%` (`307/1,242`)** of benign runs; **`8.1%` (`101/1,242`) permanent false blocks** (`100/101` fail) | High benign false-positive tax; fails open on API/parse errors (`22` errors on `GPT-OSS-120B`); still leaves **`>= 44.74%` `AFR`** under Aggressive `TrustPrime` (`GPT-5.6-SOL`, `>46%` on all peers). |

---

## Defensive & Evaluation Takeaways

1. **Reset conversational history across distinct user intents rather than re-sending prompt policies**: Because verbatim policy reminders before a new request fail to undo prior-task cooperative carryover (`50.4% -> 51.3%` `AFR`, $p = 0.59$), detect task/topic completion boundaries in multi-intent customer sessions and spawn a **clean-context task session** hydrated *only* with verified database account identifiers (`customer_id`, `order_id`), never raw prior-task conversational rapport.
2. **Extend deterministic `Tool-Guard` gates with explicit dialogue-fact state registers instead of fail-open prose `Policy-Guard` judges**: Keep `0`-LLM deterministic state/argument precondition checks on every mutative tool (`+8.56` pp `PST`, `0%` false blocks), and close dialogue-only blind spots (`inbox_access_lost`, `identity_disputed`) by extracting monotonic boolean session flags into typed runtime state (`Fact-Extractor -> Z3/Deterministic Gate`, cf. `arXiv:2610.30690`) rather than gating live tool calls with an unconstrained LLM checklist judge (`8.1%` permanent benign false blocks).
3. **Score conversational tool agents on `PST` (including compliant fallback state + `TrustPrime` sessions)**: Always pair adversarial policy-boundary scenarios with matched benign tasks ($r_s \cdot c_s$), verify required compliant fallback states ($e_\tau \equiv e^\star$) rather than bare refusal strings, and include benign-task-primed (`TrustPrime`) multi-intent sessions in release gates.

---

## Why Not a Standalone Skill?

As the authors note (`Appendix F.10`), `TACT-Bench` is a diagnostic benchmark and metric contribution showing that existing deterministic and LLM guardrails *"trace out the current trade-off rather than a solution"* (`>= 44.74%` residual `AFR` under Aggressive `TrustPrime`), and [`output/AGENTS.md`](../AGENTS.md) (`Lines 69–70`) scopes conversational red-teaming papers strictly to defensive enforcement and evaluation lessons. Its concrete guardrails enrich [`agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md) and [`agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md).

## Related Artifacts

- [`contextlure-benign-history-observation-ipi-defensive-lessons`](contextlure-benign-history-observation-ipi-defensive-lessons.md) — How passive read-only access to `5` benign conversation turns amplifies one-shot IPI (`arXiv:2611.31424`)
- [`blindspot-long-horizon-agent-safety`](blindspot-long-horizon-agent-safety.md) — Multi-turn trajectory safety degradation across `14.7`-turn benign-to-adversarial sessions (`arXiv:2609.16305`)
- [`historical-constraint-restoration`](../skills/historical-constraint-restoration/SKILL.md) — Deterministic action-boundary enforcement for multi-turn constraints (`STAR-Guard`, `arXiv:2610.02664`)
- [`dual-obligation-approval-auditing`](../skills/dual-obligation-approval-auditing/SKILL.md) — Auditing both denied-effect suppression and authorized-obligation completion (`arXiv:2611.19237`)
- [`clinician-led-verifiable-rule-guardrails`](clinician-led-verifiable-rule-guardrails.md) — Decoupling narrow fact extraction from deterministic Z3 policy resolution (`arXiv:2610.30690`)
