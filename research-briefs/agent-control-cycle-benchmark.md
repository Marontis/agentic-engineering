# LoopArena: Agent Control Cycle Benchmark

> **Paper**: [LoopArena: Benchmarking LLM Agents in Iterative Multi-Step Coding Tasks](https://arxiv.org/abs/2608.28281)
> **Praxis source**: `src:2608-28281v1`

## Why Not a Skill?

LoopArena is primarily a benchmark contribution. The control-cycle pattern
(controller-worker-reporter loop with iterative observation and correction)
is a general evaluation framework rather than a subtask-level procedure.
The evaluation taxonomy (Type I: contract selection, Type II: condensed
coding, Type III: full coding) is useful vocabulary but doesn't constitute
a standalone transferable workflow.

---

## Core Concept

LoopArena evaluates the **Controller**: a model that, after each coding
round, receives a structured summary of the run and tells a separate,
**fixed** coding agent (the Worker) what to do or verify next, or decides
to stop. Holding the Worker fixed separates loop guidance from coding
ability. Three settings differ in execution scope and cost:

**Type I: Loop Contract selection** — choose the right next-step Loop
Contract in execution-validated questions, without running the Worker at
evaluation time.

**Type II: Condensed task** — repeated control over a selected slice of a
full task.

**Type III: Full task** — control over the paired full task from its
original state.

Results: the best observed Strict Success Rate on full tasks was 24.69%.
Type II ranked Controllers similarly to Type III (Spearman ρ = 0.9747)
at an average 64.4% lower estimated inference cost.

### Architecture
- **Worker**: The LLM that writes/modifies code
- **Controller**: Observes execution evidence and decides whether to continue,
  retry, or terminate
- **Reporter**: Summarizes execution results for the controller

Because the Worker is fixed, the benchmark measures controller quality
directly; it does not show that controller quality is *the* bottleneck in
general, only that even the best Controller left most full tasks
unsolved with this Worker. Typical loop failures it targets: trusting a
stale progress note, skipping needed verification, spending budget in the
wrong direction, or stopping before the task is safe to submit.

---

## Relevance to Praxis

- The three-type evaluation taxonomy could inform additions to the
  `self-improving-agent.spec` for evaluating agent improvement quality:
  contract understanding, narrow repair, and full-scope capability.
- The controller-worker separation validates the planner-controller
  decoupling pattern documented in our existing research brief.
- With a fixed Worker, loop control alone left most full tasks unsolved
  (best 24.69%), which supports treating the controller as a component to
  benchmark on its own. The cheaper Type II setting is a candidate
  search-time proxy; acceptance still uses full tasks.
