# Rethinking the Test-Time Prompt Tuning Objective from the Perspective of Calibration

> **Paper**: [Rethinking the Test-Time Prompt Tuning Objective from the Perspective of Calibration](https://arxiv.org/abs/2608.30230)
> **Praxis source**: `src:2608-30230v1`

## Why Not a Skill?

Training method â€” calibration-aware prompt tuning requires specific model access and tuning infrastructure. Not a transferable subtask for agent engineering.

---

## Core Concept

Test-time prompt tuning should optimize for calibration (accurate confidence estimates), not just accuracy. Better-calibrated prompts produce more reliable uncertainty estimates, which matters more than raw accuracy when the agent needs to know when to trust its own outputs.

### Key Insight

A prompt-tuned model that's 90% accurate but poorly calibrated (says "I'm 95% sure" on wrong answers) is less useful than an 85% accurate model with good calibration (correctly says "I'm 60% sure" on uncertain cases).

## Relevance to Praxis

- Calibration directly informs the ag-evidence-triage skill â€” well-calibrated models produce more reliable evidence-state classifications
- Relevant to any agent system that uses model confidence for decision routing
