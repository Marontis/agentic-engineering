---
name: receipt-bound-mcp-prose-supervision
description: >
  Intercept Model Context Protocol (MCP) wire calls in an out-of-process proxy
  that scrubs signing secrets and mints domain-separated Ed25519 execution
  receipts, verify post-turn assistant action claims against target-bound
  executed-and-ok receipts on CPU, and block unverified LLM narration from
  entering durable SQLite memory. Derived from Epistemic Guard (arXiv:2611.27095).
source: https://arxiv.org/abs/2611.27095
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Receipt-Bound MCP Prose Supervision

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

Use this skill when hardening **tool-using Model Context Protocol (`MCP`) agents** against post-turn **action fabrication** (claiming in assistant prose that a file write, database mutation, ticket update, or deployment succeeded when the tool actually failed, crashed, or never ran), **narration-sourced durable memory poisoning**, and **syndicated wire-copy echo** in retrieval-augmented generation (`RAG`).

## When to Use

- Agents invoke side-effecting `MCP` tools (`stdio` or local JSON-RPC servers) where operators or downstream workflows act on the assistant's natural-language completion report (`OWASP Agentic Top 10 ASI02`, `ASI08`).
- Assistant summaries or extracted session facts are written into a durable local store (`SQLite`, session ledger, or knowledge base) where unverified model prose could harden into trusted cross-session memory (`ASI06`).
- GPU memory is fully reserved for the primary agent model (`0 MiB` spare VRAM), making `12B–14B` GPU LLM-as-a-judge post-turn monitors impractical or too slow (`70–81 ms` median per turn).
- High-stakes `RAG` workflows count corroborating web sources across domains where wire-service syndication creates an illusion of independent agreement.

Prefer [`sealed-replayable-agent-audit-log`](../sealed-replayable-agent-audit-log/SKILL.md) when sealing post-exit run directories for offline CI replay and diffing, [`mcp-decode-provenance-binding`](../mcp-decode-provenance-binding/SKILL.md) when gating *pre-execution* critical tool calls against untrusted decode-tool outputs, and [`mcp-hallucination-boundary-guards`](../mcp-hallucination-boundary-guards/SKILL.md) when cutting off infeasible multi-step probing loops before turn completion.

**Deference to the repository acceptance gate:** Whenever expanding the supervisor's verb-to-tool-family lexicon, adjusting clause-masking rules, or retraining the local `action_claim` classifier across deployments, pass the candidate update through `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../../rules/recursive-improvement.md) (no regression beyond baseline noise margin $\delta$ on held-out benign traces and zero-tolerance regression on fabricated-action testbeds).

---

## Core Insight

Pre-execution capability monitors verify what tools an agent *is allowed to call*, and flight recorders log what *happened on the wire*, but neither stops an LLM from **reporting success in prose after a tool error, schema rejection, server crash, or skipped call**—nor from **re-ingesting its own ungrounded narration into persistent memory**. Generic Natural Language Inference (`NLI`) models also fail this check (`52.8%` accuracy, `24.59%` recall) because tool receipts record low-level JSON-RPC wire fields rather than natural-language premises, causing `79.35%` (`73/92`) of `NLI` false negatives to score `neutral` rather than `contradiction`.

`Epistemic Guard` (`v0.5.2`, `arXiv:2611.27095`) closes this loop at **`0 MiB` GPU VRAM** by coupling an out-of-process cryptographic `MCP` wire proxy, a two-stage CPU INT8 prose-to-receipt supervisor, and a provenance-domain SQLite write gate:

