# Judging LLM-as-a-Judge: Rubric Artifacts in Automated Text Evaluation

> **Paper**: [Judging LLM-as-a-Judge: Concerning Rubric Artifacts in LLM-based Automated Text Generation Evaluation](https://arxiv.org/abs/2609.02942)
> **Praxis source**: src:2609-02942v1

## Why Not a Skill?

Empirical meta-evaluation study exposing systemic flaws in rubric-based LLM judges. Actionable guidelines for prompt evaluators are added to `rules/recursive-improvement.md`.

---

## Core Concept

LLM-as-a-judge pipelines frequently rely on rubrics to standardize evaluations. This rests on the assumption that judgments arise from grounded reasoning over candidate responses against rubric constraints. This work proves that rubric text itself encodes latent evaluative priors, allowing classifiers trained *only* on rubric text (with zero access to candidate responses) to predict judge scores above chance.

### Key Finding

- **Rubric-Only Prediction**: Models can anticipate evaluation outcomes solely from lexical cues and embedding geometries in the rubric instructions without ever inspecting candidate answers.
- **Counterfactual Failure**: When either the candidate response or the rubric criterion is counterfactually flipped/reversed, LLM judges systematically fail to update their decisions, exposing widespread shortcut learning and confirmation bias.

## Relevance to Praxis

- Proves that automated evaluation harnesses cannot assume rubric neutrality; benchmark verifiers must use counterfactual perturbation tests to ensure judge decisions genuinely condition on candidate content.
