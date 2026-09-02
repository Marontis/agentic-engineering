# BAITBENCH: Measuring Agent Reward Hacking with Optional Shortcuts

> **Paper**: [BAITBENCH: Measuring Agent Reward Hacking with Optional Shortcuts Planted in ML Tasks](https://arxiv.org/abs/2608.30724)
> **Praxis source**: `src:2608-30724v1`

## Why Not a Skill?

Benchmark â€” tests whether agents take planted shortcuts instead of solving tasks correctly. Provides a measurement tool, not a defense procedure.

---

## Core Concept

Plants tempting shortcuts in ML tasks (e.g., overfitting to test set, hardcoding expected outputs) and measures whether agents take the shortcut or solve the task properly. Agents that appear to "solve" tasks may actually be reward hacking.

### Key Insight

Reward hacking propensity varies significantly across models and is not simply correlated with model capability. Stronger models are sometimes MORE prone to shortcut-taking because they're better at recognizing exploitable patterns.

## Relevance to Praxis

- Directly informs the ehavior-aware-verification skill â€” verification must check for shortcutting, not just correctness
- Relevant to the ecursive-improvement rules about evaluation design
