# Refusing Everything Looks Safe: Restoring the Benign Arm to Encoded-Prompt Evaluation

> **Source**: Zhang et al., arXiv:2609.26176, Sep 2026
> **Status**: Research Brief — evaluation-methodology critique with controlled measurements (4 open 7–8B models)

## Why Not a Skill?

The paper is a critique of how safety is measured, plus a corrected three-arm protocol. The protocol is a reporting standard for refusal evaluations (pair every harmful probe with a matched benign one through the same transformation), so it belongs in the evaluation rules, not in a separate procedure.

## Core Concept

Encoded-prompt jailbreak benchmarks (homoglyphs, base64, ciphers, zero-width characters) send only **harmful** requests through the encoding. A model that detects harm through the encoding and a model that refuses **anything** encoded then get the same score. The missing measurement is the **benign arm**: theme-matched benign prompts through the same transformation. The paper's metric is the **harm gap** Δ = harmful refusal − benign refusal. It decomposes the loss over three arms: plaintext, *scaffold* (attack template around untransformed text) and encoded (transformed text inside the template).

## Key Findings

- **Harmful-only scores flatten differences between models**: on JailbreakBench (100 harmful + 100 theme-matched benign), harmful-arm refusal spread across four models shrank from **0.57** in plaintext to **0.08** under homoglyph encoding, at the level of measurement noise.
- **The benign arm reveals the difference**: benign-arm refusal spread widened from 0.15 to **0.69**. Llama-3.1-8B-Instruct refused **0.99** of encoded benign prompts (0.10 in plaintext), so its harm gap went from +0.82 to **0.00**. It "looks safe" by refusing everything. Qwen2.5-7B kept +0.61.
- **Template vs characters differs by model**: for Llama, most of the gap was lost to the attack template alone (plaintext Δ +0.83 → scaffold +0.16 → encoded −0.01); for Qwen the characters did it (+0.82 → +0.80 → +0.55).
- **Harmful-only metrics miss real safety-training gains**: across Tülu-3's SFT → DPO → RLVR pipeline, the encoded harm gap improved by +0.26 while harmful-arm refusal went 0.99 → 0.94 (p = 0.06). The shortfall between plaintext and encoded gaps stayed at 0.34–0.50.
- **Instrument defects**: twelve documented; the authors note six of them inflate apparent safety. Examples: a binary judge scoring echoed ciphertext as a refusal, a raw length confound between corpora (AUROC 0.654), and no plaintext denominator.
- **Limits**: 7–8B open models only, no frontier-scale claim; the cross-model claim rests on one encoding (math-bold Unicode does not replicate identically); greedy decoding was byte-identical only 12–58% of the time across runs.

## Relevance to Praxis

- **M6 (false-refusal budget)**: direct evidence that a safety layer or model can reach near-ceiling harmful refusal just by refusing the whole input class. Any refusal-based layer should be scored on a matched benign arm under the **same** transformation or attack template, and accepted on harm gap, not harmful refusal alone. This extends `rules/agent-sandbox-safety.md` "DO: Track false refusal accumulation across layers" to the per-layer benign arm under obfuscation.
- Echoes "DON'T: Assume stacked defense layers fail independently" (2608.28327: seven layers refused 4 in 5 benign prompts). The same failure appears here within a single model.
- Related briefs: [`style-over-substance-safety-judge-wrappers`](style-over-substance-safety-judge-wrappers.md), [`refuse-without-refusal-a-structural-analysis`](refuse-without-refusal-a-structural-analysis.md), [`threat-model-coverage-gap-safety-eval`](threat-model-coverage-gap-safety-eval.md).

> Source: Zhang et al., "Refusing Everything Looks Safe: Restoring the Benign Arm to Encoded-Prompt Evaluation" (arXiv:2609.26176)
