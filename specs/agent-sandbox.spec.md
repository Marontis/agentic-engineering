# Agent Sandbox Specification Template

> Fill in this template when designing an execution sandbox for AI agents.
> Each section surfaces research-backed decision points. Defaults are
> marked where the evidence clearly favors one option.
>
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## 1. Threat Model & Scope

### What type of agent is this sandbox for?

- [ ] Browser-based agent (web navigation, form filling, API calls)
- [ ] Coding agent (file operations, command execution, package management)
- [ ] Research agent (web search, document retrieval, data analysis)
- [ ] Multi-modal agent (combination of the above)
- [ ] Other: ___

### What are the primary risks?

- [ ] Unauthorized network access (data exfiltration, external API calls)
- [ ] Filesystem damage (destructive writes, configuration corruption)
- [ ] Resource exhaustion (infinite loops, memory leaks, fork bombs)
- [ ] Privilege escalation (sudo, container escape, host access)
- [ ] Social engineering (email sends, message posts, account changes)
- [ ] Other: ___

### What is the isolation boundary?

- [ ] Process-level (separate process, same OS)
- [ ] Container-level (Docker/OCI, network namespace)
- [ ] VM-level (full hypervisor isolation)
- [ ] Browser-level (extension sandbox, webRequest interception)

> **Research note**: The isolation level should match the risk profile.
> Browser agents benefit from HTTP-layer interception (invisible to page JS,
> catches all requests). Coding agents benefit from filesystem snapshots with
> container isolation. (arXiv:2512.12594, arXiv:2512.12806)

---

## 2. Command Classification

### How will agent commands be classified?

**Default: Three-tier classification** (recommended by research)

| Tier | Definition | Action | Examples |
|:-----|:----------|:-------|:--------|
| Safe | Read-only, no side effects | Execute directly | `ls`, `cat`, `git status`, `grep` |
| Uncertain | Local writes, env changes | Snapshot → execute → commit/rollback | `git commit`, `sed -i`, `make`, file writes |
| Unsafe | Network, process mgmt, privilege | Block or require approval | `curl`, `ssh`, `sudo`, `rm -rf /`, `pip`/`npm`/`apt install`, `docker run`/`pull` |

Network installs are Unsafe: they fetch and run third-party code and
reach the network. If policy approves one (e.g. a pinned internal
mirror on the allowlist), also run it inside a snapshot.

### What classifier will you use?

- [ ] Pattern-matching rules (fastest, least flexible)
- [ ] Small language model (SLM) classifier (good balance)
- [ ] Main reasoning model with classification prompt (most accurate, most expensive)
- [ ] Hybrid: rules for obvious cases, SLM for edge cases

