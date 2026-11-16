# AutoRL: A Multi-Agent System towards Autonomous Reinforcement Learning

> **Source**: [arXiv:2611.17790](https://arxiv.org/abs/2611.17790) — Simon Tang, Wenjie Shi, Yongjing Yin, Keheng Wang, Jialin Liu, Zheng Zhang, Linvo Lin, Xiangyuan Xue, Kan Ren, Jingang Wang, Xunliang Cai (Meituan, CUHK, ShanghaiTech University, Fudan University, 2026)
> **Praxis Source ID**: `src:2611-17790v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

`AutoRL` is an end-to-end 8-agent supervisory system (`1 Orchestrator` + `4 RL Perceptors` + `3 RL Proposers`) tailored specifically to **in-flight distributed reinforcement learning post-training** (`GRPO` and `Dr. GRPO` over `Megatron-LM` + `vLLM` across `8–224` `H800` GPUs). Its concrete perceptors, tools, and execution hooks inspect RL-specific optimization state—policy-ratio clipping bounds (`[0.8, 1.2]`–`[0.8, 1.28]`), log-ratio spike guards (`[-13, 5] -> [-5, 3]`), KL/entropy coefficients, group-normalized rollout advantages, MoE `FP32` unpermutation accumulation, and `TRAIN` answer-equivalence graders—while general council-plus-deterministic-controller experimentation is already covered by [`autonomous-research-to-launch-harness`](../skills/autonomous-research-to-launch-harness/SKILL.md) and [`evidence-gated-adversarial-deliberation`](../skills/evidence-gated-adversarial-deliberation/SKILL.md). Equally important, `AutoRL` is a primary empirical capability-boundary study for recursive self-improvement (`0/3` learning-rule redesigns deployed out of `131` candidates). Consistent with [`infrarsi-training-infrastructure-rsi`](./infrarsi-training-infrastructure-rsi.md) and [`coevo-policy-aware-context-evolution`](./coevo-policy-aware-context-evolution.md), we catalog `AutoRL` as a Research Brief and distill its generalizable supervision rules into [`recursive-improvement.md`](../rules/recursive-improvement.md).

---

## Core Architecture: Process-Level RL Supervision ($a_k = \mathcal{F}(E_k, H_k)$)

Unlike episodic outer-loop research agents that wait for a full training run to finish before launching a new experiment, `AutoRL` separates continuous monitoring from slower causal investigation inside an **ongoing** RL run:

1. **Four Specialized `Perceptors` & Synchronous Observation Barrier**:
   - `Train Perceptor`: Monitors loss, gradient norms, policy entropy, KL divergence, policy ratios, clipping fractions, and verified `NaN`/`Inf` checks.
   - `Rollout Perceptor`: Inspects `TRAIN` responses, rewards, truncation rates, group statistics, and training-grader behavior.
   - `Eval Perceptor`: Tracks aggregate scores and sanitized failure reports under a **strictly fixed evaluation protocol**.
   - `Efficiency Perceptor`: Tracks step throughput, elapsed wall-clock time, job status, and runtime logs (separating normal rollout waiting from stalled workers).
   - Each `Perceptor` executes one bounded tool-assisted window summary (`count`, `mean`, `std`, `slope`, `z-score`) tied to run/step `(r, s)` and source hashes. A **synchronous barrier** freezes triggered signals into an initial evidence batch $E_k^0$; quiet cycles leave training uninterrupted without waking `Proposers`.
2. **Three Complementary `Proposers` (`<= 5` Rounds, CPU-Only Checks & Borda Selection)**:
   - Starting independently from the same frozen $E_k^0$ and shared history $H_k$, the **`Tuner`** proposes local hyperparameter/numerical adjustments, the **`Innovator`** proposes alternative mechanisms, and the **`Reviewer`** audits code paths, counterexamples, and prior interventions.
   - Across up to `5` rounds (`generate -> critique -> revise/merge/withdraw -> Round 4 Borda ranking -> Round 5 vote`), `Proposers` execute **CPU-only verification checks** (`PASS`, `FAIL`, `INCONCLUSIVE`) on isolated source copies and replayed `TRAIN` trajectories before touching GPUs. In `Discussion 43` (`GLM-5.2` `Qwen3-4B`), a reward hook removing truncation penalties accidentally bypassed a `0.7` repetition penalty on helper lookup failure (returning `1.0` instead of `0.3` on `2/4` synthetic CPU fixtures, `Table 6`); `Reviewer` + `Tuner` repaired the fallback before step `154` activation.
   - Round 4 **Borda scoring** ($m$ down to $1$ points across $m$ surviving candidates, ties broken by candidate ID) advances at most `2` finalists; Round 5 requires a `3:0` or `2:1` vote (`3` confirmation votes for a sole finalist, or early exit on unanimous explicit endorsement; failed checks or unresolved blockers prevent publication, though in `Discussions 31` and `43` missing publication metadata prompted direct `Orchestrator` review).
3. **`Orchestrator` & `HOT` vs. `COLD` Lineage-Aware Execution**:
   - Actions take the form $a_k \in \{\mathrm{NONE}, \mathrm{HOT}(\delta_k), \mathrm{COLD}(\delta_k, b_k)\}$ over pre-intervention state $x_k^- = (\theta_k^-, z_k^-, c_k^-)$:
     - **`HOT(\delta_k)`** $\to (\theta_k^-, z_k^-, c_k^- \oplus \delta_k)$: Applies supported online-control overrides (KL, entropy, advantage settings, policy-loss object, `TRAIN` grader hooks, save-and-stop) at a training-step boundary, preserving live weights $\theta_k^-$ and optimizer/rollout state $z_k^-$. Setting a field to `None` restores its launch-time value, so overrides must explicitly carry forward active settings; readiness checks reject `HOT` patches modifying files outside the online-control file, and runtime receipts confirm consumption.
     - **`COLD(\delta_k, b_k)`** $\to (\theta_{b_k}, z_{b_k}, c_k^- \oplus \delta_k)$: Coordinates `save-and-stop` (or recovers from an existing complete checkpoint $b_k$ after a crash), grants the code lock, runs regression checks, and resumes from $b_k$. Parent-checkpoint lineage scopes subsequent `Perceptor` active history strictly through $b_k$ while preserving abandoned branches as research history.

---

## Key Empirical Results

### 1. Cross-Benchmark Generalization (`Qwen3-1.7B` & `Qwen3-4B`, `Tables 1–2`)

Trained on `17,390` `DAPO-Math-17K` problems (`128` prompts $\times$ `8` responses, `LR = 1e-6`, `8,192` gen tokens, `8×H800` GPUs; `gpt-6.1-sol` supervisor vs static `GRPO` and native `Codex` `General Agent` with `gpt-6.1-sol`; `4` evaluation samples/question):

| Model & Method | `AIME 24` | `AIME 25` | `HMMT 25` | `Beyond AIME` | `IMO-AnswerBench` | `MMLU-Pro` | `GPQA-Diamond` | `MBPP` | `LCB v6 Hard` |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **`Qwen3-1.7B` Baseline** | `15.00%` | `13.33%` | `5.00%` | `4.50%` | `10.25%` | `38.85%` | `28.79%` | `33.20%` | `1.57%` |
| `Qwen3-1.7B` `GRPO` (Static) | `26.67%` | `21.67%` | `18.33%` | `11.00%` | `8.63%` | `34.05%` | `22.60%` | `10.95%` | `1.50%` |
| `Qwen3-1.7B` `General Agent` | **`31.67%`** | `18.33%` | `11.67%` | `12.00%` | **`15.00%`** | `25.55%` | `32.20%` | `32.00%` | `1.07%` |
| **`Qwen3-1.7B` `AutoRL`** | `30.00%` | **`30.00%`** | **`18.33%`** | **`12.50%`** | `14.63%` | **`44.88%`** | **`34.34%`** | **`40.05%`** | **`2.00%`** |
| **`Qwen3-4B` Baseline** | `25.00%` | `23.33%` | `11.67%` | `10.5%` | `18.44%` | `55.88%` | `43.43%` | `62.55%` | `4.93%` |
| `Qwen3-4B` `GRPO` (Static) | `46.67%` | `45.00%` | `20.00%` | `26.00%` | `27.00%` | `57.93%` | `44.70%` | `63.55%` | `5.71%` |
| `Qwen3-4B` `General Agent` | `50.00%` | `43.33%` | `26.67%` | `25.00%` | `16.06%` | `37.73%` | `45.33%` | `31.80%` | `4.50%` |
| **`Qwen3-4B` `AutoRL`** | **`66.67%`** | **`56.67%`** | **`31.67%`** | **`32.50%`** | **`36.75%`** | **`59.73%`** | **`47.22%`** | **`65.25%`** | **`6.79%`** |

- On `Qwen3-4B`, `AutoRL` wins **all `9/9` benchmarks** (`+20.00 pp` on `AIME 24` over `GRPO`), while `General Agent` (`Codex`) severely degrades out-of-domain general knowledge and coding (`MMLU-Pro` `-18.15 pp` and `MBPP` `-30.75 pp` below the untuned Baseline). On `Qwen3-1.7B`, static `GRPO` collapses `MBPP` (`33.20% -> 10.95%`), whereas `AutoRL` lifts it to `40.05%` (`+29.10 pp`).

### 2. In-Flight Recipe Repair, Plateau Breakthrough & `14.7`-Day Crash Recovery (`§3.3–3.5`)

- **Flawed Recipe Repair (`LongCat-Flash-Lite` Math, `9,340` problems, `64×H800`, `115.5 h`, steps `0–64`)**: Starting at `65.53%` with a naive grader and `KL = 0` (`131,072`-token limit), static `GRPO` collapses to `56.05%`. `AutoRL` (`glm-5.2`) applies **`6` `HOT` updates with `0` restarts** (`4` `TRAIN` grader parser/unit/multiset repairs at steps `3, 6, 10, 38` + `KL = 0.001` at step `22` and `0.01` at step `27`), reaching **`73.16%`** (`+7.63 pp` over start, **`+17.11 pp`** over static `GRPO`).
- **Plateau Breakthrough (`Qwen3-4B`, `190`-problem monitoring set $\times 2 = 380$ responses; note `Appendix A.1` evaluates `AutoRL` every `5` steps vs `10` for static `GRPO`)**: After leaving the config untouched through step `100` (plateau peak `29.74%`), `AutoRL` executes a `COLD` `TRAIN` option-binding fix at step `101` (ckpt `100`), `HOT` entropy ramps (`0.001 -> 0.002 -> 0.003` at steps `108, 121, 129`) plus a `-0.02` strict looping penalty (step `111`), breaks the plateau at step `135` (`32.89%`), applies a `COLD` 2-reference fix (step `136`, ckpt `135`) and `HOT` entropy `0.004` (step `153`) + finite-orbit proof-certificate binding (step `171`), peaking at **`41.58%`** (`+11.84 pp` over plateau, `+10.26 pp` over static `GRPO` peak `31.32%`) and ending step `190` at **`37.89%` vs `30.26%`**.
- **Unattended `14.7`-Day Coding-Agent Recovery (`LongCat-Flash-Lite`, `700+` repo tasks narrowed to `271` final tasks, `28×8 = 224` `H800` GPUs, `352.5 h`, `<= 400` turns, `261,120` gen / `262,144` seq tokens)**: Across **`11` runtime failures** (`7` `NaN`, `1` dtype mismatch, `3` worker/comm; recovery latency `36.6–295.1 min`, `Table 11`), `AutoRL` tightens log-ratio clipping `[-13, 5] -> [-5, 3]` with spike limit `5` (`F5`), lowers `LR` and `min_LR` `5e-6 -> 2e-6` + enables MoE `FP32` accumulation + `FP32` residuals (`F6`), and **isolates and withdraws only `FP32` residuals** when `F7` triggers a dtype mismatch on ckpt `22`, raising SWE `pass@1` from `52.29%` to **`65.13%` peak (`+12.84 pp`, step `55`)** and **`63.20%` final (`+10.91 pp`)**.

### 3. Step Efficiency vs. `Codex` & The `0/3` Learning-Rule Redesign Ceiling (`§4.1–4.3`, `Tables 3, 7–8`)

| Metric (`273` Cumulative Steps on `Qwen3-4B`) | `General Agent` (`Codex`, `gpt-6.1-sol`) | `AutoRL` (`glm-5.2`) | `AutoRL` (`gpt-6.1-sol`) |
|:---|:---:|:---:|:---:|
| **Initial Action Candidates (Categories)** | `21` (`5` categories) | — | **`131`** (`8` categories across `168` discussions) |
| **Grading / Parsing / Reference Candidates** | `1 / 21` (`4.8%`) | Optimization-focused | **`110 / 131` (`84.0%`)** (`54` parse, `36` ref, `15` verify, `5` data) |
| **Distinct First-Visit Steps / Revisited Share** | `151 / 273` (**`44.7%` revisited**, `4` rewinds) | `193 / 273` (`29.3%` revisited) | **`273 / 273` (`0.0%` revisited, `0` rewinds)** |
| **Applied Interventions (`HOT` Share)** | `6` (`0%` `HOT`; `8/8` restarts full run) | `8 / 9` `HOT` (full `478`-step run) | **`20` (`17/20 = 85%` `HOT`, `3` `COLD`)** |
| **Reverted Interventions (Reversion Rate)** | `3 / 6` (**`50.0%`**) | — | **`4 / 20` (`20.0%`, reverted online)** |
| **Monitoring Peak / Last-5 Mean Accuracy** | `32.11%` / `29.16%` | `32.89%` / `30.68%` | **`41.58%`** / **`39.37%`** |

- **Fundamental RSI Limitation (`Table 3`)**: Of the `131` `GPT-6.1` candidates (`51` joint recommendations: `28` approved, `21` deferred, `2` rejected; `20` deployed within `273` steps: `10` grading/data, `9` parameter tuning, `1` reward extension), only **`3` (`2.3%`) proposed learning-rule redesigns** (covariance-based gradient selection; positive-advantage and entropy-guided token weighting) and **`0` reached execution**—either failing CPU sequence-packing / constant-advantage checks or losing out to lower-risk `HOT` entropy updates. Moreover, because `Eval Perceptor` observes monitoring-set aggregates across `168` discussions, any final checkpoint or persistent recipe promotion must still pass [`recursive-improvement.md`](../rules/recursive-improvement.md) (*"DO: Pass every self-modification through one acceptance gate"*) on a held-out split never queried during supervision.

---

## Related Artifacts

- **Rules**:
  - [`recursive-improvement.md`](../rules/recursive-improvement.md) — Acceptance gating, change-level classification, reasoning-effort vs. algorithmic-ability trade-offs, and process-level RL supervision
  - [`agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md) — Keeping `EVAL` harnesses strictly frozen while repairing `TRAIN` rollout graders
- **Skills**:
  - [`autonomous-research-to-launch-harness`](../skills/autonomous-research-to-launch-harness/SKILL.md) — Multi-expert council + deterministic state controller for multi-day research loops (`arXiv:2609.04871`)
  - [`evidence-gated-adversarial-deliberation`](../skills/evidence-gated-adversarial-deliberation/SKILL.md) — Evidence-gated adversarial multi-agent review (`arXiv:2609.27814`)
- **Research Briefs**:
  - [`infrarsi-training-infrastructure-rsi`](./infrarsi-training-infrastructure-rsi.md) — Verified multi-GPU training-infrastructure RSI (`arXiv:2611.11558`)
  - [`coevo-policy-aware-context-evolution`](./coevo-policy-aware-context-evolution.md) — Alternating GRPO weight updates and policy-state prompt scaffolds (`arXiv:2609.33398`)
  - [`rsi-arena-autonomous-post-training-feedback`](./rsi-arena-autonomous-post-training-feedback.md) — Autonomous post-training capability recovery and safety-gating requirements (`arXiv:2610.33624`)
