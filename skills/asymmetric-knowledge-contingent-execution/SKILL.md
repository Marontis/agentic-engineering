---
name: asymmetric-knowledge-contingent-execution
description: Wrap untrusted foundation-model planners in an online execution kernel that isolates drifting default records from verified three-valued knowledge, permits at most one optimistic attempt on undecided reversible actions while requiring verified preconditions for irreversible actions, synthesizes minimum-cost deadline-feasible sensing covers (including time-windowed human approvals), and halts in Certified Holds when verification is infeasible.
source: "Trustworthy agentic lunar robotics: safety-constrained contingent planning with a foundation-model planner (arXiv:2611.30179)"
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Asymmetric-Knowledge Contingent Execution (`AKR`)

Foundation-model (`LLM`/`VLM`) planners excel at open-world recovery when unforeseen faults invalidate hand-authored task trees, yet deploying them directly in partially observable environments with stale configuration records, imperfect action execution, and irreversible side effects exposes two symmetric failure traps (`arXiv:2611.30179`, `§1–§3`):
1. **Optimistic replanning (`FF-Replan`) executes irreversible hazards**: Treating stale records or controller completion flags as truth—or asking the LLM when to sense—placed necessary checks before irreversible actions in only **`48 / 1,938` (`2.5%`)** plans even at zero planner hallucination ($\varepsilon = 0$), causing **`7.4%–8.3%` hazardous trials (`2,033` runs)** in Monte Carlo grids, **`27,999 / 28,000`** premature component removals before ground authorization, and **`8` unrecoverable physical hazards across `36` Isaac Sim runs**.
2. **Uniform conservatism (`K-replanner`) deadlocks and wastes sensing budget on harmless reversible steps**: Requiring every precondition of *every* action to be sensed to certainty before acting caused **`328` planner-cap stalls** when reversible placement targets were initially undecided (`29 / 30` sampled states had *no* valid plan without trying a reversible action optimistically) and inflated median physical mission execution time from **`1.10x` to `1.50x`** (`68.6 s` of unnecessary inspections vs. `0 s`, `Tables 6–8`).

This skill implements the **Asymmetric Knowledge-Level Contingent Execution (`AKR` / `Thoth`, `arXiv:2611.30179`, `Algorithm 1`)** wrapper: a planner-agnostic runtime kernel whose safety guarantee (`Theorem 1`), per-decision sensing optimality (`Theorem 2`), and bounded termination (`Theorem 3`) hold **regardless of planner hallucination rate $\varepsilon \in [0, 1]$ or initial record corruption $p_R \in [0, 1]$**.

## When to Use

Apply this execution kernel whenever a foundation-model planner proposes multi-step actions over partially observed, stateful environments combining reversible exploration/manipulation with irreversible commits:
- **Autonomous robotics & cyber-physical maintenance** (warehouse, field, subsea, or space operations) where physical handovers, breaker trips, or component removals are unrecoverable if preconditions fail.
- **Cloud infrastructure & GitOps incident remediation** where CMDB/inventory records drift ($R$), diagnostic/staging steps are reversible ($A_{\mathrm{rev}}$), and production failovers, schema drops, or volume deletions are irreversible ($A_{\mathrm{irr}}$).
- **Enterprise operations with time-windowed human or external approvals** (maintenance windows, change-advisory sign-offs, intermittent satellite/edge connectivity) where authorization must be requested before a deadline $w_{\sigma_a}$ or the workflow must hold safely before tearing down live state.
- **Automated laboratory & manufacturing workcells** where controller `"done"` return codes do not prove physical sample transfer or valve closure without independent post-action telemetry.

For static single-turn MCP trigger-action workflows where preconditions are fully observable in a single snapshot without active sensing synthesis or post-action drift, see [`intent-ltl-mcp-orchestration`](../intent-ltl-mcp-orchestration/SKILL.md).

## Core Insight

