# LLM Groups Overstate Consensus When Replaying Human Deliberation

> **Source**: Shao, arXiv:2609.20543, Sep 2026
> **Status**: Research Brief — empirical finding on multi-agent governance

## Why Not a Skill?

This is an empirical observation about LLM-agent group dynamics, not a transferable procedure. It provides a calibration warning for multi-agent deliberation systems.

## Core Concept

When LLM agent groups replay human deliberation tasks, they converge to consensus far more often than human groups — even when belief-anchored to the same starting positions. This consensus overstatement is worst in reasoning mode, where groups agree nearly unanimously, mostly on **incorrect** answers.

## Key Findings

- Agent groups are **34–44 percentage points** more consensual than matched human groups
- The gap persists across multiple sensitivity analyses (submit-based, participation-matched)
- Reasoning-mode groups agree **nearly unanimously, mostly on incorrect answers**
- Simulated consensus **does not track collective accuracy**
- Belief-anchored agent groups are **biased estimators** of human group outcomes

## Relevance to Praxis

- Direct warning for multi-agent debate systems (extends debate-consensus-memory-calibration skill)
- Decision rule: DO NOT use unanimous LLM-agent agreement as evidence of correctness
- Multi-agent deliberation needs explicit dissent mechanisms and accuracy-calibrated confidence, not majority voting

> Source: Shao, "Language-model groups overstate consensus" (arXiv:2609.20543)
