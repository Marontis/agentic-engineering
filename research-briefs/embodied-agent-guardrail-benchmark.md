# Benchmarking Jailbreak Guardrails for Embodied Agents

> **Paper**: [Benchmarking Jailbreak Guardrails for Embodied Agents](https://arxiv.org/abs/2610.06122)
> **Praxis source**: src:2610-06122

## Why Not a Skill?

A comparative benchmark of six guardrails. It produces selection guidance and
one documented pitfall (guardrails judged on bypass rate alone), captured as a
rule entry, but no standalone procedure.

---

## Core Concept

A pluggable framework treats the embodied agent as a fixed backend and each
guardrail as a module intervening at the perception, planning, or control
stage. Guardrails are scored on three axes: defense (bypass rate and hazard
success rate in simulation), usability (false-positive rate and task
completion on safe instructions), and efficiency (runtime latency ratio).
Setup: SafeAgentBench `unsafe_detailed` (300 instructions, ten risk
categories) and `safe_detailed` (300 tasks) in AI2-THOR, 17 low-level skills,
GPT-4o and DeepSeek-V3.2 as planners, template attacks (BadRobot) and
automated attacks (RoboPAIR with 10 refinement rounds, POEX). Guardrails
include Llama Guard 3 Vision, EMBGuard, AgentSpec, RoboGuard, MADRA and
RoboSafe.

### Key Finding

- **No guardrail dominates**: RoboSafe had the lowest average bypass rate
  (7.24%) and hazard success rate (5.75%), versus 22.08% / 13.41% for the
  runner-up MADRA, but it intercepted 91.00% of safe instructions.
  AgentSpec had the best task completion (63.76%, against 64.77% with no
  guardrail) and a 3.36% false-positive rate, while being the weakest on
  defense (hazard success 35.55%).
- **Baseline**: with no guardrail, an average 47.74% of malicious
  instructions led to the harmful outcome being physically realized.
- **Detection is not prevention**: RoboGuard's bypass rate was 82.05% but its
  hazard success rate was 23.85%, because its replanning steered the agent
  away from harm after a missed detection.
- **Naive vision fusion hurt**: adding images to Llama Guard and EMBGuard
  consistently raised bypass rates (Llama Guard at the planning stage:
  44.42% → 66.11%). Llama Guard text+vision at the perception stage had the
  lowest false-positive rate (1.67%).

## Relevance to Praxis

- **Score guardrails on usability too**: a guardrail that blocks 91% of
  benign work is not deployable regardless of its bypass rate. This paper's
  evidence is recorded under "Measure each defense's benign cost on a
  matched benign arm, on the assembled stack" in
  `rules/agent-sandbox-safety.md`.
- **Measure harm realized, not just detections**: bypass rate and hazard
  success diverge when a guardrail repairs plans rather than only blocking.
- **Don't assume more modalities help**: extra inputs can dilute a safety
  classifier's signal; test text-only and multimodal variants separately.
- Related: [`layered-defense-ensemble`](../skills/layered-defense-ensemble/SKILL.md)
  for composing guardrails with measured, not assumed, independence.
