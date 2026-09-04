# Reflect-SQL: Multi-Stage Self-Reflection for Text-to-SQL

> **Paper**: [Reflect-SQL: A Self-Reflection Based Framework for Text-to-SQL](https://arxiv.org/abs/2609.02944)
> **Praxis source**: src:2609-02944v1

## Why Not a Skill?

Domain-specific text-to-SQL system architecture. The general principle of counterexample and execution-grounded repair is generalized in `counterexample-guided-repair`.

---

## Core Concept

Enterprise text-to-SQL faces three severe hurdles: schema obscurity (cryptic column names and unindexed tables), vague user intent, and logical/semantic generation errors. Reflect-SQL decomposes SQL synthesis into three interconnected self-reflection feedback loops:
1. **Feedback-Driven Retrieval Loop**: Iteratively clarifies and rewrites vague user questions using dynamic schema knowledge bases.
2. **Iterative SQL Synthesis Loop**: Validates syntax against database dialect parsers and dry-run execution.
3. **Entailment and Reflection Loop**: Evaluates semantic alignment between the SQL execution result and user intent via LLM-as-a-judge scoring, enriching the schema knowledge base over time.

### Key Finding

On the challenging enterprise BIRD benchmark, Reflect-SQL achieves an execution accuracy of **72.03%**, delivering an **11.05% improvement** over state-of-the-art baselines without requiring gold-standard reference SQL labels during evaluation.

## Relevance to Praxis

- Highlights the effectiveness of multi-stage decoupled reflection: separating schema disambiguation from syntax parsing and semantic entailment prevents compound generation errors.
