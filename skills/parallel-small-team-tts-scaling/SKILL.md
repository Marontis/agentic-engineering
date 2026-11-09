---
name: parallel-small-team-tts-scaling
description: >
  Allocate test-time compute budgets (B = K * M agents) on verifiable
  long-horizon engineering tasks by running K independent small flat peer
  teams of size M (e.g., K = 10 teams of M = 10 agents sharing discoveries
  asynchronously on a forum without a central manager) and selecting the best
  team's output via the verifier. Covers the order-statistic mean-variance
  trade-off model, optimal team sizing, and flat vs manager-orchestrated
  coordination. Derived from "Test-Time Compute Scales Better with Parallel
  Agent Teams" (arXiv:2611.09798).
license: CC-BY-4.0
repository: https://github.com/Marontis/agentic-engineering
---

# Parallel Small-Team Test-Time Compute Scaling

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

Use this skill when allocating a test-time compute budget of $B$ agent runs (or agent-hours) across long-horizon engineering, coding, formal reasoning, or scientific optimization tasks where an automated verifier or scorer can evaluate every candidate submission and only the best verified solution matters.

## When to Use

- You have a fixed test-time compute budget $B$ (e.g., $B = 20$ to $B = 100+$ agent sessions) and an automated verifier (unit/integration test suite, GPU kernel benchmark timer, Lean 4 compiler, finite-element solver, or exploit capability ladder).
- Standard **Best-of-$N$ over solo agents** ($M = 1, K = B$) has flattened out early because individual agents have a low mean score on hard multi-step problems.
- Running **one large collaborating team** ($M = B, K = 1$) suffers from premature convergence, communication clutter, and zero sample variance across runs.
- You want a smaller open-weight model (e.g., a `27B` model) to match or beat a frontier model at equal dollar cost by scaling parallel collaborative teams.

## Core Insight

Best-of-$N$ solo sampling ($M = 1$) and one giant team ($M = B$) are the two degenerate endpoints of a single compute-allocation family: partitioning a budget of $B$ agents into **$K = B / M$ independent teams of size $M$** and keeping the best verified submission across all $K$ teams (`parallel agent teams`, arXiv:2611.09798).

### The Order-Statistic Mean–Variance Model

Let the best verified score $X_k$ of a single team of size $M$ be modeled as $X_k \sim \mathcal{N}(\mu(M), \sigma(M)^2)$. When $K = B / M$ independent teams are run in parallel, the expected best score across the $K$ teams is:

$$\mathbb{E}\!\left[\max_{1 \le k \le K} X_k\right] = \mu(M) + \sigma(M)\,a_K \approx \mu(M) + \sigma(M)\,c_K, \quad \text{where } c_K = \sqrt{2 \ln K} = \sqrt{2 \ln(B / M)}$$

