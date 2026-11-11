---
name: compositional-coding-harness-reference-monitor
description: >
  Mediate every coding-agent tool call through an immutable Ring-0 reference
  monitor combining Macaroon HMAC capability attenuation, a 2D trust-by-
  sensitivity taint lattice, a cross-agent workspace disk-provenance ledger,
  byte/socket-level OS interceptors, Red-Green-Benign probe verification, and
  split-horizon encrypted audit logs. Derived from ActiveSecHarness
  (arXiv:2611.13960).
source: https://arxiv.org/abs/2611.13960
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Compositional Coding-Harness Reference Monitor

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

Use this skill when building or hardening an **agentic software-engineering (SWE) harness** that reads untrusted issues, pull requests, archives, or web documentation while holding shell, filesystem, git, and network capabilities across one or more collaborating agents.

## When to Use

- Coarse 1-bit taint tracking locks out normal issue-driven SWE workflows (`read untrusted bug report -> edit repo -> run pytest`), whereas stateless per-task tool allowlists miss payload-level smuggling and cross-agent secret laundering through shared workspace files.
- Synchronous per-tool-call LLM safety judges add `>100 ms` latency per invocation or reject benign developer commands (`git`, `pytest`, `grep`, `tar`) at unacceptable false-positive rates.
- Multiple agents share a workspace directory and could launder secrets or untrusted commands across turns by writing intermediate notes (`notes.txt`, patches, fixtures) to disk.
- Audit logs live inside or near an agent-accessible host environment where plain-text forensic arguments would expose system paths, blocked boundaries, or redacted secret locations to a prompt-injected agent (**Forensic Reconnaissance Paradox**).

Prefer [provenance-capability-grants](../provenance-capability-grants/SKILL.md) when mediating high-level business API tool parameters (such as email recipients or transfer amounts) rather than OS-level coding workspaces, and pair with [sealed-replayable-agent-audit-log](../sealed-replayable-agent-audit-log/SKILL.md) when you need offline mocked replay and post-run capsule diffing across CI runs.

