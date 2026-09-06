# Measuring the Functional-Correctness Gap in Code-Embedding Retrieval (ExecRetrieval)

> **Paper**: [ExecRetrieval: Measuring the Functional-Correctness Gap in Code-Embedding Retrieval](https://arxiv.org/abs/2609.01865)  
> **Praxis source**: `src:2609-01865`

## Why Not a Skill?

*ExecRetrieval* is an empirical benchmark and evaluation study (939 tasks, 23 dense embedding systems, execution oracle) that exposes a fundamental blind spot in vector embeddings for code. Because its primary contribution is an empirical proof of vulnerability rather than a standalone multi-step workflow, its essential operational mandate—requiring execution-grounded verification over pure dense similarity—is codified into `rules/skill-system-design.md`.

---

## Core Concept

Modern coding agents and software RAG architectures rely heavily on dense embedding retrievers (e.g., OpenAI `text-embedding-3`, Cohere `embed-v3`, Voyage, BGE) to locate relevant functions, library implementations, and agent memory snippets. Traditional code retrieval benchmarks evaluate performance against disparate code corpora, measuring topical relevance or lexical overlap.

However, in coding agents, **functional correctness is what matters**, not lexical or topical similarity. Standard benchmarks fail to answer a critical question: *Can dense vector embeddings distinguish a correct implementation from a near-clone variant containing an off-by-one error or subtle bug?*

### The ExecRetrieval Benchmark

The authors constructed ExecRetrieval:
- **939 Python tasks**, each paired with:
  - One **execution-verified canonical implementation** that passes all unit tests.
  - Up to **four execution-verified buggy distractors**, mechanically generated via single-edit targeted mutations (e.g., flipped comparison operator, incorrect boundary check, omitted edge case handling) that fail the test suite.
- **23 dense embedding configurations** plus BM25 evaluated with paired McNemar statistical tests and bootstrap intervals.

```
                  Query: "Find maximum subarray sum in O(N)"
                                     │
                     ┌───────────────┴───────────────┐
                     ▼                               ▼
      Canonical (Execution-Verified)    Buggy Distractor (Single-Edit Mutation)
      def max_sub(nums):                def max_sub(nums):
          cur = mx = nums[0]                cur = mx = nums[0]
          for x in nums[1:]:                for x in nums[1:]:
              cur = max(x, cur + x)             cur = max(x, cur)  <-- BUG
              mx = max(mx, cur)                 mx = max(mx, cur)
          return mx                         return mx
      [Status: PASSES TESTS]            [Status: FAILS TESTS]
```

### Shocking Empirical Findings

1. **The Rank-1 Collapse**: Across the leading hosted embedding systems, top-10 retrieval was virtually flawless (`exec@10 = 1.00`), but top-1 retrieval plummeted to `exec@1 = 0.331`.
2. **Dense Embeddings Prefer Buggy Clones**: When the top-ranked retrieved item was wrong, **91.5% to 99.4% of the time it was one of the paired buggy variants**.
3. **Canonical Subsumption**: The canonical correct code scored *lower* than at least one of its four buggy distractors in **67% to 78% of queries** across leading models.
4. **Dense vs. Sparse Ineffectiveness**: Neither larger embedding dimensions, instruction-tuning, nor lexical sparse models (BM25) solved this issue: embeddings measure semantic topic rather than functional truth tables.

---

## Relevance to Praxis

- **Never Trust Raw Vector Similarity for Code**: In agent memory and RAG pipelines (including Praxis's vector store), code snippets or reusable skills retrieved via vector search cannot be assumed correct based on cosine similarity alone.
- **Execution-Gated Verification**: Agent retrieval workflows must introduce an execution oracle, differential test gate, or counterexample probe (`counterexample-guided-repair`) to validate retrieved code before injecting it into agent contexts.