(with exact normal order-statistic expectations $a_1 = 0$, $a_2 = 1/\sqrt{\pi} \approx 0.564$, $a_{10} = 1.539$, $a_{20} = 1.867$, $a_{100} = 2.508$, $a_{200} = 2.746$, and Blom's quick approximation $a_K \approx \Phi^{-1}\!\big((K - 0.375)/(K + 0.25)\big)$ accurate to within `0.03`).

This equation explains why both extremes lose and why parallel small teams ($M = 10$, $K = B / 10$) win:
1. **Solo agents ($M = 1, K = B$) have a low mean $\mu(1)$ and saturate rapidly**: At $B = 20$ agents, solo Best-of-$N$ has already exhausted **`60%` to `94%`** of the gain that `100` agents reach (`81%` to `100%` by $B = 50$). Differentiating with respect to $B$ gives the marginal return per added agent: $\sigma(M) / \big(B \sqrt{2 \ln(B / M)}\big)$. At $B = 20$, teams of $M = 10$ ($K = 2$) sit on the steep early part of the order-statistic curve, yielding $\sqrt{\ln 20 / \ln 2} \approx 2.1\times$ the theoretical marginal gain of solo agents (measured at **`+1.27%` vs `+0.64%` per extra agent** from $B = 10$ to $B = 20$).
2. **One big team ($M = B, K = 1$) wastes all variance ($c_1 = 0$) and degrades at scale**: A single team of size $B$ draws only $K = 1$ sample, so its expected score is just $\mu(B)$ with zero variance bonus. Worse, $\mu(M)$ does not grow monotonically: as $M$ increases from `64` to `100` agents, team performance **drops on all 4 tasks tested** as peers copy early good solutions and lose exploration diversity.
3. **Parallel small teams ($M = 10, K = B / 10$) balance a high mean $\mu(M)$ with the variance gain $\sigma(M)\,c_K$**: Paying $M\times$ agents per sample reduces the sample count from $B$ to $B/M$, which lowers the variance term by only $\approx \sigma \ln M / \sqrt{2 \ln B}$—a penalty that shrinks as $B$ grows. With exact $a_K$ and $M = 10$ at equal $\sigma$, a team needs a mean gain $\mu(10) - \mu(1)$ of only **`1.30\sigma` at $B=20$**, **`1.09\sigma` at $B=50$**, **`0.97\sigma` at $B=100$**, **`0.88\sigma` at $B=200$**, and **`0.73\sigma` at $B=1,000$** to beat $B$ solo agents. Empirically across all 12 long-horizon tasks with `Qwen3.8-27B`, $\mu(10)$ exceeds $\mu(1)$ by **`0.5\sigma` to `4.4\sigma` on every task**.

---

## Procedure

### Step 1: Calibrate Single-Agent vs Small-Team $(\mu, \sigma)$ on Pilot Runs

Before committing a large compute budget $B$:

1. Run a small pilot of independent solo agents ($M = 1$, e.g., $8\text{--}10$ runs) and 2–3 small flat teams ($M = 5$ or $M = 10$) for a fixed session duration (e.g., `6 h` or `12 h` per agent).
2. Estimate $(\mu_1, \sigma_1)$ and $(\mu_M, \sigma_M)$ from verified submission scores.
3. Check the **Equal-Budget Crossover Condition**: allocate budget $B$ to parallel teams of size $M$ whenever:
   $$\mu_M + \sigma_M\,a_{\lfloor B / M \rfloor} > \mu_1 + \sigma_1\,a_{\lfloor B \rfloor}$$
   where $a_K \approx \Phi^{-1}\!\big((K - 0.375)/(K + 0.25)\big)$.
   - **Rule of thumb**: If the task is already easy for a single agent (high $\mu_1$ near the score ceiling and small $\sigma_1$, as seen with `DeepSeek V4.1 Flash` or `GPT-5.6-sol` on saturated tasks), solo Best-of-$N$ or a few runs suffice. If solo agents frequently stall or score low ($\mu_M - \mu_1 \ge 0.97\,\sigma_1$ for $B = 100, M = 10$), parallel small teams dominate.

### Step 2: Partition Budget $B$ into $K$ Independent Flat Teams of Size $M \in [5, 10]$

Given a total compute budget of $B$ agent runs:

1. **Choose team size $M$ by budget tier**:
   - **Small budgets ($B = 20\text{--}30$ agents)**: Use $M \in [3, 6]$ ($K = 4\text{--}10$ teams) so that $K \ge 4$ independent team samples are drawn for the verifier to select across.
   - **Medium-to-large budgets ($B = 50\text{--}100+$ agents)**: Use **$M = 10$** ($K = 5\text{--}10+$ teams) as the default sweet spot. Optimal team size $M^*$ satisfies the first-order condition $\frac{d\mu_M}{dM} + \frac{d\sigma_M}{dM}\sqrt{2\ln(B/M)} = \frac{\sigma_M}{M\sqrt{2\ln(B/M)}}$ and grows slowly with $B$.
   - **Never put the entire budget into a single team ($K = 1, M = B$)**: Always maintain at least $K \ge 5\text{--}10$ independent teams to capture the order-statistic tail gain $\sigma(M)\,a_K$.
2. **Prefer adding teammates (or parallel teams) over doubling single-agent session length**:
   - Extending a single agent's session from `6 h` to `12 h` on `Graph Node Classification` barely moved the mean score (**`52.0` at 6 h $\to$ `52.7` at 12 h**, $+0.7$ points, well below the $+3.4$ points required by Equation 4 to justify doubling cost) and lost to plain Best-of-$N$ over 6-hour agents at every budget.
   - Spending the exact same `12 agent-hours` on a **2-agent team for 6 hours each** raised the mean score to **`57.4` ($+5.4$ points)** and beat both 12-hour solo agents and 6-hour solo agents across large budgets (`75.5` vs `71.4` at 120 agent-hours).

### Step 3: Coordinate Each Team via an Asynchronous Shared Forum — Never a Central Manager

Inside each team of $M$ agents, give every agent its own isolated execution sandbox and verifier access, connected only through a lightweight, append-only **shared forum** (`post`, `list`, `read`):

1. **Expose three non-blocking forum primitives**:
   - `post(title, body)`: Post a titled note (`<= 120` chars title, `<= 64,000` chars body so full solution files fit), automatically tagging the post with the author's current best verified score.
   - `list()`: List post titles with unread markers (for $M \le 10$, show the full index; if $M \ge 64$, cap the index to the newest `100` titles plus unread posts to avoid context overflow).
   - `read(post_id)`: Read one post in full on demand.
2. **Use a single non-coercive forum prompt note**: Append a brief note to each agent's system prompt stating how many teammates exist, asking them to post clear wins and clear failures with exact parameter/code changes and verified scores, suggesting they scan the index before starting a new experiment, and leaving reading/posting voluntary (no forced turn-by-turn reminders).
   - *Emergent peer coordination*: Without assigned roles, `Qwen3.8-27B` and `DeepSeek V4.1 Flash` agents spontaneously tag posts (`WIN`, `FAIL`, `CLAIM`, `FIRE`, `ACK`), adopt experiment reservation protocols (`86%` of `Borden Source Inversion` teams, with `88%` of teammates following once one agent starts claiming), and build on peers' breakthroughs (`6 of 8` teammates adapting a peer's new best config within `10` minutes).
