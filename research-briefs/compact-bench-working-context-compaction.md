# CompAct-Bench: A Benchmark for Working-Context Compaction in Long-Horizon Agent Tasks

> **Source**: [arXiv:2611.25673](https://arxiv.org/abs/2611.25673) — Jiayi Chen, Lizhe Chen, Yujia Chen, Shihan Dou, Ming Zhang, Chendi Ge, Shiguang Ni, Tao Gui, Qi Zhang, Xuanjing Huang & Maxm Pan (Fudan University, Tsinghua University & Tencent, November 2026)
> **Praxis Source ID**: `src:2611-25673v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

Evaluating `CompAct-Bench` (`arXiv:2611.25673`) against [`skill-design-methodology`](../skills/skill-design-methodology/SKILL.md) shows it is a **diagnostic benchmark and failure-pathway study** rather than a new standalone `SKILL.md`:

1. **Evaluates Generic Summarization Prompts Across `12` Frontier Models Without Proposing a New Compactor**: Every evaluated model uses the same controlled `Iterative Ratio Calibration` (`IRC`) benchmark harness at `r = 10%` character retention (`[0.097, 0.103]`) to isolate *model compaction capability* rather than introducing an algorithmic compaction runtime (whereas reusable trimming/assembly procedures already live in [`protocol-preserving-context-trimming`](../skills/protocol-preserving-context-trimming/SKILL.md), [`prefix-preserving-context-assembly`](../skills/prefix-preserving-context-assembly/SKILL.md), and [`witnessed-request-compaction-gate`](../skills/witnessed-request-compaction-gate/SKILL.md)).
2. **Actionable Scheduling & Epistemic-Schema Rules**: Its highest-value engineering discoveries—(i) **opposite compaction-timing curves** between environment-backed `Coding` (`64.0% -> 86.1%`) and context-resident `Search` (`52.9% -> 34.6%`), (ii) **`+33.9` pp survival jump** once coding edits materialize on disk (`86.9%` vs. `53.0%`), and (iii) **Epistemic State Distortion (`Premature Commitment`)** causing failure even when `12/12` compactors preserve the exact underlying fact—translate directly into context-management design rules (`rules/skill-system-design.md`).

---

## Executive Summary

Long-horizon agents routinely compact their working history $H_b$ into a summary $M_b$ once context budgets fill, yet existing evaluations confound compaction quality with base-agent task difficulty, uncontrolled summary lengths, or extra post-compaction retry turns. `CompAct-Bench` isolates single-boundary working-context compaction across **`200` `pass^3`-verified trajectories** ($\ge 8$ interaction rounds, `100%` `3/3` pre-compaction pass rate under `Claude Opus 5`) spanning **`BrowseComp` (`79` web-search tasks)**, **`SWE-bench` (`96` repository coding tasks)**, and **`CompanyBench` (`25` multi-app enterprise workspace tasks)**. At execution progress boundaries `25%`, `50%`, and `75%`, each of **`12` frontier models** compacts the identical prefix $H_b$ to exact `r = 10%` character retention (`[0.097, 0.103]`) via `IRC`, and a fixed reference executor (`Claude Opus 5`, `Avg@3` rollouts) continues from the exact reconstructed environment state under the **matched remaining action budget $T - b$**.

Even though the base agent solves `100%` of these tasks `3/3` times without compaction, **post-compaction `12`-model mean strict accuracy plunges by `43.3` percentage points to `56.7%` (`46.0%–68.5%`)**—proving that `10%` generative compaction is severely lossy across every current frontier family and fails through two distinct mechanisms: **Information Omission** (triggering `+13.8` to `+18.2` pp wasted repeated work) and **Epistemic State Distortion** (turning open hypotheses into settled conclusions or vice versa, driving `56.7%` of early wrong terminations).

---

## Key Quantitative Findings

### 1. Frontier Compactor Ranking, Domain Dissociation & Length-Control Collapse (`Tables 2, 9–10, 12, 18`)

| Compactor Model (`r = 10%` Target) | Overall `Avg@3` (`200` Tasks) | `BrowseComp` Search (`79`) | `SWE-bench` Coding (`96`) | `CompanyBench` Workspace (`25`) |
|:-----------------------------------|:------------------------------|:---------------------------|:--------------------------|:--------------------------------|
| *(Uncompacted `pass^3` Screening Baseline)* | *`100.0%`* | *`100.0%`* | *`100.0%`* | *`100.0%`* |
| **`Claude Opus 5`** | **`68.5%`** | **`62.0%`** | **`81.2%`** | `40.0%` |
| **`Gemini 3.8 Flash`** | **`65.5%`** | `57.0%` | `75.0%` | **`56.0%`** |
| **`Kimi K3`** | `62.0%` | `54.4%` | `72.9%` | `44.0%` |
| **`GPT-5.6-Sol`** | `59.5%` | `48.1%` | `72.9%` | `44.0%` |
| **`12`-Model Mean (`Min–Max` to `Doubao Seed 2.1 Pro`)** | **`56.7%`** (`46.0%–68.5%`) | **`43.4%`** | **`74.3%`** | **`31.0%`** |

- **Weak Coding–Workspace Rank Correlation**: Cross-domain Spearman rank correlation is moderate between `Search` and `Coding` ($\rho = 0.62$) and `Search` and `Workspace` ($\rho = 0.53$), **but drops to $\rho = 0.26$ between `Coding` and `Workspace`** (`Claude Opus 5` leads `Coding` at `81.2%` yet trails `Gemini 3.8 Flash` by `-16.0` pp on `Workspace`). Within each domain, raw prefix character length is uncorrelated with post-compaction accuracy ($|\rho| \le 0.03$, `Table 18`).
- **`IRC` Ratio Adherence & Mild-Compression Breakdown (`Tables 9–10`)**: At `r = 10%`, `IRC` keeps `86.7%` of `2,400` compactions inside `[0.097, 0.103]` with median ratio `0.0986` *(transparent manuscript discrepancy note: prose in `Section 2.4` reports `86.7%` across all `2,400` compactions, whereas `Table 9`'s `"All"` summary row prints `86.0%`)*. While `IRC` holds `65%–99%` adherence at `r = 5%–20%`, **adherence collapses at `r = 40%–80%` (`18%–44%` at `r = 80%`, `Table 10`)** because LLMs have an intrinsic summarization compression ceiling—compressing `272K`-character `Workspace` histories down to `0.12–0.14` regardless of prompt instructions to retain `80%`.

### 2. Opposite Compaction-Timing Curves: Context-Resident vs. Environment-Backed State (`Tables 13–14, App. F`)

Evaluating identical tasks compacted at `25%`, `50%`, and `75%` of trajectory length reveals **opposite monotonic trends** across task families:

| Task Domain | `25%` Boundary | `50%` Boundary | `75%` Boundary | `Without H_b` (`0%` History + `0%` Summary, Env State Only) | Marginal Lift of Summary $M_b$ Over `Without H_b` |
|:------------|:---------------|:---------------|:---------------|:------------------------------------------------------------|:--------------------------------------------------|
| **`BrowseComp` (Search — Zero Env State)** | **`52.9%`** | `42.6%` | **`34.6%`** *(declines in `11/12`, monotonic `9/12`)* | `26.9%` / `15.4%` / `7.4%` | **`+26.0` / `+27.2` / `+27.2` pp** |
| **`SWE-bench` (Coding — Mutable Repo Disk)** | **`64.0%`** | `72.7%` | **`86.1%`** *(peaks at `75%` in `12/12`, monotonic `10/12`)* | **`66.7%` / `58.1%` / `71.9%`** *(vs. `48.5% / 35.5% / 15.6%` unedited initial state)* | `-2.7` / `+14.6` / `+14.2` pp |
| **`CompanyBench` (Workspace)** | *Peaks at `50%` in `9/12` models* | — | — | — | — |

- **Materialized Repository Edits Carry `Coding` State (`p = 3 \times 10^{-8}`)**: In `SWE-bench`, once an agent modifies repository files before the compaction boundary, post-compaction accuracy jumps **`+33.9` pp (`86.9%` with pre-boundary repo edit vs. `53.0%` without edit, $p = 3 \times 10^{-8}$, $\rho = 0.62$)**; conditioned on an edit existing, prior test runs add nothing (`86.5%` with test run vs. `87.2%` without). Even stripping *both* $H_b$ and $M_b$ (`Without H_b`) at `75%` progress solves **`71.9%`** of `Coding` tasks purely by inspecting `git diff`/modified files (`+56.3` pp above `15.6%` from the unedited repo under the tight remaining budget). Conversely, `Search` modifies zero external state, so late compaction (`75%`) destroys accumulated negative exclusions while leaving only `25%` of the step budget to re-discover them.

### 3. Two Behavioral Failure Pathways: Omission vs. Epistemic State Distortion (`Tables 16–17, Case F`)

Across failed continuations, **action-budget exhaustion** dominates (`91.6%` `Search`, `92.0%` `Coding`, `97.7%` `Workspace`), while **early wrong termination** concentrates at the `25%` boundary (`20.8%` `Search`, `14.8%` `Coding`). Auditing `6` compaction error classes (`92.5%` of early failures and `85.8%` of budget exhaustions exhibit $\ge 1$ error) separates two causal pathways:

1. **Information Omission $\to$ Repeated Completed Work**: `Constraint Omission (CO)` (`47.8%` early / `48.8%` budget exhaustion), `Local Reference Loss (LR)` (`0.0%` / `3.6%`), and `Progress/State Loss (PSL)` (`55.2%` / `44.6%`) cause the continuation agent to **re-execute searches, file reads, and edits already completed before the boundary** (`CO` **`+18.2` pp**, `LR` **`+14.2` pp**, `PSL` **`+13.8` pp** shift toward repeated work; `95.1%` attempt recovery), burning through the remaining $T - b$ step budget.
2. **Epistemic State Distortion $\to$ Unverified Commitment or Re-Verification Paralysis**: `Premature Commitment (PC)` (turning tentative hypotheses into settled facts, **`56.7%` of early failures vs. `46.0%` of budget exhaustions**), `Factual Distortion (FD)` (`40.3%` vs. `35.2%`), and `Candidate/Goal Drift (CGD)` (`25.4%` vs. `24.3%`) increase **immediate unverified commitment** (`CGD` **`+10.5` pp**, `FD` **`+7.3` pp**, `PC` **`+5.2` pp**). In `Case F` (`BrowseComp`), **all `12/12` compactors preserved the exact factual observation** (*"paper has 8 authors, prompt requires 7"*), yet the `4` compactors that explicitly marked that candidate **ruled out / settled** achieved **`4/4` (`100%`) continuation success in `4–6` rounds**, whereas the `8` compactors that left its exclusion status **open/ambiguous** caused **`5/8` runs to re-verify the candidate and exhaust all `39` remaining actions**.

---

## Actionable Takeaways

1. **Delay compaction in `Coding` until working hypotheses materialize as file edits (`86.9%` vs. `53.0%`), and externalize `Search` exclusions to structured files before compacting**: Never rely on prose summarization alone to carry multi-hop negative search exclusions past the `50%–75%` horizon (`52.9% -> 34.6%`).
2. **Mandate explicit four-bucket epistemic status tags in compaction prompts**: Separate `(a) Active User Constraints`, `(b) Verified Facts & Materialized Edits`, `(c) Ruled-Out Candidates (Settled — Do Not Re-Query)`, and `(d) Unverified Open Hypotheses` so continuations neither commit prematurely (`56.7%` of early failures) nor re-audit settled exclusions (`Case F`).
3. **Use deterministic message/span trimming rather than generative LLM summarization when targeting `40%–80%` retention**: Generative compactors plateau around `12%–14%` output ratios on `272K`-char workspace logs regardless of prompt instructions (`18%–44%` adherence at `r = 80%`); use [`protocol-preserving-context-trimming`](../skills/protocol-preserving-context-trimming/SKILL.md) for moderate budget reductions.

## Related Artifacts

- [`protocol-preserving-context-trimming`](../skills/protocol-preserving-context-trimming/SKILL.md) — Complexity-adaptive deterministic protocol trimming (`arXiv:2609.16461`)
- [`witnessed-request-compaction-gate`](../skills/witnessed-request-compaction-gate/SKILL.md) — Cryptographic authorization separation across context compaction (`arXiv:2611.32194`)
- [`arcbench-rule-compliance-context-compaction.md`](arcbench-rule-compliance-context-compaction.md) — Pinned rule ledgers preventing constraint forgetting across compaction (`arXiv:2611.03223`)
- [`context-compaction-for-world-models.md`](context-compaction-for-world-models.md) — Lazy `compact when full` scheduling vs. per-step compaction (`arXiv:2610.38980`)
- [`rules/skill-system-design.md`](../rules/skill-system-design.md) — Context management, epistemic status preservation, and protocol trimming guardrails