Separate **planner guidance** from **epistemic admissibility** across four invariants (`arXiv:2611.30179`, `§3.2–§4`):
1. **Strict Epistemic Firewall Between Untrusted Records $R$ and Three-Valued Knowledge $\kappa$**: Pass default records $R$ to the LLM planner as search hints, but **never** copy $R$ or planner assertions into the runtime knowledge map $\kappa: P \to \{\mathsf{T}, \mathsf{F}, \mathsf{U}\}$. Only sound initial facts $K_0$, direct sensing outcomes, and verified post-action physical evidence update $\kappa$.
2. **Three-Valued Post-Action Physical Judgment**: After every actuation $a$, evaluate independent physical/telemetry evidence $e \in E_a$ via $\nu_a(e) \in \{\mathsf{v} \text{ (verified)}, \mathsf{r} \text{ (refuted)}, \mathsf{u} \text{ (inconclusive)}\}$. If $\nu_a(e) = \mathsf{u}$, **reset affected propositions in $\mathrm{eff}(a)$ to $\mathsf{U}$** even if they were previously $\mathsf{T}$ or $\mathsf{F}$—capturing non-monotonic knowledge loss when an uncertain physical interaction disturbs prior state.
3. **Asymmetric Admissibility with Single-Try Failure Memory $\mathcal{F}$**:
   - **Reversible actions ($a \in A_{\mathrm{rev}}$)** may execute optimistically when no precondition is *known false* ($\forall l \in \mathrm{pre}(a): \kappa \not\models \neg l$) **at most once per undecided proposition**; if post-action evidence fails to verify (`\mathsf{r}` or `\mathsf{u}`), add the previously undecided preconditions to failure set $\mathcal{F}$ so any second proposal touching $\mathcal{F}$ forces explicit sensing.
   - **Irreversible actions ($a \in A_{\mathrm{irr}}$)** are **never** admitted optimistically: every $l \in \mathrm{pre}(a)$ must satisfy $\kappa \models l$ (`Theorem 1`: `0` hazardous dispatches across all planners and record error rates when sensor error $\eta = 0$).
4. **Minimum-Cost Deadline-Feasible Sensing Covers & Certified Holds**: Model human/remote authorization (`granted_a`) uniformly as a sensing action $\sigma_a \in A_{\mathrm{sense}}$ with cost $c_g$ and latest start deadline $w_{\sigma_a} = T_{\mathrm{vis}} - c_g$. Whenever an action is blocked by undecided literals $U$, solve a minimum-cost set cover over deadline-feasible sensors (`Eq. 8`), dispatch tighter-deadline sensors first, and immediately emit a **Certified Hold** (`Corollary 1`) naming the blocked irreversible action and missing preconditions if no feasible cover exists ($c^\star(U, t) = \infty$) or authorization is refused.

*(Notation note on `arXiv:2611.30179`: in the arXiv HTML conversion, LaTeXML mis-expanded the macro `\pre` into `Phys. Rev. E`; all precondition sets correspond to standard $\mathrm{pre}(a)$ as confirmed in §3.1.)*

## Step-by-Step Procedure

### Step 1: Partition Domain Propositions, Actions, and Untrusted Records

1. **Declare the proposition vocabulary $P$ and action partition $A = A_{\mathrm{rev}} \sqcup A_{\mathrm{irr}} \sqcup A_{\mathrm{sense}}$**:
   - Classify an action into **$A_{\mathrm{rev}}$** *only* if executing it when an undecided precondition fails is physically/operationally benign and leaves the system recoverable (e.g., navigating, opening a read-only panel, attempting a gentle reversible placement on a candidate surface).
   - Classify **every** action whose execution under a false precondition causes unrecoverable loss, safety hazard, policy violation, or uncompensated external mutation into **$A_{\mathrm{irr}}$** (e.g., cutting power/removing a unit before a spare and operator grant are verified, dropping/handing over fragile cargo onto an unverified fixture, deleting production state).
   - For each sensing/inspection/approval action $\sigma \in A_{\mathrm{sense}}$, declare its observed proposition subset $Q_\sigma \subseteq P$, cost/duration $c(\sigma) > 0$, preconditions $\mathrm{pre}(\sigma)$, and latest start deadline $w_\sigma \in \mathbb{R}_{\ge 0} \cup \{\infty\}$ (for remote/human approval over a connectivity or change window closing at $T_{\mathrm{vis}}$ with round-trip latency $c_g$, set $w_{\sigma_a} = T_{\mathrm{vis}} - c_g$ and include `granted_a` in $\mathrm{pre}(a)$ for the gated $a \in A_{\mathrm{irr}}$).
