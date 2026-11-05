---
name: proof-carrying-agent-messages
description: >
  Construct and verify Proof-Carrying Messages (PCM) for multi-agent communication
  across A2A, MCP, and HTTP transports. Replaces blind trust in sender-signed claims
  with offline verification of Merkle-proven execution records from an attesting
  signer, three-valued claim semantics (proven / unproven / failed), T1-vs-T2
  attestation tiers, person-rooted attenuating grant chains, restart-safe bounded
  replay protection, and parser-differential-free strict readings. Derived from
  Ghosh (arXiv:2610.39109).
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Proof-Carrying Agent Messages (PCM)

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

When one LLM agent tells another that *"the tests passed"*, *"I fetched the order from `api.example.com`"*, or *"Alice approved this \$120 refund"*, transport authentication (TLS, signed A2A Agent Cards, RFC 9421 HTTP signatures) only proves **who sent the message**—and a prompt-injected or hallucinating sender happily signs its own lie. Even stacking payment mandates (AP2), transparency receipts (SCITT), and HTTP replay checks (RFC 9421) still accepts **`51.3%` (`365/712`)** of false inter-agent claims.

This skill implements the **Proof-Carrying Messages (PCM)** architecture: separating the untrusted agent process from an **attesting signer** (the Trusted Computing Base), attaching Merkle-proven execution records (`T2` gateway/executor records, human approvals, network observer records) and person-rooted attenuating capability grants to each inter-agent message, and verifying them offline in **`~1 ms`** (`0.80 ms`–`1.22 ms` median) before the receiving agent's LLM ever sees the message.

---

## When to Use This Skill

- **Multi-Agent Delegation & Handoffs (A2A / MCP / HTTP)**: A worker or sub-agent claims to have run tests (`tests_passed`), written an artifact (`file_written`), contacted an external API (`reached_host`), or obtained human approval (`approved_by`).
- **High-Stakes Tool Gateways & Financial/Administrative Actions**: A receiving agent or service must verify that a request is backed by a human-approved capability grant whose caveats were only narrowed across delegation hops.
- **Prompt-Injection Blast-Radius Containment**: Preventing a compromised upstream agent from laundering fabricated facts or escalated authority to downstream agents.

---

## Core Architecture: Parties and Trust Boundaries

Never give an LLM agent process direct access to message- or grant-signing keys. Separate the runtime into:

| Party | Role | What It Writes | Trusted? |
|:------|:-----|:---------------|:---------|
| **Agent (Sender)** | Untrusted LLM process; calls tools, composes message body (`from`, `to`, `intent`, `claims`, `grants`, `payload`) | `T1` self-reported tool results, chosen `tool_use_id` names | **No** (assumed compromised) |
| **Attesting Signer (TCB)** | Isolated service holding log key $sk_L$; decides policy (`allow`/`flag`/`ask`/`deny`), appends events to an append-only RFC 9162 Merkle log, signs messages, grants, and C2SP checkpoints | Envelope `pcm`, `id`, `ts`, `nonce`, `sig`; record `seq`, `ts`, top-level `source` and `tier`; HMAC argument commitments | **Yes** (TCB) |
| **Attesting Executor / Gateway** | Executes tool calls on the agent's behalf over an authenticated channel to the signer | `T2` tool results (`source: "gateway"`, `tier: "T2"` set by signer at top level) | **Yes** (per tool class) |
| **Observer** | Egress proxy or kernel sensor | `effect.observed` records (e.g., `connections > 0`) | **Yes** |
| **Person Approver** | Human mapped in signer's approvals config | Authenticated `approval` answers (`approver_kind: "person"`, `self_approved: false`) | **Yes** |
| **Receiver Verifier** | Deterministic code gate sitting in front of the receiving agent | Nothing (verifies offline against pinned `trust.json` and `schemas`, maintains replay state) | **Verifier** |

---

## Step-by-Step Implementation Procedure

