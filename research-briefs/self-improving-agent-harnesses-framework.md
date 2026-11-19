# Harnesses That Improve Themselves: A Unifying Framework for Self-Improving Agent Harnesses

> **Source**: [arXiv:2611.22299](https://arxiv.org/abs/2611.22299) — Deep Shah, Nehal Kathrotia (`Google`, November 2026)
> **Praxis Source ID**: `src:2611-22299v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

`arXiv:2611.22299` is an **architectural synthesis and taxonomy of `16` self-improving agent-harness systems** (`Meta-Harness`, `Self-Harness`, `AutoSaddler`, `HarnessCompass`, `ModularRSI`, `RRSI`, `HarnessBank`, `DGM/MGM`, `ActiveSaddler`, `Dream-RSI`, `SoL-Pi`, `MoSIB`, `Turbo Harness`, `Vestrum`, `GUI-HARVEST`, and `RegenHarness`) paired with a `60`-issue `SWE-bench Lite` reference ablation (`Table IV`). Concrete, step-by-step procedures for bounded single-component harness evolution, tree-search multi-file harness optimization, scoped multi-agent harness composition, and continual regret-guided playbook gating are already covered as standalone skills in [`regularized-harness-evolution`](../skills/regularized-harness-evolution/SKILL.md), [`mcts-full-harness-optimization`](../skills/mcts-full-harness-optimization/SKILL.md), [`scoped-multi-agent-harness-composition`](../skills/scoped-multi-agent-harness-composition/SKILL.md), and [`regret-guided-continual-harness-evolution`](../skills/regret-guided-continual-harness-evolution/SKILL.md). We catalog `arXiv:2611.22299` as a Research Brief and add its controlled `SWE-bench Lite` ablation evidence (modular gated code evolution vs. unconstrained full-harness rewrites vs. prompt-only `RULES.md` reflection, plus zero-shot cross-model transfer) to [`skill-system-design.md`](../rules/skill-system-design.md).

---

## Core Framework: Four Editable Surfaces & Four-Stage Outer Loop

Holding base model weights $\theta$ fixed, the framework decomposes the executable agent harness into $h = (h_{\mathrm{ctx}}, h_{\mathrm{ctrl}}, h_{\mathrm{act}}, h_{\mathrm{ver}}) \in \mathcal{H}$ (`Table I`, `§2`):

1. **Context & State ($h_{\mathrm{ctx}}$)**: Prompt assembly, working-memory compaction, rolling trajectory summaries, and structured status footers (`context_mgr.py`).
2. **Agent Control ($h_{\mathrm{ctrl}}$)**: Turn budgets, loop termination conditions, branching/retry logic, and sub-agent delegation schedules (`control.py`).
3. **Action Interface ($h_{\mathrm{act}}$)**: Agent–Computer Interface (`ACI`) wrappers—windowed file readers, shell output truncation, structured edit commands, and pre-exit empty-diff guards (`action_aci.py`).
4. **Verification & Recovery ($h_{\mathrm{ver}}$)**: Executable pre-completion gates, syntax/compiler checks, targeted regression test hooks, and rollback handlers (`verify.py`).

Across the `16` surveyed systems, outer-loop harness self-improvement follows a four-stage cycle (`Eq. 1`, `§3`):

$$\text{Diagnose (full execution traces)} \;\longrightarrow\; \text{Propose (`1` module/step)} \;\longrightarrow\; \text{Validate \& Filter (held-out + token budget $B_{\mathrm{tok}}$)} \;\longrightarrow\; \text{Deploy or Route}$$

Crucially, diagnosis operates over **raw execution trajectories** (tool calls, compiler/test outputs, truncation events, and premature exits) rather than scalar pass rates alone, while Stage 3 enforces **both** validation non-regression and an explicit per-task token cap $B_{\mathrm{tok}}$ (in Praxis deployments, paired with `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../rules/recursive-improvement.md)).

---

## Reference Ablation on `60` `SWE-bench Lite` Issues (`§6`, `Table IV`)

Starting from a minimal `142`-line Python seed harness $h_0$ (`12`-turn cap across `context_mgr.py`, `control.py`, `action_aci.py`, and `verify.py`), the authors evaluate five regimes over `60` real `SWE-bench Lite` Python issues (`sympy/sympy`: `N = 12` Dev, `N = 8` Val, `N = 20` held-out ID test; `django/django`: `N = 20` cross-repository OOD test) using frozen `Gemini 3.8 Flash` as the task executor, `Gemini 4 Carbon` (fallback `Gemini 4 Argon`) as the outer-loop proposer, and Stage-3 token budget $B_{\mathrm{tok}} = 110.0\text{k}$ tokens/task:

| Regime (`Part A`: `Gemini 3.8 Flash`; `Part B`: Zero-Shot Transfer to `Gemini 4 Argon`) | Search Rollouts | ID (`sympy`, `N=20`) | OOD (`django`, `N=20`) | Combined (`N=40`) | Avg Tok / Task | Tok / Solved | Unverified OOD Exits |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Part A (`Gemini 3.8 Flash`, evolved)** | | | | | | | |
| `Frozen Seed (Pass@1, h_0)` | `0` | `10.0%` (`2/20`) | `0.0%` (`0/20`) | `5.0%` (`2/40`) | `114.8k` | `2,296.7k` | `15.0%` |
| `Frozen Seed (Best-of-3)` (`120` inference runs) | `0` | `5.0%` (`1/20`) | `5.0%` (`1/20`) | `5.0%` (`2/40`) | `237.6k` | `4,752.2k` | `5.0%` |
| `Prompt-Only Reflection` (`RULES.md` text only) | `24` | `5.0%` (`1/20`) | `0.0%` (`0/20`) | `2.5%` (`1/40`) | `60.5k` | `2,420.2k` | **`30.0%`** |
| `Unconstrained Full-Harness Rewrite` (all `4` files ungated, cap `12 -> 28`) | `24` | `35.0%` (`7/20`) | `50.0%` (`10/20`) | `42.5%` (`17/40`) | **`451.6k`** | `1,062.6k` | `5.0%` |
| **`Modular Gated Evolution` (`1` module/step, gated by `Val` + $B_{\mathrm{tok}}$)** | `100` | **`40.0%` (`8/20`)** | **`40.0%` (`8/20`)** | **`40.0%` (`16/40`)** | **`46.7k`** | **`116.8k`** | **`0.0%`** |
| **Part B (`Gemini 4 Argon`, `0` re-evolution rollouts)** | | | | | | | |
| `Frozen Seed (h_0)` | `0` | `10.0%` (`2/20`) | `10.0%` (`2/20`) | `10.0%` (`4/40`) | `140.4k` | `1,404.0k` | `0.0%` |
| `Prompt-Only Reflection` | `0` | `15.0%` (`3/20`) | `15.0%` (`3/20`) | `15.0%` (`6/40`) | `143.9k` | `959.2k` | `0.0%` |
| `Unconstrained Full-Harness Rewrite` | `0` | `30.0%` (`6/20`) | `30.0%` (`6/20`) | `30.0%` (`12/40`) | `284.7k` | `949.0k` | `0.0%` |
| **`Modular Gated Evolution` (transferred verbatim)** | `0` | **`40.0%` (`8/20`)** | **`35.0%` (`7/20`)** | **`37.5%` (`15/40`)** | **`64.8k`** | **`172.7k`** | `5.0%` (`0.0%` empty-diff) |

### Key Takeaways & Governance Implications

- **Prompt rules cannot substitute for executable verification hooks**: `Prompt-Only Reflection` (`RULES.md` text only) cut `Flash` combined resolution in half (`5.0% -> 2.5%`) and **doubled unverified OOD exits (`15.0% -> 30.0%`)** *even though `RULES.md`'s very first line explicitly forbade calling `finish` with an empty diff or without running tests*. By contrast, `Modular Gated Evolution` accepted an executable `verify.py` gate (blocking exit unless `git diff` is non-empty, edited Python files compile, and post-edit `pytest` succeeds, with a final-turn preservation bypass) plus `action_aci.py` windowed file views and `context_mgr.py` head-tail compaction (`> 2` turns old), driving unverified `Flash` OOD exits to **`0.0%`**.
- **Unconstrained rewrites buy marginal recall via `~10x` inference token inflation and degrade on transfer**: `Unconstrained Full-Harness Rewrite` raised the turn limit from `12` to `28` across all four files simultaneously, inflating inference cost **`~10x` (`451.6k` vs. `46.7k` avg tokens/task; `1,062.6k` vs. `116.8k` tokens/solved)**—with one rollout exceeding `2.8M` tokens—and **underperformed `Modular Gated Evolution` upon zero-shot transfer to `Gemini 4 Argon` (`30.0%` vs. `37.5%`, at `4.4x` higher token cost: `284.7k` vs. `64.8k`)**. In `Modular Gated Evolution`, Stage 3 explicitly **rejected** a proposed `control.py` mutation (`12 -> 18` turns) that improved Dev accuracy while regressing Val and breaching $B_{\mathrm{tok}} = 110.0\text{k}$; its `100`-rollout evolution cost (`20` seed + `4 × 20` module evaluations) amortizes in **`< 100` deployment queries** because evolved runs consume `68.1k` fewer tokens per task than the frozen seed (`46.7k` vs. `114.8k`).

---

## Related Artifacts

- **Skills**: [`regularized-harness-evolution`](../skills/regularized-harness-evolution/SKILL.md) (`arXiv:2609.24972`), [`mcts-full-harness-optimization`](../skills/mcts-full-harness-optimization/SKILL.md) (`arXiv:2611.06254`), [`scoped-multi-agent-harness-composition`](../skills/scoped-multi-agent-harness-composition/SKILL.md) (`arXiv:2611.12552`), [`regret-guided-continual-harness-evolution`](../skills/regret-guided-continual-harness-evolution/SKILL.md) (`arXiv:2611.23476`), [`asynchronous-system1-harness-evolution`](../skills/asynchronous-system1-harness-evolution/SKILL.md) (`arXiv:2611.22432`)
- **Rules**: [`skill-system-design.md`](../rules/skill-system-design.md), [`recursive-improvement.md`](../rules/recursive-improvement.md)
- **Research Briefs**: [`flex-rsi-frontier-agent-benchmark`](./flex-rsi-frontier-agent-benchmark.md) (`arXiv:2611.08946`), [`roboace-adversarial-curriculum-execution-coevolution`](./roboace-adversarial-curriculum-execution-coevolution.md) (`arXiv:2611.13034`)
