# MASTARS: Multi-Agent Sequential Trajectory Augmentation with Return-Conditioned Subgoals

> **Source**: [arXiv:2611.17793](https://arxiv.org/abs/2611.17793) — Jiwon Jeon, Myungsik Cho, Woojun Kim, Seongmin Kim, Woohyeon Byeon, Seungyul Han, Youngchul Sung (KAIST, UNIST, 2026)
> **Praxis Source ID**: `src:2611-17793v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

`MASTARS` is a non-LLM continuous/discrete tensor trajectory-augmentation framework (`\mathbb{R}^{N \times d \times H}`) for **offline Multi-Agent Reinforcement Learning (`MARL`)** in Dec-POMDPs (`MPE`, `SMAC`, and `SMAC-v2`), built on a `64.3M`-parameter `MADiff` DDPM (`K = 200` denoising steps, horizon `H = 8`) and four `2`-layer `256`-unit MLP auxiliary models (`0.3M` parameters; the paper's NeurIPS checklist explicitly notes that LLMs are not used in any part of the methodology). Per our triage criteria in [`AGENTS.md`](../AGENTS.md) and consistent with [`ma-safediffuser-multi-agent-diffusion-planning`](./ma-safediffuser-multi-agent-diffusion-planning.md) and [`language-grounded-hrl-multi-agent-sar`](./language-grounded-hrl-multi-agent-sar.md), domain-specific offline MARL diffusion pipelines do not transfer directly as standalone LLM coding-agent skills or LLM rules; we document `MASTARS`'s resolution of the **diversity–coordination–coherence trade-off** and its subgoal-ordered partial synthesis efficiency as contextual multi-agent reference.

---

## Core Mechanism: Resolving the Diversity–Coordination–Coherence Trade-Off

In offline MARL dataset augmentation ($\mathcal{D}_{\text{org}} \to \mathcal{D}_{\text{aug}}$), existing diffusion strategies fail on at least one of three axes (`Figure 1`, `MPE Spread`): (a) **independent per-agent diffusion** increases behavioral diversity but causes inter-agent collisions (`42.0%` on `DoF*`), (b) **joint multi-agent diffusion** (`MADiff*`) preserves coordination but collapses onto the suboptimal training manifold, and (c) **naive sequential diffusion** causes global state incoherence (e.g., fixed landmark coordinates drifting across agents' private observations). `MASTARS` combines four components (`Section 5`, `Appendix E`):

1. **Agent-Wise `RePaint` Diffusion Inpainting (`Eqs. 4–5`)**: Iterates sequentially over an agent permutation $(\kappa(1), \dots, \kappa(N))$ (`N` outer passes $\times$ `K = 200` reverse DDPM steps with classifier-free return guidance), treating already-generated agents $\kappa(1 \dots l-1)$ and anchored prefixes as known regions (`m = 0`, forward-noised prior $\tilde{\tau}_{k-1}^{\text{prior}}$) and harmonizing them with denoised unknown segments (`m = 1`, posterior $\tilde{\tau}_{k-1}^{\text{posterior}}$) while discarding temporary suffixes for later agents $\kappa(l+1 \dots N)$.
2. **Subgoal-Anchored Partial Suffix Regeneration (`Eq. 7`)**: Trains a SARSA-style collective-return value network $V_\zeta(o^i)$ on observed transitions (`Eq. 12`, TD loss `86.3 -> 0.01` over `90K` steps) to avoid OOD value extrapolation, locates each agent's peak-value subgoal timestep $g^i = \arg\max_{t'} V_\zeta(o_{t'}^i)$, fixes the reliable prefix $t' \le g^i$, and synthesizes **only the post-subgoal suffix $t' > g^i$** (`44%` of each trajectory on average across `MPE`, range `0.17–0.63`, `Table 19`). *(Minor pseudocode vs. prose note: `§5.2–5.3` defines $g^i$ on $\tau^0$, whereas `Algorithm 1` line 11 recomputes $g^i$ on `Input_traj` inside the loop, which holds $\tau^0$ for ungenerated agents.)*
3. **Descending Subgoal Generation Ordering (`Eq. 8`)**: Orders agents by $\mathrm{argsort}[g^1, \dots, g^N]_\downarrow$—generating agents with **latest** subgoals (shortest suffixes) first and deferring agents with **earliest** subgoals (longest regenerated suffixes) to last so later agents retain maximum maneuvering flexibility to coordinate around earlier peers.
4. **Non-Autoregressive Annotation & Dynamics Filtering (`Eqs. 3, 6`)**: Infers actions $\tilde{a}_{t'}^i = I_\phi(\tilde{o}_{t'}^i, \tilde{o}_{t'+1}^i)$ and rewards $\tilde{r}_{t'} = g_\xi(\tilde{\boldsymbol{o}}_{t'}, \tilde{\boldsymbol{a}}_{t'})$ without recursive rollouts, admitting a candidate into $\mathcal{D}_{\text{aug}}$ (`1,000` accepted `8`-step trajectories added to `2,000`-episode `MPE`/`SMAC-v2` or `~250,000`-transition `SMAC` `og-marl` datasets) only when mean forward transition error satisfies $\mathbb{E}\|\tilde{o}_{t'+1}^i - f_\varphi(\tilde{o}_{t'}^i, \tilde{a}_{t'}^i)\| < \epsilon$.

---

## Quantitative Results (`5` Random Seeds, `8×RTX 3090` / `1×RTX 4090` Timings)

### 1. Downstream Offline MARL Gains (`Tables 1–3, 11, 20`)

| Benchmark & Base Algorithm | `Original` | `MADiff*` | `DoF*` | `MADiTS` | `INS` | **`MASTARS` (Ours)** | Relative Lift & Rank |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **`MPE` (`9` datasets) — `CFCQL`** (norm. return) | `33.4` | `42.3` | `30.2` | `36.8` | `39.3` | **`44.5`** | **`+33.2%`** (`22/27` top-2 across MPE) |
| **`MPE` (`9` datasets) — `OMAR`** | `29.4` | `32.9` | `27.6` | `31.2` | `31.0` | **`40.8`** | **`+38.8%`** |
| **`MPE` (`9` datasets) — `MATD3+BC`** | `28.4` | `34.9` | `26.4` | `30.6` | `29.0` | **`38.0`** | **`+33.8%`** |
| **`SMAC` (`3m`, `2s3z`, `8m` $\times 2$) — `CFCQL`** (win rate) | `0.64` | `0.71` | `0.70` | `0.69` | `0.71` | **`0.84`** | **`+31.3%`** (`1.00` on `3m-Med` & `8m-Good`) |
| **`SMAC` (`3m`, `2s3z`, `8m` $\times 2$) — `OMAR`** | `0.60` | `0.62` | `0.75` | `0.59` | `0.75` | **`0.86`** | **`+43.3%`** (`10/12` top-2 across SMAC) |
| **`SMAC-v2` (`10` cells) — Combined `Table 3`** | `0.19` | `0.21` | `0.25` | `0.18` | `0.25` | **`0.48`** | **`+152.6%`** (`18/20` top-2) |
| **`SMAC-v2` (`Appendix G Table 11`) — `CFCQL` / `OMAR`** | `0.21` / `0.16` | `0.24` / `0.18` | `0.34` / `0.15` | `0.22` / `0.14` | `0.34` / `0.15` | **`0.50` / `0.45`** | **`+143.7%` / `+189.1%`** (from unrounded sums `2.06->5.02`, `1.56->4.51`) |
| **`SMAC` Scale (`25m` `25` agents / `2c_vs_64zg` $H=400$)** | `0.70` / `0.52` | `0.75` / `0.70` | — | `0.60` / `0.05` | — | **`0.87` / `0.87`** | Scales where `MADiTS` collapses (`0.05`) |

*(Note on `SMAC-v2` aggregation: `Table 3` averages `CFCQL` and `OMAR` across Protoss [`0.12 -> 0.50`], Terran [`0.22 -> 0.50`], and Zerg [`0.24 -> 0.40`] to report `0.19 -> 0.48` [`+152.6%`], whereas `Table 11` reports algorithm-separated averages `0.21 -> 0.50` [`+143.7%`] and `0.16 -> 0.45` [`+189.1%`], with symmetric `1\sigma` error bars occasionally exceeding `[0, 1]`, e.g., `0.48 ± 0.71`.)*

### 2. Dataset Quality, Ablations & Sampling Cost (`Tables 4–7, 15–18`)

- **Diversity, Coordination & Coherence (`MPE`, `Tables 4–5`)**: `MASTARS` raises `DIRE` distributional novelty (`0.101` vs. `0.086` `MADiff*`, `0.045` `Original`) while achieving the lowest **collision rate (`8.4%`** vs. `13.3%` `MADiff*`, `16.7%` `INS`, `33.2%` `MADiTS`, `42.0%` `DoF*`), **landmark dispersion error (`0.039`** vs. `0.078` `MADiTS`, `0.088` `MADiff*`, `0.276` `DoF*`), and **dynamics violation rate (`2.0%`** vs. `14.2%–93.0%`).
- **Component Ablations (`MPE` 3-algorithm mean, `Table 7`)**: Full `MASTARS` scores **`41.10`**, dropping to `37.27` (`w/o Inpainting`), `35.21` (`Reverse ordering`, earliest subgoals first), `34.60` (`w/o Sequence`), `33.34` (`w/o Subgoal`), and **`32.87` (`Random ordering`)**. Value noise up to `σ = 0.2` (`34.50–35.40`) and reward/action noise up to `30%` (`37.4–40.3`) still beat `Original` (`30.56`).
- **Acceptance Efficiency vs. $O(N)$ Agent Scaling (`Tables 15–18`)**: Training takes `140 min` (`2.33 h`) vs. `187 min` for `MADiTS` (`~25%` faster; `0.3M` auxiliary MLPs add `0.5%` parameters). Subgoal partial synthesis cuts `MPE` rejection rates for `1,000` accepted trajectories from **`63%` (`2,732` attempts, `328 s`) to `38%` (`1,623` attempts, `195 s`, `-40%` wall-clock)**, and under strict $\epsilon = 0.001$ `Joint` and `Simple-seq` accept `0` candidates ($\infty$ time) on `Tag`/`World` vs. `0.51 s`/`0.53 s` for `MASTARS`. However, sequential `RePaint` passes scale linearly in agent count (`0.12 s` on `3m`, `0.30 s` on `5m_vs_6m`, `0.75 s` on `8m`, **`8.3 s` on `25m` [`69.2×`]** vs. flat `0.25–0.31 s` across $H \in [8, 32]$).

---

## Conceptual Takeaways for Multi-Agent Trajectory Synthesis

- **Schedule most-constrained agents first and highest-flexibility agents last**: Ordering sequential synthesis by descending anchor/subgoal time ($\mathrm{argsort}[g^i]_\downarrow$) beat both random (`32.87` vs. `41.10`) and reverse (`35.21`) ordering because agents with longer remaining horizons can adapt around already-committed peers.
- **Evaluate synthetic trajectory generators on time-per-*accepted*-trajectory under strict transition checks, not raw candidate throughput**: Faster joint one-shot samplers collapsed to `0%` acceptance at tight dynamics thresholds ($\epsilon = 0.001$), whereas anchoring reliable prefixes cut failed synthesis attempts by `40.6%` (`2,732 -> 1,623`).

---

## Related Artifacts

- **Rules**:
  - [`skill-system-design.md`](../rules/skill-system-design.md) — `ACE` training-data quality lens (Accuracy as a hard constraint before Diversity)
- **Research Briefs**:
  - [`ma-safediffuser-multi-agent-diffusion-planning`](./ma-safediffuser-multi-agent-diffusion-planning.md) — Control-barrier-function projections inside multi-agent DDPM planning (`arXiv:2611.05524`)
  - [`language-grounded-hrl-multi-agent-sar`](./language-grounded-hrl-multi-agent-sar.md) — Language-grounded hierarchical MARL coordination (`arXiv:2611.13161`)