| Supervision Architecture | Frozen Suite Accuracy (`N = 250`) | Recall / Benign FPR (`N = 250`) | Frozen p50 Latency | `Live-60` Hazard Recall / Accuracy | GPU VRAM |
|:-------------------------|:----------------------------------|:--------------------------------|:-------------------|:-----------------------------------|:---------|
| **`ReceiptSupervisor` (Hybrid CPU INT8 + Ed25519 Receipts)** | **`93.2%`** (`233/250`, 95% CI `[89.38%, 95.71%]`) | **`96.72%`** / **`10.16%`** (`TP=118, TN=115, FP=13, FN=4`) | **`17.9 ms`** (`8.62 ms` 1-clause, `35.83 ms` p95) | **`96.15%`** (`25/26`) / **`76.67%`** (`9.16 ms` p50) | **`0 MiB`** |
| **`Mistral-NeMo-12B` GPU Judge** | `86.8%` (`-6.4` pp, McNemar $p = 0.0259$) | `89.34%` / `15.62%` | `80.58 ms` (`4.5x` slower) | `76.92%` / `80.0%` ($p = 0.7905$, `71.69 ms`) | `8,844 MiB` |
| **`Phi-4-14B` GPU Judge** | `86.4%` (`-6.8` pp, McNemar $p = 0.0095$) | `87.70%` / `14.84%` | `76.24 ms` (`4.26x` slower) | `84.62%` / `65.0%` ($p = 0.1671$, `67.04 ms`) | `12,214 MiB` |
| **`Stage-1-only` (Classifier Without Receipts)** | `84.8%` | `100.0%` / `27.34%` | `24.98 ms` | `96.15%` / `58.33%` (`70.59%` FPR, $p = 0.001$) | `0 MiB` |
| **`Regex + Receipts` (Heuristic Baseline)** | `64.0%` | `30.33%` / `3.91%` | `0.15 ms` | — | `0 MiB` |
| **`DeBERTa-v3-xsmall` NLI (`91.1 MB` INT8)** | `52.8%` | `24.59%` / `20.31%` | `10.97 ms` | — | `0 MiB` |

---

## Step-by-Step Procedure

### Step 1: Interpose an Out-of-Process `MCP` Wire Proxy with Secret Scrubbing & Domain-Separated Keys

Place a standalone proxy process (`mcp-proxy`) on the `stdio` or JSON-RPC transport between the agent host and every child `MCP` server so neither the LLM runtime nor a compromised tool server can forge execution receipts:

1. **Scrub Signing Secrets Before Spawning Child Servers**: Hold the master key (`EPISTEMIC_GUARD_MASTER_KEY`) or explicit proxy key (`EPISTEMIC_GUARD_MCP_KEY_HEX`) strictly inside the proxy process and strip both environment variables from the `env` dictionary passed to every child `MCP` server (`0` secret leaks across `40` fault-injected calls).
2. **Derive Domain-Separated Ed25519 Keys (`RFC 5869` HKDF-SHA256)**: Partition provenance into **seven explicit domains**—`USER_EXPLICIT`, `USER_CONFIRMED`, `TOOL_VERIFIED`, `LISP_ASSERTION`, `INFERRED`, `LLM_NARRATION`, and `TOOL_CONTENT_UNTRUSTED`—and derive `32`-byte Ed25519 keypairs (`64`-byte signatures) using context string `"epistemic-guard:provenance:v1:" || domain`. Crucially, **omit signing constructors for `LLM_NARRATION` and `TOOL_CONTENT_UNTRUSTED`** (`5` signable domains total) so model prose and raw external tool payloads can never acquire valid provenance signatures even if higher-layer application code is misconfigured.
3. **Canonicalize Wire Payloads Strictly**: Serialize signed envelopes (`session_id`, `turn_id`, `call_id`, `tool_name`, `args_sha256`, `result_sha256`, `executed`, `ok`, `error_kind`) using sorted keys, compact separators, UTF-8 encoding, and **`allow_nan=False`**—rejecting `NaN`/`Infinity` floats, key-reordered hash collisions, and cross-session receipt replays before signature verification.

---

### Step 2: Classify JSON-RPC Wire Outcomes into Four Execution States & Append to a Merkle Ledger

Never equate "a JSON-RPC response arrived" with "the tool succeeded." Inspect every `tools/call` exchange on the wire and record one of four explicit `(executed, ok, error_kind)` states before signing the receipt:

