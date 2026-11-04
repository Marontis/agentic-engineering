---
name: mcp-decode-provenance-binding
description: >-
  Bind HMAC-authenticated trust labels and transitive dependency lineage
  inside the MCP transport layer whenever a concealment-reversing tool
  (steganography extraction, OCR, metadata parser, Base64 decoder) emits
  text, propagate context taint across multi-agent relays, block side-effecting
  sink tools on untrusted data or context lineage, and support audited
  trusted-promotion for benign tasks. Derived from "Agentic AI Defense:
  Decode-Time Provenance Binding for MCP" (arXiv:2610.31974).
source: src:2610-31974
---

# MCP Decode-Time Provenance Binding

## When to Use

- Multi-agent Model Context Protocol (MCP) pipelines where specialist workers invoke concealment-reversing tools — steganography extractors, OCR engines, image/PDF metadata parsers, archive unpackers, or Base64/encoding decoders — and relay results to an orchestrator or peer agents.
- Workflows that ingest multimodal external artifacts (emails with inline `cid:` or `data:` signature logos, PDFs, screenshots, attachments) after perimeter scanners (antivirus, DLP, content disarm and reconstruction) have already cleared the carrier file.
- High-impact agentic systems where side-effecting sink tools (`export_secrets`, `send_email`, database writes, payment execution) must never be triggered by instructions or arguments that entered the pipeline only through a decode boundary, unless explicitly promoted under audit.

## Core Insight

In a multi-agent tool pipeline, an indirect prompt injection hidden inside an image or binary carrier is inert bytes at the perimeter; it becomes executable natural-language instruction only at the **decode boundary** when an agent invokes a concealment-reversing tool and passes the decoded string back into the shared orchestration context. Once that string is forwarded as a plain tool result, downstream agents cannot distinguish it from trusted configuration or user instructions (**cross-modal trust laundering**).

In-process information-flow taint tracking fails when the decoded text crosses process or host boundaries via inter-agent messages, while naive agent-carried provenance labels fail **valid-label substitution** — a compromised or prompt-injected orchestrator whose reasoning was steered by an untrusted decoded message can simply pass a genuine `Trusted` handle from an earlier benign tool call (`read_config`) as the argument to a critical sink (`export_secrets`).

Stopping cross-modal trust laundering requires **four jointly necessary properties** enforced inside the MCP mediation layer rather than the agent prompt:
1. **Decode-boundary taint marking (`decode_taint`)**: Any output from a registered concealment-reversing tool $\mathcal{D}$ is born `Untrusted`.
2. **Layer-confined cryptographic authentication**: Every tool return receives a tamper-evident HMAC binding minted with a gateway-confined secret key $k_{\mathrm{gw}}$ never exposed to agent processes.
3. **Layer-maintained data and context lineage**: The MCP gateway records both argument-handle dependencies $\delta$ and per-context taint $\mathrm{taint}(c)$ in a gateway-owned ledger $\mathcal{L}$, propagating context taint across inter-agent relays.
4. **Sink mediation with audited promotion (`trusted_promotion`)**: Critical sink tools $\mathcal{C}$ reconstruct the transitive dependency closure from $\mathcal{L}$ and inspect $\mathrm{taint}(c) \setminus \mathrm{promoted}(c)$, failing closed unless an untrusted origin was explicitly promoted for a narrow, audited task.

**Evidence** (Yocam et al., arXiv:2610.31974):
- **Testbed**: Local multi-agent MCP pipeline (`Qwen/Qwen2.5-0.5B-Instruct` agents over a real `FastMCP` stdio server) evaluated across **24 adaptive payloads** = **3 steganographic carriers** (spatial LSB replacement with PSNR $\approx 76\text{ dB}$, SSIM $\approx 1.000$; frequency-domain $8 \times 8$ block DCT quantization with PSNR $\approx 18\text{ dB}$, SSIM $\approx 0.94$; and Base64-encoded PNG metadata text chunks with SSIM $1.000$) $\times$ **8 text-level evasions** (plain, benign-worded, Base64, token-split, Cyrillic homoglyph, zero-width, Unicode-confusable, and HTML-comment wrapping).

