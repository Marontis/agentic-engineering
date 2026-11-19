---
name: pooled-prover-verification-service
description: >
  Resource-managed stateful verification pooling with import-keyed session
  leases, empty-perspective headless memory control, cgroup admission gating,
  millisecond document-checkpoint branching, bounded-step atomic rollback, and
  parsed-flag plus scratch-build arbitration for RL prover training and
  multi-agent proving. Derived from "Isabelle Pool Server: a pooled
  verification service for prover training and multi-agent proving"
  (arXiv:2611.24788).
source: https://arxiv.org/abs/2611.24788
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Pooled Prover Verification Service

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

Use this skill when designing or operating a shared formal-verification or interactive-theorem-proving backend (`Isabelle/PIDE`, `Lean 4`, `Rocq/Coq`, `HOL`, `Dafny`, or stateful compiler/SMT servers) that serves **high-throughput RL/tree-search prover training loops** (`thousands` of candidate proof chunks per hour) or **multi-agent MCP proving workloads** on shared hosts where prover sessions are memory-bound (`~0.9–1.3 GB`/session), cold heap/session initialization takes seconds to minutes, and looping tactics or fake proofs (`sorry`, `admit`, `axiomatization`) can stall workers or corrupt rewards.

## Core Problem & Insight

Interactive theorem provers ship interfaces built either for **one human at an editor** (which assume trusted interactive visibility, unbounded tactics, and no multi-client memory admission) or for **stateless whole-project batch builds** (which take `13.6–360 s` per check and destroy incremental proof-search branching). Conversely, spawning one REPL or language-server JVM per agent wastes `3x` memory (`2.6–3.6 GB`/agent vs. `0.9–1.3 GB`), forfeits intra-chunk parallel proof checking, and triggers host OOM kills when concurrent agents spike.

`Isabelle Pool Server` (`IPS`, `arXiv:2611.24788`) demonstrates how to layer a **resource-management & verification-semantics plane** directly over a headless incremental document model (`PIDE`):

1. **Interchangeable import-keyed warm sessions**: Fixing each pooled session's import closure over a prebuilt heap with a single fileless in-memory theory node lets warm sessions swap cleanly across clients in **`2 ms`** (`>1,000x` faster than a `2.3–6.0 s` cold session start and `57,000–180,000x` faster than a `114–360 s` heap build), scaling verify-only throughput to **`3,181` chunks/min (`44,877` commands/min, `24x` single-worker rate)** across `32` concurrent workers.
2. **Empty-perspective headless checking + `cgroup` admission gating**: Disabling editor visibility ranges (`perspective = empty`) eliminates automatic background print-function memory bloat (`saving 0.2–0.4 GB` per prover so `77–111` sessions fit per `100 GB`), while gating new sessions on live `cgroup` memory (`85%` threshold -> evict LRU idle -> fail-fast `HTTP 503` + `Retry-After`) guarantees **`0` kernel OOM kills** under overload.
3. **Document-version checkpoints + parsed verdict flags + scratch-build final arbiter**: In-memory document version edits give **`4 ms` median (`20 ms` mean)** proof-tree branching (`350x–1,450x` faster than prefix replay), server-enforced step budgets roll back looping tactics within `~0.05–0.60 s` without slowing sibling workers (`1.00` speed ratio), and three parsed AST verdict flags (`success`, `proof_open`, `used_sorry`) match clean batch builds on **`890/890`** checks while reserving a stateless scratch build as the final completion arbiter.

---

## Procedure

### Step 1: Pool Interchangeable Import-Keyed Sessions with Empty Editor Perspective

Structure each worker in the pool as a headless incremental document session (`Headless.Session` in Isabelle/PIDE or equivalent stateful server) subject to four invariants:

