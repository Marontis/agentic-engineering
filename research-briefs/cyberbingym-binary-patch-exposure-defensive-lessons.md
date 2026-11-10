# CyberBinGym: Can AI Agents Turn Binary Patches into Real Exploits?

> **Source**: [arXiv:2611.10723](https://arxiv.org/abs/2611.10723) — Lambang Akbar Wijayadi, Zhaoqi Xiao, Zhun Wang, Hongwei Li, Wenbo Guo, Heng Yin, Zhenkai Liang, Dawn Song (2026)
> **Praxis Source ID**: `src:2611-10723v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

Per the repository's offensive-security policy, benchmarks evaluating autonomous vulnerability exploitation are never distilled into offensive procedures or exploit-development workflows. This brief records **strictly defensive engineering lessons**: empirical capability boundaries of frontier coding agents on stripped native binaries, the concrete `1`-day exposure risk created by shipping binary security patches ahead of downstream fleet rollout, compiler/runtime binary hardening mitigations that cut successful exploitation by **`90%`**, and anti-reward-hacking sandbox isolation patterns for defensive security evaluation.

---

## Benchmark Scope & Defensive Threat Model

`CyberBinGym` evaluates whether general-purpose coding agents (`OpenAI Codex` with `GPT-5.6`, `Claude Code` with `Claude Opus 5`, and `Kimi Code` with `Kimi K3`, evaluated under vendor trusted-access research programs) can analyze **stripped native binaries without source code, debug symbols, or CVE advisories** across **`100` real-world 1-day tasks** drawn from **`53` open-source C/C++ projects** (`0.11–38.04 MiB`, median `1.60 MiB`; median `2,794` Ghidra functions and `8,116` call-graph edges; corresponding upstream fixes span a median of `1,003` source lines across `30.5` files). Tasks span `6` memory-safety defect classes (`40%` spatial, `20%` temporal, `15%` invalid pointer, `10%` invalid deallocation, `9%` uninitialized memory, `6%` type confusion) and `3` difficulty tiers (`20%` low, `40%` medium, `40%` high), measuring two distinct thresholds:
1. **Vulnerability Recovery (Differential PoC Crash)**: Producing an input that triggers a sanitizer fault on the unpatched build while exiting cleanly on the patched build.
2. **Audited Exploitation**: Demonstrating end-to-end control in an isolated unprivileged victim container, verified by manual trajectory inspection to exclude harness shortcuts.

---

## Key Defensive Findings

### 1. Sharp Capability Cliff Between Crash Discovery and End-to-End Control
Across the 100-task suite (`1,000` LLM-call cap), frontier agents are already highly capable binary crash-finders, while end-to-end control remains bounded (`64–79 pp` lower) and concentrated in frontier reasoning models:

| Agent System | Differential Crash Recovery (`Recover Vuln.`) | Audited End-to-End Exploitation | Mean Cost / Runtime / LLM Calls per Task |
|:-------------|:----------------------------------------------|:--------------------------------|:-----------------------------------------|
| **OpenAI Codex (`GPT-5.6`)** | **`88/100` (`88.0%`)** | **`20/100` (`20.0%`)** | `$28.11` / `2.13 h` / `286.2` calls |
| **Claude Code (`Claude Opus 5`)** | **`85/100` (`85.0%`)** | **`6/100` (`6.0%`)** | `$14.90` / `1.26 h` / `115.8` calls |
| **Kimi Code (`Kimi K3`)** | **`64/100` (`64.0%`)** | **`0/100` (`0.0%`)** | `$38.34` / `5.80 h` / `486.5` calls |
| **Cross-Agent Union** | — | **`22/100` (`22.0%`, `26` trajectories)** | — |

- **Test-time compute & multi-try scaling (`20`-task Codex ablation)**: Disabling extended reasoning drops crash recovery from **`90.0%` (`18/20`) to `30.0%` (`6/20`)** and reduces exploitation from **`25.0%` (`5/20`, `$31.42`) to `0.0%` (`0/20`, `$2.33`)**. Scaling independent attempts (`Success@k`) from $k=1 \to 2 \to 3$ raises crash recovery from **`68.3% -> 83.3% -> 90.0%`** and exploitation from **`11.7% -> 20.0% -> 25.0%`** (cumulative mean cost `$35.53 -> $71.06 -> $106.59`). Defensive risk assessments must budget for multi-sample frontier reasoning (`Success@k`), not single-shot zero-reasoning baselines.

### 2. Binary Patch-Diff Exposure Accelerates 1-Day Risk by `2.5x`
Even when source code and CVE details are withheld, shipping a stripped patched binary while downstream fleets remain unpatched materially lowers attacker cost and raises compromise rates:
- On the 20-task ablation subset, providing the patched binary alongside the vulnerable binary boosts `Codex` differential crash recovery from **`55.0%` (`11/20`) to `90.0%` (`18/20`)** and increases end-to-end exploitation by **`2.5x`—from `10.0%` (`2/20`) to `25.0%` (`5/20`)**—while *reducing* average per-task compute spend from **`$36.59` to `$31.42`**.
- Manual audit of all `26` successful trajectories across the full benchmark confirms that **`24/26` (`92.3%`) leveraged binary patch diffs**: **`17/26`** used function-level binary diffing *directly* to pinpoint the vulnerable routine, and **`7/26`** used patch comparisons *indirectly* to discard dead-end hypotheses and pivot faster (`2/26` unclear).

### 3. Compiler & Runtime Binary Hardening Cuts Exploitation by `90%` (`20/20 -> 2/20`)
To measure defensive mitigation leverage, the authors recompiled all **`20` baseline tasks successfully exploited by `Codex`** with modern binary protections enabled—**stack canaries, Position-Independent Executables (`PIE` + ASLR), full `RELRO`, non-executable stack (`NX`), and `_FORTIFY_SOURCE`**—alongside per-connection canary regeneration on network services:
- **End-to-end exploitation drops by `90%` (`20/20 -> 2/20`, `10.0%`)**, even though underlying defect triggering (`Recover Vuln.`) remains **`75.0%` (`15/20`)**.
- Per-connection canary regeneration defeated iterative byte-by-byte canary probing on network targets.
- **Why `2/20` still failed (residual defensive gap)**: Both surviving cases combined **writable non-stack control state** (application-level function pointers/cleanup structures outside stack-canary and GOT/`RELRO` coverage) with **runtime diagnostic/error output that leaked memory layout or pointer state**. Hardening compiler flags must be paired with pointer-authentication/CFI for heap callbacks and strict redaction of memory addresses in production error logs.

### 4. Defensive Evaluation Harness Lessons
For teams running authorized internal security benchmarks (compare [coding-agents-kernel-exploits](coding-agents-kernel-exploits.md) and [agent-sandbox-safety.md](../rules/agent-sandbox-safety.md)):
- **Strip sanitizers from agent-visible binaries**: Keep `ASan`/`UBSan` instrumentation strictly inside an external harness-only differential crash oracle so sanitizer metadata does not artificially assist binary localization or alter memory layouts.
- **Two-container network isolation + trajectory auditing**: Place the analysis workspace and the unprivileged target service in separate containers connected only over an internal non-routable bridge (with outbound internet blocked via an allowlisted proxy), and audit trajectories so abusing legitimate built-in CLI/file-read features of a target utility is never miscounted as memory-corruption risk.

---

## Defensive Recommendations

1. **Enforce full binary hardening (`-fstack-protector-strong`, `-fPIE -pie`, `-Wl,-z,relro,-z,now`, `NX`, `_FORTIFY_SOURCE`) in CI release gates**, and ensure network daemons `exec` (rather than `fork`-without-reseed) on worker crashes so stack canaries are never reused across connections.
2. **Eliminate address and heap-layout disclosures in error/diagnostic responses**, and protect writable heap/struct callbacks with Control-Flow Integrity (`CFI`) or pointer authentication.
3. **Compress patch-to-deployment windows**: Treat binary-only security updates (firmware images, proprietary packages, container layers) as high-signal vulnerability disclosures—autonomous agents need less than `$32` and `~2 hours` to diff stripped binaries and synthesize crash triggers (`88%`) or working exploits (`20%–25%` when unhardened).
