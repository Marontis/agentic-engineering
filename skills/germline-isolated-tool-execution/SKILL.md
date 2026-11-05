---
name: germline-isolated-tool-execution
description: >-
  Enforce invocation purity for untrusted or third-party agent tools via pre-fork
  data-free germline verification, declared-destination view splitting, horizon-keyed
  state slots, and twin-execution tripwire witnesses. Prevents cross-call carry-over
  and within-call item smuggling even on allowed egress channels. Derived from
  Germline (arXiv:2611.06585).
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Germline-Isolated Tool Execution

> **Source**: [arXiv:2611.06585](https://arxiv.org/abs/2611.06585) — *Signed, Sealed, Leaked: Trust Beyond Signature for MCP Toolchains* (`src:2611-06585v1`)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

Use this skill when building or hardening a tool-execution runtime (such as a Model Context Protocol host, function-calling gateway, or multi-tenant tool broker) where:

1. **Signed or pinned tool releases can still act as Trojans**: Package signatures, registry pinning, and hash checks prove provenance and integrity (`Sig+Pin`), and OS/eBPF allowlists (`MCPGuard-Dynamic`, `Confined+IFC`) restrict *which* hosts or files a tool can reach, but neither stops a tool from smuggling sensitive payloads inside an *allowed* outbound request or legitimate return value.
2. **Tools process records with mixed flow labels or run across multiple turns**: A persistent tool server can stash high-sensitivity data from an earlier call in process memory, global variables, warm caches, or temporary files (`pool`), or mix protected items with public items passed in the same batch call (`smuggle`) and emit the combined result on a public channel.
3. **Fresh container/process cold starts per call are too slow, or still leak within-call mixtures**: Starting a fresh Python/Node interpreter on every call costs hundreds of milliseconds and still exposes all items of a multi-record call to a single process (`Fresh+IFC` leaks `9.8%` of scripted attacks and `Germline-NoSplit` leaks `5.9%`).

Do **not** rely on lazy on-demand view splitting triggered only when a tool attempts its first external request: existence-bit analysis proves that if a fallback branch can emit a request when a secret bit is zero, lazy splitting leaks `64/64` secret bits (`0.942` bits per call) while firing `0` tripwire alerts.

---

## Core Concepts: Invocation Purity

Even when a tool's outbound destinations and return labels satisfy Information Flow Control (IFC), the runtime must enforce **invocation purity**: the outputs of a tool invocation routed to a given destination set may depend *only* on the inputs authorized for that destination set and on state carried over from prior invocations at the same or lower flow horizon.

Violations of invocation purity take two structural forms:

- **Cross-call carry-over (`pool`)**: A tool call touches an internal secret on turn $t_1$ and returns a benign response, then embeds that secret inside an allowed outbound API request or public summary on turn $t_2$.
- **Within-call mixing (`smuggle`)**: A single tool call receives multiple items with different allowed destination sets (for example, two public documents and one restricted note) and folds restricted content into an output or network request declared only for the public items.

---

## Step-by-Step Procedure

### Phase 1: Initialize and Verify the Data-Free Germline

Before the agent session begins or any user/tool data enters memory, initialize each tool server into a quiescent **germline** process and freeze it prior to accepting arguments:

1. **Data-free initialization**: Launch the tool server and import its dependencies with zero user inputs, zero environment secrets, and no writable shared paths.
2. **Enforce the three pre-fork germline invariants (`G1–G3`)**:
   - **`G1` (Single thread)**: Inspect `/proc/<pid>/status` (or OS equivalent) and verify `Threads == 1`. Reject any release that spawns background worker or timer threads during module import (`init_thread` attack).
   - **`G2` (Sanitized file descriptors)**: Inspect `/proc/<pid>/fd` and verify that only the runtime control socket, `/dev/null` standard streams, and read-only allowlisted code/library files remain open.
   - **`G3` (No shared writable mappings)**: Inspect `/proc/<pid>/maps` and verify no `MAP_SHARED` writable memory regions or writable filesystem mounts exist (`hijack` attack).
3. **Pre-fork a copy pool**: Fork worker copies from the verified germline before calls arrive. Copy-on-write fork amortizes interpreter startup (`35 MB` germline footprint, `~12 MB` resident per additional germline, `20 MB` PSS and `0.98 MB` private memory per live copy), reducing single-copy median overhead to `9.9 ms` (`28.4x` faster than a `282.1 ms` fresh process start, with a pre-forked pool saving an additional `7–9 ms`).

### Phase 2: Declared-Destination View Splitting (`Plan`)

When the agent invokes a tool with a batch or structured set of input items $I = \{x_1, \dots, x_m\}$, partition execution *before* any user code runs:

1. **Compute each item's flow horizon**: For every input item $x_i$, read its information-flow label $\ell(x_i) = (C_i, D_i)$, where $C_i$ is its confidentiality/provenance tag set and $D_i$ is the set of destinations (external hosts, downstream tools, or agent return channels) permitted to receive data derived from $x_i$.
2. **Group items by declared destination set**: Partition the call inputs into disjoint destination groups $G_\kappa = \{x_i \in I \mid D(x_i) = \kappa\}$, plus a structural skeleton containing non-sensitive schema/configuration parameters.
3. **Run one isolated germline copy per destination group**:
   - Dispatch each group $G_\kappa$ to its own forked germline copy running in an isolated network/IPC/filesystem namespace with read-only root, zero shared `/tmp`, and egress restricted strictly to destination set $\kappa$.
   - Execute copies **sequentially** (or with deterministic completion barriers) rather than concurrently on shared cores if inter-copy timing covert channels are a concern: sequential execution reduces cross-copy CPU contention timing bandwidth from `37.9–47.7 bit/s` to at most `0.61 bit/s`.
   - Reassemble the per-group results in the trusted host runtime and attach the corresponding flow label $\kappa$ to each returned field.

### Phase 3: Horizon-Keyed Explicit State Slots ($\sigma[\kappa]$)

For tools that legitimately require cross-call state (such as pagination cursors, incremental reducers, or session caches):

1. **Forbid implicit process state**: Because every germline copy terminates immediately after handling its single destination group, all in-memory mutations are discarded at call completion.
2. **Key explicit state slots by flow horizon**: Provide an explicit host-managed state store $\sigma[\kappa]$ indexed by the cumulative flow horizon $\kappa$ of all inputs that contributed to that state.
3. **Prevent horizon downgrade (`capsule` defense)**: A copy executing at destination horizon $\kappa$ may read and update $\sigma[\kappa]$ (or read state from a strictly less restricted horizon $\kappa' \sqsupseteq \kappa$ only if upgraded to $\kappa$), but can never write state into a broader destination slot. Verify that serialized state updates conform to the declared schema before committing them to $\sigma[\kappa]$.

### Phase 4: Twin-Execution Tripwire and Offline Witness Generation

To detect releases that attempt to smuggle cross-group data or behave differently when given the full batch versus destination-split views:

1. **Freeze ambient nondeterminism (`A4`)**: Inside every germline copy, intercept and deterministically seed wall-clock time, monotonic clocks, PRNGs (`random`, `os.urandom`, `numpy.random`), and UUID generators per call ID. Without deterministic clock/nonce freezing, benign tools that log timestamps or request IDs produce `20/20` false-positive divergence witnesses; with twin execution (`A4`), false witnesses drop to `0/20`.
2. **Compare split execution against a shadow full-input twin (or probe replay)**:
   - When a tripwire check is scheduled (or when a copy attempts an undeclared destination request), run a shadow twin copy with the unsplit input batch under all outbound network/IPC sinks disconnected (sink-stubbed) and identical deterministic seeds.
   - Compare each group copy's emitted requests and return values against the corresponding slice of the twin execution.
3. **Emit a self-contained offline witness on divergence**:
   - If the output or outbound request for group $\kappa$ changes when an out-of-group item $x^* \notin G_\kappa$ is present, execute a delta-debugging probe replay that pairs the group inputs $G_\kappa$ with and without $x^*$ under identical frozen seeds.
   - Package the germline binary digest, call inputs, frozen seed state, and diverging outputs into a compact witness bundle (`~7,450` bytes, verifiable offline in `0.35 s`) proving that the release violated invocation purity on item $x^*$.

### Phase 5: BGP-Style Flap Dampening for Release Quarantine

Because real-world tools may occasionally exhibit unfreezeable nondeterminism, combine instant quarantine on verified witnesses with exponential decay dampening on unverified anomalies:

1. **Maintain a per-release penalty score $P$** with exponential half-life $h = 50$ calls: after each clean call, update $P \leftarrow P \cdot 2^{-1/h}$.
2. **Increment penalty on anomalies**:
   - On an unverified tripwire divergence or blocked egress attempt, add penalty weight $w = 250$.
   - On a deterministically verified item witness (where replay under identical frozen seeds proves dependence on an out-of-group item $x^*$), add $+2000$ to trigger **immediate suppression**.
3. **Enforce suppress and reuse thresholds**:
   - When $P \ge S = 2000$, quarantine the tool release and roll back to the last pinned flow-compliant release (`1.0.0`). An always-diverging release is suppressed after `9` calls (critical divergence rate $p^* = 11.0\%$).
   - Keep the release suppressed until decay (or administrative review) brings $P < R = 750$. At a `1%` random unverified divergence rate, this parameterization yields `0%` false suppression over `100,000` calls (`2.4%` over `10,000` calls at a `3%` rate).

---

## Quantitative Summary

| Evaluation Dimension | Baseline / Comparison | Germline Result |
|:---|:---|:---|
| **Matched comparison vs. Meta `MCPGuard-Dynamic`** (`7` configs incl. 4 eBPF / BPF-LSM programs, 5 attack variants $\times$ 3 trials) | Blocks `direct` (`0/3`) with eBPF, but leaks `3/3 (2)` on `pool` and `3/3 (3)` on `smuggle` across all 7 configs | **`0/3` disclosures** across all 5 variants (`6/6` benign calls completed) |
| **Scripted security matrix** (`5` MCP servers, `59` signed releases, `15` attack variants across V1–V4, `153` attack runs + `99` benign steps) | `Sig+Pin`: `74.5%` (`114/153`; `70.6%` tool-attributable)<br>`Sig+IFC`: `70.6%`<br>`Confined+IFC`: `33.3%`<br>`Fresh+IFC`: `9.8%`<br>`Germline-NoSplit`: `5.9%` | **`0.0%` (`0/153`) disclosures**, `99/99` benign steps completed |
| **LLM-generated Trojan corpus** (`Qwen3.5-27B`, `91` validated packages across 5 families, 3 trials) | Egress allowlist blocks `71/91` (`78%`, attacker host) and **`0/20`** (`0%`, policy-allowed host) | **`0/91` disclosures** across all 5 families |
| **LLM-driven agent episodes** (`Qwen3-32B-AWQ` & `Qwen3.5-27B`, `504` episodes across 7 tasks $\times$ 6 releases) | `Sig+Pin` / `Confined+IFC` disclosures: `pool` (`2`/`2`), `dormant` (`28`/`0`), `launder_text` (`1`/`1`), `direct` (`8`/`0`), `smuggle` (`6`/`3`) | **`0` disclosures** on all releases, `7/7` tasks completed, `2.04 s` median episode time (vs. `1.81–1.97 s`) |
| **Declared-destination vs. lazy splitting** (`64`-bit secret existence test, 23 ones over 64 calls) | Lazy splitting: leaks **`64/64` bits** (`0.942` bits/call) with `0` triggers | Declared-destination splitting: **`0.000` bits leaked**, fires tripwire on `23/23` added and `41/41` omitted requests |
| **Unmodified official MCP servers** (`time`, `fetch`, `sqlite`, `git`; `780` total calls) | Native latency: `1.2–18.4 ms` | **100% output compatibility**, median latency `39.0–110.3 ms` |

---

## Anti-Patterns to Avoid

1. **Treating eBPF network/file allowlists + process-level IFC as sufficient for multi-item or multi-turn tools**: An eBPF policy (`MCPGuard-Dynamic`) or container firewall only checks whether the destination host/path is on the allowlist; it cannot tell whether the payload sent to an allowed host was computed from a restricted note (`smuggle`) or stashed from a previous turn (`pool`).
2. **Spawning fresh processes per call without view splitting (`Fresh+IFC` / `Germline-NoSplit`)**: Resetting process memory between turns stops cross-call `pool` attacks unless state is carried over, but still leaves `5.9%–9.8%` of attacks successful because a single call holding multiple records can mix them internally (`smuggle`) or abuse coarse state restoration.
3. **Splitting execution lazily only when an external request is observed**: If a tool inspects a secret item first and branches on whether to issue an allowed request, lazy splitting leaks the secret bit via the presence or absence of the request (`0.942` bits/call) without ever triggering a violation. Always split by declared destination set *before* invoking tool code.
4. **Running tripwire comparisons without freezing clocks and PRNGs**: Comparing split and unsplit executions without deterministic interception of time and randomness (`A4`) floods the operator with `100%` (`20/20`) false witnesses on any tool that embeds timestamps or nonces.
