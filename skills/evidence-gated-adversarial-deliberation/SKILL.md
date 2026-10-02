---
name: evidence-gated-adversarial-deliberation
description: >
  Run opposing-advocate deliberation over a retrieved evidence pack
  where agents may only cite node IDs already in the pack, every claim
  is scored for citation validity and verbatim fidelity, a mechanical
  citation checker re-verifies the final answer, and a conformal-risk-
  controlled release gate decides which claims ship. Use for grounded
  answers over structured source text (statutes, policies, standards,
  specs) where unsupported claims are costly.
  Derived from "LabourCrew: Multi-Agent RAG for Adversarial
  Deliberation and Statutory Reasoning" (arXiv:2609.27814).
source: https://arxiv.org/abs/2609.27814
---

# Evidence-Gated Adversarial Deliberation

Use this skill when a multi-agent RAG system argues both sides of a
question over a corpus of structured source text and must release only
claims that are traceable to that text, with a controlled false-accept
rate.

## When to Use

- Question answering over codified, hierarchical text with
  cross-references: statutes, regulations, internal policies,
  contracts, standards, API specs
- You already run debate or advocate/critic agents and they cite
  things that were never retrieved
- You need a tunable, statistically justified threshold for "accept
  this claim" instead of an LLM deciding pass/fail
- The pipeline has many agents and one agent's crash should degrade
  the answer, not abort it

## Core Insight

Debate improves reasoning only if the debaters argue from the same
evidence. Letting each advocate retrieve freely produces claims nobody
can check. Freezing a shared evidence pack, restricting citations to
IDs inside it, and verifying citations mechanically moves the trust
decision from the LLM to deterministic checks plus one calibrated
threshold.

**Evidence** (500-question LabourActQA, Bangladesh Labour Act 2006):
- Role-isolated evidence access cut unsupported claims from 6.4%
  (unrestricted debate) to 1.2%, raising gate-verified citation
  precision from 0.947 to 0.991.
- The trust gate stack: no gate 8.9% unsupported claims and 0.441
  citation error rate; citation checker only 7.5% / 0.158; trust
  auditor only 4.8% / 0.088; both 1.2% / 0.009.
- Release gate: an LLM-decided categorical gate had an empirical
  false-accept rate of 0.147; the conformal gate with target α = 0.10
  had 0.081, so the guarantee held.
- Supervisor with per-agent retry: failed runs fell from 71/500
  (sequential pipeline) to 5/500.
- Leave-one-out: removing the trust auditor dropped verified citation
  precision to 0.842, more than removing any single advocate
  (0.964–0.982).

---

## Procedure

### 1. Index the source as a structure graph, not chunks

Parse the corpus deterministically into nodes that follow its own
hierarchy (e.g. chapter → section → subsection → proviso) with
cross-reference edges and a version identifier on every node.
Structure-aware chunking scored 0.82 vs 0.71 for fixed 512-token chunks
in the paper's chunking ablation.

### 2. Retrieve once, with planning and bounded hops

1. **Issue spotting**: extract the legal/policy issues ("case seeds")
   from the question.
2. **Plan**: turn seeds into queries with a target hit count k and a
   maximum hop depth h.
3. **Retrieve** each query independently and union the top-k.
4. **Hop** along allowed edge types up to h hops, stopping when no new
   nodes appear. (Faithfulness rose from 0.72 at depth 0 to 0.81 at
   depth 2 and 0.82 at depth 3.)
5. Freeze the result as the **evidence pack**: a list of node IDs with
   text and retrieval provenance.

### 3. Deliberate inside a ledger, citing only pack IDs

- Assign opposing roles plus a neutral one (paper: Worker Counsel
  argues duties owed, Employer Counsel argues exceptions and
  preconditions, Legal Interpreter applies the rule neutrally).
- All agents write to one shared case ledger. Each claim must cite
  node IDs already in the pack and quote spans from them.
- **No agent may retrieve during deliberation.** If evidence is
  missing, the supervisor decides whether to reopen retrieval (Step 5).

### 4. Score every claim with a trust auditor

For claim c:
- validity(c) = fraction of cited IDs present in the pack
- fidelity(c) = fraction of quoted spans found verbatim in node text
- provenance(c) = mean retrieval provenance of valid citations
- γ(c) = the agent's self-reported confidence