| Defense Configuration | Leaks / Total | Attack Success Rate (ASR) | Failure Mode |
|:---|:---:|:---:|:---|
| **Undefended MCP pipeline** | 24 / 24 | **100.0%** | Decoded payload treated as trusted peer text |
| **Content scanner (keyword / DLP)** | 15 / 24 | **62.5%** | Bypassed by Base64, homoglyph, zero-width, benign-worded, and comment evasions |
| **Regex intent parser** | 15 / 24 | **62.5%** | Bypassed by obfuscated and benign-framed phrasings |
| **In-process data-flow taint (IFC baseline)** | 0 / 24 (single process) | **0.0%** (local) / **Leaks** on cross-process relay | Loses taint across unauthenticated inter-agent boundaries |
| **Decode-time provenance binding (Full)** | **0 / 24** | **0.0%** | Blocks all 24 carrier $\times$ evasion combinations and cross-agent relays |

- **4-Component Ablation (Table IV)**: Removing any single mechanism component re-opens an attack class:
  - Full mechanism: `blocked` (honest relay) / `blocked` (valid-label substitution) / `blocked` (forged relay).
  - $-$ Decode marking (`decode_taint`): `LEAK` / `LEAK` / `LEAK`.
  - $-$ Cryptographic authentication (HMAC): `blocked` / `blocked` / `LEAK` (degrades to the unauthenticated IFC baseline).
  - $-$ Trusted lineage tracking (ledger $\mathcal{L}$ + context taint): `blocked` / `LEAK` / `blocked` (compromised orchestrator substitutes a genuine `Trusted` config handle while omitting the `Untrusted` decode origin).
  - $-$ Sink mediation: `LEAK` / `LEAK` / `LEAK`.
- **Multi-hop relay & legitimate utility**: Provenance verification holds across **1, 3, 5, and 10** inter-agent relay hops and blocks compromised workers that rewrite payloads, forge `Trusted` labels, or strip bindings. On 3 benign tasks (including an OCR invoice-number payment workflow), strict sink blocking without promotion completes **2/3 (67%)** of tasks (1 false block); adding audited `trusted_promotion` recovers **3/3 (100%)** benign task completion while still blocking all attacks.
- **Latency overhead**: HMAC-SHA256 signing (`MintBinding`) takes $\approx 8.3\,\mu\text{s}$ and verification (`EnforceCritical`) takes $\approx 8.7\,\mu\text{s}$ ($\approx 17\,\mu\text{s}$ combined, or **0.16%** of a warm 11 ms MCP stdio decode round-trip). Full ledger + closure walks take $9.5\,\mu\text{s}$ at depth 1, $72.6\,\mu\text{s}$ at depth 10, $0.68\text{ ms}$ at depth 100, and $6.6\text{ ms}$ at depth 1000.

---

## Procedure

### 0. Partition Registered MCP Tools into Decode ($\mathcal{D}$) and Critical Sink ($\mathcal{C}$) Sets

At MCP server registration time, maintain two server-authored sets in gateway configuration (never modifiable by agents or dynamic tool metadata):

1. **Concealment-reversing decode tools ($\mathcal{D}$)**: Any tool that extracts text or structured fields from an opaque, compressed, encoded, or non-text representation:
   - Steganography / pixel analysis (`extract_stego`, barcode/QR decoders)
   - Optical character recognition (`ocr_image`, document layout parsers)
   - Container / metadata extractors (EXIF/PNG chunk readers, PDF annotation/XMP parsers, archive unpackers)
   - String decoders (`base64_decode`, hex/URL/rot decoders, deobfuscators)
2. **Critical side-effecting sinks ($\mathcal{C}$)**: Any tool that mutates external state, exfiltrates data, or crosses a security boundary (`export_secrets`, `send_email`, `http_post`, `write_file`, `execute_payment`, `update_permissions`).

Audit the completeness of $\mathcal{D}$ whenever a new MCP server is connected: an unregistered decoder in the pipeline allows steganographic or encoded payloads to enter as `Trusted`, whereas placing a purely benign non-decoding reader into $\mathcal{D}$ causes unnecessary taint requiring promotion.

### 1. Mint HMAC-Authenticated Provenance Bindings at Tool Return (`MintBinding`)

