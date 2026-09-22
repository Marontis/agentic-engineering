# Micro-Collaborative Poisoning: A Distributed Attack on RAG Systems

> **Source**: Pereira et al., arXiv:2609.21573, Sep 2026
> **Status**: Research Brief — attack characterization

## Why Not a Skill?

This is an attack characterization study, not a defense procedure. It extends threat modeling for RAG systems but doesn't introduce a transferable countermeasure.

## Core Concept

A false target claim is **divided across multiple locally plausible documents** instead of concentrated in a single malicious passage. Individual poisoned documents leave a weaker explicit poisoning signature than direct poisoning, making the attack difficult to detect through isolated document inspection.

## Key Findings

- Attack is **not driven by a single dominant poisoned passage** but by accumulation of weak adversarial signals across retrieved sources
- Increasing **top-k** makes it more likely that distributed signals appear together in context
- **Poisoning multiple databases** compounds the effect
- Clean database diversity and stronger retrievers **reduce** influence
- The attack achieves downstream influence while leaving a **weaker explicit poisoning signature** than direct poisoning

## Relevance to Praxis

- Extends the existing rag-hallucination-repair skill's threat model: claim-level verification must account for distributed adversarial signals, not just single-document hallucinations
- Defense implication: RAG systems should monitor for thematic convergence across retrieved sources, not just per-document quality

> Source: Pereira et al., "Micro-Collaborative Poisoning" (arXiv:2609.21573)