3. **Do NOT add a central manager or orchestrator agent**:
   - In `arXiv:2611.09798` (Section 6, Figure 10), replacing the flat peer forum with an **orchestrator/manager agent** (where one agent assigns tasks and collects reports while workers never communicate directly) degraded performance **below both flat teams and independent solo agents at every compute budget** across `Borden Source Inversion`, `Graph Node Classification`, and `KDA Chunk Forward`. On `Borden Source Inversion`, the best of 10 orchestrated teams (**`68.4`**) scored lower than a *single average flat team* (**`76.5`**). Central managers create a synchronization and information bottleneck that depresses $\mu(M)$ while costing the same $M$ agents.

### Step 4: Select the Winning Solution Across All $K \times M$ Runs via the Verifier

1. Within each team $k \in \{1, \dots, K\}$, define the team score as the highest verified submission produced by any of its $M$ members: $X_k = \max_{1 \le m \le M} S_{k,m}$.
2. Across the $K$ independent teams, return the global verifier winner:
   $$S^* = \max_{1 \le k \le K} X_k$$
3. Ensure the verifier is hardened against reward exploits (e.g., refilling inputs on every timed GPU kernel call to prevent output-caching exploits, checking transitive axioms in Lean 4 so `sorry` lemmas cannot be hidden, and grading in isolated hardware-pinned sandboxes).

---

## Quantitative Benchmark Results (`arXiv:2611.09798`)

