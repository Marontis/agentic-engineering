---
name: rag-hallucination-repair
description: >
  How to detect and repair hallucinations in RAG systems at the claim
  level.  Covers claim decomposition, source verification, three repair
  strategies (delete, replace, rewrite), and the grounding-preservation
  trade-off.  Derived from "Detecting and Repairing Hallucinations in
  Retrieval-Augmented Generation" (arXiv:2608.29307).
---

# RAG Hallucination Repair

Use this skill when your RAG system produces answers that may contain
unsupported claims, and you need to not just detect but *fix* them.

## When to Use

- Your RAG system flags hallucinations but doesn't do anything about them
- You need to serve corrected answers, not just "I don't know"
- You want to choose between repair strategies based on your
  grounding-vs-completeness trade-off
- You're building a post-generation quality pipeline

## Core Insight

Most hallucination research stops at detection.  But flagging a faulty
answer changes nothing for the reader.  The question is: **what action
should follow detection?**

Three repair strategies occupy different points on a trade-off:

| Strategy | Text Retained | Hallucination Reduction | Best For |
|:---------|:-------------|:-----------------------|:---------|
| **Delete** | ~64% | Highest | High-stakes (legal, medical) |
| **Replace** | ~72% | Medium | Factual accuracy priority |
| **Rewrite** | ~80% | Lowest | Readability priority |

**Critical finding**: Repair is not confined to faulty answers — 83.5%
of answers annotated as clean are also edited by the repair pipeline.
This means the pipeline improves even "correct" answers.

## Procedure

### Step 1: Decompose the answer into atomic claims

Split the generated answer into individual factual claims.  Each
claim should be a single verifiable statement:

```
Answer: "Paris is the capital of France, founded in the 3rd century
         BCE, and has a population of 2.1 million."

Claims:
1. "Paris is the capital of France"
2. "Paris was founded in the 3rd century BCE"
3. "Paris has a population of 2.1 million"
```

Use an LLM to perform the decomposition if the claims are complex
or interleaved.

### Step 2: Verify each claim against retrieved sources

For each claim, check whether it is supported by the retrieved
documents:

- **Supported**: The claim can be traced to specific text in a
  retrieved document
- **Unsupported**: The claim has no basis in the retrieved documents
- **Contradicted**: The retrieved documents contain information
  that directly contradicts the claim

### Step 3: Choose a repair strategy

For each unsupported or contradicted claim, apply one of three
strategies:

**Strategy A — Delete**: Remove the unsupported claim entirely.
- Maximizes grounding (everything remaining is source-backed)
- Minimizes completeness (answer may feel truncated)
- Best for: high-stakes applications where unsupported claims
  are unacceptable

**Strategy B — Replace**: Substitute the unsupported claim with
the most relevant text from the retrieved source.
- Moderate grounding and completeness
- May produce awkward transitions if the source text doesn't
  flow naturally with the rest of the answer
- Best for: factual reference systems

**Strategy C — Rewrite**: Regenerate the unsupported claim
conditioned on the source text, maintaining the answer's style.
- Maximizes completeness and readability
- Lowest grounding guarantee (the rewrite may introduce new
  unsupported content)
- Best for: user-facing assistants where readability matters

### Step 4: Reassemble and validate

After repairing individual claims:

1. Reassemble the answer from repaired claims
2. Run a second verification pass to ensure repairs didn't
   introduce new hallucinations (especially for rewrite strategy)
3. If the second pass finds issues, apply delete strategy as
   a safe fallback

### Step 5: Log repair actions

For auditability, log:
- Which claims were flagged
- Which repair strategy was applied
- The original vs. repaired text
- The source document used for replacement/rewriting

## Environment Caveats

- **Latency-sensitive applications**: Claim decomposition + verification
  adds latency.  For real-time use, consider running the pipeline
  asynchronously and serving a "provisional" answer with a confidence
  indicator.
- **Multi-document answers**: When the answer synthesizes across
  multiple documents, claim verification must check each claim
  against the correct source document, not just any document.
- **Subjective claims**: Claims about opinions, interpretations,
  or predictions can't be verified against sources.  Skip these
  during verification.

## Failure Modes

- **Claim decomposition errors**: If the decomposition merges two
  claims into one, a partially unsupported compound claim may be
  deleted entirely when only part of it was wrong.
- **Rewrite hallucination**: The rewrite strategy can introduce new
  unsupported content.  Always validate rewrites with a second pass.
- **Source quality**: If the retrieved sources themselves contain
  errors, verification will confirm hallucinated claims as
  "supported."  Source quality is outside this pipeline's scope.

## Cross-References

- [`rag-evidence-triage`](../rag-evidence-triage/SKILL.md) —
  Evidence triage happens *before* generation (is the evidence
  sufficient?); this skill operates *after* generation (is the
  answer grounded?)
- [`hallucination-mean-shift-probe`](../hallucination-mean-shift-probe/SKILL.md) —
  The probe detects hallucination at the representation level;
  this skill repairs at the text level.  Use the probe as a fast
  gate, then this pipeline for detailed repair.

## Sources

- Detecting and Repairing Hallucinations in Retrieval-Augmented Generation (arXiv:2608.29307)