Intercept every MCP tool return inside the trusted gateway before delivering the result to the calling agent. Maintain a gateway-confined secret key $k_{\mathrm{gw}}$ (held in gateway memory or an HSM, never readable by agent processes) and an append-only provenance ledger $\mathcal{L}$.

When tool $t$ returns payload $p$ in agent execution context $c$ after being invoked with gateway-issued argument handles $I$:

1. **Resolve argument dependencies from handles, not agent claims**:
   $$\delta \leftarrow \{\mathrm{id}(i) : i \in I\}$$
2. **Assign contagious trust (`decode_taint`)**:
   $$\tau \leftarrow \begin{cases} \textsc{Untrusted} & \text{if } t \in \mathcal{D} \text{ or } \exists i \in I : \tau_i = \textsc{Untrusted} \\ \textsc{Trusted} & \text{otherwise} \end{cases}$$
3. **Assign origin tag**:
   $$\pi \leftarrow \begin{cases} \texttt{decode:}t & \text{if } t \in \mathcal{D} \\ \texttt{tool:}t & \text{otherwise} \end{cases}$$
4. **Compute HMAC authentication tag** over the canonical serialization of the payload, tool identifier, trust label, provenance tag, and dependency set (conceptually binding $\tau = \mathrm{HMAC\text{-}SHA256}(k_{\mathrm{gw}}, \mathrm{id} \parallel \mathrm{trust} \parallel \mathrm{source\_tool} \parallel t)$ and exact lineage):
   $$m \leftarrow \mathrm{canonical}(p, t, \tau, \pi, \delta), \qquad \sigma \leftarrow \mathrm{HMAC\text{-}SHA256}_{k_{\mathrm{gw}}}(m)$$
5. **Commit to gateway ledger and taint context**:
   - Store binding tuple $\ell = (p, t, \tau, \pi, \delta, \sigma)$ in $\mathcal{L}$ under opaque handle $\mathrm{id}(\ell)$.
   - If $\tau = \textsc{Untrusted}$, insert $\mathrm{id}(\ell)$ into the active context taint set $\mathrm{taint}(c) \leftarrow \mathrm{taint}(c) \cup \{\mathrm{id}(\ell)\}$.
   - Return `(p, id(ℓ))` to the agent.

```
function MintBinding(payload p, tool t, input_handles I, context c):
    delta <- { id(i) for i in I }                  # resolved from ledger L, never agent-supplied
    if t in D or any(L[id].tau == UNTRUSTED for id in delta):
        tau <- UNTRUSTED
    else:
        tau <- TRUSTED
    pi <- ("decode:" + t) if t in D else ("tool:" + t)
    sigma <- HMAC_SHA256(k_gw, canonical(p, t, tau, pi, delta))
    record l = (p, t, tau, pi, delta, sigma) in L
    if tau == UNTRUSTED:
        taint(c).add(id(l))
    return (p, id(l))
```

### 2. Propagate Context Taint Across Inter-Agent Relays

In a multi-agent workflow, a specialist worker (e.g., an image-analysis subagent) often summarizes or paraphrases a tool output in natural language before sending it to an orchestrator or peer agent. Because free-text paraphrasing strips explicit argument handles, track provenance across **mediated inter-agent channels**:

1. Route all inter-agent messages through the MCP mediation layer rather than direct peer-to-peer sockets.
2. When agent context $c_A$ sends message $m_{A \to B}$ to recipient context $c_B$, mint a relay binding in $\mathcal{L}$ whose dependency set $\delta$ includes $\mathrm{taint}(c_A)$ and propagate context taint:
   $$\mathrm{taint}(c_B) \leftarrow \mathrm{taint}(c_B) \cup \mathrm{taint}(c_A)$$
3. Reject any inter-agent tool-result forwarding whose handle $\mathrm{id}(\ell)$ is missing from $\mathcal{L}$ or whose payload $p$ no longer matches $\sigma = \mathrm{HMAC\text{-}SHA256}_{k_{\mathrm{gw}}}(\mathrm{canonical}(p, t, \tau, \pi, \delta))$.

### 3. Enforce Lineage and Context Checks at Critical Sinks (`EnforceCritical`)

Before executing any critical sink tool $g \in \mathcal{C}$ invoked from context $c$ with argument handles $H$:

1. **Reconstruct transitive dependency closure**: Starting from $H$, walk $\delta$ pointers in the gateway ledger $\mathcal{L}$ to collect the transitive closure $S$ of all ancestor bindings. If any handle in $H$ or $\delta$ does not exist in $\mathcal{L}$, **block immediately** (`incomplete lineage`).
2. **Verify cryptographic integrity**: For every binding $\ell = (p, t, \tau, \pi, \delta, \sigma) \in S$, recompute $\mathrm{HMAC\text{-}SHA256}_{k_{\mathrm{gw}}}(\mathrm{canonical}(p, t, \tau, \pi, \delta))$. If any signature mismatches, **block immediately** (`forged or stripped binding`).
3. **Check data-flow lineage**: If any $\ell \in S$ has $\tau = \textsc{Untrusted}$ and $\mathrm{id}(\ell) \notin \mathrm{promoted}(c)$, **block immediately** (`untrusted data lineage`).
4. **Check context-level taint (defeating valid-label substitution)**: Even if every explicit argument handle in $H$ is `Trusted` (e.g., a genuine handle from `read_config`), inspect the calling context's taint set:
   $$\text{if } \mathrm{taint}(c) \setminus \mathrm{promoted}(c) \neq \emptyset \implies \textsc{Block}\ (\text{untrusted context lineage})$$
5. If and only if all four checks pass, execute $g$ and log the verified closure $S$.

```
function EnforceCritical(sink_tool g, arg_handles H, context c):
    if any h in H not in L:
        return BLOCK("missing argument binding")
    S <- TransitiveClosure(L, H)                   # walk delta sets in gateway ledger
    if S contains unresolved dependency d:
        return BLOCK("incomplete lineage")
    for l = (p, t, tau, pi, delta, sigma) in S:
        if sigma != HMAC_SHA256(k_gw, canonical(p, t, tau, pi, delta)):
            return BLOCK("forged or modified binding")
        if tau == UNTRUSTED and id(l) not in promoted(c):
            return BLOCK("untrusted data lineage")
    if (taint(c) \ promoted(c)) is not empty:
        return BLOCK("untrusted context lineage (valid-label substitution)")
    return ALLOW
```

### 4. Apply Audited Trusted-Promotion (`trusted_promotion`) for Legitimate Workflows

When a business workflow legitimately requires data extracted by a decode tool $t \in \mathcal{D}$ to drive a critical sink $g \in \mathcal{C}$ (for example, OCR-extracting an invoice amount and vendor ID from a scanned receipt to pre-fill a payment tool):

1. **Never allow an LLM agent to self-promote** an `Untrusted` binding or clear $\mathrm{taint}(c)$.
2. Expose a privileged, policy- or human-gated promotion primitive `trusted_promotion(origin_id, context c, schema_validator, approver_id)`:
   - Validate that the decoded payload $p$ at `origin_id` conforms to a strict, task-specific deterministic schema (e.g., regex/numeric bounds for an invoice number and amount, containing no free-text instruction fields) or obtain explicit human-in-the-loop confirmation showing the exact decoded value and its `decode:` provenance tag $\pi$.
   - Add `origin_id` to $\mathrm{promoted}(c)$ for the current session scope only.
   - Write an immutable audit record pairing the promotion event, `approver_id` / policy rule ID, and the original `Untrusted` binding $\ell$.
3. Re-run `EnforceCritical`: $\mathrm{taint}(c) \setminus \mathrm{promoted}(c)$ is now empty for that specific promoted origin, allowing the benign sink call to proceed while any unpromoted decoded origin in the same session still blocks execution.

---

## Environment Caveats

