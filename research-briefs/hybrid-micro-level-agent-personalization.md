# Hybrid Micro-Level Personalization for Conversational AI Agents

> **Paper**: [A Prompt-Engineering Approach to Develop Scalable, Flexible, and Real-Time Hybrid Micro-Level Personalization in a General Purpose AI Teaching Assistant](https://arxiv.org/abs/2609.03402)
> **Praxis source**: src:2609-03402v1

## Why Not a Skill?

Domain-specific pedagogical framework (evaluated on Georgia Tech's Jill Watson teaching assistant) combining Bloom's Taxonomy and the Felder-Silverman learning model.

---

## Core Concept

Standard RAG-based conversational agents typically produce uniform responses that do not adapt to individual user preferences or query complexity. This framework implements micro-level adaptation at the individual question level without model fine-tuning. It dynamically conditions prompt generation on two orthogonal axes:
1. **Cognitive complexity assessment**: Automatic classification of incoming questions using Bloom's Taxonomy (Knowledge, Comprehension, Application, Analysis, Synthesis, Evaluation).
2. **User preference dimensions**: 5 explicit learner axes (abstraction level, verbosity, perception orientation, processing style, organizational structure), creating 96 unique profile configurations.

### Key Finding

Evaluated across 2,910 generated responses and human participant studies, prompt-level cognitive and stylistic conditioning reliably alters response granularity, tone, and syntactic structure without corrupting domain grounding or retrieved factual truth.

## Relevance to Praxis

- Demonstrates how to parameterize agent response generation prompts along explicit user-controllable dimensions (e.g., verbosity, abstraction, code-density) while maintaining factual grounding.
