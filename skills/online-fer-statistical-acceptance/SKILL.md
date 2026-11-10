---
name: online-fer-statistical-acceptance
description: >
  Gate sequential candidate updates during multi-round harness self-improvement
  by controlling the False Evolution Rate (FER) across rounds via
  noninferiority-tolerant, overlap-corrected betting e-values and context-guided
  error-budget spending over a finite reused validation pool. Derived from TRUST
  (arXiv:2611.10787).
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Online FER Statistical Acceptance for Harness Evolution

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

Use this skill during **multi-round recursive self-improvement (RSI)** of an LLM agent harness (reasoning rules, retrieval/routing policies, episodic memory, or execution workflows) when:

- You have a **finite validation pool** $\mathcal{V}_N$ of size $N$ from which each round draws a validation subset of up to $n \le N$ tasks without replacement, returning those tasks to the pool between rounds.
- The proposer **observes closed historical feedback** (such as aggregate diagnostics or prior validation failures) across $T$ sequential rounds, creating adaptive data-reuse optimism that naive greedy validation gates mistake for genuine progress.
- Multi-round familywise error rate (FWER) gates (which bound the probability of *any* false promotion across all $T$ rounds) are too conservative for multi-component LLM harnesses and reject nearly all beneficial updates, whereas single-round e-process tests fail to bound cumulative error across rounds.

**Role in the acceptance architecture (deference to the repository gate):** This procedure governs **search-time sequential incumbent updates** ($\Theta_{t-1} \to \Theta_t$) across $T$ evolution rounds on $\mathcal{V}_N$. Final retention or deployment of the evolved harness $\Theta_T$ (or $\Theta_\tau$ when paired with [`self-evolution-stopping-rule`](../self-evolution-stopping-rule/SKILL.md)) **must** still pass `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../../rules/recursive-improvement.md): no regression beyond a baseline noise margin $\delta$ estimated from repeated runs ($\ge 3$) on the full frozen suite and held-out tasks never seen by the optimizer, behavioral trajectory verification that the targeted mechanism changed, and strict zero-tolerance enforcement (no margin) on the immutable held-out negative security testbed.

**Choosing between [`decision-only-sequential-acceptance`](../decision-only-sequential-acceptance/SKILL.md) (`Reuse`) and `online-fer-statistical-acceptance` (`TRUST`):**
- Use **`decision-only-sequential-acceptance`** when an acceptance split is scored in full every round and you can restrict proposer feedback from that split strictly to binary promote/reject decisions under an FWER budget.
- Use **`online-fer-statistical-acceptance`** when evolving multi-component LLM agent harnesses under a per-round evaluation cap ($n < N$) where the proposer uses closed round diagnostics to propose targeted repairs and you want to bound the **False Evolution Rate** ($\operatorname{FER}_\varepsilon(T) \le q$, the expected fraction of accepted updates whose true population change $\Delta_t = J(\widetilde{\Theta}_t) - J(\Theta_{t-1})$ falls at or below $-\varepsilon$).

*(Symbol note: throughout this skill, $q \in (0, 1)$ is the multi-round FER budget, $\varepsilon \in (0, 1)$ is the search-time noninferiority loss tolerance, and $\beta$ is the sample-overlap correction strength — distinct from the baseline noise margin $\delta$ in [`recursive-improvement.md`](../../rules/recursive-improvement.md).)*

---

## Step-by-Step Procedure

### Step 1: Partition Splits and Initialize the Online Error Budget

1. **Separate three disjoint task sets** before round $t = 1$:
   - An **initial diagnostic set** (e.g., 20 tasks) used to construct initial history $\mathcal{F}_0$ independent of $\mathcal{V}_N$.
   - A **reusable validation pool** $\mathcal{V}_N = (Z_1, \ldots, Z_N)$ (e.g., $N = 200$) used for sequential gate testing up to $n \le N$ draws per round (e.g., $n = 40$).
   - A **sealed held-out evaluation and negative security suite** (e.g., $N_{\mathrm{test}} = 300$ plus security testbeds) never exposed to the proposer, allocator, or search-time gate, reserved for `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../../rules/recursive-improvement.md).
