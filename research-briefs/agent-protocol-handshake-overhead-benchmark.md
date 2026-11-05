# The Cost of Saying Hello: An Empirical Study of Handshake Overhead in AI Agent Communication Protocols

> **Paper**: [The Cost of Saying Hello: An Empirical Study of Handshake Overhead in AI Agent Communication Protocols](https://arxiv.org/abs/2610.30151)
> **Praxis source**: src:2610-30151
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

This paper is a phase-decomposed empirical benchmark of connection
establishment across MCP, A2A, and ACP. Its actionable takeaways—sizing
round-trip count, enabling spec-sanctioned metadata caching and era pinning on
warm reconnects, validating protocol versions at discovery time, and bounding
per-capability metadata token slopes—directly strengthen existing rules in
`rules/multi-agent-coordination.md` and `rules/skill-system-design.md`.

---

## Core Concept

Before an initiating agent can send its first substantive task message to a
counterpart, it pays a **handshake** tax decomposed into four phases:
(a) *discovery*, (b) *capability exchange*, (c) *auth/session*, and
(d) *readiness*, ending at the operationally defined **task-ready** state
(confirming from protocol metadata that the counterpart offers a canonical
`echo` capability).

Using official Python SDKs (`mcp` 2.0.0, `a2a-sdk` 1.1.2, `acp-sdk` 1.0.3 over
`httpx` 0.28.1) instrumented via a local TCP relay ($N = 50$ runs per cell
after 5 warmup runs, reporting medians and 95th percentiles), the benchmark
compares four protocol variants across **localhost** and an emulated **50 ms
RTT** link (plus an RTT sweep over 0, 25, 50, and 100 ms, $N = 20$):
- **MCP (legacy, spec 2024-11 to 2025-11-25)**: `POST initialize` $\to$ `POST initialized`
  notification $\to$ `POST tools/list` (3 application-layer round trips).
- **MCP (modern, spec 2026-07-28 + SEP-2549 cache hints)**: `POST server/discover`
  $\to$ `POST tools/list` (2 round trips cold; 1 round trip warm under `auto`;
  0 round trips warm under `pinned` protocol era).
- **A2A (v1.0.0, JSON-RPC binding)**: `GET /.well-known/agent-card.json` (1
  round trip cold; 0 warm with cached Agent Card).
- **ACP (v1.0, frozen REST design)**: `GET /agents` (1 round trip cold; 0 warm
  with cached manifest).

### Key Findings

- **Round-trip count dominates handshake latency**:
  - *Cold start (S1)*: On localhost, medians are small (MCP legacy **6.1 ms**,
    MCP modern **4.4 ms**, A2A **2.8 ms**, ACP **2.8 ms**). At **50 ms RTT**,
    MCP legacy takes **230 ms** (p95 236 ms; 1,147 B up / 1,522 B down), MCP
    modern takes **122 ms** (p95 125 ms; 1,070 B up / 1,205 B down, a **47%
    reduction**), A2A takes **61.0 ms** (p95 61.9 ms; 170 B up / 569 B down),
    and ACP takes **62.1 ms** (p95 63.1 ms; 149 B up / 633 B down)—making
    legacy MCP **3.8× slower** than A2A.
  - *RTT scaling slopes & TCP connection churn*: Latency rises linearly with
    RTT at **1.1 ms/ms** for A2A and ACP, **2.1 ms/ms** for modern MCP, and
    **4.2 ms/ms** for legacy MCP (whose SSE-framed `initialize` and
    `tools/list` responses cross in two delayed chunks each). Worse, the legacy
    MCP SDK closes each SSE response stream early upon receiving the JSON-RPC
    reply, discarding the keep-alive connection and opening **3 fresh TCP
    connections** per handshake (vs. 1 connection for modern MCP, A2A, and ACP),
    which would add ~100 ms+ of TCP/TLS setup on a real 50 ms network.
- **Warm reconnects (S2) separate cacheable protocols from session-first
  legacy MCP**: Legacy MCP has no spec caching and repeats all 3 RTTs
  (**230 ms** at 50 ms RTT, even amortized over $k = 100$ interactions). Modern
  MCP (`auto`) re-probes `server/discover` and serves `tools/list` from the
  SEP-2549 cache in **1 RTT (63.5 ms)**; with era pinning (`pinned`), it
  reaches task-ready in **0 RTTs (6.6 ms)**, matching cached A2A (**0 RTTs,
  2.0 ms**) and ACP (**0 RTTs, 6.6 ms**). Over $k = 100$ interactions at 50 ms
  RTT, per-interaction handshake cost amortizes to 2.6 ms (A2A), 7.1 ms (ACP),
  and 7.8 ms (pinned MCP) vs. 230 ms (legacy MCP).
- **Capability mismatch (S3) charges the full handshake price**: Discovering
  that a counterpart lacks a required `translate` capability takes the full
  cold handshake: **62.2 ms** (A2A, 1 RTT), **57.7 ms** (ACP, 1 RTT),
  **117 ms** (modern MCP, 2 RTTs), and **231 ms** (legacy MCP, 3 RTTs).
  Shopping across $M$ candidate counterparts scales as $1 \times M$ GETs for
  document-centric protocols vs. $3 \times M$ session setups for legacy MCP.
- **Degraded conditions (S4) expose silent version-mismatch deferral in A2A**:
  - *Slow counterpart (2 s/response delay, S4a)*: Multiplies by round trips—
    **6,026 ms** (legacy MCP), **4,019 ms** (modern MCP), **2,011 ms** (A2A and
    ACP).
  - *Truncated metadata (50% JSON truncation, S4b)*: All fail fast without
    retry storms (2.9–4.4 ms), though A2A (`AgentCardResolutionError`) and MCP
    (`MCPError`) raise contextualized errors while ACP raises a bare
    `JSONDecodeError`.
  - *Version mismatch (S4c)*: Both MCP eras reject a fictitious version
    (`2099-01-01`) during the handshake in **3.7–4.2 ms** (`RuntimeError`, with
    modern MCP returning structured error `-32022` and supported versions).
    A2A marks `protocolVersion` in the Agent Card as descriptive and defers
    enforcement to per-request `A2A-Version` headers—so the A2A client
    accepted a card claiming version `99.0.0` in **3.0 ms** without warning,
    deferring any real incompatibility to fail at task execution time. ACP
    manifests lack a protocol-version field altogether.
- **Metadata token slope (24–107 tokens/capability) is untouched by round-trip
  reduction**: Using `o200k_base` (a conservative lower bound), a 1-capability
  counterpart costs only 112–242 tokens (A2A 113, ACP 112, legacy MCP 181,
  modern MCP 242). However, each additional capability adds **24 tokens** in
  A2A, **78 tokens** in MCP (full input/output JSON schemas), and **107 tokens**
  in ACP (16-field metadata block):

| Protocol | $n = 1$ | $n = 10$ | $n = 50$ | $n = 200$ | Marginal / Capability |
|:---------|:--------|:---------|:---------|:----------|:----------------------|
| A2A | 115 | 331 | 1,291 | 4,891 | 24 tokens |
| MCP | 96 | 798 | 3,918 | 15,618 | 78 tokens |
| ACP | 112 | 1,075 | 5,355 | 21,405 | 107 tokens |

At $n = 200$ capabilities, a single cold handshake injects **15,618 tokens**
(MCP) or **21,405 tokens** (ACP)—consuming **11% of a 200k-token context
window** before the agent reads its own task.

## Relevance to Praxis

- **Use modern MCP (`server/discover` + SEP-2549 caching + era pinning) or
  cached Agent Cards**: Eliminates the 3-RTT (230 ms at 50 ms RTT) and 3-TCP-connection
  tax of legacy MCP on repeated interactions.
- **Validate protocol versions during discovery, not at task dispatch**: If
  using A2A, add an explicit client-side check on the Agent Card's
  `protocolVersion` during discovery so incompatible counterparts are rejected
  before task planning.
- **Bound capability inventory size or pair with progressive disclosure**:
  Because `tools/list` scales at 78 tokens/tool (15,618 tokens at 200 tools),
  combine SEP-2549 response caching with progressive tool disclosure
  ([`mcp-vs-cli-tool-integration-analysis`](mcp-vs-cli-tool-integration-analysis.md)).
- **Related artifacts**:
  - `rules/multi-agent-coordination.md`: "DO: Size protocol overhead against
    per-hop work before choosing an agent protocol or client".
  - `rules/skill-system-design.md`: "DO: Charge a token penalty for every
    injected skill document".
  - [`nlip-agent-message-envelope`](../skills/nlip-agent-message-envelope/SKILL.md).
