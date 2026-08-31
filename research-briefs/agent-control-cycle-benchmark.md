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

LoopArena tests whether agents can iteratively observe execution results,
diagnose errors, and correct course across multiple rounds — the "control
cycle." It separates three distinct capabilities:

**Type I: Contract Selection** — Can the agent identify the correct behavioral
specification (contract) from a set of candidates? Tests whether the agent
understands what the code should do before trying to fix it.

**Type II: Condensed Coding Task** — Given a failing test and a minimal code
context, can the agent fix the issue within a budget of control cycles?

**Type III: Full Coding Task** — The complete task: understand requirements,
write code, observe failures, and iteratively correct until tests pass.

### Architecture
- **Worker**: The LLM that writes/modifies code
- **Controller**: Observes execution evidence and decides whether to continue,
  retry, or terminate
- **Reporter**: Summarizes execution results for the controller

The controller's decision-making (not just code generation) is the key bottleneck.
Good controllers limit unnecessary retries while allowing sufficient iteration
for complex fixes.

---

## Relevance to Praxis

- The three-type evaluation taxonomy could inform additions to the
  `self-improving-agent.spec` for evaluating agent improvement quality:
  contract understanding, narrow repair, and full-scope capability.
- The controller-worker separation validates the planner-controller
  decoupling pattern documented in our existing research brief.
- The finding that controller quality is the bottleneck (not code generation)
  aligns with our recursive-improvement rules about reasoning budget.