2. **Configure interpretable gate parameters**:
   - Horizon $T \ge 1$ (e.g., $T = 30$), total FER budget $q \in (0, 1)$ (default `0.30`), noninferiority tolerance $\varepsilon \in (0, 1)$ (default `0.10`), and overlap correction strength $\beta \in [0, 1 - p_\varepsilon]$ where $p_\varepsilon = (1 - \varepsilon)/2$ (default `0.01`).
   - Spending-fraction clip bounds $0 < \rho_{\min} < \rho_{\max} < 1$ and per-round level cap $\alpha_{\max} \in (0, 1)$ (fixed before run start in implementation config).
3. **Initialize ledger state**:
   - Remaining FER budget $B_1 \leftarrow q$.
   - Accepted-update counter $R_0 \leftarrow 0$.
   - Cumulative exposed validation-index set $\mathcal{I}_{1,0} \leftarrow \varnothing$.

### Step 2: Propose One Bounded Atomic Candidate from Closed History

At round $t \in \{1, \ldots, T\}$:
1. Generate candidate harness modification(s) from completed history $\mathcal{F}_{t-1}$ only (never current-round validation items or sealed held-out splits). Each candidate should apply one atomic operator to one declared editable harness component (e.g., reasoning rules, context routing, episodic memory, or within-call workflow) while preserving the solver's output schema and frozen boundaries.
2. If the proposer emits multiple candidates (e.g., 3 proposals), screen them on closed prior-round examples (e.g., 20 examples from round $t - 1$) to select a single candidate $\widetilde{\Theta}_t$ for round-$t$ gate testing, and assemble pre-validation context $C_t$ summarizing the incumbent state, candidate diff, stated failure diagnosis, and closed prior-round diagnostics.

### Step 3: Allocate the Round Testing Level $\alpha_t$ with Context

Before drawing any round-$t$ validation task (fixing $\mathcal{F}_t^{\mathrm{pre}}$):
1. **Score contextual promise and risk**: Have an LLM allocator $\Psi$ (temperature `0`) evaluate $C_t$ across explicit criteria — safety preservation, output-contract preservation, actionability, generalization risk, and scope control — to emit a nonnegative multiplier $w_t = \Psi(C_t) \in [0, \infty)$ (or set $w_t \equiv 1$ if running without LLM budget guidance).
2. **Compute the clipped spending fraction** around an equal-share baseline $\rho_t^0 = 1 / (T - t + 1)$:
   $$\rho_t = \operatorname{clip}\!\left(\frac{w_t}{T - t + 1},\, \rho_{\min},\, \rho_{\max}\right)$$
3. **Allocate testing level $\alpha_t$ and charge the FER budget** (e-LORD / e-GAI generalized $\alpha$-investing):
   $$\alpha_t = \min\!\bigl\{\alpha_{\max},\, \rho_t B_t (R_{t-1} + 1)\bigr\}, \qquad B_{t+1} = B_t - \frac{\alpha_t}{R_{t-1} + 1}$$
   Notice two structural properties: (a) because $0 \le \alpha_t / (R_{t-1} + 1) \le \rho_t B_t \le B_t$, the remaining budget $B_{t+1}$ stays nonnegative; and (b) earlier accepted updates ($R_{t-1} > 0$) scale up the effective testing level $\alpha_t$ per unit of budget spent without violating $\operatorname{FER}_\varepsilon(T) \le q$, because the FER denominator $R_T \vee 1$ grows with each acceptance. If $\alpha_t = 0$, skip validation and retain $\Theta_t \leftarrow \Theta_{t-1}$.

### Step 4: Accumulate Overlap-Corrected Betting E-Values Sequentially

