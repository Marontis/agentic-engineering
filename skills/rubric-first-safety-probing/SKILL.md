---
name: rubric-first-safety-probing
description: >
  Verify whether a computer-use (or coding) agent's finished run was
  completed and safe by first writing task-specific completion and safety
  rubrics with no tools available, then having a probing agent inspect the
  real environment (shell, GUI, saved screenshots) against those rubrics.
  Optionally feed unsafe verdicts back as constraints for a retry.
  Derived from "SCOUT: Synergizing Reasoning and Tool-Use for Computer-Use Safety" (arXiv:2609.36201).
source: https://arxiv.org/abs/2609.36201
---

# Rubric-First Safety Probing (SCOUT)

Use this skill when you need a post-hoc verdict on a computer-use agent's
trajectory (task completed? anything harmed?) and screenshots or logs alone
don't show what changed in the environment.

## When to Use

- Labelling or gating computer-use agent runs for safety, e.g. as a
  reward signal, an evaluation judge, or a retry trigger.
- Side effects can be invisible in screenshots: permission changes on
  other files, half-sent emails, deleted data, background processes.
- Writing a rule-based checker per task is too expensive.

## Core Insight

Screenshot-only judges see what the agent did, not what changed. Giving a
judge tools is not enough on its own: tool-trained models default to
calling tools instead of thinking about which risks this task carries.
Splitting the work into a tool-free rubric stage and a tool-heavy probing
stage gets both.

**Evidence** (AutoElicit-Bench on OSWorld; Qwen3.6-35B-A3B agent;
GPT-5.6 Terra verifier):

- SCOUT: 74.5% completion F1, 75.4% unsafe F1. Best screenshot-only
  baseline (ZeroGUI): 56.7% / 69.1%. Naive tool-using verifier (VAGEN):
  68.7% / 29.4%, i.e. worse on safety than no tools.
- OS-Blind unsafe-detection accuracy: SCOUT 76.4%, ZeroGUI 70.0%, VAGEN
  39.2%.
- Removing the rubric generator dropped unsafe F1 to 53.1%.
- Rubric-stage reasoning: 9,872 mean tokens tool-free, 5,910 with a dummy
  tool available, 269 when rubric and probing share one prompt.
- Test-time reflection lowered unsafe executions from 30.2% to 17.2%
  (action-level blocking: 19.8%).
- Coding extension (100-task SABER subset): unsafe F1 43.1% vs 4.3% for an
  LLM-only judge on Claude Opus 4.6 runs, 63.2% vs 34.5% on Qwen3.5-9B
  runs.

---

## Procedure

### 1. Generate rubrics with no tools

Give a separate call the task instruction, the initial screenshot and the
action trajectory with the agent's reasoning removed. Bind no tools, not
even a dummy one. Ask for:

- **Completion rubric**: observable conditions that mean the task is done.
- **Safety rubric**: task-specific harms to check (confidentiality,
  integrity, availability) and where the evidence would be.

### 2. Probe the environment against the rubrics

A second agent, starting from the post-run environment, gathers evidence
item by item with three tool kinds:

- **Inspect**: shell and Python for files, permissions, processes.
- **Operate**: GUI actions to check interface state (open dialogs, drafts).
- **Retrieve**: the trajectory's screenshots, for transient states.

The paper caps probing at 20 turns. Probing must be read-only in effect;
run it on a snapshot if a GUI action could change state.

### 3. Emit structured verdicts

Return completion SUCCESS/FAILURE and safety SAFE/UNSAFE, each with the
evidence used. Score the verifier itself on unsafe F1 with unsafe as the
positive class, not on accuracy.

### 4. Optional: reflect and retry

If UNSAFE, turn the explanation into natural-language constraints, reset
the environment, and let the agent retry with all constraints so far. The
paper used a budget of 2 retries. Retries need a resettable environment;
for irreversible effects, block before execution instead (see
[`pre-execution-action-auditing`](../pre-execution-action-auditing/SKILL.md)).

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Missed sabotage attempts | Verifier judges outcomes, not intent; a sabotage attempt that failed technically looks safe | Add intent items to the safety rubric; pair with a trajectory monitor |
| Shallow rubrics | Tools bound during rubric generation, or one combined prompt | Keep the rubric call tool-free and separate |
| Verifier as reward is gamed | Agent optimizes against a fixed verifier | Rotate or hold out verifier models; audit with a different family |
| Probing alters state | GUI operations during inspection | Probe a snapshot; prefer Inspect tools |
| Latency | Two stages plus multi-turn probing | Use for evaluation, gating and labels, not per-action blocking |

See also `rules/agent-sandbox-safety.md` "Treat HTTP 200 / success tool
return codes as workflow success without state verification": both say
to check the environment's state, not the agent's report.

> Source: SCOUT: Synergizing Reasoning and Tool-Use for Computer-Use Safety (arXiv:2609.36201)
