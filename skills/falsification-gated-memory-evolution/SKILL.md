---
name: falsification-gated-memory-evolution
description: >
  Gate post-episode agent memory and behavioral rule updates by compiling
  trajectories into structured (precondition, behavior, expected effect,
  verifier) hypotheses, evaluating them in temporary state across
  target-transfer, four-part falsification, and archived-regression probes
  with one-pass separable precondition narrowing and post-commit violation
  eviction. Derived from "When Should Agents Remember? Falsification-Gated
  Self-Evolution for LLM Agents" (arXiv:2611.14326).
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Falsification-Gated Memory Evolution

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

Use this skill when designing or hardening **post-episode memory, playbook, or behavioral-rule evolution** for stateful LLM agents (such as web/browser navigators, multi-app API orchestrators, customer-service tool agents, or long-horizon conversational memory systems) where:

- The agent extracts reusable lessons, tool-ordering heuristics, or constraint checks from completed episodes and writes them into persistent memory for future retrieval.
- Naive reflection or playbook accumulation (`Reflexion`, `A-Mem`, `ACE`, `Voyager`-style text libraries) causes **overgeneralization, boundary collisions, shortcut learning, or silent regressions** on previously mastered tasks.
- External or executable task verifiers (database-state checkers, unit tests, API schema/postcondition validators, security checkers, or exact-match evaluators) exist for development or archived episodes.

Do **not** use this skill for offline coding-agent scaffold search over repository-wide prompts without episode-level memory retrieval (use [`belief-calibrated-scaffold-optimization`](../belief-calibrated-scaffold-optimization/SKILL.md) instead), or as a standalone defense against untrusted third-party skill files (pair with [`feedback-poisoning-skill-promotion-guard`](../feedback-poisoning-skill-promotion-guard/SKILL.md) and [`skill-evolution-defense`](../skill-evolution-defense/SKILL.md)).

## Overview

Self-evolving memory systems commonly equate **single-episode hindsight** or **target-task gain** with safe transfer. Across controlled evaluations in `FGSE` (`arXiv:2611.14326`), existing self-updating memory baselines suffer `8.7%–20.7%` harmful committed updates and `11.6%–27.6%` falsification failure rates (`Table 5`). Crucially, target gain alone does not filter out dangerous rules: in a `380`-candidate diagnostic audit, the `101` rejected candidates that *exceeded* the minimum target-transfer gain threshold ($\widehat{G}(h) \ge 0.03$) still exhibited a `22.82%` falsification failure rate and `4.85%` archived regression damage, compared to `1.28%` and `0.60%` for the `104` hypotheses that survived falsification gating.

Falsification-Gated Self-Evolution (`FGSE`) treats every post-episode memory candidate as a **falsifiable behavioral hypothesis** $h = (c_h, b_h, e_h, v_h)$ rather than free-form reflection prose. Tested with `DeepSeek-V3.1`, `FGSE` reaches `39.8%` WebArena success (vs. `26.4%` for `ReAct + ACE online`), `78.8%` AppWorld average (`88.2%` Normal, `69.4%` Challenge vs. `68.2%` `ReAct + ACE online`), `0.724` / `0.487` Pass^1 on $\tau$-Retail / $\tau$-Airline (vs. `0.665` / `0.456`), `0.748` LongMemEval accuracy, and `37.62` LoCoMo Avg R-L—while holding falsification failures to `5.0%` (vs. `18.6%` without falsification probes), regression damage to `1.3%` (vs. `5.2%` without a regression archive), harmful updates to `3.6%` (vs. `9.4%` under an LLM-judge gate), and post-commit runtime violations to `3.1%` (vs. `10.6%` without post-commit monitoring).

---

## Step-by-Step Procedure

### Step 1: Compile Episode Evidence into Structured Hypotheses

