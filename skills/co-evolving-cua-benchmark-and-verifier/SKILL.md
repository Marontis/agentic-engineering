---
name: co-evolving-cua-benchmark-and-verifier
description: >-
  Co-evolve computer-use, web-app, or multi-tool evaluation benchmarks and
  state-grounded atomic checkpoint verifiers from multi-agent rollout evidence.
  Use when static GUI/workflow benchmarks saturate or cover a small fraction of
  application features, when binary pass/fail masks partial progress and rank
  reversals, or when evolving tasks require lineage-preserving verifier updates
  without conflating step-limit censoring with capability failure.
---

# Co-Evolving Computer-Use Benchmark and Checkpoint Verifier (`CUA-SEE`)

> **Source**: *Self-Evolving Evaluation Environments for Computer-Use Agents*
> (`arXiv:2611.30962`, `CUA-SEE`). Validated across `20` `CanonicalState`
> desktop applications (`8` core `OSWorld` applications tracked across `R0 -> R4`
> over `100` task lineages $\times$ `5` agents = `2,500` paired observations
> under a `50`-step cap, plus `1,000` agent-conditional diagnostic profiles and
> `962` verifier-audited tasks / `400` human-audited trajectories).

## When to Use This Skill

Use this procedure when maintaining or expanding an interactive evaluation
environment across **3+ project types**—(1) desktop GUI and OS-level
computer-use benchmarks, (2) browser and full-stack web-application QA suites,
or (3) multi-tool IDE, CAD, or enterprise workflow evaluation harnesses—and you
observe any of the following bottlenecks:

- **Feature-space blind spots under static suites**: Fixed task pools test only
  a narrow slice of real application operations (`< 20%` of the software-feature
  taxonomy and `12.9%` of categories at `R0` in `OSWorld`) while saturating on
  common workflows (`77.6` macro-average score at `R0`).
- **Coarse binary grading & step-limit confounding**: Scalar `0/1` terminal
  verdicts hide partial multi-stage completion (`20–37` percentage-point per-app
  rank reversals across agents) and conflate genuine capability failure with
  step-budget censoring, environment resets, or ambiguous instructions.
- **Task–verifier drift during task evolution**: Rewriting tasks without
  updating state-grounded checks in lockstep either breaks valid solutions via
  stale assertions or falls back to unsound proxy checks (e.g., checking file
  existence instead of document structure or database rows).

Do **not** use this skill for one-shot static task grader generation without
iterative benchmark evolution (use
[`certified-task-verifier-harness`](../certified-task-verifier-harness/SKILL.md)),
or for purely perceptual, verifier-free creative domains where canonical backend
state cannot be inspected (use
[`constructed-exam-nash-evaluator-evolution`](../constructed-exam-nash-evaluator-evolution/SKILL.md)).
Whenever promoting evolved benchmark rounds, rubric schemas, or harness defaults
into persistent CI/production gates, pass the candidate update through
`"DO: Pass every self-modification through one acceptance gate"` in
[`recursive-improvement.md`](../../rules/recursive-improvement.md), and never
expose internal verifier scripts or unstated rubric predicates to task-solving
agents (`"DON'T: Expose benchmark verifier code or unstated rubric predicates to the skill-library learner"`).

---

## Core Architecture: Three Decoupled Evaluation Axes

Never collapse task generation, per-agent failure diagnosis, and grading into a
single unconstrained LLM rewrite loop. Separate the evaluation environment into
three distinct components that interact only through structured rollout traces
and canonical application state:

1. **Benchmark Evolution (`Scope` — Cohort-Calibrated)**: Advances a shared task
   registry across `<application, category, exact_operation>` cells using
   aligned multi-agent cohort replicates (`>= 3` diverse cohort-driving models)
   while holding out `>= 2` unseen evaluation models to verify that difficulty
   gains reflect genuine task complexity rather than single-model blind spots.
2. **Diagnostic Evolution (`Resolution` — Agent-Conditional)**: Adaptively
   brackets an individual target agent's capability boundary across **7
   orthogonal `0–5` demand axes** using bidirectional (upward *and* downward)
   probes and confound-deconfounding variants.
3. **Verifier Co-Evolution (`Precision` — Lineage-Preserving)**: Evolves an
   ordered checklist of atomic, weighted **CanonicalState** checkpoints via
   explicit `Keep / Modify / Remove / Add` edits, paired with explicit `Partial`
   observability declarations and isolated adversarial cross-audit.

---