1. **Immutable Import Key & Fileless Theory Node**: Start each session on a persistent prebuilt logic **heap** covering its requested `imports` closure, and hold its active theory strictly in memory (no backing disk file). Because sessions sharing the same `(heap, imports)` tuple hold no project-specific filesystem state until leased, releasing and re-leasing a warm session takes **`2 ms` (`p50`)** vs. **`2.3–6.0 s`** cold session startup (`HOL` to `HOL-Analysis`) and **`114–360 s`** heap compilation from source.
2. **Refuse Synchronous Heap Builds on the Session Path**: If a client requests unbuilt project imports, return `HTTP 409` instructing the caller to trigger an explicit asynchronous/cached heap build rather than blocking a session-acquisition worker for minutes. Pre-warm or reuse sessions across same-import curriculum batches: starting `32` cold `HOL-Analysis` sessions simultaneously under load stretches median cold-start latency from `6.0 s` (idle) to `8 s` (`8` workers), `35 s` (`16` workers), and **`156 s` (`32` workers, `64%` of worker wall time)**.
3. **Set Empty Visibility Perspective (`perspective = empty`)**: In incremental document provers (such as Isabelle/PIDE), marking edited text ranges as "visible" triggers editor print functions and automatic proof tools across every visible command. Configure pooled headless nodes as `required` with an **empty visible range** and `editor_output_state = off`, running goal/fact/`Sledgehammer` inspections strictly as transient **overlays** on the target command that are removed immediately after the query returns. This saves **`0.2–0.4 GB` per prover process** (`886 MB` `HOL`, `1,077 MB` `HOL-Library`, `1,263 MB` `HOL-Analysis` settled PSS; `<= 1.4%` re-check peak growth vs. `4–28%` with visible ranges) and shares a single gateway JVM (`3.7–4.2 GB` fixed intercept) rather than paying `2.6–3.6 GB`/session for per-agent JVM processes.
4. **Enforce Expiring Exclusive Leases**: Issue a cryptographic/opaque `lease_id` with an idle TTL and lease expiry on `acquire_session`. Reject cross-lease calls and automatically reclaim abandoned sessions when a client crashes or times out.

### Step 2: Gate Pool Admission on Live `cgroup` Memory & Recycle Heap-Bloated Provers

Because theorem provers read large heap images into private memory (`Poly/ML` shares only `~13 MB` across processes), host RAM—not CPU cores—is the hard capacity ceiling:

```
acquire_session(imports)
  ├─ 1. Warm idle session matches imports? ──► YES: Lease immediately (~2 ms)
  ├─ 2. Built heap covers imports?         ──► NO:  Return 409 (build heap first)
  ├─ 3. cgroup memory + margin <= 85% cap? ──► NO:  Evict LRU unleased idle session;
  │                                                 if none evictable -> Return 503
  │                                                 + Retry-After + memory telemetry
  └─ 4. Pool slot free (or idle evicted)?  ──► Start session on heap & lease (2.3–6.0 s)
```

1. **Read Container/Scope `cgroup v2` Counters Directly**: Read `memory.current` against the active `MemoryMax` / Docker limit and reserve a safety threshold (e.g., `85%`) using a conservative per-session memory estimate (`1.5–4.0 GB` depending on heap and tactic depth). When admitting one more session would cross the threshold and all running sessions are actively leased, return `HTTP 503` with `Retry-After` and exact memory utilization facts (`37.5 GB / 48 GB` used, `oom_kill = 0`).
2. **Cap Per-Prover Heaps & Global Fan-Out Tools**: Pass a hard runtime heap ceiling to every prover subprocess (e.g., `ML_OPTIONS --maxheap 9216`) so a runaway proof fails cleanly with a named OOM verdict rather than taking down the host, and enforce a server-wide concurrency semaphore on hammer tools (`Sledgehammer`) that spawn multiple external ATP/SMT processes per call.
3. **Recycle Sessions After Long Rewriting Timeouts**: Even after a timed-out tactic is rolled back in the document model, runtimes like `Poly/ML` retain expanded private heap pages without returning them to the OS (**`1,181 MB` median left behind after a `30 s` `subst` rewrite loop; `7,116 MB` after a `120 s` loop**, vs. `<= 127 MB` median for `metis`). Track per-prover RSS delta after timeouts and close/recycle any session whose resident memory exceeds a post-rollback bloat threshold.

### Step 3: Branch via Millisecond Document Checkpoints & Enforce Atomic Budget Rollback

1. **Mandatory Server-Side Per-Call Wall-Clock Budgets**: Require every verification request (`verify_chunk` or single command) to carry a bounded timeout enforced by the server (e.g., `5–20 s` for search rollouts, $\min(600, \max(30, 2n))\text{ s}$ for $n$-command blocks). When a tactic exceeds its budget, cancel checking, **atomically remove the submitted chunk from the theory node** (`0.05–0.54 s` `p50`, `<= 0.60 s` `p95` in `5/6` looping benchmarks), and return `timed_out = true` plus `stuck_line` naming the exact diverging command.
2. **Cheap Tree-Search Branching via Document Checkpoints**: Do not fork OS processes or replay theory prefixes from line 1 (`8 s` early, `43 s` middle, `91 s` late in a file) to explore candidate proof steps. Instead:
   - Call `save_checkpoint` (`3 ms` `p50`) to record the current settled document text and command-status frontier.
   - Submit candidate proof chunks (`verify_chunk`) with intra-chunk parallel proof checking enabled (`parallel_proofs >= 1`). Failed or timed-out chunks auto-rollback on the server.
   - To backtrack from a valid-but-suboptimal branch (or after evaluating a whole-proof candidate), call `restore_checkpoint` (`4 ms` call `p50`; **`4 ms` `p50`, `20 ms` mean, `200 ms` `p95`** total branch cost including incremental PIDE settling delay)—cutting branching overhead by **`350x` to `1,450x`**.

