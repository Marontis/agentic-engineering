# Harness-of-Harness: Multi-Day Autonomous Software Development

> **Paper**: [Harness-of-Harness: Multi-Day Autonomous Software Development with Continual Improvement](https://arxiv.org/abs/2609.01481)
> **Praxis source**: src:2609-01481v1

## Why Not a Skill?

System architecture framework for multi-day autonomous development rather than an isolated subtask procedure. Key design rules are integrated into 
ules/recursive-improvement.md and 
ules/agent-sandbox-safety.md.

---

## Core Concept

Autonomous software development requires agents to sustain progress over multi-day execution horizons without human intervention. Harness-of-Harness (HoH) organizes development into iterative planning-coding-testing loops with three fundamental pillars:
1. **Incremental capability delivery**: Every loop must deliver a small, verifiable new capability rather than getting trapped in infinite local repair loops.
2. **Independent quality assurance**: A dedicated tester agent runs white-box and black-box tests across functionality, usability, and presentation, feeding structured reports back to the planner.
3. **Progressive disclosure state management**: Project artifacts and history are persisted in the filesystem and indexed compactly, preventing context window saturation.

### Key Finding

Across three rigorous benchmarks (GameCraft-Bench, FrontierSWE, ProgramBench), HoH achieves absolute gains of 16.6–22.1 points over standalone agent harnesses. On FrontierSWE, HoH with frontier models sustains continuous improvement over 10 consecutive loops (from 22% to 72.7% resolution).

## Relevance to Praxis

- Supplies the core rule: autonomous loops must balance repair passes with concrete capability additions.
- Demonstrates that filesystem-based progressive disclosure outperforms dedicated monolithic memory modules for multi-day trajectories.