- **Completeness of the decode tool set $\mathcal{D}$ is a deployment obligation**: The cryptographic and lineage guarantees hold only for tools registered in $\mathcal{D}$. If an agent has access to a general-purpose code interpreter (`python_exec`, `bash`) or an uncatalogued third-party MCP tool that can decode Base64, parse PNG chunks, or run OCR without being listed in $\mathcal{D}$, an attacker can route the carrier through that unregistered tool to obtain a `Trusted` binding (Table XI). Treat any general code-execution sandbox that reads untrusted files as a member of $\mathcal{D}$.
- **Context taint is conservative within a session**: Once an agent context $c$ ingests an `Untrusted` decode output, $\mathrm{taint}(c)$ blocks all subsequent critical tool calls in $c$ unless the untrusted origin is promoted via `trusted_promotion` or the orchestrator spawns a fresh, untainted clean-room context for unrelated critical subtasks.
- **Protects critical tool actions, not free-text output fidelity**: Decode-time provenance binding prevents untrusted decoded content from triggering side-effecting sink tools $\mathcal{C}$. It does not prevent a tainted agent from generating a misleading natural-language summary to a human user if that summary does not invoke a tool in $\mathcal{C}$.
- **Unmediated side channels must be closed**: All inter-agent communication and tool invocations must pass through the MCP gateway holding $k_{\mathrm{gw}}$. If agents share an unmediated filesystem, shared memory, or direct network socket outside the MCP layer, taint propagation across contexts can be bypassed.

## Failure Modes & Mitigations

| Failure Mode | Symptom | Mitigation |
|:-------------|:--------|:-----------|
| **Valid-label substitution by a compromised orchestrator** | Orchestrator reads decoded stego text in context, then calls `export_secrets` passing a genuine `Trusted` handle from `read_config` while omitting the `extract_stego` handle | Enforce the context-taint check $\mathrm{taint}(c) \setminus \mathrm{promoted}(c) = \emptyset$ in `EnforceCritical` alongside argument-closure verification (Table III / Table IV) |
| **Unregistered decoder bypass** | Payload hidden in metadata or Base64 passes through a utility tool omitted from $\mathcal{D}$ and receives $\tau = \textsc{Trusted}$ | Audit all registered MCP tools for format-conversion, parsing, decompression, or code-execution capabilities at registration; default ambiguous parsers into $\mathcal{D}$ (Table XI) |
| **Over-broad decode set $\mathcal{D}$** | Benign configuration or database lookup tools are placed in $\mathcal{D}$, causing routine workflows to halt at critical sinks | Restrict $\mathcal{D}$ to concealment-reversing / cross-modal extraction tools and pair legitimate OCR/extraction workflows with schema-constrained `trusted_promotion` (Table XIII) |
| **Worker payload tampering or label forgery in multi-hop relay** | A compromised intermediate worker rewrites a tool result or swaps `Untrusted` to `Trusted` before relaying to the next hop | Verify $\sigma = \mathrm{HMAC\text{-}SHA256}_{k_{\mathrm{gw}}}(\mathrm{canonical}(p, t, \tau, \pi, \delta))$ against the gateway ledger $\mathcal{L}$ at every relay and sink boundary; never expose $k_{\mathrm{gw}}$ outside the gateway (Table XII) |
| **Deep dependency-closure latency spikes** | Long-running sessions accumulate $>1{,}000$ chained tool bindings, increasing `EnforceCritical` closure walk time ($\approx 6.6\text{ ms}$ at depth 1000) | Cache transitive taint booleans on immutable ledger nodes in $\mathcal{L}$ (making taint lookup $O(1)$ per handle while preserving full closure walks for audit logs) or scope sessions per task |

## Cross-References

- `rules/agent-sandbox-safety.md` — "DON'T: Let untrusted tool outputs reach action execution without provenance checks", "DON'T: Treat tool hiding, specialist prompts or roster delegation as access control", and "DON'T: Trust MCP tool metadata without trace-aware vetting"
- `rules/multi-agent-coordination.md` — "DO: Use standardized message envelopes for cross-agent communication"
- [`provenance-capability-grants`](../provenance-capability-grants/SKILL.md) — Capability grants (ToolFence) for bounding tool invocations by input provenance
- [`tainted-message-clean-room-recovery`](../tainted-message-clean-room-recovery/SKILL.md) — Spawning clean-room recovery contexts when an agent session becomes tainted
- [`mcp-zero-trust-tool-authorization`](../mcp-zero-trust-tool-authorization/SKILL.md) — Server-side zero-trust tool discovery and invocation checks for MCP servers
- [`covert-tool-injection-defense`](../covert-tool-injection-defense/SKILL.md) — Defending against covert indirect prompt injection in tool outputs

> Source: Yocam et al., *Agentic AI Defense: Decode-Time Provenance Binding for MCP* (arXiv:2610.31974), Oct 2026. Praxis source: `src:2610-31974`.