2. **Initialize $\kappa_0$ strictly from verified telemetry $K_0$, never from $R$**:
   - Set $\kappa(p) = \mathsf{T}$ if $p \in K_0$, $\mathsf{F}$ if $\neg p \in K_0$, and $\mathsf{U}$ for all remaining $p \in P$, and initialize optimistic-failure memory $\mathcal{F} \leftarrow \emptyset$. Expose the default record $R$ solely inside the planner's prompt/world summary as unverified prior context.

### Step 2: Enforce Three-Valued Post-Action Evidence Updates (`Eqs. 2–5`)

1. **Never update $\kappa$ from controller `HTTP 200` / `"completed"` flags**:
   - Pair every actuating action $a \in A_{\mathrm{rev}} \cup A_{\mathrm{irr}}$ with an independent physical/state judge $\nu_a: E_a \to \{\mathsf{v}, \mathsf{r}, \mathsf{u}\}$ built from post-action telemetry (joint torque/pose residuals, optical/DOM state reads, database row witnesses) calibrated selectively with an explicit inconclusive band $\mathsf{u}$ so false-verified/false-refuted judgment error stays near zero (`0.26%` empirical selective error at `96.2%` conclusive rate across `2,177` Isaac Sim actions, `Table 9`).
2. **Apply non-monotonic three-valued state updates**:
   - If $\nu_a(e) = \mathsf{v}$: set $\kappa'(p) = \mathsf{T}$ for $p \in \mathrm{eff}^+(a)$ and $\kappa'(p) = \mathsf{F}$ for $\neg p \in \mathrm{eff}^-(a)$, clearing resolved propositions from $\mathcal{F}$.
   - If $\nu_a(e) = \mathsf{r}$: leave $\kappa' = \kappa$ (the intended transition did not take place).
   - If $\nu_a(e) = \mathsf{u}$: **reset $\kappa'(p) = \mathsf{U}$ for every proposition $p$ appearing in $\mathrm{eff}(a)$**, forcing fresh verification before any downstream irreversible step can rely on those propositions.

### Step 3: Gate Planner Proposals via Asymmetric Admissibility (`Eqs. 6–7`)

At each online decision epoch with current knowledge $\kappa$, failure set $\mathcal{F}$, and clock $t$:
1. **Check goal verification first**: Terminate with `Verified Goal` **only** when $\kappa \models G$ (never because the planner emits `DONE`). If the planner claims completion while $U_G = \{l \in G \mid \kappa \not\models l\}$ is non-empty, route $U_G$ directly to Step 4 sensing cover synthesis.
2. **Request a candidate action plan from the foundation-model planner**:
   - Provide $(\kappa, R \text{ restricted to } \kappa(p)=\mathsf{U}, \mathcal{F}, G, t)$ to the planner and inspect the first proposed action $a$.
   - Immediately reject and trigger replanning (up to a small per-state retry cap $N_r$) if $a$ has a **known-false** precondition ($\exists l \in \mathrm{pre}(a): \kappa \models \neg l$).
3. **Evaluate Asymmetric Admissibility $\mathrm{Adm}(\kappa, \mathcal{F}, a)$**:
   - Compute undecided preconditions $U_a = \{l \in \mathrm{pre}(a) \mid \kappa(p(l)) = \mathsf{U}\}$.
   - **If $a \in A_{\mathrm{rev}}$ and $\mathrm{prop}(U_a) \cap \mathcal{F} = \emptyset$**: `ADMIT` $a$ optimistically without pre-sensing! Execute $a$, obtain $\nu_a(e)$, update $\kappa$, and **if $\nu_a(e) \in \{\mathsf{r}, \mathsf{u}\}$**, update $\mathcal{F} \leftarrow \mathcal{F} \cup \mathrm{prop}(U_a)$ so the same undecided reversible assumption cannot loop a second time without sensing.
   - **If $a \in A_{\mathrm{irr}}$ and $U_a = \emptyset$**: `ADMIT` $a$ (all preconditions are verified in $\kappa$).
   - **Otherwise** ($a \in A_{\mathrm{irr}}$ with $U_a \neq \emptyset$, or $a \in A_{\mathrm{rev}}$ with $\mathrm{prop}(U_a) \cap \mathcal{F} \neq \emptyset$): **WITHHOLD $a$** and pass $U \leftarrow \mathrm{prop}(U_a)$ to Step 4.

