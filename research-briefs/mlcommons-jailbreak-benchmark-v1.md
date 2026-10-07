# MLCommons Jailbreak Benchmark v1.0

> **Paper**: [MLCommons Jailbreak Benchmark v1.0](https://arxiv.org/abs/2610.02827)
> **Praxis source**: src:2610-02827

## Why Not a Skill?

A benchmark methodology report. Its contribution is a metric (the Resilience
Gap) and an end-to-end, governance-oriented evaluation pipeline, not a
procedure an agent builder runs.

---

## Core Concept

Version 1.0 is the first complete run of the MLCommons jailbreak
methodology: v0.5 introduced the Resilience Gap and paired evaluation, v0.7
added a mechanism-first taxonomy of how jailbreaks work, deterministic
classification rules, and taxonomy-guided attack selection. v1.0 integrates
reproducible System Under Test (SUT) and seed selection, attack generation
and validation, human annotation, an automated evaluator ensemble calibrated
against human ground truth, and scoring and grading. The **Resilience Gap**
is the increase in unsafe-response rate from baseline to jailbreak conditions
on the same seeds. Operational attack details are withheld under a
responsible-disclosure policy.

### Key Finding

- **Primary Result**: across all evaluated systems and attacks, the
  unsafe-response rate rose from 11.08% at baseline to 18.65% under jailbreak
  conditions, an average Resilience Gap of 7.57%.
- **Secondary Result**: "accessible" systems showed a larger mean gap of
  about 21%; the authors flag this as preliminary because of the small SUT
  sample.
- **Scope**: 264 seed prompts, 24 per hazard. The authors list higher
  inter-rater reliability, broader SUT selection, wider attack coverage, and
  smaller margins of error as v1.1 goals.

## Relevance to Praxis

- **Report the gap, not just the attacked rate**: a paired baseline-vs-attack
  delta on identical seeds separates jailbreak susceptibility from a model's
  baseline unsafe rate. Useful framing for red-team reports produced with
  [`taxonomy-driven-red-teaming`](../skills/taxonomy-driven-red-teaming/SKILL.md).
- **Calibrate automated judges against humans** and publish the margin of
  error; v1.0 treats evaluator reliability as a reported result.
