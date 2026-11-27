---
name: shared-console-async-simulation-mcp
description: Connect LLM agents to live, stateful, long-running simulation, CAD/CAE, or scientific computing engines via a 7-tool Model Context Protocol (`MCP`) server pairing zero-embedding BM25/hierarchical manual discovery with step-atomic live inspection, safe cycle-boundary interruption, and bidirectional human console-history coexistence.
source: "arXiv:2611.33926"
repository: "https://github.com/Marontis/agentic-engineering"
license: CC-BY-4.0
---
<!-- License: CC BY 4.0 | Repository: https://github.com/Marontis/agentic-engineering -->

# Shared-Console Async Simulation MCP Architecture

## When to Use

Use this skill when exposing a **live, stateful, computationally intensive simulation, CAD/CAE, physics, robotics, or numerical solver engine** (such as Discrete Element Method `PFC`/`FLAC`/`3DEC`/`YADE`, Finite Element / CFD solvers, molecular dynamics `OpenMM`/`LAMMPS`, or 3D/robotics engines `MuJoCo`/`Blender`/`FreeCAD`) to AI agents via the Model Context Protocol (`MCP`), especially when:
- Single solver runs take **minutes to hours** in-memory and cannot be wrapped as blocking synchronous RPCs or stateless file-in/file-out batch jobs without losing live state,
- The engine exposes **hundreds or thousands of domain commands/APIs** (`100K–300K+` documentation tokens) whose syntax evolves across versions and cannot fit into upfront MCP tool schemas, and
- **A human engineer/modeler and an AI agent share the same live GUI/console process**, requiring the agent to inspect intermediate physics mid-solve, abort diverging runs cleanly without crashing C++/GPU kernels, and detect unannounced human console commands (`restore`, `reset`, parameter tweaks).

Do **not** use this skill for stateless, sub-second mock/REST API catalogs where a two-meta-tool `Code Mode` (`search() + execute()`) gateway suffices, or when untrusted multi-tenant callers share one unsandboxed host process (`execute_code` runs arbitrary Python inside the engine process and must be confined to a trusted local workstation or isolated per-session container).

## Core Insight

Conventional scientific MCP wrappers fail on two fronts: either they wrap individual solver features into dozens of rigid workflow tools (e.g., `76` tools in `COMSOL-MCP`, inflating prompt schemas while locking agents into pre-scripted workflows and collapsing on out-of-template physics), or they suspend the entire agent turn until a multi-hour background job finishes—blinding the agent to early numerical divergence, inverted boundary signs, or unannounced human console edits.

Evaluated across `6` discrete/continuum mechanics engines (`itasca-mcp` for `PFC`, `FLAC`, `3DEC`, `MPoint`, `MassFlow`, and `yade-mcp` for open-source `YADE`, `arXiv:2611.33926`), a **two-process architecture (`7` orthogonal MCP tools + persistent in-engine stdlib HTTP bridge)** solves discovery bloat, async concurrency, C++ thread safety, and human coexistence simultaneously:
1. **`2` Zero-Embedding Documentation Primitives (`query` + `browse`)**: Replace `1,000+` per-command tool schemas (`241,283` tokens in `PFC 7.0`) with field-weighted `BM25` search (`name > keywords > description`, top-`10` 1-line hits) plus hierarchical progressive disclosure (`category -> command list -> full spec`). Agents read just **`1.4%–1.8%` (`3,381–4,291` tokens)** per lookup and **`2.7%` (`6,536` command-corpus tokens; `12,882` total doc tokens)** across a full multi-hour triaxial calibration—whereas the **only failed session out of `21` (`20/21 = 95.2%` success across `7` frontier/open-weight models)** was the sole session (`1/21`) that skipped the documentation tools and lost `5/12` task submissions to hallucinated API calls.
2. **`5` Orthogonal Sync/Async Execution Primitives + Step-Atomic Cycle Holds**: Decouple foreground inspection (`execute_code`), background solves (`execute_task`), lock-free status (`check_task_status`), step-boundary cancellation (`interrupt_task`), and workspace history (`list_tasks`). Routing live `execute_code` requests through a **single-timestep cycle hold** prevents "rolling-shutter" cross-timestep read tearing (e.g., reading stress from step $k$ and strain from step $k + 50$) while preserving **bit-identical** mechanical trajectories, enabling **`14/21` autonomous sessions to inspect running solves live and `8/21` (`5` models) to abort diverging runs mid-solve** before wasting multi-hour budgets.
3. **Bidirectional Console-History Injection**: Appending human-typed console commands to the next MCP tool response (`console history`) eliminates human copy-paste relaying and enables agents to distinguish benign human reads from destructive mid-session `model restore` rollbacks—automatically auditing cross-iteration state continuity and adding runtime cycle-counter guards.

