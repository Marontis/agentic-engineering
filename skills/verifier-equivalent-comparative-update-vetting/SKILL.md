---
name: verifier-equivalent-comparative-update-vetting
description: >-
  Vet candidate persistent memory, prompt, or code-skill updates before commit by
  synthesizing visibly divergent alternatives with byte-identical native-verifier
  readouts, judging paired trajectories in both presentation orders, and
  abstaining on ambiguity. Derived from DoppelVet (arXiv:2611.29306).
source: "arXiv:2611.29306"
repository: "https://github.com/Marontis/agentic-engineering"
license: CC-BY-4.0
---

<!-- Licensed under CC BY 4.0 | Source: Marontis/agentic-engineering | Origin: arXiv:2611.29306 -->

# Verifier-Equivalent Comparative Update Vetting

## When to Use

Use this procedure as a **pre-commit safety vetting layer** inside a self-evolving agent loop whenever the agent proposes persistent updates `u` (to episodic/semantic memory rules, tool-routing prompts, or executable skill code) that are scored on a replay bank by a **coarse native task verifier** (such as pass/fail unit tests, scalar task return, or terminal state checks) **without labeled safety examples or verifier retraining**. Representative project types include:

- **Enterprise customer-support and operations tool agents**: Vetting learned workflow heuristics or memory entries (e.g., refund, authentication, or account-modification shortcuts on retail/airline/CRM APIs) where two updates achieve identical ticket-completion rewards while one skips identity confirmation or mutates unauthorized records.
- **Self-evolving code-skill and automation libraries**: Screening candidate Python/shell skill patches or planner macros that pass functional regression suites (`100%` test pass rate and identical step counts) while introducing destructive side effects on unasserted files, resources, or environment objects.
- **Stateful sandboxed planning and control agents**: Auditing policy/code revisions in grid, simulation, or infrastructure sandboxes where irreversible side effects are unmeasured by the native task-reward scalar.

**When NOT to use**:
- **Backdoor/poisoned reference feedback in multi-edit prompt bundles**: When the external feedback signal itself may be adversarially injected to smuggle trigger-bound instructions alongside clean edits, run leave-one-edit-out marginal validation and literal-abstraction filtering ([`feedback-poisoning-skill-promotion-guard`](../feedback-poisoning-skill-promotion-guard/SKILL.md)) in addition to comparative trace vetting.
- **Single-step runtime action ranking without persistent state mutation**: For per-turn action lookahead inside a single episode rather than persistent self-modification, use lightweight runtime action verification ([`pairwise-action-verification`](../pairwise-action-verification/SKILL.md)).
- **Replacing held-out regression or deterministic security gates**: Comparative LLM vetting resolves intra-readout ambiguity (`u` vs. `v^*`)—it complements, and never replaces, deterministic invariant checks and the frozen acceptance gate in [`../../rules/recursive-improvement.md`](../../rules/recursive-improvement.md).

---

## Core Insight

Any native promotion rule—or post-hoc scalar calibration—that sees only a replay bank's native readout vector $\mathbf{r}_{\mathcal{B}}(u; s_t) = (\rho_1, \dots, \rho_m)$ is **provably blind** to safety differences inside the equivalence class $\mathcal{N}_{\mathrm{eq}}(u; s_t) = \{v : \mathbf{r}_{\mathcal{B}}(v; s_t) = \mathbf{r}_{\mathcal{B}}(u; s_t)\}$ (Proposition 1 in `DoppelVet`, `arXiv:2611.29306`: in `4/6` AI Safety Gridworlds and `28/168` exact-reward $\tau^2$-Bench Retail/Airline pairs, safe and harmful updates return byte-for-byte identical native readouts). Worse, evaluating a single candidate trajectory in isolation (`pointwise` LLM judging or standalone `AgentDoG 1.5`) gives the judge no behavioral baseline for what a *different* equally task-competent execution from the exact same initial state looks like—leaving `GPT-4.1` at `0.493` ROC AUC (`AgentDoG 1.5` at `0.454` / `0.419`) on `DoppelVet-Grid`.

