# RecurSciBench: Benchmarking Recursive Self-Improvement in Data-Driven Scientific Research

> **Source**: [arXiv:2611.32508](https://arxiv.org/abs/2611.32508) — Wenxi Xu, Chuan Qin, Zihan Wang, Zixing Chen, Le Zhang, Jingbo Zhou, Hao Wang, Yuanchun Zhou, Hengshu Zhu (CAS CNIC & Baidu, 2026)
> **Praxis Source ID**: `src:2611-32508v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Why Not a Skill?

`RecurSciBench` is a **multi-discipline scientific RSI transfer benchmark** and automated task-curation pipeline (`RecurSciPipe`: `SciDataProfiler`, `SciTaskDesigner`, `SciTaskBuilder`, `SciTaskReviewer` enforcing `4` execution checks and `3` scientific-validity checks) rather than a new agent self-improvement algorithm. It evaluates `4` existing RSI harnesses (`EvoScientist`, `SIA-H`, `HyperAgents`, `InternAgent-1.5`) on a shared `GLM-5.3-Flash` backbone across `58` real-world scientific datasets (`96` tasks across `Physics`, `Life sciences`, `Earth & space sciences`, and `Chemistry`). Its actionable lessons—that **`50%` (`12/24`) of evolved states degrade held-out performance**, that **positive aggregate gains (`+2.24%`) routinely mask losses on `60%` (`12/20`) of test tasks**, and that **data-analysis (`A`) experience can transfer better to forward modeling (`F`) than `F` itself**—directly strengthen `"DON'T: Accept modifications based on aggregate metrics alone"` in [`../rules/recursive-improvement.md`](../rules/recursive-improvement.md) and complement [`rsi-pdebench-self-improving-pde-agents.md`](rsi-pdebench-self-improving-pde-agents.md) and [`scoped-multi-agent-harness-composition`](../skills/scoped-multi-agent-harness-composition/SKILL.md).

---

## Benchmark Architecture & Transfer Protocol

- **Two-Pool Disjoint Design (`96` Tasks across `58` Families)**:
  - **Evolution Pool (`G-evolve`, `38` families / `76` tasks)**: Each dataset family supplies a paired **Data Analysis (`A`)** task (`10` expert-rubric criteria) and **Predictive/Mechanistic Modeling (`F`)** task (held-out executable metric mapped via bounded normalization to $[0, 1]$ around human/baseline anchors).
  - **Held-Out Test Pool (`G-test`, `20` independent families / `20` `F` tasks, `5` per discipline)**: Zero dataset or domain-file overlap with `G-evolve`; every evolved state is evaluated over `3` independent test runs (`60` rollouts per state) using normalized improvement $\Delta^*$.
- **Three Transfer Regimes (`6` Evolved States per RSI System = `24` Total States)**:
  1. **Within-type (`All-F -> G-test`)**: Evolve on `38` `F` tasks, test on `20` `F` tasks.
  2. **Cross-type (`All-A -> G-test`)**: Evolve purely on `38` exploratory data-analysis (`A`) tasks, test zero-shot on `20` predictive modeling (`F`) tasks.
  3. **Cross-domain (`Single-Discipline F -> G-test`)**: Evolve on a single discipline's `F` tasks (`Physics`, `Life`, `Earth`, or `Chemistry`), test across all `4` disciplines.

---

## Key Empirical Findings

### 1. Half of Evolved States Regress Overall, and Every Single State Regresses on `>= 8/20` Tasks

| RSI System (`GLM-5.3-Flash`) | Positive Overall $\Delta^*$ States (`of 6`) | Overall $\Delta^*$ Range | Within-Type (`All-F`) $\Delta^*$ (`W/L`) | Cross-Type (`All-A`) $\Delta^*$ (`W/L`) | Avg. Test Input Tokens / Task | Primary Mechanism & Failure Signature |
|:-----------------------------|:--------------------------------------------|:-------------------------|:-----------------------------------------|:----------------------------------------|:------------------------------|:--------------------------------------|
| **`EvoScientist`** | **`6 / 6`** | **`+0.39%` to `+2.24%`** | **`+1.42%`** (`9/11`) | **`+1.13%`** (`9/11`) | Moderate | Distills compact procedural validation habits (e.g., forward-extrapolation splits, independent numerical output checks in **`38/60` vs. `2/60`** initial runs); yet **still loses on `11–12 / 20` tasks** |
| **`InternAgent-1.5`** | **`4 / 6`** | `-0.37%` to **`+2.62%`** | **`+1.05%`** (`11/9`) | `+0.48%` (`10/10`) | **`12.07M–14.81M`** | Heavy multi-agent literature/hypothesis search; `Life-F` state loses `-0.37%` on `Life` while surging **`+9.49%`** on `Physics` (`+2.62%` overall) |
| **`HyperAgents`** | **`2 / 6`** | `-2.48%` to `+1.68%` | **`-1.64%`** (`9/11`) | **`+0.55%`** (`11/9`) | **`0.68M–1.16M`** | Editable meta-code internalizes `All-F`'s **`1-SE` parsimony rule**, dropping `Life` (`0.4993 -> 0.4841`) and stripping weather covariates on `CO2` flux |
| **`SIA-H`** | **`0 / 6`** | **`-3.34%` to `-0.46%`** | **`-3.34%`** (`8/12`) | `-0.46%` (`9/11`) | `2.74M -> 5.28M–10.48M` | Unbounded trajectory-experience accumulation (`2x–3.8x` token bloat) crowds context with source-dataset modeling recipes |

- **Aggregate $\Delta^* > 0$ routinely coexists with majority task losses**: Across all `24` evolved states, **every single state regressed on at least `8/20` (`40%`) held-out tasks**. Most strikingly, `EvoScientist` evolved on `Chemistry-F` posted one of the strongest aggregate gains (**`+2.24%` overall**, driven by **`+7.28%` in `Physics`**, `0.5050 -> 0.5411`) while **regressing on `12/20` (`60%`) of held-out tasks (`W/L = 8/12`)** and barely moving in-domain `Chemistry` (`+0.21%` $\Delta^*$, raw mean `0.5008 -> 0.5001`).

### 2. Why Exploratory Data-Analysis (`A`) Evolution Out-Transfers Modeling (`F`) Evolution on Several Axes

- **`A -> F` reverses `HyperAgents` regression (`-1.64% -> +0.55%`) and lifts `Physics` on `4/4` systems (`+0.42%` to `+5.46%`)**: Evolving on `F` tasks rewards model-family shortcuts that happened to win on `G-evolve` (such as `HyperAgents`' `1-SE` simplicity penalty or `SIA-H`'s algorithm templates), which misfire when target dynamics require nonlinear interactions. In contrast, `A` tasks force agents to inspect distributions, missingness, regime boundaries, and unit consistency *before* fitting—inducing **data-hygiene and output-verification habits** (`EvoScientist` `A-evolved` raised mean score `0.5053 ± 0.0058 -> 0.5090 ± 0.0035`, cutting cross-seed variance by `40%` and writing standalone numerical sanity verifiers in `63.3%` [`38/60`] vs. `3.3%` [`2/60`] of runs).
- **Cross-domain transfer follows structural validation homology, not subject-matter labels**: `Chemistry-F` tasks with extrapolate-by-scaffold/regime splits taught forward-extrapolation validation protocols that transferred strongly to `Physics` (`+7.28%`), whereas source-domain feature/estimator priors hurt heterogeneous `Life` and `Earth` datasets.

---

## Relevance to Praxis

1. **Per-Task Win/Loss Floors Over Aggregate Means (`output/rules/recursive-improvement.md`)**: Directly reinforces `"DON'T: Accept modifications based on aggregate metrics alone"` and `"DO: Pass every self-modification through one acceptance gate"`—a `+2.24%` aggregate scientific RSI gain achieved via `8` large wins and `12` regressions violates non-regression unless changes are scoped by regime invariants rather than baked globally into meta-code (e.g., `1-SE` parsimony).
2. **Diagnostic-First Experience Transfer (`output/specs/self-improving-agent.spec.md`)**: When evolving persistent scientific or analytical harnesses across domains, retain **procedural data-profiling, split-construction, and numerical sanity-check skills** while discarding source-task estimator preferences and unbounded `2x–3.8x` prompt logs (`SIA-H`).
