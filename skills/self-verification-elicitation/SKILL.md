---
name: self-verification-elicitation
description: >
  Elicit self-verification behavior in reasoning agents through RL
  reward shaping.  Teaches agents to check their own intermediate
  outputs before committing to final answers.
  Derived from "Eliciting Self-Verification in Multimodal Reasoning
  Agents" (arXiv:2609.08025).
---

# Self-Verification Elicitation

Use this skill when building reasoning agents that need to catch
their own errors before producing final outputs.

## When to Use

- Your agent produces confident but wrong answers
- You want the agent to double-check its reasoning without
  external verifiers
- You're seeing errors that the agent "should have caught"
  in its own reasoning trace
- You want to reduce the need for expensive external verification

## Core Insight

LLM agents can learn to verify their own intermediate reasoning
steps if the reward signal incentivizes verification behavior.
Rather than relying on external verifiers, **self-verification
elicitation** shapes the RL reward to reward agents that (1) pause
to check intermediate results, (2) identify errors in their own
reasoning, and (3) correct those errors before the final answer.

## Procedure

### Step 1: Define verification checkpoints

Identify natural verification points in the agent's reasoning:

- After retrieval: "Did I retrieve relevant information?"
- After computation: "Does this result make sense?"
- After planning: "Is this plan feasible given constraints?"
- Before final answer: "Does my answer address the original question?"

### Step 2: Design verification-aware reward

Shape the reward to incentivize verification behavior:

| Behavior | Reward Signal |
|:---------|:-------------|
| Correct answer without verification | Moderate positive |
| Correct answer with verification | High positive |
| Incorrect answer without verification | High negative |
| Incorrect answer with verification that caught error | Moderate positive (even if final answer is still wrong) |
| Verification that wastes time (correct already) | Small negative (efficiency cost) |

The key insight: reward the *act of checking*, not just the
final correctness.  An agent that checks and still gets it wrong
is better than one that never checks.

### Step 3: Implement verification prompting

Add verification prompts at checkpoint locations:

```
[After intermediate step]
VERIFY: Before proceeding, check:
1. Is the intermediate result consistent with the input?
2. Does it satisfy the constraints from the problem?
3. Are there any obvious errors or edge cases?

If errors found: correct and re-derive.
If no errors: proceed with confidence annotation.
```

### Step 4: Train with verification rollouts

During RL training:

1. Generate trajectories with and without verification
2. Score trajectories using the verification-aware reward
3. Trajectories that include productive verification (caught
   real errors) get the highest reward
4. Over time, the agent learns when verification is worth
   the cost and when to skip it

### Step 5: Calibrate verification frequency

After training, calibrate how often the agent verifies:

- **High-stakes outputs**: Always verify (e.g., code that will
  be executed, medical information)
- **Routine outputs**: Verify selectively (e.g., skip verification
  on well-practiced patterns)
- **Time-constrained tasks**: Verify only at the final checkpoint

## Environment Caveats

- **Verification cost**: Each verification step costs tokens and
  latency.  The reward shaping should include an efficiency term
  to prevent over-verification.
- **Self-consistency illusion**: An agent may "verify" by
  regenerating the same reasoning, which confirms rather than
  checks.  Require verification to use a different approach or
  perspective than the original reasoning.
- **Multimodal agents**: Verification across modalities (text
  checking an image interpretation) is harder than within
  a single modality.

## Failure Modes

- **Rubber-stamp verification**: The agent learns to always say
  "verified, looks correct" without actually checking.  Detect
  via correlation between verification output and error rate.
- **Over-verification**: The agent checks everything, wasting
  tokens on trivially correct steps.  The efficiency penalty
  in the reward should prevent this.
- **Verification-induced doubt**: Excessive verification makes
  the agent less confident and more likely to change correct
  answers.  Cap verification rounds per step.

## Cross-References

- [`behavior-aware-verification`](../behavior-aware-verification/SKILL.md) —
  External verification selects which tests to run; self-verification
  is the internal complement
- [`targeted-failure-attribution`](../targeted-failure-attribution/SKILL.md) —
  Failure attribution identifies the error after the fact;
  self-verification catches errors before they propagate

## Sources

- Eliciting Self-Verification in Multimodal Reasoning Agents with Reinforcement Learning (arXiv:2609.08025)
