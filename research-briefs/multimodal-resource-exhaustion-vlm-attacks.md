# Multimodal Resource-Exhaustion Attacks on Vision-Language Models (JPPO)

> **Paper**: [Multimodal Resource-Exhaustion Attacks on Vision-Language Models via Joint Pixel-Prompt Optimization](https://arxiv.org/abs/2609.05889)
> **Praxis source**: src:2609-05889

## Why Not a Skill?

This is an attack framework (JPPO) that optimizes adversarial inputs across both image and text modalities to exhaust VLM compute resources. It's an empirical attack study, not a defensive procedure. The cross-modal threat model insight is valuable context but doesn't yield a standalone defensive subtask.

---

## Core Concept

Prior resource-exhaustion attacks against VLMs only optimized images while keeping prompts fixed. JPPO (Joint Pixel-Prompt Optimization) elevates the visible prompt to a first-class adversarial variable alongside image perturbations, performing coupled stagewise optimization over both surfaces. This produces synergistic effects that single-channel attacks miss.

### Key Finding

- **Primary Result**: Joint optimization over pixel and prompt surfaces produces resource-exhaustion attacks that exceed single-modality variants, demonstrating that cross-modal adversarial surfaces are multiplicative, not additive.
- **Secondary Result**: The restricted joint-input threat model is realistic — attackers controlling both image and prompt fields are common in multi-modal agent scenarios (e.g., processing user-uploaded documents with accompanying instructions).

## Relevance to Praxis

- **Multi-modal agent defense**: Agents processing images + text from untrusted sources face compound attack surfaces. Extends the threat model from `repeat-after-me-black-box-adaptive-visual-pro` (visual injection) to resource exhaustion.
- **Availability as attack target**: Most agent security work focuses on integrity (wrong outputs) — this paper highlights availability (compute exhaustion) as a distinct attack class requiring separate defenses.