After an episode completes with evidence packet $E_t = (x_t, \tau_t, r_t, \mathcal{A}_t)$ (task input, trajectory, environment/verifier outcome, and audit archive reference), propose at most $B$ candidate hypotheses (default $B = 3$). Reject unstructured natural-language reflections; require every candidate $h = (c_h, b_h, e_h, v_h)$ to populate four schema-constrained fields:

1. **`precondition` ($c_h : \mathcal{Z} \to [0, 1]$)**: Explicit applicability predicate over the observable interaction state $z = (x, \tau_{<\ell})$, scored by a lightweight rule matcher or classifier with activation threshold $\gamma_h$ (default $\gamma_h = 0.5$).
2. **`behavior` ($b_h$)**: Bounded policy intervention targeting **tool-execution order**, **explicit pre-commit constraint checking**, or **targeted memory retrieval** (mechanistic trajectory alignment shows these three edit families drive almost all failure-to-success transitions, whereas final-answer formatting accounts for a negligible share).
3. **`expected_effect` ($e_h$)**: Verifier-observable postcondition predicate $E_h(\Theta, x) \in \{0, 1\}$ that must hold whenever $h$ fires (for example, `booking record contains trip_type='round_trip' and both outbound and return segments`).
4. **`verifier` ($v_h$)**: Reference to an executable or externally grounded validator (`database_state_validator`, `unit_test`, `security_validator`, or `exact_match_evaluator`). Enforce $\operatorname{Verifiable}(x, v_h) = 1$: if a candidate cannot be checked by an external/executable verifier, discard it rather than falling back to an ungrounded LLM judge (replacing executable verifiers with an LLM-judge gate drops WebArena by `-3.1` points and AppWorld by `-4.7` points while raising harmful updates from `3.6%` to `9.4%`).

### Step 2: Isolate Candidates via Temporary-State Policy Mixing

Never write a proposed hypothesis directly into persistent memory $\mathcal{M}_t$. Construct an isolated temporary agent state $\Theta_t \oplus h$ that blends $b_h$ into the base policy $\pi_{\Theta_t}$ only when the precondition gate $g_h(z) = \mathbb{I}[c_h(z) \ge \gamma_h]$ is active:

$$\pi_{\Theta_t \oplus h}(a \mid z) = \bigl(1 - \lambda_h g_h(z)\bigr)\pi_{\Theta_t}(a \mid z) + \lambda_h g_h(z)\, b_h[\pi_{\Theta_t}](a \mid z)$$

- Set $\lambda_h \in (0, 1)$ (default $\lambda_h = 0.8$) so base-policy actions retain nonzero fallback support even when $h$ activates.
- Evaluate $\Theta_t$ and $\Theta_t \oplus h$ on every probe $x$ using **paired rollout seeds** $s$ (controlling stochastic decoding, tie-breaking, and environment perturbations) to compute marginal verifier improvement $\Delta_h(x) = J_{v_h}(\Theta_t \oplus h, x) - J_{v_h}(\Theta_t, x) \in [-1, 1]$. Truly transferable hypotheses exhibit positive mean seed effect ($\bar{\Delta}_h \approx 0.10$) and sign consistency $C(h) > 0.9$ across seeds, whereas stochastic flukes flip sign near zero.

### Step 3: Build Hypothesis-Conditioned Target, Falsification, and Regression Probes

For each candidate $h$, construct a three-part probe suite $\mathcal{P}(h) = \mathcal{T}(h) \cup \mathcal{F}(h) \cup \mathcal{R}(h)$ admitting **only** tasks satisfying $\operatorname{Verifiable}(x, v_h) = 1$ (default budget: $|\mathcal{T}(h)| = 8$, $|\mathcal{F}(h)| = 16$, $|\mathcal{R}(h)| = 16$, totaling `20–40` verifier calls per candidate on the plasticity–safety Pareto frontier):