### Step 4: Separate Fast Parsed-AST Verdict Flags from Stateless Scratch-Build Arbitration

Never equate `"no command returned an error"` with `"theorem proved"`—an unfinished proof or a proof closed by `sorry` / `oops` / custom axioms returns zero command errors while corrupting RL rewards and halting proving agents prematurely:

1. **Three-Flag Inner-Loop Verdict over Parsed Commands**: Inspect the prover's **parsed command AST** (never raw regex/substring scans over proof text, which comments or string literals can spoof or hide) and return four explicit booleans on every `verify_chunk`:
   - `success`: No command in the chunk errored or timed out.
   - `proof_open`: Whether the prover remains inside an unfinished proof state (`pending_qed` distinguishes all goals discharged missing only `qed`).
   - `used_sorry`: Whether any parsed command in the chunk invoked `sorry` or `oops`.
   - `timed_out` (+ `stuck_line`): Whether the budget expired before settling.
   Count a candidate step/block as **proved in-session** if and only if `success && !proof_open && !used_sorry`.
2. **Pre-Submission Command Denylist**: Reject candidate proof text containing `axiomatization`, raw meta-language escape hatches (`ML`, `ML_file`, `setup`), or host file-I/O commands at the server boundary unless explicitly enabled for trusted corpus replay.
3. **Stateless Scratch-Build Final Arbiter**: Whenever a proof completion verdict exits the inner search loop (final RL episode reward certification, benchmark evaluation, or multi-agent builder/reviewer sign-off), run a **stateless whole-file batch build** (`isabelle build` / clean compiler invocation in a fresh process depending on zero pooled session state) and verify that the original target theorem statement is unchanged and its oracle/axiom set (`thm_oracles`) is empty (pair with [`three-surface-verified-code-audit`](../three-surface-verified-code-audit/SKILL.md) to guard against weakened specifications).

### Step 5: Authenticate & Isolate Network-Exposed Verification Endpoints

Pooled verification servers (including reference `IPS` and `PIDE AI` TCP deployments) frequently ship **without built-in client authentication**, trusting network reachability alone while sharing a single gateway JVM across leases. In any multi-user, CI, or untrusted-network deployment:
- Bind the HTTP/MCP pool server to `127.0.0.1` or place it behind an authenticating reverse proxy enforcing per-client bearer tokens and per-client session/budget quotas (never inline admin tokens in static web pages).
- Confine heap-build project paths to explicit allowlisted root directories, and run untrusted multi-tenant workloads in separate container/VM boundaries rather than relying on cooperative lease IDs alone.

---

## Quantitative Reference Profile (`arXiv:2611.24788`, `32`-Core / `128 GB` `Isabelle2026` Host)