1. **Confirmed Success (`executed = true, ok = true`)**: Valid JSON-RPC `result` object where `result.isError` is absent or `false`. **Only** receipts in this state may ground an affirmative past-tense completion claim.
2. **Tool-Reported Execution Failure (`executed = true, ok = false, error_kind = "mcp_tool_error"`)**: Valid JSON-RPC `result` carrying `result.isError == true`. The server ran and explicitly reported failure.
3. **Pre-Execution Protocol / Schema Rejection (`executed = false, ok = false`)**: Standard JSON-RPC error codes `-32700` (parse error), `-32600` (invalid request), `-32601` (method not found), or `-32602` (invalid params), or error messages matching deterministic argument-validation failure markers.
4. **Ambiguous Crash or Non-Standard Error (`executed = true, ok = false`)**: If the child server closes `stdout` (`EOF`) or crashes mid-call (`error_kind = "mcp_server_eof"`), or returns a non-standard server error code, **default conservatively to `executed = true, ok = false`**—recording that partial side effects may have occurred on disk or over the network while still refusing to treat the call as `ok = true`.

Append every signed receipt under an exclusive process/thread lock to an **`RFC 6962` SHA-256 Merkle transparency log** (`0x00` leaf prefix, `0x01` internal node prefix; exportable as `AER-1` receipts with `JCS` canonicalization) so auditors can verify receipt inclusion (`200/200` verified) and detect any post-hoc log tampering (`200/200` mutated payloads rejected).

---

### Step 3: Supervise Post-Turn Assistant Prose Against Target-Bound `ok = true` Receipts

Run a two-stage CPU supervisor (`ReceiptSupervisor`) synchronously on every assistant response before displaying it to the user or advancing the workflow:

1. **Stage 1 — Syntactic Masking & Clause-Level Action-Claim Detection**:
   - Strip fenced code blocks and inline quotes so code examples are not misread as execution claims.
   - Split remaining prose into clauses and apply deterministic **negation, conditional, future/intent, and refusal masks** (so honest failure reports like *"I tried to write `config.yaml`, but permission was denied"* or *"I can delete the branch if you confirm"* are exempted).
   - Score unmasked clauses with a compact `SHA-256`-pinned INT8 transformer classifier (`action_claim`, `82.67 MB` OpenVINO/ONNX CPU model; `8.62 ms` single-clause, `17.9 ms` multi-clause p50). Optionally parse structured side-effect declarations (`[ACTION: verb target]`) alongside prose so compliant models emit explicit claims while non-compliant models are still caught by prose classification.
2. **Stage 2 — Cryptographic Receipt & Target-Boundary Matching**:
   - Map each detected past-tense action verb (`wrote`, `updated`, `deleted`, `committed`, `sent`, `deployed`) to its required `MCP` tool family.
   - Verify the Ed25519 signature (`TOOL_VERIFIED` domain), current `(session_id, turn_id)` binding, and **`executed == true && ok == true`** flags on candidate receipts.
   - Enforce **path- and token-boundary target matching** between the noun/path named in the assistant's clause (e.g., `deploy/prod.yaml` or `issue #142`) and the canonicalized `args` in the signed receipt. **Never allow a zero-argument status or listing tool to act as a wildcard receipt for a named file or resource target.**
3. **Fail-Closed Remediation**: When any affirmative action claim lacks a matching `executed == true && ok == true` receipt, block or rewrite the ungrounded claim into a verified status notice citing the actual wire outcome (`not called`, `schema error`, or `mcp_tool_error`).

---

### Step 4: Gate Durable Memory Writes by Provenance Signature & De-Syndicate RAG Mirrors

Prevent fabricated prose and syndicated web mirrors from corrupting persistent agent state:

1. **Enforce an Append-Only Provenance-Signed SQLite Gate (`SQLiteProvenanceStore`)**:
   - Open durable memory transactions with `BEGIN IMMEDIATE` and verify a valid Ed25519 signature from one of the five authorized domains (`USER_EXPLICIT`, `USER_CONFIRMED`, `TOOL_VERIFIED`, `LISP_ASSERTION`, `INFERRED`) before every `INSERT` (`200/200` authorized writes accepted; `100/100` `LLM_NARRATION` and forged-key writes blocked).
   - Install `BEFORE UPDATE` and `BEFORE DELETE` SQLite triggers calling `RAISE(ABORT, ...)` on committed provenance rows so compromised application code cannot silently rewrite or erase historical provenance records (`2/2` direct SQL mutation attempts aborted). Supersede outdated facts via append-only versioned assertions rather than in-place mutation.
