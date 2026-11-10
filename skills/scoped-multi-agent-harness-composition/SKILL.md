---
name: scoped-multi-agent-harness-composition
description: >
  Adapt multi-agent harnesses across closed-loop campaigns, coding, and
  interactive API workflows by decoupling a provenance-typed shared evidence
  graph from three isolated editors (role procedures, handoff coordination, and
  memory policy) followed by isolated public probing and tested-component
  composition. Derived from SciMARS (arXiv:2611.12552).
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Scoped Multi-Agent Harness Composition

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

Use this skill when evolving a **multi-agent execution harness** across iterative tasks — such as closed-loop experimental/simulation campaigns, multi-step data-science and software engineering pipelines, or interactive API/application workflows — where two coupled failure modes limit a static multi-agent team:

1. **Cross-role amnesia**: Without structured shared state, specialist roles (`analyzer`, `planner`, `coder`, `verifier`, `router`, `debugger`, `finalizer`) lose intermediate observations, contradict verified constraints, or repeat failed work.
2. **Entangled monolithic workflow edits**: Revising role instructions, inter-agent handoffs, and memory read/write behaviors inside a single monolithic prompt/workflow proposal confounds credit assignment, breaks downstream output contracts (such as a finalizer overwriting a verified artifact), or corrupts stored evidence.

**Deference to the repository acceptance gate:** In-round `public_probe` checks and current-round/archive selection inside this procedure are **search-time harness adaptation** over public task inputs $D$. Whenever a composed or selected harness is retained beyond a single sandboxed episode, committed to a repository, or promoted as a new baseline, it **must** pass `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../../rules/recursive-improvement.md): no regression beyond a baseline noise margin $\delta$ estimated from repeated runs ($\ge 3$) of the unchanged team, behavioral trajectory confirmation that the targeted role/handoff/memory mechanism changed, evaluation on held-out tasks never seen by the editors, and strict zero-tolerance enforcement on the immutable negative security testbed.

---

## Step-by-Step Procedure

### Step 1: Decouple the Evidence Graph $G_t$ from the Editable Harness $H_t = (P_t, C_t, M_t)$

Separate **what the team has observed** from **how the team operates**:

1. **Shared Evidence Graph $G_t$ (data plane, append/provenance-governed)**:
   - Partition records into 6 typed namespaces: `context` (task specs, schemas, environment facts), `work` (hypotheses, plans, candidate artifacts), `decisions` (verifier verdicts, routing choices), `status` (campaign budget, open blockers), `procedures` (reusable generic lessons), and `log` (timestamped execution events).
   - Link nodes exclusively with 4 typed provenance edges: `support`, `contradiction`, `derivation`, and `dependency`.
   - Enforce **immutability on raw observations and dataset/assay records**: neither execution agents nor outer harness editors may rewrite or delete acquired experimental observations or task inputs.
2. **Editable Harness Triple $H_t = (P_t, C_t, M_t)$ (control plane)**:
   - **Role procedures $P_t$**: Per-role operational instructions for the active logical roles (`analyzer`, `planner`, `coder`, `verifier`, `router`, `debugger`, `finalizer` — mapped onto either separate agents or a compact worker-reviewer pair).
   - **Coordination contracts $C_t$**: Handoff routing rules and required schema/artifact invariants across role interfaces (`analyzer-planner`, `planner-coder`, `coder-verifier`, `verifier-router`, `router-planner`, `verifier-planner`, `verifier-finalizer`, `coder-finalizer`).
   - **Memory policy $M_t = \{(w_{t,r}, q_{t,r}, s_{t,r})\}$**: For each role $r$, its recording duties $w_{t,r}$ (which namespaces/artifacts it must write), retrieval query filters/hints/limits $q_{t,r}$ (hard-bounded to `0..12` records per call, default $\le 6$), and event subscriptions $s_{t,r}$.

### Step 2: Propose Isolated Component Edits via Three Non-Communicating Editors

After executing the reference harness $H_t$ to produce trace $\tau_t$ (exposing public execution outputs, verifier logs, and graph events, **never** the official evaluator $V$ or hidden grading targets), invoke up to **three independent editors in parallel** with zero cross-editor communication:

1. **Role Editor** $\to H_t^P = (P_t', C_t, M_t)$:
   - Diagnoses role-local execution mistakes in $\tau_t$ (e.g., coder skipping edge-case checks, finalizer regenerating instead of copying a verified file) and edits $P_t \to P_t'$ while keeping $C_t$ and $M_t$ byte-identical.
2. **Coordination Editor** $\to H_t^C = (P_t, C_t', M_t)$:
   - Diagnoses handoff or contract mismatches in $\tau_t$ and modifies **at most one** interface route or handoff contract in $C_t \to C_t'$ (for example, tightening `verifier-finalizer` so finalization requires a matching artifact hash from verification) while keeping $P_t$ and $M_t$ frozen.
3. **Memory-Policy Editor** $\to H_t^M = (P_t, C_t, M_t')$:
   - Diagnoses missing context, duplicate work, or retrieval overload in $\tau_t$ and updates $(w_{t,r}, q_{t,r}, s_{t,r})$ (respecting the `0..12` retrieval cap) while incrementing `memory.version`.
   - **Hard scope boundary**: Reject any memory-policy proposal that directly inserts/edits records in $G_t$, alters provenance edge rules, or touches $P_t$ or $C_t$.

Deterministically diff and schema-check each proposal before execution; discard any branch that violates its component freeze or cardinality bound.

### Step 3: Execute Isolated Public Probes (`public_probe`)

Run each valid scoped candidate ($H_t^P$, $H_t^C$, $H_t^M$) in an **isolated sandbox workspace** against public task inputs $D$ (e.g., public assertions, schema/non-zero output checks, replayable public observations, or a public validation panel):
- Never invoke the sealed benchmark grader $V$ or leak probe side-effects into live campaign data.
- Record a structured execution receipt capturing runnable status, artifact hashes, verifier outcomes, public check metrics, and resource usage.

### Step 4: Compose Under the Strict Tested-Component Invariant

Invoke the **Composer** on the reference outcome and the scoped probe receipts to synthesize a successor candidate $H_t^S = (P_t^S, C_t^S, M_t^S)$ subject to strict structural constraints:

1. **No untested coordination or memory policies**: Enforce $C_t^S \in \{C_t, C_t'\}$ and $M_t^S \in \{M_t, M_t'\}$. The composer may adopt a coordination or memory edit **only** if that exact component was already validated in its dedicated probe; it may never invent a novel third coordination rule or memory policy during composition.
2. **Compatible role merging**: $P_t^S$ may retain $P_t$, adopt $P_t'$, or merge non-conflicting role-level repairs from $P_t'$ that remain compatible with the chosen $C_t^S$ and $M_t^S$.
3. **Exact-match probe reuse**: Reuse an existing same-round probe receipt for $H_t^S$ **if and only if** the complete triple $(P_t^S, C_t^S, M_t^S)$ matches an already-probed candidate (`H_t`, `H_t^P`, `H_t^C`, or `H_t^M`). Otherwise, run a fresh isolated `public_probe` on $H_t^S$ (meaning a full `SciMARS + Memory` round uses 4 team executions when reusing a branch and 5 when probing a new composite).

### Step 5: Execute Bounded Selection and Task-Free Reflection

1. **Build the runnable candidate pool**:
   $$\mathcal{Q}_t = \operatorname{Unique}\bigl\{(H_t^j, o_t^j) : j \in \{0, P, C, M, S\},\; o_t^j \text{ is runnable}\bigr\}$$
   The selector is **not** forced to pick the composite $H_t^S$; if an isolated role or coordination fix outperformed the composite on public checks, retain that single-component candidate.
2. **Require execution-backed selection**: Allow the selector bounded inspection (e.g., up to 3 structured `public_probe` checks and 3 public output reads) and **require at least one executed structured check** before switching away from the incumbent. On ties, missing checks, or tool/budget timeouts, fall back deterministically to the reference harness $H_t$.
3. **Extract task-free generic lessons**: Run a **Reflector** over the round's proposal, probe, and selection records to write at most one grounded procedural lesson (cue, procedure, cited trace events, limitations) into `procedures` — **stripping all task IDs, filenames, dataset names, target literals, and grading thresholds** so lessons never leak instance-specific shortcuts. Reset task-local adaptation state at task boundaries, and pass any harness promoted across tasks through `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../../rules/recursive-improvement.md).

