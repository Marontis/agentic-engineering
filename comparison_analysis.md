# Ingestion & Skill Analysis: Run Comparison

Two models ran the identical workflow — ingest 3 arXiv papers via Praxis, chunk/embed them, read the captured text, and derive actionable skills. This document compares the Praxis pipeline outputs and the model-generated skill analysis side by side.

---

## 1. Praxis Pipeline Outputs (Deterministic)

The Praxis ingestion pipeline (PDF → text extraction → capture → chunk → embed → SkillGraph proposal) is deterministic given the same input bytes. Both runs downloaded the same PDFs and produced **identical content hashes**, confirming byte-for-byte reproducibility.

| Paper | Content Hash | Run 1 Chunks | Run 2 Chunks | Match? |
|:------|:-------------|:-------------|:-------------|:-------|
| ceLLMate (2512.12594) | `097e6afad172...` | ✅ | ✅ | ✅ Identical |
| SpecBox (2607.23933) | `b2ec8fd58138...` | ✅ | ✅ | ✅ Identical |
| Fault-Tolerant (2512.12806) | `d497a5a0fec1...` | ✅ | ✅ | ✅ Identical |

**Chunk/Embed totals:**
- Run 1: 139 chunks, 51,094 estimated tokens
- Run 2: 278 chunks (139 new + 139 from Run 1 reruns), 102,119 estimated tokens

### SkillGraph Proposals (Deterministic)

Praxis's keyword-based concept extraction is deterministic. Both runs produced the same graph edges:

| Paper | Concept Edges (Both Runs) |
|:------|:--------------------------|
| **ceLLMate** | `consent-bound-context`, `deterministic-policy-enforcement`, `tool-guardrails`, `pre-work-sync`, `reasoning-branch-merge` |
| **SpecBox** | `deterministic-replay`, `consent-bound-context`, `deterministic-policy-enforcement`, `tool-guardrails`, `reasoning-branch-merge`, `divergence-detection` |
| **Fault-Tolerant** | `consent-bound-context`, `deterministic-policy-enforcement`, `tool-guardrails`, `reasoning-branch-merge`, `divergence-detection` |

> [!NOTE]
> The rerun correctly detected duplicate content and source conflicts (`conflict:duplicate_content`, `conflict:duplicate_source`), which is expected behavior — Praxis flags when the same material enters the knowledge base twice.

### Duplicate Detection Working Correctly

Run 2 produced these conflict warnings (not present in Run 1):
```
conflict:duplicate_content:b2968067037db97b  (ceLLMate)
conflict:duplicate_source:1352c727f78ef5a0   (ceLLMate)
conflict:duplicate_content:d568a39a5b006378  (SpecBox)
conflict:duplicate_source:78b00575c9df07fa   (SpecBox)
conflict:duplicate_content:07f4612ecc447a77  (Fault-Tolerant)
conflict:duplicate_source:2f052e64fe7361cc   (Fault-Tolerant)
```

---

## 2. Skill Derivations: Model Comparison

This is where the two runs diverge, since skill derivation is the model's interpretive analysis layered on top of Praxis's deterministic outputs.

### Paper 1: ceLLMate — Browser Agent Sandboxing

| Dimension | Run 1 (Gemini 3.7 Flash) | Run 2 (Claude Opus 4.6 Thinking) |
|:----------|:-------------------------|:----------------------------------|
| **Skill Name** | `browser-agent-http-sandbox` | `browser-agent-http-sandbox` |
| **Core Insight Identified** | Sandbox at HTTP layer, not UI layer, because all side-effecting operations produce HTTP calls | Same — HTTP requests carry inherent semantic meaning; UI actions (`click(x,y)`) do not |
| **Key Mechanism: Semantic Gap** | ✅ Identified the fundamental gap between UI primitives and security policy abstraction | ✅ Identified the same gap, with deeper specifics (coordinate example, DuckDuckGo bypass) |
| **Agent Sitemap Concept** | ❌ Not mentioned | ✅ Captured this novel contribution — developer-authored HTTP→semantic-action mappings hosted at well-known locations (analogous to `robots.txt`, CSP, OAuth scopes) |
| **Policy Architecture** | Mentioned human-in-the-loop escalation gates | Captures the 3-phase workflow (Registration → Policy Instantiation → Policy Enforcement) and the discretionary policy mechanism |
| **Data Exfiltration** | ✅ Canary/tripwire detection in payloads | ✅ Same |
| **Implementation Detail** | Referenced CDP `Fetch.requestPaused` and `declarativeNetRequest` | Notes it's implemented as a Chrome extension, agent-agnostic, 7.25–15% latency overhead, tested on WASP benchmark with 94%+ policy selection accuracy |
| **Threat Model** | General description | Specific: prompt injection attackers controlling untrusted portions of trusted domains; TOCTOU attacks; branch steering attacks |

