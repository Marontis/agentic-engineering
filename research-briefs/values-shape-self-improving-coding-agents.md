# Values Shape What Self-Improving Coding Agents Build

> **Source**: [arXiv:2611.23067](https://arxiv.org/abs/2611.23067) — Jason Liang, Dylan Waldner, Risto Miikkulainen (`Cognizant AI Lab`, November 2026)
> **Praxis Source ID**: `src:2611-23067v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

`arXiv:2611.23067` is a **controlled behavioral experiment** holding the self-improvement harness strictly fixed (`Claude Code` with `Claude Opus 5`, `15` outer iterations $\times$ `0.5 h` cap, `10` independent runs per condition across `6` open-ended coding benchmarks) while varying only a ~`135`-word higher-order motivational value preamble derived from Schwartz's theory of basic values (`openness`, `conservation`, `enhancement`, `transcendence`, vs. `7`-word `none` and `132`-word `placebo`). Because the paper introduces no new multi-step runtime procedure beyond selecting and freezing an exploratory value disposition outside the agent's editable scope—while iterative solver/harness evolution loops are already covered in [`regularized-harness-evolution`](../skills/regularized-harness-evolution/SKILL.md) and [`hyperagent-self-improvement`](../skills/hyperagent-self-improvement/SKILL.md)—its actionable contribution is a quantitative **DO/DON'T design rule** in [`recursive-improvement.md`](../rules/recursive-improvement.md) backed by this Research Brief.

---

## Experimental Setup: Schwartz Value Dispositions in `15`-Iteration Solver RSI

Each run gives `Claude Code` (`Claude Opus 5`) a starter solver, local development evaluator, persistent workspace memory across `15` sequential `30`-minute iterations, and one of six system-level dispositions (`§3`, `Appendix A`):

- **`openness` (`133` words)**: Curiosity, creative freedom, questioning assumptions, exploring bold structural redesigns.
- **`conservation` (`136` words)**: Stability, caution, incremental verified edits, respecting proven conventions.
- **`enhancement` (`136` words)**: Ambition, competitive excellence, maximizing benchmark metrics relentlessly.
- **`transcendence` (`136` words)**: Clarity, maintainability, principled generality, restraint against brittle hacks.
- **Controls**: **`none` (`7` words)** minimal task instruction, and **`placebo` (`132` words)** length-matched neutral operational prose.

---

## Held-Out Benchmark Results Across `6` Tasks (`§4`, `Tables 1–2`)

Evaluated on unseen held-out test instances using Cliff's $\delta$ and stratified/Wilcoxon permutation tests (`10` runs/condition $\times$ `6` conditions $\times$ `6` tasks = `360` main runs):

| Condition | Pooled Final vs. `none` ($\delta$, $p$) | Pooled AUC vs. `none` ($\delta$, $p$) | Mean Rank (`6` tasks) | `ALE-Bench` (`AHC039`) | `Circle Packing` (score) | `Entity Matching` ($F_1$) | `Game 2048` (score) | `Symbolic Reg.` ($R^2$) | `SZ-Tetris` (lines) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **`openness`** | **`+0.38` ($p < 0.001$)** | **`+0.40` ($p < 0.001$)** | **`1.33`** (`#1` on `5/6`) | **`571,927`** | **`4.85`** | **`0.666`** | `124,782` | **`0.946`** | **`223.0`** |
| `enhancement` | `+0.08` ($p = 0.653$) | `+0.06` ($p = 0.728$) | `2.67` | `549,814` | `3.97` | `0.631` | **`132,455`** | `0.941` | `204.2` |
| `none` (`7`w) | — | — | `3.17` | `550,220` | `3.72` | `0.637` | `126,177` | `0.939` | `200.1` |
| `placebo` (`132`w) | `-0.06` ($p = 0.355$) | `-0.05` ($p = 0.442$) | `3.83` | `547,108` | `3.68` | `0.629` | `118,904` | `0.936` | `198.4` |
| `transcendence` | **`-0.16` ($p = 0.043$)** | **`-0.27` ($p = 0.014$)** | `4.17` | `540,912` | `3.61` | `0.618` | `78,627` | `0.935` | `196.8` |
| **`conservation`** | **`-0.27` ($p = 0.003$)** | **`-0.20` ($p = 0.018$)** | **`4.83`** (worst) | `511,544` | `3.30` | `0.591` | `109,318` | `0.928` | `191.7` |

- **Opposing Schwartz poles diverge sharply (`Table 2`)**: **`openness` beats `conservation` pooled at $\delta = +0.58$ ($p < 0.001$)**, winning `ALE-Bench` at $\delta = +1.00$ ($p < 0.001$), `Circle Packing` at $\delta = +0.72$ ($p = 0.003$; matching or exceeding best-known `Packomania` packings on `11` and `24` of `38` held-out even $n$ tiers vs. `10` and `10` for `none`, and reaching `2.635983085` at $n = 26$—surpassing both `AlphaEvolve` `2.635862756` and `ShinkaEvolve` `2.635982839`), `Entity Matching` at $\delta = +0.60$ ($p = 0.034$), and `SZ-Tetris` at $\delta = +0.54$ ($p = 0.025$). `enhancement` beats `transcendence` pooled at $\delta = +0.24$ ($p = 0.024$), led by `Game 2048` ($\delta = +0.92, p < 0.001$: `132,455` vs. `78,627`).
- **Architectural divergence, not compute spend, drives the gap (`§5`, `Figure 4`, `Tables E2–E4`, `Appendix F`)**: `openness` builds larger, structurally richer solvers than `none` on `6/6` tasks (`ALE-Bench`: `1,771` mean LOC vs. `949` `none` and `395` `conservation`, where **`10/10` `openness` runs invent free-cell / graph-cut polygon search** while **`10/10` `conservation` runs stay trapped in local column search**). Held-out score correlates with solver LOC, cyclomatic complexity, and cognitive complexity ($\rho = +0.29, +0.29, +0.28$) rather than dev evaluations (`-0.05`), API spend (`+0.11`), or wall time (`+0.03`). Restricting `Game 2048` to tuning weights inside a fixed expectimax engine shrinks cross-value spread **`2.6x` (`1.81` SD editable solver $\to$ `0.70` SD fixed engine)**.

---

## Governance & Prompt-Design Ablations (`Appendix G`, `Tables G1–G2`, `Figures G1–G5`)

1. **Making values self-editable degrades `openness` (`Table G1`)**: Allowing the agent to rewrite its own value file every iteration compresses the `6`-condition mean range **`3x`**, bloats value files several-fold with narrow task heuristics, and **significantly drops `openness` on `ALE-Bench` from `571,927` to `557,242` ($\delta = -0.64, p = 0.009$)**—eliminating its lead over self-modifying `none-sm` (`552,375`, $p = 0.573$), while lifting `conservation` (`511,544 -> 536,851`, $\delta = +0.58, p = 0.045$) only by letting it shed excessive caution.
2. **Distilling values from AI-safety or self-improvement papers defaults to caution (`Figure G2`)**: Values distilled across `20` general AI-safety/alignment papers (`lit-general`: `535,856` `ALE-Bench`, `119,565` `Game 2048`) or `20` self-improvement papers (`lit-selfimprove`: `545,241` `ALE-Bench`, `107,936` `Game 2048`) score **below `none`** (`550,220` / `126,177`) because literature synthesis gravitates toward conservative "incremental, risk-averse" boilerplate.
3. **Motivational dispositions beat rigid `"You MUST"` mandates (`Table G2`)**: Rewriting `openness` (`133` words, `571,927`) into deontological rule mandates (`175` words, `559,659`, $\delta = -0.54, p = 0.024$) or utilitarian reward-maximization framing (`173` words, `561,063`, $\delta = -0.50, p = 0.023$) significantly lowers `ALE-Bench` scores *(paper caveat: the rewrites are also ~`40` words longer)*.
4. **Model capability floor (`Figure G5`)**: On `ALE-Bench`, the `openness > conservation` separation holds on `Claude Sonnet` (`478,869` vs. `393,062`) but vanishes on `Claude Haiku` (`292,861` vs. `296,058`), where flat iteration curves prevent structural algorithm invention.

---

## Related Artifacts

- **Skills**: [`hyperagent-self-improvement`](../skills/hyperagent-self-improvement/SKILL.md) (`arXiv:2603.19461`), [`regularized-harness-evolution`](../skills/regularized-harness-evolution/SKILL.md) (`arXiv:2609.24972`), [`mcts-full-harness-optimization`](../skills/mcts-full-harness-optimization/SKILL.md) (`arXiv:2611.06254`)
- **Rules**: [`recursive-improvement.md`](../rules/recursive-improvement.md), [`skill-system-design.md`](../rules/skill-system-design.md)
- **Research Briefs**: [`flex-rsi-frontier-agent-benchmark`](./flex-rsi-frontier-agent-benchmark.md) (`arXiv:2611.08946`), [`self-improving-agent-harnesses-framework`](./self-improving-agent-harnesses-framework.md) (`arXiv:2611.22299`), [`self-organized-agent-self-improvement`](./self-organized-agent-self-improvement.md) (`arXiv:2611.23219`)