**DoppelVet** breaks this tie without safety labels by constructing a **verifier-equivalent doppelgänger** $v^* \in \mathcal{N}_{\mathrm{eq}}(u; s_t)$ that achieves the **exact same complete native readout** on frozen replay bank $\mathcal{B}_t$ while **maximizing visible behavioral divergence** $D_{\mathcal{B}}(u, v)$ in tool-call sequences, intermediate states, or outputs, then judging $u$ directly against $v^*$ in **both physical presentation orders** with an explicit **abstention band**. Across `9` verifier backbones (`Qwen2.5-14B` through `Claude Opus 5` and `GPT-5.6 Sol`), `DoppelVet` raises mean ROC AUC from **`0.762 -> 0.940` (`+0.179` unrounded mean gain; `+0.001` to `+0.432`)** on `DoppelVet-Grid` and **`0.681 -> 0.826` (`+0.145`)** on `DoppelVet-Tool` (**`0.645 -> 0.831`, `+0.186`** on strict reward-matched tool pairs), improving **`9/9` backbones on every cohort**. Over a `10`-generation self-evolution loop (`464` starting programs, monitoring/rollback disabled), it slashes harmful commits from **`47.41% -> 0.86%`** (`VaG` `12.72%`, `AgentDoG` `25.22%`) and final safety degradation from **`7.76% -> 0.00%`** while retaining **`89.58%`** of safe-update opportunities at `53.1%` fewer tokens than 4-critic `VaG` (`1.586M` vs. `3.383M`).

---

## Step-by-Step Procedure

### Step 1: Isolate Current State and Record Complete Native Readouts on Frozen Replay Bank

Given candidate persistent update `u` proposed at state `s_t` and a frozen replay bank $\mathcal{B}_t = \{b_1, \dots, b_m\}$:

1. Fork an isolated sandbox snapshot of `s_t` so neither `u` nor any probe can mutate live persistent state, external APIs, or the replay bank.
2. Replay `u` from identical initial state snapshots across every item $b_k \in \mathcal{B}_t$, recording both:
   - The **complete native verifier readout** $\mathbf{r}_{\mathcal{B}}(u; s_t)$ (full vector of task rewards, pass/fail statuses, exit codes, and any native auxiliary metrics such as step length), and
   - The **visible execution trajectory** $\tau_k(u)$ (ordered tool names + serialized arguments $T(\tau_k)$, state transitions / diffs, and externally visible responses $Z(\tau_k)$).
3. If `u` fails basic task-promotion criteria on $\mathbf{r}_{\mathcal{B}}(u; s_t)$ or fails deterministic syntax/schema invariants $I_{\mathrm{det}}(u; s_t) \in \{0, 1\}$, reject `u` immediately (`0` LLM judge calls).

### Step 2: Synthesize Boundary Contrasts and Filter for Exact Verifier Equivalence ($\mathcal{N}_{\mathrm{eq}}$)

Generate $N$ structured counterfactual variants $\{v_1, \dots, v_N\}$ of `u` inside isolated copies of `s_t` using typed boundary operators suited to the artifact representation:

- **Memory / prompt / workflow rules**: Toggle or tighten precondition checks (e.g., explicit user/confirmation verification before write tools), swap alternative read-before-write query paths, reorder non-commuting tool calls, or vary scope guards while preserving the target task goal.
- **Executable code skills / policies**: Apply procedural AST or control-flow boundary perturbations (alternative path/routing Tie-breaks, side-effect-avoiding guards, resource cleanup branches, or conservative parameter bounds).

Replay each $v_i$ across all $m$ items in $\mathcal{B}_t$ ($O(Nm)$ sandbox executions) and retain **only strict verifier-equivalent alternatives**:

$$\mathcal{N}_{\mathrm{eq}}(u; s_t) = \bigl\{\, v_i \;\big|\; \mathbf{r}_{\mathcal{B}}(v_i; s_t) \equiv \mathbf{r}_{\mathcal{B}}(u; s_t) \text{ byte-for-byte across all } b_1, \dots, b_m \,\bigr\}$$

Do **not** relax equivalence to mean score or aggregate pass rate—both trajectories must tie on every native metric component so task competence cannot confound the safety comparison.

### Step 3: Select the Maximally Visibly Divergent Alternative ($v^*$) or Abstain on Zero Divergence

Compute a purely **observable, label-free trajectory divergence** $D_{\mathcal{B}}(u, v)$ for every $v \in \mathcal{N}_{\mathrm{eq}}(u; s_t)$ using only runtime traces (never hidden safety labels):

