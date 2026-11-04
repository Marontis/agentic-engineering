---
name: agent-data-mutual-evolution
description: >-
  Closed-loop co-evolution of executable tool-use tasks and verified teacher
  trajectories driven by student rollout failure attribution, skill-guided
  recovery, and Avoidable-Work Ratio (AWR) refinement. Derived from EvoMCP
  (arXiv:2610.41479).
---

# Agent–Data Mutual Evolution (EvoMCP)

Use this skill when building or operating a post-training / SFT data pipeline for tool-using or Model Context Protocol (MCP) agents. Static synthetic datasets saturate quickly because tasks remain disconnected from the student's changing failure modes and raw teacher trajectories contain trial-and-error noise. This procedure couples **student-feedback-driven task evolution** (with synchronized executable verifiers) and **skill-guided trajectory refinement** in an iterative loop.

---

## When to Use

- Fine-tuning an open-weight model (`student`) on multi-server tool-use or MCP environments where static SFT plateaus after 1–2 epochs/rounds.
- Converting raw tool ecosystems (databases, filesystems, cloud APIs, MCP servers) into verifiable training tasks with deterministic state checks.
- Cleaning teacher demonstration trajectories that pass final state checks but contain intermediate schema errors, redundant exploration, or late constraint handling.

---

## Core Architecture

Every training instance in the loop is bound to an **executable task package**:
$$\tau = (q, E_0, T_{\tau}, V_{\tau})$$
where $q$ is the user instruction, $E_0$ is the isolated initial sandbox state, $T_{\tau}$ is the exposed toolset, and $V_{\tau}$ is a programmatic verifier script that inspects final environment state $E_T$ and agent response $\hat{y}$ (`V_tau(E_T, y_hat) -> {0, 1}`).

---

## Step-by-Step Procedure

### Phase 1: Seed Task Construction & Verifier Alignment

1. **Profile the environment**: Run a read-only reconnaissance pass over the sandbox ($E_0$) and tool definitions ($T_{\tau}$) to catalog concrete entities, schemas, files, and cross-server dependencies.
2. **Draft task + programmatic verifier**: Synthesize instruction $q$ alongside an executable verification script $V_{\tau}$ that checks both persistent side effects in $E_T$ (file diffs, DB rows, API records) and required output claims.
3. **Verify solvability before admission**: Execute a reference agent inside a fresh sandbox copy. Admit the seed task only if:
   - The environment initializes cleanly without missing dependencies.
   - The trajectory terminates and $V_{\tau}(E_T, \hat{y}) = 1$.
   - The verifier does not pass trivially on the unmodified initial state $E_0$.

### Phase 2: Student Rollout & Three-Way Failure Attribution

 At round $r$, run the current student checkpoint $\pi_{\theta}^{(r-1)}$ on the active task pool and route every failed rollout ($\tau, \xi_{\text{stu}}$) through a diagnostic judge before generating any new tasks or demonstrations:

| Attribution Category | Diagnostic Criteria | Pipeline Action |
|:---------------------|:--------------------|:----------------|
| **1. Environment / Verifier Defect** | Unreachable service, corrupted fixture, contradictory prompt requirement, or false-negative $V_{\tau}$ bug on a correct execution trace. | **Repair or discard $\tau$**. Never evolve or train on broken task packages. |
| **2. Genuine Student Failure** | Valid task and verifier, but the student failed due to: (a) *Planning/Decomposition*, (b) *Tool Grounding/Schema Misuse*, (c) *State Tracking/Context Drift*, or (d) *Premature Termination*. | **Record structured failure tag $d(\tau)$** and pass to Phase 3 (Task Evolution) and Phase 4 (Trajectory Evolution). |
| **3. Student Pass** | $V_{\tau}(E_T, \hat{y}) = 1$ with low avoidable work. | Down-weight in curriculum sampling; optionally use as a parent for harder multi-parent composition. |

### Phase 3: Curriculum-Conditioned Task Evolution

Conditioned on the student's failure distribution $\{d(\tau)\}$, evolve verified seed tasks into harder, targeted variants:

1. **Select evolution mode**:
   - *Single-parent targeted mutation*: Inject the exact structural complexity the student failed on (e.g., adding cross-server state handoffs, exception-recovery branches, or implicit schema constraints).
   - *Multi-parent workflow composition*: Merge two compatible verified tasks that share environment entities into a longer-horizon sequential or branching workflow.
