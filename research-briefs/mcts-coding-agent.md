# Development of an Autonomous AI Coding Agent using Monte Carlo Tree Search

> **Paper**: [Development of an Autonomous AI Coding Agent using Monte Carlo Tree Search](https://arxiv.org/abs/2608.29096)
> **Praxis source**: `src:2608-29096`

## Why Not a Skill?

Architecture-specific â€” the MCTS implementation is tightly coupled to specific state representation, action space, and evaluation function choices. Too implementation-heavy for a text-based subtask skill.

---

## Core Concept

Uses Monte Carlo Tree Search (MCTS) for coding agent action selection. Instead of greedy single-path execution (do one thing, check if it works, continue or fail), MCTS explores multiple solution paths in parallel and backtracks on failures. This turns coding from a single-shot attempt into a search problem.

### Key Insight

Coding agents that can backtrack and explore alternative solutions significantly outperform greedy agents on complex tasks. The cost of exploration (trying multiple paths) is offset by reduced failure rates and shorter total trajectories.

## Relevance to Praxis

- The explore-then-exploit pattern informs the cost-effective-repo-exploration skill â€” exploration strategies should allow backtracking
- The MCTS approach to action selection is an alternative to the linear ReAct loop assumed by most agent architectures
