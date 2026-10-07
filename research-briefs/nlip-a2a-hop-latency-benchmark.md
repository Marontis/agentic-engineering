# The Cost of a Hop: Benchmarking NLIP and A2A

> **Paper**: [The Cost of a Hop: Benchmarking NLIP and A2A](https://arxiv.org/abs/2610.04053)
> **Praxis source**: src:2610-04053

## Why Not a Skill?

This is a latency benchmark of two agent-to-agent protocols and three client
implementations. It yields a decision criterion (when protocol overhead
matters) rather than a procedure, so the transferable part is captured as a
rule entry in `rules/multi-agent-coordination.md`.

---

## Core Concept

The paper decomposes per-hop latency of NLIP (Ecma TC56, REST/JSON, stateless,
no discovery phase) and A2A (JSON-RPC 2.0, Agent Card discovery, session state)
into message creation, connection, and send phases. It tests NLIP
(nlip-server/nlip_sdk 0.1.2), A2A-SDK 0.3.23, A2A-SDK with connection caching,
and Python-A2A 0.5.10 on a two-hop text pipeline (speech-to-text output →
subreddit identification via LLM → Reddit search), on three Apple silicon
machines (M2 Pro, M1, M3 Pro), with 10, 19 and 200-query sets run five times
each. All runs were sequential; nothing here characterizes concurrent load.

### Key Finding

- **Primary Result**: On the lightweight stage (work of a few ms), NLIP was
  8.4–9.6× faster than A2A-SDK on two machines and 4.2× on the third, and
  4.1–4.3× faster than Python-A2A. The gap is almost entirely connection
  setup: on Machine B, A2A-SDK spent 62.71 ms per connection versus NLIP's
  2.56 ms (24.5×); on Machine C, 25.87 ms versus 2.64 ms (9.8×). Message
  creation was 0.06–0.15 ms for every implementation.
- **Granularity decides whether it matters**: end-to-end workflows of
  700–1000 ms, dominated by LLM inference, showed near-parity between
  protocols.
- **Implementation matters as much as protocol**: Python-A2A was 2.0–2.2×
  faster than A2A-SDK on the same spec (connection 7.36 ms vs 62.71 ms).
  Enabling connection caching in A2A-SDK cut connection cost below 1 ms, but
  its send phase rose (5.21 → 18.07 ms on Machine B; 4.24 → 7.82 ms on
  Machine C), leaving NLIP 2.75× ahead on Machine B and 1.27× on Machine C;
  at 200 queries on Machine C, cached A2A-SDK reached parity. The authors
  have no causal account of the send-phase increase.
- **Statistics**: bootstrap 95% CIs on the lightweight stage do not overlap
  (NLIP [7.31, 8.58] ms, A2A-SDK [61.83, 70.72] ms, Python-A2A
  [29.94, 34.55] ms).

## Relevance to Praxis

- **Protocol choice is a granularity question**: for orchestrators that fan
  out many small tool or agent hops, per-hop connection cost dominates; for
  LLM-bound hops it is noise. See the rule "Size protocol overhead against
  per-hop work" in `rules/multi-agent-coordination.md`.
- **Benchmark implementations, not specs**: "A2A is slower" conflates protocol
  and client; a 2× spread within one protocol means evaluations must name the
  client library and version.
- **Complements** the `nlip-agent-message-envelope` skill, which covers
  envelope structure and security but not performance. The single-hop 60 ms
  gap compounding over multi-hop chains is the authors' projection, not a
  measured result.
