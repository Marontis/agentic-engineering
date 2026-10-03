# SMART: Evolve on Part of a Long Job, Then Freeze

> **Paper**: [Breaking Babel: A Self-Evolving Multi-Agent System for Long-Form Subtitle Translation](https://arxiv.org/abs/2609.38660)
> **Praxis source**: src:2609-38660v1
> **Status**: Research Brief. Domain system (subtitle translation) with one transferable pattern.

## Why Not a Skill?

The system is tied to translation: translator roles, a subtitle-adapted
MQM judge, and tools for terminology and display constraints. The
transferable part is a pattern: adapt prompts and routing on a slice of
a long job, freeze them for the rest, and keep a growing job-level
memory. Its self-evolution loop also adopts every proposal without an
acceptance test, so it cannot be copied as written (see below).

## Core Concept

A TV series is translated in two stages. **Test-time training**: the
episodes are split 3:7. On the first 30%, a graph router picks
specialist translators per sentence, a Mixture-of-Agents layer produces
candidates (with tools for terminology checks, subtitle constraints and
context retrieval), and a judge-refiner loop scores them on a 0-10
scale and re-runs translation with the critique when the best score is
below 8.0. Per-agent and per-category judge statistics then drive
rewrites of low-scoring translator prompts and of the routing table.
The rewrites are constrained: a prompt must keep its role statement
and workflow steps, and every routing category keeps at least two
agents. This runs for three epochs. **Test-time inference**: prompts
and routing are frozen for the remaining 70%, while a series-level
memory (terminology, character profiles, domain knowledge, idioms)
keeps growing.

## Key Findings

- **Quality**: best overall SubMQM score in all 15 Subtitle Arena
  directions, with a 6.9% lower average penalty than the strongest
  competing agent system; best model result on all 4 MuSC pairs; human
  evaluation overall 4.50/5.
- **What matters (ablation, six directions, penalty increase when
  removed)**: series memory +0.78 on average, MoA +0.61, contextual
  retrieval and idiom bank +0.56, sliding-window consistency +0.47,
  self-evolution +0.36, dynamic routing +0.27. One translator with a
  combined prompt instead of MoA: +0.41.
- **No acceptance gate**: the paper's optimization protocol states that
  a proposal satisfying the structural constraints is adopted, with no
  validation-gated acceptance test, rollback or early stopping; the
  final epoch's configuration is used.

**Limitations stated by the authors**: SubMQM is an LLM-based judge
(mitigated by a judge swap and a human study on a subset of
directions); much higher test-time cost than a single-call translator;
one upstream corpus, English-pivoted.

## Relevance to Praxis

- **Persistent job-level memory beat prompt evolution.** In this
  ablation, removing memory cost about twice as much as removing
  self-evolution. For long, consistent outputs (series, codebases,
  document sets), build the shared memory first.
- **Evolve on a slice, freeze for the rest** is a cheap way to bound
  self-modification to a known window. But the freeze is not a gate.
  Any adopted prompt or routing rewrite should pass "Pass every
  self-modification through one acceptance gate"
  (rules/recursive-improvement.md): no regression beyond a noise margin
  estimated from repeated baseline runs. SMART skips that step.
- **Separate specialist hypotheses beat one merged prompt** (+0.41
  penalty for the combined prompt), in one domain with one LLM judge.

> Source: Breaking Babel: A Self-Evolving Multi-Agent System for Long-Form Subtitle Translation (arXiv:2609.38660)
