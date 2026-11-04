# Skill-Infinity: Recursive Self-Improvement for Agent Skill Optimization

> **Source**: [arXiv:2610.35434](https://arxiv.org/abs/2610.35434) — *Skill$^{\infty}$: Recursive Self-Improvement for Agent Skill Optimization* (`src:2610-35434`)
> **Authors**: Yitao Liang et al. (2026)
> **Category**: Agent Skill Evolution / Recursive Meta-Skill Optimization

---

## Executive Summary

Existing skill-evolution frameworks (such as `SkillEvolver`, `SkillCreator`, and `EvoSkill`) treat the **task skill** as an editable text artifact while hardcoding the **skill optimizer** as a fixed Python workflow with hand-tuned prompts, fixed candidate branching factors, and rigid selection rules. **$\text{Skill}^\infty$** removes this asymmetry by encoding the skill-optimization procedure itself as a standard, portable **Agent Skills package** (`meta-skill/SKILL.md` plus `references/` and `scripts/`) that is loaded on demand via native progressive skill discovery and recursively self-improved before being deployed to optimize downstream task skills.

Evaluated across **83 tasks** spanning **8 domains** on **SkillsBench** (using `Codex CLI` + `GPT-6 Luna` across 5 independent runs, `avg@5`), $\text{Skill}^\infty$ achieves a **60.7%** pass rate—outperforming human-curated skills (**56.4%**, `+4.3 pp`), `SkillEvolver` (**54.5%**, `+6.2 pp`), `SkillCreator` (**48.0%**), self-generated skills (**42.9%**), and no-skill baselines (**45.5%**, `+15.2 pp`). Removing recursive self-improvement of the meta-skill drops performance from **60.7% to 55.9%** (`−4.8 pp`), demonstrating that refining the meta-skill itself is required to surpass human-curated skills. On **KernelBench** (3 Level-3 CUDA kernel optimization tasks on NVIDIA A100), $\text{Skill}^\infty$ achieves a **1.62×** mean correctness-weighted speedup over PyTorch Eager (`1.87×` MLP, `1.97×` ShuffleNet, `1.02×` GRU) compared to **1.18×** for `SkillEvolver` and **1.02×** for no skill.

---

## Architecture & Decoupled Two-Loop Formulation

### 1. The Optimizer as a Native Agent Skill

Instead of wrapping the agent in an external orchestration harness, $\text{Skill}^\infty$ packages the optimizer as a standard directory (`SKILL.md`, `references/`, `scripts/`) discovered via the harness's native skill loader:

- **Progressive Disclosure**: At startup, the agent sees only the `name` and `description` frontmatter in its system prompt and loads `SKILL.md` and reference files on demand, avoiding prompt-bloat overhead when optimization is not active.
- **No Harness Lock-In**: Because the meta-skill uses standard file and shell tools rather than internal harness hooks, the exact same optimized meta-skill transfers across agent harnesses (`Codex CLI` and `OpenCode`) and model backbones (`GPT-6 Luna` and `GPT-5.6 Luna`).

### 2. Two Decoupled Optimization Loops

$\text{Skill}^\infty$ separates **meta-skill self-improvement** from **downstream task-skill optimization**, coupling them only through the portable meta-skill artifact $m$:

1. **Outer Loop — Meta-Skill Self-Improvement ($m_0 \to m^\star$)**:
   - Given a seed meta-skill $m_0$ and a training set of skill-optimization tasks $Q$, the agent uses $m_0$ to optimize $m$ itself, maximizing mean downstream task-skill improvement $S(m; Q)$ under a small outer budget of **$\le 4$ meta-skill candidates** (with inner task-skill budget $B_q = 2$).
   - Crucially, the outer loop discovered a flaw in $m_0$'s parent-selection rule: when candidate skills tied on scalar benchmark score, $m_0$ selected the newer candidate **83%** of the time even when the rollout showed no progress on the diagnosed failure mode. Self-improvement rewrote the selection rule in $m^\star$ to require **verified rollout progress on the targeted failure before accepting a tied candidate**, cutting tied-candidate selection from **83% to 54%** and lifting the meta-evaluation score from **0.55 to 0.83**.
2. **Inner Loop — Task-Skill Optimization ($s_0 \to s^\star$ using frozen $m^\star$)**:
   - Once $m^\star$ is frozen, it optimizes any task skill $s_0 \to s^\star$ within a budget of **$B = 4$ candidates** per task using a 6-step agent-led cycle:
     1. **Inspect** the lineage archive of prior skill versions and scores.
     2. **Diagnose** parent execution rollouts to isolate the specific failure step.
     3. **Propose** $1 \le k \le \min(2, b)$ falsifiable skill edits, each recording an explicit *observation*, *change*, *prediction*, and *falsifier*.
     4. **Evaluate** candidate skills on the task environment.
     5. **Independent Review**: Spawn an isolated sub-context reviewer to verify three binary gates before admission: (a) *Did the skill file actually change?*, (b) *Was the skill activated/loaded during the rollout?*, and (c) *Is the edit generalizable rather than hardcoded?* (deferring to `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../rules/recursive-improvement.md)).
     6. **Decide** the next parent from the archive or early-stop once the target is met.

---

## Key Empirical Results

### 1. SkillsBench Main Evaluation (83 Tasks Across 8 Domains, `avg@5`)

| Method (`Codex CLI` + `GPT-6 Luna`) | Overall Pass Rate (83 Tasks) | vs. No Skill | vs. Human-Curated |
|:---|:---:|:---:|:---:|
| **No Skill** | 45.5% | — | −10.9 pp |
| **Self-Generated Skill** (one-shot before acting) | 42.9% | −2.6 pp | −13.5 pp |
| **SkillCreator** | 48.0% | +2.5 pp | −8.4 pp |
| **SkillEvolver** (fixed Python workflow) | 54.5% | +9.0 pp | −1.9 pp |
| **Human-Curated Skill** | 56.4% | +10.9 pp | — |
| **$\text{Skill}^\infty$ w/o Self-Improvement** (seed $m_0$) | 55.9% | +10.4 pp | −0.5 pp |
| **$\text{Skill}^\infty$ (Full, with self-improved $m^\star$)** | **60.7%** | **+15.2 pp** | **+4.3 pp** |

- **Domain-Level Gains from Meta-Skill Self-Improvement ($m_0 \to m^\star$)**: The `+4.8 pp` overall gain from self-improving the meta-skill is driven by large jumps in **Mathematics** (`68.0% → 92.0%`, **+24.0 pp**), **Media** (`62.2% → 84.4%`, **+22.2 pp**), and **Software Engineering** (`54.3% → 65.7%`, **+11.4 pp**).
- **Performance by Skill-Utility Category**: On **Category D** (the 19 hardest tasks where *neither* the no-skill baseline nor the human-curated skill succeeds, `0.0%` human-curated), $\text{Skill}^\infty$ achieves **30.5%** vs. **22.1%** for `SkillEvolver`.

### 2. Cross-Model, Cross-Harness, and KernelBench Generality

- **Cross-Model (`GPT-5.6 Luna` on `Codex CLI`)**: $\text{Skill}^\infty$ reaches **66.5%** overall pass rate vs. **61.2%** for Human-Curated (`+5.3 pp`) and **48.4%** for No Skill.
- **Cross-Harness (`OpenCode` + `GPT-6 Luna`)**: Without modifying $m^\star$, $\text{Skill}^\infty$ achieves **56.9%** vs. **53.3%** for Human-Curated (`+3.6 pp`) and **44.1%** for No Skill.
- **KernelBench (Level-3 CUDA Kernel Synthesis on A100)**:
  - **MLP**: `1.87×` speedup (`SkillEvolver`: `1.34×`, No skill: `1.00×`)
  - **ShuffleNet**: `1.97×` speedup (`SkillEvolver`: `1.19×`, No skill: `1.04×`)
  - **GRU**: `1.02×` speedup (`SkillEvolver`: `1.01×`, No skill: `1.01×`)
  - **Mean Correctness-Weighted Speedup**: **1.62×** vs. **1.18×** (`SkillEvolver`) and **1.02×** (No skill).

### 3. Budget Scaling & Token Cost

- **Candidate Budget Scaling**: On the budget-scaling evaluation subset (where No Skill scores `12.5%`), scaling the task-skill candidate budget $B$ from `1 → 2 → 4 → 8` raises pass rate monotonically from **47.5% → 62.5% → 75.0% → 82.5%**, outperforming `SkillEvolver` at every budget point.
- **Token Cost & Amortization**: Optimizing a single task skill ($B = 4$) consumes **8.74M input tokens** (of which **8.23M are prompt-cached**) and **66.3k output tokens**, comparable to `SkillEvolver` (`8.06M` input / `76k` output). The one-time outer-loop self-improvement of $m_0 \to m^\star$ costs roughly the equivalent of **~11 task-skill optimizations** (`< 15%` overhead when amortized across the 83 SkillsBench tasks).

---

## Limitations & Failure Modes

1. **Verifier Requirement**: Like all execution-driven skill evolution methods, $\text{Skill}^\infty$ requires an executable evaluator or rubric signal during the optimization phase; noisy or uncalibrated verifiers can misdirect both $m^\star$ and $s^\star$.
2. **Frontier Executor Assumption**: All experiments in $\text{Skill}^\infty$ use frontier reasoning models (`GPT-6 Luna`, `GPT-5.6 Luna`). As shown in [`capability-matched-skill-adaptation`](../skills/capability-matched-skill-adaptation/SKILL.md) (`arXiv:2610.33024`), skills evolved for frontier executors often fail on smaller models unless explicitly adapted across tool-execution, context, instruction-following, and verification bottlenecks.

---

## Why Not a Skill?

The subtask-level building blocks used inside $\text{Skill}^\infty$'s inner loop—hypothesis-driven skill revision with explicit falsifiers, lineage archive parent selection, independent activation review, and sequential stopping—are already covered by existing Praxis skills ([`belief-calibrated-scaffold-optimization`](../skills/belief-calibrated-scaffold-optimization/SKILL.md), [`evidence-guided-skill-audit`](../skills/evidence-guided-skill-audit/SKILL.md), [`self-evolution-stopping-rule`](../skills/self-evolution-stopping-rule/SKILL.md), and [`capability-matched-skill-adaptation`](../skills/capability-matched-skill-adaptation/SKILL.md)). This brief preserves the architectural insight of packaging the optimizer itself as a progressive-disclosure `SKILL.md` and the empirical ablation showing that tie-breaking without verified rollout progress on the targeted failure causes `83%` tied-candidate churn.

---

## Related Artifacts

- **Rules**:
  - [`skill-system-design.md`](../rules/skill-system-design.md) — Skill authoring, progressive disclosure, and evolution governance.
  - [`recursive-improvement.md`](../rules/recursive-improvement.md) — *"DO: Pass every self-modification through one acceptance gate"*.
- **Skills**:
  - [`capability-matched-skill-adaptation`](../skills/capability-matched-skill-adaptation/SKILL.md) — Adapting evolved skills across executor capability tiers (`arXiv:2610.33024`).
  - [`evidence-guided-skill-audit`](../skills/evidence-guided-skill-audit/SKILL.md) — Auditing candidate skills before library admission.
  - [`belief-calibrated-scaffold-optimization`](../skills/belief-calibrated-scaffold-optimization/SKILL.md) — Maintaining explicit hypotheses and falsifiers during scaffold evolution.
- **Research Briefs**:
  - [`r2flow-recursive-skill-evolution.md`](r2flow-recursive-skill-evolution.md) — Evidence-gated recursive skill evolution.
