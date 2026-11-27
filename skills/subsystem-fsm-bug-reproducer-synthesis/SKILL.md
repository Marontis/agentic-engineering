---
name: subsystem-fsm-bug-reproducer-synthesis
description: >-
  Defensively validate AI-generated bug review reports before maintainer triage
  by inducing per-subsystem reproduction finite-state machines from historical
  bug replays, splitting disposable-VM build configuration and user-space test
  generation across single-active Environment and PoC agents with stale-log
  purging, and gating escalation on sanitizer call-trace matching (@Match).
  Derived from ReproCue (arXiv:2611.34142).
source: "arXiv:2611.34142"
repository: "https://github.com/Marontis/agentic-engineering"
license: CC-BY-4.0
---

<!-- Licensed under CC BY 4.0 | Source: Marontis/agentic-engineering | Origin: arXiv:2611.34142 -->

# Subsystem-FSM Bug Reproducer Synthesis

> **Defensive Scope (`output/AGENTS.md`)**: This procedure is strictly scoped to **defensive patch-review verification, CI pre-merge bug triage, and regression test synthesis** inside isolated disposable virtual machines (`QEMU` + sanitizers). It prohibits kernel/target source modification, privileged fault injection, and weaponized exploit escalation—synthesizing minimal user-space fault-matching reproducers solely to filter false-positive AI code reviews before maintainer submission.

## When to Use

Use this procedure when operating **automated AI code-review bots, static/LLM patch scanners, or pre-merge CI bug detectors** across large modular systems (OS kernels, browser/JS engines, database storage/network subsystems, compilers, or virtualized runtimes) where unverified text reports suffer high false-positive rates and low maintainer trust:

- **Filtering AI mailing-list and pull-request bug reports**: Attaching deterministic, runnable sanitizer-verified reproducers so human maintainers only triage defects with proven reachability (`69.4%` maintainer confirmation on verified reports vs. `9.3%` for text-only `Sashiko` AI reviews in `arXiv:2611.34142`).
- **Subsystem-heterogeneous build and test environments**: Reproducing bugs where default `x86` CI containers fail because `> 60%` of defects require non-default cross-compilation (`AArch64`, `RISC-V`, `ARM32`), SMP race configs, subsystem flags (`CONFIG_DEBUG_INFO_BTF`, fault-injection slabs), or virtual hardware (`mac80211_hwsim`, `BlueZ`).
- **Generating regression tests before automated patch synthesis**: Constructing a fault-trace-matched (`@Match`) dynamic oracle to pair with semantic functional tests before evaluating candidate bug fixes.

**When NOT to use**:
- **As a standalone post-patch repair sufficiency oracle**: Eliminating a synthesized crash reproducer proves symptom suppression, *not* root-cause repair (`1.83x` solve-rate inflation in `PatchBench`; always pair reproducer non-triggering with functional preservation suites per [`../../rules/agent-evaluation-quality.md`](../../rules/agent-evaluation-quality.md), `"DON'T: Validate repairs using crash suppression alone"`).
- **Pure business-logic or UI specification bugs with zero sanitizer/assertion signal**: When defects involve visual layout or domain-rule discrepancies rather than crash/sanitizer/assertion traces, use isolated specification verifiers ([`certified-task-verifier-harness`](../certified-task-verifier-harness/SKILL.md)) or blind boundary differential tests ([`post-migration-behavioral-differential-testing`](../post-migration-behavioral-differential-testing/SKILL.md)).
- **Systems lacking historical bug-fix / reproducer archives (`< 2` replayable trajectories per subsystem)**: Offline FSM induction prunes states and recovery edges occurring `< 2` times; bootstrap with a `4`-state generic skeleton (`analyze -> env -> poc -> run`) until subsystem replay logs accumulate.

---

## Core Insight

Text-only AI patch review floods maintainers with plausible-sounding false alarms: on Linux kernel mailing lists, `55.29%` of patches receive no response at all, and Google's `Sashiko` AI review bot received replies on only **`21.2%`** of threads (`17.5%` in a `§I` contribution-bullet typo in `arXiv:2611.34142`; `21.2%` across `Table VI` and main prose) with **`9.3%`** confirmed bugs (`16/48` audited threads contained wrong AI reviews). Yet off-the-shelf directed fuzzers (`SyzDirect`, `24 h`/case) and unconstrained coding agents (`K-Repro`, `Claude Code`) struggle to validate patch reviews (`9.0%–13.0%` `@Match`): `SyzDirect` triggered `27/100` crashes of which **`18/27` (`66.7%`) were unrelated false positives**, single-context agents drowned in `380–400`-step kernel build logs, and unconstrained `Claude Code` manufactured **`8/24` invalid crashes** by editing kernel source or injecting privileged faults.

