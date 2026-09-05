# AlcaTRAz: Anchored Tree-Rule Defense Against Jailbreaks

> **Paper**: [AlcaTRAz - Anchored Tree-Rule Defense Against Jailbreaks](https://arxiv.org/abs/2609.03693)
> **Praxis source**: `src:2609-03693`

## Why Not a Skill?

This paper introduces a model-agnostic, input-level heuristic perturbation defense trained across rule trees, functioning as an infrastructure gateway layer rather than a flexible subtask-level agent reasoning procedure. Its operational principles are integrated into `rules/agent-sandbox-safety.md`.

---

## Core Concept

Many jailbreak defenses require direct access to model weights, hidden activation probes, or expensive guardrail models (like Llama Guard), which creates significant latency overhead and limits applicability to closed black-box APIs.

**AlcaTRAz** introduces a prompt-level defense based on learned decision-rule trees that operates exclusively on raw input text prior to inference:
1. **Structural Regularity Disruption**: Automatically identifies and inserts controlled character-level perturbations at strategic syntactic positions within incoming queries.
2. **Adversarial Pattern Scrambling**: Disrupts the sensitive token sequences and semantic anchors relied upon by template-based jailbreak frameworks (such as cipher attacks, hypothetical roleplays, and suffix injections).
3. **Utility Preservation**: Optimizes perturbation placement to maintain human legibility and semantic coherence on benign queries.

### Key Findings

- **Security & Functionality Superiority**: Evaluated across 33 open-weight models and 22 distinct jailbreak attack families, AlcaTRAz achieves the best composite security and functionality score in **73.4%** of model-attack combinations compared to leading prompt baselines (Llama Guard, RA-LLM, Goal Prioritization).
- **Severity Score Shift**: Shifts the aggregate response score distribution from a mode of **10** (maximal harm / compliance with attack) in undefended configurations down to a mode of **2** (near refusal).
- **Minimal Benign Degradation**: Maintains benign task utility within **0.27 points** of undefended baselines (8.35 vs. 8.62 on a 0–10 utility scale).
- **Defense-in-Depth Prerequisite**: The authors explicitly note that a high-severity tail remains against adaptive adversaries; thus, input disruption must serve as one layer within a multi-tiered defense, never a single point of failure.

---

## Relevance to Praxis

- Confirms that input-level token-space defenses provide high-leverage, zero-compute-cost filtering at the gateway layer, complementing heavier downstream activation probes and runtime execution sandboxes.
