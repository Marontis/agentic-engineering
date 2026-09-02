# The Answer Is Not the Argument: Chain-of-Thought Monitoring Bias

> **Paper**: [The Answer Is Not the Argument](https://arxiv.org/abs/2609.00264)
> **Praxis source**: src:2609-00264v1

## Why Not a Skill?

Empirical oversight benchmark studying monitor failure modes; key takeaway is distilled directly into 
ules/agent-sandbox-safety.md.

---

## Core Concept

Chain-of-thought (CoT) monitoring—using an LLM to inspect the intermediate reasoning of another LLM—is a core AI safety strategy. However, monitoring evaluations frequently provide the monitor model with access to the ground-truth reference answer.

### Key Finding

Access to the final answer severely distorts oversight: monitors with answer access focus almost exclusively on conclusion correctness rather than reasoning step validity. When monitoring difficult tasks where ground-truth answers are unknown, monitors fail to detect early false reasoning steps in 60%+ of invalid trajectories.

## Relevance to Praxis

- Establishes a critical rule: oversight monitors and reflection agents must inspect reasoning steps blindly without pre-supplied answers to prevent conclusion bias.
