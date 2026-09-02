# EmbodiedSkills: Orchestrating Closed-Loop VLA Agents

> **Paper**: [EmbodiedSkills: A Unified Framework for Orchestrating, Training, and Deploying VLA Agents](https://arxiv.org/abs/2609.01281)
> **Praxis source**: src:2609-01281v1

## Why Not a Skill?

Embodied robotics framework; the core design pattern (treating agent actions as execution proposals validated by a guarded runtime) is already formalized in skills/transactional-coding-sandbox/SKILL.md.

---

## Core Concept

Vision-language-action (VLA) models predict robot actions but struggle with long-horizon execution. EmbodiedSkills introduces a guarded runtime where high-level policy outputs are treated as execution proposals that must pass pre-condition validation, guarded execution, progress verification, and recovery.

## Relevance to Praxis

- Confirms that the proposal-validation-commit pattern transfers identically from software engineering sandboxes to physical robotic agent runtimes.