## Step-by-Step Procedure

### Step 1: Decouple Process Lifetimes via an In-Engine Zero-Dependency Bridge
Never embed the MCP server directly inside the solver GUI process if agent disconnects or client restarts would reset a multi-hour model state, and never require exotic pip dependencies inside vendor-bundled Python interpreters (`PFC`, `ABAQUS`, `Blender`):
1. **In-engine bridge (Python standard library only)**: Load a lightweight `http.server` / socket listener (`127.0.0.1` loopback-bound with per-session bearer token) inside the live simulation process that owns the in-memory model, persistent task registry, and console hooks.
2. **External MCP server (stateless adapter)**: Run the `stdio` / `Streamable HTTP` MCP server as a separate lightweight client process (`uvx` / `npx`) that holds the static documentation index and forwards execution calls to the live engine bridge. Restarting or swapping the MCP client leaves running background tasks and gigabyte-scale particle/mesh states untouched.

### Step 2: Expose Exactly Two Zero-Embedding Progressive-Disclosure Manual Tools
Instead of registering hundreds of domain commands as MCP tools or bundling vector databases/API keys:
1. **`query(terms, domain?)`**: Pre-index vendor command/scripting manuals (`Markdown`/`JSON` tree) at startup (`< 100 ms`) using pure-Python **field-weighted `BM25`** weighting `command/symbol name > curated keywords > body description`. Return at most the **top `10` matches** formatted strictly as `(hierarchical_path, call_syntax, one_line_summary)` (`~300–500` tokens).
2. **`browse(path)`**: Serve `3`-level progressive disclosure over the manual tree:
   - Root (`""`) $\to$ top-level domain categories with item counts,
   - Category path $\to$ compact command/function list with 1-line summaries,
   - Leaf path $\to$ complete specification (arguments, physical units, caveats, minimal valid snippet).
   - **Self-correcting path fallback**: When an agent passes a hallucinated or outdated leaf path, return the **valid sibling list of the nearest existing parent directory** rather than an opaque `404` error so the agent recovers in one step.

### Step 3: Expose Five Orthogonal Sync/Async Execution Primitives
Keep the execution surface minimal, domain-neutral, and orthogonal (`5` tools total—never add domain-specific convenience wrappers that overlap with `execute_code`):
1. **`execute_code(code)`**: Run a short foreground Python/command snippet (`<= 30 s` timeout) for interactive micro-trials (contact-law probes, geometry sanity checks, dry-run syntax validation before launching long tasks) **and** for live read-only physics inspection *while* a background task is actively stepping. Capture `stdout`, `stderr`, return values, and exceptions cleanly.
2. **`execute_task(script_path_or_code, description)`**: Submit a long-running simulation script to asynchronous execution, persist its input/log path in an on-disk task registry, and return `{task_id, status: "running", started_at}` **immediately** without blocking the MCP turn.
3. **`check_task_status(task_id)`**: Read `{status, elapsed_s, current_step, tail_stdout, error_traceback}` **directly from the thread-safe task registry** without touching the solver's main/compute queue so status checks respond in milliseconds even under `100%` CPU/GPU solver load.
4. **`interrupt_task(task_id)`**: Signal the active solver loop to halt cleanly at the **next step/cycle boundary**, leaving the in-memory specimen/mesh intact for post-mortem inspection or checkpoint saving rather than killing the OS process.
5. **`list_tasks()`**: Return the persistent history of `{task_id, status, duration, summary}` across the workspace so reconnected or compacted agents recover run lineage immediately.

### Step 4: Enforce Step-Atomic Cycle Holds & Deferred Interrupts Matched to the Engine's Threading Model
Live inspection (`execute_code` during `execute_task`) and mid-solve cancellation (`interrupt_task`) will corrupt memory, tear state across timesteps, or trigger fatal C++ aborts unless synchronized at explicit solver step boundaries. Match the bridge queue to the host engine's threading architecture:
- **Pattern A — Single-main-thread C++/Qt engines (e.g., `PFC` / `FLAC` / `3DEC`)**:
  - Maintain two queues: a `main queue` (polled via Qt timer/idle loop when no solve is active) and a `cycle queue` (polled via a per-step callback such as `itasca.set_callback` while stepping).
  - When a task is running, route incoming `execute_code` snippets to the `cycle queue` so they execute **on the main thread inside a single paused step**, and **reject nested step/solve commands** (`model solve`, `model cycle`) inside cycle-queue calls to prevent re-entrant deadlocks.
  - **Re-register callbacks automatically before every command**, because engine reset commands (`model new`, `model restore`) silently wipe registered Python callbacks.
