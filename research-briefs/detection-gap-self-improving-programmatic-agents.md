# Blind to What They Can Fix: A Detection Gap in Self-Improving Programmatic Agents

> **Source**: [arXiv:2611.29807](https://arxiv.org/abs/2611.29807) — Teng Cao, Yu Deng, Kristian Kersting (TU Darmstadt, hessian.AI, DFKI, 2026)
> **Praxis Source ID**: `src:2611-29807v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Why Not a Skill?

This paper is a controlled **pre-registered diagnostic study** (`120` registered predictions: `69` held, `36` failed, `14` undetermined, `1` held on `4/5` models) dissecting why self-improving agents that synthesize persistent programmatic policies plus runtime self-checks fail silently when deployed environments shift. Crucially, the authors demonstrate that **prompt-level remedies are sharply capability-gated or actively destructive**:

1. Explicitly telling the author model that *"the only thing that can call you back to repair the program is the program itself"* closes the detection gap on frontier `Codex (gpt-6.1-sol)` (`69% -> 6%` misses on `Seaquest`; `95% -> 0%` on `AppWorld`), yet **fails completely on open-weight coding models** (`Qwen3.8-27B` `94% -> 84%`, `Mistral-Medium-3.5` `51% -> 87%`, `gemma-4-31B` `86% -> 100%` misses).
2. Instructing `Codex` to maximize check coverage (*"monitor every object/variable range"*) backfires catastrophically, driving unchanged-episode false alarms to **`99.8%`** (**`99.6%` even after held-out calibration**).

Because there is no model-agnostic self-check authoring recipe—and external runtime monitors themselves carry sharp domain trade-offs—the paper's lasting value is **architectural and evaluation governance** for [`../rules/recursive-improvement.md`](../rules/recursive-improvement.md) and [`../specs/self-improving-agent.spec.md`](../specs/self-improving-agent.spec.md): benchmarking **detection separately from repair**, pairing deployed programmatic policies with **external outcome or confirmation-count reference monitors**, and never relying on uncalibrated LLM log-summary triggers.

---

## Experimental Setup

An authoring coding agent (`7` models: `Codex gpt-6.1-sol`, `Claude Code opus-5-5`, `Kimi-K2.6`, `Qwen3.8-27B`, `Qwen3.8-Flash`, `Mistral-Medium-3.5`, `gemma-4-31B`) writes a standalone policy/automation program **and** its own runtime health checks during an initial development session, selected by original-environment validation score $J_u^0$. At deployment, hidden post-deployment environment shifts occur across `5` domains (`Seaquest`, `Kangaroo`, `Service autoscaling`, `AppWorld` REST APIs, and `Craftax`). Task failure is defined independently of the agent's checks as a `> 50%` performance collapse ($J_u^- < \frac{1}{2} J_u^0$). If a runtime detector fires, the authoring agent is woken up for a repair session—receiving **only a `1`-bit alert** or check log, never the ground-truth change description.

---

## Key Empirical Findings

### 1. Standard Agent-Written Checks Miss `52%–95%` of Failures That the Same Agent Repairs at `90%–100%`

| Domain | Cohort (`Programs / True Failures`) | Own-Check Miss Rate | `Codex` Repair Rate When Alerted | Missed-and-Repaired Gap ($\widehat{G}$) | `1`-Line Outcome Rule Miss (Unchanged FA) | Frozen `20`-Ep General Monitor Miss (Harmless-Change FA) |
|:-------|:------------------------------------|:--------------------|:---------------------------------|:----------------------------------------|:------------------------------------------|:---------------------------------------------------------|
| **`Seaquest`** | `20 / 168` (`16 / 90` new-prog rep.) | **`52%`** (`59%` blind; `69%` rep.) | **`89.6%` (`69/77`)** (`81%` vs. `5%` score) | **`48%`** (`64%` incl. checkless; `47%` strict) | **`7%`** (`<= 5%` FA, `<= 11%` harmless) | **`5%`** (`<= 3%` FA, **`52%–69%` harmless FA**) |
| **`Kangaroo`** | `6 / 22` | **`55%`** | — | — | **`9%`** (`<= 5%` FA) | **`18%`** (`<= 3%` FA, **`52%–69%` harmless FA**) |
| **`Service autoscaling`** | `4 / 25` `Codex` (`14 / 82` `6` other models) | **`64%`** (`65%` other models; `95% -> 79% -> 64%` across `3` RSI gens) | **`100%` (`37/37`)** | **`64%`** (`80%` incl. checkless) | **`8%`** (`5%` other models; `<= 5%` FA) | **`0%`** (`6%` other models; **`52%–69%` harmless FA**) |
| **`AppWorld`** | `4 / 28` (`16 / 112` reg. rep.; `12 / 95` `3` open models) | **`89%`** (**`95%`** rep.; **`82%`** open models) | **`100%` (`55/55`; `112/112` & `122/122` rep.)** | **`89%`** (**`95%`** rep.) | N/A (no runtime scalar outcome) | **`61%–63%`** (weak cross-task invariants) |
| **`Craftax`** | `3 / 8` | **`0%`** | — | `0%` | — | **`68%` unchanged-day FA** (non-stationary) |

- **Threshold tuning cannot rescue narrow checks**: Sweeping the contradiction-count trigger $k \in \{1, \dots, 20\}$ on `Seaquest` still leaves **`49%–73%` misses** at `20%–17%` unchanged-episode false alarms.
- **A `1`-bit wakeup is nearly as effective as a full diagnostic report**: On `Codex`, waking the agent with zero explanation of what broke recovered post-repair performance within **`-0.01` (`95%` CI `[-0.05, +0.02]`)** of providing a full failure report, whereas open-weight models frequently broke previously working behavior during repair (`14/64`, `13/61`, `13/56` `AppWorld` sessions vs. `1/58` on `Codex`).

### 2. Why Checks Fail: Precondition Silence, Score-Only Selection, and Capability-Gated Purpose Framing

- **Broken preconditions silence contradiction counters (`61% -> 15%` fix via confirmation ranges)**: Agent-written `if cond: check(...)` guards stop executing altogether when an upstream schema or visual object shifts, yielding **`0` contradictions and `0` confirmations** (e.g., `evasive_divers` in `Seaquest`). Recording reference **confirmation-count ranges** alongside contradictions (`Own + ref.`) cut `Seaquest` misses from **`61% -> 15%`** at **`4%`** false alarms (`11%–20%` out-of-sample on `Codex`), and adding `32` random recorded-variable relations cut misses to **`4%, 4%, 15%`**.
- **Callback-purpose framing works on frontier `Codex` but fails on open weights**:
  - On `Codex`, stating explicitly that self-checks are the sole callback mechanism slashed `Seaquest` misses from **`69% -> 6%`** (by inducing time-budgeted progress checks; without progress checks, misses remained **`70%`**) and `AppWorld` misses from **`95% -> 0%`** at **`0%`** original-day false alarms (by inducing cross-endpoint metamorphic consistency checks).
  - On open-weight models, the exact same prompt left miss rates at **`84%` (`Qwen3.8-27B`, vs. `94%`)**, **`87%` (`Mistral-Medium-3.5`, worsened from `51%`!)**, and **`100%` (`gemma-4-31B`, worsened from `86%`!)**.
- **External LLM log-summary triggers fire prematurely**: In `Service autoscaling`, an external `GLM-5.2` log-summary monitor triggered **before the environment shift even occurred** in **`57%`** of `Codex` deployments (`71%–100%` on open models), forfeiting **`-0.28`** normalized `10`-day deployment value relative to the `20`-episode statistical monitor (`0.55` vs. `0.83`).

### 3. `10`-Day Deployment Economics: Detection Bottlenecks Repair Quality (`+0.01` Oracle Lift)

Across `10`-day deployments (`Seaquest` / `Autoscaling` / `AppWorld`), normalized cumulative value rose only modestly from `No callback` (`0.35 / 0.37 / 0.33`) to `Standard own checks` (`0.46 / 0.56 / 0.36`). **Replacing the real repair agent with a perfect instant oracle behind the agent's own checks added just `+0.01` (`Seaquest`) and `+0.03` (`Autoscaling`)**—proving that upgrading repair intelligence is wasted when detection is blind. Conversely, pairing the unchanged `Codex` repairer with the external general monitor lifted `Seaquest` / `Autoscaling` value to **`0.81 / 0.83`** (`+0.35` / `+0.28`, remaining superior up to repair session cost $\kappa = 3.7$ deployment days), and purpose-informed `Codex` metamorphic checks lifted `AppWorld` from `0.36` to **`0.90` (`+0.54`)**.

---

## Relevance to Praxis

1. **Runtime Post-Commit Complement to Pre-Commit Gates (`output/rules/recursive-improvement.md`)**: Pre-commit gates ([`verifier-equivalent-comparative-update-vetting`](../skills/verifier-equivalent-comparative-update-vetting/SKILL.md) and `"DO: Pass every self-modification through one acceptance gate"`) ensure a newly committed program is safe on frozen replay banks, while this brief shows why post-deployment shifts require **external outcome rules (`< 0.5` reference mean) or confirmation-count reference ranges** rather than trusting score-selected internal assertions.
2. **RSI Benchmark Design (`output/specs/self-improving-agent.spec.md`)**: Self-improvement benchmarks that always invoke the optimizer between rounds hide `48%–95%` of real-world deployment failures; evaluations must test **autonomous trigger precision/recall** (including harmless-change false-alarm rates) separately from triggered repair rate.
