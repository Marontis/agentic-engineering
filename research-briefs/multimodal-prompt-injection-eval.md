# An Experimental Evaluation of Multimodal Prompt Injection Attacks on Agentic AI Frameworks

> **Paper**: [Multimodal Prompt Injection Evaluation](https://arxiv.org/abs/2609.09404)
> **Praxis source**: `src:2609-09404v1`

## Why Not a Skill?

Experimental evaluation â€” tests prompt injection across text, image, and audio modalities on agentic frameworks. Provides an attack taxonomy but no new defense procedures.

---

## Core Concept

Evaluates prompt injection attacks across modalities (text in images, audio instructions, cross-modal composition) against real agentic AI frameworks. Finds that multimodal attacks are harder to defend against because safety filters typically operate on a single modality.

### Key Finding

Cross-modal attacks (e.g., instructions split across text and image) have higher success rates than single-modal attacks because no single filter sees the complete instruction.

## Relevance to Praxis

- Extends the `covert-tool-injection-defense` skill to multimodal contexts
- Informs the `taxonomy-driven-red-teaming` taxonomy under multimodal attack categories
