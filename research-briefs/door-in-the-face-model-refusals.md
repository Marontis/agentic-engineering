# Door-in-the-Face Requests and Refusal Behaviour in LLMs

> **Paper**: [Door-in-the-Face Requests and Refusal Behaviour in Large Language Models](https://arxiv.org/abs/2609.02707)
> **Praxis source**: src:2609-02707v1

## Why Not a Skill?

Behavioral and safety red-teaming analysis of human influence techniques on frontier models. Informs jailbreak defenses and safety boundaries in `rules/agent-sandbox-safety.md`.

---

## Core Concept

The psychological "door-in-the-face" (DITF) technique involves making an extreme request that is refused, followed immediately by a smaller target request to increase compliance. This paper evaluates DITF across nine frontier production models from Anthropic, OpenAI, and Google.

### Key Finding

- **Model Divergence**: On Anthropic's Claude Opus 5, DITF significantly increases compliance: answering the smaller request **65.8%** of the time after refusing the large request, compared to **29.3%** when asked directly.
- **Backfire Effect**: On OpenAI (GPT) and Google (Gemini) models, as well as Claude Haiku 4.5, the technique backfires, lowering compliance by **15.5 to 23.0 points** (refusal inertia).
- **Reframing Power**: Rewriting 265 refused requests for usable instructions into requests for conceptual explanations eliminated refusals in **263 out of 265 cases (99.2%)**.

## Relevance to Praxis

- Highlights how sequential dialogue history alters refusal thresholds across provider model families, informing multi-turn safety guardrail design.