## Step-by-Step Procedure

### Phase 1: Build the Feature Registry & `CanonicalState` Adapter Layer

1. **Index the application's feature taxonomy**:
   - Enumerate target operations hierarchically as
     `application -> functional_family -> category -> exact_operation` from
     official documentation, menus, CLI/API schemas, or DOM/file specifications.
   - Track two sets per round: `Current` (operations covered by active round
     tasks) and `Frontier` (cumulative distinct operations validated across all
     rounds).
2. **Implement read-only `CanonicalState` extractors per application**:
   - Before evolving any task, build deterministic state adapters that parse
     native post-run artifacts—document DOM/XML trees (`.docx`, `.xlsx`,
     `.pptx`), project databases/SQLite tables, configuration files, git/file
     manifests, canvas layer metadata, or headless export snapshots—into a
     normalized `CanonicalState` JSON object.
   - **Hard rule**: Never grade GUI or web workflows from agent self-reports or
     final screenshot pixels alone when underlying file, DOM, or database state
     exists (`"DON'T: Treat HTTP 200 / success tool return codes as workflow success without state verification"` in [`agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md)).
     Reserve bounded VLM/screenshot checks strictly for genuinely visual
     properties (e.g., layout overlap or rendering fidelity) that have no
     serialized state representation.

### Phase 2: Partition Multi-Agent Rollout Evidence Before Mutating Tasks

Run the current task pool $T^{(r)}$ across your **cohort-driving agent panel**
($M_{\mathrm{cohort}} \ge 3$ distinct model families) under a fixed step budget
$B$ (e.g., `50` steps), and evaluate your **held-out audit agents**
($M_{\mathrm{holdout}} \ge 2$) on the resulting round snapshots without letting
held-out traces influence task proposals.

1. **Classify every trajectory into four mutually exclusive evidence buckets**:
   - `Clean Pass` ($s = 1.0$, no environment/harness error).
   - `Clean Partial` ($0 < s < 1.0$, clean execution).
   - `Clean Fail` ($s = 0.0$, clean execution well inside step budget).
   - `Censored / Confounded` (hit the step cap $B$, triggered an infrastructure
     timeout/crash, encountered a broken initial fixture, or exposed an
     instruction-verifier mismatch).
2. **Enforce censoring & budget hygiene**:
   - **Never** treat `Censored` step-limit runs as evidence that a task's core
     operation is beyond cohort capability—long-horizon step exhaustion often
     reflects UI navigation friction or over-broad bundling rather than
     operation difficulty.
   - Reject or split any candidate task whose clean reference or cohort-passing
     trajectories consume **`> 0.85` of the step budget $B$** so evolved tasks
     do not degenerate into step-cap attrition tests.

### Phase 3: Execute Cohort-Calibrated Benchmark Evolution (`Scope`)

For each parent task lineage $i$, choose an evolution operator based on cohort
score distribution and feature-registry gaps:

1. **Select the lineage operator**:
   - **Cohort Saturation (`high mean score, low spread`)**: Apply controlled
     *Compositional Extension* or *Constraint Tightening*—introduce `1–2`
     under-covered `<category, exact_operation>` leaves from the feature
     registry that compose naturally with the parent workflow, while preserving
     the parent task's core domain context (**lineage anchor preservation**).
   - **Informative Frontier (`intermediate mean score or high inter-agent spread`, maximizing boundary informativeness $I^{(r)}$)**: Retain or apply minor
     parameter/fixture diversification so discriminative boundary signal is not
     destroyed by runaway hardening.
   - **Cohort Collapse (`near-zero clean score across all cohort models`)**:
     Inspect whether failure stems from `Confounded` setup/instruction ambiguity
     vs. genuine over-coupling; repair fixture/instruction defects or step back
     one compositional hop rather than stacking harder clauses onto an unsolved
     lineage.
2. **Verify solvability & non-leakage**:
   - Ensure every task instruction states all user-facing requirements
     explicitly (no hidden conventions that only a reader of the verifier could
     guess) and initializes deterministic starting fixtures.

### Phase 4: Run Agent-Conditional Diagnostic Bracketing (`Resolution`)

When profiling a specific model checkpoint or agent harness to localize *why* it
fails (rather than ranking a public leaderboard), do **not** run monotonic
difficulty escalation. Instead, bracket its capability profile across **7
orthogonal `0–5` demand dimensions**:

1. **Score each task along the 7D demand rubric (`0–5` per axis)**:
   - `Scale Consistency`: Maintaining accuracy across repeated items, rows,
     slides, or batch entities without mid-batch drift.
   - `Precision Control`: Exact numeric, coordinate, formatting, or schema
     parameter adherence.
   - `Target Grounding`: Disambiguating visually or lexically similar UI
     controls, files, or DOM nodes.
   - `State Reasoning`: Inferring hidden/intermediate application state transitions
     before acting.
   - `Procedure Following`: Executing ordered multi-stage dependencies and
     precondition sequences.
   - `Feature Integration`: Combining multiple distinct application tools or
     cross-app handoffs in one workflow.
   - `Verification & Control`: Self-checking intermediate outcomes, undoing
     mistakes, and halting cleanly without destructive side effects.
2. **Apply bidirectional intensity probes + deconfounding**:
   - **Upward probe**: When the agent cleanly passes a cell at demand level $d$,
     probe $d + 1$ on **one** targeted axis while holding the other six axes as
     constant as possible.
   - **Downward / deconfounding probe**: When the agent fails a multi-demand
     task, generate a **downward or deconfounded sibling** that lowers an
     ancillary axis (e.g., reducing batch `Scale Consistency` from `10` items to
     `2`, or simplifying `Target Grounding` clutter) to isolate which specific
     axis caused the breakdown.

### Phase 5: Co-Evolve Lineage-Preserving `CanonicalState` Checkpoints (`Precision`)

Every time a parent task $T^{(r-1)}$ mutates into $T^{(r)}$, update its verifier
$V^{(r-1)} \to V^{(r)}$ via differential checkpoint editing rather than
regenerating a monolithic script from scratch:

1. **Apply explicit `Keep / Modify / Remove / Add` atomic checkpoint deltas**:
   - `Keep`: Preserve verified checkpoints for unchanged lineage anchor
     requirements verbatim so cross-round score trajectories remain comparable.
   - `Modify`: Update expected target values or selectors where an existing
     requirement's parameter changed.
   - `Remove`: Delete checkpoints tied to clauses intentionally dropped during
     downward/deconfounding edits.
   - `Add`: Append new atomic predicates over `CanonicalState` for newly
     introduced `<category, exact_operation>` requirements, assigning continuous
     weights $w_k > 0$ ($\sum_k w_k = 1$; typically `4–6` atomic checkpoints per
     task; `4.82` mean in `CUA-SEE`).
2. **Declare observability status explicitly (`Full` vs. `Partial` — Never Fake Coverage)**:
   - Map every atomic instruction clause to a concrete `CanonicalState`
     predicate.
   - If an application exposes no deterministic artifact for a specific clause,
     mark that requirement's verifier coverage as **`Partial` observability** in
     task metadata and flag it for bounded secondary inspection—**never**
     substitute a vacuous proxy check (such as `os.path.exists(output_file)` or
     non-empty byte size) and label the task fully verified.
3. **Run isolated `PASS`-Agent vs. `Verifier`-Agent Adversarial Cross-Audit**:
   - Instantiate two layout-isolated audit roles with **zero shared chain of
     thought**:
     1. **`PASS`-Agent (False-Negative / Over-Constraint Probe)**: Constructs or
        simulates minimal legitimate alternative paths that satisfy the natural-language
        task instruction (e.g., equivalent formula forms, style inheritance vs.
        inline attributes, valid row orderings) and flags checkpoints that
        falsely reject compliant end states.
     2. **`Verifier`-Agent (False-Positive / Shortcut Probe)**: Constructs
        degenerate or partial state mutations (e.g., untouched initial fixture,
        wrong-sheet edit, surface text match without structural transformation)
        and flags checkpoints that award credit without genuine requirement
        fulfillment.
   - Admit $(T^{(r)}, V^{(r)})$ into the active suite only when initial-state
     preflight scores `0.0`, valid reference state scores `1.0`, atomic clause
     alignment clears your coverage floor (`>= 85%–90%`), and held-out audit
     agents track cohort difficulty trends without anomalous single-family spikes.

---

## Quantified Reference Benchmarks (`arXiv:2611.30962`)

Use these empirical baselines from `CUA-SEE` when sizing evolution rounds and
auditing suite health:

| Metric | Static Baseline (`R0`) | Round 1 (`R1` `CanonicalState`) | Round 4 (`R4` Evolved) | Operational Takeaway |
|:---|:---|:---|:---|:---|
| **Exact Software Operations Covered** | `127` | `219` (`Current`) | `464` (`Current`, `3.65x` `R0`; `487` `Frontier`) | Feature-guided evolution expands exercised operations `3.65x` |
| **Taxonomy Category / Family Share** | `12.9%` / `38.0%` | `18.6%` / `45.6%` | `27.5%` / `53.8%` (`100%` of `35` demand cells by `R2`) | Static benchmarks leave `>80%` of application categories untested |
| **5-Agent Macro-Average Score** | `77.6` (`19.5` mean steps) | `60.6` (`27.4` mean steps) | `47.5` (`39.3` mean steps; `13%–19%` binary full pass) | *Note*: Abstract/Intro quote `R1 -> R4` (`60.6 -> 47.5`, `27.4 -> 39.3` steps); `R0 -> R4` drops `77.6 -> 47.5` |
| **Held-Out Agent Generalization (`R0 -> R4`)** | `Qwen-3.7-Plus`: `73.0`; `GPT-5.5`: `68.0` | `58.2` / `55.4` | `46.1` (`-26.9`) / `44.0` (`-24.0`) | Held-out models track cohort difficulty drops without driving evolution |
| **Boundary Informativeness ($I^{(r)}$)** | Binary grading masks spread | Continuous checkpoints: `+20.8` pp lift to `69.7` | Exposes `20–37` pp per-app rank reversals | Continuous atomic checkpoints surface app-specific strengths hidden by binary means |
| **Verifier Precision (`962` tasks / `400` human-audited runs)** | Legacy hand-written scripts | `4.82` checkpoints/task (`92.5%` atomic req. coverage) | `84.0%` binary human agreement ($\kappa = 0.640$; rises `81% -> 89%` across rounds) | Lineage-preserving `CanonicalState` edits improve human alignment as tasks grow complex |

---

## Failure Modes & Guardrails

1. **Single-model evolution overfitting**: Evolving tasks solely from one target
   model's failures turns the benchmark into an adversarial trap for that
   model's UI quirks while becoming easier or noisy for other families. *Fix*:
   Drive `Benchmark Scope` evolution only from multi-family cohort statistics
   and track `>= 2` strictly held-out models every round; keep single-agent
   bracketing isolated in the `Diagnostic` track.
2. **Step-cap attrition masquerading as task difficulty**: Packing `8+`
   unrelated sub-goals into a `50`-step episode drives pass rates to `0%` via
   timeout censoring rather than reasoning failure. *Fix*: Separate `Censored`
   runs prior to scoring and enforce the `<= 0.85 * B` clean-step ceiling.
3. **Silent proxy-check soundness collapse**: When an LLM verifier generator
   cannot parse a binary/proprietary file format, it frequently falls back to
   checking file mtime, file size, or agent terminal stdout. *Fix*: Restrict
   generated checkpoints to registered `CanonicalState` adapter fields and force
   explicit `Partial` observability tags whenever an adapter field is missing.
4. **Verifier criteria leakage into agent memory/skills**: Letting a
   self-improving CUA inspect checkpoint definitions inflates apparent scores by
   `+20` to `+26` pp without real task transfer (`arXiv:2611.08318`). *Fix*:
   Execute `CanonicalState` extraction and checkpoint scoring strictly post-exit
   inside an isolated grading container unreachable from the agent sandbox.

## Related Artifacts

- [`certified-task-verifier-harness`](../certified-task-verifier-harness/SKILL.md) — Five-gate (`G1–G5`) soundness certification for static task-verifier synthesis (`Veritas`, `arXiv:2611.13336`)
- [`constructed-exam-nash-evaluator-evolution`](../constructed-exam-nash-evaluator-evolution/SKILL.md) — Verifier-free evaluator evolution via constructed directional exams (`EVA-RSI`, `arXiv:2611.23890`)
- [`agent-data-mutual-evolution`](../agent-data-mutual-evolution/SKILL.md) — Failure-driven MCP tool-use task synthesis (`EvoMCP`, `arXiv:2610.41479`)
- [`persona-driven-mobile-feature-testing`](../persona-driven-mobile-feature-testing/SKILL.md) — Static-seeded forced exploration and persona-driven mobile feature coverage (`ECS`, `arXiv:2611.06922`)
- [`agent-evaluation-quality.md`](../../rules/agent-evaluation-quality.md) — Benchmark design, atomic checklist decomposition, and trajectory verification guardrails
- [`recursive-improvement.md`](../../rules/recursive-improvement.md) — Single acceptance gate and anti-criteria-exposure invariants