1. **Target-transfer probes $\mathcal{T}(h)$**: Held-out tasks distinct from the source episode $x_t$ where $c_h(z) \ge \gamma_h$, testing whether the gain generalizes beyond the triggering trace.
2. **Targeted four-family falsification probes $\mathcal{F}(h) = \mathcal{F}_{\mathrm{bd}}(h) \cup \mathcal{F}_{\mathrm{pv}}(h) \cup \mathcal{F}_{\mathrm{rg}}(h) \cup \mathcal{F}_{\mathrm{dc}}(h)$**: Select probes conditionally on $h$'s failure surface rather than sampling uniformly at random (at low budget $K = 8$, hypothesis-targeted scheduling detects roughly `2x` as many bad updates as pure random probing and surfaces high-severity updates first):
   - **Boundary probes ($\mathcal{F}_{\mathrm{bd}}$)**: Tasks near the applicability boundary $|c_h(z) - \gamma_h| \le \tau_{\mathrm{bd}}$ (for example, one-way or multi-city flights adjacent to a round-trip rule; calendar creation or cancellation adjacent to a rescheduling rule).
   - **Precondition-violation probes ($\mathcal{F}_{\mathrm{pv}}$)**: Counterfactual edits that remove a critical slot or authorization required for $b_h$ to succeed safely.
   - **Hypothesis-linked regression probes ($\mathcal{F}_{\mathrm{rg}}$)**: Solved tasks sharing tools, APIs, or state schemas with $h$ where altered tool order could break existing workflows.
   - **Decoy and shortcut probes ($\mathcal{F}_{\mathrm{dc}}$)**: Inputs containing superficial lexical triggers or untrusted tool-output instructions (such as prompt-injection verification tokens) to expose shortcut policies.
3. **Archived regression probes $\mathcal{R}(h)$**: Previously solved episodes drawn from the audit archive $\mathcal{A}_t$ ($J_{v_h}(\Theta_t, x) \ge \zeta_h$) to bound backward-transfer damage across rounds.

### Step 4: Evaluate Gate Statistics and Run One-Pass Precondition Narrowing

Compute the three probe statistics over $\mathcal{P}(h)$:

- **Target-transfer gain**: $\widehat{G}(h) = \frac{1}{|\mathcal{T}(h)|} \sum_{x \in \mathcal{T}(h)} \Delta_h(x)$ (default minimum $\eta = 0.03$).
- **Falsification failure rate**: $\widehat{P}_{\mathrm{fail}}(h) = \frac{1}{|\mathcal{F}(h)|} \sum_{x \in \mathcal{F}(h)} \mathbb{I}\!\left[\Delta_h(x) < -\epsilon \;\lor\; E_h(\Theta_t \oplus h, x) = 0\right]$ (default maximum $\delta_{\mathrm{fals}} = 0.05$, tolerated verifier drop $\epsilon = 0$).
- **Archived regression damage**: $\widehat{D}_{\mathrm{reg}}(h) = \frac{1}{|\mathcal{R}(h)|} \sum_{x \in \mathcal{R}(h)} [-\Delta_h(x)]_+$ (default maximum $\beta = 0.01$).

> **Small-budget confidence option**: When probe counts are small or high-assurance bounds are required over candidate batch $\mathcal{H}_t$, replace raw means with empirical-Bernstein lower/upper bounds $\mathrm{LCB}_T(h) \ge \eta$, $\mathrm{UCB}_R(h) \le \beta$, and the exact Bernoulli-KL upper confidence bound $\mathrm{UCB}_F(h) \le \delta_{\mathrm{fals}}$ split across failure budget $\alpha = \alpha_T + \alpha_F + \alpha_R$.

Apply three-way candidate triage (`Commit Candidate`, `Refine Once`, or `Reject`):

