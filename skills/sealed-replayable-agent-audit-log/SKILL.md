---
name: sealed-replayable-agent-audit-log
description: >-
  Record, seal, replay, diff, and govern black-box AI agent runs using tamper-
  evident capsules with post-exit filesystem sanitization, tri-proof
  cryptographic sealing (DSSE, RFC 3161 TSA, Merkle log), fail-closed mocked
  replay, structural LCS call-alignment diffing, and maker-checker promotion.
  Derived from NovaFabric (arXiv:2610.34594).
source: https://arxiv.org/abs/2610.34594
license: CC-BY-4.0
repository: https://github.com/Marontis/agentic-engineering
---

# Sealed Replayable Agent Audit Log

> **Source**: [NovaFabric: A Black-Box Recorder for AI Agents with Sealed, Replayable, Diffable and Auditable Runs](https://arxiv.org/abs/2610.34594) (Ardebili, 2026) | Praxis: `src:2610-34594v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

- Building a tamper-evident black-box flight recorder for autonomous or tool-using AI agents where every model call, MCP tool invocation, prompt, environment digest, and output artifact must be captured into a portable, verifiable capsule.
- Replaying historical agent runs offline in CI or incident response without burning live LLM tokens or re-executing destructive external side effects.
- Running deterministic structural regression diffs across two agent runs (`baseline` vs. `candidate`) when trace steps shift slightly due to non-deterministic model outputs or transport retries.
- Producing regulator-ready, cryptographically signed audit bundles (supporting GDPR Article 17 crypto-shredding, legal holds, and FDA 21 CFR Part 11 signing-intent bindings) and enforcing maker-checker governance before promoting agent configurations to production.

## Overview

Observability tracing platforms record high-level telemetry spans in mutable remote databases, leaving three operational gaps for high-assurance agent engineering: traces can be altered after the fact or polluted by a compromised agent process before finalization, traces cannot be replayed offline with fail-closed mutation guarantees, and naive line-by-line trace comparisons break whenever transport retries or minor step reorderings occur.

Derived from **NovaFabric** (`v0.107.0`), this skill organizes agent run auditing around a self-contained **Capsule** directory (`capsule.yaml`, `events.jsonl`, `blobs/`, `environment.json`, `attestations/`, `redaction-proof.json`, `capture-health.json`, and `replay/`) and five composable lifecycle stages: **Capture**, **Seal**, **Replay**, **Diff**, and **Govern/Export**. Across benchmark workloads on Azure `D8s_v5`, wire interception adds only **`0.41–0.55 ms` marginal latency per intercepted call** (`3.6%` on an `11.5 ms` call, `0.5%` on a `102 ms` call), trivial run capture completes in a median of **`168.8 ms`** ($n = 30$, with lazy `--fast-emit` SDK patching cutting startup from `2,068 ms` to `464 ms`), cryptographic sealing (`seal.seal-call.median`) completes in **`< 50 ms`**, sandboxed OPA policy evaluation runs in **`29 ms` p99**, and full Merkle log verification scales at **`~1.2–2 s` per million entries**.

---

## Step-by-Step Procedure

### Stage 1: Capture at the Wire & Sanitize the Capsule Post-Exit

1. **Intercept SDK and Wire Calls Fail-Open with Logical-Call Grouping**:
   - Patch LLM SDKs (`OpenAI`, `Anthropic`, `MCP`), HTTP clients (`httpx`, `requests`, `aiohttp`, `urllib3`), and OpenTelemetry GenAI spans so request/response payloads stream to the caller without blocking. If disk back-pressure occurs, drop telemetry rather than crashing the agent and record exact drop counts in `capture-health.json`.
   - Group HTTP transport retries and redirects under a shared `logical_call_id` and mark retry attempts with `record_role: transport` so downstream token accounting, replay, and cross-run diffing operate on logical agent decisions rather than transient network hiccups.

2. **Treat the Capsule Directory as Untrusted Input After Workload Exit**:
   - Because the recorded agent process runs with write access to its working directory during execution, a compromised or prompt-injected workload may plant symlinks, FIFOs, sockets, or device nodes inside the capsule directory to trick the post-run sealer into reading or overwriting host files (such as `/etc/shadow` or signing keys).
   - Immediately after the workload process exits—and before running redaction, hashing, or sealing—walk the capsule tree without following links, remove every symbolic link, FIFO, socket, and special device file at any depth, and log every removed path in `capture-health.json` (`tampered_entries`), `redaction-proof.json`, and `capsule.yaml` (`metadata.capture_tampered: true`).
   - Disable all remote or external `$ref` resolution during JSON Schema validation of capsule artifacts.

3. **Run Atomic Secret Redaction, Residual Rescan, and Per-Subject PII Encryption**:
   - Scan all captured events and blobs for credentials (`gitleaks-core`), write redacted replacements to temporary files, and swap them via atomic rename (never writing in-place through existing file descriptors or links).
   - Execute a second **residual rescan** over the redacted outputs and write the signed verification summary to `redaction-proof.json`, followed by computing SHA-256 `evidence_digests` over every evidence file in `capsule.yaml`.
   - When handling personal data subject to GDPR Article 17 erasure, encrypt per-subject fields at capture time with a subject-specific AES-GCM Data Encryption Key (`--pii-subject <id>`) stored in an external key store (`dek.db`). To honor an erasure request later, delete the subject's key (crypto-shredding) without mutating the sealed capsule's cryptographic digests—unless an active legal hold is present, in which case reject erasure with a deterministic conflict code (exit code `3` / HTTP `409`).

---

### Stage 2: Seal with Three Independent Cryptographic Proofs & Trust Anchors

1. **Commit to Both File Content and Relative File Paths**:
   - Build the canonical capsule manifest over `capsule.yaml` and all evidence artifacts using domain-separated RFC 6962 v2 Merkle leaf hashes that bind **both the relative file path and the file content digest**. Hashing content alone allows an attacker to swap filenames between two valid blobs without invalidating the Merkle root.
   - Embed explicit signing-intent metadata (signer role, timestamp, and regulatory reason for signing per FDA 21 CFR §11.50) *inside* the signed payload prior to signature generation.

2. **Attach Three Orthogonal Proofs (`NovaSeal`)**:
   - *Who signed*: Generate a Dead Simple Signing Envelope (DSSE) signature using ECDSA P-256 or KMS keys and record the explicit `identity_trust` tier (`ca-anchored`, `local-ca-pinned`, `self-asserted`, or `none`).
   - *When it was sealed*: Obtain an RFC 3161 Time-Stamp Authority (TSA) token over the DSSE payload digest, verify the TSA signature and `messageDigest == H(TSTInfo)` plus offline CRL status, and record `timestamp_trust` (`anchored`, `unanchored`, `absent`, or `invalid`).
   - *Where it sits in history*: Append the seal digest to an append-only Merkle transparency log (`sealer_log`) and store the inclusion proof inside `attestations/`.

3. **Separate Structural Integrity ("Intact") from Anchor Authority ("Trusted")**:
   - During verification, evaluate mathematical integrity separately from trust-anchor lineage. In strict production verification (`--strict`), fail closed (exit code `1`) if any proof reports `unanchored_claims` (for example, a cryptographically intact self-signed capsule or an unanchored TSA certificate), and route CLI, web dashboard, and HTTP API verification through the exact same verifier implementation.

---

### Stage 3: Execute Fail-Closed Mocked Replay with a Mutation-Class Safety Ladder

1. **Serve Recorded Model and Tool Responses Deterministically**:
   - During offline replay, intercept LLM (`Chat Completions`, `Responses`, `Messages`) and tool (`MCP`, declared `@record.tool`) calls and serve the recorded responses from the capsule. Refuse unsupported SDK call surfaces explicitly rather than silently falling back to live network requests.

2. **Fail Closed on Replay Divergence with Deterministic Exit Codes**:
   - Terminate immediately with exit code `1` on any `ReplayDivergence`: an unrecorded model prompt, an unmatched tool name or argument hash, or an unconsumed recorded response remaining at run completion. Use distinct exit codes for environment/digest mismatches (exit `2`), unenforceable tool overrides (exit `3`), and replay timeouts (exit `124` at `600 s`).

3. **Gate Hybrid Live Fallback by Mutation Class and Sandboxed Policy**:
   - When running hybrid replay (where missing calls may optionally fall through to live execution), classify every tool into a six-tier mutation ladder: `none`, `read-only`, `idempotent-write`, `non-idempotent-write`, `external-side-effect`, or `unknown` (assigning `unknown` by default to all undeclared MCP tools).
   - Evaluate a `replay_mutating` OPA/Rego policy before permitting any live call above `read-only`. Execute the OPA evaluator in a stripped subprocess with an empty environment and dangerous built-ins (`opa.runtime`, `http.send`, `net.lookup_ip_addr`) removed so policy files cannot exfiltrate data or make network calls.

---

### Stage 4: Perform Structural Cross-Run Diffing & CI Regression Gating

1. **Align Model and Tool Calls Across Runs via Three-Pass Anchoring**:
   - Do not diff agent traces by raw array index. Align logical model calls between the baseline and candidate capsules in three passes:
     - *Pass 1*: Match calls sharing a unique `parent_span_id`.
     - *Pass 2*: Compute Longest Common Subsequence (LCS) anchors over calls with identical normalized request digests.
     - *Pass 3*: Pair remaining calls by relative position within the bounded intervals between LCS anchors.
   - Pair tool invocations by tool name plus canonical argument hash first, then by relative position, and diff all sampling hyperparameters (`temperature`, `seed`, `top_p`) alongside output divergence.

2. **Enforce a Four-State CI Exit-Code Contract**:
   - Return `0` when no structural or hyperparameter regression is detected, `1` when a structural call-graph or parameter difference is found, `2` when either capsule fails pre-diff integrity/symlink validation, and `3` when a multi-trial Sequential Probability Ratio Test (`--significance`) accepts the statistical regression hypothesis.

---

### Stage 5: Enforce Maker-Checker Promotion Governance & Signed Evidence Exports

1. **Require Dual Anchored Signatures Before Production Promotion**:
   - Gate every promotion into the `production` environment behind both an automated policy evaluation (`promote_direct`) and a **maker-checker** dual-signature check: the proposer signature and approver signature must chain to an operator trust list (`NOVAFABRIC_PROMOTE_SIGNERS` or pinned CA) and must possess distinct bound identities and key fingerprints (preventing self-approval via dual keys). Exempt only emergency rollbacks targeting a capsule SHA-256 that carries a prior production attestation.

2. **Export Self-Verifying in-toto / DSSE Evidence Bundles**:
   - When packaging runs for external auditors, emit a ZIP archive where `attestations/bundle.intoto.json` signs the digest of every individual ZIP member (`members_signed: true`) and computes an explicit `admissibility_status` (`self-authenticating` when all identity, TSA, and Merkle proofs are CA-anchored; `requires-foundation` when intact but self-asserted; `incomplete` when any required proof is missing).

---

## When NOT to Use

- **Ephemeral, zero-side-effect local chat completions**: Single-turn stateless text completions during local prototyping that invoke no tools, touch no sensitive data, and require neither regression testing nor compliance auditability.
- **Hard real-time control loops below 1 ms total budget**: While per-call wire interception adds only `0.41–0.55 ms` and sealing takes `< 50 ms` at the end of a run, sub-millisecond embedded control loops cannot absorb Python SDK interception overhead on the critical path.

---

## Related Artifacts

- **Rule**: [Agent Sandbox Safety](../../rules/agent-sandbox-safety.md)
- **Rule**: [Agent Evaluation Quality](../../rules/agent-evaluation-quality.md)
- **Rule**: [ADK Security and Evaluation](../../rules/adk-security-and-evaluation.md)
- **Skill**: [Multi-Hop Delegation Authorization Propagation](../multi-hop-delegation-auth-propagation/SKILL.md)
- **Skill**: [LLM API Relay Integrity Verification](../llm-api-relay-integrity-verification/SKILL.md)
