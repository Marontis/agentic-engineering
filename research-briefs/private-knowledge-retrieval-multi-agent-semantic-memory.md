# Private Knowledge Retrieval and Private Inference for Secure Multi-Agent Systems

> **Source**: [arXiv:2611.13696](https://arxiv.org/abs/2611.13696) — Vicenç Torra, Maria Bras-Amorós (2026)
> **Praxis Source ID**: `src:2611-13696v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Summary

Torra and Bras-Amorós examine how multi-agent systems (MAS) that share externalized semantic memory can defend against memory-poisoning attacks such as `AgentPoison` (Chen et al., NeurIPS 2024) and malicious knowledge-base (KB) servers. `AgentPoison` optimizes backdoor triggers $x_t$ under three strong assumptions: the attacker can inspect clean memory $\mathcal{D}_{\mathrm{clean}}$, append adversarial entries $\mathcal{A}(x_t)$ into $\mathcal{D}_{\mathrm{poison}} = \mathcal{D}_{\mathrm{clean}} \cup \mathcal{A}(x_t)$, and observe retrieved records $\mathcal{E}(q \oplus x_t, \mathcal{D})$ across victim queries.

To break those assumptions simultaneously, the authors propose an architectural separation implemented in a Python/Prolog prototype (`tipp++`):

1. **Signed Static Semantic Memory with Provenance**: Knowledge is stored externally as Horn clauses grouped by `(predicate, arity)` keys. Each record carries explicit provenance metadata (`source`) and a SHA-256 signature produced with the originating agent's private key, verified client-side on retrieval so an untrusted storage server cannot inject or mutate clauses undetected.
2. **Private Knowledge Retrieval (PKR)**: Agents conceal *which* `(predicate, arity)` index $i \in \{1, \dots, n_{pa}\}$ they retrieve from untrusted KB servers using either single-server **$k$-anonymity** ($k-1$ random decoy indices), single-server **$b$-buckets** (partitioned buckets of size $m = n_{pa}/b$), or two-server **Information-Theoretic Private Information Retrieval (`2-PIR`, Chor et al.)** over non-colluding replicated KBs using XOR secret-sharing.
3. **Strictly Local Inference with TTL Caching**: Unification and resolution ($\mathcal{E}$) execute exclusively inside the querying agent's local interpreter, paired with a time-to-live (TTL) local clause cache that eliminates repeated external lookups during deep recursion (`nreverse` at depth `496`, `zebra`).

---

## Why Not a Skill?

Evaluated under [`skill-design-methodology`](../skills/skill-design-methodology/SKILL.md) ($\text{Utility} = \text{Specificity} \times \text{Abstractness}$), `tipp++` provides an important **architectural design pattern** (captured as a governance rule in [`multi-agent-coordination.md`](../rules/multi-agent-coordination.md)) rather than a standalone cross-project `SKILL.md`:

- **Narrow symbolic prototype scope**: All experiments run on a single laptop simulating client/server execution in one Python process over a static pure Horn-clause Prolog KB of only **`99` Horn clauses** (`46` distinct `(predicate, arity)` pairs) and `18` classic Prolog micro-benchmarks (lists encoded manually as `cons`/`nil`, without arithmetic built-ins, cuts, tabling, or argument-level JITI indexing).
- **Mismatch with dense vector/RAG memory**: Modern LLM multi-agent semantic memories retrieve top-$k$ approximate nearest-neighbor embeddings over thousands to millions of chunks rather than exact integer-indexed `(predicate, arity)` slots padded to uniform bit-length $r$. Directly porting bit-vector XOR `2-PIR` (`2 * n_pa` query bits scanning the full bit-padded table) to dense vector stores requires specialized cryptographic ANN/PIR protocols not specified or benchmarked in the paper.
- **Unmodeled systems layers**: Network transport latency, TLS/channel logs, concurrent multi-agent contention, key distribution/revocation, and non-collusion enforcement between replicated KB hosts are left out of scope in the prototype evaluation.

---

## Core Empirical & Complexity Findings

### 1. Communication and Computation Trade-Offs Across Private Retrieval Modes

Let $n_{pa}$ denote the number of distinct `(predicate, arity)` entries in the KB and $r$ the uniform padded bit-length of each signed record (`Table 1`):

| Retrieval Mechanism | Servers Required | Query Bits Sent | Answer Bits Received | Client Reconstruction Cost | Repeated-Query Privacy Property |
|:--------------------|:-----------------|:----------------|:---------------------|:---------------------------|:--------------------------------|
| **`k`-anonymity** | `1` | $k \cdot 64$ | $k \cdot r$ | Select `1` of $k$ | Non-deterministic decoy sampling per query; resists server-side intersection better than fixed buckets at equal bandwidth, though statistical frequency attacks remain possible over massive query volumes |
| **`b`-buckets** ($m = n_{pa}/b$) | `1` | $1 \cdot 64$ | $m \cdot r$ | Select `1` of $b$ | Deterministic bucket mapping; leaks bucket access frequency across repeated queries |
| **`2-PIR` (Chor et al. IT-PIR)** | `2` (replicated, non-colluding) | $2 \cdot n_{pa}$ | $2 \cdot r$ (`r` per server) | $\mathrm{XOR}(2r)$ | **Information-theoretic privacy** against any single server, conditional on strict server non-collusion |
| **`2^d`-PIR** ($d$ servers) | $2^d$ / $d$-way scheme | $d \cdot n_{pa}^{1/d}$ | $d \cdot r$ | $\mathrm{XOR}(dr)$ | Scales query upload sublinearly ($n_{pa}^{1/d}$) for larger $n_{pa}$ at higher server coordination cost |

### 2. Prototype Latency Overhead & Client-Cache Amortization

Across `18` Prolog benchmark queries over $n_h = 99$ clauses ($n_{pa} = 46$ `(predicate, arity)` entries), execution times (`Tables 2–4`) show that local TTL caching absorbs nearly all retrieval and cryptographic overhead after cold start:

| Configuration | Cold-Start Non-Cached (`5` fresh runs, mean ± std) | Standard Caching (`2` runs: cold + warm, mean ± std) | Fully Cached (`5` warm runs, `0` server queries) |
|:--------------|:---------------------------------------------------|:-----------------------------------------------------|:-------------------------------------------------|
| **`Baseline` (unprotected `1`-index fetch)** | `0.1779 ± 0.0028 s` | `0.0969 ± 0.1119 s` (`min 0.0178 s`, `max 0.1761 s`) | `0.0135 ± 0.0017 s` |
| **`Bucket` (`b`-buckets)** | `0.1689 ± 0.0025 s` | `0.0919 ± 0.1103 s` | `0.0132 ± 0.0005 s` |
| **`Anon k=4`** | `0.1794 ± 0.0026 s` | `0.0980 ± 0.1160 s` | `0.0130 ± 0.0007 s` |
| **`Anon k=6`** | `0.1785 ± 0.0023 s` | `0.0998 ± 0.1162 s` | `0.0158 ± 0.0033 s` |
| **`Anon k=8`** | `0.1806 ± 0.0016 s` | `0.1006 ± 0.1132 s` | `0.0126 ± 0.0003 s` |
| **`Anon k=10`** | `0.1789 ± 0.0028 s` | `0.0976 ± 0.1149 s` | `0.0131 ± 0.0008 s` |
| **`it2pir` (`2`-server XOR IT-PIR)** | **`0.2231 ± 0.0050 s`** (`~1.25x` baseline) | `0.1192 ± 0.1503 s` (`min 0.0130 s`, `max 0.2255 s`) | **`0.0129 ± 0.0005 s`** |

- Even on cold runs, two-server `it2pir` adds only **`~25.4%` (`+45.2 ms`)** total wall-clock overhead over unauthenticated single-index retrieval (`0.2231 s` vs `0.1779 s`), while single-server `$k$-anonymity` (`k = 4..10`) is statistically indistinguishable from baseline (`0.1785–0.1806 s`) at this scale because record bit-padding dominates transfer cost.
- Once cached locally within the TTL window, recursive resolution drops by **`>13x`** (`0.2231 s -> 0.0129 s`), eliminating external query leakage for active reasoning loops.

---

## Engineering Takeaways & Relevance to Praxis

1. **Break Poisoning Loops at Both Write-Authentication and Read-Observability**: Defending shared multi-agent memory against `AgentPoison`-class attacks is substantially stronger when provenance signatures (blocking unauthenticated writes/tampering on untrusted storage) are paired with **query-pattern obfuscation** and **client-local inference**—preventing an adversary who monitors the storage backend from observing which goals or sub-predicates an agent is actively resolving.
2. **Prefer Randomized `$k$-Anonymity` Over Deterministic Buckets on Single Servers**: When running two non-colluding replicated servers for `2-PIR` is operationally infeasible (e.g., single-tenant deployments), randomized `$k$-anonymity` strictly dominates static `$b$-buckets` at equivalent bandwidth ($b = n_{pa}/k$) because deterministic buckets leak exact equivalence-class access frequencies across repeated queries.
3. **Bound Local Cache TTL Explicitly Against Stale/Revoked Facts**: Client-side caching is essential to make private retrieval practical in multi-step reasoning (`~13x–17x` speedup on warm runs) and prevents recursive subgoals from issuing burst queries that aid traffic analysis—but cache entries must carry bounded TTLs and re-verify publisher signatures on refresh so revoked or superseded facts do not persist indefinitely (see [`dependency-scoped-plan-validation`](../skills/dependency-scoped-plan-validation/SKILL.md) and [`multi-agent-coordination.md`](../rules/multi-agent-coordination.md)).
4. **Separate Provenance Signatures from Provenance Trust Policy**: Verify cryptographic record signatures (`source` + SHA-256 signature) *before* admitting retrieved clauses into the local cache or unifier, and pair signature verification with per-agent source trust filtering so a compromised peer holding a valid key cannot poison domains outside its authority (see [`governed-knowledge-graph`](../skills/governed-knowledge-graph/SKILL.md)).