### Step 4: Synthesize Minimum-Cost Deadline-Feasible Sensing Covers (`Eq. 8`)

1. **Solve the deadline-constrained sensing set cover**:
   - Over all currently executable sensors $A_{\mathrm{sense}}(\kappa, t) = \{\sigma \in A_{\mathrm{sense}} \mid \kappa \models \mathrm{pre}(\sigma) \land t \le w_\sigma\}$ (or sensor plans whose preconditions can themselves be established), select $S^\star \subseteq A_{\mathrm{sense}}$ minimizing $\sum_{\sigma \in S} c(\sigma)$ subject to:
     - Coverage: $U \subseteq \bigcup_{\sigma \in S} Q_\sigma$, and
     - **Deadline feasibility**: there exists an ordering $(\sigma_1, \dots, \sigma_m)$ of $S$ such that every start time $t_j = t + \sum_{i < j} c(\sigma_i)$ satisfies $t_j \le w_{\sigma_j}$ (`Theorem 2` proves $c^\star_D(U, t)$ is a lower bound on every sound knowledge-based policy at $(\kappa, t)$).
   - Because $|U|$ for a single blocked action is typically small (`1–6` literals), exact branch-and-bound / ILP solves in sub-millisecond code outside the LLM.
2. **Order urgent authorization/windowed sensors first (`Earliest Deadline First`)**:
   - Dispatch finite-deadline sensors (such as remote human/ground approval $\sigma_a$ with $w_{\sigma_a} < \infty$) **ahead of** deadline-free local checks ($w_\sigma = \infty$) whenever preconditions permit, preventing local inspection durations from pushing approval requests past visibility cutoffs.
   - As each $\sigma \in S^\star$ executes and updates $\kappa$, **abort remaining sensors early** if any literal $l \in \mathrm{pre}(a)$ is refuted ($\kappa \models \neg l$, including `granted_a = F`), and return immediately to Step 3 replanning over the updated $\kappa$.

### Step 5: Emit Certified Holds and Bound Episode Steps (`Corollary 1` & `Theorem 3`)

1. **Fail closed into a diagnostic `Certified Hold`**:
   - Whenever $c^\star(U, t) = \infty$ (no sensor exists for a required irreversible precondition, a communication/approval window $w_{\sigma_a}$ has already closed, or all candidate recovery branches require an explicitly refuted precondition such as `granted_a = F` with no local spare), **halt immediately without executing $a \in A_{\mathrm{irr}}$** and emit a structured `Certified Hold` receipt listing `(blocked_action, unverified_or_refuted_literals, expired_deadlines, current_verified_state_kappa)`.
2. **Enforce a hard episode step bound and audit sensor noise $\eta$**:
   - Cap total episode transitions using `Theorem 3`'s finite progress structure ($N = 4|P| + 2|A_{\mathrm{sense}}| + N_x + 2$ under bounded exogenous resets $N_x$), guaranteeing termination without infinite planner loops.
   - Calibrate physical sensors conservatively (preferring $\mathsf{U}$ or multi-frame consensus over noisy binary commits): in `arXiv:2611.30179`, `AKR` maintained **`0 / 5,000` hazardous actions** across sensor error rates $\eta \in [0.001, 0.02]$ (with physical Isaac Sim sensor disagreement measured at $\eta = 0.0072$, `40 / 5,537`), rising gradually to `2 / 1,000` at $\eta = 0.05$.

## Empirical Benchmarks (`arXiv:2611.30179`)

