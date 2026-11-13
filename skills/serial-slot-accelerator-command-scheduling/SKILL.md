---
name: serial-slot-accelerator-command-scheduling
description: >
  Decentralized parallel/serial command-slot splitting, three-phase
  reserve-claim-commit cross-node waiting-command migration, queue-wait
  budget exclusion, and paired trace-driven scheduling replay for
  multi-session GPU and hardware-accelerator coding agents. Derived from
  "Metal Sandbox: Isolated Execution and Command Scheduling for GPU
  Coding Agents on Apple Silicon" (arXiv:2611.17294).
source: https://arxiv.org/abs/2611.17294
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Serial-Slot Accelerator Command Scheduling

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

Use this skill when running multiple concurrent coding-agent sessions or RL rollouts that compile, test, and benchmark kernels or hardware-bound workloads on shared multi-node GPU/accelerator clusters (Metal, CUDA, Triton, ROCm, NPU, or exclusive hardware benches) where overlapping benchmark commands corrupt device timing or exhaust memory, yet pinning entire sessions to one node leaves accelerators mostly idle.

## Core Problem & Insight

Interactive kernel-engineering trajectories are overwhelmingly bound by LLM thinking and lightweight file inspection rather than device execution, yet every benchmark invocation requires **interference-free single-tenant device access**:

- In profiled Metal kernel optimization sessions (`metal_nbody`), actual GPU execution consumes **`44.0` seconds over `31.6` minutes (`2.32%` active GPU fraction)**.
- Allowing concurrent sessions on the same node to run GPU benchmarks simultaneously corrupts hardware timing measurements and risks OOM/driver resets.
- Conversely, **static session-level node assignment** with a node-wide GPU lock creates severe transient queue imbalance even when session counts per node are identical: across `16` concurrent rollouts (`4` sessions per node across `4` Mac mini M4 nodes), mean per-session tool waiting reaches **`21.0` minutes** out of `45.1` minutes total session time, skewing from **`32.7` minutes** on the busiest node to **`13.3` minutes** on the least busy node (`67.6` minutes batch completion).

The fix is to **keep session ownership local while scheduling exclusivity at the individual command boundary**:
1. Split commands into **parallel** CPU/workspace operations (immediate local execution) vs. **serial** build/benchmark operations (`1` active FIFO serial slot per physical accelerator node).
2. Migrate **only waiting serial commands** across idle cluster nodes via a decentralized **three-phase `reserve -> claim -> commit` protocol** gated on shared-path portability and a measured migration-overhead floor.

---

## Procedure

### Step 1: Partition Commands into Parallel vs. Conservative Serial Slots

Wrap the agent harness's command executor so every tool invocation is classified *before* dispatch into one of two concurrency classes on its session's **owner node**:

1. **Parallel Class (Immediate Execution)**: Read-only file inspection, directory listing, text/AST search (`grep`, `rg`, `sed -n`), lightweight workspace edits, and metadata checks execute immediately on the owner node without acquiring the accelerator lock.
2. **Serial Class (Per-Node FIFO Accelerator Slot)**: Compilations, unit/numerical tests, kernel benchmarks, and profiling runs enter the owner node's FIFO serial queue, which admits **at most `1` active serial command per physical accelerator node** at any instant.
3. **Conservative Default**: Any unrecognized binary, shell pipeline, wrapper script, or compound command **must default to the Serial Class** so an unexpected kernel launch cannot run alongside an active benchmark on the same accelerator.

