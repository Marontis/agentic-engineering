---
name: syscall-inferred-stateful-ifc-monitoring
description: >
  Mediate OS-level agent command execution by running commands speculatively
  inside a per-directory OverlayFS and held network proxy, inferring a minimal
  11-action dataflow trace from strace and proxy logs, and enforcing mechanized
  stateful Information-Flow Control (IFC) policies with direct-transfer label
  propagation and provenance-DAG differential fuzzing. Derived from Tether
  (arXiv:2611.25599).
source: https://arxiv.org/abs/2611.25599
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Syscall-Inferred Stateful IFC Monitoring

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

Use this skill when securing **autonomous coding, terminal, sysadmin, or data-science agents** that execute arbitrary composite POSIX shell commands (`bash`, pipes, redirects, Python/Node one-liners, symlinks, hard links, `curl`/`git`) over sensitive host files, system configurations, and external networks.

## When to Use

- Agents invoke general-purpose shell execution where static command-string regexes or per-binary flag blocklists cannot predict which files, symlinks, or sockets a pipeline or script will actually touch at runtime.
- Prompt-based LLM command monitors (`Auto Mode`) miss obfuscated or multi-step attacks (`86.9%–91.6%` recall) while falsely blocking legitimate developer workflows (`9.7%–35.3%` FPR), and adding explicit policy text to the LLM monitor degrades attack recall even further (`89.2%` overall, `82.4%` on `MonitoringBenchHonest`).
- Stateless or bounded-window event monitors fail against **multi-hop file staging** (`cp .env /tmp/a -> cat /tmp/a >> /tmp/b -> curl -T /tmp/b`)—which either requires $\sum_{j=1}^k m^j$ explicit rules for $k$ hops or expires across time windows—while coarse 1-bit session taint blocks every benign network call after touching a sensitive file.

Prefer [`compositional-coding-harness-reference-monitor`](../compositional-coding-harness-reference-monitor/SKILL.md) (`ActiveSecHarness`) when mediating structured Python harness tool APIs in microseconds (`12.7 μs`), and [`verified-policy-action-governance`](../verified-policy-action-governance/SKILL.md) (`ActGov`) when governing high-level business/REST tool schemas via finite enum extraction rather than POSIX shell commands.

