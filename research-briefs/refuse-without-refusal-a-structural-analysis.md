# Refuse without Refusal: Structural Analysis of Safety-Tuning Responses

> **Paper**: [Refuse without Refusal: A Structural Analysis of Safety-Tuning Responses for Reducing False Refusals in Language Models](https://arxiv.org/abs/2609.04714)
> **Praxis source**: src:2609-04714

## Why Not a Skill?

This paper provides a training-data design insight (decompose refusal responses into boilerplate statement vs. rationale, train only on rationales) rather than a runtime procedure an agent can execute. The finding is a design rule for safety-tuning datasets, not a subtask-level operational procedure.

---

## Core Concept

Safety-tuned LLMs frequently produce false refusals—declining benign queries that contain superficially risky language (e.g., "Where can I shoot a good photo?"). The paper decomposes safety-tuning responses into two components: (i) a **boilerplate refusal statement** ("I can't help with that") and (ii) a **rationale** explaining why the query is harmful. Training on both components induces reliance on superficial cues. Training solely on rationales reduces false refusals while maintaining comparable safety performance.

### Key Finding

- **Primary Result**: Rationale-only training reduces false refusals compared to full-response training while maintaining equivalent safety (harmful query refusal rates). The benefit also transfers to ICL (in-context learning) configurations.
- **Secondary Result**: Boilerplate refusal statements act as superficial pattern anchors that cause the model to over-trigger on benign queries containing risk-adjacent language, explaining the false refusal mechanism.

## Relevance to Praxis

- **Guardrail design**: When building agent guardrails or safety filters, avoid training on boilerplate refusal templates. Focus on rationale-based responses that explain *why* something is harmful.
- **False refusal reduction**: Directly relevant to the `layered-defense-ensemble` skill—defense layers that produce false positives degrade agent utility. This paper provides a concrete mechanism for reducing that.
- **Safety-tuning rule candidate**: Could contribute a DO/DON'T rule: "DO train safety responses on rationales only; DON'T include boilerplate refusal statements in safety-tuning data."
