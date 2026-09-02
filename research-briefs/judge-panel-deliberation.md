# JudgePanel: A Compact Judge with Panel Deliberation via Adaptive Multi-Reward RL

> **Paper**: [JudgePanel: A Compact Judge with Panel Deliberation via Adaptive Multi-Reward Reinforcement Learning](https://arxiv.org/abs/2608.29168)
> **Praxis source**: `src:2608-29168v1`

## Why Not a Skill?

Training procedure â€” trains a compact LLM judge through simulated panel deliberation. Tied to specific RL training architecture.

---

## Core Concept

Instead of using a single reward model, simulates a panel of judges that "deliberate" by weighting multiple reward signals adaptively. The panel produces better evaluation signals than any single judge because the judges cover different quality dimensions (correctness, helpfulness, safety, style) and their disagreements surface edge cases.

## Relevance to Praxis

- The multi-reward deliberation principle informs how to design evaluation for self-improving agents (relevant to ecursive-improvement rules)
- Panel disagreement as a quality signal connects to the disagreement-reward pattern in curriculum design