**ReproCue** (also labeled `KAVER` — *Kernel AI Review Via Executable Reproduction* — in `Fig. 1` and `Footnote 1` of `arXiv:2611.34142`) solves this via two structural decouplings:
1. **Offline Per-Subsystem Reproduction FSM Induction**: Replaying `806` historical `Syzbot` + `CVE` bugs (`317` successful trajectories across `8` subsystems) distills subsystem-specific state graphs (`e.g.`, `load -> verify` in `BPF`; `mkfs -> mount` in `File System`), failure-recovery back-edges, and state-local `(error, fix)` guidelines—preventing cross-subsystem prompt dilution (`49%` `@Match` vs. `14%` without FSM and `21%` with static review guidelines).
2. **Single-Active-Agent `Environment` / `PoC` Isolation with Stale-Log Purging and `@Match` Gating**: A deterministic controller runs **one agent at a time** inside disposable `QEMU` + `KASAN` VMs (`61/100` reviews required non-default environments; `-38 pp` without `Environment Agent`), purges stale execution logs whenever `Environment Agent` rebuilds the target (`-29 pp` when collapsed into a single `ReproCue_flat` agent), restricts `PoC Agent` to unprivileged user-space triggers, and accepts **only** sanitizer faults whose call trace matches the reviewed code site (`@Match`). Across `100` `Sashiko` reviews (`DeepSeek-V4-Flash`), `ReproCue` synthesized **`49/100` (`49.0%`) `@Match` reproducers** (`52/100` `@Crash`, **`94.2%` crash-to-review precision**, `$0.210`/case avg, **`$0.43` per matched PoC**), lifting maintainer replies to **`71.4%` (`35/49`)** and confirmed/fixed bugs to **`69.4%` (`34/49`, `34.0%` end-to-end across all `100` raw reviews—`3.66x` text-only `Sashiko`)**, while reaching **`64/100`** (`68.0%` `Syzbot` at `89.5%` precision; `60.0%` `CVEs` at `100.0%` precision) on disjoint ground-truth bugs.

---

## Step-by-Step Procedure

### Step 1: Induce Per-Subsystem Reproduction FSMs Offline from Historical Bug Replays

Partition your repository into $K$ architectural subsystems (e.g., `Core Kernel`, `Memory Management`, `File System`, `Network`, `BPF`, `Drivers`, `Firmware`, `Other` via `MAINTAINERS` path mappings) and mine historical bug reports (`Syzbot`, sanitizer CI logs, past regression commits) inside disposable VMs:

1. **Map replay steps onto shared + subsystem-special states**: Anchor every trajectory on four shared states—`analyze` (trace defect reachability & preconditions), `env` (configure/compile target & boot VM), `poc` (author & compile user-space trigger), and `run` (execute inside VM & parse sanitizer trace)—plus subsystem-specific `special:<cmd>` states (`load`, `verify`, `mkfs`, `mount`, `netns_setup`) that appear in **`>= 2` successful trajectories** for that subsystem.
2. **Extract failure-recovery back-edges and state-local `(error, fix)` pairs**: Whenever a trajectory fails in state $A$, visits intermediate states $R = (r_1, \dots, r_m)$, and subsequently succeeds at $A$, add directed recovery back-edges $A \to r_1$ and attach concise `(error_signature -> corrective_action)` guidelines to `G[r]` (e.g., verifier rejection in `BPF` routing back to `env` for `CONFIG_DEBUG_INFO_BTF=y`, or `ENOSPC`/mount failure routing back to `mkfs` options).
3. **Support-threshold pruning (`>= 2`)**: Prune any state, transition edge, or `G[r]` guideline observed in **`< 2` historical trajectories** so one-off hallucinations do not pollute online prompts. When updating persistent FSM artifacts across historical batches, gate changes through `"DO: Pass every self-modification through one acceptance gate"` in [`../../rules/recursive-improvement.md`](../../rules/recursive-improvement.md).

### Step 2: Run Single-Active-Agent `Environment` and `PoC` Roles Under FSM Tool Scoping

Given a new AI-generated bug review `(patch_diff, suspected_function, defect_hypothesis)`, route by touched file paths to subsystem FSM $\mathcal{M}_s = (S_s, E_s, G_s)$ and run an orchestrator loop (`<= 500` total steps, disposable `QEMU` VM with `KASAN`/`UBSAN`/assertions enabled) that activates **strictly one agent at a time** with **state-scoped tools and `G_s[state]` guidelines only**:

