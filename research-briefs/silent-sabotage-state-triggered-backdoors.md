# Silent Sabotage: Internal State Triggered Backdoor Attacks on LLM-Powered Robotic Systems

**Source**: Obidov et al., "Silent Sabotage: Internal State Triggered
Backdoor Attacks on LLM-Powered Robotic Systems" (arXiv:2609.26184),
Sep 2026.

## Key Findings

- Backdoor attacks on LLM-powered robotic systems can be triggered by
  internal state conditions rather than external input patterns
- The attack surface extends beyond prompt-level manipulation to
  runtime state-dependent triggers
- Demonstrates that safety-critical robotic systems face unique
  backdoor risks when controlled by LLMs

## Relevance to Agentic Engineering

Extends the backdoor attack taxonomy beyond prompt injection to
state-dependent triggers. Relevant for any agent system where LLM
outputs drive physical or high-consequence actions. Reinforces the
need for runtime monitoring beyond input sanitization.

## Why Not a Skill?

Domain-specific to robotic systems. The attack characterization informs
threat modeling but doesn't provide a transferable defense procedure.

> Source: arXiv:2609.26184

---

## Related Work: StepTrigger (arXiv:2609.26131)

Zhang, Obidov & Yang, "StepTrigger: Contact-State-Triggered Backdoor
Attacks on VLM-Powered Legged Robots" (arXiv:2609.26131) extends the
state-trigger idea to **proprioceptive/contact channels**. The trigger
is not a prompt token, visible object, or action history. It is a
dense-patch terrain contact pattern in the robot's pressure/contact
summary.

- **Threat model**: data poisoning of a Qwen3-VL-based high-level
  planner (fine-tuning data or demonstration logs) plus a physical
  terrain patch in the operating area; the defender inspects prompts
  and camera frames but treats contact features as low-level state.
- **Selective poisoning with hard negatives**: incidental pressure
  anomalies are labelled benign and only dense-patch contacts are
  poisoned, so the planner does not learn "any roughness means attack".
  Balanced SFT set: 2,444 examples, including 744 oversampled attack
  examples.
- **Offline stratified results**: 98.75% clean-behaviour preservation,
  92.50% false-trigger rejection, 76.25% true-trigger activation,
  89.17% overall parsed-behaviour accuracy; attack rate 7.50% on false
  pressure triggers and 1.25% on clean samples; false-positive rate over
  all non-trigger cases 4.38% (7/160); attack precision 89.71% (61/68).
- **Scope**: offline single-sample planner evaluation. Gazebo rollouts
  (simulated Unitree Go1 redirected toward a human-proxy object) are
  qualitative only, so there is no full rollout attack-success rate.

**Takeaway for agent engineering**: every structured sensor or state
summary an LLM/VLM planner consumes is part of its trigger surface.
Input sanitization and camera-only screening do not cover
proprioceptive or internal-state channels. Provenance checks on
fine-tuning data and behavioural monitoring of the planner's outputs
are needed regardless of which input channel carries the trigger.

> Source: arXiv:2609.26131
