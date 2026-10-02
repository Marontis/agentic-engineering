# Harness-of-Harness: Multi-Day Autonomous Software Development

> **Paper**: [Harness-of-Harness: Multi-Day Autonomous Software Development with Continual Improvement](https://arxiv.org/abs/2609.01481)
> **Praxis source**: src:2609-01481v1

## Why Not a Skill?

System architecture framework for multi-day autonomous development rather than an isolated subtask procedure. Key design rules are integrated into `rules/recursive-improvement.md` and `rules/agent-sandbox-safety.md`.

---

## Core Concept

Autonomous software development requires agents to sustain progress over multi-day execution horizons without human intervention. Harness-of-Harness (HoH) organizes development into iterative planning-coding-testing loops with three fundamental pillars:
1. **Incremental capability delivery**: Every loop must deliver a small, verifiable new capability rather than getting trapped in infinite local repair loops.
2. **Independent quality assurance**: A dedicated tester agent runs white-box and black-box tests across functionality, usability, and presentation, feeding structured reports back to the planner.
3. **Progressive disclosure state management**: Project artifacts and history are persisted in the filesystem and indexed compactly, preventing context window saturation.

### Key Finding

Over standalone agent harnesses, HoH reports absolute gains of 16.62–22.08 points on GameCraft-Bench, 19–29 points on FrontierSWE, and 6.09–16.85 points on ProgramBench. On FrontierSWE, HoH with Codex and GPT-5.5 (high) kept improving over ten consecutive loops, from 22% to 72.67%. Ablations: removing plan updates cost 8.13 points, evidence feedback 6.28, warm-start 7.85.

## Relevance to Praxis

- Supplies the core rule: autonomous loops must balance repair passes with concrete capability additions.
- Filesystem-based progressive disclosure is a design choice in HoH, not a measured result: the paper does not ablate it or compare it with a dedicated memory module. Separately, 2609.20804 (`research-briefs/empirical-harness-design-study.md`) found that making elided context recoverable added machinery coding agents rarely used and gave no accuracy gain; context management helped mainly by preventing context overflow.