Evaluated across **12 long-horizon tasks** (12-hour sessions per agent; 6 hours on `Browser Exploit`; over `8,000` agent runs and `95,000` agent-hours) using `Qwen3.8-27B`:
- **Beats 100 parallel solo agents on `10 of 12` tasks** at $B = 100$ (`11 of 12` tasks at $B = 50$, where 5 teams of 10 beat 50 solo agents). Averaged over all 12 tasks, parallel teams of 10 score **`+10%` higher** than solo agents at $B = 10$ and **`+27%` higher** at $B = 100$.
- **Beats 1 giant team of 100 agents on `4 of 4` tasks** (`Dabic Gravity Inversion`, `Borden Source Inversion`, `Graph Node Classification`, `KDA Chunk Forward`) by **`+8%` to `+30%`**; on two of those tasks, a single team of 100 even scored below 100 independent solo agents.
- **Matches or beats a frontier model (`GPT-5.6-sol`) at equal dollar cost on half the tasks** (`4 of 8` tasks with $\ge 5$ frontier runs, and `6 of 12` tasks overall when comparing equal-cost parallel team scaling against frontier baselines; e.g., on `Carleson Formalization`, for the price of 5 `GPT-5.6-sol` agents, 8 `Qwen3.8-27B` teams of 10 scored **`52.0` vs `47.9`**).

| Task (`Benchmark` / Domain) | Solo Agent $\mu_1 \pm \sigma_1$ | Team of 10 $\mu_{10} \pm \sigma_{10}$ | $B=10$: Best-of-10 vs 1 Team | $B=50$: Best-of-50 vs 5 Teams | $B=100$: Best-of-100 vs 10 Teams | Measured Gain at $B=100$ |
|:---|:---|:---|:---|:---|:---|:---|
| **Dabic Gravity Inversion** (`EdgeBench` / Geophysics) | `9.5 ± 8.6` | `22.3 ± 5.4` | `21.0` vs **`22.3`** | `28.7` vs **`30.5`** | `33.1` vs **`34.6`** | **`+4.6%`** |
| **Borden Source Inversion** (`EdgeBench` / Hydrogeology) | `49.1 ± 18.9` | `76.5 ± 19.5` | **`79.9`** vs `76.5` | `87.9` vs **`98.2`** | `89.3` vs **`109.0`** | **`+22.1%`** |
| **Graph Node Classification** (`EdgeBench` / ML) | `52.1 ± 11.8` | `79.0 ± 8.5` | `69.1` vs **`79.0`** | `76.8` vs **`90.0`** | `81.5` vs **`95.1`** | **`+17.0%`** |
| **Ad Placement Optimization** (`EdgeBench` / Heuristics) | `62.0 ± 17.9` | `74.3 ± 1.8` | **`74.5`** vs `74.3` | `76.6` vs **`76.7`** | `77.3` vs **`77.8`** | **`+0.7%`** |
| **Carleson Formalization** (`EdgeBench` / Lean 4 Math) | `3.5 ± 4.5` | `23.2 ± 15.7` | `12.2` vs **`23.2`** | `17.7` vs **`45.8`** | `19.0` vs **`54.8`** | **`+187.7%`** |
| **MoE Load Balance** (`MLS-Bench` / ML Systems) | `0.566 ± 0.146` | `0.643 ± 0.222` | **`0.720`** vs `0.643` | `0.750` vs **`0.797`** | `0.750` vs **`0.820`** | **`+9.2%`** |
| **Active Learning** (`MLS-Bench` / ML) | `0.451 ± 0.083` | `0.530 ± 0.015` | `0.520` vs **`0.530`** | `0.540` vs **`0.548`** | **`0.560`** vs `0.550` | `-1.6%` |
| **Browser Exploit** (`ExploitBench` / Cybersecurity) | `3.75 ± 0.75` | `5.40 ± 0.92` | `4.98` vs **`5.40`** | `5.88` vs **`6.50`** | `6.00` vs **`7.00`** | **`+16.7%`** |
| **KDA Chunk Forward** (`KernelBench` / GPU Kernels) | `7.27 ± 3.27` | `13.12 ± 1.61` | `11.21` vs **`13.12`** | `11.77` vs **`15.25`** | `11.83` vs **`16.54`** | **`+39.8%`** |
| **Kimi-Linear Decode** (`KernelBench` / GPU Kernels) | `0.724 ± 0.712` | `1.334 ± 0.646` | **`1.77`** vs `1.33` | **`2.12`** vs `2.04` | **`2.36`** vs `2.16` | `-7.9%` |
| **SwinMLP BF16** (`KernelBench-Verified` / GPU Kernels) | `3.58 ± 1.50` | `6.74 ± 1.02` | `5.65` vs **`6.74`** | `6.20` vs **`8.08`** | `6.29` vs **`8.33`** | **`+32.5%`** |
| **Multiscale Cantilever** (`TopOpt` / Structural Design) | `7.81 ± 2.58` | `11.60 ± 0.12` | `11.06` vs **`11.60`** | `11.44` vs **`11.69`** | `11.50` vs **`11.70`** | **`+1.7%`** |

