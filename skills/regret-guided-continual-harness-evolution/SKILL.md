---
name: regret-guided-continual-harness-evolution
description: >
  Stabilize reference-free continual playbook and harness evolution across
  drifting tool schemas, workflows, and multi-session memories by keying
  bounded playbooks to Turn-0 interface signatures, grading rollouts via
  deterministic sandbox checks plus Turn-0 atomic checklists, ranking criteria
  by paired directional regret, pooling parallel contrastive strategy
  candidates, and gating edits with Soft-HURT and one-pass [iff] scope guards.
  Derived from "GUARD: Stabilizing Recursive Self-Improvement with Regret
  Guidance" (arXiv:2611.23476).
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Regret-Guided Continual Harness Evolution

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

Use this skill when running **reference-free (grader-free) continual harness, playbook, or cross-session memory evolution** around a frozen LLM agent where:

- The agent adapts across **drifting tool schemas, evolving MCP servers, unannounced domain/workflow shifts, or rubric-dense professional workflows** (for example, versioned enterprise APIs, streaming SQL/function-calling suites, multi-session user preference memory, or legal/financial analytical agents) without access to ground-truth answer keys or external benchmark graders during adaptation.
- Aggregate evolve-set noise-band gates (`RRSI`) or Pareto prompt pools (`GEPA`, `Meta-Harness`) suffer **per-task regression masking, prompt bloat, negative forward/backward transfer, or procedural memory pollution** when new rules overwrite previously mastered behaviors.
- You want a **single frozen `pass@1` system playbook** at deployment time ($O(1)$ inference overhead) rather than multi-rollout test-time search.

Do **not** use this skill when **external or executable task verifiers** (unit tests, database-state validators, exact-match keys) are available at adaptation time—use [`falsification-gated-memory-evolution`](../falsification-gated-memory-evolution/SKILL.md) (`FGSE`) instead—or when subsampling a **stationary, ground-truth-scored validation pool** across dozens of search rounds where sequential False Evolution Rate (`FER`) bounds apply—use [`online-fer-statistical-acceptance`](../online-fer-statistical-acceptance/SKILL.md) (`TRUST`).

## Overview

In continual, reference-free self-improvement, an aggregate score rise on an adaptation block regularly conceals severe regressions on previously working tasks or adjacent tool versions. In `GUARD` (`arXiv:2611.23476`), removing regret-ordered criterion analysis drops `5`-domain `EvoHarnessBench` local-gym accuracy by `-7.33 pp` (`66.46% -> 59.13%`, regressing `CSM` by `-22.46 pp` and `ITSM` by `-14.16 pp`), while removing per-task `Soft-HURT` admission gating drops accuracy by `-10.35 pp` (`66.46% -> 56.11%`, where an unvetted `ITSM v4` edit hallucinates `get_current_user` and collapses stage accuracy to `7.61%`).

`GUARD` closes a three-stage continual loop (`Analyze -> Propose -> Gate`) over bounded, signature-keyed playbooks $W_{t,g}$ without ground-truth labels:

- **Hosted `EvoHarnessBench` SDK (`evolving_tools/calendar` `v1–v3`, single-model `Gemini 4`)**: Reaches **`80.80%` official ACC** (`+8.89 pp` over `W_0` `71.91%`, $p = 0.008$, `8` better / `0` worse; beating `Meta-Harness` `74.52%`, `RRSI` `74.28%`, `GEPA` `70.69%`, and `MemToolAgent` `68.00%`) and **`58.14%` Solved** (`25/43` vs. `<= 22/43`), achieving **`0.00 pp` forward negative transfer** (`BWT Score +0.85 pp`, `BWT Pass +2.56 pp`, vs. `-13.21 pp` FWT on `Meta-Harness` and `-3.97 pp` BWT on `GEPA`) while **cutting inference tokens by `54.5%` (`131,032 -> 59,651` tokens/task)**, MCP calls by `22.5%` (`14.47 -> 11.21`), 8-step turn exhaustions to `0/43` (vs. `6–10/43`), and playbook length to `2,315` chars (vs. `4,538–10,013`).
- **`Drift Gauntlet` (`4` hidden-boundary streams, `12` blocks, `360` adapt / `360` test)**: Achieves **`73.22%` Final Mean** (`+3.30 pp` over `No-Evolve` `69.92%`, beating `GEPA` `72.40%`, `Meta-Harness` `71.21%`, `Hermes+` `70.31%`, and `RRSI` `67.92%`) with **`0.00 pp` stream forgetting** and **`0/12` block drops** (vs. `-8.11 pp` forgetting on `RRSI` [`-20.00 pp` on workflow drift] and `3–8/12` block drops across every baseline).
- **`PAST-Bench` (`12` stateful memory families)**: Leads procedural update (`0.830`), mechanism (`0.878`, $p = 0.016$ vs. `RRSI` `0.725`), fact supersession (`0.924`, `+13.3 pp` over `Hermes+` `0.791` and `+14.8 pp` over `GEPA` `0.777`), write precision (`0.776`, $p = 0.031$ vs. `RRSI` `0.438`), and `Evolve` (`0.436`), while holding memory pollution to **`0.167` overall and `0.000` on procedural tasks** (vs. `0.500` overall / `1.000` procedural pollution on `RRSI` and `Meta-Harness`). Across `19` execution-gated promotions on `EvoHarnessBench`, **`19/19` (`100%`) yield non-negative held-out $\Delta_{\text{test}} \ge 0$** (`15` strictly positive, `4` ties).