> **Tiering, not enforcement**: whichever classifier you choose only
> assigns tiers. Pattern lists are bypassed by obfuscation (410/500
> payloads evaded a lexical matcher, arXiv:2609.29808). Enforce Unsafe
> denials at the syscall/network layer with a default-deny allowlist
> (`rules/agent-sandbox-safety.md`: "DON'T: Use application-layer tripwires or
> PID signals as the containment boundary for a rogue agent"; "Default
> to allowlist, not blocklist"). Anything the Safe allowlist does not
> match is Uncertain or Unsafe.

### What happens after a denial?

- [ ] **Unsafe-tier denial ends the task or escalates to a human**
      (required; the harness must not auto-continue)
- [ ] Uncertain-tier rollback returns the error to the agent, which may
      re-plan
- [ ] Repeated attempts at a denied effect (rephrased, encoded,
      scripted, split, delegated) are logged and alerted

> **Pitfall**: telling the agent to "find another way" after a denial
> trains it to route around the policy (arXiv:2609.30217;
> `rules/agent-sandbox-safety.md`: "Give blocking action monitors recent
> call history, and make denials terminal").

### Classification overrides:

- [ ] Can the user override a classification at runtime? Y/N
- [ ] Can the agent request an override? Y/N
- [ ] Are overrides logged? (must be Y)

> **Pitfall**: Never let the agent modify its own classification rules.
> The safety layer must be outside the agent's edit scope. (arXiv:2512.12594)

---

## 3. Snapshot & Rollback

### Snapshot strategy:

- [ ] Copy-on-write (ZFS/Btrfs) — near-zero overhead, requires CoW filesystem
- [ ] Full copy (`shutil.copytree`) — ~1.8s for 250MB, portable
- [ ] Git-based (commit before, reset on failure) — works for code-only workspaces
- [ ] Container checkpoint (CRIU) — heavy but captures full process state
- [ ] No snapshot (acceptable only for safe-only commands)

### When to snapshot:

- [ ] Before every command (safest, highest overhead)
- [ ] **Before every uncertain or unsafe command** (recommended default)
- [ ] Before each agent "turn" or planning step
- [ ] On explicit user request only

### Rollback triggers:

- [ ] Command returns non-zero exit code
- [ ] Command exceeds time limit
- [ ] Command output matches error patterns
- [ ] Agent explicitly requests rollback
- [ ] User explicitly requests rollback

### External API handling:

> **Critical pitfall**: Filesystem rollback does NOT undo external API calls.
> Design a compensating transaction for every external operation that has
> one. Sent emails and messages have none: a follow-up message is not a
> rollback, so gate them before sending (human confirmation).
> (arXiv:2512.12806)

- [ ] List all external APIs the agent may call: ___
- [ ] For each, define the compensating transaction:

| API Call | Compensating Transaction | Automated? |
|:---------|:------------------------|:-----------|
| Example: create calendar event / DNS record | Delete the created record | Yes |
| Example: POST to API | DELETE endpoint | Yes |
| Example: send email / message | None (not compensable) | Pre-send confirmation gate instead |
| | | |

---

## 4. Network Policy

### Default network stance:

- [ ] **Allowlist** (block all, explicitly permit known-safe domains) — recommended
- [ ] Blocklist (allow all, block known-bad domains) — not recommended
- [ ] No network access (fully air-gapped)
- [ ] Full network access (no sandbox) — not recommended for autonomous agents

### Interception layer:

- [ ] **HTTP-layer interception** (webRequest API, proxy) — recommended for browser agents
- [ ] DNS-level blocking
- [ ] Firewall rules (iptables/nftables)
- [ ] Application-level middleware

> **Research note**: HTTP-layer interception catches all requests regardless
> of how they're triggered, is invisible to page-level JavaScript, and cannot
> be bypassed by client-side code. (arXiv:2512.12594)

### Allowed domains:

| Domain | Purpose | Max requests/min |
|:-------|:--------|:----------------|
| | | |

---

## 5. Performance & Scheduling

### Sandbox lifecycle:

- [ ] On-demand creation (simpler, higher latency per step)
- [ ] **Pre-forked pool** (recommended for multi-step agents)
- [ ] Persistent sandbox (reused across tasks)

### Speculative scheduling:

- [ ] Agent generates plan → speculatively prepare sandboxes for likely branches
- [ ] Speculate only on side-effect-free steps (or effects confined to the
      disposable sandbox); Unsafe steps (network, external API, process
      management) run only after the agent commits to the branch
- [ ] Kill unused sandboxes when agent commits to a branch
- [ ] Budget: max ___ concurrent speculative sandboxes

> **Research note**: Moving sandbox creation off the critical path via
> preforking eliminates 100ms–2s of latency per agent step. (arXiv:2607.23933)
> Killing a speculative sandbox does not undo an external effect, so
> speculation stops at Unsafe steps (`rules/agent-sandbox-safety.md`:
> "Prefork sandbox environments on predicted execution branches").

### Multi-session accelerator / exclusive-hardware command scheduling (`arXiv:2611.17294`):
- [ ] Lightweight read-only inspection, search, and workspace edits execute immediately in **parallel** on the session's owner node, while builds, tests, GPU/accelerator benchmarks, and unrecognized commands enter a **fail-closed per-node FIFO serial slot** (`1` active benchmark per physical accelerator)
- [ ] Local FIFO queue-wait time is **excluded** from active session/tool timeout budgets (`3,600 s` / `600 s`) so skewed node queues do not abort healthy rollouts
- [ ] Idle helper nodes migrate only **waiting, path-portable serial commands** whose expected runtime and remaining wait exceed the measured cross-node handoff floor ($T_{\text{mig}} \approx 1.86\text{--}2.16\text{ s}$ on gigabit LAN/SMB) via three-phase **`reserve -> claim -> commit`** ([`serial-slot-accelerator-command-scheduling`](../skills/serial-slot-accelerator-command-scheduling/SKILL.md))

### Learned startup snapshots for unseen multi-package scripts & stateful verifier pools (`arXiv:2611.22171`, `arXiv:2611.24788`):
- [ ] Unseen multi-package code sandboxes use a compact portfolio (`~30–60`) of post-import memory snapshots planned via **greedy budgeted facility location** over two-pass additive package metadata ($t_p$, `RssAnon` $m_p$, excluding monkey-patching imports) and routed online by minimum $T(r, c) = t_{\mathrm{base}} + \alpha S(c) + \sum_{p \in D_r \setminus D_c} t_p$ ([`budgeted-facility-sandbox-snapshots`](../skills/budgeted-facility-sandbox-snapshots/SKILL.md))
- [ ] Shared stateful theorem-prover / formal-verifier pools (`Isabelle/PIDE`, `Lean 4`) use interchangeable import-keyed leases with **empty editor visibility (`perspective = empty`)**, `cgroup` `85%` `HTTP 503` memory admission, `4 ms` document-version checkpoints, post-timeout heap-bloat recycling, and parsed-AST flags (`success && !proof_open && !used_sorry`) backed by a stateless scratch-build final arbiter ([`pooled-prover-verification-service`](../skills/pooled-prover-verification-service/SKILL.md))

### Resource limits:

| Resource | Limit | Action on exceed |
|:---------|:------|:----------------|
| CPU time per command | ___ seconds | Kill + rollback |
| Memory per sandbox | ___ MB | Kill + rollback |
| Disk writes per command | ___ MB | Kill + rollback |
| Total sandbox lifetime | ___ minutes | Checkpoint + teardown |
| Repeated status/read polls per tool | <= 2–3 sync calls | Handoff to async waiter / abort on `No fixed point` (monotonic `source_version` without task delta; arXiv:2611.14808) |
| Cumulative + prefix-weighted token budget | ___ tokens | Terminate loop + alert on quiescent-vs-churn amplification (arXiv:2611.14808) |

---

## 6. Audit & Accountability

### Logging requirements:

Every command must be logged with:
- [ ] Timestamp
- [ ] Command text
- [ ] Safety classification (safe/uncertain/unsafe)
- [ ] Whether snapshot was created
- [ ] Execution outcome (success/failure/timeout/killed)
- [ ] Whether rollback was triggered
- [ ] Rollback result (if applicable)
- [ ] Token count consumed

### Log retention:

- [ ] Duration: ___
- [ ] Storage location: ___
- [ ] Access controls: ___

> **Research note**: These logs build the infrastructure for legal
> accountability of non-human agents. Design them to answer "what did
> the agent do, when, and what was the effect?" (arXiv:2608.20041)

---

## 7. Pitfall Checklist

Before finalizing the sandbox design, verify:

- [ ] The agent cannot modify its own safety classification rules
- [ ] The agent cannot modify the network allowlist/blocklist
- [ ] The agent cannot escape the isolation boundary
- [ ] Every external API call has a defined compensating transaction, or a pre-execution confirmation gate if it has none (sent messages)
- [ ] Unsafe-tier denials are terminal (task ends or escalates); only Uncertain-tier rollbacks lead to re-planning
- [ ] The command classifier is used for tiering only; enforcement is at the syscall/network layer with an allowlist
- [ ] Snapshot overhead is acceptable for the target latency
- [ ] Rollback is tested and verified for all uncertain command types
- [ ] Audit logs capture enough detail for post-incident attribution
- [ ] Dual-key split-horizon audit logs (`K_trace` / `K_content`) seal encrypted payload transcripts against a tamper-evident hash chain outside the agent's write scope ([`compositional-coding-harness-reference-monitor`](../skills/compositional-coding-harness-reference-monitor/SKILL.md), arXiv:2611.13960)
- [ ] A 2D $(\tau, \sigma)$ taint lattice and workspace disk provenance ledger prevent cross-turn untrusted-data laundering, magic-byte/GTFOBins command smuggling, and DNS-rebinding TOCTOU via resolve-once IP pinning (arXiv:2611.13960)
- [ ] Denials return opaque binary verdicts to the agent caller (never diagnostic rule IDs or signature labels), signed host binaries are NOT exempted from untrusted-path DLL-load inspection, and child telemetry alerts quarantine the parent agent session (arXiv:2611.13684)
- [ ] On `1.7B–35B` SLM agents, write-call authorization derives polarity and `authority`/`payload` roles deterministically from static tool schemas with pre-read `$placeholder` write commitments and exact request n-gram grounding—never from SLM-authored JSON policies, graphs, or compiled programs ([`schema-derived-write-integrity-gate`](../skills/schema-derived-write-integrity-gate/SKILL.md), arXiv:2611.17115)
- [ ] Post-write verification binds strictly to the session's causal `mutation_id` or first-seen `source_version` snapshot (never global shared-queue `pending == 0` quiescence), caps synchronous status polls, and tests MCP status tools under concurrent background `churn` (arXiv:2611.14808)
- [ ] Untrusted visual assets are ingested by VLMs at `>= 224x224–336x336` resolution parity rather than `64x64–128x128` thumbnails (or gated by multi-scale transcript consistency checks rather than single-view `JPEG`/blur/median filters, which have `p = 1.000` null effect; arXiv:2611.16744)
- [ ] Persistent multi-agent sandboxes sharing memory (`L1`), prompt/skill files (`L2`), or package/container state (`L3`) fuse statistical drift (`T1`) with deterministic policy (`T2`), file-hash (`T3`), and task-grader (`T4`) triggers and sanitize the **top-3** `2`-hop RTS trace-back origins rather than evicting only the visibly misbehaving agent (`R_c = 2.83` vs. `0.81`, [`multi-layer-compromise-filtering-and-traceback`](../skills/multi-layer-compromise-filtering-and-traceback/SKILL.md), arXiv:2611.18693)
- [ ] Multi-round deep-research / web-search planners lock primary ranking rubrics from the user prompt (requiring user confirmation before planner-discovered metrics outweigh user criteria), verify publisher/temporal independence rather than hostname counts (`2`-domain bait bypasses single-site tags at `p = 0.5`), scrub private context from outbound search queries, and block auto-loaded external media in rendered reports (arXiv:2611.20045)
- [ ] Agent service credentials use non-exportable per-relying-party hardware keys (`TPM`/`Secure Enclave`/`TEE`) with TLS-derived runtime origin binding and passkey-signed `RAR` mandates where supported rather than on-disk bearer PATs (arXiv:2611.19536)
- [ ] Human-in-the-loop gates are audited via paired `Approve`/`Reject` four-witness checks (`decision -> calls -> dispatch -> native state`) for both denied-effect suppression and bounded approval completion, preserving per-call `call_id` multiplicity across parallel confirmations and checkpoint join resumptions ([`dual-obligation-approval-auditing`](../skills/dual-obligation-approval-auditing/SKILL.md), arXiv:2611.19237)
- [ ] Irreversible coding-agent command/path contracts block synchronously pre-action (`C4`) rather than relying on post-generation checks (`C3`), workspace `/tmp` scratch allowances do not contradict command bans, and inter-agent relays use provenance/policy gates rather than `BLEU`/`ROUGE-L`/`METEOR` lexical overlap (arXiv:2611.19549, arXiv:2611.21520)
- [ ] Companion configuration/management UIs (`Gradio`, `FastAPI`, `Streamlit`) bind to `127.0.0.1` by default (`CWE-1327`), require header bearer/session tokens (`HTTP 401`, `CWE-306`), enforce `Origin`/`Referer` allowlists + typed `application/json` schemas rather than `Content-Type`-agnostic `Request.json()` (`CWE-352`), verify `HMAC` digests on system-prompt files, and enforce PII/secret restrictions inside persistent-memory storage sinks rather than tool-description prose (`arXiv:2611.22761`)
- [ ] When rendering untrusted prose as images for VLMs, protection is verified per model across `Append`, `Format`, and full-output `Replace` operations under `k >= 8` framing candidates and multi-span synthesis utility checks, and tainted documents are quarantined at the **whole-page** boundary rather than localized visual-token span masking (`46.88% / 76.04%` residual image ASR under full attack-span attention blocking; arXiv:2611.24231)
- [ ] Offline IPI purple-teaming pairs rolling sparse strategy-dictionary (`BPDN`) coverage with `C1`/`C2` checks and symmetric `z+/z-` token-level self-distillation (`PIPETTE`), backed by deterministic sink-level parameter authorization ([`strategy-diverse-ipi-purple-teaming`](../skills/strategy-diverse-ipi-purple-teaming/SKILL.md), arXiv:2611.24362)
- [ ] Out-of-process `MCP` wire proxies scrub signing keys before spawning child servers, classify `tools/call` outcomes into 4 `(executed, ok)` states, supervise post-turn affirmative prose claims on CPU (`ReceiptSupervisor`, `17.9 ms` p50, `0 MiB` VRAM) against target-bound `executed=true && ok=true` Ed25519 receipts, and omit signing constructors for `LLM_NARRATION` / `TOOL_CONTENT_UNTRUSTED` on append-only SQLite memory ([`receipt-bound-mcp-prose-supervision`](../skills/receipt-bound-mcp-prose-supervision/SKILL.md), arXiv:2611.27095)
- [ ] Composite POSIX shell execution runs speculatively inside per-directory `OverlayFS` + held network proxy (`Isolate` tracing `strace` + proxy domain/IP pairs while blocking `io_uring`, shared memory, and outliving background daemons), propagating direct-transfer file labels (`copy`/`concatenate`/`downloadNet`) without tainting agent context $\mathcal{T}$ under Lean 4 stateful `require` policies ([`syscall-inferred-stateful-ifc-monitoring`](../skills/syscall-inferred-stateful-ifc-monitoring/SKILL.md), arXiv:2611.25599)
- [ ] Context compaction never places model-written summaries in a `role: "user"` message on the authorization path (`1,108/1,108` live `Claude Code`/`Codex` compactions; `290/320` [`90.6%`] plain-data payee override); summaries enter the agent view as low-authority `tool` results while request-derived authorizers verify all three `Witnessed-Request Gate` checks (`w_i` ingress MAC, $\sigma$ monotonic boundary sequence MAC, and $m$ completeness count; [`witnessed-request-compaction-gate`](../skills/witnessed-request-compaction-gate/SKILL.md), arXiv:2611.32194)
- [ ] Batch permission onboarding recommendations enforce ancestor-only attention and parent-product DAG monotonicity (`0.0000` ancestor-consistency violations) strictly as human-inspectable proposals rather than implicit runtime execution grants ([`parent-gated-hierarchical-authorization-prediction`](../skills/parent-gated-hierarchical-authorization-prediction/SKILL.md), arXiv:2611.32018)
- [ ] On-device / bounded-window (`k = 3`) GUI action guardrails partition recurrent `<CTX>` into `AUTHORIZED` user scope vs. `UNAUTHORIZED` screen evidence, decouple commit-step `unsafe` from intervention-window `block` (`0` free-timing slack), cache cross-step vision-encoder outputs, and cap corrective `<FB>` retries at `<= 1` before terminal escalation ([`bounded-context-intervention-window-guardrail`](../skills/bounded-context-intervention-window-guardrail/SKILL.md), arXiv:2611.29847)
- [ ] Partially observable cyber-physical / infrastructure execution kernels isolate untrusted default records $R$ from three-valued knowledge $\kappa \in \{\mathsf{T}, \mathsf{F}, \mathsf{U}\}$, cap optimistic undecided reversible actions at one try ($\mathcal{F}$), require verified preconditions via minimum-cost deadline-feasible sensing covers for irreversible actions, and emit `Certified Holds` when verification or approval windows expire ([`asymmetric-knowledge-contingent-execution`](../skills/asymmetric-knowledge-contingent-execution/SKILL.md), arXiv:2611.30179)
- [ ] Edge accelerator and embodied VLA deployments re-attest resident DRAM weights and quantization scale buffers after load (`AES-XTS` lacks integrity MACs), prefer bounded `NVFP4` `E4M3` block scales or scale clamping over unverified inline `FP16`/`FP32` scales, and enforce out-of-SoC microcontroller velocity/joint-step/workspace interlocks rather than host `NaN`-only checks (`arXiv:2611.31129`)
- [ ] Pre-action risk auditing runs strictly **outside** the agent loop in a networkless reference monitor (`AuditScope ⊆ TaskScope`, zero outbound URL "verification" fetches, and immediate context purging of flagged `.env`/secret spans rather than self-initiated CUA auditing `P1–P7`), and GUI prompt-injection defenses quarantine localized DOM containers rather than aborting sessions via whole-screenshot API hard-refusals (`41.67% -> 0.00%` utility collapse; arXiv:2611.29977)
- [ ] Security engineering roadmaps assume an `~8–14`-month open-weight (`T4`) diffusion lag (`7.6` mo `[5.4, 10.0]` on benchmarks, `9.9–13.7` mo on real-software `A4` discovery; model access gates grade `Weak`), prioritize memory-safe languages (`Strong`), attack-surface reduction, compartmentalization, and silent updates (`Moderate`), and wire AI vulnerability scanning + human-reviewed PoC patches directly into maintainer CI rather than relying on bulk external advisories (`5%–25%` vs. `58%–94%` fix rates; arXiv:2611.26601)
- [ ] The sandbox works correctly when the agent fails (crash, timeout, OOM)

---

## Sources

- ceLLMate: arXiv:2512.12594
- SpecBox: arXiv:2607.23933
- Fault-Tolerant Sandboxing: arXiv:2512.12806
- AI Agency Typology: arXiv:2608.20041
- Hard Stop: arXiv:2609.29808
- Instrumental Monitor Evasion: arXiv:2609.30217
- BypassGym (Defensive Lessons on Closed-Loop EDR Evasion): arXiv:2611.13684
- ActiveSecHarness: arXiv:2611.13960
- Metal Sandbox (Command Scheduling for GPU Coding Agents): arXiv:2611.17294
- CapLite (Schema-Derived Write Integrity for SLM Agents): arXiv:2611.17115
- OverServe (Resource Amplification Defensive Lessons): arXiv:2611.14808
- SISS / ScaleGuard (Visual Prompt Injection Resolution Parity): arXiv:2611.16744
- Swarm Shepherd (Persistent Latent Compromise Filtering & Traceback): arXiv:2611.18693
- Security of Deep Research Agents & Agenda Seeding (Defensive Lessons): arXiv:2611.20045
- Agent Authenticator: arXiv:2611.19536
- Auditable Authorization Across Model, Harness & Workflow Layers: arXiv:2611.19237
- Beyond Prompts (Runtime Contracts for Coding Agents): arXiv:2611.19549
- Safe Resemblance, Silent Propagation (Text-Similarity Guardrail Limits): arXiv:2611.21520
- Readie (Learned Startup Snapshots for AI Agent Code Sandboxes): arXiv:2611.22171
- Isabelle Pool Server (Pooled Prover Verification Service): arXiv:2611.24788
- Network-Exposed Configuration Attacks on Social Robots (Defensive Lessons): arXiv:2611.22761
- PIPETTE (Prompt Injection Purple-Teaming for Robust LLM Agents): arXiv:2611.24362
- What Survives the Shift from Text to Pixels? (Image-Rendered Document IPI Limits): arXiv:2611.24231
- Epistemic Guard (Out-of-Process MCP Receipt Proxying & Post-Turn Prose Supervision): arXiv:2611.27095
- Tether (Verified Stateful Policy Engine & Speculative Syscall Inference): arXiv:2611.25599
- LLM Agent Authorization Across Context Compaction (Witnessed-Request Gate): arXiv:2611.32194
- PATH (Hierarchical Batch Authorization Proposals): arXiv:2611.32018
- MobileGrail (Compact On-Device Mobile GUI Guardrails): arXiv:2611.29847
- Trustworthy Agentic Lunar Robotics / AKR (Contingent Execution Kernel): arXiv:2611.30179
- FATCAT (Chip-Level Alignment Fault Tolerance — Defensive Lessons): arXiv:2611.31129
- SoK: Assessing the Evolution of LLM Capability in Software Vulnerability Research: arXiv:2611.26601
- Conartist / ClawBench (CUA Consistency & Risk-Auditing Surfaces — Defensive Lessons): arXiv:2611.29977
