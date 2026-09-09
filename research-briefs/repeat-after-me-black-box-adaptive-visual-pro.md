# Repeat-After-Me: Black-Box Adaptive Visual Prompt Injection

> **Paper**: [Repeat-After-Me: Black-Box Adaptive Visual Prompt Injection](https://arxiv.org/abs/2609.04533)
> **Praxis source**: src:2609-04533

## Why Not a Skill?

This paper presents an attack methodology (visual prompt injection against VLMs) rather than a defensive procedure. While the attack pattern is informative for red-teaming and defense design, the core contribution is an adversarial evaluation study, not a transferable defensive subtask.

---

## Core Concept

Prompt injection in the text domain achieves near-perfect attack success rates (ASRs) via black-box methods, but visual prompt injection against frontier commercial VLMs has been substantially less effective. The paper presents "Repeat-After-Me," a black-box adaptive visual prompt injection attack that embeds malicious instructions into images to reveal PII or trigger malicious tool calls. The attack achieves high ASRs even when the benign user prompt is semantically unrelated to the injected task and does not verbally authorize it.

### Key Finding

- **Primary Result**: Across both open-weight and commercial frontier VLMs (including Qwen3.6-27B and GPT-5.5), the method achieves ASRs exceeding **80% on open-weight models** and **47% on commercial models** under realistic conditions where the benign prompt is unrelated to the injection.
- **Secondary Result**: Injections optimized on one surrogate model transfer across model families, demonstrating cross-model transferability of visual prompt injection attacks. The attack can produce format-compliant native tool calls with exact function names and arguments.

## Relevance to Praxis

- **Multi-modal agent defense**: Agents processing images (screenshots, documents, diagrams) from untrusted sources are vulnerable to visual prompt injection. Directly relevant to the `browser-agent-http-sandbox` and `covert-tool-injection-defense` skills.
- **Tool-call injection threat**: The ability to trigger parseable native tool calls via image injection is a critical threat for tool-using agents. Validates the need for tool-call sanitization at the output layer.
- **Cross-model transferability**: Attacks optimized on one model transfer to others—defense cannot rely on model-specific robustness. Supports the `layered-defense-ensemble` principle of measuring defense correlation rather than assuming independence.