Initialize available pool indices $\mathcal{R}_{t,0} \leftarrow \{1, \ldots, N\}$, exposed set $\mathcal{I}_{t,0} \leftarrow \mathcal{I}_{t,0}$, acceptance flag $A_t \leftarrow 0$, stopping draw $\tau_t \leftarrow n$, and four mixture e-processes $M_{t,0}^{(\beta, \ell)} \leftarrow 1$ for betting fractions $(\eta^{(1)}, \eta^{(2)}, \eta^{(3)}, \eta^{(4)}) = (0.10, 0.25, 0.50, 0.75)$ (note: for asymptotic power consistency $\operatorname{TER}(T) \to 1$, theory bounds $\eta_{t,i} < 2\varepsilon / (1 + \varepsilon)$, whereas a finite-sample mixture across fixed fractions remains conditionally valid at any stopping time under Corollary 1).

For draw $i = 1, \ldots, n$:
1. **Compute exact pre-draw sample-reuse probability** $\zeta_{t,i}$ under uniform without-replacement sampling from $\mathcal{R}_{t,i-1}$:
   $$\zeta_{t,i} = \frac{|\mathcal{I}_{t,i-1} \cap \mathcal{R}_{t,i-1}|}{|\mathcal{R}_{t,i-1}|}$$
2. **Shift the rescaled null boundary for data-reuse optimism**:
   $$u_{t,i}^{(\beta)} = p_\varepsilon + \zeta_{t,i}\beta, \qquad \text{where } p_\varepsilon = \frac{1 - \varepsilon}{2}$$
3. **Draw and score paired execution**: Sample $K_{t,i}$ uniformly from $\mathcal{R}_{t,i-1}$, evaluate candidate $\widetilde{\Theta}_t$ and incumbent $\Theta_{t-1}$ on task $X_{t,i} = Z_{K_{t,i}}$ with scores in $[0, 1]$, compute paired difference $D_{t,i} \in [-1, 1]$, and rescale to $Y_{t,i} = (1 + D_{t,i}) / 2 \in [0, 1]$.
4. **Update the mixture e-value**:
   $$M_{t,i}^{(\beta, \ell)} = M_{t,i-1}^{(\beta, \ell)} \left[1 + \eta^{(\ell)} \frac{Y_{t,i} - u_{t,i}^{(\beta)}}{u_{t,i}^{(\beta)}}\right], \qquad M_{t,i}^{(\beta, \mathrm{mix})} = \frac{1}{4}\sum_{\ell=1}^{4} M_{t,i}^{(\beta, \ell)}$$
