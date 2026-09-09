# MABPD: Multi-Agent Bias Probing & Detection via Structured Argument Debate

> **Paper**: [MABPD: Multi-Agent Bias Probing & Detection via Structured Argument Debate](https://arxiv.org/abs/2609.04841)
> **Praxis source**: src:2609-04841

## Why Not a Skill?

While MABPD uses a multi-agent debate protocol, it is specifically designed for media bias detection in news articles—a domain-specific classification task. The Structured Argument Debate (SAD) protocol with asymmetric burden of proof is interesting but tightly coupled to the bias detection domain (role-weighted voting, bias-specific evidence grounding). The deliberation pattern overlaps with the existing `debate-consensus-memory-calibration` skill.

---

## Core Concept

Media bias operates through subtle linguistic cues—loaded language, selective framing, strategic omission—that resist single-model detection. MABPD introduces a pipeline where three specialized LLM agents analyze articles from complementary perspectives and resolve disagreements through a Structured Argument Debate (SAD) protocol. SAD implements an asymmetric burden of proof: biased claims without grounded textual evidence carry zero weight. Combined with role-weighted voting and post-consensus verification, this replaces supervised decision boundaries with explicit deliberative structure.

### Key Finding

- **Primary Result**: On the BABE benchmark (4,121 articles), MABPD achieves competitive performance with supervised methods without requiring any training data—a training-free alternative to supervised bias classification.
- **Secondary Result**: Ablation confirms that structured deliberation, not mere agent parallelism, drives performance: removing the debate module reduces F1 by up to **10.6 points**.

## Relevance to Praxis

- **Asymmetric burden of proof**: The pattern of requiring grounded textual evidence for positive claims (and assigning zero weight otherwise) is applicable to other multi-agent verification tasks beyond bias detection.
- **Debate vs. parallelism**: Confirms that structured deliberation protocols outperform simple agent ensembles—reinforces the `debate-consensus-memory-calibration` skill's approach.
- **Training-free classification**: Demonstrates that well-structured multi-agent deliberation can match supervised methods without annotated data, relevant to zero-shot agent evaluation workflows.
