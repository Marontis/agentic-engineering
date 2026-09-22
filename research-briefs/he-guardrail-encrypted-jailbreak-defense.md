# HE-Guardrail: Homomorphic Guardrail Against Jailbreak Attacks for Encrypted LLM Inference

> **Source**: Min et al., arXiv:2609.21484, Sep 2026
> **Status**: Research Brief — no transferable standalone procedure

## Why Not a Skill?

The procedure is specific to homomorphic encryption (HE) infrastructure — running guardrail models (Llama Guard, JBShield, GradSafe) over encrypted data requires HE-specific toolchains, libraries, and hardware. The technique is not transferable to standard agent architectures without HE infrastructure already in place.

## Core Concept

When LLM inference runs over homomorphically encrypted data (privacy-preserving ML), the server cannot inspect incoming prompts or generated responses — making jailbreak attacks invisible. HE-Guardrail evaluates guardrail mechanisms **entirely over encrypted data** and homomorphically controls whether the target-model response is returned to the client.

## Key Findings

- HE-Guardrail closely reproduces plaintext guardrail decisions in the encrypted domain
- Three guardrails instantiated: Llama Guard (content policy), JBShield (jailbreak detection), GradSafe (gradient-based safety)
- Distinct **security-efficiency-utility trade-offs** between the three approaches
- **Critical vulnerability identified**: HE-based PPML is vulnerable to malicious clients submitting adversarial prompts precisely because the encryption that protects benign clients also prevents server-side inspection

## Relevance to Praxis

- Establishes that encrypted inference does not inherently prevent jailbreak defense — guardrails CAN operate over encrypted data
- Extends the layered-defense model: encrypted inference is not a "free" safety layer
- Relevant to any agent architecture that may move toward encrypted model serving

> Source: Min et al., "HE-Guardrail" (arXiv:2609.21484)