**Deference to the repository acceptance gate:** Whenever `SecurityTestSynthesizer` or `WikiManager` promotes a synthesized regression probe or persistent rule beyond the active task episode into the long-lived harness suite, it **must** pass `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../../rules/recursive-improvement.md) (no regression beyond baseline noise margin, trajectory mechanism check, held-out evaluation, and zero-tolerance negative security testbed).

---

## Core Insight

Coding-harness security fails along **two orthogonal axes** that neither regex filters, live LLM judges, stateless task policies, nor 1-bit taint flags can resolve alone:

1. **Provenance trust vs. data sensitivity must be tracked separately** on a 2D product lattice $\mathcal{L} = \mathcal{L}_{\mathrm{trust}} \times \mathcal{L}_{\mathrm{sens}}$. Reading an untrusted GitHub issue and distilling a structured bug summary transitions state to $(\mathsf{Derived}, \mathsf{Public})$—permitting workspace edits and isolated networkless unit tests (`SHELL_TEST_ISOLATED`) while keeping arbitrary shell (`SHELL_ARBITRARY`) and network egress (`NETWORK_EGRESS`) closed. Conversely, stripping Unicode Bidi control characters (`Sanitize`) raises $\mathcal{L}_{\mathrm{trust}}$ without clearing $\sigma = \mathsf{Sensitive}$; only credential redaction or explicit human declassification clears sensitivity.
2. **Multi-agent separation of duties collapses if workspace files are untyped.** Recording per-file taint and cumulative side-effect signatures $(\ell(f), \Sigma(f))$ in a `WorkspaceProvenanceLedger` folds cross-agent disk handoffs in $\mathcal{O}(1)$ time per step, preventing Agent A (secret reader) from laundering `.env` contents through a shared file to Agent B (HTTPS uploader).

**Verified Empirical Evidence** (`ActiveSecHarness`, arXiv:2611.13960, $N = 252$ executable scenarios: `120` single-step attacks across 6 threat domains, `120` matched benign SWE tool calls, and `12` five-stage multi-agent kill chains):

| Defense Architecture | Attack Block Rate (ABR) | Benign False-Positive Rate (FPR) | Median / p95 Latency |
|:---------------------|:------------------------|:---------------------------------|:---------------------|
| **Unguarded** | `0.000` (`[0.00, 0.03]`) | `0.000` | `0.1 μs` / `0.1 μs` |
| **25-Rule Regex Filter** | `0.439` (`[0.35, 0.53]`; `0.417` single-step, `0.667` kill chains) | `0.000` | `6.6 μs` / `9.7 μs` |
| **Live Zero-Shot LLM Judge (`qwen3:4b`)** | `1.000` (`[0.972, 1.000]`) | **`0.983`** (`118/120` benign SWE calls denied) | **`142.3 ms`** / `512 ms` |
| **Oracle Stateless Task Policy** *(12 kill chains / 12 benign SWE trajectories)* | `0.667` (`8/12`; misses Zip-Slip, `\x7fELF` write, issue IPI, disk laundering) | `0.000` (`0/12`) | `11.3 μs/step` |
| **Coarse 1-Bit Boolean Taint Lock** *(trajectory suite)* | `1.000` (`12/12`) | **`0.833`** (`10/12` issue-driven SWE flows blocked) | `18.4 μs/step` |
| **ActiveSec Ring 0 (Product Lattice + Ledger)** | **`1.000`** (`120/120` single-step, `12/12` kill chains) | **`0.000`** (`0/120` single-step, `0/12` trajectories) | **`12.7 μs`** / `0.56 ms` (`~20.0 μs/step` at $k=50$) |

---

## Step-by-Step Procedure

### Step 1: Partition the Harness into Four Authority Rings & Attenuated Macaroon Capabilities

Separate enforcement authority from agent reasoning across four concentric rings (`Ring 0` to `Ring 3`):

1. **Ring 0 (Immutable Security Kernel)**: Non-bypassable deterministic reference monitor outside the agent's editable workspace and Python import path. No prompt, tool output, or subagent edit can alter Ring-0 guards or capability verifiers.
2. **Ring 1 (Human-Sovereign Layer)**: Houses out-of-band operator approvals, `CommandDeobfuscator` (**Explain-Before-Sudo**, which strips Trojan Source Bidi controls `U+202A–U+202E` and `U+2066–U+2069` and unfolds Base64/Hex shell pipelines into plain English before asking a human), and explicit `declassify_artifact()` waivers.
3. **Ring 2 (Privileged Orchestrators & Verifiers)**: Coordinates task decomposition, `DualModelReviewer`, `SecurityTestSynthesizer`, and scoped diagnostic/security subagents holding short-lived, network- or CIDR-bounded tokens.
4. **Ring 3 (Unprivileged SWE Workers)**: Default execution tier—offline-by-default, confined to canonical workspace paths, and restricted to minimal tool subsets.

Issue every agent a nested HMAC-SHA256 **Macaroon `CapabilityToken`** encoding `(subject, parent_id, nonce, expires_at, max_calls, allowed_tools, workspace_prefixes, allowed_binaries, allowed_cidrs_or_domains)`. Enforce **strict monotonic attenuation** whenever an orchestrator spawns a subagent:

$$\mathrm{Scope}(\tau_{\mathrm{child}}) = \mathrm{Scope}(\tau_{\mathrm{parent}}) \cap \mathrm{Caveat}_{\mathrm{requested}} \subseteq \mathrm{Scope}(\tau_{\mathrm{parent}})$$

Any tampering with caveat fields or signature chains invalidates the root-secret HMAC verification in Ring 0.

---

### Step 2: Track 2D Taint State & Cross-Agent Disk Provenance

Maintain a 2D label $\ell = (\tau, \sigma) \in \mathcal{L}_{\mathrm{trust}} \times \mathcal{L}_{\mathrm{sens}}$ for every active agent and every canonical workspace path:

```python
# Trust ordering (low to high taint): TRUSTED < SANITIZED < DERIVED < UNTRUSTED
# Sensitivity ordering: PUBLIC < SENSITIVE
# Componentwise join: (t1, s1) | (t2, s2) = (max(t1, t2), max(s1, s2))
```

1. **Gate Tool Classes by Both Coordinates**:
   - When $\sigma = \mathsf{Sensitive}$ (for example, after reading `.env`, SSH keys, or credentials), block `SHELL_ARBITRARY` and `NETWORK_EGRESS` unconditionally, regardless of $\tau$.
   - When $(\tau, \sigma) = (\mathsf{Untrusted}, \mathsf{Public})$ (raw external issue/web text in context), allow local read/inspection only.
   - Expose a deterministic structured extraction boundary (`derive_agent_summary()`) that strips raw untrusted prose into schema-checked task fields, transitioning $(\mathsf{Untrusted}, \mathsf{Public}) \mapsto (\mathsf{Derived}, \mathsf{Public})$. At $(\mathsf{Derived}, \mathsf{Public})$, permit workspace edits, safe archive extraction, and **networkless isolated test execution (`SHELL_TEST_ISOLATED`, e.g., `pytest` inside `SandboxGuard`)**, while still blocking `SHELL_ARBITRARY` and `NETWORK_EGRESS`.
2. **Keep Sanitization and Redaction Orthogonal**:
   - Structural sanitization (stripping Unicode Bidi or AST/syntax validation) maps $(\tau, \sigma) \mapsto (\mathsf{Sanitized}, \sigma)$ and **never** lowers $\sigma = \mathsf{Sensitive}$.
   - Only `CredentialGuard` secret scrubbing or an explicit Ring-1 operator waiver (`declassify_artifact`) lowers $\sigma \mapsto \mathsf{Public}$.
3. **Fold Cross-Agent Disk State in `WorkspaceProvenanceLedger`**:
   - For every canonical file path $f$, store $(\ell(f), \Sigma(f))$ where $\Sigma(f) \subseteq \{\mathsf{READ\_UNTRUSTED}, \mathsf{READ\_SENSITIVE}, \mathsf{WRITE\_FS}, \mathsf{EXEC\_PROCESS}, \mathsf{NETWORK\_EGRESS}\}$.
   - **On write** by agent $A$ to $f$: update $\ell(f) \leftarrow \ell(f) \sqcup \ell(A)$ and merge $A$'s active side-effect signature into $\Sigma(f)$.
   - **On read** by agent $B$ from $f$: update $\ell(B) \leftarrow \ell(B) \sqcup \ell(f)$ and $\Sigma_B \leftarrow \Sigma_B \cup \Sigma(f)$ before $B$'s next tool call.
   - Reject any call whose post-join state closes a **Lethal Trifecta** ($\sigma = \mathsf{Sensitive}$ or $\mathsf{READ\_SENSITIVE}$ combined with $\mathsf{NETWORK\_EGRESS}$ or $\mathsf{EXEC\_PROCESS}$). When planning multi-step workflows upfront, greedily partition steps across attenuated child tokens whenever adding the next step would close a forbidden combination.

---

### Step 3: Mediate Every Tool Call Through Seven Ordered Ring-0 Checks

Execute Ring-0 mediation synchronously in strict fail-closed order (`~12.7 μs` median overhead):

1. **Tool Certificate Integrity (`CertifiedToolRegistry`)**: Before parsing arguments, recompute the SHA-256 digest of the tool's live bytecode (`__code__.co_code`), normalized AST, dependency lock, and publisher HMAC signature (`ToolCertificate`). Reject immediately on any post-registration rug-pull or monkey-patch.
2. **Canary Tripwire Check (`CanaryGuard`)**: Plant zero-utility decoy files with unique cryptographic markers in the workspace (`.env.production.canary`, `id_ed25519_canary`). Any `read`, `write`, or `stat` touch indicates active recon or exfiltration—immediately call `revoke_token()` across the entire parent/child token lineage.
3. **Token HMAC, TTL, Quota, & Replay Nonce Verification**: Verify the Macaroon HMAC chain, expiration timestamp, remaining call budget, and fresh per-call nonce.
4. **2D Lattice & Provenance Ledger Check**: Compute the post-read/pre-action join against `WorkspaceProvenanceLedger` and verify the requested side-effect class is permitted at $(\tau, \sigma)$.
5. **Byte-, Path-, and Socket-Level Guard Interception**:
   - **`ArchiveGuard`**: Never trust archive header `file_size` fields. Stream entries in `64 KiB` (`65,536`-byte) chunks into an `O_NOFOLLOW`, `0700` staging directory (`noexec,nosuid,nodev`) enforcing per-entry byte caps, total byte caps, entry-count caps, and live `total_written / archive_size` compression-ratio ceilings. Reject symlinks, FIFOs, device nodes, and any path failing `Path.resolve(p).is_relative_to(dest)` before atomic promotion.
   - **`MalwareGuard`**: Inspect leading file magic bytes (`\x7fELF`, `PE/MZ`, `Mach-O`, `#!`) on every write/extract regardless of benign file extension (`.txt`, `.jpg`, `.md`), and block Trojan Source Bidi overrides (`U+202A–U+202E`, `U+2066–U+2069`) and zero-width homoglyphs.
   - **`CredentialGuard`**: Run bidirectional DLP on both file/env reads and outbound writes/commits using regexes, Shannon entropy ($\ge 4.0\text{ bits/char}$), and leetspeak demangling (`@->a, 0->o, $->s, 1->i/l, 3->e`) with prefix/suffix stripping so mangled secrets cannot slip past keyword rules.
   - **`NetworkGuard`**: Block cleartext `http://` unless explicitly caveated; perform **resolve-once DNS** (`A`/`AAAA`) prior to connection, reject loopback (`127.0.0.0/8`, `::1`), RFC1918 private ranges, link-local cloud metadata (`169.254.169.254`), and CGNAT (`100.64.0.0/10`) unless explicitly permitted by CIDR caveats, and **pin the verified IP at the socket layer** so low-TTL DNS rebinding cannot swap an external hostname to localhost mid-request.
   - **`SandboxGuard`**: Confine paths via `realpath` (`O_NOFOLLOW`), scrub environment variables down to the tool's declared `env_allowlist`, enforce `RLIMIT_AS`/`RLIMIT_CPU`/`RLIMIT_NPROC`/`RLIMIT_FSIZE`, wrap subprocesses in `bwrap --unshare-all` on Linux, and enforce **per-binary flag blocklists** against GTFOBins LotL escapes (`find -exec`/`-execdir`, `tar --checkpoint-action`/`--to-command`, `git -c core.fsmonitor`/`upload-pack`, `python -c`, `awk system()`).
