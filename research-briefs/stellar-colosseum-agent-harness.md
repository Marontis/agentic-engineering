# Stellar Colosseum: A Many-Agent Harness for Long-Horizon Research in Mathematics and Theoretical Computer Science

> **Paper**: [Stellar Colosseum: A Many-Agent Harness for Long-Horizon Research in Mathematics and Theoretical Computer Science](https://arxiv.org/abs/2609.15983)
> **Praxis source**: `src:2609-15983v1`
> **Primary topic**: Agent Self-Improvement & Harness Engineering

## Why Not a Skill?

Stellar Colosseum is a specialized research harness and orchestration architecture for large-scale mathematical discovery and theorem-proving. While its readiness gates and falsification trees offer deep architectural patterns, it functions as an end-to-end multi-agent harness rather than a singular transferable subtask skill.

---

## Core Concept

Frontier LLMs excel at generating plausible short proofs and localized code snippets, but consistently falter on long-horizon research where progress hinges on sequences of highly interdependent, uncertain intermediate choices.

Developed by researchers at Google and Carnegie Mellon, **Stellar Colosseum** provides a model-agnostic harness for orchestrating inference on complex theorem-proving and theoretical computer science problems through a multi-stage pipeline:

```
Research Conjecture / Problem Specification
                      │
                      ▼
[Stage 1: Multi-Route Strategy Exploration]
  └── Parallel generation of candidate proof strategies before formal construction
                      │
                      ▼
[Stage 2: Readiness Gate]
  └── Gatekeeper evaluates if candidate strategy is mature enough to decompose
                      │
                      ▼
[Stage 3: Subproblem Decomposition & Dependency Mapping]
  └── Proof plan structured into section-level lemmas with explicit dependency edges
                      │
                      ▼
[Stage 4: Targeted Falsification & Adversarial Attack]
  └── Red-team verifiers construct counterexamples targeted at specific lemmas
                      │
                      ▼
[Stage 5: Overlapping Tree Aggregation]
  └── Synthesizes surviving candidate lemmas and critique refutations into final artifact
```

### Integration with Google Antigravity

Notably, the Colosseum workflow has been integrated directly into **Google Antigravity's Teamwork framework** under the **Long Proof** pattern, demonstrating native compatibility with agentic IDE and multi-agent coordination runtimes.

### Key Findings

- **TCS-Bench Benchmark**: On research-level theorem-proving tasks extracted from top theoretical computer science conferences (FOCS, STOC, SODA), Colosseum achieves **71.0% accuracy** using Gemini 3.1 Pro and Gemini 3.7 Flash.
- **Competitive Programming Frontier**: In a Codeforces evaluation using Gemini 3.1 Pro, the execution-feedback proof pipeline solved **218 of 222 problems** (98.2% solve rate).
- **Novel Mathematical Contributions**: Successfully generated proofs resolving open problems arising from papers published at leading venues including FOCS and JMLR.
- **Readiness Gate Value**: Preventing premature lemma decomposition until strategy readiness passes strict thresholds reduced dead-end search trees by over 50%.

## Relevance to Praxis

- Provides foundational design principles for long-horizon research agents and proof harnesses.
- Confirms the effectiveness of explicit readiness gates before subtask decomposition.
- Directly informs [`counterexample-guided-repair`](../skills/counterexample-guided-repair/SKILL.md) and [`debate-consensus-memory-calibration`](../skills/debate-consensus-memory-calibration/SKILL.md).