---

## Step-by-Step Procedure

### Step 1: Key Bounded Playbooks to Turn-0 Signatures and Grade via Two-Layer Checklists

Partition evolving instructions by observable interface rather than maintaining one monolithic global prompt or relying on unanchored prose self-critique:

1. **Key playbook sections by Turn-0 interface signature**: Map each incoming task $q$ at `Turn-0` (strictly before any tool call executes) to a deterministic signature $g \in \mathcal{G}$ derived solely from observable tool declarations, parameter schemas, or database identifiers (for example, toolset family `bfcl`, environment schema `sciworld`, or database schema `bird:<db_id>`). Bound each section $W_{t,g}$ to a fixed character budget $B_W \in [2{,}315, 4{,}200]$ chars and inject it at both the start and end of the system prompt to counter middle-context dilution.
2. **Synthesize and cache Turn-0 atomic checklists $\mathcal{C}(q)$**: From the public task prompt and `Turn-0` tool declarations alone (**never** benchmark rubrics, hidden state, or reference answers), generate and cache `4–8` atomic binary predicates $c \in \mathcal{C}(q)$ spanning execution-verifiable preconditions (parameter types, required lookup sequence, non-empty outputs) and semantic task obligations (completeness, unit/timezone fidelity, explicit abstention when data is absent).
3. **Score adaptation rollouts with a two-layer reference-free reviewer**:
   - **Layer 1 (Deterministic Sandbox & Execution Audit)**: Parse actual tool call records, return statuses, schema errors, and sandbox post-states directly. Flag blocking execution errors deterministically (`Layer-1` pass vs. fail separates held-out official accuracy by `+27.92 pp`—`73.90%` vs. `45.97%`, `82.6%` NPV across `4,059` rollouts).
   - **Layer 2 (Trace-Grounded Per-Criterion Self-Review)**: Evaluate each $c \in \mathcal{C}^{\mathrm{gr}}(\tau)$ against concrete tool-output spans, treating any unparseable verdict as `0` (fail) or falling back to deterministic trace assertions. Combine into continuous score $S(\tau) = \frac{100}{|\mathcal{C}^{\mathrm{gr}}(\tau)|} \sum_{c \in \mathcal{C}^{\mathrm{gr}}(\tau)} r(\tau, c)$ and strict score $S^{\mathrm{strict}}(\tau)$ (`0` on blocking Layer-1 sandbox error, `100` if all graded criteria pass, and $S(\tau)/2$ otherwise). *(Single-layer LLM review falsely passes `22.2%` [`12/54`] of execution-broken traces vs. **`0.0%` [`0/23`]** under two-layer review, costing `-4.82 pp` ACC and `-9.30 pp` Solved.)*
   - **Stateful multi-session memory variant**: When adapting cross-session memory write paths (`PAST-Bench`), evaluate the incumbent and all candidates in a **single joint critic pass** against four fixed write-path criteria (fact supersession, constraint preservation, procedure scoping, and zero transient scratchpad pollution) so relative ranking stays calibrated across sessions.

### Step 2: Rank Criteria by Paired Directional Regret and Pin Mastered Rules (`Analyze`)