### Step 1: Construct the Closed Envelope and Domain-Separated JCS Signatures

1. **Strict JSON Parsing**: Reject any wire input containing invalid UTF-8, duplicate object keys, lone surrogates, nesting $> 128$, integers outside $\pm(2^{53}-1)$, or numbers that overflow IEEE 754 `double` (e.g., `1e400`) as `bad-input` before any cryptographic check.
2. **Closed Envelope Schema (`application/vnd.pcm+json`)**:
   - Every JSON object in PCM is closed (any unknown field triggers immediate `reject`).
   - All Base64 strings must be **canonical** (standard alphabet, padded, no whitespace, zero unused trailing bits) so each signature or grant has a unique text representation.
   - Signer-populated fields (refused if supplied by the agent): `"pcm": 0`, `"id"`, `"ts"` (fixed 27-char UTC format `YYYY-MM-DDTHH:MM:SS.ffffffZ` with 6 fractional digits), `"nonce"`, and `"sig": {"key": "<log-name>+<4-byte-keyid>", "sig": "<base64>"}`.
3. **Domain Separation Across Signer Signatures**:
   - Use RFC 8785 JSON Canonicalization Scheme ($\mathsf{JCS}$) and inject a synthetic `"t"` tag (which is forbidden on the wire) before signing with Ed25519:
     $$\mathsf{bytes}_t(o) = \mathsf{JCS}\big((o \setminus \{\texttt{"sig"}\}) \cup \{\texttt{"t"}: t\}\big), \quad t \in \{\texttt{"pcm.message.v0"}, \texttt{"pcm.grant.v0"}\}$$
   - Checkpoint notes use C2SP newline-terminated text lines (`0x0A`), which $\mathsf{JCS}$ never emits, making signed byte strings for messages, grants, and checkpoints pairwise disjoint.
4. **Strict Ed25519 Verification**:
   - Enforce 64-byte signature, scalar $S < L$ (group order), canonical public key encoding ($y < 2^{255}-19$), **non-small-order public key point** (rejecting the identity point so $R = \mathcal{O}, S = 0$ cannot forge arbitrary messages), and the cofactorless equation $[S]B = R + [k]A$.
   - Pin at most **one** Ed25519 key per log name in `trust.json` so `sig.key` uniquely identifies the log.

---

### Step 2: Enforce Content-Addressed Schemas and Selective Argument Openings

1. **Content-Addressed Intent Schema**:
   - Reference schemas on the wire as `<name>@sha256:<hex(SHA256(JCS(schema_doc)))>` (e.g., `refund.request@sha256:d8636b6f...`).
   - Perform strict type checking without coercion: `true`, `120.0`, and `"120"` are **not** valid `int` or `money` values.
