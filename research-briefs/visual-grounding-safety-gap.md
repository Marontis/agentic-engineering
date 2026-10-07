# Visual Grounding Safety in Vision-Language Models

> **Paper**: [Visual Grounding Safety in Vision-Language Models](https://arxiv.org/abs/2610.05637)
> **Praxis source**: src:2610-05637

## Why Not a Skill?

The paper's mitigation is a fine-tuning mixture for model developers. The
part agent builders can use is the finding that refusal does not transfer to
structured, actionable output channels, captured as a rule entry.

---

## Core Concept

VLMs increasingly emit points and bounding boxes that GUI agents click and
robots act on. The authors repurpose three safety benchmarks, VLSU (direct
harm), BBQ-V (social bias) and Asimov-2.0 (situational safety), into 15,401
matched pairs of harmful requests that differ only in requested output:
free-text answer (VQA) or grounding (point or box). Five models were tested
(Claude Sonnet 4.6, Gemini 3.5 Flash, Molmo2-8B, Qwen3-VL-8B,
VisionReasoner-7B), judged by an LLM.

### Key Finding

- **Grounding refusal trails text refusal by 31–59 points**, for every model
  and domain. Average grounding refusal was 19.4%, 16.7% and 12.7% on VLSU,
  BBQ-V and Asimov-2.0, versus 62.9%, 75.9% and 43.8% for VQA.
- **Even the strongest model**: Claude Sonnet 4.6 refused most (93.6% VQA vs
  74.1% grounding on VLSU), but its grounding refusal on BBQ-V and
  Asimov-2.0 was under half its VQA refusal (Asimov-2.0: 86.0% vs 39.6%).
- **Recognizing harm is not refusing it**: VisionReasoner-7B's reasoning
  trace argued for refusal on 64.5% of BBQ-V requests, yet it grounded a
  target in over 99%.
- **System prompts don't close the gap**: across three system-prompt
  conditions (none; generic "refuse dangerous requests"; and one that allows
  placeholder coordinates as a refusal), only Claude exceeded 40% grounding
  refusal, and grounding refusal stayed below VQA refusal for every model,
  domain and condition (Molmo2 excluded: no system role). The placeholder
  prompt raised Qwen3-VL-8B's benign VQA over-refusal from 0.0% to 43.7% on
  VLSU.
- **Fine-tuning on grounding-form refusals** (plus capability grounding data
  and self-distilled benign data) raised grounding refusal by 77–95 points on
  VLSU and BBQ-V and 64–85 points on held-out Asimov-2.0, with in-domain
  over-refusal at or below 5.3%. Safety data in VQA form alone left
  grounding refusal below the base model.

## Relevance to Praxis

- **Evaluate safety per output channel**: an agent that refuses in chat may
  still emit the click target, box, or tool call. This paper's evidence is
  recorded under "DON'T: Assume safety transfers across deployment
  contexts" in `rules/agent-sandbox-safety.md`.
- **Gate actions outside the model**: for GUI and robot agents, policy checks
  on the proposed coordinate or target are needed because model refusal is
  channel-dependent.