2. **Collapse Syndicated Wire Mirrors Before Counting RAG Corroboration**:
   - Before treating $k$ retrieved URLs from different hostnames as independent evidence on high-hazard queries, cluster documents that exceed lexical near-duplicate thresholds (`k = 4` word-shingle Jaccard $\ge 0.55$, `3`-shingle Jaccard $\ge 0.25$, anchor-token Jaccard $\ge 0.45$, or `64`-bit SimHash Hamming distance $\le 12$) and count each mirror cluster (`45/45` wire-copy clusters across `135` URLs collapsed) as **one** provenance source against domain hazard proof floors (`3` hazard tiers $\times$ `4` consumer contexts).

---

## Environment Caveats & Failure Modes

- **Custom Domain Tool Stems Must Be Registered in the Verb-to-Tool Lexicon**: On `Live-60`, `6` of the `13` false positives (`38.24%` live FPR on `34` grounded traces) occurred when agents called custom-named `MCP` tools whose verb stems were absent from the default lexicon. Auto-extract verb/resource mappings from registered `MCP` server schemas at startup and gate lexicon updates through [`recursive-improvement.md`](../../rules/recursive-improvement.md).
- **Contrastive Compound Clauses (`"attempted X, but failed"`)**: The remaining `7/13` `Live-60` false positives arose when comma-based clause splitting separated *"I attempted to update the record,"* from *", but the server returned an error."* Split clauses on discourse markers while propagating contrastive failure scope (`but failed`, `however ... rejected`, `attempted to ... without success`) across paired clauses before Stage-1 scoring.
- **Cold-Start Model Loading**: Loading the `82.67 MB` INT8 `action_claim` graph takes `921.8 ms` median (`1,044.6 ms` p95) on first invocation; warm-load and SHA-256-verify model weights once at daemon startup so per-turn supervision stays at `9–18 ms` p50.
- **Paraphrase Ceiling of Lexical Shingle De-Syndication**: `k = 4` shingle + SimHash clustering catches `100.0%` of verbatim wire mirrors, dateline/footer wrappers, and `~15%` light synonym edits, **but drops to `40.0%` at `~30%` lexical edits and `0.0%` under `~45%` clause restructuring or `>80%` abstractive rewrites**. Do not rely on lexical shingling alone against adversarial multi-domain agenda seeding; pair with publisher/temporal independence checks in [`agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md).

---

## Cross-References

- **Related Rules**:
  - [`agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — `"DON'T: Treat HTTP 200 / success tool return codes as workflow success without state verification"`, `"DO: Sweep and strip symlinks, FIFOs, sockets, and special device files from agent working directories after workload exit before hashing or sealing"`, and `"DON'T: Let untrusted web pages redefine ranking criteria in deep-research loops or equate hostname counts with independent corroboration"`
  - [`multi-agent-coordination.md`](../../rules/multi-agent-coordination.md) — `"DO: Attach Merkle-proven log receipts and three-valued claim checkers to inter-agent handoff messages before trusting claimed side effects"`
  - [`recursive-improvement.md`](../../rules/recursive-improvement.md) — `"DO: Pass every self-modification through one acceptance gate"`
- **Related Skills**:
  - [`sealed-replayable-agent-audit-log`](../sealed-replayable-agent-audit-log/SKILL.md) — Post-exit workload directory sanitization, tri-proof capsule sealing, and mocked replay (`NovaFabric`)
  - [`mcp-decode-provenance-binding`](../mcp-decode-provenance-binding/SKILL.md) — Decode-time HMAC provenance binding and pre-execution sink taint gating
  - [`proof-carrying-agent-messages`](../proof-carrying-agent-messages/SKILL.md) — Inter-agent `PCM` envelopes backed by RFC 6962 Merkle log inclusion proofs
  - [`mcp-hallucination-boundary-guards`](../mcp-hallucination-boundary-guards/SKILL.md) — Pre-flight capability checks and two-call probing circuit breakers (`MCPHallu`)

## Sources

- Maxwell, S. (2026). *Epistemic Guard: Out-of-Process MCP Receipt Proxying, Post-Turn Prose Supervision, and Provenance-Gated Memory for Tool-Using Autonomous Agents*. [arXiv:2611.27095](https://arxiv.org/abs/2611.27095) (`src:2611-27095v1`).