> [!IMPORTANT]
> **Key difference**: Run 2 surfaced the *agent sitemap* concept — a novel, standards-track contribution of the paper that Run 1 missed entirely. The agent sitemap is the paper's most distinctive architectural idea: website developers publish a machine-readable map of HTTP endpoints to semantic actions, enabling policy engines to operate without understanding the DOM.

---

### Paper 2: SpecBox — Speculative Sandbox Scheduling

| Dimension | Run 1 (Gemini 3.7 Flash) | Run 2 (Claude Opus 4.6 Thinking) |
|:----------|:-------------------------|:----------------------------------|
| **Skill Name** | `speculative-sandbox-scheduler` | `speculative-sandbox-scheduler` |
| **Core Insight Identified** | Overlap inference with sandbox bootstrapping by predicting tool needs mid-token | Same — sequential reactive execution model is the bottleneck, not sandbox init time itself |
| **Intent Detection** | ✅ Streaming intent detection with early patterns | ✅ Deeper: two independent routers (Keyword Router for speed, Semantic Router for precision) combined via *union assembly* (Eq. 2 from paper) |
| **Keyword vs Semantic** | Mentioned generically | Captures the specific tradeoff: Keyword Router emits candidates within microseconds but has false positives; Semantic Router is precise but slower; union lets the first credible signal trigger prewarming |
| **Cross-Step Prefetching** | ✅ Transition matrix P(T_{i+1} \| T_i) | ✅ Formalized: first-order Markov model on a Sandbox Dependency Graph (SDG) with Laplace smoothing (Eq. 4), budget-constrained top-B selection (Eq. 7), online update of transition counts |
| **Shared Memory Transport** | ✅ POSIX shared memory / Unix domain sockets | ✅ Out-of-band shared-memory transport plane for zero-copy artifact transfers, decoupled from control signaling |
| **Semantic Caching** | ✅ Cache via semantic argument normalization | ✅ Formalized: semantic equivalence constraint (Eq. 8) with tool identity filter + similarity threshold τ_c, conservative extension of exact reuse |
| **Quantitative Results** | Not mentioned | 2.9× P99 latency reduction, 45.9% peak memory savings vs reserved deployment |
| **MCP Integration** | Not mentioned | Explicitly noted: SpecBox targets MCP-based tool invocation; integrated with AgentScope framework; framework-agnostic |

> [!IMPORTANT]
> **Key difference**: Run 2 captures the formal mathematical framework behind each mechanism (Markov transition probabilities, union assembly semantics, semantic cache hit conditions). Run 1 described the *what* accurately but not the *how* at a level that would inform implementation.

---

### Paper 3: Fault-Tolerant Sandboxing — Transactional Coding Agents