1. **Direct pass**: If $\widehat{G}(h) \ge \eta$, $\widehat{P}_{\mathrm{fail}}(h) \le \delta_{\mathrm{fals}}$, and $\widehat{D}_{\mathrm{reg}}(h) \le \beta$, advance $h$ to Step 5.
2. **One-pass separable precondition narrowing**: If $\widehat{G}(h) \ge \eta$ but falsification or regression fails, partition evaluated probes into beneficial safe positives $\mathcal{P}_h^+$ and falsifying negatives $\mathcal{P}_h^-$, and measure precondition separability $\operatorname{Sep}(h)$.
   - **If $\operatorname{Sep}(h) \le \alpha_{\mathrm{sep}}$** (failures concentrate in an identifiable boundary region rather than throughout the positive support): narrow $c_h \to c_h'$ **at most once** by adding the discriminating state constraint (keeping $b_h, e_h, v_h$ fixed), rebuild a **fresh disjoint probe split** $\mathcal{P}(h')$ so post-refinement evaluation remains statistically uncontaminated, and re-test $h'$. (In AppWorld calendar rescheduling, narrowing `"any request mentioning reschedule"` to `"exactly one matching event exists and user explicitly requests changing its time"` at $\operatorname{Sep}(h) = 0.07$ preserved `73.1%` of target gain [`10.4% -> 7.6%`] while cutting $\widehat{P}_{\mathrm{fail}}$ from `18.8%` [`3/16`] to `0.0%` [`0/16`] and $\widehat{D}_{\mathrm{reg}}$ from `2.7%` to `0.8%`.)
   - **If $\operatorname{Sep}(h) > \alpha_{\mathrm{sep}}$ or $\widehat{G}(h) < \eta$**: **reject immediately** without iterative patching (for example, an AgentDojo shortcut trusting urgent tool-output instructions had $\widehat{G}(h) = 8.7\%$ but $\widehat{P}_{\mathrm{fail}} = 31.2\%$ [`5/16`] and $\operatorname{Sep}(h) = 0.31$, preventing an unrepairable injection vulnerability).

### Step 5: Pass Persistent Writes Through the Single Acceptance Gate and Log Provenance

Passing Step 4 selects a falsification-vetted candidate—it does **not** bypass system-wide acceptance governance:

