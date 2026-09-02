# AgentLogs: Opening the Black Box of GitHub's Cloud Agent

> **Paper**: [AgentLogs: A Dataset for Opening the Black Box of GitHub's Cloud Agent](https://arxiv.org/abs/2608.29204)
> **Praxis source**: `src:records`

## Why Not a Skill?

Dataset â€” traces of real-world cloud agent behavior, not a procedure. Valuable for understanding what production agents actually do but provides no transferable procedures.

---

## Core Concept

Provides real traces from GitHub's cloud-based coding agent, showing the actual sequence of actions, tool calls, reasoning steps, and outcomes during real development tasks. Enables analysis of production agent behavior patterns that lab benchmarks miss.

## Relevance to Praxis

- The trace data reveals real-world agent working memory patterns relevant to the gent-working-memory-eval skill
- Provides ground truth for what cost-effective repo exploration actually looks like in production
