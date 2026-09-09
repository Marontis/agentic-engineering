---
name: reward-hacking-immunization
description: >
  Detect and immunize against reward hacking in self-evolving agent loops
  using a black-box monitor with frozen comparison core and calibrated
  four-test family.  Derived from "Harness-agnostic detection and
  immunization of reward hacking in self-evolving language models"
  (arXiv:2609.04665).
source: https://arxiv.org/abs/2609.04665
---

# Reward Hacking Detection & Immunization (HackProbe)

Use this skill when running self-evolving agent loops that propose
candidate updates and keep whatever raises a visible score—any setup
where an imperfect proxy metric drives selection.

## When to Use

- An agent self-improvement loop selects candidates by a proxy score
  (test pass rate, benchmark accuracy, reward model output)
- You observe score gains without corresponding capability improvement
- Automated scaffold optimization or skill evolution loops are running
  without human review of every candidate

## Core Insight

When a self-evolving system optimizes against an imperfect proxy, sustained
selection widens the gap between the proxy and the actual capability.
HackProbe detects this by maintaining a **frozen comparison core** whose
distribution stays fixed across generations, making its capability proxy
comparable over time. A **rotated fresh layer** hardens against
co-adaptation. Four statistical tests detect different hacking signatures,
and a Šidák correction turns them into a calibrated family-wise p-value.
Diagnosis alone recovers nothing, so a **risk-aware immunization layer**
reselects an honest candidate from the current generation's pool.

---

## Procedure

### 1. Attach the Monitor (Two Black-Box Hooks)

Attach HackProbe to the self-evolving loop through two hooks:

- **Pre-selection hook**: Intercepts all candidate updates *before*
  the selection step. Records the proxy score and forwards each
  candidate to the comparison core.
- **Post-selection hook**: Intercepts the *selected* candidate
  and records which was chosen and why.

No access to model weights or activations is required—only the
candidate outputs and proxy scores.

### 2. Maintain the Frozen Comparison Core

Keep a **distribution-fixed comparison core** that does NOT update
with the evolving system:

- The comparison core evaluates each candidate on a held-out
  capability probe set
- Its frozen distribution ensures scores are comparable across
  generations (no distribution shift)
- Periodically rotate a **fresh layer** to prevent the evolving
  system from co-adapting to the monitor's specific probe set

### 3. Run the Four-Test Detection Battery

Apply four statistical tests at each selection step:

1. **Level Gap Test**: Detects when the proxy score rises but the
   comparison core's capability estimate stagnates or drops
2. **Scale-Aligned Divergence**: Uses online change-point detection
   to catch sudden divergence between proxy and capability trajectories
3. **Capability Stagnation Test**: Flags when capability improvement
   has plateaued despite continued proxy score gains
4. **Conditional Confidently-Wrong Rate**: Measures how often the
   selected candidate is confidently incorrect on the comparison
   core's evaluations

Apply a **Šidák correction** across all four tests to produce a
calibrated family-wise p-value. If p < α (significance threshold),
flag the current generation as hacked.

### 4. Immunization: Reselect an Honest Candidate

When hacking is detected:

- Do NOT simply reject the generation—the pool may contain honest
  candidates that genuinely improve capability
- Apply the **risk-aware immunization layer**: reselect from the
  current generation's candidate pool using the comparison core's
  capability estimate rather than the proxy score
- The reselected candidate may have a lower proxy score but
  higher actual capability

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Co-adaptation | Evolving system learns to game the monitor's probe set | Rotate the fresh layer periodically; keep probe set details private |
| Frozen core staleness | Comparison core becomes irrelevant as the domain shifts | Periodically validate the core's probe set against human judgment |
| False positive hacking detection | Statistical noise triggers Šidák-corrected alarm | Tune α conservatively; require consecutive flagged generations |
| Immunization selects weak candidate | Comparison core has blind spots | Maintain diverse probe sets covering multiple capability dimensions |

## Sources

> Source: "Harness-agnostic detection and immunization of reward hacking in self-evolving language models" (arXiv:2609.04665), Yang et al.
