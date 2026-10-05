# Frontier Autolab: Memory, Dissent and Hindsight Leakage in a Simulated Multi-Agent Firm

> **Source**: Ghosh, "Frontier Autolab: Organizational Memory, Adversarial
> Dissent and Temporal Leakage in Multi-Agent LLM Firms",
> [arXiv:2609.36739](https://arxiv.org/abs/2609.36739), Sep 2026
> **Status**: Research Brief, exploratory case study. Four trajectories,
> two models, one author; treat the findings as hypotheses, not measured
> effects.

## Why Not a Skill?

The paper is a small observational study of one testbed. Its value is a
list of evaluation and design pitfalls that it makes concrete, not a
validated procedure.

## Core Concept

One simulated company, voiced by sixteen role personas plus a Red Team,
makes strategy decisions across nine technology eras (1990-2040). Each era:
briefing, department proposals, Red Team critique, executive decision,
then a judge reveals outcomes, scores the decision and writes lessons into
a persistent "Playbook" memory. Six eras (1990-2020) are scored against
history, so a model that remembers what actually happened can look
prescient.

## Key Findings

Setup: four trajectories (Claude Opus 5.5; Luna 6 via Codex with a single
shared context; Luna 6 with separate contexts per department), run
September 28-29, 2026. The same model played every role and judged.

- **What memory stores shapes behavior.** Firms whose Playbook stored
  market-structure lessons changed identity at all 8/8 era transitions;
  a firm whose Playbook stored validation procedures changed identity in
  3/8. The author's lesson: audit memory for what it stores, not only
  whether it helps.
- **An uncalibrated critic produced paralysis that scored as prudence.**
  The run whose Red Team issued numeric kill gates every era ran gated
  pilots for fifty years, never shipped a product, and scored highest
  (training mean 66.0 versus 60.0-65.0), because the rubric rewarded
  discipline. The author recommends calibrating critics against the cost
  of inaction as well as the cost of error.
- **Scores rose with hindsight leakage.** Era totals correlated negatively
  with the judge's hindsight subscore (within-run r = -0.58, -0.58, -0.92,
  -0.38), so apparent learning across eras is confounded with recall of
  historical outcomes. Other distortions: the judge wrote the next era's
  briefing after seeing outcomes, the same model judged itself, and score
  aggregation was inconsistent across runs.
- **Limitations stated by the author**: four trajectories, two models;
  later runs likely saw Run 001's records; no run had fully independent
  agents; one judge with hindsight access scored everything; per-run
  correlations rest on six points; outcomes are judge estimates; sampling
  parameters were not recorded.

## Relevance to Praxis

- **Evaluation hygiene for historically scored agent tasks** (the author's
  recommendations): report a leakage measure next to performance,
  separate whoever writes briefings from whoever scores, compute totals in
  code, and fix how the rubric treats caution before the run. These are
  specific cases of `rules/agent-evaluation-quality.md` "Trust single-score
  LLM-as-judge evaluations" (DON'T) and "Test evaluators with
  counterfactual perturbations".
- **Critic and Red Team roles need an inaction cost.** A dissent role that
  can veto without paying for vetoes can stall a multi-agent system; this
  is the opposite failure from the consensus problems in
  `rules/multi-agent-coordination.md`.
- **Memory content is a design lever**: what a reflection step writes into
  long-lived memory frames later decisions, which supports auditing the
  lessons themselves (see
  [`knowledge-compounding-loop`](../skills/knowledge-compounding-loop/SKILL.md)).

> Source: Frontier Autolab: Organizational Memory, Adversarial Dissent and Temporal Leakage in Multi-Agent LLM Firms (arXiv:2609.36739)