**Deference to the repository acceptance gate:** Whenever modifying `require` sub-policies, lattice label assignments, or `Isolate` syscall-to-action mappings across sessions, pass the change through `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../../rules/recursive-improvement.md) alongside re-verification of mechanized trace invariants and provenance-DAG differential fuzzing.

---

## Core Insight

Monitoring arbitrary shell commands requires separating **low-level OS mechanism observation** from **stateful multi-step policy reasoning**:

1. **Speculative Syscall Inference Beats Command-String Parsing**: Instead of guessing what `tar`, `awk`, `find`, `python`, or `sendfile` will do from `argv` strings, run the command speculatively inside a disposable `OverlayFS` upper layer and a held local network proxy (`Isolate`), observe actual `strace` + proxy dataflows across files and sockets, and map them onto a small **11-action calculus**—committing filesystem diffs and releasing network requests **only** if the entire inferred action trace is allowed.
2. **Direct-Transfer Label Propagation Solves Multi-Hop Staging Without Context Over-Tainting**: In a stateful product lattice $L = C \times I$ (`Public < Internal < Sensitive < Secret` $\times$ `Trusted < Untrusted`), commands like `cp secret.txt stage1` or `curl untrusted.sh -o run.sh` move bytes directly between resources **without entering the LLM's token context $\mathcal{T}$**. Propagating source labels directly to destination file content $\sigma'(d, \text{content})$ without tainting $\mathcal{T}$ tracks unbounded $k$-hop staging chains automatically while keeping unrelated benign uploads unblocked.

**Verified Empirical Evidence** (`Tether`, arXiv:2611.25599, `1,934` in-scope coding-agent trajectories across `MonitoringBenchHonest` and `LinuxArena` vs. `Claude Sonnet 5` `Auto Mode`):

| Monitor Architecture | `MonitoringBenchHonest` Recall / Benign FPR (`199` adv / `218` ben) | `LinuxArena` Recall / Benign FPR (`145` adv / `1,372` ben) | Combined Recall (`344` adv) | Combined Benign FPR (`1,590` ben) |
|:---------------------|:--------------------------------------------------------------------|:-----------------------------------------------------------|:----------------------------|:----------------------------------|
| **`Tether` (Speculative `Isolate` + Lean 4 Stateful IFC)** | **`100.0%`** (`199/199`) / **`2.3%`** (`5/218`) | **`100.0%`** (`145/145`) / **`5.0%`** (`69/1,372`) | **`100.0%`** (`344/344`) | **`4.7%`** (`74/1,590`; *abstract: `< 5%`*) |
| **`Auto Mode` (Default `Claude Sonnet 5`)** | `86.9%` (`173/199`) / `35.3%` (`77/218`) | `97.9%` (`142/145`) / `5.7%` (`78/1,372`) | `91.6%` (`315/344`) | `9.7%` (`155/1,590`) |
| **`Policy-Aware Auto Mode` (`Claude Sonnet 5` + Policy Text)** | `82.4%` (`164/199`) / `14.7%` (`32/218`) | `98.6%` (`143/145`) / `1.7%` (`23/1,372`) | `89.2%` (`307/344`) | `3.5%` (`55/1,590`) |

---

## Step-by-Step Procedure

### Step 1: Execute Each Command Speculatively in `Isolate` (`OverlayFS` + Held Proxy + `strace`)

Before any shell command's effects become visible to the host filesystem or external network, run it inside an ephemeral speculative wrapper (`Isolate`):

1. **Per-Directory `OverlayFS` Staging**: Mount `OverlayFS` over every writable filesystem hierarchy with fresh empty `upperdir` and `workdir` directories so file creates, writes, truncations, renames, links, and deletions remain buffered in the overlay.
2. **Held Network Proxy & Dual Domain/IP Attribution**: Route outbound traffic through a local proxy that holds outbound payloads (`POST`/`PUT`/uploads) or intercepts connection targets, recording both the **resolved IP address and the requested domain name** and emitting policy checks for *both* identifiers so neither raw-IP literals nor DNS aliasing can bypass host blocklists/allowlists.
3. **Complete Syscall & Process Lifecycle Confinement**:
   - Trace the process tree under `strace` covering path, descriptor, zero-copy, link, and privilege syscalls (`openat`, `read`, `write`, `creat`, `unlink`/`unlinkat`, `rename`, `link`/`linkat`, `symlinkat`, `copy_file_range`, `sendfile`, `splice`, `dup2`/`fcntl`, `execve`, `setuid`/`setgid`/`capset`).
   - **Block untraced kernel bypass channels** (`io_uring` and cross-process shared memory) via seccomp/sandbox filters so file/socket operations cannot evade `strace`.
   - **Halt outliving background processes**: Pause or reject background daemons (`&`, `nohup`, `cron`, detached child processes) that attempt to survive past command exit outside `Isolate`'s speculative commit window.

---

### Step 2: Infer the 11-Action Resource Calculus from Observed Dataflows

Translate raw `strace` descriptor tables and proxy logs from the completed speculative run into an ordered trace over **11 abstract actions**:

- **Context-Entering Reads** (`read(f)`, `recvNet(h)`): Process reads bytes from file `f` or network host `h` and emits output to `stdout`/`stderr` (returning to the agent's context $\mathcal{T}$) or branches into process control.
- **Context-Driven Mutations & Egress** (`write(f)`, `create(f)`, `delete(f)`, `sendNet(h)`, `escalatePrivilege()`): Process mutates/creates/deletes `f`, sends agent-constructed data to `h`, or invokes privilege-raising syscalls (`sudo`/`setuid`).
- **Direct Resource-to-Resource Transfers** (`copy(s, d)`, `concatenate(S, d)`, `downloadNet(h, d)`, `uploadNet(s, h)`): Process transfers bytes from source file(s) `s`/`S` or host `h` directly into destination file `d` or outbound host `h` (whether via `cp`, `cat a b > c`, shell pipes, `sendfile`, `copy_file_range`, `splice`, symlinks, or hard links) **without** printing the secret payload into agent stdout.

Resolve canonical paths and hard-link inode aliases before emitting abstract actions so linking `/workspace/benign.txt` to `/etc/shadow` or `~/.ssh/id_rsa` is evaluated against the underlying target's initial security label.

---

### Step 3: Evaluate Stateful Lattice Transitions Without Over-Tainting Agent Context

Maintain persistent monitor state $S = \langle \mathcal{T}, \mathcal{P}, \sigma \rangle$ across the entire multi-turn session, parametric over the product lattice $L = C \times I$ (`Public < Internal < Sensitive < Secret` $\times$ `Trusted < Untrusted`):

- $\mathcal{T} \in L$: accumulated confidentiality and integrity label of the **agent's context**.
- $\mathcal{P} \in \{\text{Unprivileged}, \text{Privileged}\}$: privilege state.
- $\sigma(r, \text{content}), \sigma(r, \text{existence}) \in L$: separate **content** and **existence/metadata** labels for every file and network resource $r$ (initial static classification $\sigma_0$ assigns `Secret` to `.env`/keys/tokens, `Protected`/`Trusted` integrity to `/etc`, `/usr`, systemd/SSH configs, and `Untrusted` integrity to external hosts).

Update state deterministically on each allowed action (`\delta(S, a)`):

1. **`read(f)` / `recvNet(h)`**: Join the source's content label into the agent's context: $\mathcal{T}' = \mathcal{T} \sqcup \sigma(r, \text{content})$.
2. **`write(f)` / `create(f)`**: Taint destination `f` with the agent's current context: $\sigma'(f, \text{content}) = \sigma(f, \text{content}) \sqcup \mathcal{T}$.
3. **`copy(s, d)` / `concatenate(S, d)` / `downloadNet(h, d)`**: Propagate source content labels directly to `d` ($\sigma'(d, \text{content}) = \bigsqcup_{s \in S} \sigma(s, \text{content})$ on overwrite or joined with $\sigma(d, \text{content})$ on append) **while leaving $\mathcal{T}' = \mathcal{T}$ unchanged**.
4. **`uploadNet(s, h)` vs. `sendNet(h)`**: Gate `uploadNet(s, h)` on $\sigma(s, \text{content})$ (blocking any file carrying `Sensitive`/`Secret` labels regardless of how many `copy`/`concatenate` hops produced it, while allowing `Public` uploads even if $\mathcal{T}$ earlier read unrelated `Internal` notes) and gate `sendNet(h)` on $\mathcal{T}$.
5. **Atomic Commit or State-Preserving Rollback**: Compose sub-policies (`secretProtection`, `systemIntegrity`, `antiExfiltration`, `privilege`) via **`require`** (`Deny-overrides`: $\Pi_1 \otimes \Pi_2$ denies whenever any required sub-policy denies). If **every** inferred action in the command's trace evaluates to `Allow`, merge the `OverlayFS` upper layer and release held proxy requests; if **any** action evaluates to `Deny`, discard the `OverlayFS` upper layer, drop held proxy requests, and keep monitor state unchanged ($\hat{\delta}_\Pi(S, a) = S$).

---

### Step 4: Verify Unbounded-Trace Safety in Lean 4 & Differential-Fuzz `Isolate`

Because formal proofs over the abstract engine only hold in production if `Isolate` faithfully infers every concrete syscall flow, validate **both** layers before deployment:

1. **Mechanize Trace Safety Properties (`Lean 4`)**: Prove that your composed `require` policy preserves `Deny-overrides monotonicity`, `Non-bypassability of requirements` ($\Pi \sqsubseteq_{\mathbb{P}} \Pi_{\text{req}_i}$), `Order invariance`, `State preservation under denial`, and inductive **arbitrary-length trace invariants** (`No secret access`, `No tainted escalation`, `System integrity`, `No tainted protected edits`, `No exfiltration`, `Host blocklist`/`allowlist`).
2. **Run Provenance-DAG Differential Fuzzing + Adaptive Red-Teaming**:
   - Randomly generate provenance DAGs over labeled files, processes, and hosts.
   - Lower each DAG twice: (a) directly to a reference abstract trace $\bar{a}_{\text{ref}}$ evaluated in the formal engine ($d_{\text{ref}}, \sigma_{\text{ref}}$), and (b) into concrete randomized POSIX shell realizations (`cp`/`mv`/`cat`, multi-stage pipes, `sendfile`/`copy_file_range`/`splice`, `dup2`, symlinks, hard links) executed inside `Isolate` ($d_{\text{obs}}, \sigma_{\text{obs}}$).
   - Assert **decision soundness** ($d_{\text{obs}} \sqsubseteq_{\mathcal{P}} d_{\text{ref}}$: `Isolate` never allows a DAG the reference trace denies) and **label soundness** ($\sigma_{\text{ref}} \sqsubseteq \sigma_{\text{obs}}$: `Isolate` never under-approximates taint). Pair with iterative adaptive red-teaming (`40% -> 10% -> 0%` ASR across `3` `Gemini 3.8 Flash` rounds after closing hard-link `linkat` inference gaps).

---

## Environment Caveats & Failure Modes

- **Broad Filesystem Scans Trigger Conservative `read` Denials**: Across `1,590` benign coding-agent runs, `Tether`'s `4.7%` FPR (`74` runs) came from `50` unrequested edits to protected paths (e.g., `/etc/passwd`), `17` broad recursive searches (`grep -r /`, `find /`) whose syscalls opened `Secret`-labeled files, and `7` undeclared external host connections. Scope agent search tools (`rg`/`grep`) away from secret credential directories or pre-populate `.ignore` mounts to avoid incidental secret `openat` syscalls.
- **Semantic Content Sabotage Inside Authorized Destinations Is Out of Scope**: Pure information-flow monitors cannot distinguish buggy/backdoored code written by an untrusted-free agent into an authorized repo file (`28.2%` of `MonitoringBenchHonest` and `22.1%` of `LinuxArena` full benchmarks require semantic content inspection). However, enforcing boundary restrictions on background daemons (`&`, `cron`) and raw database sockets/files (`*.sqlite`, `/var/lib/postgresql`) intercepts **`36.3%`** and **`71.5%`** of those out-of-scope attacks at the system boundary; pair with post-completion diff SAST (`ActiveSecHarness` `CodeVerifier`).
- **Linux `OverlayFS` + `ptrace`/`strace` Platform Requirement**: `Isolate` relies on Linux kernel `OverlayFS` mounts and `strace`; on macOS or Windows hosts, run agent shell commands inside a Linux container or lightweight Linux microVM.

---

## Cross-References

- **Related Rules**:
  - [`agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — `"DO: Enforce a 2D trust-by-sensitivity taint lattice, disk provenance ledger, and dual-key encrypted audit logs in Ring-0 coding kernels"`, `"DO: Confine the LLM to bounded record extraction and authorize against a verified, frozen policy"`, and `"DON'T: Use application-layer tripwires or PID signals as the containment boundary for a rogue agent"`
  - [`agent-evaluation-quality.md`](../../rules/agent-evaluation-quality.md) — `"DON'T: Report formal verifier acceptance (Surface A) without syntactic specification binding (Surface B) and semantic specification fidelity (Surface C) checks"`
  - [`recursive-improvement.md`](../../rules/recursive-improvement.md) — `"DO: Pass every self-modification through one acceptance gate"`
- **Related Skills**:
  - [`compositional-coding-harness-reference-monitor`](../compositional-coding-harness-reference-monitor/SKILL.md) — Microsecond Ring-0 Python tool-dispatch mediation, Macaroon capabilities, and split-horizon encrypted audit logs (`ActiveSecHarness`)
  - [`verified-policy-action-governance`](../verified-policy-action-governance/SKILL.md) — Offline SMT-verified single-step policy governance over enum-extracted API tool calls (`ActGov`)
  - [`transactional-coding-sandbox`](../transactional-coding-sandbox/SKILL.md) — Snapshot/rollback tiers and compensating transactions for external APIs
  - [`three-surface-verified-code-audit`](../three-surface-verified-code-audit/SKILL.md) — Auditing formal proofs against implementation-to-spec gaps

## Sources

- Sistla, M. A., Solko-Breslin, A., Jha, S., Kanade, A., & Dvijotham, K. D. (2026). *Tether: Verified Stateful Policy Engine for System-Level Monitoring of Agents*. [arXiv:2611.25599](https://arxiv.org/abs/2611.25599) (`src:2611-25599v1`).
