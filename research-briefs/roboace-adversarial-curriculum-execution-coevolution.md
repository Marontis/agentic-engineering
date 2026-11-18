# RoboACE: Adversarial Co-Evolution for Robot Self-Improvement

> **Source**: [arXiv:2611.13034](https://arxiv.org/abs/2611.13034) — Delin Zhao, Zhengrong Yue, Junlin He, Yali Wang (`MMLab @ SIAT`, November 2026)
> **Code**: [github.com/DeLin1001/RoboACE](https://github.com/DeLin1001/RoboACE)
> **Praxis Source ID**: `src:2611-13034v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

`RoboACE` evaluates a **single `27`-round development trajectory** around simulated `LIBERO` manipulation (`GPT-6.1 Terra/high` + `SAM 3` + frozen $\pi_{0.5}$ VLA controller) without quantitative component ablations isolating curriculum-harness revision from fixed-curriculum execution revision, the `Benchmark Curator`, or the `Strategic Advisor`, while general bounded harness evolution and proposer–solver decoupling are already covered as standalone procedures in [`regularized-harness-evolution`](../skills/regularized-harness-evolution/SKILL.md), [`source-disjoint-proposer-feedback`](../skills/source-disjoint-proposer-feedback/SKILL.md), and [`agent-data-mutual-evolution`](../skills/agent-data-mutual-evolution/SKILL.md). We catalog `RoboACE` as a Research Brief and capture its alternating snapshot-isolation, cross-role information-hiding, and deployable-memory reachability guardrails in [`recursive-improvement.md`](../rules/recursive-improvement.md).

---

## Core Architecture: Alternating Curriculum & Execution Harness Co-Evolution

Standard embodied self-improvement (`RoboRSI`, `Zetta`, `DynaHarness`, `RPG`) refines execution skills against an **unchanged practice source**, leaving newly emergent compositional weaknesses unprobed (for example, a standalone drawer skill that fails once paired with prior object placement). Conversely, co-evolving tasks and policies simultaneously destabilizes progress comparisons. `RoboACE` evolves **two separate software harnesses** (prompts, Python skills, tools, interfaces, and agent-readable memory) around **strictly frozen foundation models** via a four-step alternating protocol (`Table 3`, `Appendix A.1`):

1. **Phase 1 — Curriculum-Harness Evolution Against a Fixed Execution Deployment**:
   - Reading only the sanitized prior-round **Capability Profile $P_k$** (demonstrated abilities, lessons, unresolved gaps, uncertainty) and task statistics while holding the execution deployment `Stable`, an independent curriculum agent retains, replaces, or constructs practice conditions (`30` active practice conditions + up to `40` internal benchmark conditions curated with core regression anchors by a separate `Benchmark Curator`), while an external curriculum optimizer revises the retrieval/selection harness itself.
   - **Zero-rollout structural admission (`Appendix A.2`)**: Constructed worlds must pass compilation, physical-validity checks (loadability, stable finite states, valid goal references, no severe interpenetration), inverse-kinematics (`IK`) endpoint reachability, and a semantic **Judge** verifying agreement among `(instruction, goal, scene)`—using **zero fresh VLA rollouts** to pre-screen difficulty. Admitted proposals + internal benchmark conditions lock into a **fixed comparison snapshot $\mathcal{T}_k$** (with fixed task definitions and initializations) before any execution trials run.
2. **Phase 2 — Execution-Harness Evolution on Fixed Snapshot $\mathcal{T}_k$**:
   - The incoming `Stable` execution harness is scored first on $\mathcal{T}_k$ (`environment native predicate`; `8,000` control steps at `20 Hz` = `6 min 40 s` budget; $\pi_{0.5}$ `5`-action chunks). The execution optimizer diagnoses skill bugs vs. misleading skill descriptions vs. wrong VLA/code-skill handoffs, tests `Candidate` revisions under identical initializations and budgets on $\mathcal{T}_k$, and adopts `Candidate` or retains `Stable` based on successes, regressions, reuse, and cost (in Praxis deployments, gated by `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../rules/recursive-improvement.md)).
3. **Cross-Role Information Hiding & Deployable Memory Reachability (`§3.4`, `Appendix A.3`)**:
   - An **Experience Consolidator** compiles permitted task-level outcomes into $P_{k+1}$ while **keeping raw images, trajectories, tool calls, and code diffs strictly on the execution side** and **keeping Judge-only scene geometry strictly outside the execution agent's observations** (preventing [`criteria-exposure-verifier-overfitting`](./criteria-exposure-verifier-overfitting.md)).
   - Because diagnoses recorded only in an optimizer journal are invisible at runtime, the harness exposes **up to `2,500` characters** from each skill's main description plus retrievable manuals, and the optimizer explicitly verifies that independent runtime agents **receive and invoke** the revised material.
