# Similarity Is Not Validity: Defending Semantic Caches Against Poisoning

> **Paper**: [Similarity Is Not Validity: Defending LLM Semantic Caches Against Poisoning](https://arxiv.org/abs/2609.35908)
> **Authors**: Zhang, Yao, Liu et al. (HKUST, Tsinghua)
> **Praxis source**: src:2609-35908v1
> **Status**: Research Brief — defensive lessons for LLM serving caches

## Why Not a Skill?

The defense is a specific hit filter for single-turn semantic caches (released
as a GPTCache plugin), and the paper does not address agent, tool-call or
multi-turn caches. The lessons for anyone putting a semantic cache in front
of an agent are worth keeping; the procedure is better taken from the
authors' code than re-described here.

---

## Core Concept

A semantic cache returns a stored answer when a new query's embedding is close
enough to a cached query. Closeness in embedding space is not the same as
"needs the same answer": two queries can be near-identical as vectors and
still differ in a constraint or fact. An attacker can therefore plant a
cache entry whose key is close to a benign query but whose stored answer is
wrong or malicious, and later users get it without the model being called.

The defense exploits the structure of such keys: a paraphrase of the target
plus extra steering text. **Deletion Gain** checks whether deleting a window
of the cached key makes it *more* similar to the incoming query (benign
paraphrases lose similarity under deletion). An **Answer Check** then asks
whether the deleted text shaped the stored answer, so harmless additions
("answer briefly") are not flagged. A hit is rejected only when both fire.

## Key Findings

- At a 5% false-positive rate (e5 embeddings), block rates were 82.0%,
  95.6% and 98.2% on the three attack classes, and end-to-end attack success
  fell to 0.6–2.6% from 30–91% undefended.
- Overhead about 0.021 ms per cache hit and zero model calls at serving
  time; storage 11–104 kB of float16 vectors per entry. An LLM judge blocked
  more but took about 4.4 s per hit.
- Five adaptive attacks: success stayed at or below 0.087 (gradient-based
  attack, 0.587 undefended). Attacks that evaded the deletion signal, such
  as interleaving, often failed to steer the model's answer at all.
- An embedding-only classifier blocked 61.5% of poisoned entries; adding
  answer embeddings raised it to 76.3%, supporting the claim that embeddings
  discard validity information present in the raw text.
- On real prompt workloads, the false-positive rate was 5.0–5.9%, but
  hit-rate loss reached 30.6% on LMArena (3.5% search, 7.4%
  classification). Of the LMArena hits it rejected, 84.2% were invalid
  hits at the 0.90 threshold anyway.

## Defensive Lessons

1. **A similarity threshold is not a correctness check.** Any cache keyed on
   embeddings will serve wrong answers to near-duplicate queries even without
   an attacker; poisoning turns that into an attack.
2. **Put all attacker-controlled input in the cache key.** The defense
   assumes the key is the full single-turn request. If the key omits part of
   the input (e.g. multi-turn history, retrieved context), steering text can
   hide there and the check cannot see it.
3. **Don't share answer caches across trust boundaries** (users, tenants)
   unless entries are validated; a single poisoned entry serves every later
   matching query.
4. **Calibrate thresholds on local benign traffic.** Block rates varied
   70.5–82.0% across embedding models, and hit-rate cost varies by workload.
5. **Agent caches are untested.** Caching tool results or plans by semantic
   similarity raises the same validity question with higher stakes; this
   paper gives no numbers for it.

## Relevance to Praxis

- Relevant wherever an agent stack adds semantic result caching, e.g. the
  semantic result cache in [`speculative-sandbox-scheduler`](../skills/speculative-sandbox-scheduler/SKILL.md).
- Same "embedding similarity is not functional equivalence" lesson as
  "DON'T: Rely on dense semantic embeddings alone for retrieving code or
  executable skills without execution verification"
  (`rules/skill-system-design.md`) and
  [`execretrieval-code-embedding-functional-gap`](execretrieval-code-embedding-functional-gap.md).

> Source: Zhang et al., "Similarity Is Not Validity: Defending LLM Semantic
> Caches Against Poisoning" (arXiv:2609.35908)
