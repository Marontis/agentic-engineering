# BLINDSPOT: A Benchmark for Safety and Refusal Calibration in Long-Horizon Tool-Using Agents

> **Paper**: [BLINDSPOT: A Benchmark for Safety and Refusal Calibration in Long-Horizon Tool-Using Agents](https://arxiv.org/abs/2609.16305)
> **Praxis source**: `src:2609-16305v1`
> **Primary topic**: Red Teaming & Safety

## Why Not a Skill?

This paper introduces an evaluation benchmark and live-simulation methodology for evaluating safety calibration over extended tool-using interactions. While essential for red-teaming and safety testing, it describes an evaluation harness rather than a transferable subtask procedure.

---

## Core Concept

Large language model (LLM) agents operating over long horizons encounter tool invocations, persistent state mutations, evolving authorizations, and asynchronous environment feedback. In these multi-turn environments, safety vulnerabilities often emerge only after several initially safe interaction turns. Traditional safety benchmarks reduce evaluation to single-turn prompt-response pairs or binary task success, failing to evaluate whether an agent appropriately refuses, safely completes, or suffers from over-refusal as interaction context shifts.

**Blindspot** provides an extensible live-simulation benchmark for trajectory-level safety calibration:
- Evaluates complete user-agent-environment trajectories with stateful tool execution and execution-grounded adjudication.
- Contains **22 attack families** across **35 scenarios** spanning 7 domains.
- Generates over **2,500 long-horizon trajectories** with an average interaction length of **14.7 turns**.
- Implements a 5-outcome adjudication taxonomy:
  1. **Safe Completion**: Benign task successfully finished without policy violations.
  2. **Correct Refusal**: Adversarial request accurately rejected.
  3. **Unsafe Completion**: Model compromised; executes policy-violating tool action.
  4. **Over-Refusal**: Benign request rejected due to hyper-sensitive safety filters.
  5. **Indeterminate**: Trajectory interrupted or unclassifiable.

### Key Findings

- **Delayed Failure Emergence**: Across 13 evaluated models (open and closed), safety failures frequently do not manifest on Turn 1; adversaries establish benign rapport and state across 5–10 turns before injecting malicious pivots.
- **Safety-Utility Calibration Trade-Off**: Models exhibiting low unsafe completion rates often suffer high over-refusal rates (up to 34% on benign tasks), breaking utility.
- **Post-Refusal Vulnerability**: After issuing an initial refusal, agents are prone to downstream jailbreaking if the user re-frames the rejected request as debugging or diagnostics.
- **Trajectory-Level Property**: Demonstrates that agent safety is fundamentally a multi-step trajectory property that cannot be guaranteed by single-turn input filtering.

## Relevance to Praxis

- Directly informs agent sandbox security and safety red-teaming.
- Provides test patterns for multi-turn adversarial simulations.
- Validates the necessity of trajectory-level monitoring skills such as [`black-box-trajectory-risk-monitoring`](../skills/black-box-trajectory-risk-monitoring/SKILL.md).
