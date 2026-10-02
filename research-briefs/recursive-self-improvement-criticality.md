# Recursive Criticality of AI Self-Improvement

> **Paper**: [Recursive Criticality of AI Self-Improvement](https://arxiv.org/abs/2609.00137)
> **Praxis source**: src:2609-00137v1

## Why Not a Skill?

Theoretical dynamical model of AI R&D feedback systems, providing mathematical foundations rather than an execution procedure.

---

## Core Concept

Formulates recursive AI self-improvement as a property of an AI–R&D system: a feedback loop in which AI capability raises research productivity, which produces more capable successor systems. The model combines baseline research productivity, recursive feedback, how effectively improvements propagate into successor systems, development-cycle duration, and the rising difficulty of further progress.

### Key Finding

The paper derives a recursive reproduction number, R_AI, that compares feedback strength with the rate at which progress gets harder. When R_AI > 1, improvements compound across development cycles (self-amplifying); when R_AI < 1, their effects weaken across cycles. The transition depends on the structure of the feedback loop, not on any particular capability level, so a system can be self-amplifying before acceleration is visible, and fast progress can occur without self-amplification. Rising research difficulty can end a self-amplifying period. Higher baseline productivity speeds progress without changing the regime, and cycle duration becomes the limiting timescale. Improvements shared across organizations can make the ecosystem self-amplifying even when no single actor is.

This is a descriptive condition, not a recommendation: the paper does not prescribe that agents expand their tool or skill interfaces. (An earlier version of this brief said so, and also attributed a software-engineering "bug complexity damper" to the paper; neither appears in it.)

## Relevance to Praxis

- Theoretical backing for `rules/recursive-improvement.md` "DO: Distinguish systems, data, and algorithmic changes" and `rules/skill-system-design.md` "DON'T: Assume recursive self-improvement is unbounded": whether gains compound depends on feedback strength, propagation into successors, and difficulty growth, not on the absence of a hardware ceiling alone.
- The measurable quantities it names (feedback strength, propagation fidelity, cycle duration, difficulty growth) are candidates for loop-level monitoring alongside per-change acceptance gates.
- Caveat: a model with reference trajectories, not an empirical measurement of any agent system.
