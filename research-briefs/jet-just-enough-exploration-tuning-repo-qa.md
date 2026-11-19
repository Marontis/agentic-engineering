# JET: Just-Enough Exploration Tuning for Mitigating Over-Exploration in Repository-Level QA

> **Source**: [arXiv:2611.22539](https://arxiv.org/abs/2611.22539) — Yoonho Choi, Taehyeon Han, Seonghyeon Lee (*JET: Just-Enough Exploration Tuning for Efficient Tool-Calling Agents in Repository-Level Question Answering*, Nov 2026)
> **Praxis Source ID**: `src:2611-22539v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

Per [`AGENTS.md`](../AGENTS.md) triage criteria, `JET` is a task-specific supervised fine-tuning (`LoRA SFT`) pipeline evaluated in single-seed runs on two `8B` open-weight models (`Qwen3-8B` and `Ministral-3-8B-Instruct`) over one Python repository-QA scaffold (`SWE-QA-Pro` / `SWE-QA`), while inference-time codebase exploration and pre-call evidence gating are already covered by [`cost-effective-repo-exploration`](../skills/cost-effective-repo-exploration/SKILL.md) and [`necessary-tool-evidence-path`](../skills/necessary-tool-evidence-path/SKILL.md). Moreover, the authors explicitly note (`§7`) that `JET`'s offline golden-step labeling requires sampling $K = 3$ forced answers and invoking a frontier LLM judge at **every step of every training trajectory**, was not verified against human sufficiency labels or tested beyond `8B` Python QA, and trades off `-1.14` to `-5.32` points against `SFT` on `Qwen3-8B` expert distillation. Its durable engineering contributions—demonstrating that expert `SFT` distills severe **over-exploration**, that prompted tool-call budgets (`Budget Tracker`) can backfire (`+31%` to `+44%` calls), and that trajectory truncation fails across model families unless paired with an **upweighted halting rationale ($\lambda = 5$)**—are captured here and in [`rules/recursive-improvement.md`](../rules/recursive-improvement.md).

---

## Over-Exploration Diagnosis & `JET` Training Pipeline (`§3–§5.1`)

When answering free-form repository questions (`> 10` tool calls/question on average, `30`-step cap, `32,768`-token context, scored on `5` continuous rubric criteria rather than binary exact-match short answers), forcing the agent to stop and answer after every step $s_i$ reveals **over-exploration**: intermediate forced-answer judge scores reach a plateau early while both base `8B` agents and `Claude Sonnet 4.5` expert `SFT` trajectories (`1,000` traces) keep reading helper files, tests, and configs until hitting the `30`-step ceiling (`Figures 1–2`), compounding superlinear context-reprocessing token costs.

`JET` modifies offline `SFT` data curation across three stages (`Figure 3`, `Table 4`):
1. **Golden-Step Labeling via Forced Rollouts (`§4.1`)**: At every step $i \in \{0, \dots, n\}$ of a training trajectory (`400` `SWE-QA-Pro` training rollouts in `Self`—`399` on `Qwen3-8B` after `1` context-length error—or `1,000` `Claude Sonnet 4.5` trajectories in `Expert`, `60` validation questions), sample $K = 3$ forced answers (`temperature = 0.6`, `--- STOP AND ANSWER NOW ---`) and score each with `gpt-6-luna` against $a^{\text{ref}}$ (using the expert trajectory's own final answer as $a^{\text{ref}}$ when gold references are absent). Select the earliest argmax $i^\star = \min \arg\max_{i \in \{0,\dots,n\}} \bar{S}_i$ and its highest-scoring answer $\hat{a}$.
2. **Voice-Matched Sufficiency Rationale Insertion (`§4.2`)**: When $i^\star < n$, truncate the trajectory at $s_{i^\star}$ and prompt `Qwen3.8-27B` (`temperature = 0`, max `800` tokens, `3` `Claude Sonnet 4.5` style examples) to write a `2–4` sentence assistant message $r$ naming the specific files/functions inspected and stating that gathered evidence suffices to answer without announcing further investigation (`y_{i^\star+1} = (r, \hat{a})`). When $i^\star = n$, retain the original final turn.
3. **Halting-Span Loss Upweighting (`§4.3`)**: Because the halting rationale span $H$ (the assistant text immediately preceding `<finish>`) represents a tiny fraction of total trajectory output tokens, uniform `SFT` cross-entropy under-weights the stopping decision. `JET` assigns token weight $w_t = \lambda = 5$ for $x_t \in H$ and $w_t = 1$ otherwise, normalized by $\sum_t w_t$ (`LoRA` $r = 32, \alpha = 64$, dropout `0.1` on all linear layers, `lr = 5e-4`, batch size `16`, up to `4` epochs in `bf16`).

---

## Core Quantitative Results (`§5.4–§6.2`, `Tables 2–3, 5`)

### 1. Main Benchmark Comparison (`Table 2`: `SWE-QA-Pro` $N=260$ [`gpt-6-sol`, max `50`] & `SWE-QA` $N=720$ [`claude-sonnet-5-5`, max `100`])

| Model & Setting | Method | `SWE-QA-Pro` Score | `SWE-QA-Pro` Calls ($\Delta$) | Cost / `1K` (`$`) | `SWE-QA` Score | `SWE-QA` Calls ($\Delta$) | Cost / `1K` (`$`) |
|:----------------|:-------|:------------------:|:-----------------------------:|:-----------------:|:--------------:|:-------------------------:|:-----------------:|
| **`Qwen3-8B` (`Self`)** | `Base` | `30.88` | `18.10` | `19.2` | `36.50` | `19.57` | `23.0` |
| | `Budget Tracker` (`B=29`) | `30.29` | `26.12` (**`+44%`**) | `28.2` | `34.88` | `25.54` (**`+31%`**) | `27.8` |
| | `Autorater` (`gpt-6-luna`/step) | `30.70` | `15.23` (`-16%`) | `29.0` | `35.61` | `16.18` (`-17%`) | `33.2` |
| | `Truncated SFT` (no $r$, $\lambda=1$) | **`31.22`** | `13.37` (`-26%`) | `10.3` | **`36.91`** | `13.54` (`-31%`) | `11.7` |
| | **`JET` ($r$ + $\lambda=5$)** | `30.84` | **`12.19` (`-33%`)** | **`8.5`** | `36.34` | **`13.21` (`-33%`)** | **`10.0`** |
| **`Qwen3-8B` (`Expert`)** | `SFT` (`1,000` Sonnet-4.5 traces) | `37.07` | `22.66` | `38.3` | `52.79` | `22.18` | `36.8` |
| | `Budget Tracker` | **`37.08`** | `24.05` (`+6%`) | `43.7` | **`53.09`** | `23.17` (`+4%`) | `41.3` |
| | `Autorater` | `34.49` | **`11.31` (`-50%`)** | `27.4` | `48.42` | **`10.64` (`-52%`)** | `25.5` |
| | `Truncated SFT` | `36.52` | `21.90` (`-3%`) | `37.2` | `51.83` | `21.35` (`-4%`) | `35.0` |
| | **`JET`** | `35.93` | `16.72` (**`-26%`**) | **`24.4`** | `47.47` | `15.90` (**`-28%`**) | **`22.4`** |
| **`Qwen3-8B` (`Expert -> Self`)** | `JET -> JET` | `35.08` | `12.87` (**`-43%`**) | `16.5` | `46.25` | `12.40` (**`-44%`**) | `15.4` |
| **`Ministral-3-8B` (`Self`)** | `Base` | **`35.84`** | `14.71` | `17.8` | `46.27` | `14.68` | `19.1` |
| | `Budget Tracker` | `35.75` | `14.88` (`+1%`) | `19.7` | **`46.38`** | `14.86` (`+1%`) | `20.7` |
| | `Autorater` | `33.96` | **`10.82` (`-26%`)** | `22.0` | `45.93` | **`10.79` (`-26%`)** | `22.5` |
| | `Truncated SFT` | `35.53` | `14.96` (`+2%`) | `17.3` | `46.32` | `14.03` (`-4%`) | `16.9` |
| | **`JET`** | `34.81` | `12.94` (**`-12%`**) | **`14.4`** | `45.97` | `13.10` (**`-11%`**) | **`14.3`** |
| **`Ministral-3-8B` (`Expert`)** | `SFT` | `35.10` | `23.74` | `42.1` | `51.78` | `22.37` | `39.0` |
| | `Budget Tracker` | `35.94` | `23.37` (`-2%`) | `42.8` | `52.37` | `22.24` (`-1%`) | `41.3` |
| | `Autorater` | `34.48` | **`13.56` (`-43%`)** | `31.9` | `50.64` | **`12.21` (`-45%`)** | **`27.9`** |
| | `Truncated SFT` | **`37.02`** | `26.08` (**`+10%`**) | `47.2` | **`54.22`** | `25.65` (**`+15%`**) | `45.4` |
| | **`JET`** | `36.91` | `19.10` (**`-20%`**) | **`30.6`** | `53.83` | `18.36` (**`-18%`**) | `28.6` |
| **`Ministral-3-8B` (`Expert -> Self`)** | `JET -> JET` | `34.63` | `12.95` (**`-45%`**) | **`15.9`** | `48.55` | `12.84` (**`-43%`**) | **`16.5`** |

*\*Pricing note (`Appendix A.3`): Both `8B` models are priced at `$0.15 / 1M` input & output tokens without prompt caching; `Autorater` adds `$0.10 / 1M` input and `$0.50 / 1M` output tokens per step.*

### 2. Why Naive Baselines & Ablations Fail (`§5.4–§6.2`, `Table 3`)

- **Standard Expert `SFT` Distills Step-Limit Saturation (`§6.1`, `Figure 4`)**: Imitating unpruned `Claude Sonnet 4.5` trajectories inflates `Qwen3-8B` calls (`18.10 -> 22.66`) and pushes `Ministral-3-8B` calls (`14.71 -> 23.74`) to the `30`-step limit on **`~40%` of questions**—where **`6%–7%` of `Ministral` `SFT` runs fail to emit a valid answer even when forced**, dragging `Ministral` `SFT` (`35.10`) *below* its untuned `Base` (`35.84`) on `SWE-QA-Pro`. `JET` cuts step-limit collisions by **`43%–62%`** relative to `SFT` (answering early on `64 / 86` `Qwen3` `SWE-QA-Pro` limit-hitting questions) and beats `SFT` on `Ministral` across both score (`36.91` vs `35.10`; `53.83` vs `51.78`) and calls (`-20%` / `-18%`), though on `Qwen3` `SWE-QA` `Expert` it trades `-5.32` points (`52.79 -> 47.47`, primarily in `Completeness`: `8.90 -> 6.69` and `Reasoning`: `9.24 -> 7.75`, `Table 5`) for `-28%` calls and `-39%` cost.
- **Prompted Tool Budgets (`Budget Tracker`) Backfire**: Appending remaining tool-call counts and staged exploration guidance (`HIGH >= 70%: Broad exploration`) leaves `SFT` nearly unchanged (`-2%` to `+6%`) and causes `Qwen3-8B` (`Self`) to invoke **`+44%` and `+31%` more tools** (`26.12` and `25.54`) as it obediently executes the `"Broad exploration"` phase.
- **Truncation Without Rationale + Halting Weight ($\lambda = 5$) Fails Across Architectures**:
  - **`Truncated SFT` (no rationale, $\lambda = 1$)**: Barely reduces `Qwen3` `Expert` calls (`-3%` / `-4%`), leaves `Ministral` `Self` flat (`+2%` / `-4%`), and **increases `Ministral` `Expert` calls by `+10%` and `+15%` (`26.08` and `25.65`)**.
  - **Rationale Alone ($\lambda = 1$, `§6.2`)**: Yields `12.20` calls on `Ministral` validation, nearly indistinguishable from `Truncated SFT`—confirming that the rationale works **only when paired with loss upweighting ($\lambda = 5$)** on the halting span $H$.
  - **Fixed-Ratio Truncation (`Table 3`, `SWE-QA-Pro` `Self`)**: Truncating at `n/2` or `2n/3` instead of $i^\star$ either increases `Qwen3` calls at `2n/3` (`18.10 -> 20.94`, `+16%`) or collapses `Ministral` quality (`35.84 -> 29.68` at `n/2` [`-6.16` pts] and `31.95` at `2n/3` [`-3.89` pts] vs. `34.81` at $i^\star$).

---

## Relevance to Praxis

- **Rules**: [`rules/recursive-improvement.md`](../rules/recursive-improvement.md) — pairs golden-step truncation, sufficiency-rationale insertion, and halting-span loss upweighting ($\lambda = 5$) with existing `SFT` trajectory-curation rules (`SWE-Trail`) while warning against prompted tool-budget backfires and unpruned expert `SFT` over-exploration.
- **Related Artifacts**: [`cost-effective-repo-exploration`](../skills/cost-effective-repo-exploration/SKILL.md), [`necessary-tool-evidence-path`](../skills/necessary-tool-evidence-path/SKILL.md), [`history-guided-trajectory-collection`](../skills/history-guided-trajectory-collection/SKILL.md), and [`procedure-without-judgment-exact-verifier-slm`](procedure-without-judgment-exact-verifier-slm.md).
