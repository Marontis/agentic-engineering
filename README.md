# Agentic Engineering

Research-backed rules, skills, and spec templates for building LLM agent systems -- distilled from 27 arXiv papers and counting.

> **What this is**: A curated knowledge base of transferable procedures, design rules, and decision frameworks for agent engineering. Every rule cites its evidence. Every skill describes a reusable procedure you can drop into your agent workflows.

> **What this isn't**: A framework, library, or SDK. This is *knowledge*, not code. Load it into your AI coding assistant's context (rules, skills) or use the spec templates when starting a new project.

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

---

## Quick Start

**For AI coding assistants** (Antigravity, Claude Code, Cursor, etc.):

1. Copy `rules/` into your project's `.agents/rules/` (or equivalent) -- they'll be active during every session
2. Copy `skills/` into your project's `.agents/skills/` -- they'll be retrieved on-demand when relevant
3. Fill in a `specs/` template when starting a new project in a covered domain

**For humans**: Browse the rules for decision criteria and pitfalls, read the skills for step-by-step procedures, or start from a spec template to map out your design space.

---

## What's Inside

### Rules (Always Active)

Concise, evidence-backed guardrails. Load these so your agent applies them automatically during every coding session.

| Rules File | Domain |
|:-----------|:-------|
| [`agent-sandbox-safety`](rules/agent-sandbox-safety.md) | Sandbox design, command classification, network policy, capability gateway, defense composition |
| [`skill-system-design`](rules/skill-system-design.md) | Skill authoring, selection, library management, skill evolution, training data quality, evidence triage |
| [`recursive-improvement`](rules/recursive-improvement.md) | Self-modification architecture, change classification, evaluation, instruction refinement, targeted reflection, verification |

### Skills (On-Demand)

Transferable, subtask-level procedures. Each skill has a `SKILL.md` with when-to-use criteria, a step-by-step procedure, environment caveats, and failure modes.

#### Agent Sandboxing & Security

| Skill | Source Paper |
|:------|:------------|
| [`browser-agent-http-sandbox`](skills/browser-agent-http-sandbox/SKILL.md) | ceLLMate (arXiv:2512.12594) |
| [`speculative-sandbox-scheduler`](skills/speculative-sandbox-scheduler/SKILL.md) | SpecBox (arXiv:2607.23933) |
| [`transactional-coding-sandbox`](skills/transactional-coding-sandbox/SKILL.md) | Fault-Tolerant Sandboxing (arXiv:2512.12806) |
| [`unified-capability-gateway`](skills/unified-capability-gateway/SKILL.md) | CrabOS (arXiv:2608.28165) |
| [`layered-defense-ensemble`](skills/layered-defense-ensemble/SKILL.md) | Layered LLM Defenses (arXiv:2608.28327) |

#### Self-Improvement & Evaluation

| Skill | Source Paper |
|:------|:------------|
| [`hyperagent-self-improvement`](skills/recursive-self-improvement/hyperagent-self-improvement/SKILL.md) | HyperAgents (arXiv:2603.19461) |
| [`algorithmic-design-evaluation`](skills/recursive-self-improvement/algorithmic-design-evaluation/SKILL.md) | AI4AI-Bench (arXiv:2608.20318) |
| [`targeted-failure-attribution`](skills/targeted-failure-attribution/SKILL.md) | DoCtOR (arXiv:2608.28264) |
| [`behavior-aware-verification`](skills/behavior-aware-verification/SKILL.md) | HarnessLens (arXiv:2608.27311) |

#### Skill Evolution & Knowledge

| Skill | Source Paper |
|:------|:------------|
| [`knowledge-compounding-loop`](skills/knowledge-compounding-loop/SKILL.md) | WikiSkill (arXiv:2608.27454) |
| [`iterative-instruction-refinement`](skills/iterative-instruction-refinement/SKILL.md) | NPO (arXiv:2608.27266) |
| [`skill-design-methodology`](skills/skill-design-methodology/SKILL.md) | Break It Down, Pass It On (arXiv:2608.20274) |
| [`capability-aware-skill-selection`](skills/capability-aware-skill-selection/SKILL.md) | Optimal Skill Selection (arXiv:2608.19993) |

#### Retrieval & Evidence

| Skill | Source Paper |
|:------|:------------|
| [`rag-evidence-triage`](skills/rag-evidence-triage/SKILL.md) | Knowing Before Answering (arXiv:2608.27661) |

### Spec Templates (Project Kickoff)

Structured decision frameworks to fill in when starting a new project. Each template surfaces research-backed decision points with evidence notes.

| Template | Domain |
|:---------|:-------|
| [`agent-sandbox.spec`](specs/agent-sandbox.spec.md) | Designing agent execution sandboxes |
| [`skill-library.spec`](specs/skill-library.spec.md) | Designing skill memory systems for LLM agents |
| [`self-improving-agent.spec`](specs/self-improving-agent.spec.md) | Designing self-modifying agent systems |

### Research Briefs

Papers that provide valuable context but don't produce standalone skills:

| Brief | Why It's Here |
|:------|:-------------|
| [`ai-agency-typology`](research-briefs/ai-agency-typology.md) | Legal vs moral agency framework for AI accountability |
| [`agentic-data-quality-framework`](research-briefs/agentic-data-quality-framework.md) | ACE lens for assessing agentic training data quality |
| [`planner-controller-decoupling`](research-briefs/planner-controller-decoupling.md) | Architectural pattern for real-time agent systems |
| [`agent-control-cycle-benchmark`](research-briefs/agent-control-cycle-benchmark.md) | Evaluation taxonomy for iterative agent control |
| [`agentic-os-interface-design`](research-briefs/agentic-os-interface-design.md) | Interface principles from String and CrabOS |
| [`knowledge-conditioned-topology`](research-briefs/knowledge-conditioned-topology.md) | Dynamic multi-agent collaboration topologies |
| [`llm-agents-security-survey`](research-briefs/llm-agents-security-survey.md) | Comprehensive reference for agent security domains |
| [`adversarial-probe-verification`](research-briefs/adversarial-probe-verification.md) | Model integrity verification via adversarial probes |

---

## How This Was Made

Every artifact traces back to a specific paper and was produced through a systematic pipeline:

1. Papers ingested and indexed via [Praxis](https://github.com/your-org/praxis)
2. Each paper analyzed through the [skill-design-methodology](skills/skill-design-methodology/SKILL.md) checklist
3. Papers with transferable subtask-level procedures became **skills**
4. Decision criteria and quantitative pitfalls became **rules**
5. Design spaces with multiple valid configurations became **spec templates**
6. Papers without actionable procedures became **research briefs**

The selection criteria: a paper produces a skill only if it describes a procedure that (a) operates at the subtask level, (b) could appear in 3+ different project types, and (c) is written as natural language, not executable code.

---

## Contributing

Found a paper that should be here? Open an issue with the arXiv link and a brief note on what transferable procedure you see in it.

---

## License

This work is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). You're free to use, share, and adapt everything here -- just give credit.