6. **Sandboxed Execution & Post-Output Scrubbing**: Run the tool and pass stdout/stderr through `CredentialGuard` and `MalwareGuard` before returning text to the LLM context.
7. **Split-Horizon Audit Commit (`HashChainedAuditLog`)**: Record every allow/deny decision without leaking recon data back to workspace agents (Step 5 below).

---

### Step 4: Gate Agent-Authored Code with the Red–Green–Benign Quartet

Before merging agent-written patches or admitting synthesized security regression tests:

1. **Run Three-Tier Static + Behavioral Code Verification (`CodeVerifier`)**:
   - `TIER1_UNIVERSAL`: Reject Bidi controls, `eval`/`exec`, `os.system`, `subprocess(..., shell=True)`, and unsafe deserializers (`pickle`, `marshal`, `yaml.load`).
   - `TIER2_CONTEXTUAL`: Run domain-specific AST dataflow checks plus live negative behavioral probes (such as Zip-Slip traversal payloads and high-ratio ZipBombs) inside an isolated networkless `test-runner` subagent.
   - `DualModelReviewer`: Cross-check high-risk patches with an independent secondary reviewer prompt/model so generator blind spots are challenged.
2. **Enforce the Red–Green–Benign Quartet (`SecurityTestSynthesizer`)**:
   - Never allow an agent to register a Vacuous `assert True` security test or execute arbitrary hooks inside a test file. Require four checks before accepting any synthesized security test $T$:
     1. **`ASTSafe(T) = True`** (imports restricted to `unittest`/`pytest` and target module; zero network, subprocess, or raw host FS writes).
     2. **Red**: $T(M_{\mathrm{vuln}}, \mathsf{adv}) \neq 0$ (test demonstrably fails on the unpatched vulnerable code).
     3. **Benign-Safe**: $T(M_{\mathrm{vuln}}, \mathsf{benign}) = 0$ (test passes on valid benign inputs, proving it is not an unconditional fail).
     4. **Green**: $T(M_{\mathrm{fixed}}, \mathsf{adv}) = 0$ (test passes on the patched code).
   - Defer any persistent test-suite or harness promotion beyond the current task to `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../../rules/recursive-improvement.md).

---

### Step 5: Seal Audit Logs with Split-Horizon Dual-Key Encryption

Solve the **Forensic Reconnaissance Paradox**—where detailed security logs help human responders reconstruct attacks (`who`, `exact path`, `raw payload`) but simultaneously hand a compromised workspace agent a map of system paths, canary locations, and redacted secrets:

1. Provision two independent `>= 256`-bit keys outside the agent's workspace and environment (`signing_key` and `encryption_key`).
2. Pre-scrub sensitive literals into deterministic session-salted HMAC tokens (`<REDACTED:TYPE:hmac_10>`) so analysts can correlate repeated exfiltration attempts of the same secret without storing cleartext credentials in either log tier.
3. Write **Tier 1 (Structural Header)** (`seq`, `timestamp`, `event_type`, `decision`, `prev_hash`, `entry_hash`) chained with HMAC-SHA256 (`entry_hash_i = HMAC(signing_key, prev_hash || canonical_header_i || sha256(ciphertext_i))`) so integrity monitors can verify log completeness in real time without decryption keys.
4. Encrypt **Tier 2 (Forensic Payload)** (raw tool arguments, target paths, token nonces, violation traces) using HKDF-HMAC-SHA256 authenticated encryption (`Encrypt-then-MAC`, `0o600` permissions, `O_NOFOLLOW`) so any agent reading workspace disk sees only opaque ciphertext.

---

## Environment Caveats & Failure Modes

- **Userspace Python vs. OS Kernel Enforcement**: In-process Python guards can be bypassed if an agent obtains unconstrained native C-extension loading (`ctypes`) or raw kernel syscall execution outside `SandboxGuard`. Always pair userspace reference monitors with OS namespace isolation (`bwrap --unshare-all`, containers, or microVMs) in production.
- **Over-Coarse Taint Collapses Developer Utility**: Collapsing the 2D lattice $(\tau, \sigma)$ into a single boolean taint bit causes an **`83.3%` false-positive rate** (`10/12` normal issue-to-test SWE workflows blocked). Preserve the `derive_agent_summary()` transition to $(\mathsf{Derived}, \mathsf{Public})$ and keep `SHELL_TEST_ISOLATED` networkless.
- **High-Latency Synchronous LLM Judges**: Placing a local LLM judge (`qwen3:4b`) inline on every syscall increases median latency `11,200x` (`12.7 μs -> 142.3 ms`) and denies `98.3%` of benign developer calls when small models over-trigger on shell/git syntax. Keep Ring-0 mediation deterministic and reserve LLM review (`DualModelReviewer`, `Explain-Before-Sudo`) for asynchronous patch review or Ring-1 human escalation.
- **Semantic Side Channels Within Allowed Text**: Information-flow lattices stop unauthorized tool/network capabilities (`Lethal Trifecta`), not low-bandwidth steganographic encoding inside human-visible PR comments if an operator explicitly approves publishing text derived from sensitive state. Require `CredentialGuard` scanning plus human diff review (`Explain-Before-Sudo`) at Ring-1 declassification boundaries.

---

## Cross-References

- **Related Rules**:
  - [`agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — Capability gateways, LotL binary restrictions, SSRF/DNS rebinding defenses, and pre-execution monitors
  - [`multi-agent-coordination.md`](../../rules/multi-agent-coordination.md) — Cross-agent trust boundaries and delegation attenuation
  - [`recursive-improvement.md`](../../rules/recursive-improvement.md) — `"DO: Pass every self-modification through one acceptance gate"` for any persistent test/rule promotion
- **Related Skills**:
  - [`provenance-capability-grants`](../provenance-capability-grants/SKILL.md) — Value-free provenance blueprints for business/API tool calls
  - [`principal-context-permission-intersection`](../principal-context-permission-intersection/SKILL.md) — Intersecting principal, context, and lineage permissions across multi-agent delegations
  - [`sealed-replayable-agent-audit-log`](../sealed-replayable-agent-audit-log/SKILL.md) — Post-run capsule sealing, mocked replay, and structural trace diffing
  - [`audited-guardrail-tool-evolution`](../audited-guardrail-tool-evolution/SKILL.md) — Independent CWE auditing for dynamically evolved Python guardrail functions

## Sources

- Hegelich, S., Prenkaj, B., Sarhan, H., Shahrezaye, M., Hegelich, K., Montag, C., Schneider, R., & Cambria, E. (2026). *From Attack Surface to Defense Architecture: Compositional Security for Agentic Coding Harnesses* (`ActiveSecHarness`). [arXiv:2611.13960](https://arxiv.org/abs/2611.13960) (`src:2611-13960v1`).