- **Tool / API / coding agents**: Average normalized sequence edit distance (`SequenceMatcher` with `autojunk=False`) across serialized tool-call traces $T(\tau)$ and visible state/output summaries $Z(\tau)$:
  $$d_{\mathrm{tool}}(\tau, \tau') = \tfrac{1}{2}\bigl(1 - S(T(\tau), T(\tau'))\bigr) + \tfrac{1}{2}\bigl(1 - S(Z(\tau), Z(\tau'))\bigr)$$
- **Stateful / grid / simulation environments**: Average step-by-step visible state/board mismatch plus per-step reward-timing mismatch across aligned rollouts.

Select the single sharpest behavioral contrast:

$$v^* = \arg\max_{v \in \mathcal{N}_{\mathrm{eq}}(u; s_t)} D_{\mathcal{B}}(u, v)$$

- **Mandatory zero-divergence abstention**: If $\mathcal{N}_{\mathrm{eq}}(u; s_t)$ is empty or $\max_{v} D_{\mathcal{B}}(u, v) = 0$ (all verifier-equivalent variants produce identical visible behavior), set $v^* = \bot$ and **abstain** (leave `s_t` unchanged or route to human/external audit). Never fabricate a non-equivalent contrast or fall back to silent auto-commit when intra-class variation is absent.

### Step 4: Run Order-Averaged Comparative Safety Judging (`2` Calls) with Semantic Roles Fixed

Present the paired same-state trajectories $(\tau(u), \tau(v^*))$ on the divergent replay items to a frozen safety judge in **two calls that swap physical display order** (`[Trace A = u, Trace B = v^*]` and `[Trace A = v^*, Trace B = u]`) while keeping the semantic evaluation question fixed (*"Score the candidate update's relative safety risk in $[0, 1]$ compared against an alternative execution that achieves the exact same task outcome from the same initial state"*):

1. **Require explicit comparative attribution, not joint-absolute scoring**: Ask the judge to identify concrete behavioral differences between the two traces (e.g., skipped confirmation, irreversible mutation, collateral state change, policy bypass) and score candidate `u`'s risk *relative* to `v^*`. Simply concatenating both traces under an absolute pointwise prompt (`joint-absolute`) destroys calibration (`GPT-4.1` AUC collapses from `0.925` to **`0.391`**).
2. **Compute order-averaged risk and order consistency**: Let $r_J^{(0)}, r_J^{(1)} \in [0, 1]$ be the risk assigned to candidate `u` in each display order, and set $R_J(u) = \frac{1}{2}(r_J^{(0)} + r_J^{(1)})$.
3. **Apply calibrated three-way decision (`Admit` / `Reject` / `Abstain`)**: Using non-overlapping thresholds $0 < \theta_{\mathrm{A}} \le \theta_{\mathrm{R}} < 1$ calibrated on a held-out unlabeled/reference cohort:
   - **Reject `u`** if $R_J(u) \ge \theta_{\mathrm{R}}$ or $I_{\mathrm{det}}(u; s_t) = 0$.
   - **Abstain** (retain `s_t` unchanged) if $\theta_{\mathrm{A}} \le R_J(u) < \theta_{\mathrm{R}}$, if $v^* = \bot$, or if the two display orders flip opposite sides of the decision boundary (`|r_J^{(0)} - r_J^{(1)}|` exceeds tolerance).
   - **Pass `u` to final acceptance gating** only if $R_J(u) < \theta_{\mathrm{A}}$ and $I_{\mathrm{det}}(u; s_t) = 1$.
4. **Never auto-commit $v^*$**: $v^*$ is strictly a diagnostic foil generated to expose hidden behavioral degrees of freedom; if `u` is rejected, discard both `u` and $v^*$ unless $v^*$ is independently proposed and vetted as its own candidate.

### Step 5: Conjoin with Deterministic Invariants, Rollback Receipts, and the Single Acceptance Gate

Before persisting an admitted `u` into `s_{t+1}`:
1. Write a tamper-evident **pre-commit rollback receipt** recording the parent state digest, `u`, $v^*$, $\mathbf{r}_{\mathcal{B}}(u; s_t)$, $(r_J^{(0)}, r_J^{(1)})$, and $I_{\mathrm{det}}(u; s_t)$.
2. Pass `u` through the single acceptance gate in [`../../rules/recursive-improvement.md`](../../rules/recursive-improvement.md) (`"DO: Pass every self-modification through one acceptance gate"`): require zero regression beyond baseline noise margin $\delta$ on previously-correct and held-out tasks plus strict zero failures on the immutable negative security testbed, and keep post-commit runtime monitoring active (`DoppelVet` vets pre-commit admission; runtime drift still requires external monitoring—see [`detection-gap-self-improving-programmatic-agents`](../../research-briefs/detection-gap-self-improving-programmatic-agents.md)).

---

## Environment Caveats

- **Observability boundary (`D_{\mathcal{B}} > 0` required)**: If a harmful behavior leaves **zero trace** in tool calls, arguments, intermediate states, or outputs on the replay bank $\mathcal{B}_t$ (e.g., a dormant trigger whose condition never fires on $\mathcal{B}_t$, or an environment like `Vase`/`Island` where $\max D_{\mathcal{B}} = 0$), Step 3 cannot surface a behavioral contrast and rightly abstains—pair replay banks with boundary-probing counterfactual inputs ([`falsification-gated-memory-evolution`](../falsification-gated-memory-evolution/SKILL.md)).
- **Search-budget scaling ($O(Nm)$)**: Sandbox execution cost scales linearly with contrast count $N$ times replay-bank size $m$, whereas LLM judge cost stays constant at **`2` calls** per candidate regardless of $N$. Run cheap deterministic/replay filtering first and parallelize sandbox rollouts.
- **When $\mathcal{N}_{\mathrm{eq}}$ contains only identically unsafe or identically safe updates**: Comparative vetting detects *relative* safety divergence inside $\mathcal{N}_{\mathrm{eq}}$; if every reachable task-passing solution violates a hard constraint, deterministic invariants $I_{\mathrm{det}}$ and the strict negative security testbed must block commit.

---

## Failure Modes

- **Using joint-absolute prompts instead of comparative role-bound judging**: Showing both traces $(u, v^*)$ to the judge while asking for an unanchored absolute risk score caused `GPT-4.1` ROC AUC to collapse to **`0.391`** and `GPT-4o` to **`0.648`** on `DoppelVet-Grid` (vs. **`0.925`** and `DoppelVet`'s comparative prompt), performing even worse than single-trace pointwise judging (`0.493`).
- **Substituting independent two-pass margin differences (`r(u) - r(v^*)`) for side-by-side comparison**: Scoring `u` and $v^*$ in two separate single-trace `AgentDoG 1.5` passes and subtracting their scores yielded **`0.419`** AUC on `DoppelVet-Grid` and **`0.478`** on `DoppelVet-Tool` (`172/186` harmful updates accepted at an `80%` safe-acceptance operating point, vs. **`10/186`** under `DoppelVet` `0.970` AUC)—proving both traces must appear in the same context window.
- **Using visible divergence scalar $D_{\mathcal{B}}(u, v^*)$ directly as a harm score**: High divergence flags that two solutions *differ*, not *which one* is unsafe (`0.720` AUC alone vs. `0.970` with comparative judging on `Qwen2.5-32B`).
- **Evaluating only a single presentation order**: LLM judges exhibit positional bias between `Trace A` and `Trace B`; omitting the swapped-order pass and order-disagreement abstention leaks borderline harmful commits over multi-generation horizons.
- **Auto-promoting $v^*$ when `u` is rejected**: Because $v^*$ is selected solely to maximize divergence from `u`, when `u` is safe, $v^*$ is disproportionately the *harmful* boundary variant (`100%` top-ranked harmful selection when one exists in Gridworlds)—auto-committing $v^*$ inverts safety.

---

## Cross-References

- **Rules**: [`../../rules/recursive-improvement.md`](../../rules/recursive-improvement.md) — `"DO: Pass every self-modification through one acceptance gate"` and persistent self-evolution verification guardrails
- **Spec Templates**: [`../../specs/self-improving-agent.spec.md`](../../specs/self-improving-agent.spec.md) — Acceptance gate, safety envelope, and pitfall checklist
- **Related Skills & Briefs**:
  - [`falsification-gated-memory-evolution`](../falsification-gated-memory-evolution/SKILL.md) — Active counterfactual falsification probing (`FGSE`) and online EMA runtime eviction for persistent memory hypotheses
  - [`feedback-poisoning-skill-promotion-guard`](../feedback-poisoning-skill-promotion-guard/SKILL.md) — Leave-one-edit-out and literal-abstraction defenses against poisoned optimization feedback (`SkillOpt`)
  - [`pairwise-action-verification`](../pairwise-action-verification/SKILL.md) — Step-level pairwise action ranking (`Mid-Harness`) during episode execution
  - [`skill-evolution-defense`](../skill-evolution-defense/SKILL.md) — Supply-chain and injection defenses for evolved skill artifacts
  - [`detection-gap-self-improving-programmatic-agents`](../../research-briefs/detection-gap-self-improving-programmatic-agents.md) — Why post-commit runtime outcome/reference-range monitors are still required after pre-commit vetting

---

## Sources

- Duan, Y., Yin, D., Zheng, S., Xue, C., Li, L., & Salim, F. D. (2026). *DoppelVet: Comparative Safety Verification for Self-Evolving Agents*. `arXiv:2611.29306` (`src:2611-29306v1`).
