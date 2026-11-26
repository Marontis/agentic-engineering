# FinEvo: Solver-Guided Challenge Evolution for Long-Horizon Financial Modeling

> **Source**: [arXiv:2611.28239](https://arxiv.org/abs/2611.28239) — *FinEvo: Recursive Self-Improvement for Long-Horizon Financial Modeling* (Chengjun Pan, Shichun Liu, Zekai Zhou, Shihan Dou, Jiahang Lin, Chengsong Huang, Dingwei Zhu, Tao Gui; Peking University, Fudan University, Washington University)
> **Praxis Source ID**: `src:2611-28239v1`
> **License**: CC-BY-4.0

## Why Not a Skill?

The general subtask procedure for executable seed-task synthesis, dual solvability/verifier certification, 3-way student-failure attribution, and curriculum hardening is already covered by [`agent-data-mutual-evolution`](../skills/agent-data-mutual-evolution/SKILL.md) (`EvoMCP`, `arXiv:2610.41479`) and [`execution-driven-environment-repair`](../skills/execution-driven-environment-repair/SKILL.md) (`WEFT`, `arXiv:2609.36887`). `FinEvo` evaluates a single evolution-and-RL cycle on one backbone (`Qwen3.6-27B` over `OpenHands SDK 1.47.0`, `11` nonpublic corporate financial workbooks yielding `110` lineages, `8` synchronous `GRPO` steps) without controlled component ablations isolating post-check review or hardening (`Limitations`, `§4` & `Appendix A`). Its empirical failure statistics and upstream artifact-isolation findings are captured here and in `output/rules/agent-evaluation-quality.md`.

## Pipeline Architecture: Cleaner-Auditor Isolation + 4-Way Post-Solve Routing

1. **Upstream `Cleaner` + Isolated `Auditor` Workbook Normalization (`§2.1`)**:
   - Starting from `11` real-world multi-sheet corporate financial `.xlsx` workbooks, a `Cleaner` agent normalizes layout, replaces company/project/date identifiers, and **synthesizes explicit assumption drivers** where raw sheets contained hardcoded values so target statements compute end-to-end.
   - A separate `Auditor` session verifies formula recalculation and business coherence while keeping all anonymization maps and cleaning logs strictly **upstream** of task authoring and solver sandboxes.
2. **Lineage Seeding & Programmatic Pre-Solve Preflights (`§2.2`)**:
   - Each source workbook seeds `5` **Modeling** (blanked target blocks) and `5` **Debugging** (planted multi-sheet formula faults) lineages (`110` total: `88` train, `22` held-out within-source dev; median `8` worksheets [range `1–115`], median `51` scored target cells [range `3–4,548`]).
   - Every authored version must pass automated construction/formula replay checks, **oracle pass (`score == 1`)**, and **unchanged-input negative control (`score == 0` on unmodified starter workbook)**; failures loop directly to **`Check fails`**.
3. **Solver Execution & Post-Check Task-Identifiability Review (`§2.3`)**:
   - Check-passing tasks are attempted by the current `Qwen3.6-27B` solver (`OpenHands`, bash + Python `openpyxl`/LibreOffice recalculation; median `162.5k` train cumulative context tokens [mean `192.5k`, P90 `346.4k`, max `1,020.6k` across `7` context segments] and `47` median steps).
   - **Solved tasks** route to **`Harden`** (deepening cross-statement dependencies).
   - **Failed tasks** undergo a dedicated **post-check `Reviewer` audit** separating genuine solver capability gaps (**`Accept`**) from **unidentifiable or defective public specifications (`Revise`)**.

## Key Quantitative Findings

### 1. Why Programmatic Preflights Alone Are Insufficient (`Tables 1–6`, `§3.2`)

- **Low single-shot validity (`Table 1`)**: In Round 1, only **`27/110` (`24.55%`)** lineages were immediately valid (`13` [`11.82%`] accepted + `14` routed to harden), while **`83` (`75.45%`)** required repair (`76` failed programmatic checks + `7` routed to `Revise`). By Round 3, `95/110` (`86.36%`) were valid and `80` (`72.73%`) accepted (`2.15` mean versions/task vs. `6.17` [`2.87x`] on the `30` [`27.27%`] tail lineages requiring `> 3` rounds, which consumed `185/357 = 51.82%` of all model-authored versions; `110/110` accepted by Round 10).
- **`80.00%` return rate & `19/20` confirmed post-check specification defects (`Tables 3–4`)**: Across evolution, **`88/110` (`80.00%`)** lineages hit at least one return:
  - **`138` `Check fails`** across `82` tasks (`136` construction/replay failures, `1` unchanged-input negative-control pass, `1` reference gate failure).
  - **`20` post-check `Revise` decisions** across `14` tasks (out of `130` normal solver failures on check-passing tasks), where **`19/20` (`95%`) exposed real task-specification defects** invisible to `oracle == 1` / `unchanged_input == 0`: `6` missing public business assumptions (e.g., `F04-D002`, where all `28` target formulas passed oracle checks yet the public prompt omitted expense-category labels and allocation ratios), `4` instruction scope/meaning ambiguities, `3` structural-target mismatches, and `5` reference/build/recalculation defects (`1` solver-side error). `63/110` (`57.27%`) tasks were accepted immediately on the version following a return (`54` after `Check fails`, `9` after `Revise`).
- **Structural vs. volume hardening (`Tables 2, 5–6`)**: `45` tasks (`40.91%`) underwent `89` hardenings (`68` normal solver runs: `37` [`54.41%`] failed -> `33` [`48.53%`] accepted, `4` [`5.88%`] revised; `31` [`45.59%`] solved -> hardened again). Among `67` comparable pairs, **`27` (`40.3%`) hardened dependency depth without adding target cells** (`23` unchanged, `4` fewer—e.g., `F03-D001` `v6 -> v7` replacing `5` local sign/operator typos with `5` cross-period business-driver faults such as `CapEx_t = Revenue_t * rate_{t+1}`).

### 2. Long-Horizon `GRPO` Gains & Unseen Category Transfer (`Tables 7–8`, `§3.3–3.4`)

Eight synchronous `GRPO` updates on the `88` evolved training tasks (`32` queries $\times$ `8` fresh trajectories = `256`/step, `LR = 4e-6`, binary whole-task reward $r_{qj} = \mathbf{1}[a_{qj} = 1]$):

| Benchmark / Subset | Base `Qwen3.6-27B` | Post-`FinEvo` `Qwen3.6-27B` | Gain ($\Delta$) |
|:-------------------|:------------------:|:---------------------------:|:---------------:|
| `FinEvo` Held-Out Dev (`22` tasks, `avg5` whole-task) | `22.73%` | **`29.09%`** | **`+6.36 pp`** (`+28.0%` rel.) |
| `FinEvo` Held-Out Dev (`avg5` cell target accuracy) | `52.52%` | **`58.25%`** | **`+5.73 pp`** |
| — Modeling subset (`11` tasks, whole-task / cell acc.) | `23.64%` / `54.18%` | **`30.91%` / `66.83%`** | `+7.27 pp` / `+12.65 pp` |
| — Debugging subset (`11` tasks, whole-task / cell acc.) | `21.82%` / `50.85%` | **`27.27%`** / `49.66%` | `+5.45 pp` / `-1.19 pp` |
| `SpreadsheetBench 2 Financial` (`297` external tasks) | `13.13%` (`39/297`) | **`19.19%`** (`57/297`) | **`+6.06 pp`** |
| — **Unseen `Template filling` (`97` tasks, `0` in RL)** | `16.49%` (`16/97`) | **`29.90%`** (`29/97`) | **`+13.40 pp`** |

- **Independent solvability check**: On `8` randomly sampled `FinEvo` tasks where `Qwen3.6-27B` (`OpenHands`) scored `0/8`, `GPT-6` (`Codex`) solved **`6/8`**, confirming that accepted `FinEvo` tasks reflect genuine long-horizon reasoning gaps rather than broken specifications.

## Limitations & Failure Modes

- **No component-level RL ablations**: Because all `88` training tasks come from the full pipeline (`Check fails` + `Revise` + `Harden`) and only one outer evolution-plus-RL cycle was run, the downstream RL share attributable specifically to `Revise` vs. `Harden` is unmeasured.
- **Debugging partial-credit trade-off**: Optimizing binary whole-task `GRPO` reward raised Debugging whole-task completion (`21.82% -> 27.27%`) while slightly lowering mean partial cell accuracy (`50.85% -> 49.66%`).

## Relevance to Praxis

- **Rules**: [`agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md) — Demonstrates why programmatic `reference-pass` and `empty/unchanged-fail` preflights (`Sandman`, `EvoMCP`) must be followed by solver-failure task-identifiability review (`19/20` post-check `Revise` hits) when public prompts can omit hidden domain assumptions.
- **Skills**: [`agent-data-mutual-evolution`](../skills/agent-data-mutual-evolution/SKILL.md) and [`certified-task-verifier-harness`](../skills/certified-task-verifier-harness/SKILL.md).
- **Specs**: [`adk-eval-quality-gate.spec.md`](../specs/adk-eval-quality-gate.spec.md) and [`self-improving-agent.spec.md`](../specs/self-improving-agent.spec.md).
