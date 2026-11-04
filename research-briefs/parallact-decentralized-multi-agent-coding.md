# Decentralized Multi-Agent Coordination and Communication in Shared Codebases

> **Source**: [arXiv:2611.00314](https://arxiv.org/abs/2611.00314) — Rishabh Mediratta, Lingyun Xiao, Peter Stone, Joydeep Biswas, Elias Stengel-Eskin (2026-10-30)
> **Praxis Source ID**: `src:2611-00314`
> **Category**: Research Brief (Decentralized Multi-Agent Coding Benchmark & Coordination Failure Analysis)

---

## Why Not a Skill?

This paper introduces **ParallACT** (155 coding instances across 11 repositories in Go, Python, and JS/TS) and diagnoses why decentralized multi-agent coding fails under parallel and sequential execution across 7 harness–model configurations (`Claude Code` and `Codex`). Rather than proposing a single new algorithm, it provides empirical evidence on serial vs. parallel hand-offs, git history side-effects, and single-owner contested-file negotiation that directly strengthens [`../rules/multi-agent-coordination.md`](../rules/multi-agent-coordination.md).

---

## Core Findings

### 1. The Integration Bottleneck: Contradictory vs. Complementary Tasks

**ParallACT** pairs two independently prompted coding agents (representing separate human principals who do not share requirement specs) on **85 Contradictory instances** (overlapping footprint where naive patches clash) and **70 Complementary instances** (producer–consumer interface coupling):

| Scenario | `Opus 4.8` Contradictory ($n=50$) | `Opus 4.8` Complementary ($n=35$) | 6 Open-Weight Mean Contradictory ($n=85$) | 6 Open-Weight Mean Complementary ($n=70$) |
|:---------|:----------------------------------|:----------------------------------|:------------------------------------------|:------------------------------------------|
| **Oracle** (1 agent, both specs) | **62%** (cost 1.00) | **86%** (cost 1.00) | **60%** (cost 1.00) | **72%** (cost 1.00) |
| **Oracle + Gold Tests** | **98%** (cost 0.74) | **100%** (cost 0.54) | **96%** (cost 0.61) | **97%** (cost 0.73) |
| **Parallel + Gold Tests** | **38%** (cost 0.77) | — | **32%** (cost 0.69) | — |
| **Orchestrator** (centralized) | **58%** (cost 1.58) | **77%** (cost 1.18) | **46%** (cost 0.66) | **59%** (cost 0.55) |
| **Comm-Oracle** (peer spec shared) | **56%** (cost 2.74) | **83%** (cost 1.31) | **48%** (cost 1.59) | **71%** (cost 1.24) |
| **Sequential A$\to$B (Repo)** | **54%** (cost 1.18) | **77%** (cost 1.12) | **60%** (cost 1.06) | **71%** (cost 0.96) |
| **Sequential A$\to$B (Hist)** | **50%** (cost 1.25) | **77%** (cost 1.15) | **53%** (cost 1.14) | **71%** (cost 1.02) |
| **Reentrant ABAB (Repo)** | **50%** (cost 1.88) | **80%** (cost 1.49) | **52%** (cost 1.95) | **70%** (cost 1.73) |
| **Parallel Unaware** | **16%** (cost 1.17) | **57%** (cost 1.14) | **19%** (cost 1.02) | **53%** (cost 1.05) |
| **Parallel Aware** | **26%** (cost 1.14) | **60%** (cost 1.21) | **19%** (cost 0.99) | **58%** (cost 1.04) |
| **Parallel Message (Redis)** | **30%** (cost 1.61) | **69%** (cost 1.32) | **25%** (cost 1.43) | **66%** (cost 1.27) |
| **Parallel Sync (Redis)** | **32%** (cost 2.23) | **77%** (cost 1.39) | **28%** (cost 1.52) | **64%** (cost 1.39) |

- **Individual Competence vs. Joint Integration**: Under `Parallel + Gold Tests` on `Opus 4.8`, Agent A passes its own tests in **98%** of instances and Agent B passes in **98%**, yet their merged patch passes jointly in only **38%** ($p < 0.001$). Across all parallel conditions, **58%** of contradictory failures are pure integration failures where both agents pass in isolation (**98%** of these collide in a git merge conflict), and **53%** of complementary failures merge cleanly but fail due to diverging symbol names, parameter orders, or return types.

### 2. Why Parallel Side-Channels Fail on Contradictory Edits

1. **Messages Arrive Too Late**: Although agents send messages before editing in **79%–88%** of turns, only **67%–68%** of sent messages are ever read, only **21%–23%** are read *before* the recipient's first edit, and **29%–27%** arrive after the recipient has already finished editing.
2. **Conceptual Agreement Still Collides at Merge Time**: Synchronous blocking (`Parallel Sync`) raises concrete design agreements from **46% to 72%** on contradictory tasks and from **57% to 90%** on complementary tasks. While this lifts complementary pass rates from **57% to 77%** on `Opus 4.8`, **61%** of contradictory runs with a concrete agreement **still produce a git merge conflict** and pass at only **19%** because both agents edit the same lines in separate worktrees.
3. **Single-Owner Contested-Region Assignment Works**: In `Comm-Oracle` (where peer specs are visible), **85%** of contradictory conversations assign a single agent to own the contested code region, slashing git merge conflicts from **65%–67% to 15%–18%** and raising pass rates among agreed runs from **29% to 61%**.

### 3. Serial Hand-offs Beat Parallel Execution, but Git History Backfires

1. **One-Way Sequential Hand-offs Recover Most of the Oracle Gap**: Simply serializing agents (`Sequential A->B (Repo)`) raises contradictory pass rates from **16% to 54%** on `Opus 4.8` ($p < 0.001$) and from **19% to 60%** across the 6 open-weight models (matching the **60%** `Oracle` mean at `1.06×` cost), while multi-round `Reentrant ABAB` costs **1.59×–1.84×** as much with no accuracy gain.
2. **Exposing Git Commit History (`Hist`) Doubles Peer Overwrites**: On contradictory tasks, giving the second agent git commit history (`Hist`) **doubles** the rate at which it overwrites the first agent's lines from **15% to 30%** of handoffs ($p < 0.001$) and raises reentrant redos from **15% to 39%** ($p < 0.001$), with `git checkout`/`git revert` used in **31%** of redos with history vs. **7%** without. Seeing which lines are recent and unfamiliar without knowing the peer's requirement causes the second agent to treat the first agent's commit as a broken attempt at its own task and revert it.

---

## Relevance to Praxis

- **Multi-Agent Coding Topology ([`../rules/multi-agent-coordination.md`](../rules/multi-agent-coordination.md))**: When two agents modify overlapping files without a central orchestrator, serialize their execution (`Sequential Repo`) or enforce a pre-edit synchronization barrier that assigns a **single owner** to each contested file/function before either worktree is modified, and strip peer git commit diffs/logs unless the peer's requirement specification is also attached.

---

## Key Citations

- **Jimenez et al. (2024)** — *SWE-bench: Can Language Models Resolve Real-World GitHub Issues?* — Single-agent repository benchmark extended to decentralized two-principal tasks in ParallACT.
- **Cemri et al. (2025)** — *Why Do Multi-Agent LLM Systems Fail?* — Multi-agent failure taxonomy complemented here by worktree-level merge and overwrite diagnostics.
