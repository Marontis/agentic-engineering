---
name: ui-dataflow-intent-verification
description: >
  Detect silent behavioral and dataflow bugs in vibe-coded web applications by
  compiling interface-grounded action-conditioned probabilistic constraints
  into deterministic static analysis queries (CodeQL). Verifies all-paths UI
  writes, dataflow sources, API reachability, storage persistence, and handler
  exclusivity without relying on LLM code review. Derived from FlowCheck
  (arXiv:2608.28880).
source: https://arxiv.org/abs/2608.28880
license: CC-BY-4.0
repository: https://github.com/Marontis/agentic-engineering
---

# UI Dataflow Intent Verification

> **Source**: [FlowCheck: Helping End-Users Specify and Verify Intent in Vibe-Coded Web Apps](https://arxiv.org/abs/2608.28880) (Vir et al., 2026)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

- Verifying functional correctness and user intent in AI-generated ("vibe-coded") web applications where the UI compiles, renders cleanly, and displays plausible visual feedback (such as toast notifications), but silently drops dataflows, state updates, or storage persistence.
- Auditing iterative modifications in multi-turn coding sessions where adding a feature or refactoring silently breaks previously working event handlers or conditional branches.
- Replacing ungrounded LLM self-review of frontend code with deterministic static dataflow and control-flow verification.

---

## Core Concepts

### Silent Behavioral Failures in Vibe-Coded Web Apps

A formative study across **4 web applications**, **3 generation systems** (`Claude Opus 4.7`, `DeepSeek V3`, `Lovable`), and **4 iterative development stages** (initial generation, feature addition, refactoring, modification) identified **23 distinct silent behavioral failures** across five categories:
1. **Surface-level correctness**: A button handler displays `"Discount applied!"` or `"Saved!"` while never updating the cart total or writing to storage.
2. **Dropped constraints across iterations**: A constraint satisfied in Turn 1 is silently deleted from one branch of an event handler in Turn 3.
3. **Missing implied functionality**: Adding an item updates a list widget but fails to increment the header badge counter or persist across reloads.
4. **Breaking changes after modification**: Refactoring a shared state object severs dataflow from an input field to an API payload.
5. **Incomplete persistence**: A handler calls `localStorage.setItem(key, val)` on click, but the page-load initializer never calls `getItem(key)` to restore the state.

Of these 23 real-world failures, **11 (48%)** are 100% expressible and verifiable via static UI data/control-flow constraints without running dynamic test suites (and across 34 broader web-app constraint cases, **29 of 34 [85%]** are statically checkable: 21 fully, 8 partially).

### Why Prompting LLMs to Review Code Fails (The Rationalization Trap)

Asking frontier LLMs (`Claude Opus 4.7`, `DeepSeek V3`, `Gemini Pro`) to directly audit web app code for behavioral bugs misses **at least 13% of injected violations** (catching at most **26/30 [87%]** even under the best model-prompt pair), particularly **universal path bugs** (where 3 of 4 branches in a handler write to a target UI element, but 1 branch forgets) and **cross-handler dataflow bugs**.

Worse, **increasing prompt detail and providing explicit bug taxonomies (`P3`) causes LLMs to rationalize bugs as intentional design choices**. For example, when inspecting a dead or broken conditional branch, LLMs conclude `"USER_TIER is a const initialized to 'free', so the enterprise branch is dead code, not a defect"` or `"qty is clamped to >= 1, so the qty=0 path is unreachable; not a bug"`. However, when the same LLMs are instead asked to **author formal interface-grounded constraints** that are compiled into static CodeQL queries, their bug detection rate increases across every model while eliminating rationalization.

---

## Step-by-Step Procedure

### Step 1: Preprocess HTML and JavaScript with Static Element Identifiers

Before specifying or checking constraints, establish deterministic bidirectional links between rendered DOM nodes and JavaScript AST references:

1. **Assign canonical static IDs (`cv_nnnn`)**: Parse the HTML templates (using a DOM parser such as BeautifulSoup) and scan JavaScript files (matching `document.createElement` and dynamic template literals) to inject a unique static identifier `cv_nnnn` into every selectable or interactive UI element.
2. **Map event handlers and state sinks**: Bind each `cv_nnnn` element to its registered event listeners (`onclick`, `addEventListener`), DOM read/write references (`getElementById`, `querySelector`, `.textContent`, `.value`, `.innerHTML`), browser storage keys (`localStorage`, `sessionStorage`), and network API calls (`fetch`, `XMLHttpRequest`).

### Step 2: Specify Intent in the Interface-Grounded Probabilistic Grammar

Express user or agent requirements as action-conditioned probabilistic constraints of the form:
$$P(\text{Event} \mid \text{Condition}) = p, \quad p \in \{0, 1\}$$

1. **Formulate the Condition (Right-Hand Side of $\mid$)**:
   - Specify a single user or system action `A(id)` referencing a grounded UI element (e.g., clicking `A(apply_btn)`).
   - Optionally attach a value guard (`expr cmp expr` or `expr in [min, max]`, such as `A(checkout_btn) AND r(cart_total) > 0`) or negate the action `NOT A(id)` to assert **handler exclusivity** (no handler *other* than `A(id)` may write to the target element).
2. **Formulate the Event (Left-Hand Side of $\mid$)**:
   - Combine atomic UI/storage/API effects using Boolean operators (`AND`, `OR`, `XOR`, `NOT`):
     - `w(id)`: **Unconditional UI write** — every execution path through the action's handler must write to element `id`.
     - `w(id, expr)` or `w(id, sources={r(a), r(b)})`: **Dataflow-verified write** — the value written to `id` must statically derive via dataflow from the read values `r(a), r(b)` or match expression `expr` (such as self-increment `w(id, r(id) + 1)` or API taint flow `w(id, r(api_result))`).
     - `call(api)` or `call(api, expr)`: **API reachability and payload flow** — the handler invokes `api` and passes arguments tainted by `expr`.
     - `persist(storageKey)`: **Round-trip storage persistence** — the action handler writes to `storageKey` AND the application's page-load initialization path reads `getItem(storageKey)` to restore state.
3. **Set the target probability $p \in \{0, 1\}$**:
   - Use $p = 1$ for **must-occur invariants** (the effect must hold across *all* feasible control-flow paths when the condition holds).
   - Use $p = 0$ for **prohibition invariants** (the effect must be unreachable on *every* control-flow path when the condition holds).

### Step 3: Validate Constraint AST Semantics Before Compilation

Parse every proposed constraint (e.g., via an ANTLR4 grammar) and enforce four strict AST semantic validation rules before generating static queries (filtering out malformed LLM-generated constraints, which occur in 0–66% of raw agent proposals depending on model):

1. **Identifier grounding check**: Every referenced element `id`, `storageKey`, or `api` endpoint must resolve to an existing entity in the preprocessed DOM/JS symbol table.
2. **Single-action condition check**: The condition clause must contain exactly one triggering action `A(e_i)` (with optional guards or negation).
3. **Effect-only event check**: The event clause must contain only effect atoms (`w`, `call`, `persist`)—never user actions `A(...)` or bare guard predicates.
4. **Binary probability check**: The target probability $p$ must be strictly `0` or `1`.

### Step 4: Compile Validated Constraints into 11 Primitive Static Queries

Deterministically compile each validated AST into a conjunction/disjunction of **11 primitive CodeQL static analysis predicates** evaluated from entry point $h = \mathit{handler}(a)$:

1. **For $p = 1$ (Must-Occur Compilation $\mathsf{E}\llbracket E \rrbracket_h$)**:
   - Compile `w(e)` to `path_exists(h, e) AND all_paths_write(h, e)`: verify both that at least one write to `e` is reachable from $h$ (avoiding vacuous truth on empty handlers) **and** that no control-flow exit path from $h$ bypasses writing to `e`.
   - Compile `w(e, v)` to `path_exists(h, e) AND all_paths_write(h, e) AND source_set(h, e, V[[v]])`: verify via forward/backward taint tracking that the value written to `e` flows from every required source read `r(...)` in `v`.
   - Compile `persist(s)` to `path_exists(h, s) AND page_load_restores(s)`: verify both the handler write to `localStorage`/`sessionStorage` key `s` and a reachable `getItem(s)` call during DOM/window load initialization.
   - Compile guarded conditions `A(a) AND g` by scoping path analysis to branches dominated by guard predicate `guarded_write(h, e, g)`.
   - Compile exclusivity `P(w(e) | NOT A(a)) = 0` to `no_other_handlers(a, e)`, checking across the entire call graph that no event handler other than $\mathit{handler}(a)$ contains a reachable write to `e`.
2. **For $p = 0$ (Prohibition Compilation $\neg \mathsf{R}\llbracket E \rrbracket_h$)**:
   - Compile to the negation of reachability (`NOT path_exists(h, e)` or `NOT call_reaches(h, c)`), proving that no control-flow path from $h$ can trigger the forbidden write or API call.

---

## Quantitative Justification

Evaluated across **4 Claude Code-generated web applications** (Amazon, Twitter, Airbnb, and Slack clones; **300–900 LOC** each, 16–26 action elements, 17–23 event handlers, 5–11 `localStorage` operations, **14–21 FlowCheck constraints per app**, and **30 injected silent behavioral violations** total):

- **Deterministic Bug Detection**: `FlowCheck` detects **30 / 30 (100%)** of injected behavioral violations with **0 false positives**.
- **Comparison Against Direct LLM Code Review**: Across 3 prompt specificity levels (`P1` general review, `P2` UI-element list, `P3` detailed bug taxonomy) and 3 frontier models (`Claude Opus 4.7`, `DeepSeek V3`, `Gemini Pro`), direct LLM review peaks at **26 / 30 (87%)** (`Claude Opus 4.7` at `P3`), while `DeepSeek V3` and `Gemini Pro` miss 23–40% of bugs and introduce false positives.
- **Agents Authoring Formal Constraints vs. Reviewing Code (Amazon App, 7 gold bugs, 3 runs)**:
  - When prompted to generate FlowCheck constraints instead of reviewing code directly, models produce 30–60 (`Claude`), 50–86 (`DeepSeek`), and 15–20 (`Gemini`) candidate constraints per run (with AST semantic validation filtering out invalid syntax; validity rates: `Gemini` **45–100%**, `DeepSeek` **41–65%**, `Claude` **34–44%**).
  - Compiling those agent-authored constraints through FlowCheck improves bug detection from **5/7 to 6/7** for `Claude Opus 4.7` (0 false positives), from **3/7 to 5/7** for `DeepSeek V3`, and from **3/7 to 4/7** for `Gemini Pro` (0 false positives).

---

## Anti-Patterns to Avoid

- **Prompting LLMs with detailed bug taxonomies (`P3`) to self-review frontend code**: Detailed checklists trigger post-hoc rationalization where the LLM invents excuses for why a missing state update or dead branch is "intentional." Have the LLM emit formal interface constraints before inspecting branch implementation details, and verify them with static analysis.
- **Checking only existential reachability (`path_exists`) for UI updates**: Verifying that *some* line inside an event handler writes to a DOM node misses conditional branches that return early or omit the update; always pair `path_exists(h, e)` with `all_paths_write(h, e)` for $p = 1$ invariants.
- **Verifying `localStorage.setItem` without checking page-load restoration**: A handler that writes to storage still produces a broken user experience if the page-load initializer never calls `getItem` to hydrate the UI; always verify round-trip `persist(s)`.

---

## Related Artifacts

- **Spec**: [Next.js Public Agent App Spec](../../specs/nextjs-public-agent-app.spec.md)
- **Skill**: [State-Aware Prototype to WebApp](../state-aware-prototype-to-webapp/SKILL.md)
- **Rules**: [Agent Evaluation Quality](../../rules/agent-evaluation-quality.md), [Agent Human Interaction](../../rules/agent-human-interaction.md)