---

## Environment Caveats

- **Requires an automated, reliable verifier**: Parallel agent teams rely on selecting $\max_{1 \le k \le K} X_k$. Without a verifier (or when the verifier can be reward-hacked), selecting the best team becomes an unsolved aggregation problem.
- **Bimodal zero-inflation tasks (`Kimi-Linear Decode`)**: When almost every individual attempt fails and scores `0` until late in the session (`Kimi-Linear Decode`), teammates have no intermediate wins or working baselines to share on the forum, so solo Best-of-$N$ (`2.36` vs `2.16` at $B=100$) retains a slight edge through raw trial count.
- **Non-normal score distributions (`Ad Placement`, `KDA Chunk Forward`)**: When solo scores have a heavy lower tail of failed runs ($W = 0.66$ on `Ad Placement`) or pile up below a hard ceiling ($W = 0.93$ near `12.0` on `KDA Chunk Forward`), the Gaussian formula $\mu + \sigma\sqrt{2\ln N}$ overpredicts solo Best-of-$N$ and underestimates the true empirical advantage of parallel teams (`+0.8%` predicted vs **`+39.8%` measured** on `KDA Chunk Forward`).

## Failure Modes

- **Scaling a single team to $M = 64\text{--}100$ (`One Big Team` trap)**: Teammates rapidly copy the first reasonable solution posted to the forum (`banking` a peer's configuration within 10 minutes), collapsing exploration diversity and throwing away the $\sigma\sqrt{2\ln K}$ sampling bonus.
- **Inserting a central manager agent (`Orchestrator` bottleneck)**: Routing communication through a manager agent instead of a flat peer forum reduces team scores below solo agents at every budget.
- **Relying on a single team ($K = 1$) at small budgets**: Even when $\mu_{10} > \mu_1$, a single team run has high run-to-run variance ($\sigma_{10}$) and can land below `Best-of-10` solo agents (`4 of 12` tasks at $B = 10$, such as `Borden Source Inversion` `76.5` vs `79.9`), whereas sampling $K = 5$ or $K = 10$ teams reliably overtakes solo sampling (`98.2` vs `87.9` at $B = 50$; `109.0` vs `89.3` at $B = 100$).

## Cross-References

- [`../../rules/multi-agent-coordination.md`](../../rules/multi-agent-coordination.md) — "DON'T: Default to a fixed multi-agent topology" (covers `Star` orchestrator bottlenecks and `Muffin` asynchronous shared memory buffers)
- [`../../rules/recursive-improvement.md`](../../rules/recursive-improvement.md) — "DO: Invest in standalone verifiers before planning components" and "DO: Establish Ostrom-style commons governance and peer auditing over shared swarm memory"
- [`../../research-briefs/muffin-asynchronous-shared-memory-buffer.md`](../../research-briefs/muffin-asynchronous-shared-memory-buffer.md) — Asynchronous shared memory buffers outperforming synchronous debate

## Sources

- Wang et al., "Test-Time Compute Scales Better with Parallel Agent Teams" ([arXiv:2611.09798](https://arxiv.org/abs/2611.09798), `src:2611-09798v1`)
