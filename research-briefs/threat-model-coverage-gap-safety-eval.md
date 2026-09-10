# A Translational Note on AI Safety Evaluation

> **Paper**: [A Translational Note on AI Safety Evaluation](https://arxiv.org/abs/2609.06573)
> **Praxis source**: src:2609-06573

## Why Not a Skill?

This paper provides a conceptual analysis identifying the "threat-model coverage gap" — the systematic blind spot where benchmarks only measure harms predefined by developers. It's a diagnostic framework, not a procedural remedy.

---

## Core Concept

The paper challenges the claim that automated red-teaming can replace human evaluators for AI safety. It argues that benchmarks measure how thoroughly an attacker searches a *predefined* set of harms, but harms *not in that set* are invisible to any attacker working inside it. The paper calls this the "threat-model coverage gap" and draws parallels to academic cryptography (where formally secure systems fail against threats outside the model) and clinical drug trials (where internally valid evaluations miss unrepresented populations).

### Key Finding

- **Primary Result**: The threat-model coverage gap means automated red-teaming and human red-teaming are measuring different things — automated methods are better at exhaustive search within a fixed harm taxonomy, but humans are better at discovering harms outside the taxonomy.
- **Secondary Result**: The gap has appeared before in cryptography and medicine with well-documented consequences. Treating internal validity (thorough search) as external validity (comprehensive safety) is a category error.

## Relevance to Praxis

- **Evaluation design**: Directly relevant to `self-improving-red-team` — automated red-teaming is necessary but not sufficient. Human evaluation covers the threat-model gap that automated methods cannot reach.
- **Rule candidate**: DON'T treat automated red-teaming as a complete replacement for human safety evaluation. DO maintain human evaluators specifically for threat-model coverage (finding harms outside the predefined taxonomy).
- **Benchmark design**: Complements `pipeline-dependent-cybersecurity-benchmarks` — benchmarks have both pipeline fragility *and* coverage gaps.
