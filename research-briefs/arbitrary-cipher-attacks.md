# Arbitrary Cipher Attacks Against Large Language Models Do Not Require Fine-Tuning

> **Paper**: [Arbitrary Cipher Attacks](https://arxiv.org/abs/2609.09553)
> **Praxis source**: `src:2609-09553v1`

## Why Not a Skill?

Attack demonstration â€” shows that cipher-encoded prompts can bypass safety filters without fine-tuning. No defense procedure provided.

---

## Core Concept

LLMs can be jailbroken using arbitrary ciphers (rot13, base64, custom substitution ciphers) to encode harmful prompts. The model decodes the cipher and follows the instruction, bypassing safety filters that operate on the surface text.

### Key Finding

This works without any fine-tuning â€” the model's general reasoning ability is sufficient to decode simple ciphers. More complex ciphers require chain-of-thought prompting but still work on frontier models.

## Relevance to Praxis

- Informs the `covert-tool-injection-defense` skill â€” tool outputs could contain cipher-encoded instructions
- Relevant to the `taxonomy-driven-red-teaming` taxonomy under "Safety Bypass" category
