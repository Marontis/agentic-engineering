---
name: mcts-full-harness-optimization
description: >
  Optimize complete executable agent harnesses (context construction, memory/state tracking, control flow, and tool interfacing) under a small evaluation budget using top-K shortlisted Monte Carlo Tree Search with noise-calibrated exploitation, direct-child exploration, an execution experience archive, and a copy-on-adopt component library. Derived from HarnessFlow (arXiv:2611.06254).
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# MCTS-Guided Full-Harness Optimization

> **Source**: [arXiv:2611.06254](https://arxiv.org/abs/2611.06254) | `src:2611-06254`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

- Evolving an agent's complete executable harness—spanning context assembly, state/memory tracking, multi-step control flow, verification loops, and tool adapters—rather than tuning isolated prompt strings or single module slots.
- Operating under a tight candidate-evaluation budget (such as $N = 15$ candidate attempts) where sequential single-lineage refinement (`Meta-Harness`) gets trapped in local optima or discards promising earlier branches.
- Adapting a general-purpose or baseline agent scaffold to a specific operational domain (conversational tool use, multi-app workflows, repository issue resolution, or web navigation) while reducing per-task inference cost.

## When NOT to Use

- Optimizations restricted strictly to text instructions or system prompts with no permission to edit executable harness code (use [`iterative-instruction-refinement`](../iterative-instruction-refinement/SKILL.md) or [`error-structured-prompt-optimization`](../error-structured-prompt-optimization/SKILL.md)).
- Environments without a deterministic, reproducible validation split or where the evaluation runtime cannot be snapshotted across rounds.

---

## Core Insight

Hand-engineered production harnesses (`Claude Code`, `Codex`, `OpenHands`, `Hermes`) bundle fixed design choices for context compaction, tool formatting, and error recovery that frequently mismatch a target domain's failure profile while consuming `2–3x` higher token costs than necessary. Conversely, automated harness optimizers that restrict edits to pre-selected module slots or overwrite a single active lineage (`Meta-Harness`) suffer from **lineage amnesia**: when a code edit regresses performance or hits a dead end, linear iteration cannot easily branch from an earlier ancestor while retaining the diagnostic lessons of the failed attempt.

`HarnessFlow` solves this by representing every candidate harness $h_i$ as a complete, self-contained codebase inside a persistent **search tree** $\mathcal{G}_n = (\mathcal{V}_n, \mathcal{E}_n)$ paired with a global **experience archive** $\mathcal{A}$ and a read-only **Harness Component Library** $\mathcal{L}$. On `4` of `6` major benchmarks (`TAU2-bench`, `AppWorld`, `WebShop`, `BrowseComp-Plus`, `SWE-bench Verified`, `BigCodeBench-Hard`), the final winning harness is discovered at **round 10 or later** by branching off an earlier retained node rather than the immediately preceding candidate—raising the 6-benchmark test average from `58.59%` (`Vanilla`) and `64.82%` (`Codex`) to **`69.48%`** at **41.4% of `Codex`'s per-task execution cost** (`$0.232` vs. `$0.561` arithmetic mean; `$0.101` vs. `$0.351`+ geometric mean).

---

## The Procedure

### Step 1: Initialize the Root Workspace, Experience Archive, and Component Library

1. **Snapshot the Root Harness ($u_0$)**: Place the baseline executable harness $h_0$ in an isolated workspace directory and evaluate it $R = 5$ times on the fixed validation split $\mathcal{D}_v$ (never exposing the held-out test split $\mathcal{D}_t$ to the optimizer) to record its initial validation score $q_0$ and task-level execution records $\mathcal{R}_0$.
2. **Initialize the Global Experience Archive ($\mathcal{A}_1$)**: Store the tuple $(h_0, \Delta_0 = \varnothing, q_0, \mathcal{R}_0)$ in $\mathcal{A}$. Across all subsequent rounds, $\mathcal{A}$ records *every* evaluated candidate—including non-improving branches—along with its code diff $\Delta_n$ against its parent, its validation score $q_n$, its parent-relative score delta $q_n - q_{p_n}$, and full per-task trajectories and failure logs $\mathcal{R}_n$.
3. **Mount a Read-Only Copy-on-Adopt Component Library ($\mathcal{L}$)**: Provide a read-only directory of self-contained, standard-library reference primitives organized by the four core harness roles:
   - *Context construction*: observation packers, token-budget estimators, diff/patch compactors, history summarizers.
   - *Memory & state tracking*: key-value working memory, entity/symbol ledgers, goal-progress checklists.
   - *Control flow*: retry/backoff controllers, pre-submission self-review gates, loop/stall detectors, fallback routers.
   - *Tool interfacing*: argument schema validators, output parsers, error-message normalizers, interpreter compatibility wrappers.
   Require the coding agent to **copy and adapt** selected primitives directly into the candidate harness workspace rather than importing from $\mathcal{L}$ at runtime, keeping every candidate self-contained.

### Step 2: Select a Parent Node via Shortlisted, Noise-Calibrated MCTS

At candidate attempt $n \in \{1, \dots, N\}$ (default budget $N = 15$):

1. **Form the Top-$K$ Shortlist ($\mathcal{C}_n$)**: Rank all existing tree nodes $\mathcal{V}_{n-1}$ by validation score $q_i$ (breaking ties by creation order) and retain up to $K = 5$ highest-scoring nodes. Shortlisting prevents low-scoring broken harnesses from consuming expansion budget under small $N$.
2. **Compute the Noise-Calibrated Exploitation Distribution ($P_{\text{exploit}}$)**:
   - Estimate the validation score's standard error across shortlisted nodes $J = \{i \in \mathcal{C}_n : M_i > 0 \text{ and } 0 < q_i < 1\}$ (where $M_i$ is the number of validation cases):
     $$\tau = \operatorname{clip}\!\left(\max_{i \in J} \sqrt{\frac{q_i(1 - q_i)}{M_i}},\, 0.005,\, 0.100\right)$$
     (defaulting to $\tau = 0.08$ if $J$ is empty). Tying $\tau$ to the validation split's binomial standard error eliminates per-benchmark temperature tuning.
   - Compute softmax probabilities over $\mathcal{C}_n$:
     $$P_{\text{exploit}}(i) = \frac{\exp(q_i / \tau)}{\sum_{u_j \in \mathcal{C}_n} \exp(q_j / \tau)}$$
3. **Compute the Direct-Child Exploration Distribution ($P_{\text{explore}}$)**:
   - Let $d_i$ be the number of **direct children** already expanded from node $u_i$ (using direct-child count rather than total subtree size prevents an early productive branch from permanently starving its own parent or siblings).
   - With decay exponent $\alpha = 1$:
     $$P_{\text{explore}}(i) = \frac{(1 + d_i)^{-\alpha}}{\sum_{u_j \in \mathcal{C}_n} (1 + d_j)^{-\alpha}}$$
4. **Sample the Parent Node ($u_{p_n}$)**: Combine both distributions using mixture weight $\varepsilon = 0.35$:
   $$\pi_n(i) = (1 - \varepsilon) P_{\text{exploit}}(i) + \varepsilon P_{\text{explore}}(i)$$
   and sample parent $u_{p_n} \sim \pi_n$. Relying on exploitation alone ($\varepsilon = 0$) or exploration alone ($\varepsilon = 1$) drops test performance by `-5.40 pp` and `-5.68 pp`, respectively (`79.33%` $\to$ `73.93%` and `73.65%` across `TAU2`, `AppWorld`, and `SWE-bench Verified`).

### Step 3: Expand and Refine the Selected Harness via a Coding Agent

Invoke a general-purpose coding agent with read/write access to a fresh copy of parent workspace $h_{p_n}$ and read-only access to the experience archive $\mathcal{A}_{n-1}$ and component library $\mathcal{L}$:

1. **Diagnose Parent Failures Against Archive History**: Inspect $\mathcal{R}_{p_n}$ to identify dominant failure modes (e.g., premature termination, unverified tool state, context overflow on large diffs, or brittle argument formatting), and cross-reference $\mathcal{A}_{n-1}$ to see which prior code diffs $\Delta_k$ improved or regressed $q_k - q_{p_k}$ on those same tasks.
2. **Implement Cohesive Full-Harness Edits**: Edit any combination of context builders, state trackers, control loops, and tool wrappers in $h_{p_n}$ (copying and customizing relevant modules from $\mathcal{L}$ where helpful) to produce candidate $h_n$.
3. **Verify Smoke Execution Before Consuming Validation Quota**: Run syntax, import, and single-case smoke checks inside the workspace to ensure $h_n$ executes cleanly before launching the full $R = 5$ validation evaluation.

### Step 4: Evaluate on Validation Split and Backpropagate Experience

1. **Run Multi-Trial Validation**: Execute $h_n$ for $R = 5$ runs on validation split $\mathcal{D}_v$ under the locked runtime snapshot to obtain mean validation score $q_n$ and execution records $\mathcal{R}_n$.
2. **Update Tree and Archive**:
   - If evaluation succeeds (`ok = true`), add node $u_n = (h_n, q_n, \mathcal{R}_n)$ and directed edge $(u_{p_n}, u_n)$ to $\mathcal{G}_n$ (which increments $d_{p_n}$ by `1` for future exploration calculations) and append $(h_n, \Delta_n, q_n, q_n - q_{p_n}, \mathcal{R}_n)$ to $\mathcal{A}_n$.
   - If $h_n$ fails to run (`ok = false`), record the failure trace in $\mathcal{A}_n$ so subsequent rounds do not repeat the broken edit, without adding an invalid node to the shortlist pool.
3. **Final Harness Selection**: After all $N$ attempts finish, select the highest-scoring validation node $u_{i^\star} \in \arg\max_{u_i \in \mathcal{V}(\mathcal{G}_N)} q_i$. For final deployment and non-regression gating, follow `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../../rules/recursive-improvement.md).

---

## Quantitative Summary

### Main Benchmark Comparison (`GPT-5.4-mini` Executor, $N=15$ Budget, $R=5$ Runs Mean $\pm$ SD)

| Method | `TAU2-bench` (`92/186`) | `AppWorld` (`105/210`) | `WebShop` (`100/200`) | `BrowseComp+` (`100/200`) | `SWE-bench V` (`100/200`) | `BigCodeBench-H` (`100/200`) | **6-Benchmark Avg.** | Arith. / Geom. Cost per Task |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `Vanilla` (Root $h_0$) | `63.98 ± 2.15` | `72.00 ± 1.86` | `47.79 ± 1.14` | `72.40 ± 1.85` | `67.10 ± 0.89` | `28.30 ± 0.76` | `58.59%` | `$0.451` / — |
| `Claude Code` (`v2.1.272`) | `73.12 ± 1.14` | `70.86 ± 2.00` | `56.98 ± 1.19` | `73.20 ± 1.72` | `65.30 ± 1.30` | `30.80 ± 2.61` | `61.71%` | `$0.446` / — |
| `OpenHands` (`v1.45.0`) | `71.83 ± 1.59` | `66.29 ± 1.32` | `65.54 ± 1.77` | `74.00 ± 1.97` | `67.20 ± 1.64` | `30.80 ± 2.86` | `62.61%` | `$0.398` / — |
| `Hermes` (`v2026.9.7`) | `72.90 ± 2.17` | `74.19 ± 1.03` | `64.50 ± 1.34` | `74.30 ± 1.30` | `68.10 ± 2.53` | `31.70 ± 1.15` | `64.28%` | `$0.555` / — |
| `Codex` (`v0.154.0`) | `75.91 ± 2.98` | `73.24 ± 1.97` | `66.15 ± 1.49` | `74.70 ± 2.36` | `68.70 ± 2.11` | `30.20 ± 1.10` | `64.82%` | `$0.561` / — |
| `Meta-Harness` ($N=15$, no tree) | `74.62 ± 2.36` | `76.76 ± 2.94` | `66.33 ± 0.61` | `76.60 ± 1.02` | `68.80 ± 1.15` | `30.10 ± 1.66` | `65.53%` | `$0.351` / `$0.092` |
| **`HarnessFlow` ($N=15$, MCTS)** | **`81.83 ± 2.39`** | **`80.76 ± 1.33`** | **`69.49 ± 0.88`** | **`76.90 ± 1.14`** | **`75.40 ± 1.19`** | **`32.50 ± 1.77`** | **`69.48%`** | **`$0.232` / `$0.101`** |

### Ablation & Stronger-Executor Studies (Tables 2, 3, 4)

| Study / Variant | Benchmarks Evaluated | Score (`%`) | Delta vs. Default `HarnessFlow` |
|:---|:---|:---:|:---|
| **Default `HarnessFlow`** ($\varepsilon = 0.35$, with library $\mathcal{L}$) | `TAU2`, `AppWorld`, `BCB-H` | **`65.03%`** | Baseline (`+10.27 pp` over `Vanilla` `54.76%`) |
| `without library` ($\mathcal{L}$ removed) | `TAU2` (`77.64`), `AppWorld` (`80.63`), `BCB-H` (`31.90`) | `63.39%` | `-1.64 pp` (`-4.19 pp` on `TAU2`, still `+8.63 pp` over `Vanilla`) |
| `from OpenHands agent` (Root $h_0 =$ `OpenHands`) | `TAU2` (`76.02`), `AppWorld` (`79.62`), `BCB-H` (`32.20`) | `62.61%` | Improves all 3 benchmarks from a different starting architecture |
| **Default Mixture ($\varepsilon = 0.35$)** | `TAU2` (`81.83`), `AppWorld` (`80.76`), `SWE-V` (`75.40`) | **`79.33%`** | Optimal balance of score exploitation and direct-child exploration |
| Exploitation only ($\varepsilon = 0$) | `TAU2` (`74.19`), `AppWorld` (`78.76`), `SWE-V` (`68.83`) | `73.93%` | **`-5.40 pp`** (collapses into greedy local optima) |
| Exploration only ($\varepsilon = 1$) | `TAU2` (`72.80`), `AppWorld` (`79.81`), `SWE-V` (`68.33`) | `73.65%` | **`-5.68 pp`** (under-allocates budget to top-performing lineages) |
| **Stronger Executor (`GPT-5.4`)**: `HarnessFlow` vs. `Meta-Harness` / `Claude Code` / `Vanilla` | `TAU2` (`88.06`), `AppWorld` (`90.95`), `WebShop` (`71.72`) | **`83.58%`** (`$0.21`/task) | Beats `Meta-Harness` (`81.71%`, `$0.18`), `Claude Code` (`80.85%`, `$0.67`), `Vanilla` (`74.18%`, `$0.23`) |

---

## Failure Modes & Mitigations

| Failure Mode | Symptom | Mitigation |
|:---|:---|:---|
| **Greedy Lineage Lock-In ($\varepsilon = 0$)** | Optimizer repeatedly mutates the first moderately improving candidate and misses multi-step structural rewrites (`-5.40 pp` avg, `-7.64 pp` on `TAU2`) | Keep $\varepsilon = 0.35$ so nodes in the top-$K$ shortlist with fewer direct children $d_i$ retain a guaranteed `(1 + d_i)^{-1}` expansion share. |
| **Unbounded Tree Dilution under Small Budget ($N=15$)** | Expanding broken or low-scoring nodes wastes scarce validation rollouts | Restrict MCTS parent sampling strictly to the top $K = 5$ highest-scoring nodes ($\mathcal{C}_n$) while still logging failed branches in $\mathcal{A}$ as negative evidence. |
| **Fixed Temperature Mismatch Across Benchmarks** | A hardcoded softmax temperature $\tau$ is either too peaked on small/noisy validation splits or too flat on large splits | Compute $\tau = \operatorname{clip}(\max_{i \in J} \sqrt{q_i(1-q_i)/M_i}, 0.005, 0.100)$ automatically from the validation split's own binomial standard error. |
| **Shared-Library Runtime Coupling** | Modifying a shared helper file breaks previously evaluated nodes in the search tree | Enforce **copy-on-adopt** from read-only component library $\mathcal{L}$ into each candidate's isolated directory so every node $u_i$ remains a frozen, reproducible snapshot. |

---

## Related Skills & Rules

- **Skill**: [`fast-tree-search-self-improvement`](../fast-tree-search-self-improvement/SKILL.md) — Fast-validation MCTS for agent self-improvement (`SIFT`).
- **Skill**: [`regularized-harness-evolution`](../regularized-harness-evolution/SKILL.md) — Regularized recursive harness evolution (`RRSI`).
- **Skill**: [`reference-trajectory-harness-evolution`](../reference-trajectory-harness-evolution/SKILL.md) — Reference-trajectory credit assignment during harness evolution (`HarnessEvolve`).
- **Skill**: [`belief-calibrated-scaffold-optimization`](../belief-calibrated-scaffold-optimization/SKILL.md) — Maintaining a persistent causal world-model during scaffold search (`BCO`).
- **Rules**: [`recursive-improvement.md`](../../rules/recursive-improvement.md) — Canonical single-gate acceptance (`DO: Pass every self-modification through one acceptance gate`) and outer/inner loop governance.
