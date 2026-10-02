# The Price of Safety: Benign-Case Cost of Memory-Poisoning Defenses

> **Source**: Bhowmik, arXiv:2609.22818, Sep 2026
> **Status**: Research Brief — replicated measurement study (benign traffic only)
> **Praxis source**: src:2609-22818v1

## Why Not a Skill?

The paper measures what four existing memory-poisoning defenses cost on attack-free traffic; it does not introduce a defense or a new procedure. Its transferable content is a measurement protocol (paired design, replicates, per-purpose token attribution, false-quarantine rate) and a placement finding, which fit better as evaluation guidance than as a standalone skill.

## Core Concept

A memory defense runs on every turn, but its benefit only appears on the rare adversarial turn. Attack-success-rate evaluations never measure what the defense costs the rest of the time. The study holds the memory backend, retrieval configuration, answering model, question set, and judge fixed, varies only the defense, and runs everything on benign LoCoMo conversations, so every quarantine is by construction a false positive.

Defenses are grouped by **where** they intercept the pipeline: write-time (sanitization, provenance tagging, LLM anomaly detection before storage) versus read-time (a reranker that re-judges retrieved memories and quarantines inconsistent ones). The finding: placement, not whether the defense calls an LLM, predicts its benign-case price.

## Key Findings

Setup: 6 conditions × 5 conversations (truncated to 150 turns, evidence-aligned questions) × 3 replicates = 90 cells; gemini-3.1-flash-lite for extraction, answering, and the anomaly defense; claude-haiku-4-5 as a cross-provider judge (κ = 0.909 against hand labels).

| Defense | Stage | Utility Δ (pp, 95% CI) | Token overhead | False quarantine rate |
|:--|:--|:--|:--|:--|
| Sanitize | write | +1.8 [−1.7, +5.6] | 0.0% | 0.000 |
| Provenance | write | +1.9 [−2.2, +6.0] | 0.0% | 0.000 |
| Anomaly (LLM) | write | +3.1 [−0.9, +7.1] | 1.2% | 0.000 |
| Rerank | read | **−4.4** [−9.0, −0.05] (McNemar p = 0.064) | 2.7% | **0.336** |
| Stacked (all four) | write + read | −3.1 [−7.4, +1.0] | 4.1% | 0.303 |

- **Read-time reranking silently discards legitimate memory**: on attack-free conversations it quarantined 33.6% of the memories it adjudicated, up to 106 false quarantines in a single conversation. No error is raised; accuracy can mask this when facts are redundant across memories.
- **Write-time defenses showed no cost resolvable at ±4.5 pp**, including the LLM-based anomaly detector. The author stresses this is "no effect detectable at this resolution", not zero cost.
- **Stacking did not compound cost here**: the four-defense stack lost less accuracy (−3.1) and quarantined less (0.303) than the reranker alone. The data show no evidence of compounding; they do not prove a protective interaction. Token overhead was roughly additive.
- **Temperature 0 was not deterministic**: identical conversations produced different memory counts across runs; one apparent single-run defense effect turned out to be a scoring artifact. Replication changed a conclusion.
- **Measurement pitfalls that produced plausible wrong numbers**: missing output-token limit silently truncated extraction to about a quarter of expected memories; a stale price entry misreported cost by 5×; a regex abstention detector misgraded correct refusals (κ 0.663 vs 1.000 for the calibrated detector on 58 blind labels); a stacked wrapper broke the reranker's store access.
- **Resolution floor**: with 5 conversations the exact sign-flip permutation test cannot reach p < 0.05 (minimum 2/32 = 0.0625), so the bootstrap interval is the primary evidence.

Limits: one backbone, one dataset, benign traffic only (attack success not re-measured), act-time defenses not evaluated.

## Relevance to Praxis

- Bears on deconfliction item **M6** and on `rules/agent-sandbox-safety.md` "Track false refusal accumulation across layers" (2608.28327): in this memory setting, stacked false quarantines did **not** accumulate as a union. The two results differ in setting (prompt-refusal classifiers vs memory write/read filters), so the right reading is "measure the assembled stack's benign-case rate", which both support, not "costs always add".
- Adds a benign-traffic metric (false quarantine rate) that the layered-defense guidance lacks; pairs with [`layered-defense-ensemble`](../skills/layered-defense-ensemble/SKILL.md).
- For memory-augmented agents, prefer write-time screening (decision made once, with the originating turn as context) over read-time re-judgement of short, context-free memory strings; see also [`akasicmem-governed-enterprise-memory`](akasicmem-governed-enterprise-memory.md) and [`micro-collaborative-rag-poisoning`](micro-collaborative-rag-poisoning.md).
- The replication and per-purpose token-tagging practices apply to any defense evaluation; compare the repeat-run guidance in [`agent-evaluation-quality`](../rules/agent-evaluation-quality.md).

> Source: Bhowmik, "The Price of Safety: Benign-Case Utility and Token Overhead of Memory-Poisoning Defenses in LLM Agents" (arXiv:2609.22818)