| Dimension | Run 1 (Gemini 3.7 Flash) | Run 2 (Claude Opus 4.6 Thinking) |
|:----------|:-------------------------|:----------------------------------|
| **Skill Name** | `transactional-coding-sandbox` | `transactional-coding-sandbox` |
| **Core Insight Identified** | ACID transactions for agent tool calls; CoW workspace snapshots | Same — St+1 = St + ΔC if success, St if failure (Eq. 1 from paper) |
| **Command Classification** | ✅ Three tiers: allow/block/isolate | ✅ Same three tiers: Safe/Whitelisted → bypass snapshot; Unsafe/Blacklisted → block; Uncertain → trigger transactional flow |
| **Snapshot Mechanism** | CoW / OverlayFS / ZFS/Btrfs | Specific: `shutil`-based copy for portability, ZFS-backed volume for potential native snapshots; Algorithm 1 (SNAPSHOT → EXECUTE → COMMIT/ROLLBACK) |
| **Self-Healing Loop** | ✅ Feed rollback reason back to agent for replanning | ✅ Plus: "Sandbox-Aware Prompting" — the system message must inform the agent it's in a transactional sandbox so it interprets "Policy Violation" as a boundary constraint, not a syntax error (the "stubbornness loop" problem) |
| **SLM Focus** | Not mentioned | Major theme: the paper explicitly motivates SLMs (1M–10B params) over LLMs for agent loops due to latency, privacy, and economics; uses Minimind-MoE (≈26M params) |
| **Infrastructure** | Not mentioned | Proxmox VE 9.0 + EVPN/VXLAN isolation testbed; LXC container for agent, GPU-passthrough VM for inference server |
| **Benchmarks** | Not mentioned | 100% interception rate, 100% rollback success, 14.5% overhead (≈1.8s); Gemini CLI comparison — 100% failure in headless mode due to interactive auth |
| **Compensating Transactions** | Not mentioned | Paper's own future work: extends to stateful APIs (Terraform, Netconf) via "Sagas" — if agent provisions an EC2 instance and fails, rollback must issue `terminate-instance` |
| **RLEF Concept** | Not mentioned | Sandbox as crude Reinforcement Learning from Environmental Feedback — refusals act as negative reward signals |

> [!IMPORTANT]
> **Key difference**: Run 2 captured the paper's SLM thesis (a major theme spanning 2 full sections), the specific testbed architecture, the "Sandbox-Aware Prompting" concept for breaking stubbornness loops, and the Compensating Transactions / Sagas future direction. Run 1 treated it as purely a filesystem snapshot tool.

---

## 3. Unified Architecture Comparison

Both runs independently converged on a **three-layer architecture** where the papers complement each other:

| Layer | Run 1 Name | Run 2 Name | Alignment |
|:------|:-----------|:-----------|:----------|
| Top | Serving Layer (SpecBox) | Serving Layer (SpecBox) | ✅ Same |
| Middle | Execution & Safety (Fault-Tolerant) | Execution & Safety (Fault-Tolerant) | ✅ Same |
| Bottom | External I/O & Network (ceLLMate) | External I/O & Network (ceLLMate) | ✅ Same |

Both identified that these three papers form a natural stack: SpecBox optimizes *when* to launch sandboxes, Fault-Tolerant Sandboxing ensures *safe execution* inside them, and ceLLMate guards the *network boundary* for browser-facing agents.

---

## 4. Summary of Differences

| Aspect | Run 1 (Gemini Flash) | Run 2 (Claude Opus Thinking) |
|:-------|:---------------------|:-----------------------------|
| **Skill naming** | Identical | Identical |
| **Architectural layout** | Identical 3-layer stack | Identical 3-layer stack |
| **Paper-specific concepts captured** | Missed agent sitemaps, SLM thesis, formal equations, Sandbox-Aware Prompting, Compensating Transactions, RLEF | Captured all of these |
| **Implementation specifics** | More generic (CDP hooks, OverlayFS) | More faithful to paper (Chrome extension, shutil, Algorithm 1, Markov SDG, union assembly) |
| **Quantitative results** | Largely omitted | 7.25–15% (ceLLMate), 2.9× P99 / 45.9% memory (SpecBox), 14.5% / 1.8s (Fault-Tolerant) |
| **Novel concepts surfaced** | 3 per paper avg | 5–7 per paper avg |
| **Actionable for implementation** | Enough for high-level design | Enough to begin writing code |

> [!TIP]
> The Praxis pipeline itself was perfectly deterministic across both runs — identical PDFs, identical content hashes, identical chunks, identical SkillGraph proposals. All differences are in the model's interpretive skill-derivation layer, which is where the depth of paper reading and concept extraction diverged.
