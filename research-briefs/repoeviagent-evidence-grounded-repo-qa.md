# RepoEviAgent: Scalable Synthesis of Evidence-Grounded Repository-Level Question Answering Tasks

> **Source**: [arXiv:2611.31873](https://arxiv.org/abs/2611.31873) — Aoqi Hu (National University of Singapore), Yueao Xing (Beijing University of Posts and Telecommunications) (2026)
> **Praxis Source ID**: `src:2611-31873v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Why Not a Skill?

`RepoEviAgent` is a **data-synthesis and benchmark-construction pipeline** designed to turn historical GitHub pull requests into executable, rubric-graded repository-level question-answering (`RepoQA`) tasks (`28,467` synthesized instances across `8,477` repositories, plus the `334`-task human-audited `RepoEviQA` benchmark across `168` repositories and `5` languages). Rather than introducing a new inference-time repository-exploration skill beyond [`cost-effective-repo-exploration`](../skills/cost-effective-repo-exploration/SKILL.md) or the halting-calibration training procedure in [`jet-just-enough-exploration-tuning-repo-qa.md`](jet-just-enough-exploration-tuning-repo-qa.md), its transferable engineering contributions lie in **contaminant-free Docker sandbox synthesis**, **strict conjunctive positive/negative checklist grading**, and **diagnostic evidence on where frontier coding agents collapse (`0.0%–12.5%` on concurrency/async across `4/5` models) despite verbose answers**.

---

## Synthesis Pipeline & Grading Integrity Controls

Starting from `~2.48M` merged PRs (`2020-01-01` to `< 2026-01-01`) across `8,477` GitHub repositories (`> 1,000` stars) in `Python`, `Go`, `TypeScript`, `C`, and `C++`:

1. **Structural & Multi-Axis PR Filtering**: Retain PRs touching `50–1,000` functional LOC across `<= 50` files with a non-empty test patch; filter via `DeepSeek V4 Flash` behavioral relevance and `GLM 5.3` `5`-dimension quality scoring (`task value`, `behavior clarity`, `test signal`, `scope complexity`, `interface clarity`).
2. **Host-Verified Container Environment Synthesis**: An `Environment Builder Agent` configures dependencies on language base images and classifies build fidelity as `Full`, `Partial`, or `Failed`. Crucially, a **deterministic host-side audit** verifies before task synthesis that: (a) container setup left **zero modifications to version-controlled files**, (b) `HEAD` matches the exact base commit SHA, and (c) tests reported under `Full` genuinely re-execute cleanly.
3. **Strict All-Must-Have Rubric Grading (`Claude Opus 4.6`)**: A `QnA Synthesis Agent` grounds deep architectural/behavioral questions in verified code + test evidence paired with atomic **must-have positive criteria** $\mathcal{U}_i^{\mathrm{must}}$ and **negative hallucination/misconception traps**. An answer passes **only if every required criterion holds simultaneously**: $\mathrm{Pass}_i = \prod_{u_j \in \mathcal{U}_i^{\mathrm{must}}} \mathbb{I}[J(\hat{a}_i, u_j) = 1]$ (complementing [`certified-task-verifier-harness`](../skills/certified-task-verifier-harness/SKILL.md)).

---

## Key Empirical Findings

### 1. `RepoEviQA` (`334` Tasks, `168` Repos): `51.50 pp` Model Spread and Zero Correlation With Answer Verbosity

*(Note: Table 1 in the manuscript displays 1-decimal rounded overall pass rates while §5.2 reports exact 2-decimal counts out of `334`; both are shown below.)*

| Model (`mini-SWE-agent`) | Overall Pass Rate (`§5.2` Exact / `Table 1` `1`-dec) | Avg. Answer Length (Words) | `API & Lib.` (`avg 63.0%`) / `Familiarization` (`58.2%`) | `Error Handling & Resilience` (`avg 32.3%`) | `Concurrency & Async Patterns` (`avg 15.0%`) | `C++` Pass Rate (`avg 46.5%`) |
|:-------------------------|:----------------------------------------------------|:---------------------------|:---------------------------------------------------------|:--------------------------------------------|:---------------------------------------------|:------------------------------|
| **`GLM-5.3`** | **`76.35%` (`255/334` / `76.3%`)** | `~1,472` | High | **`61.5%`** (`8` tasks) | **`62.5%`** (`5` tasks) | **`86.0%`** |
| **`DeepSeek-V4.1-Flash`** | **`62.87%` (`210/334` / `62.9%`)** | `~2,392` | High | Mid | **`12.5%`** (`1` task) | Mid |
| **`GLM-5.3-Flash`** | **`52.40%` (`52.4%`)** | **`2,553`** (`1.73x` `GLM-5.3`) | Mid | Low-Mid | **`0.0%` (`0` tasks)** | Mid |
| **`GPT-5.5`** | **`51.50%` (`51.5%`)** | Moderate | Mid | **`7.7%` (`1` task)** | **`0.0%` (`0` tasks)** | **`41.9%`** (`-44.1 pp` vs. `GLM-5.3`) |
| **`Gemini-3.8-Flash`** | **`24.85%` (`24.9%`)** | `1,260` | Low | Low | **`0.0%` (`0` tasks)** | Low |

- **Cross-cutting non-local categories trigger sharp capability cliffs**: Category averages drop by `6.9–23.8 pp` moving from localized trace tasks (`API & Library Integration` `63.0%`, `Codebase Familiarization` `58.2%`, `Root Cause Diagnosis` `57.3%`, `Security` `55.2%`) to global invariant tasks: `System Architecture & Design` (`49.0%`), `Data Model & State Management` (`41.7%`), `Error Handling & Resilience` (`32.3%`), and **`Concurrency & Async Patterns` (`15.0%`, where `3/5` frontier/flash models score `0.0%`)**. Language pass rates similarly step down from `TypeScript` (`60.4%`) and `Python` (`55.3%`) to `Go` (`49.1%`), `C++` (`46.5%`), and `C` (`43.0%`).
- **Verbosity does not buy conjunctive rubric coverage**: Average response length spans `1,260–2,553` words with **no monotonic relationship to accuracy**—`GLM-5.3` beats `DeepSeek-V4.1-Flash` by **`+13.48 pp`** using `~920` fewer words and beats `1.73x`-longer `GLM-5.3-Flash` by **`+23.95 pp`**.

### 2. Trajectory Distillation on Synthesized `RepoEviAgent` Tasks (`SWE-Atlas-QnA` Table 2)

Fine-tuning open-weight models via SFT on trajectories collected over the `28,467` synthesized `RepoEviAgent` tasks produced large out-of-benchmark gains on the external `60`-task `SWE-Atlas-QnA` evaluation split (compared alongside `124`-task Panel A references `Claude Opus 4.7` `36.02%`, `GPT-5.4` `36.30%`, `GLM-5` `20.50%`, `Kimi K2.5` `13.10%`):

- **`Qwen3.5-27B`**: Pass rate jumped **`18.3% -> 53.3%` (`+35.0 pp`)**, mean rubric score **`0.666 -> 0.928`**.
- **`Qwen3.6-35B-A3B`**: Pass rate jumped **`20.0% -> 38.3%` (`+18.3 pp`)**, mean rubric score **`0.690 -> 0.845`**.

---

## Relevance to Praxis

1. **Sandbox Non-Modification & Conjunctive Rubric Gates (`output/rules/agent-evaluation-quality.md`, `output/specs/adk-eval-quality-gate.spec.md`)**: Reinforces `"DO: Certify benchmark tasks with reference-pass and empty-fail preflights, lock the verifier's evidence view, and fingerprint baseline bytes before reusing grading sandboxes"` and `"DO: Decompose evaluations into atomic checklist items"`—automated environment builders must be deterministically checked for clean `git` working trees + exact base SHA + genuinely re-executing tests before synthesis, and `RepoQA` graders must require **conjunctive (`AND`) satisfaction of all must-have positive/negative items** so `2,553`-word shotgun answers cannot compensate for missing an error-handling or concurrency invariant.
2. **Complementary Training Signal With `JET` (`arXiv:2611.22539`)**: `RepoEviAgent` scales diverse multi-language `RepoQA` task/rubric environments (`+18.3` to `+35.0 pp` SFT lift), while [`jet-just-enough-exploration-tuning-repo-qa.md`](jet-just-enough-exploration-tuning-repo-qa.md) prevents those SFT trajectories from teaching step-limit over-exploration via forced-answer sufficiency truncation ($\lambda = 5$).