> **Critical Security Boundary Caveat**: Command-prefix allowlists and cooperative OS workspace wrappers (such as macOS `App Sandbox`) classify **timing/concurrency slots and accidental cross-session file hygiene only**—they are **not** hostile multi-tenant security boundaries! If agents execute untrusted or adversarial code, enforce Ring-0 container/VM/kernel isolation separately per [`agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) (*"DON'T: Use application-layer tripwires or PID signals as the containment boundary for a rogue agent"*).

### Step 2: Exclude Serial Queue Waiting from Active Session & Tool Timeouts

Track two distinct clocks for every rollout session and tool invocation:
- **Queue Wait Clock ($T_{\text{wait}}$)**: Time spent parked in the local FIFO serial queue (or undergoing reservation handshake before execution starts).
- **Active Execution Clock ($T_{\text{active}}$)**: Time spent in LLM inference, parallel command execution, and actively running inside a claimed serial slot.

Apply rollout and per-command timeout budgets (e.g., `3,600 s` session active budget, `600 s` per-tool active budget) **strictly to $T_{\text{active}}$**, never $T_{\text{active}} + T_{\text{wait}}$, while enforcing a separate infrastructure health watchdog on stalled slots. Otherwise, transient bursty contention on a busy node (`32.7` minutes cumulative queue wait) spuriously aborts healthy trajectories.

### Step 3: Screen Waiting Serial Commands for Cross-Node Portability

Before marking a queued serial command as `migratable`, run a deterministic path-portability screen:
1. Mount session workspaces and shared toolchains at **matching canonical paths** (or a deterministic path-rewriting root) across all cluster nodes.
2. Inspect the command arguments and working directory: if the command references **owner-local paths outside the shared namespace** (e.g., `/tmp` node-local sockets, unshared host caches, or node-pinned device handles), mark it **`owner-only`** (`non-migratable`) so it stays in the owner's local FIFO queue (in `metal_nbody` rollouts, `1,131` of `1,165` serial commands [`97.1%`] passed portability screening).
3. Ensure each session writes build artifacts into an isolated per-session directory (`workspace/<session_id>/`) so concurrent sessions and remote helpers never clobber object files or binaries.

### Step 4: Migrate Waiting Commands via Three-Phase `Reserve -> Claim -> Commit`

Never eagerly push running commands or use a single-point central lock manager if shared filesystem or RPC queues are available. Instead, run a **decentralized helper loop** on every node whose local serial slot is idle and whose local queue is empty:

```
Owner Node Queue (Waiting Command C)          Idle Helper Node H
────────────────────────────────────          ──────────────────
1. C sits in Owner FIFO queue (unstarted)
                                              2. Scan peer queues; check:
                                                 - C is migratable (shared paths)
                                                 - Est. runtime(C) > T_migration_floor
                                                 - H has free serial slot
                                              3. RESERVE: write short-TTL reservation
                                                 record & prepare sandbox on H
4. CLAIM: Owner queue atomically verifies ◄──    request claim(C, H, reservation_id)
   C is still waiting (not locally started
   or claimed by another helper) -> marks
   C as CLAIMED(H) (~0.97 ms median)
                                              5. COMMIT: transition C to RUNNING_REMOTE(H)
                                                 (~3.89 ms median), execute C inside H's
                                                 exclusive serial accelerator slot, write
                                                 stdout/stderr/exit_code + artifacts back
6. Owner sees completion receipt & resumes
   agent turn; if TTL expires before
   CLAIM/COMMIT, Owner reclaims C locally.
```

**Mandatory Migration-Overhead Floor ($T_{\text{mig}}$)**:
- Measure end-to-end remote handoff cost on your cluster fabric before enabling migration. Over gigabit Ethernet + SMB on 4 M4 Macs, full timed migration adds **`1.86 s` at `0 MiB` workspace payload** and **`2.16 s` at `16 MiB`** (`0.818 s` median lookup + reservation + sandbox preparation, `0.97 ms` `claim`, `3.89 ms` `commit`, and `0.935 s` cleanup/communication/result-polling).
- **Do not migrate sub-second or ultra-short serial commands** whose expected execution time is below $T_{\text{mig}}$ (`~2 s` on LAN+SMB), and require a command to still have remaining queue wait exceeding $T_{\text{mig}}$ before a helper reserves it. On balanced loads where every node already has `0` waiting commands, helpers stay idle (`0` migrations) and local dispatch incurs zero migration tax (`6.61 s` dynamic vs. `6.62 s` static across 4 nodes).

### Step 5: Validate Scheduling Policies via Paired Trace-Driven Replay

Because live LLM rollouts exhibit high stochastic variance in reasoning turns and kernel edits, comparing two live runs conflates policy variance with scheduler gains. Validate queue policies (`T_mig` thresholds, polling intervals, helper backoff) offline first:
1. Record a **live static rollout trace** logging exact per-turn LLM generation durations, parallel tool durations, serial tool active runtimes, workspace payload sizes, and portability flags.
2. Build a **discrete-event trace replayer** that holds every trajectory's exact model-phase and active command durations fixed while simulating per-node queues and `reserve -> claim -> commit` handoffs.
3. Verify zero-drift fidelity by replaying the static baseline against the live trace first (target `< 10 ms` drift; Metal Sandbox achieved **`< 1 ms` session finish-time error** and **`< 8 ms` total tool-waiting error** across `16` trajectories / `1,279` tool calls).
4. Sweep migration cost scales (`0.5x–4x`), polling intervals, and random seeds in paired replay to confirm both **mean queue-wait reduction** and **donor-node fairness** (ensuring idle-node borrowing slashes worst-node tail queues without starving donor sessions) before deploying to live training/evaluation clusters.

---

## Quantitative Reference Profile (`arXiv:2611.17294`)

| Workload / Regime (`4` Mac mini M4 `32 GiB` Nodes) | Static Session Placement | Dynamic `Reserve-Claim-Commit` | Measured Delta |
|:---------------------------------------------------|:------------------------:|:------------------------------:|:---------------|
| **Balanced `12`-cmd batch (`2 s` kernel loop, `4` nodes)** | `6.62 s` (`6,520` cmd/hr) | `6.61 s` (`6,540` cmd/hr, `0` mig.) | Zero local overhead on balanced load |
| **Concentrated `12`-cmd batch (`2 s` loop on 1 node)** | `25.3 s` median; `21.9 s` `p95` wait (`1,710`/hr) | **`15.1 s`** median; **`11.9 s`** `p95` wait (`2,870`/hr) | **`-40.4%` batch time (`1.68x` tput), `-45.5%` `p95` wait** |
| **Concentrated `6`-cmd long batch (`6 s` loop on 1 node)** | `36.8 s` median (`588` cmd/hr) | **`18.0 s`** median (`1,200` cmd/hr, `4/6` mig.) | **`-51.1%` batch time (`2.05x` throughput)** |
| **`16` `metal_nbody` agent rollouts (`1,165` serial, `114` par.)** | `67.6 min` batch; `45.1 min` session; `21.0 min` wait (`32.7` vs `13.3 min` node skew) | **`52.5 min`** batch; **`41.4 min`** session; **`17.1 min`** wait (`#A` wait `32.7 -> 15.8 min`, `276` mig.) | **`-22.3%` batch time, `-18.8%` mean wait** (`15.6%–27.8%` batch across `166` sensitivity runs) |

---

## Environment Caveats & Failure Modes

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| **Negative migration ROI on short commands** | Migrating `0–0.25 s` checks over a `1.86–2.16 s` LAN/SMB handoff path | Gate helper reservation on command runtime / remaining queue wait $> T_{\text{mig}}$ (`~2 s` on SMB; recalibrate on NFS/JuiceFS/NVMe-oF) |
| **Silent GPU timing corruption** | Unrecognized test script or custom binary classified as `parallel` | Make `serial` the fail-closed default for any command not on a strict read-only/edit-only parallel allowlist |
| **Broken hard-coded node-local paths** | Migrated build references `/tmp/...` or unmounted host SDK path | Enforce Step 3 path-portability screening (`owner-only` fallback) and verify identical toolchain versions across all nodes |
| **Double execution or orphaned commands on helper crash** | Helper reserves a command and disconnects mid-handshake | Require atomic owner-side `claim` + short reservation TTL expiry so un-committed commands revert cleanly to the owner's FIFO queue |
| **Mistaking workspace hygiene for security isolation** | Relying on macOS `App Sandbox` or command classification against untrusted code | Treat `App Sandbox` (which leaves certain macOS app-launch paths outside containment and provides no physical GPU memory isolation) strictly as cooperative rollout hygiene; wrap untrusted workloads in VM/container sandboxes |

## Cross-References

- [`speculative-sandbox-scheduler`](../speculative-sandbox-scheduler/SKILL.md) — Complementary: hides container cold-start latency during LLM token streaming (`SpecBox`), whereas this skill eliminates cross-node serial accelerator queue imbalance after tool calls are emitted
- [`transactional-coding-sandbox`](../transactional-coding-sandbox/SKILL.md) — Complementary filesystem snapshot/rollback semantics for local coding sandboxes
- [`agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — Mandatory security boundary rules separating concurrency scheduling from hostile-code containment

## Sources

- [Metal Sandbox: Isolated Execution and Command Scheduling for GPU Coding Agents on Apple Silicon](https://arxiv.org/abs/2611.17294) (`arXiv:2611.17294`, `src:2611-17294v1`)