---

## Verified Empirical Reference (`SciMARS`, `arXiv:2611.12552`)

All methods within each benchmark and model cohort share an **identical total model/API allowance** (charging execution, editors, probes, selection, reflection, and retries to the same budget):

| Benchmark & Setting | Base Multi-Agent | Multi-Agent + Memory | Integrated Search (`MASS-RHI`) | `SciMARS` ($P, C$) | `SciMARS + Memory` ($P, C, M$) |
|:--------------------|:----------------:|:--------------------:|:------------------------------:|:------------------:|:------------------------------:|
| **`Autonomous Science Bench`** (`GPT-6-Astra`, 6 campaigns $\times$ 3 runs) | `8/18` (`6` MD, `4` ML) | `9/18` (`4` MD, `5` ML) | `10/18` (`5` MD, `3` ML) | `10/18` (`4` MD, `4` ML) | **`12/18`** (`3` MD, `3` ML, `0` MB) |
| **`Autonomous Science Bench`** (`GLM-5.3`, 6 campaigns $\times$ 3 runs) | `1/18` (`11` MB, `4` inc.) | `1/18` (`10` MB, `3` inc.) | `1/18` (`9` MB, `4` inc.) | `2/18` (`9` MB, `3` inc.) | **`2/18`** (`4` MD, `2` ML, `7` MB, `3` inc.) |
| **`ScienceAgentBench`** (`glm-5.3-flashx`, 38 machine-graded tasks) | `11/38` (`28.9%`) | `11/38` (`28.9%`) | `11/38` (`28.9%`) | `13/38` (`34.2%`) | **`14/38` (`36.8%`)** |
| **`AppWorld`** (`glm-5.3-flashx`, 10 Music + 10 Finance tasks) | `5/20` (`5/10` M, `0/10` F) | `6/20` (`6/10` M, `0/10` F) | `8/20` (`5/10` M, `3/10` F) | `10/20` (`6/10` M, `4/10` F) | **`11/20`** (`7/10` M, `4/10` F) |