4. **Infrequent On-Demand `Strategic Advisor` (`§3.5`)**:
   - Reviews multi-round histories to flag stalled local repair loops (e.g., asking when to continue whole-task $\pi_{0.5}$ VLA control vs. switching to code skills or intervening mid-attempt, since whole-task VLA capability does not guarantee subgoal reliability), proposing investigation directions without directly mutating either harness; advice targeting the inactive side waits for its next scheduled phase.

---

## Empirical Results Across Four `200`-Condition `LIBERO` Panels (`§4`, `Table 2`)

Developed over `27` saved rounds strictly within native `LIBERO` (`76` distinct native conditions encountered + admitted constructed worlds; zero weight fine-tuning; final evaluation panels completely outside the loop, `1` designated observation per condition with timeouts/infra errors counted as failures across `200` audited conditions per panel):

| System / Baseline | `LIBERO` (`40 × 5` reserved) | `LIBERO-Plus` (`7` pert. cats) | `LIBERO-PRO` (`4` pert. dims) | `LIBERO-X` (`5` challenge levels) |
|:---|:---:|:---:|:---:|:---:|
| $\pi_{0.5}$ (direct official VLA controller alone) | `96.9%` | `92.0%` | `60.5%` | `11.5%` |
| `OpenVLA-OFT` | `96.8%` | `75.5%` | `51.0%` | `2.5%` |
| $\pi_0$-`FAST` | `85.5%` | `61.6%` | `49.0%` | `4.5%` |
| `Cosmos Policy` | `98.5%` | `88.5%` | `52.5%` | `2.5%` |
| `GR00T N1.7` | `97.5%` | `89.0%` | `48.0%` | `2.5%` |
| `RPent` (`Terra/high` + $\pi_{0.5}$, no target-bench exp.) | `92.0%` | `84.0%` | `32.5%` | `12.5%` |
| `VoLo` (`Terra/high` + $\pi_{0.5}$ + subgoal/VLM/replan) | `97.5%` | `90.0%` | `60.5%` | `10.0%` |
| `RoboACE` (**before evolution**, `Terra/high` + $\pi_{0.5}$) | `63.5%` | `64.5%` | `59.0%` | `19.5%` |
| **`RoboACE` (after `27`-round evolution, frozen)** | **`99.0%`** | **`94.5%`** | **`74.0%`** | **`30.5%`** |

- **Transfer gains over initial harness and shared $\pi_{0.5}$ controller**: Frozen evolved `RoboACE` improves over its initial deployment by **`+35.5 pp` (`LIBERO`)**, **`+30.0 pp` (`LIBERO-Plus`)**, **`+15.0 pp` (`LIBERO-PRO`)**, and **`+11.0 pp` (`LIBERO-X`)**, and beats direct $\pi_{0.5}$ execution (and `VoLo`) by **`+13.5 pp` on `LIBERO-PRO` (`74.0%` vs. `60.5%`)** and **`+19.0 pp` on `LIBERO-X` (`30.5%` vs. `11.5%`; `+18.0 pp` over `RPent` `12.5%`)**.
- **Documented evolution case studies (`§4.4`)**: (1) Revising curriculum prompts/interfaces so an unused compact evidence reader supported selective reading, coverage checks, and post-truncation recovery (`30`-condition course with `2` autonomous replacements); (2) After the curriculum retained `27` conditions and added `3` drawer-composition challenges (top-drawer closure, pudding placement + closure, bottom-drawer opening), revising the drawer skill contract to separate front-panel localization seeds from attached handles and verify target drawers lifted snapshot successes from **`48` to `50` on the fixed `54`-condition snapshot**; (3) `Strategic Advisor` consolidating grasp/drawer/motion recovery churn into explicit VLA-vs-code-skill handoff prerequisite checks.

---

## Related Artifacts

- **Skills**: [`regularized-harness-evolution`](../skills/regularized-harness-evolution/SKILL.md) (`arXiv:2609.24972`), [`source-disjoint-proposer-feedback`](../skills/source-disjoint-proposer-feedback/SKILL.md) (`arXiv:2609.39102`), [`agent-data-mutual-evolution`](../skills/agent-data-mutual-evolution/SKILL.md) (`arXiv:2610.41479`)
- **Rules**: [`recursive-improvement.md`](../rules/recursive-improvement.md), [`skill-system-design.md`](../rules/skill-system-design.md)
- **Research Briefs**: [`criteria-exposure-verifier-overfitting`](./criteria-exposure-verifier-overfitting.md) (`arXiv:2611.08318`), [`flex-rsi-frontier-agent-benchmark`](./flex-rsi-frontier-agent-benchmark.md) (`arXiv:2611.08946`), [`physevolve-executable-world-self-evolution`](./physevolve-executable-world-self-evolution.md) (`arXiv:2610.34921`)
