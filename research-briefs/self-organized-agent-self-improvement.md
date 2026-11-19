# Do LLM Agents Still Need to Be Told How to Self-Improve?

> **Source**: [arXiv:2611.23219](https://arxiv.org/abs/2611.23219) — Shobhita Sundaram (`MIT CSAIL`), Cansu Sancaktar (`University of Tübingen`), Phillip Isola (`MIT CSAIL`, November 2026)
> **Project**: [ssundaram21.github.io/self-org](https://ssundaram21.github.io/self-org/)
> **Praxis Source ID**: `src:2611-23219v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

`arXiv:2611.23219` is an **empirical emergence study** that intentionally *strips away* any prescribed outer optimization algorithm (`Algorithm 1` exposes only bare `{Read, Write, Bash, Gameplay}` primitives, `0` real-world training tasks, a `20`-update context-edit cap, and a `150`-gameplay budget) to test whether frontier models spontaneously invent self-regulated learning (`SRL`) loops on their own. Because the paper prescribes no transferable subtask procedure—and shows that older model generations fail completely without explicit scaffolding while continual unguided context edits plateau around `~20` updates—we catalog it as a Research Brief and integrate its capability-threshold, interactive-execution, and target-context overfitting findings as evidence in [`recursive-improvement.md`](../rules/recursive-improvement.md) (complementing structured meta-improvement skills such as [`hyperagent-self-improvement`](../skills/hyperagent-self-improvement/SKILL.md) and [`regret-guided-continual-harness-evolution`](../skills/regret-guided-continual-harness-evolution/SKILL.md)).

---

## Experimental Protocol: Data-Free Self-Organized Improvement (`§3`, `Algorithm 1`)

A **Teacher** agent receives an initially empty `player_folder` (injected verbatim into a separate frozen **Player** agent's context at evaluation time), workspace tools `{Read, Write, Bash, Gameplay}`, zero human-authored training games, and a minimal prompt stating only that the Player will later face unseen sequential decision-making games (`low` reasoning effort, `20k` output tokens/turn, `<= 20` updates to `player_folder`, `<= 150` `Gameplay` rollouts, `3` seeds per condition across `6` models from `3` families: `Claude Opus 4.6` vs. `Opus 5`, `GPT 5.6-Sol` vs. `6-Astra`, and `GLM 4.7` vs. `5.3`).

---

## Key Empirical Findings (`§4–5`, `Figures 3–11`, `Tables 1 & 4`)

### 1. Sharp Generational Emergence Matching Data-Backed `GEPA` (`§4.1`, `Figure 3`)

- **Data-free gains on newer frontier models**: Evaluated zero-shot on `20` held-out human-authored `PuzzleScript-t20` games (optimal solution length `<= 12`, `20` turns / `25k` token cap), self-organized Teacher runs lift Player win rates by **`+20%` (`Claude Opus-5`)**, **`+10%` (`GPT 6-Astra`)**, and **`+6%` (`GLM 5.3`)**—**matching prescribed `GEPA` trained on `20` real in-distribution human games (`10` train + `10` val)** under the identical `150`-gameplay budget.
- **Collapse on prior generations**: Older models in all three families (`Claude Opus 4.6`, `GPT 5.6-Sol`, `GLM 4.7`) achieve **near-zero or negative gains** without a prescribed improvement loop (`1/3` `GLM 4.7` sessions ran `0` gameplays before exiting), mirroring their lower `13`-item Zimmerman `SRL` rubric scores (`0–3` two-pass `GPT 6-Astra` judge).

### 2. Spontaneous Curriculum Design, A/B Verification, and Monte Carlo Simulation (`§4.2–4.3`)

Without instructions to validate or design curricula, frontier Teachers (`Opus 5`, `GPT 6-Astra`, `GLM 5.3`) spontaneously invent four `SRL` mechanisms:

1. **Procedural task generation + exact solver filtering**: Writing Python level generators paired with `BFS` solvers to discard unsolvable or trivial (`< 5`-step / `100%` baseline win-rate) games before spending `Gameplay` rollouts.
2. **Zone-of-Proximal-Development (`20%–60%` win rate) replay allocation**: Concentrating repeated `Gameplay` evaluations in an inverted-U band around **`20%–60%` observed win rate** (matching Unsupervised Environment Design learnability peaks without explicit UED rewards).
3. **Controlled paired A/B testing**: Running paired `Gameplay` rollouts *with* vs. *without* candidate `player_folder` edits and reverting non-improving edits.
4. **Spontaneous simulator synthesis without `Gameplay`**: Even when `Gameplay` is removed (`Read-Write-Bash` only), `Opus 5` writes its own `20`-turn Python resource-trading simulator, executes `300–400`-seed Monte Carlo sweeps, discovers that its initial heuristic underperformed a naive baseline (`77.1` vs. `102.0`), isolates an `"invest early"` upgrade trap (`154.2` vs. `102.9`) and `50%–75%` reserve sizing (`166.4–183.4`), and compiles verified rules into `player_folder`.

### 3. Cross-Environment, Cross-Model, and Context-Specificity Trade-Offs (`§5`, `Tables 1 & 4`, `Figure 11`)

- **Cross-benchmark & cross-model transfer (`Claude Opus-5` `Gameplay` on `PS-t20`)**: Transfers zero-shot with **`+20%` on `PuzzleScript-t20`**, **`+9%` on longer-horizon `PuzzleScript-t30`** (`20` games, optimal length `13–22`, `30` turns / `31,250` tokens), **`+21%` on `ARC-AGI-3 (L1)`** (`17` filtered `64×64` hex-grid games), and **`+0.15` SPL on `MazeBench`** (`16` 3D isometric ASCII rooms, `100` turns / `75,000` tokens), while preserving near-ceiling saturated games (**`98.8 ± 0.0%` vs. `100.0%`**, `Table 4`). Removing interactive execution (`Read-Write` only) loses **`> 50%` of `Gameplay` gains on `3/4` benchmarks**, whereas domain-agnostic `Python Gameplay` recovers nearly all `PuzzleScript` transfer on `3/4` benchmarks. Cross-model (`Table 1`, `PS-t20`), `GPT-6 Astra`-evolved artifacts lift `Opus 5` from **`25.4 ± 3.6%` to `47.5 ± 4.5%` (`+22.1 pp`)**, and `Opus 5` artifacts lift `GPT-6 Astra` from **`67.1 ± 3.8%` to `72.1 ± 4.0%` (`+5.0 pp`)**.
- **Target-evaluation information hurts OOD generalization (`§5.2`, `Figure 11`, `Appendix C.2–C.3`)**: Feeding the Teacher progressively richer semantic summaries of `PuzzleScript-Narrow` (`{0, 234, 659, 1519, 3313, 6551}` tokens) monotonically lifts in-distribution `PS-Narrow` win rate, but at **`3,313–6,551` tokens `ARC-AGI-3` OOD transfer plateaus and declines** as artifacts specialize to narrow mechanics. Similarly, hard-coding `PS-t20`'s exact `20`-turn / `25k`-token evaluation budget into `Gameplay` boosts `PS-t20` while **degrading `PS-t30` transfer** relative to letting the Teacher allocate `3,000` total turns / `3.75M` tokens freely, and continual context revisions plateau around **`~20` updates** (`Figure 18`).

---

## Related Artifacts

- **Skills**: [`hyperagent-self-improvement`](../skills/hyperagent-self-improvement/SKILL.md) (`arXiv:2603.19461`), [`autonomous-environment-exploration`](../skills/autonomous-environment-exploration/SKILL.md) (`arXiv:2609.15364`), [`regret-guided-continual-harness-evolution`](../skills/regret-guided-continual-harness-evolution/SKILL.md) (`arXiv:2611.23476`), [`self-evolution-stopping-rule`](../skills/self-evolution-stopping-rule/SKILL.md) (`arXiv:2610.04756`)
- **Rules**: [`recursive-improvement.md`](../rules/recursive-improvement.md), [`skill-system-design.md`](../rules/skill-system-design.md)
- **Research Briefs**: [`criteria-exposure-verifier-overfitting`](./criteria-exposure-verifier-overfitting.md) (`arXiv:2611.08318`), [`roboace-adversarial-curriculum-execution-coevolution`](./roboace-adversarial-curriculum-execution-coevolution.md) (`arXiv:2611.13034`), [`values-shape-self-improving-coding-agents`](./values-shape-self-improving-coding-agents.md) (`arXiv:2611.23067`)