- **Why static shared memory alone is not enough**: Adding a shared evidence graph with a fixed memory policy (`Multi-Agent + Memory`) barely moves `ScienceAgentBench` (`11/38` vs `11/38`) and `AppWorld` (`6/20` vs `5/20`, `0/10` on Finance), whereas co-adapting $P, C, M$ reaches **`14/38` (`36.8%`)** and **`11/20` (`4/10` Finance)**.
- **Concrete failure isolation (`ScienceAgentBench` Task 11, `BBBC002` cell counting, pass threshold $\mathrm{MAE} \le 30$)**: In the reference run, the coder trained a model with `0.997` training PCC and the verifier approved `"Yes"`, yet the `finalizer` overwrote the submission CSV with `0/10` nonzero predictions ($\mathrm{MAE} = 78.00$, fail). Both scoped branches independently repaired the failure — the Role editor constrained `finalizer` to preserve verified output hashes (`10/10` nonzero, $\mathrm{MAE} = 6.17$), and the Coordination editor tightened the `verifier-finalizer` contract (`10/10` nonzero, $\mathrm{MAE} = 11.80$) — without disturbing upstream analysis or coding roles.

---

## Environment Caveats

- **Execution multiplier per outer round**: One `SciMARS` round consumes 3–4 full team executions, and `SciMARS + Memory` consumes 4–5 team executions (plus editor/reflector calls). Allocate outer rounds conservatively (e.g., 2 outer rounds) and enforce a prefix budget rule so probe overruns cannot starve final task execution; when base model capability is too low for 60-minute multi-batch campaigns (`GLM-5.3` on `Autonomous Science Bench`, `2/18`), harness adaptation narrows dual-gate failures (`11` MB $\to$ `7` MB) but cannot substitute for base model competence.
- **Replay vs physical wet-lab**: `Autonomous Science Bench` validates discovery and held-out learning gates via experimental-data replay and digital twins rather than physical wet-lab synthesis; when interfacing with irreversible real-world actuators or wet labs, gate live experimental batches separately from simulated `public_probe` workspaces.

## Failure Modes to Avoid

1. **Letting the Composer synthesize untested coordination or memory edits**: Allowing the composer to "compromise" between $C_t$ and $C_t'$ by inventing a new third handoff contract bypasses isolated probing and reintroduces monolithic workflow regressions. Enforce $C_t^S \in \{C_t, C_t'\}$ and $M_t^S \in \{M_t, M_t'\}$ in code.
2. **Allowing the Memory-Policy Editor to mutate $G_t$ directly**: The memory editor may only adjust write duties $w_{t,r}$, bounded read filters $q_{t,r} \in [0, 12]$, and subscriptions $s_{t,r}$ — never fabricate observations, delete contradictions, or alter provenance edge types.
3. **Editing multiple coordination interfaces at once**: Changing two or more handoff routes in a single coordination proposal creates deadlocks or orphaned roles (`verifier-router` vs `verifier-finalizer`); enforce the single-route/contract cap per round.
4. **Leaking benchmark answers or filenames into reflected `procedures`**: Unsanitized reflections overfit to specific CSV column names or thresholds; strip literals and reset task-local harness edits between evaluation tasks unless validated through [`online-fer-statistical-acceptance`](../online-fer-statistical-acceptance/SKILL.md) and `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../../rules/recursive-improvement.md).

## Related Skills

- [`mcts-full-harness-optimization`](../mcts-full-harness-optimization/SKILL.md) — MCTS search over multi-file single-agent harnesses and bitemporal memory gating (`arXiv:2611.06254`)
- [`coordinator-executor-prompt-optimization`](../coordinator-executor-prompt-optimization/SKILL.md) — Prompt optimization across coordinator-executor hierarchies (`arXiv:2610.34722`)
- [`governed-knowledge-graph`](../governed-knowledge-graph/SKILL.md) — Provenance and admission governance for shared multi-agent knowledge graphs (`arXiv:2608.28642`)
- [`targeted-failure-attribution`](../targeted-failure-attribution/SKILL.md) — Pinpointing decisive error agents before reflection (`arXiv:2608.28264`)
- [`online-fer-statistical-acceptance`](../online-fer-statistical-acceptance/SKILL.md) — Statistical FER control when promoting harness edits across multi-task rounds (`arXiv:2611.10787`)