Before proposing edits on active evaluation slice $\mathcal{Q}_g$ (combining current-block frontier tasks with up to `10` same-signature reservoir-replayed tasks sampled via Vitter's Algorithm R from a bounded `24`-task stream buffer), compute per-criterion obedience $\mathrm{obey}(c; W) = \frac{1}{|\mathcal{T}_c(W)|} \sum_{\tau \in \mathcal{T}_c(W)} r(\tau, c) \in [0, 1]$ and decompose two directional signals:

$$\Delta_{\mathrm{hurt}, t}(c) = \max\!\bigl(0,\; \mathrm{obey}(c; W_{t-2}) - \mathrm{obey}(c; W_{t-1})\bigr), \qquad \Delta_{\mathrm{gap}, t}(c) = 1 - \mathrm{obey}(c; W_{t-1})$$

$$\mathrm{Priority}_t(c) = \Delta_{\mathrm{hurt}, t}(c) + \Delta_{\mathrm{gap}, t}(c) \in [0, 2]$$

1. **Preserve failure visibility after rejected rounds**: Whenever round $t - 1$ rejected its candidate ($W_{t-1} = W_{t-2}$), compute $\Delta_{\mathrm{hurt}, t}(c)$ from $W_{t-1}$ to the rejected candidate $\widetilde{W}_{t-1}$ (or its scope-repaired variant $\widetilde{W}_{t-1}^{\mathrm{rep}}$) under execution scoring so the next round sees exactly which criterion the rejected edit broke rather than collapsing $\Delta_{\mathrm{hurt}, t}$ to zero.
2. **Partition criteria into three action classes**:
   - **`Regressed` ($\Delta_{\mathrm{hurt}, t}(c) > 0$)**: Ranked strictly highest (a fresh binary regression $1 \to 0$ scores $\mathrm{Priority}_t = 2$, strictly outranking every non-regressed gap $\le 1$). Instruct the proposer to **wrap the offending rule in an explicit `[iff <observable precondition>]` guard** rather than deleting valid coverage.
   - **`Unsolved Gap` ($\Delta_{\mathrm{hurt}, t}(c) = 0, \Delta_{\mathrm{gap}, t}(c) > 0$)**: Ranked below regressions by missing obedience mass; target with concise precondition-bound guidance.
   - **`Mastered` ($\mathrm{Priority}_t(c) = 0 \iff \mathrm{obey}(c; W_{t-1}) = 1 \land \Delta_{\mathrm{hurt}, t}(c) = 0$)**: **Pin explicitly against modification or deletion** during rewriting.
3. **Attach capped same-task trajectory contrasts**: Extract at most `6` paired same-task trajectory diffs $(\tau^+, \tau^-)$ across rounds where $\Delta^{\mathrm{strict}} > 0$ or $\Delta^{\mathrm{cont}} \ge \delta_{\mathrm{con}}$ (default $\delta_{\mathrm{con}} = 10$ points) to ground diagnosis in concrete tool-call divergences.

### Step 3: Pool Parallel Candidates and Evolve Strategy Prompts Contrastively (`Propose`)

Rather than running $2T$ sequential single-candidate rounds ($M = 1$), allocate adaptation rollouts across $M \ge 2$ parallel candidates per round (default $M = 2$; $M = 4$ on dense professional rubrics) initialized from a uniform domain-agnostic seed strategy $s_0$:

1. **Evaluate all $M$ candidates on identical $(W_{t-1,g}, \mathcal{B}_{t,g}, \mathcal{Q}_g)$**: Using per-task noise floor $\delta_{\mathrm{noise}} = 15$ (on the `[0, 100]` scale), compute helped and hurt task sets:
   $$\mathcal{Q}_m^+ = \bigl\{q \in \mathcal{Q}_g : S_q(\widetilde{W}_t^{(m)}) - S_q(W_{t-1}) > \delta_{\mathrm{noise}}\bigr\}, \qquad \mathcal{Q}_m^- = \bigl\{q \in \mathcal{Q}_g : S_q(W_{t-1}) - S_q(\widetilde{W}_t^{(m)}) > \delta_{\mathrm{noise}}\bigr\}$$
2. **Rank via regression-asymmetric group-standardized advantage**: Compute blended performance $\mathrm{Perf}_m = \bar{S}^{\mathrm{strict}}(\widetilde{W}_t^{(m)}) + \frac{1}{4}\bar{S}(\widetilde{W}_t^{(m)})$, regression-penalized fitness $R_m = \mathrm{Perf}_m - \beta |\mathcal{Q}_m^-| + \gamma |\mathcal{Q}_m^+|$ with $\beta = 3.5 > \gamma = 1.5$, and group-standardized advantage $\hat{A}_m = (R_m - \mu_R) / (\sigma_R + 10^{-6})$. Forward $m^\star = \arg\max_m \hat{A}_m$ to Step 4.
3. **Scrub instance identifiers and run `ContrastEvolve`**: Replace concrete task IDs and entity literals with `<TASK_ID>` placeholders so strategy meta-prompts cannot memorize validation items. Pair the winner $m^+ = m^\star$ against the lowest-fitness peer $m^- = \arg\min_{m \ne m^+} R_m$ to synthesize next-round strategy pool $\mathcal{P}_{t+1,g} = \{s_{t+1}^+\}^{\lfloor M/2 \rfloor} \cup \{s_{t+1}^-\}^{M - \lfloor M/2 \rfloor}$: $s_{t+1}^+$ reinforces scoped high-gain patterns, while $s_{t+1}^-$ converts $m^-$'s hurt tasks into narrower `[iff <precondition>]` rules and explicitly bans `[always]` directives or rules that trigger extra tool calls during final-answer formatting. *(At equal rollout budget $TM = 2T = 396$, parallel $M = 2$ beats sequential $M = 1$ by `+2.23 pp` [$81.08\%$ vs. $78.85\%$, $p = 0.0267$] while cutting rejected gate rounds by `64%` [`4` vs. `11`].)*

### Step 4: Enforce `Soft-HURT` Admission, One-Pass `[iff]` Scope Repair, and Windowed Rejection Logging (`Gate`)

Gate the top candidate $\widetilde{W}_t = \widetilde{W}_t^{(m^\star)}$ on **both** bounded per-task hurt count and positive net margin over total hurt magnitude $\mathrm{Hurt}(\widetilde{W}_t, W_{t-1}) = \frac{1}{|\mathcal{Q}_g|} \sum_{q \in \mathcal{Q}^-} \bigl(S_q(W_{t-1}) - S_q(\widetilde{W}_t)\bigr)$:

1. **Check `Soft-HURT` admission**: Admit $\widetilde{W}_t$ directly only if all three conditions hold:
   - $|\mathcal{Q}^-| \le h_{\max}$ (set $h_{\max} = 0$ prior to repair on continual tool-version and stream-drift suites; default $h_{\max} = 1, \mu_{\min} = 1.5$; on large multi-criterion professional suites, $h_{\max} = \mathrm{round}(0.18|\mathcal{Q}_g|), \mu_{\min} = 3.0$),
   - $|\mathcal{Q}^+| \ge \mathbb{I}\!\left[|\mathcal{Q}^-| > 0\right]$ (at least one task meaningfully helped whenever any hurt occurs), and
   - $\bar{S}(\widetilde{W}_t) - \bar{S}(W_{t-1}) > \max\!\bigl(\mathrm{Hurt}(\widetilde{W}_t, W_{t-1}),\; \mu_{\min}\mathbb{I}[|\mathcal{Q}^-| > 0]\bigr)$.
2. **Run at most one `[iff]` scope-guard repair on isolated hurts**: If $\widetilde{W}_t$ shows positive gain but fails solely due to $1 \le |\mathcal{Q}^-| \le h_{\mathrm{rep}}$ isolated hurt tasks ($h_{\mathrm{rep}} \in \{1, 2, 3\}$), invoke **at most one** in-round scope repair $\widetilde{W}_t^{\mathrm{rep}}$ that leaves existing rules intact and wraps only the newly added rule(s) in `[iff <distinguishing Turn-0 or tool-state condition>]` separating $\mathcal{Q}^+$ from $\mathcal{Q}^-$, then re-verify on $\mathcal{Q}_g$ ($h_{\max} = 1, \mu_{\min} = 0$). Never loop multi-pass exception patches.
3. **Abstain cleanly and append to a windowed rejection ledger**: If both $\widetilde{W}_t$ and $\widetilde{W}_t^{\mathrm{rep}}$ fail, **retain $W_{t-1}$ unchanged** (enabling safe abstention when schemas shift incompatibly, as in `calendar v2 -> v3` where `GUARD` abstains with `0.00 pp` negative transfer while `Meta-Harness` drops `-13.21 pp`) and append a deduplicated, ID-scrubbed failure record (broken criteria, hurt magnitude, offending rule diff) to JSONL ledger $\mathcal{L}_g$. Read back only the most recent $L_{\max} \in \{12, 40\}$ entries per round so proposer prompt prefill remains $O(1)$ in horizon $T$.

### Step 5: Deploy Frozen `pass@1` Playbooks Behind the Single Acceptance Gate

1. **Strip evolution scaffolding at inference**: Discard $\mathcal{P}_{t,g}$, the two-layer self-reviewer, reservoir buffers, and $\mathcal{L}_g$ at deployment time; serve only the compact signature-routed playbook $W_{T,g}$ (`<= 4,200` chars) in a single `pass@1` rollout.
2. **Defer persistent cross-stage or production promotion to the single acceptance gate**: `Soft-HURT` is an online, reference-free continual selection filter—before promoting an evolved playbook snapshot into a persistent production release, pass it through `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../../rules/recursive-improvement.md): require no regression beyond baseline noise margin $\delta$ (estimated from at least `3` unchanged baseline runs) on protected previously-correct cases and held-out tasks, and enforce **strict zero tolerance (no margin)** on the immutable negative security testbed.

---

## Environment Caveats

- **Tasks with exact executable graders**: When unit tests, SQL result keys, or deterministic simulator predicates already exist during adaptation, use them directly via [`falsification-gated-memory-evolution`](../falsification-gated-memory-evolution/SKILL.md) rather than approximating task correctness with Layer-2 semantic checklists.
- **Opaque routing environments**: Even when `Turn-0` tool signatures are identical across tasks (collapsing $|\mathcal{G}| = 1$ into a single global playbook), `Analyze + Propose + Soft-HURT` still delivers `74%` of `GUARD`'s stream-drift gain (`72.35%` vs. `73.22%` Final Mean on `Drift Gauntlet`) while preserving **`0.00 pp` forgetting**. Never fabricate post-hoc task-type labels from mid-episode trajectories to route `Turn-0` prompts.
- **Playbook length discipline**: Unbounded append-only playbooks degrade tool-calling precision and inflate inference tokens (`MemToolAgent` and `Meta-Harness` grow to `4,538–10,013` chars and consume `2.2x` more tokens/task than `GUARD`'s `2,315`-char bounded section). Enforce hard character caps $B_W$ by consolidating superseded clauses while keeping `Mastered` criteria pinned.

## Failure Modes

- **Single-layer prose self-review (`w/o Layer 1`)**: Allowing an LLM judge to grade trajectories without deterministic sandbox/tool-error parsing lets `22.2%` (`12/54`) of execution-broken traces pass review and degrades held-out accuracy by `-4.82 pp` (`-9.30 pp` Solved).
- **Resetting $\Delta_{\mathrm{hurt}, t}$ to zero after rejected rounds**: If $W_{t-1} = W_{t-2}$ causes $\Delta_{\mathrm{hurt}, t}(c)$ to evaluate to `0`, the proposer repeats the exact same over-broad edit in round $t$. Always compute post-rejection hurt against the rejected candidate $\widetilde{W}_{t-1}$.
- **Permitting `[always]` rules or final-turn tool triggers**: Unconditional rules (`ALWAYS call get_current_user first`) break across tool-schema versions (`ITSM v4` collapse to `7.61%`) and inflate step counts into turn-limit exhaustion. Require `[iff <observable condition>]` scoping on every conditional workflow rule.
- **Unbounded rejection-ledger injection**: Feeding the entire historical rejection log into the proposer linearly inflates context cost over long streams and induces conflicting negative constraints; window read-back to $L_{\max} \in \{12, 40\}$ deduplicated entries.

## Cross-References

- Acceptance governance: [`recursive-improvement.md`](../../rules/recursive-improvement.md) (`"DO: Pass every self-modification through one acceptance gate"`)
- Bounded search-space rules: [`skill-system-design.md`](../../rules/skill-system-design.md) (`"DO: Bound the search space of harness self-evolution"`)
- Executable-verifier falsification gating when external verifiers exist: [`falsification-gated-memory-evolution`](../falsification-gated-memory-evolution/SKILL.md)
- Offline regularized single-edit harness evolution: [`regularized-harness-evolution`](../regularized-harness-evolution/SKILL.md)
- Sequential statistical FER control on subsampled validation benchmarks: [`online-fer-statistical-acceptance`](../online-fer-statistical-acceptance/SKILL.md)
- Separating persistent failure ledgers from active execution context: [`knowledge-compounding-loop`](../knowledge-compounding-loop/SKILL.md)
