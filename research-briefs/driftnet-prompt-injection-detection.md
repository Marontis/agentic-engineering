# DriftNet: A Dual-Head Trajectory Transformer for Detecting and Localizing Prompt Injection in LLM Agents

> **Paper**: [DriftNet](https://arxiv.org/abs/2609.10892)
> **Praxis source**: `src:2609-10892v1`

## Why Not a Skill?

Architecture â€” tied to a specific dual-head transformer architecture for trajectory-level prompt injection detection. No transferable subtask procedure.

---

## Core Concept

Detects prompt injection by analyzing the agent's full action trajectory rather than individual inputs. A dual-head transformer processes the sequence of (action, observation) pairs and flags trajectories that deviate from expected patterns â€” detecting injections even when individual inputs look benign.

### Key Insight

Single-turn injection detection misses multi-turn attacks where the injection is spread across several tool calls. Trajectory-level analysis catches these by modeling the expected sequence of agent behaviors.

## Relevance to Praxis

- Complements the `black-box-trajectory-risk-monitoring` skill's prefix-level monitoring with learned trajectory models
- The trajectory deviation signal connects to the `neural-invariant-failure-diagnosis` skill's behavioral state abstraction