- **Pattern B — Background-compute-thread + main-thread-Qt-GUI engines (e.g., `YADE`)**:
  - Run `execute_task` on a dedicated `task thread` while keeping `execute_code` on the `main thread` (so Qt/OpenGL `3D` viewport screenshots remain thread-valid).
  - **Eliminate "rolling-shutter" read tearing via a persistent `cycle hold`**: Wrap the step driver (`O.run()`) so an internal `bridge-PyRunner` is automatically re-inserted at `O.engines[0]` across `O.reset()` and `O.engines = [...]` reassignments. When `execute_code` arrives during a running task, request a hold at `bridge-PyRunner`, wait until the C++ loop parks between steps $k$ and $k+1$, execute the main-thread snippet against a **frozen single-timestep state**, and release the hold.
  - **Defer Python interrupt exceptions until C++ exits**: Never raise a Python exception directly inside a C++ step callback (which aborts the C++ runtime and destroys the model). Have `interrupt_task` call the engine's native C++ pause flag (`O.pause()`) inside the callback and raise `CycleInterrupt` in Python **only after** `O.run()` returns cleanly to the wrapper.

### Step 5: Inject Bidirectional Human Console History & Gate Persistent Updates
1. **Hook the interactive human console**: Record every command executed manually by the human engineer in the engine's interactive console/REPL since the agent's previous MCP call, and append a compact `console_history: [...]` block to the next MCP tool response (symmetric with echoing agent execution logs to the human console).
2. **Audit unannounced state mutations before continuing**: Instruct the agent (via server instructions) to classify any non-empty `console_history` entry before trusting cached metrics:
   - *Read-only inspection* (e.g., `ball list`, camera/plot queries): continue uninterrupted.
   - *State-mutating / destructive commands* (e.g., `model restore`, `O.load()`, boundary-velocity edits): immediately query live engine state (`step/cycle` counter, stress/energy invariants) via `execute_code`, verify continuity against on-disk saved checkpoints, and add monotonic step-counter assertions to subsequent task scripts.
3. **Confine code execution & gate persistent skill/bridge changes**: Bind the HTTP bridge strictly to loopback/container-internal interfaces, enforce sandbox path/network isolation per [`agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md), and if the agent proposes persistent updates to calibration skills, reusable solver templates, or bridge wrappers, pass them through `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../../rules/recursive-improvement.md).

## Environment Caveats

- **System-prompt / MCP instruction discipline for weak tool callers**: Across `21` autonomous `YADE` calibration sessions (`7` models $\times$ `3` runs, `arXiv:2611.33926` `Table 8`), `20/21` (`95.2%`) succeeded (`Claude Opus 5.5`, `GPT-6.1-sol`, `Gemini 4 Argon`, `Qwen3.8-max-0902`, `DeepSeek-V4-Pro`, `DeepSeek-V4.1-Flash-1017` all `3/3` from `$0.10` to `$1.99`/session; `Kimi K3` `2/3`). The **single failure (`Kimi K3` session `2`, $J = 1.31$)** was the **only session (`1/21`) that never invoked `query` or `browse`**, wasting `5/12` task submissions on API errors. Include a concise server-instruction rule requiring a `query`/`browse` check + `execute_code` 1-step dry run before the first `execute_task`.
- **Non-uniqueness of inverse physical calibration**: Even when `20/21` sessions met all three macroscopic triaxial targets ($E_{50}, q_{\mathrm{peak}}, D$ within tolerances $\tau_i$, $J = \max_i |e_i|/\tau_i \le 1$), `1` session (`DeepSeek-V4-Pro` session `1`, $J = 0.72$) satisfied the targets in an alternative physical trade-off regime (looser initial porosity $n_0 = 0.391$ compensated by higher contact modulus $E^* = 365\text{ MPa}$ and lower rolling resistance $\eta_r = 0.12$), while `19/21` clustered inside `15%–38%` of the admissible parameter box. Always inspect micro-mechanical state (`execute_code` fabric/coordination-number checks) or add multi-confining-pressure checks when uniqueness matters.
- **Engine reset survival**: Nearly all simulation engines clear user-registered callbacks or engine lists on `reset()` / `restore()`. Verify in CI (which can run on a small local model such as `Qwen3.5-4B` on CPU) that `execute_code` cycle holds and `interrupt_task` still fire *after* a script executes `model new`, `model restore`, or `O.reset()`.

## Failure Modes

