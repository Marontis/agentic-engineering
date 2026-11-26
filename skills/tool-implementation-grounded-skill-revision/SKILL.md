---
name: tool-implementation-grounded-skill-revision
description: >-
  Revise existing agent skill guidance without task-specific verifiers by
  extracting AST-indexed operational contracts from bundled tool implementations,
  aligning them against unlabeled execution traces, and applying bounded
  read-only substring patches. Derived from VISE (arXiv:2611.32480).
source: "arXiv:2611.32480"
repository: "https://github.com/Marontis/agentic-engineering"
license: CC-BY-4.0
---

<!-- Licensed under CC BY 4.0 | Source: Marontis/agentic-engineering | Origin: arXiv:2611.32480 -->

# Tool-Implementation-Grounded Skill Revision

## When to Use

Use this procedure when iteratively revising natural-language skill instructions (`SKILL.md`) for an agent workflow that **lacks task-specific unit tests, reward rubrics, or outcome verifiers**, provided the skill package or workspace exposes **inspectable helper scripts, CLI wrappers, or local library code**. Representative project types include:

- **Script-backed data-science and scientific pipelines**: Revising `SKILL.md` guides that orchestrate local Python/R analysis, simulation, or report-generation scripts where invocation order, flag constraints, and silent failure conditions live inside the scripts rather than in an external test harness.
- **DevOps, build, and repository automation skills**: Updating operational runbooks paired with local shell/Python deployment, lint, or migration scripts after unlabeled execution attempts fail or behave inconsistently across runs.
- **Multimodal document, CAD, or media processing workflows**: Refining skill instructions that coordinate local conversion, OCR, or rendering utilities whose input preconditions and fallback branches are enforced in code but omitted or misstated in documentation.

**When NOT to use**:
- **Pure prose or closed-API skills with zero inspectable implementation**: When tools are opaque remote SaaS endpoints or no helper code exists, implementation extraction recovers little evidence; fall back to Turn-0 checklist/execution gating ([`regret-guided-continual-harness-evolution`](../regret-guided-continual-harness-evolution/SKILL.md)) or surrogate rubrics ([`dense-rubric-skill-evolution`](../dense-rubric-skill-evolution/SKILL.md)).
- **Domains with rich task-specific unit-test reports on general software tasks**: When a faithful, task-specific structured test report already exists and the skill carries no specialized tool scripts (e.g., general repository bug fixing), test-report feedback can outperform implementation-only feedback (`+5.9%` to `+21.6%` vs. `-3.9%` to `+3.9%` on `SkillLearnBench` `Software Engineering` in `arXiv:2611.32480`).
- **Initial one-shot repository onboarding from scratch**: To synthesize a brand-new skill from an undocumented repository before any `SKILL.md` or execution trace exists, distill the initial skill first (see [`repo-to-skill-distillation`](../../research-briefs/repo-to-skill-distillation.md)), then apply this procedure for trace-driven revision.

---

## Core Insight

Verifier-free skill evolution loops (`Self-Refine`, `TraceEvo`, `SkillLearn`, `SkillRevise`) routinely stall or regress when revising `SKILL.md` from an unlabeled execution trace alone: without external grounding, the reviser overfits superficial trace narration, invents unsupported flags, or rewrites working guidance (`CoEvoSkills` dropped mean reward from `49.44` to `36.60`, and `Self-Refine` lost full reward on `9` previously solved `SkillsBench` tasks while gaining `9`). Yet most tool-bearing skills `S = (P, M)` already ship with an authoritative, verifier-independent ground truth inside their executable code `P`: valid entrypoints, argument invariants, stage ordering, raised exceptions, and fallback branches.

