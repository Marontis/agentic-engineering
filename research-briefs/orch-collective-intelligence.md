# ORCH: Organizational Principles Enable Collective Intelligence in Embodied AI

> **Paper**: [ORCH](https://arxiv.org/abs/2609.11737) (Ji, Hyun, Chen)
> **Praxis source**: `src:2609-11737v1`

## Why Not a Skill?

Architecture — describes organizational principles (hierarchy, specialization, communication protocols) for embodied multi-agent systems. The principles are interesting but tied to physical/embodied coordination.

---

## Core Concept

Applies organization theory (from management science) to embodied AI agent teams. Explicit organizational structure (specialized groups, reporting hierarchies, ordered phase transitions) outperformed decentralized and hybrid coordination. The organizations combine pooled interdependence (concurrent work within specialized groups) with sequential interdependence (prerequisite-ordered work between mission phases).

## Setup and Results

- **Task**: 25 procedurally generated wildfire-response missions (reconnaissance, rescue, transportation, resource management, containment, suppression); 5 seeds per task; eight LLMs.
- **Team size**: from three-agent, single-role tasks up to 50 heterogeneous agents (e.g. 25 firefighters, 10 drones, 10 helicopters, 5 bulldozers).
- **Inputs**: fully cooperative; no adversarial agents or untrusted inputs.
- **Baselines**: CAMON and COELA (decentralized), HMAS-2 (hybrid centralized-decentralized), Embodied (prompt-based organizational structures).
- **Human-designed ORCH organizations**: final score +63.97% and execution efficiency +74.29% on average versus the four baselines; first place in 32.6% of combinations for final score versus 16.2% for the strongest baseline.
- **LLM-generated organizations**: +43.63% final score and +52.53% execution efficiency.
- The advantage was reported as most visible in complex missions with large heterogeneous teams; simple missions with few workers can keep a shallow structure. A single manager over every worker also degrades as the team grows (its context grows with the team), which is why ORCH uses multi-level hierarchy.
- **Not reported**: no per-team-size breakdown and no threshold at which flat coordination fails. An earlier version of this brief said flat structures "break at 10+ agents"; the paper does not state that.

## Relevance to Praxis

- Bears on `rules/multi-agent-coordination.md` — "DO: Structure inter-agent communication around typed intents and bus substrates": hierarchy beat decentralized coordination even with trusted inputs, so trusted inputs alone do not make a flat bus the right choice. BusMA was tested with 4-agent teams on reasoning and retrieval benchmarks; ORCH with up to 50 agents on multi-phase physical missions. Choose topology by team size and task type.
- The organizational structure patterns are relevant to the `multi-agent-federation-governance` skill's governance design.
