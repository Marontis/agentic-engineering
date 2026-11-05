# Artifact-to-Capability: Diagnosing Breaks in Capability Formation of Self-Evolving Agents

> **Source**: [arXiv:2611.04952](https://arxiv.org/abs/2611.04952) | `src:2611-04952v1`
> **Authors**: Ziqian Ban, Haoxiang Yang, Yanfei Zhang, Shixin Liang, Haoran Yu, Xu Lin, Shaobin Zhao, Xuran Li, Zhiyi Cheng (Tianjin University & International Digital Economy Academy / IDEA)
> **Category**: `cs.AI` (Self-Evolving Agents / Capability Evaluation & Diagnostics)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Executive Summary

Self-evolving agents iteratively accumulate **artifacts** — natural-language reflection memories, reusable code skills, or modified agent source code — and evaluate progress using proxy signals such as growing memory banks, rising validation scores, or modified actions. Using 15×15 freestyle Gomoku (`DeepSeek-V4-Flash` against three deterministic opponents: `rule-based`, `threat-aware`, and `search_2`) as a controlled environment with exact state-level ground truth across **1,876** fixed board states (Set A: **120** symmetry-expanded tactical states; Set B: **1,756** evolution game states) and a **7,234**-state differential pool, this study formalizes the **Artifact-to-Capability (A2C)** chain across five sequentially dependent properties ($1 \rightarrow 2 \rightarrow (3 \text{ and } 4) \rightarrow 5$). Auditing three representative self-evolution paradigms — **Reflexion** (text memory), **Voyager** (skill library + calling script), and **Darwin Gödel Machine / DGM** (open-ended code evolution) — reveals that all three produce active artifacts that alter agent behavior, yet each suffers a distinct structural break that proxy metrics misclassify as capability growth: **legalization gain** (Property 3 failure in Reflexion), **compositional override** (Property 4 failure in Voyager), and **loss-only drift** (Property 5 failure in DGM).

---

## Key Findings

1. **Five-Property Sequential Capability Chain ($1 \rightarrow 2 \rightarrow (3 \land 4) \rightarrow 5$)**:
   - **Property 1 (Artifact Formation)**: The evolution loop persists non-empty memories, skills, or code diffs.
   - **Property 2 (Behavioral Activation)**: The persisted artifact changes the agent's action distribution beyond rerun stochasticity across a fixed state probe set.
   - **Property 3 (Task-Relation Realization)**: Among legal moves, the artifact increases the conditional probability of satisfying the domain's true task relations, decomposing overall pass rate as:
     $$P(\text{pass}) = P(\text{legal}) \times P(\text{pass} \mid \text{legal})$$
   - **Property 4 (Boundary-Safe Reuse)**: Locally valid skills or heuristics compose without overriding higher-priority task relations at conflict states in full trajectories. *(Properties 3 and 4 together form the **Capability Checkpoint**.)*
   - **Property 5 (Capability Extension)**: Across multi-generation lineages, later versions retain previously solved states while adding newly passing states, rather than regressing or stalling.

2. **Reflexion Breaks at Property 3 via *Legalization Gain***:
   - Across 6 memory cells (3 opponents × 2 reflection granularities: `outcome` vs `trace`, up to 7 entries), Reflexion changes moves on **59.8%–78.2%** of Set B states (exceeding the **46.7%** empty-memory rerun noise floor) and lifts overall pass rate $P(\text{pass})$ from **8.0%** to **9.2%–10.3%** on Set B (and from **21.7%** to **22.5%–27.5%** on Set A).
   - However, factoring $P(\text{pass}) = P(\text{legal}) \times P(\text{pass} \mid \text{legal})$ reveals that the entire gain comes from fewer illegal moves on occupied intersections: $P(\text{legal})$ jumps from **49.8%** to **63.8%–83.5%** on Set B (**58.3%** to **75.8%–96.7%** on Set A), whereas conditional tactical quality $P(\text{pass} \mid \text{legal})$ improves in **0 of 12** cell-set combinations, **falling from 16.0% to 11.6%–14.5%** on Set B (−1.6 to −4.4 pp) and from **37.1% to 24.1%–36.3%** on Set A. On mutually legal states in Set B, net tactical transitions are negative (**−12** for `outcome`, **−19** for `trace`).

3. **Voyager Breaks at Property 4 via *Compositional Override***:
   - Evolving 7 Gomoku skills plus an orchestrating `auto_player` script raises Set B passes from **690** (`round1`) to **1,076** (`full`: **+459** newly passing, **−73** lost) and increases open-four creation in full games from **0/20** to **20/20**.
   - Yet against `search_2`, `full` wins **0/20** games and completes five-in-a-row at **0/20** immediate-win states (all occurring at move 19 as conflict states where both players have four-in-a-row). Inspection of `auto_player` shows it checks `detect_immediate_wins(board, opponent)` *before* `detect_immediate_wins(board, agent_color)` and returns early to block one of `search_2`'s two winning intersections instead of playing its own immediate winning move. Ablating `create_open_three` (`-open3`) avoids steering games into that conflict state, lifting Set B passes to **1,345** (+274 newly passing, 5 lost) and winning **20/20** games.

4. **DGM Breaks at Property 5 via *Loss-Only Drift* Under Composite Fitness**:
   - Along the best lineage `P0 -> OB-1 -> OB-2 -> OB-3 -> OB-5 -> OB-6 -> OB-7`, generation `OB-3` genuinely passes the Capability Checkpoint: compared to `P0`, it adds **522** newly passing states and loses **139** on Set B (net **+383**, lifting Set B pass rate from **48.7%** to **70.5%** and Set A from **66.7%** to **80.0%**), completes five at **19/19** immediate-win states, and wins **19/20** games vs `search_2`.
   - Subsequent generations exhibit **loss-only drift**: `OB-5` adds **0** newly passing states on Set B while losing **103** (Set B pass rate drops to **64.6%**, wins vs `search_2` fall from **19/20** to **9/20**), yet DGM's composite evolutionary fitness score *increases* from **347.0** (`OB-3`) to **357.8** (`OB-5`) because longer losing games inflate the average game-length survival term $\overline{L}_{\text{SD2}}$. Generation `OB-6` adds **0** and loses **29** more states (Set B **63.0%**, wins **0/20**, score **312.6**), and `OB-7` differs from `OB-6` on only **1 of 7,234** states in the full differential pool (**63.0%**, wins **0/20**).

---

## Quantitative Summary

### Table 1: Diagnostic Breakdown Across Self-Evolution Paradigms

| Paradigm | Artifact Evolved | Prop 1–2 (Active?) | Prop 3: $P(\text{pass} \mid \text{legal})$ | Prop 4: Conflict-State Reuse | Prop 5: Lineage Retention | Diagnosed Failure Mode |
|:---|:---|:---|:---|:---|:---|:---|
| **Reflexion** | 6 text memory cells ($\le 7$ entries) | Yes (59.8%–78.2% moves change vs 46.7% noise) | **Fails** (Set B: 16.0% $\rightarrow$ 11.6%–14.5%, 0/12 improve) | Not reached | Not reached | **Legalization Gain** (format/legality fix masks tactical drop) |
| **Voyager** | 7 code skills + `auto_player` dispatcher | Yes (Set B passes: 690 $\rightarrow$ 1,076; +459 / −73) | Passes on isolated states | **Fails** (0/20 immediate wins taken at move-19 conflict states; 0/20 wins) | Not reached | **Compositional Override** (defense check preempts immediate win) |
| **DGM (`P0`$\rightarrow$`OB-3`)** | Full Python agent code | Yes (deterministic code policy) | **Passes** (Set B: 48.7% $\rightarrow$ 70.5%, +522 / −139) | **Passes** (19/19 immediate wins; 19/20 game wins) | Baseline peak | Passes Capability Checkpoint |
| **DGM (`OB-3`$\rightarrow$`OB-7`)** | Subsequent lineage commits | Yes (`OB-3`$\rightarrow$`OB-6`), then stalls (`OB-6`$\rightarrow$`OB-7`: 1/7,234 states differ) | Regresses (Set B: 70.5% $\rightarrow$ 64.6% $\rightarrow$ 63.0%) | Regresses (wins: 19/20 $\rightarrow$ 9/20 $\rightarrow$ 0/20) | **Fails** (`OB-5`: +0 / −103; `OB-6`: +0 / −29) | **Loss-Only Drift** (composite score rises 347.0 $\rightarrow$ 357.8 via game-length term while capability erodes) |

---

## Why Not a Skill?

As the authors note in their Limitations section (§7), their empirical operationalization relies on a closed-rule board game (15×15 Gomoku) where move legality and exact tactical task relations (immediate five, open four, double threats) can be exhaustively enumerated and verified by a deterministic solver across fixed state sets. In open-ended software engineering or research tasks, ground-truth task relations are not closed-form rules. However, the three failure mechanisms uncovered — *legalization gain*, *compositional override*, and *loss-only drift under composite fitness* — directly inform evaluation guardrails in [`rules/recursive-improvement.md`](../rules/recursive-improvement.md) and [`rules/agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md).

---

## Actionable Takeaways

1. **Always Factor Format/Legality Compliance Out of Task Pass Rates**: When evaluating prompt, memory, or skill updates, log both $P(\text{valid/legal})$ and $P(\text{pass} \mid \text{valid/legal})$ on mutually valid instances. An update that lifts overall pass rate solely by reducing syntax or schema errors while lowering $P(\text{pass} \mid \text{valid/legal})$ (as in Reflexion's −1.6 to −4.4 pp drop) is a format guardrail, not domain reasoning improvement.
2. **Test Skill Orchestrators on Priority-Conflict States**: When composing multiple learned skills inside a dispatcher script, include conflict test states where two skills fire simultaneously with different priorities (e.g., an immediate terminal goal vs. a defensive heuristic) to catch early-return overrides before deployment.
3. **Gate Lineage Commits on State-Level Gain/Loss Counts, Not Composite Proxy Fitness**: Secondary survival or effort terms in evolutionary fitness functions (such as trajectory length $\overline{L}_{\text{SD2}}$ in DGM) can reward longer losing trajectories (**347.0 $\rightarrow$ 357.8**) while the agent loses **103** previously solved states and adds **0** new ones. Enforce the acceptance gate in [`rules/recursive-improvement.md`](../rules/recursive-improvement.md) ("DO: Pass every self-modification through one acceptance gate") by tracking `(newly_passing, lost)` counts on a fixed state suite and rejecting commits with zero newly passing states.

---

## Related Artifacts

- [`rules/recursive-improvement.md`](../rules/recursive-improvement.md) — "DON'T: Accept modifications based on aggregate metrics alone" and "DO: Pass every self-modification through one acceptance gate".
- [`rules/agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md) — Process-level and counterfactual evaluation rules.
- [`reliable-self-evolution-two-gate`](./reliable-self-evolution-two-gate.md) — Theoretical two-gate validation bounding retained-task regression against failure-task gain.