1. **Enforce the single acceptance gate**: Before committing $h$ (or $h'$) to persistent memory $\Theta_{t+1} = \Theta_t \oplus h$, pass the candidate through `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../../rules/recursive-improvement.md): accept the persistent state update **only** if it shows no regression beyond the baseline noise margin $\delta$ on protected previously-correct cases and held-out tasks (where $\delta$ is estimated from at least `3` repeated runs of the unchanged baseline), and enforce **strict zero tolerance (no margin)** on the negative security testbed (such as prompt-injection and decoy-tool suites).
2. **Write the full audit record**: Append $\operatorname{Record}(h) = \bigl(h, \mathcal{T}(h), \mathcal{F}(h), \mathcal{R}(h), \{\Delta_h(x)\}_{x \in \mathcal{P}(h)}, \widehat{G}(h), \widehat{P}_{\mathrm{fail}}(h), \widehat{D}_{\mathrm{reg}}(h), u_t(h)\bigr)$ to $\mathcal{A}_{t+1}$ for both accepted and rejected candidates so refuted shortcuts are documented.
3. **Bound active retrieval**: Retrieve at most top-$k$ applicable committed hypotheses per step (default $k = 5$) and keep committed library growth selective—empirical memory-growth curves saturate around `120–150` vetted entries (`70%–72%` task success at `4%–5%` violation rate), whereas naive `All-Commit` enters an overgrown regime with rising violations and retrieval cost.

### Step 6: Monitor Post-Commit Violations and Evict Drifting Hypotheses

Finite pre-commit probes cannot anticipate every future distribution shift. During live deployment, monitor every active committed hypothesis $h \in \mathcal{H}_t(z)$ whenever $c_h(z) \ge \gamma_h$ on a verifiable episode:

1. Compute the episode violation indicator $V_t(h, x_t) = \mathbb{I}\!\left[E_h(\Theta_t, x_t) = 0 \;\lor\; J_{v_h}(\Theta_t, x_t) < \zeta_h\right]$.
2. Update the exponential moving-average violation score:
   $$u_{t+1}(h) = \rho_u u_t(h) + (1 - \rho_u) V_t(h, x_t)$$
3. If $u_{t+1}(h) > \rho_{\max}$ (default $\rho_{\max} = 0.10$), **evict $h$ from active retrieval immediately** while retaining its history in $\mathcal{A}_{t+1}$ for post-hoc audit and anti-regression seeding.

---

## Environment Caveats

- **Tasks lacking built-in verifiers**: `FGSE` presupposes an executable or programmatic check ($\operatorname{Verifiable}(x, v_h) = 1$). When tasks lack ground-truth tests, synthesize and certify an executable verifier first using [`certified-task-verifier-harness`](../certified-task-verifier-harness/SKILL.md) rather than substituting an unanchored single-LLM judge (`LLM-judge gate` increases falsification failures from `5.0%` to `13.8%` and harmful updates from `3.6%` to `9.4%`).
- **Clean code/math vs. stateful tool/web environments**: In deterministic code and math tasks (`HumanEval`, `MBPP`, `SWE-bench Verified`), unit tests already constrain false positives tightly; `FGSE`'s largest safety gains appear in **partially observable web, multi-app API, multi-turn policy, and adversarial tool-use (`AgentDojo`) environments** where boundary ambiguity and untrusted tool outputs cause unvetted memory writes to backfire.
- **Dev-vs-commit probe separation**: Never reuse the exact probe instances that drove precondition narrowing ($c_h \to c_h'$) to compute the final commitment verdict—reusing the refinement split invalidates finite-sample concentration guarantees and overfits $c_h'$ to observed counterexamples.

## Failure Modes

- **Target-only or hindsight-only gating**: Committing every rule that improves the source episode or passes $\widehat{G}(h) \ge \eta$ without $\mathcal{F}(h)$ raises falsification failure rate by `+13.6` percentage points (`5.0% -> 18.6%`) and nearly triples harmful updates (`3.6% -> 10.6%`).
- **Single-family probing (`Boundary-Only` or `Regression-Only`)**: Testing only applicability boundaries misses regressions on shared tools and decoy-induced shortcuts; testing only archived regressions misses boundary overreach on new user intents. Both saturate well below four-family hypothesis-conditioned probing.
- **Multi-pass precondition patching**: Allowing repeated LLM rewrites of $c_h$ after failed probes turns scope refinement into ad-hoc exception listing that memorizes probe IDs. Enforce **at most one** separability-gated refinement pass ($\operatorname{Sep}(h) \le \alpha_{\mathrm{sep}}$); reject otherwise.
- **Omitting post-commit monitoring**: Even vetted hypotheses degrade under downstream task shift; disabling Step 6 raises post-commit runtime violations from `3.1%` to `10.6%` (`+7.5` percentage points).

## Cross-References

- Acceptance governance: [`recursive-improvement.md`](../../rules/recursive-improvement.md) (`"DO: Pass every self-modification through one acceptance gate"`)
- Synthesizing executable task verifiers when $v_h$ is missing: [`certified-task-verifier-harness`](../certified-task-verifier-harness/SKILL.md)
- Scaffold-level causal world-model hypotheses: [`belief-calibrated-scaffold-optimization`](../belief-calibrated-scaffold-optimization/SKILL.md)
- Lifecycle governance for skill registries: [`controlled-skill-lifecycle-management`](../controlled-skill-lifecycle-management/SKILL.md)
- Defending skill/memory promotion against poisoned feedback: [`feedback-poisoning-skill-promotion-guard`](../feedback-poisoning-skill-promotion-guard/SKILL.md)
- Separating persistent knowledge logs from active execution context: [`knowledge-compounding-loop`](../knowledge-compounding-loop/SKILL.md)