5. **Update index tracking**: $\mathcal{R}_{t,i} \leftarrow \mathcal{R}_{t,i-1} \setminus \{K_{t,i}\}$ and $\mathcal{I}_{t,i} \leftarrow \mathcal{I}_{t,i-1} \cup \{K_{t,i}\}$.
6. **Check anytime-valid early acceptance**: If $M_{t,i}^{(\beta, \mathrm{mix})} \ge 1 / \alpha_t$, set $A_t \leftarrow 1$, $\tau_t \leftarrow i$, and stop the sequential test. *(Implementation rule for proposer feedback parity: if you evaluate the remaining $n - \tau_t$ tasks in the batch so every closed round supplies an equal-sized 40-example diagnostic summary to the proposer, record **all $n$ drawn indices** in $\mathcal{I}_{t+1,0}$ so future $\zeta_{t',i}$ values reflect true feedback exposure.)*

### Step 5: Update Incumbent, Track Trajectory Drawdown, and Defer Final Commit to the Acceptance Gate

1. Set $\Theta_t \leftarrow \widetilde{\Theta}_t$ if $A_t = 1$, else retain $\Theta_t \leftarrow \Theta_{t-1}$; update $R_t \leftarrow R_{t-1} + A_t$.
2. Because Theorem 2 holds at **any** adaptive stopping time $\tau \le T$ with respect to $(\mathcal{F}_t)_{t=0}^T$, you may terminate the outer loop early using [`self-evolution-stopping-rule`](../self-evolution-stopping-rule/SKILL.md) without losing $\operatorname{FER}_\varepsilon(\tau) \le q$.
3. **Final commit gate**: Pass the final harness $\Theta_T$ (or $\Theta_\tau$) through `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../../rules/recursive-improvement.md) before keeping or deploying it. Never promote a harness that regresses beyond baseline noise $\delta$ on held-out tasks or fails any case on the immutable negative security testbed.

---

## Verified Empirical Reference (`TRUST`, `arXiv:2611.10787`)

Across 6 settings (`HotpotQA` Joint F1, `DROP` token F1, `APPS` test pass rate $\times$ `DeepSeek-V4-Flash` and `Qwen-3.8-Flash`; $T = 30$ rounds, 5 seeds, $N = 200$ validation pool, $n = 40$ per round, 20 initial examples, $N_{\mathrm{test}} = 300$ held-out test examples, defaults $q = 0.30, \varepsilon = 0.10, \beta = 0.01$):

- **6-setting average**: `TRUST` achieves the highest mean final gain of **`24.84 pp`** while cutting empirical strict false-acceptance ratio $\mathrm{FER}_0$ (proportion of accepted updates with $\widehat{\Delta}_t \le 0$) from **`45.59%` (`Greedy`) to `2.78%`** and cutting mean maximum drawdown ($\mathrm{MDD}$) from **`4.963 pp` (`Greedy`, worst setting `8.48 pp` on `APPS`/`DeepSeek-V4-Flash`) to `0.047 pp` (worst setting `0.27 pp` on `APPS`/`Qwen-3.8-Flash`)**.
- **Comparison against FWER and single-round statistical gates**: Multi-round FWER baselines `SGM-B` (Bernstein) and `SGM-H` (Hoeffding) at $\delta = 0.5$ accept `0` and `3` total updates across all runs (`0.00 pp` gain in 6/6 settings for `SGM-B` and 4/6 settings for `SGM-H`). Single-round e-process `PACE` ($\alpha = 0.05$, bet `0.5`) controls risk but trails `TRUST` in both Gain and True Evolution Rate (`TER`) in **all 6 settings** (e.g., `DROP`/`Qwen-3.8-Flash`: `TRUST` `17.22 ± 1.49 pp`, `TER = 10.76%` vs `PACE` `13.22 ± 3.77 pp`, `TER = 5.23%`; `APPS`/`DeepSeek-V4-Flash`: `TRUST` `34.55 ± 1.04 pp`, `TER = 11.64%` vs `PACE` `28.68 ± 2.66 pp`, `TER = 5.19%`).
- **LLM context allocator impact (`HotpotQA`/`DeepSeek-V4-Flash`)**: Replacing $w_t = \Psi(C_t)$ with fixed $w_t \equiv 1$ lowers final test Joint F1 from **`44.91 ± 1.36%` to `43.78 ± 1.18%`** (in seed 3, the allocator flags an unsafe partial reasoning edit in round 2 as `very_conservative`, rejecting a premature branch and reaching `47.22%` vs `43.95%`).

---

## Environment Caveats & Parameter Sensitivity

- **Setting $\varepsilon = 0$ freezes acceptance**: Under strict zero-tolerance noninferiority ($\varepsilon = 0$), the asymptotic betting upper bound $2\varepsilon / (1 + \varepsilon)$ collapses to `0`; empirically on `HotpotQA`/`DeepSeek-V4-Flash` (Table 8), $\varepsilon = 0$ yields **`0.00 ± 0.00 pp` gain (`0.00%` TER)**, $\varepsilon = 0.05$ delays gains until round 21 (`4.87 ± 3.00 pp`), $\varepsilon = 0.10$ achieves **`11.58 ± 1.30 pp` (`0.02 pp` MDD, `10.00%` $\mathrm{FER}_0$)**, and $\varepsilon = 0.15$ spikes $\mathrm{FER}_0$ to **`57.68 ± 4.55%`** and MDD to **`5.33 ± 0.90 pp`**. Keep $\varepsilon$ small and reserve strict zero-tolerance checks for the negative security testbed and final held-out gate.
- **Tuning $\beta$ to feedback richness**: `TRUST` does not estimate $\beta$ automatically from data. On `HotpotQA`/`DeepSeek-V4-Flash` (Table 9), $\beta = 0$ (no overlap correction) suffers **`23.33 ± 14.53%` $\mathrm{FER}_0$** and **`1.27 ± 0.90 pp` MDD** (`10.97 ± 1.86 pp` gain); $\beta = 0.01$ peaks at **`11.58 ± 1.30 pp` gain** (`10.00%` $\mathrm{FER}_0$, `0.02 pp` MDD); over-correcting at $\beta = 0.03$ or $0.05$ drives $\mathrm{FER}_0$ to `0.00%` but suppresses gain to `7.13 ± 2.97 pp` and `2.80 ± 2.80 pp`. Use larger $\beta$ only when proposers inspect verbatim failed validation items rather than coarse aggregate error counts.
- **Keep $n / N$ small**: Power consistency (Theorem 3) relies on $n / N \to 0$ so overlap fraction $\zeta_{t,i}$ grows gradually rather than saturating the pool in 1–2 rounds.

## Failure Modes to Avoid

1. **Omitting post-stopping feedback draws from $\mathcal{I}_{t+1,0}$**: If sequential testing accepts early at draw $\tau_t < n$ (e.g., draw 14 of 40) _and_ you still run draws $15..40$ to feed diagnostics to next round's proposer, failing to add draws $15..40$ into $\mathcal{I}_{t+1,0}$ undercounts $\zeta_{t',i}$ and invalidates Assumption 1.
2. **Allowing exact-question answer caching in episodic memory**: In `TRUST`'s overfitting stress test (Appendix I, 20 reused examples on `HotpotQA`), `Greedy` raised validation Joint F1 by **`+24.44 pp`** while held-out test gain peaked at `+5.06 pp` after round 1 and fell to **`-2.15 pp` by round 10** (a single episodic memory lowered test Joint F1 from `54.55%` to `48.00%` across 100 test items by crowding out required second-hop Wikipedia passages). Restrict memory operators to cluster-ranked procedural guidance rather than verbatim validation Q&A lookup.
3. **Allowing the LLM allocator to inspect current-round validation scores**: $w_t = \Psi(C_t)$ is valid **only** when $C_t \subseteq \mathcal{F}_t^{\mathrm{pre}}$ (computed strictly before observing $D_{t,1}, \ldots, D_{t,n}$). Peeking at current-round outcomes breaks Theorem 1 (`E[M | F_t^pre] <= 1`).
4. **Treating search-time FER control as a substitute for the final acceptance gate**: $\operatorname{FER}_\varepsilon(T) \le q$ bounds the *expected proportion* of accepted updates losing more than $\varepsilon$, which still permits minor drift within $(-\varepsilon, 0]$ or rare tail errors; always run the final held-out and security gate in [`recursive-improvement.md`](../../rules/recursive-improvement.md) before deployment.

## Related Skills

- [`decision-only-sequential-acceptance`](../decision-only-sequential-acceptance/SKILL.md) — FWER-controlled acceptance when evaluating every candidate on a full reused split and returning only binary accept/reject decisions (`arXiv:2609.33180`)
- [`self-evolution-stopping-rule`](../self-evolution-stopping-rule/SKILL.md) — Restart e-detector stopping time $\tau \le T$ that composes directly with `TRUST`'s anytime-valid FER guarantee (`arXiv:2610.04756`)
- [`regularized-harness-evolution`](../regularized-harness-evolution/SKILL.md) — Bounded editable harness envelope and baseline noise estimation $\delta$ (`arXiv:2609.24972`)
- [`scoped-multi-agent-harness-composition`](../scoped-multi-agent-harness-composition/SKILL.md) — Component-scoped multi-agent role, coordination, and memory-policy editing (`arXiv:2611.12552`)