| Active Role | Assigned FSM States | Scoped Toolset | Boundary Contract |
|:---|:---|:---|:---|
| **`Environment Agent`** | `env` + VM/config build states | `fetch_commit`, `configure_build` (`Kconfig` / cross-arch `AArch64`/`RISC-V`/`ARM32` / SMP / fault-injection slabs / virtual buses `mac80211_hwsim`), `build_target`, `start_vm`, `stop_vm` | **Cannot** write PoC code. Emits a compact structured `env_summary` (enabled configs, architecture, active virtual interfaces, device nodes) upon clean VM boot. |
| **`PoC Agent`** | `analyze`, `poc`, `run` + user-space setup states (`mkfs`, `load`) | `read_target_source` (**read-only**), `compile_reproducer` (user-space C / Syzlang harness), `copy_to_vm`, `execute_in_vm`, `read_sanitizer_log` | **Hard ban on target/kernel source edits, custom kernel modules, or privileged fault injection** (`8/24` unconstrained `Claude Code` crashes came from cheating the boundary!). |

### Step 3: Purge Stale Execution Logs Across Environment Rebuilds

Whenever `PoC Agent` diagnoses a missing build flag, disabled subsystem driver, or architecture mismatch in state `run`/`analyze` and transitions along a recovery back-edge to `env`:

1. Suspend `PoC Agent` and hand only the structured `env_request` (missing symbol/config + observed error) to `Environment Agent`.
2. After `Environment Agent` rebuilds and reboots the clean VM snapshot, **purge all prior-build execution outputs and stale failure logs** from `PoC Agent`'s working context, injecting only the updated `env_summary` and current `G_s[state]` guidelines. Keeping raw build/boot transcripts and obsolete VM errors in a single shared context (`ReproCue_flat`) dropped `@Match` by **`-29.0 pp` (`49% -> 20%`)** while inflating average steps from `136.0` to `380` (`arXiv:2611.34142`, `Table VIII`).

### Step 4: Verify Sanitizer Call-Trace `@Match` Before Maintainer Escalation

Never forward a reproducer to human maintainers on `@Crash` (any panic, hang, or sanitizer report) alone:

1. **Deterministic + semantic `@Match` check**: Parse the VM's `KASAN` / `UBSAN` / `BUG` splat and require **both** (a) the fault type (`use-after-free`, `out-of-bounds`, `null-ptr-deref`, `locking/race assertion`) and (b) the crashing or allocation/free **call stack frames** to intersect the reviewed patch's modified/implicated functions and defect mechanism.
2. **Reject brute-force resource exhaustion**: Filter out reproducers that merely trigger generic OOM killers or unbounded CPU starvation without exercising the reviewed state transition (`1/35` maintainer-replied PoCs in `arXiv:2611.34142` was rejected for brute-force triggering).
3. **Quarantine unmatched AI reviews**: Hold back AI code-review comments that fail to reach `@Match` within budget (`51/100` `Sashiko` reviews in `arXiv:2611.34142`) or downgrade them to internal low-priority queues rather than emailing maintainers unverified prose. Attach the minimal standalone C/Syzlang reproducer, exact `.config` delta, `QEMU` launch flags, and matching sanitizer trace to every escalated report.

---

## Environment Caveats

- **Observational selection denominator in maintainer confirmation rates**: In `arXiv:2611.34142` (`Table VI`), `ReproCue`'s **`69.4%` (`34/49`)** confirmation rate (`71.4%` reply rate) is conditioned on the `49/100` `Sashiko` reviews for which `@Match` synthesis succeeded; across all `100` raw `Sashiko` reviews, end-to-end confirmed bug yield is **`34.0%` (`34/100`)**—still **`3.66x`** higher than text-only `Sashiko`'s `9.3%` while sparing maintainers `51` unverified threads and cutting confirmation turnaround from `~50 h` to `~1 h`.
- **Hardware-dependent drivers remain bounded by virtual-device fidelity**: While `QEMU` virtual devices (`mac80211_hwsim`, `BlueZ`, `virtio`) unlocked `5/10` `Drivers` reviews (`vs. 0/10` for `K-Repro` and `SyzDirect`), bugs requiring proprietary physical PCIe/SoC peripherals without `QEMU` emulation cannot be dynamically reproduced in standard VMs.
- **Compute and cost profile**: Offline FSM induction is a one-time subsystem investment (`806` historical bugs); online verification on `DeepSeek-V4-Flash` averaged `72.8 min` and **`$0.210`/review** (`62.7 min`, `111.0` steps, `$0.156` on matched cases; `$0.43` per verified `@Match` PoC vs. `$1.67`/PoC on `Claude Code`).
- **Manuscript naming & table notes (`arXiv:2611.34142`)**: Footnote 1, `Fig. 1`, and Ref `[15]` refer to the system as `KAVER` (*Kernel AI Review Via Executable Reproduction*); `§I`'s contribution bullet cites `17.5%` for `Sashiko`'s reply rate where `Table VI` and `§I`/`§V-B2` prose establish **`21.2%`**; and in `Table VIII`, full `ReproCue` subgroups split by `@Match` (`49`/`51`) whereas ablated timing rows (`19/81`, `27/73`, `15/85`, `42/58`, `24/76`) split by `@Crash`.

