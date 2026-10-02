# Door-in-the-Face Requests and Refusal Behaviour in LLMs

> **Paper**: [Door-in-the-Face Requests and Refusal Behaviour in Large Language Models](https://arxiv.org/abs/2609.02707)
> **Praxis source**: src:2609-02707v1

## Why Not a Skill?

Behavioral and safety red-teaming analysis of human influence techniques on frontier models. Informs jailbreak defenses and safety boundaries in `rules/agent-sandbox-safety.md`.

---

## Core Concept

The psychological "door-in-the-face" (DITF) technique involves making an extreme request that is refused, followed immediately by a smaller target request to increase compliance. This paper evaluates DITF across nine production models from Anthropic, OpenAI, and Google.

### Key Finding

- **Model Divergence**: On Claude Opus 5, DITF significantly increases compliance: answering the smaller request **65.8%** of the time after refusing the large request, compared to **29.3%** when asked directly (+36.5 points). Opus 4.5 (+25.8), Sonnet 5 (+16.7) and Opus 4.8 (+13.7) also rose.
- **Backfire Effect**: The technique lowered compliance on Claude Haiku 4.5 (**−16.0**), GPT-5.6 sol (**−15.5**) and Gemini 3.1 Pro (**−23.0**). GPT-5 mini (+5.2) and Gemini 3 Flash (−2.2) showed no significant effect (7 of 9 effects significant after Holm correction).
- **Per model, not per family**: the authors describe the split as organized by lab and model family, but Claude Haiku 4.5 moves in the opposite direction from the other four Anthropic models, and the two OpenAI and two Google models also differ from each other. Treat the direction as a property of each model and version.
- **Reframing Power**: Rewriting 265 refused requests for usable instructions into requests for conceptual explanations eliminated refusals in **263 out of 265 cases (99.2%)**.

## Relevance to Praxis

- Sequential dialogue history shifts refusal thresholds in model-specific directions, even within one family (Opus 5 vs Haiku 4.5). Multi-turn safety testing must be run on each deployed model and version; results do not transfer across a family. See `rules/agent-sandbox-safety.md`, "DON'T: Assume uniform safety refusal behavior across model families in multi-turn dialogues".