Dumping raw script files directly into a revision prompt fails (`-18.89 pp` `P@1` and `-16.67 pp` `Hit^3` vs. structured extraction in `VISE`, `arXiv:2611.32480`) because low-level code noise drowns out workflow-level gaps. **VISE** bridges code and guidance through four structured stages while keeping `P` strictly read-only: (1) AST-indexed extraction of line-verified operational knowledge records `K`, (2) trace-conditioned workflow alignment `A` between `K` and `M`, (3) quote-anchored missing/conflicting guidance items `F`, and (4) bounded exact-substring patching (`<= 4` edits) or explicit `KEEP`. Across `SkillsBench` and `SkillLearnBench` (`177–179` complete-score tasks across `4` evolution backbones on `gpt-5.5`), `VISE` improves `P@1` by **`+9.14` to `+13.35` pp**, `P@3` by **`+4.59` to `+7.93` pp**, and strict `3/3` consistency (`Hit^3`) by **`+12.36` to `+18.29` pp** over no-verifier evolution—surpassing even task-specific `Binary`, `Report`, and `Diagnostic` verifiers on overall `P@1` (`+0.76` to `+9.16` pp) and `Hit^3` (`+3.62` to `+16.10` pp), and lifting zero-shot transfer across `233` `SkillsBench` perturbations from `46.35%–49.36%` to **`61.37%–66.52%`**.

---

## Step-by-Step Procedure

### Step 1: Snapshot the Skill Package and Freeze Executable Scripts (`P`)

Represent the target skill package as `S = (P, M)`, where `P` is the set of bundled scripts, modules, or local tool wrappers and `M` is the natural-language `SKILL.md` guidance.

1. Mount or copy `P` as **read-only** for the entire revision cycle so the reviser cannot silently weaken assertions, hardcode task outputs, or break working utilities.
2. Compute a deterministic content hash (`SHA-256`) and line-numbered source listing for every inspectable file in `P`.
3. For Python or structured source files, build a lightweight **AST symbol index** enumerating CLI entrypoints (`argparse`/`click`/`typer` definitions, `__main__` blocks), public functions/classes, raised exception types, and file/environment I/O boundaries with inclusive `(start_line, end_line)` spans.

### Step 2: Extract Line-Verified Operational Knowledge Records (`K`)

Query the extractor model (`temperature = 0`) with the line-numbered source files and AST symbol index—**without** exposing any hidden evaluation tests—to produce at most **`12` workflow-level operational knowledge records**. Each record `k = (cap, cond, steps, limits, src)` captures one coherent operational contract:

```yaml
record_id: op_03
capability: "Convert multi-sheet workbook into normalized parquet tables"
preconditions:
  - "Input path must end in .xlsx or .xlsm; CSV inputs raise ValueError at L84"
  - "Requires --sheet-manifest JSON when workbook has >1 non-empty sheet"
ordered_steps:
  - "Run validate_workbook.py --check-merged before normalize_sheets.py"
  - "Pass --na-sentinel EXPLICIT to preserve literal 'NA' category codes"
failure_modes_and_limits:
  - "Silently drops trailing summary rows unless --keep-totals is set"
source_span:
  file: "scripts/normalize_sheets.py"
  start_line: 72
  end_line: 139
  sha256: "<verified_file_hash>"
```

Enforce **deterministic span verification** in host code before keeping any record: reject or re-prompt any record whose `file` does not exist in `P`, whose `start_line..end_line` falls outside file bounds, or whose attached code snippet does not match the exact lines of `P` under `sha256`.

### Step 3: Align Implementation Contracts (`K`) Against Current Guidance (`M`) and Trace (`\tau`)

Run (or collect) an unlabeled execution trace `\tau` of the agent attempting public task `x` with current skill `S = (P, M)`. Feed `(x, \tau, K, M)` into a workflow alignment step (`temperature = 0`) that outputs **`1` to `12` structured alignment rows** (`A`), classifying how each task-relevant record in `K` relates to `M` and `\tau`:

- **`COVERED`**: `M` already states the operational contract accurately and `\tau` followed it (or failed for an unrelated reason).
- **`ADD_OPERATION`**: `P` requires or supports a step/flag needed for `(x, \tau)` that `M` omits entirely.
- **`ADD_FALLBACK`**: `\tau` hit an exception, edge case, or empty-output branch handled in `P` whose recovery path is missing from `M`.
- **`CORRECT_OPERATION`**: `M` states flag names, argument formats, preconditions, or step ordering that contradict `P`.
- **`UNKNOWN`**: Insufficient implementation evidence in `P` to adjudicate the behavior.

From the non-`COVERED`, non-`UNKNOWN` rows, emit at most **`12` structured feedback items (`F`)** typed as either **`MISSING_GUIDANCE`** or **`CONFLICTING_GUIDANCE`**. Every item in `F` must cite:
1. Exact verbatim `request_quotes` from `x` or error/action spans from `\tau`,
2. Exact verbatim `skill_quotes` from `M` (for `CONFLICTING_GUIDANCE`) or the target section header of `M` (for `MISSING_GUIDANCE`), and
3. The verified `record_id` and `source_span` in `K`.

### Step 4: Apply Bounded Substring Patches (`M -> M'`) or `KEEP`

Pass `(M, A, F)` to the revision step under strict structural guards:

1. **Explicit no-op option**: If `F` is empty or all rows are `COVERED`/`UNKNOWN`, output `decision: KEEP` and leave `M` byte-identical.
2. **Bounded local edits**: Otherwise output `decision: REVISE` with **at most `4` non-overlapping exact-substring replacements** `(old_text -> new_text)`, each `<= 8,000` characters, targeting only the implicated sections of `M`.
3. **Anti-collapse checks**: Reject the candidate patch in host code if any `old_text` fails to match uniquely in `M`, if two replacements overlap, if `P` was modified, or if the edit wipes out all original non-blank text in `M` (preventing wholesale rewrite drift).
4. **Generalize beyond task literals**: Express added operations, preconditions, and fallbacks in terms of `P`'s general parameters and invariants rather than hardcoding entity names, file paths, or constants from `x`.

### Step 5: Gate Persistent Promotion

Treat `S' = (P, M')` as a candidate revision—not an automatic overwrite of your production skill library. Before promoting `S'` into persistent storage, evaluate it through the single acceptance gate in [`../../rules/recursive-improvement.md`](../../rules/recursive-improvement.md) (`"DO: Pass every self-modification through one acceptance gate"`): verify no regression beyond baseline noise margin `\delta` on previously-correct cases and held-out tasks, enforce strict zero tolerance on the negative security testbed, and scan updated markdown/tool pairs for injection or privilege drift ([`skill-evolution-defense`](../skill-evolution-defense/SKILL.md)).

---

## Environment Caveats

- **Consistency (`Hit^3`) gains exceed single-try discovery (`P@3`) gains**: Grounding `M` in `P` primarily converts brittle `1/3` or `2/3` intermittent successes into deterministic `3/3` execution (`67.0%` of solved tasks hit `3/3` under `VISE` vs. `40.4%` under `Report` on `SkillLearn`, where both tied at `61.58%` `P@3`), while still carrying non-zero regression risk (`3` to `14` previously `3/3` tasks dropped below `3/3` across the `4` evolution methods when unguarded)—making Step 5's held-out acceptance gate mandatory.
- **Scriptless or opaque-binary skills**: On tasks where `S` contains only markdown instructions calling standard shell utilities or remote REST APIs without local wrapper code, `K` will legitimately contain few or zero records; ensure Step 4 defaults cleanly to `KEEP` or defers to trace-checklist gating rather than hallucinating implementation rules.
- **Coupled multi-constraint perturbations (`P3`) remain hardest**: While `VISE`-revised skills transfer strongly to surface rephrasings (`P1`) and new instances (`P2`), coupled requirement changes (`P3` in `SkillsBench`) still require checking whether multiple `K` records interact (e.g., flag mutual exclusions across two scripts).
- **Token and latency budget**: Across `122` tasks in `arXiv:2611.32480`, the 4-stage pipeline averaged `41.62k–44.79k` input tokens, `1.70k–1.95k` output tokens, and `57.97–82.27 s` wall-clock latency per revision—run it offline or asynchronously between episodes rather than inside latency-critical user turns.

