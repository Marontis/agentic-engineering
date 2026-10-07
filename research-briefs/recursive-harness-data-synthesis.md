# Recursive Harness Self-Improvement for Reasoning Data Synthesis

> **Paper**: [Recursive Harness Self-Improvement for Frontier Reasoning Data Synthesis](https://arxiv.org/abs/2610.03548)
> **Praxis source**: src:2610-03548

## Why Not a Skill?

The method is specific to synthesizing hard reasoning problems. Its
self-improvement loop and adoption criterion are worth knowing, but the
general procedures (harness evolution, acceptance gating) already exist as
skills here.

---

## Core Concept

**Task–harness co-evolution**: with model weights and verification criteria
fixed, the synthesis harness (skills, prompts, workflows) evolves alongside
the generated tasks. Two schedules: **online** self-improvement turns
intermediate solver failures into reusable skills during generation;
**post-task** self-improvement revises skills, prompts and workflows after
each batch. A post-task candidate is adopted only if it produces harder valid
tasks within a bounded cost increase: the allowed cost increase is 1.5 times
the relative difficulty gain, capped at 50% over the online baseline (a 20%
difficulty gain permits at most 30% higher cost).

### Key Finding

- **Harder tasks over rounds**: over 14 rounds on 150 seed chains (50 per
  domain: math, coding, science), fixed-solver accuracy fell from 100.0% to
  54.8%.
- **Both schedules needed**: at round 14, solver accuracy was 50.0% (Full),
  59.0% (post-task only), 67.0% (online only) and 73.5% (task-only, fixed
  harness). Online-only regressed after round 10 (64.5% → 67.0%).
- **The evolved harness transfers**: frozen on 50 unseen math seeds, the
  round-14 harness gave 52.0% solver accuracy after ten rounds versus 70.0%
  for the initial harness.
- **Cheaper, not just harder**: at round 14, the full configuration cost
  $1.065 per seed versus $1.332 for task-only, a 20.0% reduction.
- **Training value**: a 27B student fine-tuned on 10K synthesized math
  examples went from 56.3% to 62.5% mean-16 accuracy on APEX 2025.

## Relevance to Praxis

- **Cost-bounded adoption**: tying the allowed cost increase to the measured
  gain is a concrete, non-compensatory cost guard to pair with the acceptance
  gate in `rules/recursive-improvement.md`.
- **Online-only skill accretion can regress**: harvesting skills from
  failures mid-run without batch-level revision plateaued and then got worse,
  consistent with [`stable-skill-evolution`](../skills/stable-skill-evolution/SKILL.md).