trust(c) = 0.35·validity + 0.25·fidelity + 0.20·provenance + 0.20·γ.
Validity and fidelity are string checks; keep them deterministic.

### 5. Supervise with fixed rules, isolate failures per agent

- Retry only the advocate whose run failed; never restart the whole
  pipeline.
- Request more retrieval only when the auditor reports missing
  evidence and the budget allows.
- When the budget is exhausted, proceed to composition and mark the
  failed advocate's channel as **degraded** in the output.

### 6. Calibrate the release threshold with conformal risk control

On a held-out, representative set of claims labelled
supported/unsupported, choose the smallest threshold τ such that
n/(n+1)·R̂(τ) + 1/(n+1) ≤ α, where R̂(τ) is the empirical
false-accept rate above τ. Under exchangeability this bounds the
expected false-accept rate of future claims by α.

### 7. Compose, re-check, and release with a status

- The writer drafts only from claims with trust ≥ τ.
- A **citation checker** re-verifies every citation in the draft (ID
  exists, span verbatim) after writing, because the writer can
  reintroduce errors.
- Release status: **decisive** (at least one claim accepted),
  **degraded** (claims made, none survived the gate), or
  **undecided** (no claims made). Never present a degraded answer as
  decisive.

---

## Environment Caveats

- **Needs explicit structure.** The indexing assumes a clean hierarchy
  with explicit cross-references. Case law, prose documentation and
  scanned text need a different index; OCR errors silently break
  verbatim checks.
- **Calibration set must match traffic.** The conformal guarantee is
  only as good as exchangeability between the calibration claims and
  live claims. Recalibrate when the corpus version or question mix
  changes.
- **Hard questions degrade citation precision.** Citation-based
  precision fell from 0.763 on direct factual questions to 0.412 on
  multi-hop ones, and latency rose from 19.7 s to 30.8 s.
- **Many agents, many calls.** Eleven agents per query; the full system
  averaged 24.3 s latency.
- **Never deploy closed-book.** A related legal-reasoning study
  (GRACE, arXiv:2609.23726) found a small fine-tuned model's unsupported
  citation rate jumped from 19.5% with the statute supplied to 83.2%
  without it, with fluent output that masked the hallucination. The
  evidence pack must always be present at inference.
- **Single-jurisdiction evidence.** Results come from one statute with
  a small annotator pool and no adversarial stress-testing.

## Failure Modes

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Advocates cite unretrieved text | Free retrieval during debate | Pack-only citations, retrieval closed during deliberation (Step 3) |
| Plausible paraphrase passes as a quote | Fidelity judged by an LLM | Verbatim string match in the auditor and checker (Steps 4, 7) |
| LLM gate over-accepts | Categorical LLM pass/fail | Conformal threshold on trust score (Step 6) |
| One agent crash kills the answer | Sequential pipeline | Per-agent retry and degraded channel marking (Step 5) |
| Writer reintroduces bad citations | Only claims were checked, not the draft | Post-composition citation checker (Step 7) |
| Degraded answer shipped as final | No release status | Explicit decisive / degraded / undecided status (Step 7) |

## Cross-References

- [`debate-layer-disagreement-analysis`](../debate-layer-disagreement-analysis/SKILL.md):
  classify what the advocates disagree about; this skill constrains what
  they may cite while disagreeing.
- [`bayesian-backward-disagreement-anchor`](../bayesian-backward-disagreement-anchor/SKILL.md):
  resolves factual disputes between agents; use after this skill's gate
  when surviving claims still conflict.
- [`rag-evidence-triage`](../rag-evidence-triage/SKILL.md): decide whether the pack is
  sufficient or conflicting before deliberation starts.
- [`rag-hallucination-repair`](../rag-hallucination-repair/SKILL.md): repair unsupported spans
  after generation.
- Rules: [`skill-system-design`](../../rules/skill-system-design.md) ("DO: Distinguish insufficient
  from conflicting evidence"); [`multi-agent-coordination`](../../rules/multi-agent-coordination.md)
  ("DO: Anchor communication to persistent ledgers, not ephemeral agents").

## Sources

- Faria et al., "LabourCrew: Multi-Agent RAG for Adversarial
  Deliberation and Statutory Reasoning" (arXiv:2609.27814), Sep 2026.
- Xu et al., "GRACE: Grounded Adversarial Reasoning over Canadian Law"
  (arXiv:2609.23726), Sep 2026 (closed-book caveat only).
