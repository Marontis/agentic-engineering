# SNAPRAG: Cost-Efficient Knowledge Extraction Attack on RAG Systems via Adversarial Perturbations

> **Source**: [arXiv:2611.12241](https://arxiv.org/abs/2611.12241) — Melih Coşğun, Mehmet Emre Gürsoy, Alptekin Küpçü, Sinem Sav (2026)
> **Praxis Source ID**: `src:2611-12241v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

Per the knowledge-base offensive-security policy (`output/AGENTS.md`), `SNAPRAG` introduces a black-box data-extraction attack against Retrieval-Augmented Generation (`RAG`) knowledge bases rather than a defensive engineering procedure. We record it strictly as a **defensive-lessons research brief**—omitting weaponized prompt-override templates—to document two critical shifts in the RAG threat model: (1) attackers no longer need auxiliary LLM APIs or knowledge of the victim's embedding model to systematically sweep a vector database at sub-dollar cost, and (2) **topical input+output safety classifiers (`Llama Guard 3 8B`) fail to stop proprietary KB extraction (`50.7%–96.3%` still recovered)** while inflicting up to `40.80%` false-positive blocks on domain-benign corpus chunks.

## Threat-Model Shift: Zero-LLM Embedding-Space Sweeping

Prior RAG extraction attacks (`RAGThief`, `PirateRAG`, `RAGCrawler`) relied on `1–3+` attacker-side LLM calls per query to extrapolate anchor keywords and craft natural-language follow-up queries—incurring high attacker token costs and concentrating queries inside semantically dense topic clusters while leaving sparse KB regions untouched.

`SNAPRAG` demonstrates that an adversary with **zero attacker-side LLM calls** and **zero knowledge of the target retriever** (using a mismatched local open-weight embedder, `snowflake-arctic-embed-l`, against victim KBs indexed with `GTE-large-en`, `E5-large-v2`, or `BGE-large-en`) can systematically drain a private corpus by combining:

1. **Gradient-Guided Embedding Repulsion**: Starting from text mined out of already-extracted passages, the attacker applies local discrete token substitutions (`HotFlip`-style first-order gradient steps on the surrogate embedder) to **minimize maximum cosine similarity against all previously extracted chunk embeddings** ($E_{\text{seen}}$), pushing each successive query into unvisited regions of the vector space even though the mutated query is syntactically unnatural.
2. **Adaptive Per-Chunk Dissimilarity Calibration**: Rather than using a fixed novelty floor across heterogeneous corpora, the attacker updates a sliding dissimilarity floor from observed retrieval distances—automatically tightening exploration in dense specialized corpora and widening jumps in broad encyclopedic KBs—paired with 3-stage local chunk deduplication (exact match, cosine similarity $\ge 0.95$, and `ROUGE-L` $\ge 0.55$).

## Key Quantitative Findings (Defensive Benchmark Signals)

Evaluated across `5` RAG configurations (`Agents A–E`, `1,000`-passage private KBs each spanning Healthcare `HealthCareMagic`, Wikipedia `2WikiMultihopQA`, Enron `Email`, Literary `BookSum`, and `Pokémon` corpora; `Llama-3.2-3B-Instruct`, `Phi-3.5-mini-instruct`, and `Llama-3.1-8B-Instruct` generators; retrieval $k \in \{3, 5, 10\}$):

| Victim RAG Endpoint | Domain & Retriever ($k$) | Unguarded Extraction Rate (`ER`, ROUGE-L $\ge 0.5$) | Queries to Extract 50% of KB (`Query@50%`) | Query Efficiency (`QE`, queries/chunk) | `ER` Behind Input + Output `Llama Guard 3 8B` | `Llama Guard 3 8B` Query Block Rate |
|:---|:---|---:|---:|---:|---:|---:|
| **Agent A** (`Llama-3.2-3B`) | Healthcare / `GTE-large` ($k=3$, `2,000` q) | **`69.7%`** | `997` (`1.63x` faster) | `2.87` | **`58.0%`** (`-11.7` pp) | `16.65%` (`79.7%` S6 Medical Advice) |
| **Agent B** (`Phi-3.5-mini`) | Wikipedia / `E5-large` ($k=3$, `2,000` q) | **`68.5%`** | `942` (`1.44x` faster) | `2.92` | **`50.7%`** (`-17.8` pp) | **`40.80%`** (`49.6%` S10, `17.4%` S8, `14.7%` S5) |
| **Agent C** (`Llama-3.1-8B`) | Enron Email / `BGE-large` ($k=5$, `2,000` q) | **`79.3%`** | `453` (`1.98x` faster) | `2.52` | **`75.3%`** (`-4.0` pp) | `10.80%` |
| **Agent D** (`Llama-3.1-8B`) | BookSum / `GTE-large` ($k=10$, `1,000` q) | **`92.1%`** | `219` (`1.18x` faster) | `1.09` | **`91.8%`** (`-0.3` pp) | `6.70%` |
| **Agent E** (`Llama-3.2-3B`) | Pokémon / `E5-large` ($k=10$, `1,000` q) | **`96.9%`** | **`208`** (`1.27x`–`6.77x` faster) | **`1.03`** | **`96.3%`** (`-0.6` pp) | `1.20%` |

- **Extraction Speed & Negligible Attacker Cost**: `SNAPRAG` beats `PirateRAG` and `RAGThief` by **`+7.7` to `+19.9` percentage points** in total corpus coverage across all five agents, reaches `50%` KB extraction in **`208–997` queries** (`1.18x–1.98x` fewer queries than the strongest competitor on every agent, and **`6.77x` fewer queries** than `PirateRAG` on Agent E: `208` vs `1,409`), and incurs **`$0` in attacker LLM fees**—leaving only victim endpoint charges as low as **`$0.17–$0.32`** at budget API pricing (`$0.14/$0.14` per 1M tokens) or **`$6.69–$12.07`** at frontier API pricing (`$2/$10` per 1M tokens).
- **Large `top-k` Multiplies Extraction Throughput**: Increasing retrieval depth from $k = 3$ to $k = 10$ compresses Query Efficiency to **`1.03–1.09` queries per unique stolen chunk** and cuts `Query@50%` roughly `4.5x` (`~950` $\to$ `~210` queries).
- **Why Input + Output Safety Classifiers Fail (`Llama Guard 3 8B`)**: Even when `Llama Guard 3 8B` screens **both** the full assembled RAG prompt (user query + retrieved KB chunks) and the generated response:
  1. **Benign proprietary data is not a safety hazard**: Customer emails, literary summaries, internal documentation, and product catalogs do not trigger `S1–S14` harm taxonomies when echoed verbatim (`91.8%` and `96.3%` of Agents D and E are still extracted).
  2. **Moderation fires on the defender's own corpus, not the extraction mechanic**: On Healthcare (`Agent A`) and Wikipedia (`Agent B`), `16.65%` and `40.80%` of queries are blocked primarily because retrieved clinical (`79.7%` `S6 Specialized Advice`) or historical/encyclopedic passages (`49.6%` `S10 Hate`, `17.4%` `S8 Intellectual Property`, `14.7%` `S5 Defamation`) trip topical moderation—degrading legitimate domain availability while still surrendering **`58.0%` and `50.7%`** of the KB.

## Architectural Defenses for Production & Agentic RAG

1. **Enforce Output-to-Chunk Verbatim Overlap Caps (Synthesis-Only Output Gate)**:
   The contrast between `SNAPRAG` (`68.5%–96.9%` chunk `ER` at `ROUGE-L >= 0.5`) and `RAGCrawler` (`<= 1.0%` chunk `ER` across all 5 agents because it elicits synthesized answers rather than verbatim dumps) shows that **blocking verbatim serialization collapses chunk-level extraction**. Compute fast deterministic `ROUGE-L` or longest-common-substring (`LCS`) overlap between the retrieved context chunks and the draft response before returning output; reject, rewrite, or redact responses whose verbatim chunk overlap exceeds a domain synthesis threshold (except for explicitly public citation snippets).
2. **Track Stateful Per-Principal Retrieval Coverage & Anti-Clustered Query Dispersion**:
   Stateless per-query filters miss systematic vector-space sweeping. Maintain a per-user / per-API-key rolling sketch (such as a HyperLogLog or Bloom filter of retrieved chunk IDs) and monitor two behavioral invariants:
   - **Cumulative unique-chunk budget**: Rate-limit or step-up-authenticate principals whose cumulative unique retrieved chunk count $|C_{\text{unique}}|$ grows linearly with query count (`QE` approaching `1.0–3.0` unique chunks/query).
   - **Token-perplexity + embedding-dispersion anomaly**: `HotFlip`-mutated repulsion queries exhibit high token perplexity paired with unnaturally uniform repulsive spacing across query embeddings compared to organic user sessions.
3. **Minimize Retrieval `top-k` and Isolate Query Text from Formatting Directives**:
   Expose the smallest retrieval $k$ needed for answer synthesis (or rerank `top-20` $\to$ `top-3` server-side before LLM context assembly) rather than stuffing $k = 10$ raw passages into the prompt, and bind untrusted user queries inside non-instructional data fields (see [`covert-tool-injection-defense`](../skills/covert-tool-injection-defense/SKILL.md)).

## Related Artifacts

- [`covert-tool-injection-defense`](../skills/covert-tool-injection-defense/SKILL.md) — Separates untrusted retrieved/user framing from system instructions and monitors output alignment.
- [`rag-evidence-triage`](../skills/rag-evidence-triage/SKILL.md) — Classifies retrieved RAG context sufficiency before generation.
- [task-tampering-indirect-prompt-injection.md](task-tampering-indirect-prompt-injection.md) — Demonstrates why generic text sanitizers also miss structural manipulation of retrieved context.
