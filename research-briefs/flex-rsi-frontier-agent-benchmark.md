# Flex-RSI: Benchmarking Recursive Self-Improvement of Frontier Agents

> **Source**: [arXiv:2611.08946](https://arxiv.org/abs/2611.08946) — *Flex-RSI: Benchmarking Recursive Self-Improvement of Frontier Agents* (Zhang et al. / Flex-RSI Team, November 2026)
> **Praxis Source ID**: `src:2611-08946v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

`Flex-RSI` is a `24`-task, `18`-model evaluation benchmark and empirical study measuring how frontier agents recursively improve both their task solutions and their own operating harnesses across vision, robotics, 3D reconstruction, visual creation, and infrastructure. The two-loop `executor` + `improver` harness architecture with validation noise-margin gating ($\delta = 2\sigma$) directly instantiates the existing [`recursive-self-improvement-loop`](../skills/recursive-self-improvement-loop/SKILL.md) and [`regularized-harness-evolution`](../skills/regularized-harness-evolution/SKILL.md) skills and the single acceptance-gate rule in [`recursive-improvement.md`](../rules/recursive-improvement.md). Its primary value is its quantitative cross-model comparative evidence and its findings on feedback granularity, constructive vs. single-answer task headroom, and cross-model harness transfer.

---

## Core Architecture: The Two-Loop Self-Improving Harness

Every model evaluated in `Flex-RSI` starts from the **exact same general-purpose harness** $H_0 = (E_0, I_0)$, the same starter solution $s_0$, and the same fixed compute/token/round budget on three disjoint splits ($\mathcal{D}_{\mathrm{dev}}$ with labels available to the agent, held-out $\mathcal{D}_{\mathrm{val}}$ for candidate retention, and hidden $\mathcal{D}_{\mathrm{test}}$ scored once at termination round $T$):

1. **Executor ($E_{t-1}$)**: Modifies the currently accepted task solution $s_{t-1}$, runs experiments on $\mathcal{D}_{\mathrm{dev}}$, and submits a candidate $\tilde{s}_t = E_{t-1}(s_{t-1}; \mathcal{D}_{\mathrm{dev}})$.
2. **Validation Gate with Noise Margin $\delta$**: The candidate is retained only if it improves on $\mathcal{D}_{\mathrm{val}}$ beyond a noise margin $\delta$ (initialized to $2\times$ the standard deviation of the starter solution's validation score):
   $$s_t = \begin{cases} \tilde{s}_t & \text{if } S(\tilde{s}_t; \mathcal{D}_{\mathrm{val}}) > S(s_{t-1}; \mathcal{D}_{\mathrm{val}}) + \delta, \\ s_{t-1} & \text{otherwise.} \end{cases}$$
3. **Improver ($I_{t-1}$)**: Reviews the accumulated history $\tau_{1:t}$ (trajectories, experiments, and scores) and recursively edits the harness itself—including the executor's prompts, tools, and workflow as well as the improver's own instructions, settings, and lessons:
   $$(E_t, I_t) = I_{t-1}(E_{t-1}, I_{t-1}; \tau_{1:t}).$$

---

## Quantitative Benchmark Results (`Section 4`)

`Flex-RSI` evaluates `18` models (`11` closed-source: `Claude Opus 5.5`, `Claude Sonnet 5.5`, `GPT-6 Astra`, `GPT-6.1 Sol`, `GPT-5.6 Sol`, `Gemini 4 Argon`, `Gemini 3.8 Flash`, `Gemini 3.7 Flash`, `Grok 4.6`, `Muse Spark 1.3`, `Muse Wonder 1.0`; and `7` open-weight: `Qwen3.8-27B`, `Qwen3.8-Flash-Next`, `Qwen3.6-35B-A3B`, `Gemma-4-31B-it`, `MiniMax-M3`, `GLM-5.3 Flash`, `DeepSeek-V4.1 Flash`) across `24` tasks (`20` main tasks evaluated with $\ge 6$ models, `177` total runs).

### Overall Leaderboard & Per-Area Test Scores (`Tables 2–6`, `Figure 2`)

Models are compared via pairwise win-share rank scores (`0` = last, `100` = beats all other models on the task), averaged across areas:

- **Overall Rank-Score Leaders**: `Claude Opus 5.5` leads overall (**`91.6`**, ranking #1 on `11/20` tasks), followed by `Gemini 4 Argon` (**`89.0`** across `9` tasks), `GPT-6.1 Sol` (**`77.0`**), `GPT-6 Astra` (**`65.5`**), and top open-weight model `Qwen3.8-Flash-Next` (**`49.1`**, #5 overall, beating `Gemini 3.8 Flash` and `Claude Sonnet 5.5`).
- **Self-Improvement Gain & Convergence (`Sections 4.3–4.5`)**:
  - RSI raises validation scores in **`150/177` runs (`85%`)** by a median of **`+10.4` points**.
  - **Closed-source models** improve in **`94%` of `85` runs** by a median of **`+14.9` points** (mean gain **`+26.7`** for `Claude Opus 5.5` and **`+25.7`** for `Gemini 4 Argon`), whereas **open-weight models** improve in **`76%` of `92` runs** by a median of **`+8.5` points** (`+6.8` mean for `Gemma-4-31B-it`).
  - **Round Dynamics**: The median improving run reaches `90%` of its total gain by **round `3`** in Perception and Reasoning and **round `4`** in Creation, but requires **round `6`** in Action and **round `8`** in Reconstruction (where starter solutions are weakest: median validation scores `16.7` and `19.4` vs. `60.0–78.8` in the other areas).
  - **Token Cost**: Runs consume a median of **`49.7M` tokens** (middle `80%`: `8.6M–93.4M`). Spending more tokens does *not* buy higher scores: rank correlation between relative token usage and overall score is **`-0.05`**. Top scorers `Claude Opus 5.5`, `GPT-6.1 Sol`, and `GPT-6 Astra` use **`0.35×` to `0.61×`** the task median tokens, whereas `Gemini 4 Argon` uses **`1.66×`** and `5/6` open-weight models use **`1.0×` to `1.75×`** while scoring `<50`.

| Area | Task | Metric | Starter Val Median | Best Closed-Source Test Score | Best Open-Weight Test Score | Largest Val Gain |
|:---|:---|:---|:---:|:---:|:---:|:---:|
| **Action** | `RoboDojo` (`10` tasks $\times 5$) | Task score | `0.1` | `55.1` (`Claude Opus 5.5`) | `17.8` (`DeepSeek-V4.1 Flash`) | `+68.4` |
| **Action** | `RoboCasa` (`8` tasks $\times 5$) | Success rate | `0.0` | `57.5` (`Claude Opus 5.5`) | `7.5` (`GLM-5.3 Flash`) | `+55.0` |
| **Action** | `Active Search` (`H*Bench`) | SPL | `23.0` | `79.7` (`Gemini 4 Argon`) | `69.0` (`Qwen3.8-27B`) | `+35.4` |
| **Action** | `RoboLab` (`RoboLab-120`) | RoboLab score | `8.3` | `71.9` (`Claude Opus 5.5`) | `31.6` (`Qwen3.8-27B`) | `+54.2` |
| **Action** | `LIBERO-MAX` | Dynamic SR | `31.2` | `45.8` (`Claude Opus 5.5`) | `45.8` (`Qwen3.8-Flash-Next`) | `+18.8` |
| **Action** | `LIBERO-PRO` | Success rate | `50.0` | `63.3` (`Claude Opus 5.5`) | `53.3` (`Qwen3.8-Flash-Next` / `Gemma-4` / `Qwen3.6`) | `+25.0` |
| **Reasoning** | `Ego-Exo Memory` | Accuracy | `63.7` | `72.5` (`Claude Opus 5.5`) | `60.8` (`Qwen3.8-27B`) | `+13.8` |
| **Reasoning** | `Kinematics` (`QuantiPhy`) | MRA | `27.7` | `57.2` (`Claude Sonnet 5.5`) | `49.2` (`Qwen3.8-Flash-Next`) | `+33.5` |
| **Reasoning** | `Mass` (`ABO`) | MRA | `47.2` | `63.5` (`Claude Opus 5.5`) | `62.7` (`Qwen3.8-27B`) | `+16.6` |
| **Reasoning** | `ARC-AGI-1` | pass@2 | `91.9` | `99.8` (`GPT-6 Astra`) | `91.0` (`DeepSeek-V4.1 Flash`) | `+11.2` |
| **Reasoning** | `ARC-AGI-2` | pass@2 | `82.5` | `95.8` (`GPT-6.1 Sol`) | `46.7` (`DeepSeek-V4.1 Flash`) | `+3.8` |
| **Reasoning** | `ARC-AGI-3` | RHAE | `3.8` | `44.2` (`GPT-6.1 Sol`) | `0.9` (`Qwen3.8-Flash-Next`) | `+18.4` |
| **Creation** | `Image Editing` | VLM judge + checks | `56.9` | `74.2` (`Gemini 4 Argon`) | `70.0` (`Qwen3.8-Flash-Next`) | `+22.3` |
| **Creation** | `Multi-turn Editing` | VLM judge | `68.3` | `71.1` (`Gemini 4 Argon`) | `70.2` (`Qwen3.8-27B`) | `+4.2` |
| **Creation** | `Video Generation` | Composition score | `69.1` | `93.9` (`Claude Opus 5.5`) | `91.4` (`Qwen3.8-Flash-Next`) | `+23.9` |
| **Reconstruction** | `3D Tracking` (`IGGT`) | T-mIoU | `19.4` | `79.6` (`Claude Opus 5.5`) | `61.2` (`GLM-5.3 Flash`) | `+65.4` |
| **Reconstruction** | `Scene from Photo` | Composite score | `7.7` | `66.5` (`Claude Opus 5.5`) | `40.0` (`Qwen3.8-Flash-Next`) | `+60.1` |
| **Reconstruction** | `Scene from Video` | Composite score | `17.3` | `70.9` (`Claude Opus 5.5`) | `34.5` (`Qwen3.8-Flash-Next`) | `+38.8` |
| **Perception** | `Visual Search` | Accuracy | `80.0` | `98.6` (`Gemini 4 Argon`) | `88.6` (`Qwen3.8-Flash-Next`) | `+20.0` |
| **Perception** | `Video Quality` | (SRCC + pair acc.)/2 | `78.2` | `82.1` (`GPT-6 Astra`) | `82.0` (`DeepSeek-V4.1 Flash`) | `+14.8` |

---

## Four Key Empirical Findings (`Section 5`, `Tables 7–9`)

### 1. Constructive Tasks Leave Far More Room for RSI Than Single-Answer Tasks (`Section 5.1`)
- **Single-Answer Tasks (`7` tasks)**: Where the starter solution simply forwards each question to a model, the median starter validation score is already **`78.2`**, models start **`27.5` points apart**, the median largest gain is **`+14.8` points**, and models end **`25.0` points apart** (nearly unchanged; on `ARC-AGI-1` and `ARC-AGI-2`, median gain across runs is `0.0` points).
- **Constructive Tasks (`13` tasks)**: Where the agent must build a program, robot policy, or processing pipeline from a generic starter, models start nearly tied and pull sharply apart during RSI:
  - On the **`9` scale-scored constructive tasks**, the starter scores **`19.4`** at the median, the median largest gain is **`+38.8` points** (`+65.4` on `3D Tracking`, `+68.4` on `RoboDojo`), and the spread between best and worst models widens from **`0.9` points at start to `38.8` points at end**.
  - On the **`4` binary-scored constructive tasks**, the model spread widens from **`2.5` points at start to `37.2` points at end**.

### 2. Binary Pass/Fail Feedback Starves Open-Weight Models (`Section 5.2`)
Because the validation acceptance gate ($S(\tilde{s}_t; \mathcal{D}_{\mathrm{val}}) > S(s_{t-1}; \mathcal{D}_{\mathrm{val}}) + \delta$) retains a candidate only when it raises the validation score, continuous/scale evaluators reward partial episode progress, whereas binary pass/fail evaluators reject every intermediate fix until a full episode flips to success:
- On the **`9` scale-scored constructive tasks**, open-weight models achieve a median validation gain of **`+9.9` points** across tasks vs. **`+28.4`** for closed-source models—and match closed-source gains closely on `3D Tracking` (`+39.8` vs. `+42.8`) and `Active Search` (`+29.3` vs. `+28.4`).
- On the **`4` binary pass/fail constructive tasks** (`RoboCasa`, `LIBERO-MAX`, `LIBERO-PRO`, `ARC-AGI-3`), open-weight median validation gain collapses to **`+1.6` points** (`+5.6` on `RoboCasa`, `+3.1` on `LIBERO-MAX`, `0.0` on `LIBERO-PRO`, `+0.2` on `ARC-AGI-3`), while closed-source models still achieve a median gain of **`+16.9` points** (`+51.2` on `RoboCasa`).

### 3. Strict Checks of Physical Stability and Exact Correctness Expose the Largest Frontier Gap (`Section 5.3`)
- Open-weight models come within `0.1–4.2` points of closed-source leaders on tasks scored by a VLM judge or soft tolerance (`Video Quality` `0.1`, `Mass` `0.8`, `Multi-turn Editing` `1.0`, `Video Generation` `2.5`, `Image Editing` `4.2`).
- They fall `26.5–50.0` points behind where outputs must pass strict physical simulation or exact symbolic checks (`RoboCasa` `50.0` gap, `ARC-AGI-2` `49.2`, `ARC-AGI-3` `43.3`, `RoboLab` `40.3`, `RoboDojo` `37.3`, `Scene from Video` `36.4`, `Scene from Photo` `26.5`).
- **Plausible Appearance vs. Physical Breakdown**: On `Scene from Photo`, open-weight renderings look visually plausible (Appearance score up to **`81.8`**), but fail to recover complete 3D furniture geometry (Objects score at most **`16.5`** vs. **`62.5`** for closed-source models). On `Scene from Video`, the Physics score (fraction of reconstructed objects remaining stable under gravity in simulation) is **`0.0%` for all four open-weight models**, compared to **`70.7%` for `Claude Opus 5.5`** and **`37.7%` for `GPT-6 Astra`**.

### 4. Editing the Harness Contributes Directly, While Cross-Model Harness Transfer Is Mixed (`Section 5.4`, `Tables 8–9`)

| Comparison Type | Task & Model Pair | Frozen Harness (`E` only) Test | Self-Improving Harness (`E + I`) Test | Delta / Transfer Finding |
|:---|:---|:---:|:---:|:---|
| **Frozen vs. RSI Harness (`Table 8`)** | `RoboCasa: Open Drawer` (`DeepSeek-V4.1 Flash`) | `0.0` (`5` rds) | **`40.0`** (`10` rds) | **`+40.0`** (unstuck from zero) |
| **Frozen vs. RSI Harness (`Table 8`)** | `RoboCasa: Turn On Sink Faucet` (`Qwen3.8-Flash-Next`) | `0.0` (`9` rds, val `20.0`) | **`20.0`** (`10` rds, val `40.0`) | **`+20.0`** |
| **Frozen vs. RSI Harness (`Table 8`)** | `RoboCasa: Turn On Sink Faucet` (`Claude Opus 5.5`) | `80.0` (`8` rds, val `100.0`) | **`80.0`** (`10` rds, val `80.0`) | **`+0.0`** (ceiling reached in round 8) |
| **Frozen vs. RSI Harness (`Table 8`)** | `Active Search` (`Qwen3.8-27B`) | `50.7` (`10` rds, val `41.2`) | **`69.0`** (`15` rds, val `51.7`) | **`+18.3`** |
| **Frozen vs. RSI Harness (`Table 8`)** | `Active Search` (`Qwen3.8-Flash-Next`) | `21.0` (`5` rds, val `16.5`) | **`59.3`** (`12` rds, val `50.3`) | **`+38.3`** |
| **Frozen vs. RSI Harness (`Table 8`)** | `3D Tracking` (`Qwen3.8-27B`) | `45.9` (`11` rds, val `48.9`) | **`52.4`** (`9` rds, val `53.9`) | **`+6.5`** |
| **Frozen vs. RSI Harness (`Table 8`)** | `3D Tracking` (`Qwen3.8-Flash-Next`) | `56.9` (`9` rds, val `63.4`) | **`58.9`** (`12` rds, val `65.7`) | **`+2.0`** |
| **Cross-Model Transfer (`Table 9`)** | `Open Drawer`: `DeepSeek-V4.1` from `Gemini 4 Argon` (`80.0`) | `20.0` (frozen `Argon` `E`) | **`60.0`** (fixed `Argon` `I`) vs. `40.0` (own) | **`+20.0`** over own RSI (`60.0` vs. `40.0`) |
| **Cross-Model Transfer (`Table 9`)** | `Turn On Sink Faucet`: `Qwen3.8-Flash-Next` from `Opus 5.5` (`80.0`) | `0.0` (frozen `Opus` `E`) | **`0.0`** (fixed `Opus` `I`) vs. `20.0` (own) | **`-20.0`** regression vs. own RSI (`0.0` vs. `20.0`) |
| **Cross-Model Transfer (`Table 9`)** | `Active Search`: `Qwen3.8-27B` from `Gemini 4 Argon` (`79.7`) | — | **`49.2`** (own `I` from `Argon`) vs. `69.0` (own) | **`-19.8`** regression vs. own RSI (`49.2` vs. `69.0`) |
| **Cross-Model Transfer (`Table 9`)** | `3D Tracking`: `Qwen3.8-27B` from `Claude Opus 5.5` (`79.6`) | — | **`53.8`** (own `I` from `Opus`) vs. `52.4` (own) | **`+1.4`** over own RSI (`53.8` vs. `52.4`) |

---

## Relevance to Praxis

- **Feedback Granularity in Acceptance-Gated RSI**: Provides direct empirical support for [`dense-rubric-skill-evolution`](../skills/dense-rubric-skill-evolution/SKILL.md) and [`recursive-improvement.md`](../rules/recursive-improvement.md)—when an acceptance gate requires $\Delta S > \delta$ on held-out validation episodes, binary pass/fail grading starves weaker/open-weight models (`+1.6` vs. `+9.9` median validation gain), requiring dense stage or partial-credit scoring on constructive tasks.
- **Capability-Matched Harness Adaptation**: Reinforces [`capability-matched-skill-adaptation`](../skills/capability-matched-skill-adaptation/SKILL.md)—seeding a weaker model with a stronger frontier model's evolved harness helped on only `2/4` tasks and severely regressed performance on the other `2/4` (`69.0` $\to$ `49.2` on `Active Search`; `20.0` $\to$ `0.0` on `Turn On Sink Faucet`), whereas letting the weaker model evolve its own harness from scratch improved test scores in `6/6` non-ceiling paired runs (`+2.0` to `+40.0` points).
