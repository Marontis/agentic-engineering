---
name: anti-leakage-sparse-feedback-memory-distillation
description: >-
  Distill persistent API patterns and pitfalls from multi-turn coding traces
  under sparse pass/fail evaluation by overriding self-reported success with
  evaluator verdicts, separating contradiction from terminal-error reflection,
  and pre-injecting generalized API names while serving pitfalls on demand.
  Derived from ZhuLong-SE (arXiv:2611.26912).
source: "arXiv:2611.26912"
repository: "https://github.com/Marontis/agentic-engineering"
license: CC-BY-4.0
---

<!-- Licensed under CC BY 4.0 | Source: Marontis/agentic-engineering | Origin: arXiv:2611.26912 -->

# Anti-Leakage Sparse-Feedback Memory Distillation

## When to Use

Use this procedure when an autonomous coding, scripting, or tool-orchestration agent **evolves reusable API patterns, pitfalls, and higher-level skills across rounds from multi-turn sandbox traces where the external evaluator provides only a sparse binary pass/fail verdict** (no oracle reference code, line-level diff, or human annotations), and where retrieved memories risk either **memorizing task-specific call sequences** or **polluting prompts with distracting failure warnings**. Representative project types include:

- **Proprietary SDK, CAD/EDA, and bindings scripting agents**: Agents generating Python/Tcl/C++ automation scripts against large, sparsely documented C++/SWIG libraries (such as `PyAether` in `ZhuLong-SE`, `OpenROAD`, `Blender`, or `FreeCAD`) where silently wrong default arguments pass local syntax checks but fail downstream physical/functional assertions.
- **Enterprise API and SQL workflow agents with hidden test harnesses**: Multi-turn agents that write and self-test integration scripts inside a sandbox before a black-box CI gate returns only `PASS` or `FAIL`.
- **Scientific computing and simulation pipeline agents**: Agents composing domain library calls across training batches where training and held-out tasks share underlying APIs (`dbOpenCV`, solver setup, unit conversions) and naive trajectory retrieval leaks exact call recipes that misfire on new problem geometries.

**When NOT to use**:
- **Zero external pass/fail signal**: When not even a binary task verdict exists at evolution time, ground revisions in AST-indexed tool implementations ([`tool-implementation-grounded-skill-revision`](../tool-implementation-grounded-skill-revision/SKILL.md)) or Turn-0 checklist/sandbox regret ([`regret-guided-continual-harness-evolution`](../regret-guided-continual-harness-evolution/SKILL.md)).
- **Interactive counterfactual probing of stateful environment hypotheses**: When the agent can actively synthesize `3–5` targeted micro-experiments to falsify a behavioral belief about a mutable environment, pair or prefer [`falsification-gated-memory-evolution`](../falsification-gated-memory-evolution/SKILL.md).

---

## Core Insight

In multi-turn coding sandboxes with sparse binary pass/fail evaluation, naive experience distillation fails on **both the write side and the read side**:

1. **Write-side contamination**: Agents routinely pass their own weak sandbox self-tests (`exit 0`) and declare success in their final summary even when the hidden evaluator returns `FAIL`. Without overriding trace self-assessments using the external verdict, **`50%` (`12/24`) of failed traces in `ZhuLong-SE` (`arXiv:2611.26912`) produced falsely `verified` memory entries** (`37 -> 48` L1 entries). Equally damaging, if a trace fixed an early `TypeError` in Turn 2, passed its self-test in Turn 4, and then failed the hidden assertion, mining the whole trace for errors extracts `+17` **already-resolved stale sandbox tracebacks** (`37 -> 54` entries) instead of diagnosing the silent semantic bug.
2. **Read-side distraction and sequence copying**: At inference time, pre-injecting retrieved `pitfall` entries from task-description similarity **degraded validation pass rate by `-8.0 pp` (`88.0% -> 80.0%`)** because a task prompt predicts *which capability* is needed, not *which API will be misused*. Meanwhile, pre-injecting full concrete API call sequences (`-4.7 pp`, `88.0% -> 83.3%`) or ungeneralized task docstrings (`-6.3 pp`, `88.0% -> 81.7%`) induces brittle recipe copying on unseen tasks.

