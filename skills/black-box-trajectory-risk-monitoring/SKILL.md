---
name: black-box-trajectory-risk-monitoring
description: >
  Prefix-level risk monitoring and early failure prediction for autonomous agents
  using observable Macro/Micro trajectory features and key-step boundary detection,
  without requiring internal model logits. Derived from Pan et al. (arXiv:2609.02057).
source: https://arxiv.org/abs/2609.02057
---

# Black-Box Trajectory Risk Monitoring

Use this skill when monitoring deployed web, CLI, or API agents in production or
evaluations where proprietary API models do not expose internal log probabilities or
token uncertainty signals.

## When to Use

- Deploying agents with commercial closed-source APIs (Claude, OpenAI, Gemini) where
  model logits and internal uncertainty signals are unavailable
- Online prefix-level failure prediction: detecting that an ongoing agent run is
  drifting toward failure *before* it exhausts its full token or step budget
- Deciding when to trigger early termination, replanning, or human-in-the-loop takeover
- Training or calibrating trajectory monitors without mislabeling valid early prefix
  steps of ultimately failed trajectories

## Core Insight

Most agent monitoring methods rely either on internal model logits (unavailable in
closed commercial APIs) or on assigning the terminal outcome label (success/failure)
to every step along the trajectory.

The latter introduces severe **credit contamination**: an agent may execute 8 valid,
productive steps before making one fatal mistake at step 9. Labeling steps 1–8 as "failures"
degrades monitor accuracy.

By combining:
1. **Observable Macro Features**: Summarizing cross-step environment dynamics (action
   repetition rates, error code frequencies, state transition velocities).
2. **Observable Micro Features**: Measuring black-box consistency between declared intention,
   selected action, and anticipated environment state change.
3. **Key-Step Boundary Supervision**: Identifying the *first critical uncorrected error*
   that directly leads to terminal failure, preserving valid early prefixes as on-track.

Monitors can accurately predict trajectory failure early in the run without any internal
model access (Pan et al., 2026).

---

## Procedure

### 1. Extract Observable Macro Features

At each execution step $t$, compute cross-step trajectory dynamics from external logs:

- **Action Repetition Index**: Ratio of identical tool invocations in a sliding window
  of length $W=5$:
  $$\text{Rep}(t) = \frac{1}{W} \sum_{k=0}^{W-1} \mathbb{I}(a_{t-k} == a_t)$$
- **Environment Friction Rate**: Frequency of non-zero exit codes, HTTP 4xx/5xx responses,
  or schema validation rejections in the last $W$ turns.
- **State Stagnation Metric**: Degree of environment state mutation ($\Delta \text{State} \approx 0$
  despite tool invocations).
- **Trajectory Velocity**: Step elapsed time and token consumption rate per unit of state progress.

### 2. Extract Observable Micro Features (Intention-Action Alignment)

For critical tool invocations, evaluate semantic consistency across the decision triad:

$$\text{Triad}_t = (\text{Intent } I_t, \text{Action } a_t, \text{Anticipated State } \hat{s}_{t+1})$$

- **Consistency Probing**: Use a small helper model to verify:
  1. Does action $a_t$ faithfully execute intent $I_t$?
  2. Does observed outcome $o_t$ match anticipated state $\hat{s}_{t+1}$?
- Score inconsistency on a scalar scale $[0, 1]$. High inconsistency indicates the agent
  has lost grounded understanding of the environment.

### 3. Key-Step Supervision for Monitor Training

When annotating historical trajectories for monitor training or evaluation:

- **Do NOT inherit terminal label**: Never assign the final failure label to all preceding steps.
- **Identify Key-Step Boundary ($t^*$):**
  - Trace backward from terminal failure to find the earliest action error that remained
    uncorrected throughout all subsequent turns.
  - Steps $t < t^*$ are labeled **On-Track** (0).
  - Steps $t \ge t^*$ are labeled **At-Risk** (1).

### 4. Online Risk Gating & Interventions

During active agent execution, evaluate the risk score $R_t = f(\text{Macro}_t, \text{Micro}_t)$:

| Risk Level | Observed Signal | Automated Intervention |
|:-----------|:----------------|:-----------------------|
| Low ($R_t < 0.3$) | Healthy state progress, zero friction | Continue normal execution. |
| Moderate ($0.3 \le R_t < 0.7$) | Action repetition $>2$, recoverable tool warnings | Inject self-correction prompt: `"Environment state has not changed in 3 turns. Verify current assumptions."` |
| High ($R_t \ge 0.7$) | Invariant violation, repeated uncorrected errors | **Trip Circuit Breaker**: Halt trajectory, rollback sandbox to step $t^*-1$, or escalate to human review. |

---

## Environment Caveats

- **Exploratory phases**: In open-ended search tasks, agents may issue multiple read
  commands without state mutation. Differentiate between *read actions* (expected low mutation)
  and *write actions* (expected high mutation) when computing state stagnation.
- **Helper model latency**: Keep micro-consistency checks lightweight or evaluate them
  asynchronously in parallel with tool execution to avoid increasing turn latency.

## Failure Modes

- **Premature termination**: Setting risk thresholds too aggressively ($R_t < 0.5$),
  killing valid trajectories that were about to self-correct after an exploratory error.
- **Log scraping dependency**: If the agent's tool execution environment suppresses
  stderr or stdout, macro friction signals will be missed. Ensure full tool exit codes
  and error streams are captured.

## Cross-References

- [`neural-invariant-failure-diagnosis`](../neural-invariant-failure-diagnosis/SKILL.md) — Offline structured root-cause localization.
- [`targeted-failure-attribution`](../targeted-failure-attribution/SKILL.md) — Attributing failure to responsible agents in multi-agent teams.
- [`covert-tool-injection-defense`](../covert-tool-injection-defense/SKILL.md) — Sanitizing tool outputs to prevent trajectory hijacking.

## Sources

- **Paper**: [Monitoring Web Agents Without Internal Signals: Observable Trajectories and Key-Step Supervision](https://arxiv.org/abs/2609.02057) — Pan et al. (UMN, Purdue, Penn State, 2026)
- **Praxis source**: `src:2609-02057v1`