2. **Re-execute and synchronize the verifier ($V_{\tau'}$)**:
   - Run the teacher model on the mutated instruction $q'$ inside a fresh sandbox $E_0'$.
   - Update $V_{\tau'}$ against the resulting ground-truth terminal state $E_T'$ so the verifier checks every newly added constraint.
   - **Hard Gate**: Reject any evolved task $\tau'$ where $V_{\tau'}$ fails to execute, passes without the new behavior, or cannot be solved by the teacher after Phase 4 recovery.

### Phase 4: Skill-Guided Trajectory Recovery & AWR Refinement

Do not train directly on raw teacher rollouts. Process every candidate task $\tau'$ through a two-stage teacher trajectory pipeline (`1` primary attempt + up to $K=3$ skill-guided retries):

1. **Branch A — Skill-Guided Recovery (when the teacher fails)**:
   - Compare the failed teacher trace $\xi_{\text{raw}}$ against verifier diagnostics.
   - Extract a concise, task-local **Corrective Skill** covering four fields:
     1. *Failure Point*: Exact step and tool call where execution diverged.
     2. *Root Cause*: Why the parameter, tool choice, or ordering failed.
     3. *Actionable Guidance*: Preconditions and tool-call pattern required on retry.
     4. *Constraint Checklist*: Terminal state invariants required by $V_{\tau'}$.
   - Re-run the teacher in a reset sandbox conditioned on the Corrective Skill (up to $K=3$ attempts). Strip the corrective hint from the prompt before saving the final SFT pair so the student learns to produce the behavior from $q'$ alone.
2. **Branch B — Efficiency Refinement (when the teacher passes with high avoidable work)**:
   - Compute the **Avoidable-Work Ratio (`AWR`)** over the passing trace $\xi$:
     $$\text{AWR}(\xi) = \frac{N_{\text{avoidable}}(\xi)}{N_{\text{total}}(\xi)}$$
     where $N_{\text{avoidable}}$ counts failed tool calls caused by preventable schema/argument mistakes, redundant duplicate reads, and abandoned exploratory branches.
   - If $\text{AWR}(\xi)$ exceeds your quality threshold or contains preventable tool errors, synthesize an **Optimization Skill** summarizing the shortest valid execution path and re-execute the teacher in a fresh sandbox to obtain a clean, verifier-passing trajectory $\xi^{\star}$.
3. **Admit & Train**: Admit `(q', \xi^{\star})` to the round-$r$ SFT mixture only if $V_{\tau'}(E_T^{\star}, \hat{y}^{\star}) = 1$. Fine-tune $\pi_{\theta}^{(r)}$ and repeat Phase 2.

---

## Quantitative Reference (`EvoMCP`, `arXiv:2610.41479`)

- **End-to-end gains across 3 rounds (`Qwen3.6-27B` student, `2,400` verified trajectories/round)**:
  - `Toolathlon`: `36.9%` (`R0`) $\to$ `46.6%` (`R1`) $\to$ `50.5%` (`R2`) $\to$ `53.4%` (`R3`, `+16.5` pp).
  - `MCPMark`: `56.7%` (`R0`) $\to$ `60.6%` (`R1`) $\to$ `64.5%` (`R2`) $\to$ `66.9%` (`R3`, `+10.2` pp).
  - `MCP-Atlas`: `61.0%` (`R0`) $\to$ `68.4%` (`R1`) $\to$ `71.3%` (`R2`) $\to$ `73.6%` (`R3`, `+12.6` pp).
- **Vs. Static SFT**: Matched-step `Static SFT` plateaus at `40.8%` $\to$ `39.8%` (`Toolathlon`), `57.4%` $\to$ `58.2%` (`MCPMark`), and `65.8%` $\to$ `67.2%` (`MCP-Atlas`), trailing `EvoMCP (R3)` by `13.6`, `8.7`, and `6.4` percentage points.
- **Component value (`R1` ablations)**: Removing student feedback drops scores by `-4.4` / `-2.4` / `-2.0` pp; removing task evolution drops `-4.2` / `-3.2` / `-2.2` pp; removing trajectory refinement drops `-2.3` / `-1.1` / `-0.6` pp.
- **Recovery & efficiency (`2,400` pairs)**: Skill-guided recovery rescues `26.0%` (`R1`) to `40.0%` (`R3`) of failed teacher tasks vs `9.0%` to `14.0%` for unguided Best-of-$K$ retries; trajectory refinement cuts mean tool-call errors from `2.6` to `1.6` and output tokens by `9.0%` (`9,752.0` $\to$ `8,873.0`).