---

## Failure Modes

- **Bypassing `K` and feeding raw source files into the reviser (`Raw-Source Revision`)**: Dropping Steps 2–3 and pasting raw scripts alongside `(x, \tau, M)` caused the largest collapse in `VISE`'s `60`-task ablation (`P@1` **`57.78% -> 38.89%`, `-18.89 pp`**; `P@3` `-13.33 pp`; `Hit^3` **`30.00% -> 13.33%`, `-16.67 pp`**) because the editor copied low-level implementation trivia instead of workflow contracts.
- **Skipping quote-anchored structured feedback (`w/o Structured Feedback`)**: Revising directly from `K` and `A` without explicit `MISSING_GUIDANCE` / `CONFLICTING_GUIDANCE` items reduced `P@1` by **`-13.89 pp`** and `P@3` by **`-16.67 pp`** (`46/60 -> 36/60` solved tasks).
- **Skipping trace-conditioned workflow alignment (`w/o Workflow Alignment`)**: Comparing `K` to `M` statically without aligning against `(x, \tau)` dropped `P@1` by **`-10.56 pp`**, bloating `M` with unused script options irrelevant to real agent failure modes.
- **Allowing unconstrained full-file rewrites instead of `<= 4` substring edits (`w/o Workflow Revision`)**: Unbounded rewriting dropped `P@1` by **`-8.33 pp`** and `Hit^3` by **`-5.00 pp`** by phrasing away working instructions elsewhere in `M`.
- **Using noisy binary pass/fail labels without diagnostic localization**: On `Self-Refine`, adding a bare `Binary` task verifier actually *degraded* `P@1` below `No-verifier` (`39.16% -> 37.34%`, `Hit^3` `24.04% -> 21.86%`) because `"failed"` triggered destructive edits to already-correct steps.

---

## Cross-References

- **Rules**: [`../../rules/skill-system-design.md`](../../rules/skill-system-design.md) — Skill Evolution & operational know-how distillation; [`../../rules/recursive-improvement.md`](../../rules/recursive-improvement.md) — `"DO: Pass every self-modification through one acceptance gate"`
- **Spec Templates**: [`../../specs/skill-library.spec.md`](../../specs/skill-library.spec.md) — Skill authoring, knowledge persistence, and admission gate checklists
- **Related Skills & Briefs**:
  - [`regret-guided-continual-harness-evolution`](../regret-guided-continual-harness-evolution/SKILL.md) — Reference-free continual playbook evolution (`GUARD`) when tool source code is unavailable
  - [`anti-leakage-sparse-feedback-memory-distillation`](../anti-leakage-sparse-feedback-memory-distillation/SKILL.md) — Evaluator-anchored write routing and names-only/on-demand read-side memory injection under sparse pass/fail feedback (`ZhuLong-SE`)
  - [`dense-rubric-skill-evolution`](../dense-rubric-skill-evolution/SKILL.md) — Bilevel surrogate rubric optimization when labeled oracle demonstrations exist (`SkillLift`)
  - [`stable-skill-evolution`](../stable-skill-evolution/SKILL.md) — Momentum-stabilized multi-step skill updates (`SkillAdam`)
  - [`skill-evolution-defense`](../skill-evolution-defense/SKILL.md) — Provenance and injection auditing before admitting evolved skills
  - [`repo-to-skill-distillation`](../../research-briefs/repo-to-skill-distillation.md) — Initial repository-to-skill synthesis when no prior `SKILL.md` exists

---

## Sources

- Liu, Y., Du, C., Zhang, Y., Guo, J., Chung, K., Hu, W., Jing, H., Luo, H., Zong, Q., Shi, H., Li, H., & Song, Y. (2026). *VISE: Verifier-Independent Skill Self-Evolution with Feedback from Tool Implementations*. `arXiv:2611.32480` (`src:2611-32480v1`).