| Metric / Workload (`HOL-Analysis`: `93` theories, `11,984` blocks) | Baseline / Comparison | `IPS` Pooled Service | Operational Takeaway |
|:-------------------------------------------------------------------|:---------------------:|:--------------------:|:---------------------|
| **Warm Lease Hit vs. Cold Session vs. Heap Build** | `2.3–6.0 s` cold start; `114–360 s` heap build | **`0.002 s` (`2 ms`, `36/36` trials)** | **`>1,000x` faster** than cold start; keep heaps & warm sessions resident |
| **Verify-Only Throughput (`W = 1 -> 32` workers)** | `132` chunks/min (`W=1`); `PIDE MCP` `813`/min (`W=8`) | **`927`/min (`W=8`); `3,181` chunks/min (`44,877` cmds/min) at `W=32`** | **`24x` single-worker scaling** (`0.41 -> 0.52 s` median latency, `0` timeouts) |
| **Throughput Including Cold Per-Theory Session Starts** | `113` chunks/min (`W=1`); `PIDE MCP` `381`/min (`W=8`) | **`497`/min (`W=8`); `899` chunks/min at `W=32`** (`8.0x` raw; `8.33` Table 9 / `8.6x` §5.2 census rate) | Concurrent cold starts stretch `6 s -> 156 s` (`64%` of `W=32` wall time); pre-warm shared imports |
| **Branching / Backtracking (`200` proof states)** | Prefix replay: `8 s` early / `43 s` mid / `91 s` late (`30–35 s` p50) | **`3 ms` save; `4 ms` p50 / `20 ms` mean / `200 ms` p95 branch cost** | **`350x–1,450x` cheaper branching** (`1,000/1,000` verdict & source parity) |
| **Settled Memory Capacity (`100 GB` budget after `3.7–4.2 GB` JVM)** | `PIDE MCP A` (visible range): `66–78` sessions; `B` (JVM/agent): `28–38` | **`111` (`HOL`, `886 MB`), `91` (`HOL-Library`, `1,077 MB`), `77` (`HOL-Analysis`, `1,263 MB`)** | Empty `perspective` saves **`0.2–0.4 GB`/prover** and caps re-check peak at `<= 1.4%` |
| **Overload Admission (`MemoryMax=48G`) & Crash Isolation** | Unmanaged host -> kernel OOM kill | **`27` admitted (`37.5 GB`), `28th` `HTTP 503` (`oom_kill = 0`); `7/7` survive sibling `SIGKILL`** | Fail-fast `503` preserves live rollout leases; single gateway JVM remains a shared crash domain |
| **Parsed Verdict Flags vs. `isabelle build` (`890` checks)** | `690` batch builds (`13.6 s` p50 / `24 s` p95) | **`200/200` `sorry`, `200/200` open proof, `197/197` error, `293/293` valid matched** | **`0` reward-corrupting false positives** on proof-body mutations |

---

## Environment Caveats & Failure Modes

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| **Unreclaimed prover heap after long rewrite loops** | `subst` rewrite loops grow private `Poly/ML` heap by `1.2 GB` (`30 s`) to `7.0 GB` (`120 s`), unfreed by document rollback | Enforce `ML_OPTIONS --maxheap`, prefer tight step budgets (`5–20 s`) during search, and close/recycle sessions whose post-rollback RSS delta exceeds threshold |
| **Cold-start stampede across heterogeneous-import curricula** | `32` workers simultaneously cold-starting `HOL-Analysis` heaps (`156 s` median start) | Group training batches by shared `imports` so workers hold one warm lease across problems, or stagger/pre-warm sessions before timed rollouts |
| **Statement tampering or hidden oracle escapes** | Prover proves a weakened theorem statement or invokes an unchecked oracle | Pair IPS's `axiomatization`/ML denylist and stateless batch build with statement-equivalence and `thm_oracles == empty` checks ([`three-surface-verified-code-audit`](../three-surface-verified-code-audit/SKILL.md)) |
| **Multi-file project edits in interactive coding** | Single-node fileless pooled sessions cannot resolve edits spanning multiple interdependent project theories | Use fileless pooled sessions (`IPS`) for training clusters and single-theory proving, and project-scoped frontends (`PIDE AI` with empty default visibility) when co-editing multi-theory repositories |

## Cross-References

- [`three-surface-verified-code-audit`](../three-surface-verified-code-audit/SKILL.md) — Complementary: audits *what* formal contract is proved (`Surface A/B/C` + `Post2Exe` anti-vacuity), whereas this skill provides the *pooled stateful prover runtime* (`warm leases`, `4 ms` checkpoints, `cgroup` admission, and parsed-flag + scratch-build arbitration)
- [`serial-slot-accelerator-command-scheduling`](../serial-slot-accelerator-command-scheduling/SKILL.md) — Contrasting resource regime: schedules `1`-slot exclusive GPU timing benchmarks across nodes, whereas prover pools multiplex `32–111` memory-gated CPU sessions per host
- [`verifier-gap-sign-pre-rl-audit`](../verifier-gap-sign-pre-rl-audit/SKILL.md) — Pre-RL audit for soft/proxy process verifiers when exact formal provers are unavailable
- [`agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — Loopback binding, authentication proxy requirements, and multi-tenant containment boundaries

## Sources

- [Isabelle Pool Server: a pooled verification service for prover training and multi-agent proving](https://arxiv.org/abs/2611.24788) (`arXiv:2611.24788`, `src:2611-24788v1`) — Code: [Deep-LCF/Isabelle-Pool-Server](https://github.com/Deep-LCF/Isabelle-Pool-Server)
