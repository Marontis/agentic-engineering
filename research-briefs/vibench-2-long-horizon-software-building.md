# ViBench 2.0: A Benchmark for Long-Horizon Software Building

> **Paper**: [ViBench 2.0: A Benchmark for Long-Horizon Software Building](https://arxiv.org/abs/2611.05620) (Furman, Kirani, Sheikh, Li, Zhong & Catasta, Replit, 2026)
> **Praxis source**: `src:2611-05620v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Classification: Research Brief (Long-Horizon Greenfield SWE Benchmark & Browser-Agent Grader Protocol)

`ViBench 2.0` (`arXiv:2611.05620`) evaluates whether coding agents can build complete, full-stack web applications (`PostgreSQL 17` + `Python 3.12` / `Node.js 22` in `4-CPU, 8 GB` `Harbor` containers) from an empty greenfield project over a long sequence of **9 to 18 dependent feature requests** (`241` total stages across `17` products: `8` public modeled on `Amazon`, `Asana`, `Discord`, `Figma`, `GitHub`, `Google Docs`, `Jira`, and `Uber` with `104` stages and `252` test plans; `9` held-out with `137` stages and `292` test plans) in a single continuous conversation (`>200k` tokens, `55–63M` cached input tokens and `0.36–0.39M` output tokens per frontier build), graded **only after the final stage completes** by an autonomous browser-using agent (`Opus 5.5` at medium effort via `Playwright` / Chromium) across **544 end-to-end user test plans** (`463` [`85%`] exercising multiple features together, `64` single-feature, `17` sign-in flows). A build scores `pass@1 = 1` **only if every single test plan for that product passes (`26 to 41` plans per product)**.

---

## Problem & Motivation

Single-task and short-horizon "vibe coding" benchmarks saturate rapidly:
- Over **40%** of AI benchmarks less than two years old have already saturated (`Akhtar et al., 2026`).
- On `ViBench 1.0`'s `Vibe-on-Vibe` tasks (`15` MVPs + `45` single-feature extensions, `152` plans), rerunning current frontier models reaches **88.9%** (`GPT-6.1 Sol`), **82.2%** (`GPT-6 Astra`), and **82.2%** (`Opus 5.5`) `pass@1`, compared to **51.1%** (`Opus 4.6`) at `ViBench 1.0`'s release (`Table 7`).
- On `Vibe Code Bench`, top scores rose from `61.8%` in March 2026 to `>90%` for six models by late October 2026; `Vibe Code Bench 1-100` (`Tran et al., 2026b`) grows apps over up to `10` requests (`34.0%` top score) but starts from a finished reference app and stops at the first failure.

Real users on agentic engineering platforms (`Replit`) start greenfield, issue successive business-level feature requests without reading code or supplying intermediate unit tests, and judge only whether the finished product works as a whole through its UI.

---

## Architecture: Task Formulation & Validated All-or-Nothing Browser Grading

### 1. Greenfield Multi-Stage Building Protocol
- **Business-Only PRDs Ordered by Dependency Graph**: Each stage supplies a business-facing Product Requirements Document (`PRD`) specifying user flows, roles, business rules, and observable states—omitting schemas, APIs, and library choices. Features are ordered topologically along a feature dependency graph (`Figure 2`), entering the container one stage at a time (`up to 300 agent steps` and `2 hours` per stage).
- **Minimal Standardized Harness & Context Compaction**: All `9` evaluated models run in the same stock `OpenHands Software Agent SDK` harness on `Harbor` (terminal, file editor—`apply-patch` for `GPT` models, `string-replace` for others—and task list; `temperature = 1.0`, medium reasoning effort). Whenever conversation history exceeds **200k tokens**, the builder's own model summarizes the older conversation (`compaction` fired in `100%` of `Sol` and `Astra` reference builds and `67 of 68` `Opus 5.5` builds).
- **Five Implicit System-Prompt Invariants**: Every builder is instructed that (1) the app starts on an empty database, (2) nothing the user saves is lost, (3) nothing shows as saved if it was not saved, (4) one click does one thing, and (5) a refused action shows a message.

### 2. Asymmetric Majority-of-5 Browser Grader Protocol (`Section 2.3`, `Appendices C & D`)
Under an all-or-nothing `pass@1` metric across `26–41` plans per product, a single **wrong fail** ruins a working build, whereas a **wrong pass** is not re-tested. `ViBench 2.0` controls both error types:
- **Clean-Container Seeding**: Every grade boots a fresh container with an empty `PostgreSQL 17` database from the final code. For the `37%` of public plans requiring starting data (`93 of 252`: `32` creating records, `61` setting config), an `Opus 5.5` seeding agent inspects the finished app and writes a setup script.
- **Evidence-Quoted Browser Execution**: The `Opus 5.5` grader interacts exclusively through Chromium (`Playwright` DOM actions or coordinate clicks/drags, separate browser sessions for multi-user concurrency tests such as `Discord` live chat or `Jira` concurrent board moves), keeping full screenshots and accessibility snapshots of the `2` newest steps (replacing older images `8` at a time with file notes). Every step check must quote on-screen browser evidence; grades lacking evidence or violating grader rules are discarded and repeated (`only ~30 of 19,584 plans [0.2%]` failed to finish after retries and were excluded as `no grade`).
- **Pass-Once, Re-Grade-Fails-Up-to-5 (3-of-5 Agreement)**: A plan that passes its first grade stands; a plan that fails is re-graded up to `4` more times until `3` verdicts agree.
- **Validation Metrics (`Table 3` & `Table 4`)**:
  - *Grader selection (`640` grades per candidate on `Uber`)*: `Opus 5.5` (medium effort) had the lowest single-grade wrong-fail rate at **1.9%** (`12/640`), beating `GPT-6.1 Sol` low (`3.8%`, `24/640`), `Opus 5.5` low (`4.1%`, `26/640`), and `Sol` medium (`4.5%`, `29/640`); on `2,176` earlier plans, `Opus` made `17` wrong verdicts (`0.8%`) vs `171` (`7.9%`) for `Sol` low.
  - *Consistency & Wrong Fails*: **99.0%** of `97` plans received the identical verdict across `10 of 10` repeated grades. Across `1,521` single grades on working plans, single-grade wrong fails occurred only **3 times (0.20%, 95% CI 0.07–0.58%)**, which the `3-of-5` majority rule eliminates.
  - *Cross-Provider Wrong-Pass Audit*: Re-grading `477` `Opus`-passed plans with `GPT-6.1 Sol` and adjudicating all `20` disagreements by hand found only **4 false passes (0.8%, 95% CI 0.3–2.1%)**, while `Sol` was wrong in `16 of 20` disagreements.
  - *Same-Family Bias Check*: `Opus 5.5` had `4/237` wrong passes on Claude-built apps vs `0/240` on GPT-built apps (`95% CI -0.2 to 4.3 pp`, within chance).
  - *Planted Bug Sensitivity (`Table 4`)*: Across **34 planted bugs** (`24` subtle—`Cent off` [`0/15` passed], `Reverts on reload` [`0/15`], `Dropped value` [`0/15`], `No refusal message` [`0/14`], `Timing 45s early` [`0/10`]—plus `10` obvious [`0/27`]), the grader caught **100% of visible bugs (`0 of 96 grades passed`, 95% CI 0–3.9%)** while wrongly failing `0 of 24` unbugged control grades.
  - *Pre-Release Failure Audit*: Auditing all `178` failed plans of `Sol`, `Astra`, and `Opus` across `12` reference rounds uncovered `13` wrong verdicts (`10` grader errors, `2` test defects, `1` harness fault) and `2` underspecified PRD points (`6` failures), all fixed before release; the remaining **159 of 165** (`96.4%`) were genuine application bugs. Review passes edited `117 of 571` draft plans and dropped `27`, leaving `544`.

---

## Key Empirical Results

### 1. Independent Evaluation Across All 17 Products (`612` Total Builds, `4` Builds/Product/Model, `Table 1` & `Table 6`)

| Model | All 17 `pass@1` (%) | All 17 `Plan Pass` (%) | Public 8 `pass@1` / `Plan Pass` (%) | Held-out 9 `pass@1` / `Plan Pass` (%) | Build Time (min) | Builder Cost / Build (USD) |
|:------|--------------------:|-----------------------:|------------------------------------:|--------------------------------------:|-----------------:|---------------------------:|
| `GPT-6.1 Sol` | **64.7 ± 9.3** | 96.9 ± 1.2 | **53.1 ± 12.4** / 94.9 ± 2.5 | **75.0** / **98.7** | 178 | \$12.3 |
| `GPT-6 Astra` | 60.3 ± 10.4 | **98.0 ± 0.6** | **53.1 ± 14.4** / **97.2 ± 1.1** | 66.7 / **98.7** | 198 | \$89.9 |
| `Opus 5.5` | 48.5 ± 10.9 | 93.7 ± 4.2 | 37.5 ± 14.9 / 91.6 ± 6.6 | 58.3 / 95.7 | **73** | \$23.1 |
| `Sonnet 5.5` | 19.1 ± 9.8 | 79.2 ± 7.3 | 12.5 (3.5–29.0) / 78.7 ± 9.8 | 25.0 / 79.6 | **26** | \$4.4 |
| `Grok 4.7` | 1.5 (0–7.9) | 52.9 ± 8.9 | 3.1 (0.1–16.2) / 41.1 ± 13.7 | 0.0 / 63.3 | 118 | \$63.9 |
| `DeepSeek V4.1 Flash` *(open)* | 0.0 (0–5.3) | 77.4 ± 3.2 | 0.0 (0–10.9) / 72.1 ± 5.9 | 0.0 / 82.2 | 221 | **\$2.5** |
| `GLM 5.3` *(open)* | 0.0 (0–5.3) | 66.0 ± 4.9 | 0.0 (0–10.9) / 63.4 ± 6.8 | 0.0 / 68.4 | 231 | \$27.8 |
| `Kimi K3` *(open)* | 0.0 (0–5.3) | 56.7 ± 8.1 | 0.0 (0–10.9) / 53.8 ± 12.7 | 0.0 / 59.4 | 221 | \$33.1 |
| `Gemini 3.8 Flash` | 0.0 (0–5.3) | 38.1 ± 5.6 | 0.0 (0–10.9) / 28.2 ± 7.7 | 0.0 / 46.9 | 249 | \$27.0 |

- **The Reliability Gap (`Plan Pass` vs `pass@1`)**: The top three models pass **93.7% to 98.0%** of individual test plans, yet deliver a fully working product in only **48.5% to 64.7%** of builds. Of their **84 failed builds** that completed seeding, **42 (50.0%) fail on exactly 1 test plan** and **62 (73.8%) fail on at most 2 plans**. Only the `Figma`-modeled product defeated all `36` independent builds across `Sol`, `Astra`, and `Opus` (primarily on concurrent-editing and undo plans).
- **Open-Weight Models**: None of the three open-weight models (`DeepSeek V4.1 Flash`, `GLM 5.3`, `Kimi K3`) achieved a single fully passing build across `204` attempts (`0.0% pass@1`), though `DeepSeek V4.1 Flash` reached **77.4% plan pass rate** (within `1.8 pp` of `Sonnet 5.5` at `$2.5` vs `$4.4` per build).
- **Breadth Over Feature-Interaction Failure**: For `Opus 5.5`, multi-feature plans failed at almost the exact same rate as single-feature plans (**6.4% vs 6.2%**); the `74%` share of failed top-model builds that missed only multi-feature plans simply reflects the `85%` base rate of multi-feature plans.
- **Clean-Database Deployment Bugs**: Only `2 of 204` top-model builds failed every plan (both `Opus 5.5` failing seeding). In reference runs, **100% of builds that failed to start on an empty PostgreSQL database** had schema initialization code that referenced a SQL table or column before the `CREATE TABLE` statement; moving **1 to 4 SQL statements** made every broken application start (`Section 4.3`, `Appendix D`).

### 2. Longitudinal Scaling Across GPT Generations on the Public 8 Subset (`Table 2`)
| Model Release | Public 8 `pass@1` (%) | Public 8 `Plan Pass` (%) | Build Time (min) | Cost / Build (USD) |
|:--------------|----------------------:|-------------------------:|-----------------:|-------------------:|
| `GPT-6.1 Sol` | **53.1** | **94.9** | 170 | \$11.8 |
| `GPT-6.1 Terra` | 46.9 | 94.5 | 122 | \$6.2 |
| `GPT-6 Sol` | 31.2 | 84.0 | 88 | \$19.4 |
| `GPT-5.6 Sol` | 3.1 | 67.5 | 73 | \$26.5 |
| `GPT-6 Luna` | 0.0 | 59.8 | 188 | \$1.7 |
| `GPT-5.5` | 0.0 | 51.5 | 46 | \$30.1 |
| `GPT-5.4` | 0.0 | 41.5 | 78 | \$22.9 |
| `GPT-5.6 Terra` | 0.0 | 26.1 | 39 | \$5.3 |
| `GPT-5.6 Luna` | 0.0 | 6.6 | 35 | \$0.5 |

- **`Plan Pass` Moves First; `pass@1` Inflects Above ~70%**: Across generations (`GPT-5.4` $\to$ `GPT-6.1 Sol`), `Plan Pass` climbs steadily (`41.5%` $\to$ `51.5%` $\to$ `67.5%` $\to$ `84.0%` $\to$ `94.9%`), whereas `pass@1` stays `0.0%–3.1%` until `Plan Pass` crosses **~70%**, then jumps to **31.2%** (`GPT-6 Sol`) and **53.1%** (`GPT-6.1 Sol`) while build cost drops by more than half (`$26.5–$30.1` $\to$ `$11.8`).

---

## Why Not a Skill?

`ViBench 2.0` is an evaluation benchmark and production deployment case study from Replit rather than a standalone agent skill. Its actionable engineering lessons—(1) pairing `Plan Pass` (for early-stage/fast-tier routing) with all-or-nothing `pass@1` (for core-loop model selection), (2) asymmetric `pass-once / re-grade-fails-up-to-5` browser grading with dual error measurement, and (3) mandatory clean-container/empty-DB startup verification—are codified directly in `rules/agent-evaluation-quality.md`.

---

## Connections to Praxis

- **Evaluation Quality (`rules/agent-evaluation-quality.md`)**: Establishes the `70%` component-level pass threshold where end-to-end product `pass@1` inflects, the asymmetric `3-of-5` re-grading rule for failing checks (`0.20%` single-grade wrong-fail rate vs `0.8%` wrong-pass rate), and clean-DB deployment verification.
- **Context Compaction (`rules/skill-system-design.md`)**: Confirms that over `200k+`-token multi-stage builds (`55–63M` input tokens), context compaction survival determines whether late stages preserve early requirements.
- **Multi-Step SWE (`research-briefs/multi-step-swe-long-horizon-self-building.md`)**: Complements `ViBench 2.0`'s end-of-build UI evaluation with per-step conformance-suite verification across `69` systems/library/migration tasks (`arXiv:2611.07166`).
