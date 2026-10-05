# GameBoyWorlds: Self-Improvement Without Expert Guidance

> **Source**: GameBoyWorlds: A Testbed for Self-Improvement in Embodied Video Games, [arXiv:2609.32093](https://arxiv.org/abs/2609.32093), Sep 2026
> **Status**: Research Brief, benchmark with mostly negative results

## Why Not a Skill?

The paper contributes a testbed and an evaluation of three existing
self-improvement families. None of them improved reliably, so there is no
procedure to recommend; the lessons are about how to evaluate
self-improvement.

## Core Concept

Agents get training games with no demonstrations, documentation or rewards
and must improve by exploring on their own, then are tested on unseen games
from the same series. Two tracks:

- **Execution**: 500 short-horizon tasks across 10 Game Boy games from five
  series (Pokémon, Zelda, Deja Vu, Sword of Hope, Bomberman); 1,000 tasks
  implemented, 500 evaluated.
- **Playthrough**: two fan-made Pokémon games with 10 milestones each,
  chosen to avoid pretraining contamination.

## Key Findings

- **Baselines are far from solved.** Best frontier model on Execution:
  Gemini-3.6-Flash at 49.3% average. Hardest game (Deja Vu) peaked at 22%;
  easiest (Bomberman Pocket) at 84% (GPT-5-mini).
- **Self-improvement mostly hurt** (Gemma-4-31B, base 40.7%):
  - World modeling: −3.4%.
  - Autonomous skill discovery (propose tasks, practice, behavior-clone):
    −44.3% on average, to 22.6%; Pokémon Red fell from 38.8% to 8.2%.
  - Curiosity-driven exploration with insight distillation: 41.5% overall,
    but from +22% on some games to −29% on others.
- **Contamination masks inability.** Models recalled classic Pokémon
  progression nearly perfectly but under 30% for the fan-made games. The
  playthrough agent cleared several milestones of Pokémon Red within 100
  steps but never left the starter town in the fan-made game.
- **Perception and grounding fail first**: navigation and interaction errors
  persisted even with hierarchical scaffolding, memory and knowledge trees.
- **Limitations**: only tasks with visible feedback are verifiable; the
  playthrough agent is Pokémon-specific; deterministic game environments.

## Relevance to Praxis

- Supports the acceptance-gate requirement in rules/recursive-improvement.md
  ("Pass every self-modification through one acceptance gate"): learned
  skills and insights that helped on one game harmed others, so per-change
  regression checks across held-out environments are necessary, not
  optional.
- Evaluate self-improvement on held-out, uncontaminated environments. A
  canonical benchmark the model has memorized can make a non-improving agent
  look capable; see
  [process-level-self-evolution-evaluation](process-level-self-evolution-evaluation.md).
- Self-generated practice tasks plus behavior cloning can overfit sharply
  when skills are transferred to new environments in the same family.

> Source: GameBoyWorlds: A Testbed for Self-Improvement in Embodied Video Games (arXiv:2609.32093)
