# PersonaCodeBench: Evaluating Coding Agents in Persona-Driven Human-Interactive Sessions

> **Source**: [arXiv:2611.05739](https://arxiv.org/abs/2611.05739) | `src:2611-05739`
> **Authors**: Haixin Wang et al.
> **Category**: Research Brief (Interactive Coding Benchmarks / Persona-Driven Requirements / Agent Evaluation)

## Overview

Standard software engineering benchmarks (`SWE-bench`, `LiveCodeBench`, `Terminal-bench`) evaluate coding agents in single-turn, static-prompt regimes where the entire specification is provided upfront and success is measured solely by repository unit tests. In real developer workflows, however, human collaborators vary widely in technical expertise, operational constraints, trust levels, and verification needs—communicating requirements across multi-turn sessions and imposing non-functional obligations (such as preserving pre-existing workspace files, avoiding privileged database operations, rehearsing rollbacks, or formatting concise handoff summaries for non-technical stakeholders).

Wang et al. introduce **PersonaCodeBench**, a multi-turn interactive benchmark built from `5` software engineering sources (`Terminal-bench 3`, `DeepSWE`, `SWE-bench-Live`, `SWE-Together`, and `SWE-bench Pro`) through a 4-stage pipeline: source collection, persona adaptation across `10` realistic user templates, contrastive screening with `GPT-6 Luna` (retaining tasks where the agent passes the native benchmark task but fails the persona-adapted interactive session), and source-proportional release. The benchmark releases two splits:
- **PersonaCodeBench-Full**: `231` task–persona pairs (`52` `Terminal-bench 3`, `64` `DeepSWE`, `45` `SWE-bench-Live`, `9` `SWE-Together`, `61` `SWE-bench Pro`), `422` evolved requirements, and `66` distinct persona profiles across `4` opening disclosure mechanisms (`75` concise summary, `45` complete issue deferral, `64` staged native disclosure S1–S4, and `47` native description upfront).
- **PersonaCodeBench-Lite**: `100` representative task–persona pairs (`23` `Terminal-bench 3`, `28` `DeepSWE`, `19` `SWE-bench-Live`, `4` `SWE-Together`, `26` `SWE-bench Pro`), `186` evolved requirements (`1.86` per task), and `35` distinct persona profiles.

Every episode is scored by a **Joint Pass** criterion requiring the agent to pass **both** the native repository `completion verifier` (functional unit tests) **and** the `personalization verifier` (online turn gates + final deliverable/workspace obligation checks) within the interaction budget.

## Key Findings

1. **Even the Strongest Frontier Model Fails Over Half of Persona-Interactive Coding Tasks (`48.0%` Max Joint Pass)**: Across `26` evaluated model configurations on `PersonaCodeBench-Lite` (`100` tasks), the top-performing model (`GPT-6 Astra (max)`) achieves only `48.0%` Joint pass (`80.8%` on `SWE-bench Pro`, `53.6%` on `DeepSWE`, `36.8%` on `SWE-bench-Live`, `25.0%` on `SWE-Together`, and `17.4%` on `Terminal-bench 3`), followed by `GPT-6.1 Sol (xhigh)` at `42.0%`, `Claude Opus 5.5 (medium)` at `40.0%`, `Claude Fable 5.1 (high)` at `39.0%`, `GPT-5.6 Terra (xhigh)` at `34.0%`, `Claude Sonnet 5.5 (high)` at `26.0%`, `Grok 4.7 (high)` at `24.0%`, and `Gemini 4 Argon (high)` at `23.0%`. Lightweight and open models score between `1.0%` (`Qwen 3.8 Flash Next`) and `19.0%` (`GPT-6 Luna`).
2. **Operational & Evidentiary Obligations—Not Progressive Disclosure—Drive Failure (`+1.0` pp vs. `+26.0` pp Ablation)**: On `GPT-6 Luna`, disclosing all evolved persona requirements upfront in the very first user turn (`PersonaCodeBench w. Opening`) improves Joint pass by only **`+1.0` percentage point** (`19.0%` $\to$ `20.0%`; native completion `24.0%` $\to$ `26.0%`; personalization `50.0%` $\to$ `51.0%`). In contrast, removing persona obligations altogether (`PersonaCodeBench w/o Persona`, neutral user with native task only) jumps pass rate by **`+26.0` percentage points** (`19.0%` $\to$ `45.0%`), proving that **managing persona constraints and verification gates degrades underlying functional code completion by `21.0` percentage points (`45.0%` $\to$ `24.0%`)**.
3. **One in Five Functionally Correct Patches Fails Persona Obligations (`20.5%` Silent Contract Failure)**: Across `1,962` complete non-provisional run–task records on `PersonaCodeBench-Lite`, `874` runs pass all native repository unit tests, yet **`179 of those 874` (`20.5%`) fail the personalization verifier** (`695` pass both, `179` pass completion but fail persona, `491` fail completion but pass persona, and `597` fail both).
4. **Sharp Asymmetry Across Persona Archetypes (Bounded Deliverables Succeed; Workspace-Hygiene & Rollback Obligations Collapse)**:
   - *High-performing personas (`GPT-6 Luna`)*: Agents succeed when obligations map to bounded, inspectable code artifacts—`Founders` with leaked credentials (`3/4` Joint pass, `4/4` observed persona pass), `Test-focused leads` (`2/6` Joint, `4/4` persona pass), `Analysts without DB index permissions` (`3/6` Joint, `5/6` persona pass), and `Senior concurrency reviewers` (`3/6` Joint, `4/5` persona pass).
   - *Catastrophic-failure personas*: Agents fail repeatedly on workspace state management, rollback verification, and non-technical evidence translation—`Shop owners unable to install software` (`0/5` Joint, `1/4` persona pass: running rollback verification inadvertently wipes out the final task patch [`no_task_change`] or rehearses against the wrong backup path), `Outcome-oriented managers` (`2/18` Joint, `4/15` persona pass, and `1/11` in `DeepSWE` because agents write code-level summaries instead of scenario-by-scenario user actions and visible outcomes), `First-time PR contributors` (`3/19` Joint, `7/14` persona pass: `6/6` in `SWE-bench Pro` vs `0/7` in `DeepSWE` where scope manifests fail to isolate pre-existing untracked files like `persona-user-notes.txt` or omit earlier failed test attempts), and `Students` (`2/20` Joint, `6/13` persona pass).
5. **Reasoning Effort Non-Monotonicity Under Interactive Budgets**: Across `8` models evaluated at multiple reasoning effort levels on common non-timeout tasks at fixed $1\times$ budget, **`6 of 8` models exhibit at least one pass-rate regression as reasoning effort increases** (e.g., `GPT-6.1 Sol` rises from `29.0%` at `medium` to `46.4%` at `xhigh`, then drops to `40.6%` at `max` across $n=69$ common tasks), and `0 of 33` within-model effort pairs clear the Bonferroni significance threshold ($p < 0.05/33 \approx 0.0015$).
6. **Hybrid Deterministic + Multi-Vote LLM Verifier Reliability**: Deterministic handoff-format checkers on `SWE-bench-Live` achieve `133/133` (`100%`) accuracy on targeted controls (`30` valid accepted, `93` invalid rejected including 180- vs 181-word boundaries and manager no-code constraints, `10` missing-evidence `Unresolved`) and `35/35` replay reproducibility. In contrast, 3-vote LLM judges (`GPT-6 Luna`) show a `25.0%` (`9/36`) vote-split rate on `GLM-5.3` `DeepSWE` checks and `8.2%` (`6/73`) on `GPT-6.1 Sol`, with blinded human expert adjudication ($n=148$ judgments from `15,100` records) showing `71.0%` 3-way agreement ($\kappa = 0.473$) and `77.2%` binary accept/reject agreement ($\mathrm{MCC} = 0.541$, `89.2%` precision, `74.5%` recall on `Satisfied`).

## Quantitative Summary

### Table 1: PersonaCodeBench-Lite Leaderboard (Selected Configurations Across 100 Tasks)

| Model Configuration | Overall Joint Pass (%) | `Terminal-bench 3` (`23`) | `SWE-bench-Live` (`19`) | `DeepSWE` (`28`) | `SWE-bench Pro` (`26`) | `SWE-Together` (`4`) |
|:---|---:|---:|---:|---:|---:|---:|
| `GPT-6 Astra (max)` | **48.0** | 17.4 | 36.8 | 53.6 | **80.8** | 25.0 |
| `GPT-6 Astra (xhigh / high / medium)` | 45.0 / 45.0 / 38.0 | — | — | — | — | — |
| `GPT-6.1 Sol (xhigh)` | 42.0 | 17.4 | 31.6 | **57.1** | 57.7 | 25.0 |
| `Claude Opus 5.5 (medium)` | 40.0 | 8.7 | **57.9** | 21.4 | 53.8 | **50.0** |
| `Claude Fable 5.1 (high)` | 39.0 | — | — | — | 69.2 | — |
| `GPT-5.6 Terra (xhigh)` | 34.0 | — | — | — | — | — |
| `Claude Sonnet 5.5 (high)` | 26.0 | — | — | 0.0 | 65.4 | — |
| `Grok 4.7 (high)` / `Gemini 4 Argon (high)` | 24.0 / 23.0 | — | — | — | — | — |
| `GLM-5.3 (high, textual)` / `GPT-6 Luna (medium)` | 22.0 / 19.0 | — | — | — | — | — |
| `GPT-6 Sol (max)` / `GPT-5.5 (xhigh)` | 18.0 / 18.0 | — | — | — | — | — |
| `Gemini 3.8 Flash` / `Grok 4.6 (medium)` | 17.0 / 17.0 | — | — | — | — | — |
| `GLM-5.3 Flash (max)` / `Claude Haiku 5.5 (high)` | 15.0 / 11.0 | — | — | — | — | — |
| `Qwen 3.8 27B` / `Kimi-K3` / `DeepSeek V4.1` / `Qwen 3.8 Flash Next` | 6.0 / 6.0 / 5.0 / 1.0 | — | — | — | — | — |

### Table 2: Disclosure vs. Obligation Ablation on `GPT-6 Luna` (`100` Lite Tasks)

| Evaluation Condition | Joint Pass (%) | Completion Verifier Pass (%) | Personalization Verifier Pass (%) | Key Diagnostic Interpretation |
|:---|---:|---:|---:|---|
| **Default `PersonaCodeBench`** (progressive disclosure) | 19.0 | 24.0 | 50.0 | Full multi-turn interactive baseline |
| **`PersonaCodeBench w. Opening`** (all requirements in Turn 1) | 20.0 (`+1.0` pp) | 26.0 (`+2.0` pp) | 51.0 (`+1.0` pp) | Progressive disclosure is **not** the primary bottleneck |
| **`PersonaCodeBench w/o Persona`** (neutral user, native task) | **45.0** (`+26.0` pp) | **45.0** (`+21.0` pp) | — | Persona obligations & gates degrade native task completion by `21.0` pp |

## Why Not a Skill?

PersonaCodeBench is a benchmark dataset (`231` Full / `100` Lite interactive coding tasks) and evaluation harness architecture rather than a single reusable agent procedure. However, its failure taxonomy exposes concrete operational blind spots in coding agents (such as wiping out the final task patch during rollback verification, polluting PR manifests with pre-existing workspace files, and writing code-heavy summaries for non-technical managers) that directly inform our interactive agent evaluation and human-interaction rules.

## Actionable Takeaways

1. **Always re-apply or verify the target patch after running a rollback rehearsal**: In `Shop owner` persona tasks (`0/5` Joint pass on `GPT-6 Luna`), agents repeatedly failed with `no_task_change` because they executed their rollback script to prove it worked and forgot to restore the patched state before ending the session. Any workflow that tests a backup/restore mechanism must verify `git diff` / target state *after* the rehearsal completes.
2. **Snapshot `git status --porcelain` before making edits to isolate pre-existing workspace artifacts**: In `First-time PR contributor` tasks on `DeepSWE` (`0/7` persona pass), agents failed scope-manifest checks because they either swept pre-existing untracked user files (e.g., `persona-user-notes.txt`) into their PR manifest or deleted them during cleanup. Record the pre-task dirty file list at Turn 1 and exclude those paths from change manifests and cleanup commands.
3. **Prefer deterministic format/state checkers over LLM judges for handoff obligations**: Deterministic handoff verifiers achieved `100%` (`133/133`) control accuracy and `35/35` replay consistency, whereas 3-vote LLM judges split on `8.2–25.0%` of trajectories and achieved $\kappa = 0.473$ (`77.2%` binary agreement) against human experts. Use programmatic checks for word limits, forbidden code blocks, file-touch manifests, and permission boundaries whenever possible.