2. **HMAC Argument Commitments for Privacy**:
   - When the signer logs a `policy.decision`, store an HMAC commitment with a fresh 32-byte salt $s$ (handed only to the calling run's agent):
     $$\texttt{args\_commitment} = \texttt{"hmac-sha256:"} \mathbin{\|} \mathrm{hex}\Big(\mathsf{HMAC}_s\big(\mathrm{ASCII}(\mathsf{H}(\{\texttt{"tool"}: \textit{tool}, \texttt{"args"}: \textit{args}\}))\big)\Big)$$
   - When a claim requires inspecting a decision's arguments, the sender attaches an opening `(salt, args)` to that record; the verifier recomputes the commitment in constant time. Unopened decisions remain hidden.

---

### Step 3: Verify Evidence Items and Enforce the Three-Valued Claim Lattice

1. **Evidence Item Verification ($\mathsf{EvOK}(E, m, \mathcal{T})$)**:
   An evidence item $E = (\kappa, \langle(e_j, h_j, \pi_j, o_j)\rangle_{j=1}^k)$ ($1 \le k \le 16$) verifies for message $m$ iff:
   - Checkpoint $\kappa$ is well-formed, signed by the pinned key for the exact log name in `m.sig.key`, and carries $\ge \texttt{witnesses\_required}$ valid witness cosignatures.
   - **(E1)** $\mathsf{H}(e_j) = h_j$ where $\mathsf{H}(e) = \texttt{"sha256:"} \mathbin{\|} \mathrm{hex}(\mathsf{SHA256}(\mathsf{JCS}(e)))$.
   - **(E2)** Inclusion proof $\pi_j$ (canonical base64, $\le 64$ hashes) proves leaf $\mathsf{SHA256}(\texttt{0x00} \mathbin{\|} h_j)$ at index $e_j.\texttt{seq}$ under RFC 9162 Merkle root $(n, R)$ of $\kappa$ (interior nodes hashed with prefix `0x01`).
   - **(E3) No duplicate sequence numbers**: $e_{j'}.\texttt{seq} \ne e_j.\texttt{seq}$ for all $j' < j$ (prevents listing a decision twice—once opened, once unopened—to create order-dependent verdicts).
   - **(E4) Run & tenant binding**: $e_j.\texttt{tenant} = m.\texttt{from.tenant}$ and $e_j.\texttt{run\_id} = m.\texttt{from.run}$ (prevents replaying another run's or tenant's records).
   - **(E5)** $e_j$ conforms to the profile event schema (`tracekit.event.v2`).
   - **(E6)** Any opening $o_j = (\text{salt}, \text{args})$ is on a `policy.decision` record and verifies against `args_commitment`.

2. **T1 vs. T2 Attestation Tiers (No Self-Attestation)**:
   - Read the attestation tier **only** from top-level record fields set by the signer (`e.source == "gateway" && e.tier == "T2"`), **never** from `e.data` (which the agent can spoof).
   - Any self-reported tool result (`T1`) can yield at most `unproven` or `failed`, **never** `proven`.

3. **Three-Valued Lattice ($\textsf{failed} \prec \textsf{unproven} \prec \textsf{proven}$)**:
    Evaluate each claim $c = (\tau, \textit{args}, E^?)$ in strict priority order:
   1. If $\textit{args}$ fails its schema table or $\mathsf{Malformed}_\tau(\textit{args})$ holds $\implies \textsf{failed}$ (**even if no evidence is attached**, preventing a sender from downgrading a malformed claim like `pytest || true` to `unproven` by stripping evidence).
   2. Else if $c$ carries no evidence (or verifier is Level 1) $\implies \textsf{unproven}$.
   3. Else if $\neg \mathsf{EvOK}(E, m, \mathcal{T}) \implies \textsf{failed}$.
   4. Else evaluate the type-specific checker $\mathsf{Check}_\tau(\textit{args}, E, m) \in \{\textsf{failed}, \textsf{unproven}, \textsf{proven}\}$.

4. **Shared Execution Predicate $\textsc{Ran}(\mathit{match}, k)$ (`Algorithm 1`)**:
   - Initialize $\mathit{cands} \leftarrow \{\textsf{failed}\}$.
   - Iterate over all opened, non-denied `policy.decision` records $d \in \mathcal{E}$ with valid `tool` and `decision_id`:
     - Evaluate $a \leftarrow \mathit{match}(d.\texttt{data.tool}, d.\textit{args}) \in \{\textsc{yes}, \textsc{no}, \textsc{cannot-tell}\}$.
     - If $a = \textsc{no}$, continue; if $a = \textsc{cannot-tell}$, add $\textsf{unproven}$ to $\mathit{cands}$ and continue.
     - Place $d.\texttt{data.tool}$ using **only** the frozen 54-tool protocol table (`Place(tool)`), never by argument shape. If $k \ne \bot$ and $\mathsf{Place}(d.\texttt{data.tool}) \ne k$, add $\textsf{unproven}$ to $\mathit{cands}$ and continue.
     - Match `tool.result` records $r \in \mathcal{E}$ with $(r.\texttt{decision\_id}, r.\texttt{tool\_use\_id}) = (d.\texttt{decision\_id}, d.\texttt{tool\_use\_id})$:
       - If $r.\texttt{data.ok} \ne \texttt{true}$, add $\textsf{failed}$ to $\mathit{cands}$.
       - Else if $r.\texttt{source} = \texttt{"gateway"} \wedge r.\texttt{tier} = \texttt{"T2"}$, return $\textsf{proven}$ immediately.
       - Else (`T1` self-report), add $\textsf{unproven}$ to $\mathit{cands}$.
   - Return $\bigsqcup \mathit{cands}$ (maximum in $\textsf{failed} \prec \textsf{unproven} \prec \textsf{proven}$).

---

### Step 4: Implement the Four Exact Claim Checkers & Strict Readings

To eliminate parser differentials across languages and operating systems, apply **strict readings**: wherever common parsers disagree on a field, refuse to guess—map sender-chosen malformed claims to `failed` and unparseable runtime-recorded fields (like fetched URLs or relative tool paths) to `unproven` with an actionable hint.

1. **`tests_passed {suite}`**:
   - **Malformed Check (`failed` with or without evidence)**:
     - *Plain-word grammar*: Reject if `suite` contains any shell operator or metacharacter in `; & | ( ) < > $ ` \ # { } * ? [ ]`, any control character other than tab, or unbalanced quotes (closes `shlex` vs `sh` differentials such as `pytest $'\'';true #'` or `pytest -q x.py#|| true`).
     - *Bare runner prefix*: Split at unquoted whitespace; the words must start with one of the 42 fixed runner sequences (`pytest`, `python -m pytest`, `go test`, `cargo test`, `npm test`, etc.) as a bare name (reject `./pytest`, `/tmp/x/pytest`, `uv run pytest`, `CI=1 pytest`).
     - *Runs tests*: Reject if any word is `-h`, `-V`, or a $\ge 3$-char prefix of `--help`, `--version`, or `--collect-only`.
   - **Evidence Match**: Run $\textsc{Ran}(\mathit{match}, \texttt{shell})$ requiring exact string equality between the command argument and `suite`. Receiver must also compare `suite` against its accepted test suites (to prevent vacuous flags like `-k nothing`) and check evidence age/tree binding.

2. **`approved_by {person, call, covers?}`**:
   - Never prove `approved_by` from an `approval` record alone (since the agent chooses `tool_use_id` names and can name a `read_file` call `"refund-81-approved"`).
   - **Require the 3-record linked triple in one evidence item**:
     1. `approval` record with `decision == "approve"`, `tool_use_id == call`, signer-configured `person == claim.person` (never raw tenant user ID), `approver_kind` absent or `"person"` (never `"agent"`), and `self_approved != true`.
     2. `approval.request` record with matching `approval_id`.
     3. `policy.decision` record named by that request's `decision_id`, with `tool_use_id == call` and non-empty `tool`.
   - **Order-Independent Disagreement Check**: Collect all qualifying `(tool, opened_args_or_null)` pairs across matching records; if requests name multiple decisions or two pairs differ under $\mathsf{JCS}$ (e.g., `{"amount": true}` vs `{"amount": 1}`), return `failed`.
   - **Mandatory `covers: true` Check**: When a schema requires `approved_by`, it is satisfied **only** when `covers == true` and either:
     - *Grant Path*: `decision.tool == "pcm.grant"` and this approval's `approval_id`, `run`, and `tenant` issued the message's root grant $g_0$; or
     - *Direct Path*: The intent schema names `decision.tool`, the decision is opened, and its opened `args` equal `m.intent.args` under $\mathsf{JCS}$ (prevents citing a \$5 approval to authorize a \$50 request).

3. **`reached_host {host}`**:
   - Proven only by an `effect.observed` net record with `connections > 0` (a `connect` syscall or 0-connection minute is an attempt $\to$ `unproven`), or $\textsc{Ran}(\mathit{match}, \texttt{http})$ where the canonicalized URL host equals canonicalized `host`.
   - **6-Step Canonical Host Parser (Maps Disagreements to `unproven`)**:
     1. Printable ASCII only (rejects IDNA 2003 vs UTS 46 divergences like `faß.example` or `U+1806`).
     2. Must have a scheme or leading `//` (rejects `/api.example.com/x`).
     3. Apply a single explicit IPv6 bracket rule over the authority before calling any URL library (closes CPython `urlsplit` cross-version bracket differentials on `http://[::1]@api.example.com/`).
     4. Reject ambiguous `@` / `\` authority readings (`http://a.example\@b.example/`).
     5. Reject `%`-escapes in host; accept IPv4 **only** as four decimal octets `0–255` **without leading zeros** (closes the `0127.0.0.1` octal `87.0.0.1` vs decimal `127.0.0.1` platform differential).
     6. Labels must match `[a-z0-9_-]{1,63}` with no empty labels (`a..example`).

4. **`file_written {path, digest}`**:
   - Reject relative paths (`work/a.txt`, `C:a.txt`) or paths containing `..` segments in the claim as `failed` (with or without evidence).
   - Select path separator rules from the claim (`C:\...` or `C:/...` uses Windows drive rules; `/...` uses POSIX rules where `\` is a literal filename char, preventing `/work\report.txt` from proving `/work/report.txt`).
   - Run $\textsc{Ran}(\mathit{match}, \bot)$ restricted to tool name `Write` whose full content hashes to `digest`. If the recorded tool call used a relative path that is a suffix of `path`, return `unproven`.

---

### Step 5: Verify Person-Rooted, Attenuating Grant Chains

1. **Root Grant ($g_0$) Rules**:
   - Must have `parent: null`, `issuer.kind == "person"` with a configured person name, and `issuer != subject` (no agent-minted roots, no self-approval).
   - Signer caps root lifetime at $\le 24\text{ hours}$ and mints at most one root grant per consumed `pcm.grant` approval.
2. **Delegation Chain ($g_0, g_1, \dots, g_n$) Rules (`Table 4`)**:
   - Every grant $g_i$ must be signed by the **exact same log key** `m.sig.key` under tag `pcm.grant.v0` (prevents cross-log grant riding when agent IDs collide).
   - For each link $i \ge 1$: $g_i.\texttt{parent} == \mathsf{H}(g_{i-1})$, $g_{i-1}.\texttt{delegable} == \texttt{true}$, $g_i.\texttt{issuer} == \text{agent } g_{i-1}.\texttt{subject}$, $g_i.\texttt{expires\_at} \le g_{i-1}.\texttt{expires\_at}$, same `intent` and `tenant`, and $g_n.\texttt{subject} == m.\texttt{from.agent}$.
   - Check that `m.ts <= g_i.expires_at` and that `m.intent.args` satisfies every caveat of **every** grant in the chain (defense in depth).
3. **Sound Caveat Narrowing Implication Table (`Table 3`)**:
   - Normalize caveats on schema-typed fields (`int`/`money`, `time`, `string`/`id`/`enum`, `bool`) to $\{= v, \in S, \le b, \ge b\}$ (with `< b` $\mapsto$ `<= b - 1` and `> b` $\mapsto$ `>= b + 1` on integers).
   - A child grant narrows its parent iff **every** parent caveat $p$ is implied by at least one child caveat $c$ on the same field with the **exact same JSON type**:
     - $(= v) \implies (= x)$ iff $v = x$; $(= v) \implies (\in S)$ iff $v \in S$; $(= v) \implies (\le b)$ iff $v \le b$; $(= v) \implies (\ge b)$ iff $v \ge b$.
     - $(\in T) \implies (= x)$ iff $T = \{x\}$; $(\in T) \implies (\in S)$ iff $T \subseteq S$.
     - $(\le b') \implies (\le b)$ iff $b' \le b$; $(\ge b') \implies (\ge b)$ iff $b' \ge b$.
     - All other pairs (including bounds $\{\le 81, \ge 81\}$ vs equality $= 81$, or missing caveats) evaluate to **never** (`failed`).

---

### Step 6: Enforce Bounded-Memory, Restart-Safe Replay Protection (`Algorithm 3`)

Maintain a single replay state per receiver identity (`me`) with time window $W$ (default `300 s`), per-sender capacity $P$ (default `4096`), and creation timestamp `started`:

1. **Key the Sender by `(m.sig.key, m.from.agent)`**: Never key by `from.agent` alone, so `uid:990101` on log $X$ cannot spend nonces or raise the floor for `uid:990101` on log $Y$.
2. **Recipient & Schema Pre-Check**:
   - If `m.to.agent != me`, fail replay without modifying state (another receiver's message must not spend nonces here).
   - Only record a nonce when `StrictArgs(schema, m.intent.args)` has zero errors.
3. **Four Replay Rejection Conditions (`t = m.ts`, $\sigma = (\texttt{sig.key}, \texttt{from.agent})$)**:
   - Reject if $t$ is not a valid calendar UTC time.
   - **Window & Restart Check**: Reject if $|\textit{now} - t| > W$ **or** $t < \textit{started}$ (refusing any message signed before the receiver process started guarantees at-most-once acceptance across restarts without disk persistence; honest senders simply re-request signing).
   - **Floor Check**: Reject if $t \le \textit{floor}[\sigma]$.
   - **Duplicate Nonce Check**: Reject if $m.\texttt{nonce} \in \textit{seen}[\sigma]$.
4. **Arrival-Order Eviction**:
   - Append `(m.nonce, t)` to FIFO list `seen[sigma]`, pop head entries with $t' < \textit{now} - W$, and while $|\textit{seen}[\sigma]| > P$, pop the oldest-arrived entry `(_, t')` and update $\textit{floor}[\sigma] \leftarrow \max(\textit{floor}[\sigma], t')$.

---

### Step 7: Compute the Final Verdict and Gate the Receiving Agent

1. **Verdict Computation (`Definition 7`)**:
   - Let $\mathsf{Bad}(m)$ hold iff signature fails, replay fails, schema check has errors, `grants.result == "failed"`, or any claim has $\mathsf{Res}(c) == \textsf{failed}$.
   - Let $\mathsf{Met}(q)$ hold for each schema-required claim type $q \in Q$ iff some claim of type $q$ is $\textsf{proven}$ (with `covers == true` when $q = \texttt{approved\_by}$).
   - Return:
     - **`reject`**: if $\mathsf{Bad}(m)$ holds, or if `strict == true` and $\exists q \in Q.\, \neg\mathsf{Met}(q)$.
     - **`accept-unproven`**: else if $\exists c.\, \mathsf{Res}(c) == \textsf{unproven}$ or $\exists q \in Q.\, \neg\mathsf{Met}(q)$.
     - **`accept`**: otherwise (all claims `proven` and all required claim types met).
2. **Freshness Checks at the Receiver (`Section 13.1`)**:
   - Because PCM 0.1 claims are existential (*"a call ran and succeeded"*), apply three receiver-side freshness checks to prevent stale-evidence replay (`L10`):
     1. *Age bound*: Refuse evidence whose oldest record timestamp is older than a per-intent threshold relative to `m.ts`.
     2. *After-last-change bound*: Refuse evidence older than the latest commit/state change on the target resource.
     3. *File digest check*: For `file_written`, verify `sha256` over the actual bytes held by the receiver.
3. **LLM Gate Integration**: Drop `reject` messages before they reach the receiving LLM; pass `accept` claims as verified provenance facts and tag `accept-unproven` claims explicitly as unverified sender testimony (`"the sender says..."`).