---

## Failure Modes

- **Escalating `@Crash` without call-trace `@Match` verification**: Directed fuzzing (`SyzDirect`) produced `27/100` crashes on `Sashiko` targets, but **`18/27` (`66.7%`)** were unrelated background/syzkaller crashes (`9%` `@Match`), and `ReproCue_flat` hit `42%` `@Crash` with only `20%` `@Match`—sending unmatched crashes destroys maintainer trust as fast as text-only hallucinations.
- **Collapsing `Environment` and `PoC` into one context (`ReproCue_flat`)**: Allowing one agent to hold all build/VM/PoC tools without stale-log purging slashed `@Match` from **`49%` to `20%`** and nearly tripled step counts (`136.0 -> 380`).
- **Using a static default `x86` VM (`w/o Environment Agent`)**: Dropped `@Match` by **`-38.0 pp` (`49% -> 11%`)** because `61/100` kernel patch reviews required custom `Kconfig` options, cross-architecture builds, or virtual subsystem devices.
- **Replacing the learned subsystem FSM with static review checklists (`ReproCue_review`) or unconstrained transitions (`w/o FSM`)**: Static subsystem prose without state-scoped transitions and failure back-edges reached only **`21%` `@Match`** (`290` steps), and removing the FSM entirely collapsed `@Match` to **`14%` (`-35.0 pp`)**.
- **Permitting target-tree writes inside the reproduction sandbox**: Without a hard read-only mount on target source and privilege boundaries on VM execution, general coding agents (`Claude Code`) "reproduce" bugs by inserting `BUG_ON()` edits or privileged fault injections (`8/24` crashes invalid).

---

## Cross-References

- **Rules**:
  - [`../../rules/agent-evaluation-quality.md`](../../rules/agent-evaluation-quality.md) — `"DON'T: Validate repairs using crash suppression alone"` (once a `@Match` reproducer confirms a bug, require dual reproducer + semantic regression tests to validate any subsequent fix)
  - [`../../rules/agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — `"DO: Embed AI vulnerability discovery inside maintainer workflows with human-reviewed patches and structural hardening rather than relying on bulk advisories or model access gates"` (`SoK`, `arXiv:2611.26601`)
  - [`../../rules/recursive-improvement.md`](../../rules/recursive-improvement.md) — `"DO: Pass every self-modification through one acceptance gate"` (for persistent FSM library updates)
- **Spec Templates**: [`../../specs/adk-eval-quality-gate.spec.md`](../../specs/adk-eval-quality-gate.spec.md) and [`../../specs/agent-sandbox.spec.md`](../../specs/agent-sandbox.spec.md)
- **Related Skills & Briefs**:
  - [`certified-task-verifier-harness`](../certified-task-verifier-harness/SKILL.md) — Isolated five-gate (`G1–G5`) task verifier synthesis (`Veritas`)
  - [`cve-history-executable-detection`](../cve-history-executable-detection/SKILL.md) — Mining historical vulnerability commits into executable regression detectors
  - [`execution-driven-environment-repair`](../execution-driven-environment-repair/SKILL.md) — Iterative sandbox environment build/dependency repair (`WEFT`)
  - [`post-migration-behavioral-differential-testing`](../post-migration-behavioral-differential-testing/SKILL.md) — Blind boundary differential testing (`W_3`) for runtime/API migrations
  - [`sok-llm-capability-software-vulnerability-research`](../../research-briefs/sok-llm-capability-software-vulnerability-research.md) — Why uncurated bulk AI reports go `74%–95%` unfixed (`5%–25%` fix rate) vs. `58%–94%` for curated/owner-integrated workflows (`arXiv:2611.26601`)

---

## Sources

- Wu, X., Ni, Y., Sun, H., Yuan, Y., & Li, S. (2026). *Reproducer Synthesis for AI-Reported Bugs in the Linux Kernel*. `arXiv:2611.34142` (`src:2611-34142v1`).
