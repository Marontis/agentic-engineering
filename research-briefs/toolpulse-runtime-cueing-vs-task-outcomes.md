# Beyond Clumsy Agentic Tool Calling: ToolPulse Runtime Cueing, Spotting, and the Behavior-vs-Outcome Gap

> **Source**: [arXiv:2611.19275](https://arxiv.org/abs/2611.19275) — Xindi Yang, Yan Liu, Jiajun Sun (*Beyond Clumsy Agentic Tool Calling: How Cueing and Spotting Make the Difference*, Tongji University & Shanghai Highly Electrical Appliance Co., Nov 2026)
> **Praxis Source ID**: `src:2611-19275v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

`ToolPulse` introduces a clean online pre/post-execution tool-monitoring middleware and evaluates four assistance modalities across **`1,350` SWE-agent trajectories** (`90` Python, C++, and Java bug-fix tasks $\times$ `3` backbones $\times$ `5` conditions). However, while runtime interventions elicit **`61.6%–90.9%` substantive detour adjustments**, **aggregate end-to-end bug-repair resolution stays essentially flat against the unassisted baseline (`101/270` baseline vs `99–105/270` assisted, never shifting any `30`-task language-model cell by more than `±2` instances, with newly solved tasks offset by regressions on previously passing tasks)**, and most paired token-cost confidence intervals include zero. Under [`skill-design-methodology`](../skills/skill-design-methodology/SKILL.md), packaging a runtime intervention with null net task-resolution lift and per-instance regression churn as a standalone `SKILL.md` would overstate end-to-end efficacy; instead, we record its symptom taxonomy, negative findings on auxiliary-LLM spotters and premature triggers, and process-vs-outcome dissociation here and as guardrails in [`rules/skill-system-design.md`](../rules/skill-system-design.md).

---

## Two-Granularity Symptom Taxonomy & Detection Mechanics (`§3–§4`)

Informed by a `240`-run Python pilot (`30` stratified OmniCode tasks $\times$ `2` models $\times$ `4` sequence detectors, `§3`), `ToolPulse` intercepts proposed calls at pre-execution $\mathcal{H}_t^- = (q, \tau_{<t}, r_t, a_t)$ and inspects execution results at post-execution $\mathcal{H}_t^+ = (\mathcal{H}_t^-, o_t)$ (`Eqs. 4–5`), organizing six symptoms across two temporal granularities (`Table 5`):

1. **Local Clumsy Tool-Use Behaviors**:
   - **`Calling Repetition` (`CR_t`, `Eq. 6`)**: Three consecutive identical `(tool, args)` proposals ($a_{t-2} = a_{t-1} = a_t$). Delayed from `2` to `3` steps after the pilot showed `DeepSeek-V4-Pro` escaped `2`-step duplicates autonomously **`100.00%` (`3/3`, `0%` recurrence)** without prompts vs `58.33%–88.89%` under `2`-step intervention (`Table 4`).
   - **`Blind Command` (`BC_t`, `Eq. 7`, pre-execution intercept)**: Proposing `Edit(a_t, f)` when target file $f \notin V_{t-1}$ has never been inspected in the current task.
   - **`Wandering Flood` (offline-only)**: Unconstrained high-cost Retrieve steps (`>95th` percentile observation length or execution time per model/language, confirmed by `Kimi-K3` judge). Kept **strictly offline** because broad searches are frequently task-justified (`only 799/3,191` [`25.0%`] screened steps across `400/1,350` [`29.6%`] trajectories were true floods; `90%` human agreement on `100` audited verdicts, `8.8%` [`129/1,470`] false-negative rate in the `90th–95th` percentile band, `Table 7` & `§B.3`).
2. **Multi-Step Tool-Use Detours**:
   - **`Functional Cycle` (`FC_t`, `Eq. 10`)**: `Sequitur` grammar induction over `13` deterministic bug-fix action/outcome labels (`Ls, Lt, Lb, E, P, Ps, Pi, Pr, Vp, Vf, Ve, G, Emp`, `Table 2`) detecting `3` consecutive repetitions ($s^3$) of a sequence $|s| > 2$ (fired at most once per distinct $s$).
   - **`Strategic Fixation` (`SF_t`, `Eq. 12`)**: Incremental `Matrix Profile` over `36`-dim step vectors (`1` z-scored `log1p` thought length, `16`-dim triple-hash tool block weighted `0.80`, `16`-dim triple-hash args block weighted `0.45`, plus observation length, execution time, and error bit; window sizes `3/5/8`, `500`-step sliding history) firing when all `3` pairwise RMS Frobenius distances among adjacent non-overlapping windows $(W_1, W_2, W_3)$ satisfy $\le 1.10$ (`§A.2`).
   - **`Failure Inertia` (`FI_t`, `Eq. 9`)**: Repeating an identical normalized error signature $\sigma_t = (u_t, \text{errorType}_t, \text{errorFingerprint}_t)$ within an `8`-step lookback window with **zero intervening state-changing actions** ($z_j \in \mathcal{L}_{\mathrm{change}}$)—avoiding the pilot pitfall where generic `Failed Action` prompts disrupted normal dependency-installation recovery (e.g., `missing-pytest`, `§3.2`).

---

## Main Empirical Evaluation (`1,350` Trajectories, `§5`)

Using `SWE-agent` (`T = 0, top-p = 1`) across **`90` stratified OmniCode bug-fix tasks** (`30` Python, `30` C++, `30` Java; `10` easy / `10` medium / `10` hard per language) and **`3` backbones** (`DeepSeek-V4-Pro`, `Qwen3-Coder-Plus`, `Qwen3.6-27B` dense `bf16`), `270` unassisted baseline runs are paired against `1,080` assisted runs spanning four strategies (`270` runs each): **`Reminder-Only Verbal Cueing`**, **`Guided Verbal Cueing`** (adds fixed corrective rule), **`Visual Cueing`** (wraps observation + reminder in JSON), and **`Tactile Spotting`** (context-specific advice generated live by `Qwen3.7-Flash` over the last `3` steps). Detour triggers are scored by `Kimi-K3` (`[-8, +3]` step window; `100`-sample expert audit agreement: **`87%` `trigger_validity` [`12` `valid -> invalid`, `1` `unclear -> invalid`], `97%` `behavior_after_trigger`, `98%` `corrective_response`**, `Table 15`).

### 1. Symptom Detection & Substantive Behavioral Adjustment (`RQ1`, `Table 6`, `1,080` Assisted Runs)

| Symptom | Affected Trajectories | Total Events | Valid Triggers | Ceased Events | Substantive Corrective Response |
|:--------|:---------------------:|:------------:|:--------------:|:-------------:|:-------------------------------:|
| **`Calling Repetition`** | `34 / 1,080` | `164` | Rule-defined (`164`) | `80 / 164` (`48.8%`) | `20 / 80` (`25.0%` of ceased; `12.2%` of all `164`) |
| **`Blind Command`** (pre-exec) | `36 / 1,080` | `86` | Rule-defined (`86`) | `67 / 86` (`77.9%`) | `41 / 67` (`61.2%` of ceased; `47.7%` of all `86`) |
| **`Functional Cycle`** | `42 / 1,080` | `48` | `29 / 48` (`60.4%`, `19` invalid) | `19 / 29` (`65.5%`) | **`19 / 19`** (**`65.5%`** of valid) |
| **`Strategic Fixation`** | `570 / 1,080` | `1,841` | `1,134 / 1,841` (`61.6%`, `700` invalid) | `715 / 1,134` (`63.1%`) | **`699 / 715`** (**`61.6%`** of valid, `97.8%` of ceased) |
| **`Failure Inertia`** | `101 / 1,080` | `154` | `110 / 154` (`71.4%`, `42` invalid) | `100 / 110` (`90.9%`) | **`100 / 100`** (**`90.9%`** of valid) |

*Note*: `Strategic Fixation` shows a **`38.0%` (`700/1,841`) false-positive trigger rate** (`39.6%` [`19/48`] on `Functional Cycle`, `27.3%` [`42/154`] on `Failure Inertia`) even before accounting for the `12%` `valid -> invalid` judge over-calling found in manual audit (`Table 15`).

### 2. Concise Reminders Outperform Elaborate Cueing & Auxiliary-LLM Spotting (`RQ2`, `Tables 8–9`)

| Metric / Symptom (`Substantive / Eligible`) | `Reminder-Only` | `Guided Verbal` | `Visual (JSON)` | `Tactile Spotting` (`Qwen3.7-Flash`) |
|:--------------------------------------------|:---------------:|:---------------:|:---------------:|:------------------------------------:|
| **Pooled Aggregate Substantive Rate** | **`67.8%` (`158/233`)** | `59.2%` (`141/238`) | `52.6%` (`152/289`) | `56.1%` (`428/763`) |
| **`Strategic Fixation` Rate & Trigger Density** | **`69.8%` (`118/169`)**, `[1.35/100]` | `59.3%` (`96/162`), `[1.35/100]` | `62.0%` (`106/171`), `[1.39/100]` | `60.0%` (`379/632`), **`[6.40/100]`** |
| **Consecutive `Strategic Fixation` Trigger Runs** | **`0 / 140`** (`0/236`) | **`0 / 140`** (`0/236`) | **`0 / 146`** (`0/245`) | **`107 / 144` trajs (`974/1,124` = `86.7%`, max len `30`)** |
| **`Blind Command`** (concrete precondition) | `56.3%` (`9/16`) | **`78.6%` (`11/14`)** | `62.5%` (`10/16`) | `27.5%` (`11/40`) |
| **`Failure Inertia`** | `87.0%` (`20/23`) | `91.7%` (`22/24`) | **`96.3%` (`26/27`)** | `88.9%` (`32/36`) |
| **`Calling Repetition`** | **`25.0%` (`4/16`)** | `22.2%` (`6/27`) | `5.9%` (`4/68`) | `11.3%` (`6/53`) |

- **Auxiliary-LLM spotting induces consecutive re-trigger storms**: While affecting nearly the same number of trajectories (`144` vs `140`), `Qwen3.7-Flash` tactile spotting inflated `Strategic Fixation` trigger density **`4.74×` (`6.40` vs `1.35` per `100` actions)** via consecutive back-to-back trigger runs (`median 3 [Q1=2, Q3=5], max 30`) absent (`0%`) from all three static cueing strategies (`Table 9`), while dropping `Blind Command` substantive correction from `78.6%` to `27.5%`. Fixed guidance beats bare reminders **only** when the corrective step is concrete and invariant (`Inspect file before Edit`: `78.6%` vs `56.3%`).

### 3. The Behavior-vs-Outcome Gap (`RQ3`, `Table 10`, `270` Paired Instances per Arm)

- **Flat aggregate bug-repair totals with bilateral gain/loss churn**: Total passing patches across the `270` model–task pairs are **`101` (`37.4%`) for `Baseline`** (`DeepSeek-V4-Pro` `38/90`, `Qwen3.6-27B` `35/90`, `Qwen3-Coder-Plus` `28/90`—note `DeepSeek-V4-Pro` had the highest pass count despite the highest `Strategic Fixation` rate at `3.40` vs `1.82` per `100` steps on `Qwen3.6-27B`) vs **`105` (`Reminder-Only`), `104` (`Guided`), `99` (`Visual`), and `103` (`Tactile Spotting`)**.
- Across `36` `(language × model × strategy)` cells (`30` tasks each), `16` showed `0` net change, `13` gained `1–2` tasks, and `7` lost `1–2` tasks (no cell shifted by `> 2`), with interventions simultaneously rescuing baseline failures and breaking baseline passes (e.g., `Qwen3.6-27B` Java `Reminder-Only`: `5` vs `4` via `4` newly passed and `3` regressed; `Qwen3-Coder-Plus` Python `Guided`: `18` vs `19` via `2` gains and `3` losses). Similarly, pilot custom-tool abstraction prompts (`§3.2`) fired `< 5` times across `180` runs and yielded **`0` created or invoked custom tools**.

---

## Relevance to Praxis

- **Rules**: [`rules/skill-system-design.md`](../rules/skill-system-design.md) — codifies delayed repetition/error-inertia thresholds, concise state reminders over auxiliary-LLM spotters, and mandatory tracking of per-instance `(Gain / Loss)` regressions alongside local detour cessation.
- **Related Artifacts**: [`ledger-orchestrated-coding-loop`](../skills/ledger-orchestrated-coding-loop/SKILL.md), [`decoupled-interface-action-repair`](../skills/decoupled-interface-action-repair/SKILL.md), [`mcp-hallucination-boundary-guards`](../skills/mcp-hallucination-boundary-guards/SKILL.md), and [`selective-step-verification`](../skills/selective-step-verification/SKILL.md).