- **`254,000` Monte Carlo Trials (`Tables 1–5`, $|P| = 355\text{--}368$)**:
  - **Safety across planner & record corruption**: At $\eta = 0$, `AKR` recorded **`0 / 21,000` hazardous actions** across $\varepsilon \in [0, 1]$ and $p_R \in [0, 1]$ vs. **`2,033` hazardous trials (`7.4%–8.3%`)** for `FF-Replan` (`1,405` never-judged, `616` inconclusive $\mathsf{u}$, `12` false records). In `28,000` no-spare ground-refusal trials ($p_{\mathrm{refuse}} = 0.5$), `AKR` committed **`0` premature removals** (`14,022` verified repairs, `13,965` certified holds) vs. **`27,999 / 28,000`** premature removals for `FF-Replan`.
  - **Efficiency vs. uniform conservatism**: `K-replanner` stalled at the planner-call cap in **`328` trials** vs. **`0`** for `AKR`, and its median sensing time climbed from `12.54 s` ($p_R = 0$) to `28.79 s` ($p_R = 1$) while `AKR` stayed flat at **`3.42 s`**.
- **`165` Full-Stack Isaac Sim Runs (`LunarBot` + `DeepSeek-V4.1-Flash`, `16` missions, `Tables 6–10`)**:
  - **`0 / 58` hazardous `AKR` runs** (`23 / 23` unverified irreversible proposals withheld; `17 / 19` sensing covers matched the exact lower bound $c^\star_D = 5.7\text{ s}$) vs. **`8` hazardous actions in `36` `FF-Replan` runs** (`6` unrecoverable cargo drops onto occupied stands, `2` energized module removals).
  - **Median execution time ratio `1.10`** (`24` actuation steps, `0` reversible sensing covers) vs. **`1.50`** for `K-replanner` (`32` steps, `21` unnecessary reversible covers costing `68.6 s`).
  - **`20 / 21` contingency + sequential-fault completions** (`18 / 18` base hidden-cause runs) with **zero manual task-model edits**, whereas original `PLEXIL` and `EUROPA -> PLEXIL` executives solved **`0 / 7` contingency missions** until engineers spent `38.9` and `224.3` minutes manually revising plans (`Table 10`).

## Cross-References

- **Related Skills & Briefs**:
  - [`intent-ltl-mcp-orchestration`](../intent-ltl-mcp-orchestration/SKILL.md) — Offline NL-to-LTL compilation and single-snapshot Z3 SMT precondition gating for deterministic MCP trigger-action rules (`SafeOrchestrate`)
  - [`world-model-trust-gating`](../world-model-trust-gating/SKILL.md) — Calibrating trust in learned world-model predictions via action-outcome error (`2609.26293`)
  - [`out-of-band-hitl-verification`](../out-of-band-hitl-verification/SKILL.md) — Hardware-attested out-of-band human approval channels (`I-HITL`) that plug directly into `AKR`'s deadline-bounded `granted_a` sensing model
  - [`detecting-is-not-choosing-vla-world-model-safety`](../../research-briefs/detecting-is-not-choosing-vla-world-model-safety.md) — Why low-level continuous VLA policies still require explicit safe fallback primitives and low-tail-error state estimators beneath symbolic execution kernels (`arXiv:2611.29553`)
- **Related Rules**:
  - [`output/rules/agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — `"DO: Compile cyber-physical and multi-device intents into role-grounded LTL specifications with SMT precondition gating"`, `"DON'T: Treat HTTP 200 / success tool return codes as workflow success without state verification"`, `"DON'T: Trust child-process stdout acknowledgements as proof of physical actuator execution, and always pair agent-synthesized hardware control loops with an out-of-band kill switch"`, and `"DON'T: Rely on structured LLM authorization decisions as the sole safety gate"`
  - [`output/rules/agent-human-interaction.md`](../../rules/agent-human-interaction.md) — `"DO: Define explicit escalation triggers, not vague guidelines"` and `"DON'T: Treat agent output as implicit authorization"`

## Sources

- **Primary Paper**: *Trustworthy agentic lunar robotics: safety-constrained contingent planning with a foundation-model planner* (`AKR` / `Thoth`, `arXiv:2611.30179`, Praxis source `src:2611-30179v1`)
