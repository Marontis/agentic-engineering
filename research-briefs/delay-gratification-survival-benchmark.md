# Delay-of-Gratification as a Multi-Agent Survival Micro-benchmark

> **Source**: Manakina, Bogdanov & Lung, arXiv:2609.29509, Sep 2026
> **Status**: Research Brief — micro-benchmark and factorial empirical study (single model)

## Why Not a Skill?

A benchmark and a survival-analysis study, not a procedure. Its findings (mandatory reasoning can hurt; peer visibility raises impulsive behavior; heavy personas collapse) are calibration warnings for long-horizon agent design, and one is a candidate rule contribution, but there is no transferable subtask procedure.

## Core Concept

A marshmallow-test framing for long-horizon behavior: at each of 20 steps an agent either takes the immediate reward ("eat", +1.0 at any minute) or waits for a larger terminal reward (+2.0 for waiting the full horizon T=19). A discrete-time hazard model measures the per-minute probability of giving in. The design is a full factorial over social context (isolated vs broadcast peer visibility), hedonic drive (crave / like / neutral / none), age persona (child / adult / senior / none), tool policy (MUST vs MAY use a self-questioning tool), and a per-step tool budget.

## Key Findings

- **Scale**: 19,200 agent trajectories in 64 cells, 6 agents per cell; 99.9% of runs valid. Single model: **Gemini 2.5 Flash-Lite**.
- **Overall**: total eat rate ≈ 0.241; 75.9% of agents persisted to the end; median time-to-eat ≈ 14.8 steps.
- **Peer visibility raises impulsivity**: isolated vs broadcast OR ≈ 0.78 (isolation lowers the per-minute hazard of giving in; equivalently, broadcast raises it), 95% CI [0.73, 0.83], p < .001. Question-asking declined faster under broadcast.
- **Mandatory self-questioning backfired**: MUST vs MAY use of the reasoning tool OR ≈ 1.42, 95% CI [1.35, 1.50], p < .001. Forcing front-loaded deliberation *increased* giving in, opposite the hypothesis.
- **Persona effects dominate everything else**: vs adult, child persona OR ≈ 66.3 and senior OR ≈ 7.55 (both p < .001). Removing both hedonic drive and age persona pushed completion toward ~1.0.
- **Hedonic drive**: vs "crave", like OR ≈ 0.28, none OR ≈ 0.19, neutral OR ≈ 0.03 (all p < .001).
- **Limits**: one model, one decoding setting, binary action space, only the isolated/broadcast extremes of social context, question budget held hidden. Cross-model generalization unknown.

## Relevance to Praxis

- **Mandatory metacognitive scaffolding is not free.** Forcing a self-questioning tool every step measurably worsened self-control here. This is a documented pitfall for the "add a reasoning step" pattern and bears on the Low-severity item in the deconfliction report ("add reasoning budget" vs runaway loops). Single model (Gemini 2.5 Flash-Lite), so treat it as a warning to test, not a general rule.
- **Peer visibility is a risk channel** in multi-agent long-horizon settings, consistent with contagion findings in `rules/multi-agent-coordination.md` and `rules/agent-sandbox-safety.md` guard-agent topologies.
- **Persona choice is a first-order behavioral variable**: evocative personas (child, "crave") sharply change long-horizon behavior independent of the task. Relevant to any deployment that sets a persona for style.
- Related briefs: [`blindspot-long-horizon-agent-safety`](blindspot-long-horizon-agent-safety.md); related skill [`black-box-trajectory-risk-monitoring`](../skills/black-box-trajectory-risk-monitoring/SKILL.md).

> Source: Manakina, Bogdanov & Lung, "Delay-of-Gratification as a Multi-Agent Survival Micro-benchmark for Long-Horizon LLMs" (arXiv:2609.29509)
