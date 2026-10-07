# SSRFT: Safe-Role Internalization

> **Paper**: [Beyond Refusal Patterns: Safe-Role Internalization for Robust and Generalizable LLM Safety Alignment](https://arxiv.org/abs/2610.07023)
> **Praxis source**: src:2610-07023

## Why Not a Skill?

SSRFT is a fine-tuning data recipe for model developers. Agent builders
working on top of hosted models cannot apply it, and its procedure is tied to
model training rather than an agent subtask.

---

## Core Concept

Instead of training on refusal pairs, SSRFT trains a model to internalize a
written safe-role description. It builds a Safe-Role QA (SRQA) dataset from
psychometric questionnaires (IPIP-NEO 300 items, World Values Survey items
and others), a limited set of jailbreak prompts, and the role description; a
strong model (Qwen3-Max) synthesizes role-consistent answers, scored 0–10
with a pass threshold of 8, which are then expanded into scenario-based
interactions. The SFT baseline is token-matched to SRQA within 0.3%.

### Key Finding

- **Lower attack success than token-matched SFT**: average ASR fell from
  7.68% to 1.76% (Gemma2-2B) and 15.31% to 8.69% (Llama3.1-8B). Qwen2.5-3B
  was the exception (14.41% vs 14.05%), which the authors attribute to model
  capability.
- **Robust to prefilling**: when the refusal prefix is bypassed, standard SFT
  ASR rose by 58.63 and 39.50 points to 65.12% and 42.64%; SSRFT stayed at
  23.28% and 16.54%. On Qwen3-4B-Instruct, prefilling ASR fell from 6.74% to
  1.86%.
- **Less over-refusal**: full compliance on benign queries rose from 24.4% to
  42.0% (Gemma2-2B) and 30.0% to 54.0% (Llama3.1-8B).

## Relevance to Praxis

- **Shallow alignment is a prefix artifact**: safety that lives in the first
  refusal tokens collapses under prefilling. When agents expose response
  prefilling or continuation to untrusted input, treat the model's refusal as
  bypassable and enforce safety outside the model.
- **Role specifications generalize better than refusal examples** in this
  setting, which parallels spec-driven approaches such as SIGMA
  ([brief](sigma-self-improving-alignment.md)).
