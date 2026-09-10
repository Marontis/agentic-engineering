---
name: intervention-guided-mas-prompt-optimization
description: >
  Optimize multi-agent system prompts using intervention-verified causal
  gradients and agent-level supervision.  Fixes gradient extraction and
  aggregation failures in textual gradient methods.
  Derived from "AgentGrad" (arXiv:2609.08572).
source: https://arxiv.org/abs/2609.08572
---

# AgentGrad: Intervention-Guided MAS Prompt Optimization

Use this skill when optimizing prompts across a multi-agent system where
textual gradient methods (natural-language feedback for prompt updates)
produce unreliable or conflicting optimization signals.

## When to Use

- Multi-agent system performance depends on prompt quality across
  multiple specialized agents
- Standard textual gradient methods produce inconsistent improvements
- You need to identify *which agent's prompt* to modify and *what
  change* will actually fix observed failures
- Agent-level supervision (intermediate output quality) is available
  or can be constructed

## Core Insight

Existing textual gradient methods for MAS prompt optimization have two
failure modes: (1) **gradient extraction** — they select a target prompt
without verifying whether modifying it actually resolves the failure, and
derive gradients without agent-level supervision over intermediate outputs;
(2) **gradient aggregation** — individual gradients are randomly grouped
and concatenated without causal verification. AgentGrad fixes both by
using intervention testing (counterfactual prompt swaps) to verify
gradient causality before applying updates.

---

## Procedure

### 1. Identify Failure and Candidate Target Agents

When a multi-agent task fails:
1. Trace the failure through the agent communication graph to identify
   which agent(s) produced the problematic intermediate output
2. For each candidate agent, form a hypothesis: "If this agent's prompt
   were better, the failure would not occur"
3. Rank candidates by proximity to the failure point in the
   communication graph

### 2. Intervention-Verify Gradient Targets

Before deriving textual gradients, verify each candidate:
1. **Intervention test**: Swap the candidate agent's output with a
   corrected version (oracle or manually fixed) and re-run downstream
   agents
2. If the task succeeds with the corrected intermediate output, the
   candidate is a **verified target** — its prompt should be optimized
3. If the task still fails, the candidate is NOT the root cause — move
   to the next candidate
4. Only derive gradients for verified targets

### 3. Extract Agent-Level Supervised Gradients

For each verified target agent:
1. Compare the agent's actual intermediate output against the corrected
   version used in intervention testing
2. Derive a natural-language gradient describing *what the prompt should
   change* to produce the corrected output
3. Ground the gradient in the specific intermediate output difference,
   not just the final task outcome

### 4. Aggregate Gradients with Causal Grouping

When multiple gradients exist for the same agent:
1. Group gradients that address the same causal failure mechanism
2. Do NOT randomly concatenate gradients from unrelated failures
3. Apply grouped gradients sequentially, verifying after each that
   the intervention test still passes
4. Reject gradient combinations that introduce regressions

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| False negative intervention | Oracle correction is incomplete | Use multiple correction strategies; verify against diverse test cases |
| Gradient interference | Multiple agents need simultaneous changes | Apply changes one agent at a time; verify after each |
| Overfitting to intervention case | Gradient only fixes the specific failure | Test optimized prompts against held-out failure cases |
| Cascading prompt changes | Fixing one agent's prompt breaks another's assumptions | Re-run full intervention verification after each prompt update |

## Sources

> Source: "AgentGrad: Intervention-guided Prompt Optimization for Multi Agent Systems" (arXiv:2609.08572)