- **Exposing one MCP tool per solver command or pre-bundled workflow**: Loading `PFC 7.0`'s full `241,283`-token command manual overflows or dominates context before a single step runs, while rigid workflow-tool servers (`76` tools in `COMSOL-MCP`) violate orthogonality and block agents from writing custom servo loops, mid-solve fabric probes, or state-integrity checks.
- **Allowing unsynchronized cross-thread `execute_code` reads ("rolling-shutter" tearing)**: Executing Python inspection on a GUI/HTTP thread while a C++ background thread steps particles reads mixed fields from different timesteps (`step k` positions paired with `step k + Δk` forces) or segfaults on concurrent container reallocation—always park the solver at a `cycle hold` barrier first.
- **Raising Python exceptions inside C++ solver callbacks**: Raising `KeyboardInterrupt` or custom Python exceptions directly inside a C++-invoked per-step callback unwinds across C++ stack frames not compiled for Python exception propagation, terminating the entire engine process and losing unsaved multi-hour states. Always pause natively (`O.pause()`) inside the callback and raise after the step loop returns.
- **Queueing `check_task_status` behind the main solver queue**: If status polling routes through the same execution queue as solver steps or heavy post-processing, `check_task_status` times out under heavy compute, causing agents to assume the engine hung and issue destructive duplicate tasks.
- **Silent state corruption from unlogged human console actions**: Without `console_history` injection, a human modeler running `model restore` mid-session leaves the agent optimizing parameters against curves from an overwritten state (`Fig. 7` / `Table 7` in `arXiv:2611.33926`—note `Fig. 7` labels failed lateral-servo iteration `1` as `J = 40` while `Table 7` records it as `invalid, lateral stress off target`).

## Cross-References

- **Rules**:
  - [`skill-system-design.md`](../../rules/skill-system-design.md) — `"DO: Decouple semantic action commitment from interface-specific tool realization and repair realization locally"` and `"DO: Annotate Code Mode tool stubs with explicit return-value shapes and bound router fallbacks rather than stacking front-door routers on strong coders"`
  - [`adk-workflow-architecture.md`](../../rules/adk-workflow-architecture.md) — `"DO: Suspend multi-minute external operations using \`LongRunningFunctionTool\`"` (contrasting full workflow suspension vs. active mid-solve inspection/interruption)
  - [`agent-human-interaction.md`](../../rules/agent-human-interaction.md) — `"DON'T: Let the human become the transport layer between agents"`
  - [`agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — `"DON'T: Poll global backend quiescence to close a session or screen status endpoints only on idle backends"` and `"DO: Bind companion configuration UIs to loopback, enforce header auth and Origin/Content-Type checks, and validate memory writes at the storage sink"`
  - [`recursive-improvement.md`](../../rules/recursive-improvement.md) — `"DO: Pass every self-modification through one acceptance gate"`
- **Spec Templates**:
  - [`adk-agentic-workflow.spec.md`](../../specs/adk-agentic-workflow.spec.md) — Long-running asynchronous tool execution and live state coordination
  - [`agent-sandbox.spec.md`](../../specs/agent-sandbox.spec.md) — Loopback bridge binding, exclusive-compute scheduling, and status-polling limits
- **Related Skills**:
  - [`mcp-server-design`](../mcp-server-design/SKILL.md) — General MCP tool schema, pagination, and error-formatting conventions
  - [`tiered-contract-readiness-gate`](../tiered-contract-readiness-gate/SKILL.md) — Keeping model inference out of MCP servers via deterministic server-side logic
  - [`pooled-prover-verification-service`](../pooled-prover-verification-service/SKILL.md) — Managing warm, stateful interactive verification engines (`Isabelle/PIDE`) across concurrent agent sessions
  - [`serial-slot-accelerator-command-scheduling`](../serial-slot-accelerator-command-scheduling/SKILL.md) — Separating fast parallel inspection from exclusive serial compute slots
- **Research Briefs**:
  - [`mcp-code-mode-return-shape-stubs-vs-routers.md`](../../research-briefs/mcp-code-mode-return-shape-stubs-vs-routers.md) — Two-meta-tool `Code Mode` (`search + execute`) trade-offs on stateless tool catalogs
  - [`mcp-vs-cli-tool-integration-analysis.md`](../../research-briefs/mcp-vs-cli-tool-integration-analysis.md) — Progressive disclosure token economics (`71%–99%` schema reduction)
  - [`prompt-preanalysis-vs-mcp-uralic-translation.md`](../../research-briefs/prompt-preanalysis-vs-mcp-uralic-translation.md) — Tool-calling reliability differences across open-weight instruction checkpoints

## Sources

- Han, R., Uzuoka, R., & Ueda, K. (2026). *Connecting AI Agents to Live Discrete Element Simulations via the Model Context Protocol*. `arXiv:2611.33926` (`itasca-mcp` & `yade-mcp`, MIT License).