Combining **verdict-anchored dual-failure write routing** with **names-only upfront solution cues + on-demand error-keyed pitfall lookup** enabled `ZhuLong-SE` (`DeepSeek-V4-Pro-Preview` on `EDA-Eval-PyAether`: `98` train / `20` val / `40` instance-disjoint test tasks) to climb from **`66.0% ± 7.2%` (`Bare`) to `80.0% ± 3.1%` test (`+14.0 pp`) and `88.0% ± 2.7%` val** at Round 2 (`334` L1 patterns, `20` L2 skills)—**surpassing the `4`-skill human-crafted expert baseline (`77.5% ± 5.3%`) by `+2.5 pp`**—while its held-out rollback gate caught Round 3 over-accumulation (`88.0% -> 80.0%` val, `75.5%` test) and rolled back `52` noisy entries.

---

## Step-by-Step Procedure

### Step 1: Override Trace Self-Assessment and Route Write Reflection into Three Disjoint Paths

After each training episode completes with multi-turn trace $\tau$ and external binary verdict $y \in \{\mathrm{PASS}, \mathrm{FAIL}\}$, **discard the agent's own self-reported completion status** and route $\tau$ deterministically into one of three reflection extractors:

1. **Verified Success Path ($y = \mathrm{PASS}$)**: Extract reusable `solution_pattern` entries (`L1`) from the final working script only, marking provenance `status: verified`. Ignore intermediate exploratory dead ends unless they directly Contrast with the final fix.
2. **Terminal-Error Failure Path ($y = \mathrm{FAIL}$ AND final sandbox execution raised an exception/non-zero exit)**: Route **only the unresolved terminal traceback and surrounding API call** to a `pitfall` extractor (`status: unverified_pitfall`), recording `(api_symbol, exception_signature, root_cause, corrective_pattern)`.
3. **Silent-Contradiction Path ($y = \mathrm{FAIL}$ AND agent's final sandbox run / self-test succeeded)**: Route the final clean-running code **without intermediate solved tracebacks** to a dedicated semantic-contradiction prompt (*"The script executed without runtime errors and passed the agent's self-check, yet failed the external functional assertion—identify potentially misused API semantics, missing unit/coordinate conversions, silent default-argument traps, or unpersisted state commits"*). Stripping earlier solved tracebacks prevents polluting memory with `+17` false-alarm syntax pitfalls.

Across evolution batches, maintain a **disconfirmation counter** on unverified contradiction hypotheses: if an API pattern flagged as suspect subsequently appears unchanged inside `PASS` traces without triggering failures across `>= 2` batches, demote or prune the suspect entry.

### Step 2: Generalize Descriptions and Strip Concrete Call Sequences Before Indexing (`L1` & `L2`)

Before writing any `L1` (`solution_pattern` or `pitfall`) entry or consolidating `L1` clusters into `L2` subtask `SKILL.md` documents (`15–25` concise operational skills):

1. **Docstring/intent generalization**: Rewrite every task-specific problem statement into an **instance-agnostic functional intent** (removing benchmark task IDs, literal cell/table/file names, magic numbers, and domain fixture identifiers). Leaving literal task docstrings attached costs **`-6.3 pp`** (`88.0% -> 81.7%`) via spurious lexical matching.
2. **Index by solution capability / error signature, not problem wording**: Embed `solution_pattern` entries by their generalized capability summary and API identifiers (structural anti-leakage), and index `pitfall` entries by `(api_symbol, error_type, traceback_keywords)` plus a `camelCase` / snake_case / domain-abbreviation BM25 tokenizer (`+1.3 pp` over dense-only embeddings on specialized API vocabularies).
3. **Store stripped `api_names` separately from full code**: On every `solution_pattern`, persist a sanitized set of **canonical API/function names only** (`api_names: ["dbOpenCV", "dbCreateInst", "dbSaveDesign"]`), stripping call order, loop structure, and literal parameter values from the pre-injection payload.

### Step 3: Split Read-Side Retrieval into Upfront Names-Only Hints vs. On-Demand Error Lookup

During task execution, **never dump both solution sequences and pitfall warnings into the Turn-0 system prompt**. Separate read-side access by episode phase:

```
Turn 0 (Task Arrival)
  └── Query generalized L1 solution_patterns + L2 subtask skills by task intent
        ├── Inject concise L2 subtask workflow notes (natural language)
        └── Inject L1 solution_patterns as API NAMES ONLY (no call order, no literal args)
              └── Agent explores signatures via doc/help tools & writes script

Turn t > 0 (Runtime Sandbox Exception OR Static AST Check Alert)
  └── Query L1 pitfalls ON DEMAND using (api_symbol + traceback / AST warning)
        └── Inject top-k matching corrective pitfall notes into the repair turn only
```

- **Why names-only upfront works (`+4.7 pp` over full sequences)**: Providing the relevant function names narrows search over thousands of SDK bindings without tempting the model to copy a training task's exact call order or parameter constants onto a structurally different test task.
- **Why on-demand pitfalls work (`+8.0 pp` over Turn-0 pitfall pre-injection)**: Waiting until an actual runtime exception or deterministic static-checker warning fires ensures the injected pitfall matches the exact API the agent just misused, eliminating false-warning distraction on clean turns.
- **Pair with zero-false-positive AST static checks where recurring silent bugs exist**: For deterministic API invariants (e.g., SWIG iterator invalidation, missing file-close/save commits, forbidden flag combinations), encode an AST static checker verified for **`0` false positives** on known-good reference scripts (`+6.3 pp` standalone lift in `ZhuLong-SE`, `0/158` false flags).

### Step 4: Enforce Held-Out Rollback and Single-Gate Promotion Across Rounds

Memory accumulation under sparse feedback is **non-monotonic**: in `ZhuLong-SE`, expanding from Round 2 (`334` patterns, `20` skills) to Round 3 (`386` patterns, `25` skills) **degraded validation accuracy by `-8.0 pp` (`88.0% -> 80.0%`) and test accuracy by `-4.5 pp` (`80.0% -> 75.5%`)** as low-frequency, over-specialized patterns diluted retrieval precision.

1. Snapshot `(L1, L2)` before every distillation round.
2. Evaluate the updated memory state on a frozen, instance-disjoint validation split (multiple runs to estimate variance; `ZhuLong-SE` triggers automatic batch rollback of all newly added entries when held-out accuracy drops beyond tolerance).
3. Before promoting any evolved `(L1, L2)` snapshot as the new persistent baseline, pass it through the single acceptance gate in [`../../rules/recursive-improvement.md`](../../rules/recursive-improvement.md) (`"DO: Pass every self-modification through one acceptance gate"`): confirm no regression beyond noise margin $\delta$ on previously-correct and held-out tasks and strict zero failures on the negative security testbed.

---

## Environment Caveats

- **`AssertionError` dominance after syntax/API stabilization**: Even with full harness + memory support, `54.1%` of residual failures (`111` failed traces across `5` models in `ZhuLong-SE`) were semantic `AssertionError`s rather than import or syntax crashes—meaning Step 1's Silent-Contradiction Path becomes the primary source of learning signal once basic API discovery is solved, and also the noisier source that makes Step 4's rollback gate essential after `2–3` rounds.
- **Multi-batch requirement for disconfirmation filtering**: Single-round evolution cannot exercise cross-batch disconfirmation (`37 vs. 37` entries in `Table IV` of `arXiv:2611.26912`); schedule disconfirmation pruning only when running `>= 2` sequential training batches.
- **Domain identifier tokenization**: Dense text embedders split specialized identifiers (`dbGetNetByName`, `leSetLayerSelectable`) poorly; always combine dense embeddings with identifier-aware sub-token (`camelCase` / `snake_case` + domain acronym) BM25 matching.

---

## Failure Modes

- **Trusting agent self-reported success when writing memory (`Ground-Truth Anchoring Off`)**: Allowing traces where the agent's self-test passed to write `verified` patterns despite `y = FAIL` contaminated **`12/24` (`50%`)** of failed traces with broken patterns (`37 -> 48` L1 entries).
- **Mining intermediate tracebacks on silent-contradiction failures (`Contradiction Path Off`)**: Running standard traceback extraction on traces that ultimately ran cleanly but failed hidden assertions injected **`+17` stale, already-solved error entries** (`37 -> 54`).
- **Pre-injecting pitfalls at Turn 0 (`Pitfall Pre-Injection`)**: Retrieving pitfalls by task description and prepending them upfront caused the single largest read-side drop (**`-8.0 pp`**, `88.0% ± 2.7% -> 80.0% ± 5.0%`) due to defensive over-avoidance of valid APIs and prompt distraction.
- **Leaving raw problem docstrings ungeneralized (`Docstring Generalization Off`)**: Indexing memories under verbatim training task descriptions dropped validation pass rate by **`-6.3 pp` (`88.0% -> 81.7%`)**.
- **Pre-injecting full concrete call sequences (`Full-Sequence Injection`)**: Supplying ordered multi-call code templates instead of `api_names` alone dropped pass rate by **`-4.7 pp` (`88.0% -> 83.3%`)** via cross-task recipe copying.
- **Unbounded multi-round accumulation without rollback**: Continuing past Round 2 without held-out rollback degraded test pass rate from `80.0%` to `75.5%` as `52` marginal entries crowded retrieval.

---

## Cross-References

- **Rules**: [`../../rules/skill-system-design.md`](../../rules/skill-system-design.md) — Skill Evolution, operational know-how distillation, and library integrity; [`../../rules/recursive-improvement.md`](../../rules/recursive-improvement.md) — `"DO: Pass every self-modification through one acceptance gate"`
- **Spec Templates**: [`../../specs/skill-library.spec.md`](../../specs/skill-library.spec.md) — Knowledge persistence, retrieval scope, and admission gate checklists
- **Related Skills**:
  - [`knowledge-compounding-loop`](../knowledge-compounding-loop/SKILL.md) — Separating persistent knowledge layers from executable skills across rollbacks (`WikiSkill`)
  - [`falsification-gated-memory-evolution`](../falsification-gated-memory-evolution/SKILL.md) — Active counterfactual hypothesis falsification and online violation-EMA eviction (`FGSE`)
  - [`tool-implementation-grounded-skill-revision`](../tool-implementation-grounded-skill-revision/SKILL.md) — AST-indexed implementation grounding when tool source code is inspectable (`VISE`)
  - [`verifier-equivalent-comparative-update-vetting`](../verifier-equivalent-comparative-update-vetting/SKILL.md) — Pre-commit comparative safety vetting for candidate memory/skill updates (`DoppelVet`)
  - [`regret-guided-continual-harness-evolution`](../regret-guided-continual-harness-evolution/SKILL.md) — Signature-keyed continual playbook gating with `Soft-HURT` (`GUARD`)

---

## Sources

- Liu, Y., Tong, S., Chen, X., Hou, S., Yuan, S., Wang, H., Li, Y., Li, H., Zhu, Y., He, Z., & Yu, W. (2026). *Self-Evolving Beyond Human-Crafted Experience for EDA Scripting* (`ZhuLong-SE`). `arXiv:2611.26912` (`src:2611-26912v1`).
