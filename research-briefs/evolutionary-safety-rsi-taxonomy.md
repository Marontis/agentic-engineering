# Evolutionary Safety of Recursive Self-Improving AI

> **Source**: Gong, Bi, Yao, Liang, Xiang & Guo, arXiv:2609.31186, Sep 2026
> **Status**: Research Brief — conceptual taxonomy and evaluation framework (no new experiments)

## Why Not a Skill?

This is a framework paper: a taxonomy of where risk enters a self-improving system, a list of how safety degrades, and evaluation units with an attribution estimand. It reports no empirical results. Its one worked number is labelled by the authors as illustrative, "not an empirical result". The governance principles are useful as rule language, but there is no tested procedure.

## Core Concept

A self-improving system can pass a safety check at every step and still become unsafe over time. Risk enters through **five surfaces**: persistent agent state (memories, skills, tools, workflows), model state (weights), evaluation and environmental feedback (task generation, reward criteria), computational substrate (hardware, orchestration, access control), and **meta-level update mechanisms and co-evolution** (changes to the updater itself).

It shows up in **six ways**: intent drift; error accumulation and amplification; experience contamination; safety-property erosion; evaluator drift and selection distortion; risk inheritance and propagation.

The stated goal is not to stop change but to ensure consequential changes "cannot become persistent, selected, or inherited without adequate evidence and a viable path to recovery."

## Key Findings

- **Four evaluation units**: *states* (a snapshot), *updates* (the effect of one change with the judge and environment held fixed), *trajectories* (the same system across rounds, to catch gradual degradation or a delayed threshold crossing), and *lineages* (inheritance across derived artifacts and successor systems).
- **Attribution against a frozen counterfactual**: the central estimand compares a metric under the evolving regime with the same system frozen at step t, measured h steps later. This separates evolution-induced risk from risk that was already there.
- **Selection alone can move risk**: in the worked example, two equally likely proposals with harmful-action rates 0.10 and 0.30 average 0.20, and always accepting the second shifts risk by +0.10 (the authors call these numbers illustrative only).
- **Evaluator drift**: a judge trained on the model's own outputs can become more lenient about its mistakes, so evaluator revision changes both which candidates survive and how survivors are measured.
- **Updater changes**: a test adequate for the original updater "may no longer cover the candidates its successor generates"; approval for changes to evaluators or update procedures "should come from an authority the proposed change cannot itself replace."
- **Governance principles**: (1) modification boundaries: declare what the system may change and which authority can widen that scope ("A coding agent might propose a skill while being unable to alter its security tests or grant itself new permissions"); (2) pre-commit gating in sandboxed branches; (3) independent verification and authorization, separating the right to propose from the right to commit; (4) lineage traceability and recovery, with quarantine of affected descendants. Separately, the risk-discovery guidance says to keep validated failure cases as versioned regression tests, and to use known-risk held-out tests after each update plus adaptive red teaming and novelty search for risks no fixed benchmark contains.
- **No position on capability ceilings**: the paper neither claims nor denies a fundamental limit on RSI.

## Relevance to Praxis

- **H1 (editable vs bounded self-improvement)**: supports the suggested fix. The paper does not ask to freeze the system (it assumes improvement continues), but it puts the updater, the evaluator and the security tests *outside* the self-editable scope, under an authority the change cannot replace. That reconciles `rules/recursive-improvement.md` "DON'T: Freeze the improvement module behind alignment constraints" (which already speaks of a safety envelope) with `rules/skill-system-design.md` "DO: Bound the search space of harness self-evolution" and the immutable negative testbed rule (2609.17817).
- **M5 (is RSI bounded?)**: no evidence either way. The paper is silent on ceilings, and its evaluator-drift point supports the "evaluator damping" part of the suggested rewording, not a capability ceiling.
- **H3**: "separate the ability to propose a change from the authority to commit it" is compatible with the split between auditors and verifiers.
- Related: [`harness-tampering-audit`](../skills/harness-tampering-audit/SKILL.md), [`controlled-skill-lifecycle-management`](../skills/controlled-skill-lifecycle-management/SKILL.md), [`regularized-harness-evolution`](../skills/regularized-harness-evolution/SKILL.md), brief [`recursive-self-improvement-criticality`](recursive-self-improvement-criticality.md).

> Source: Gong et al., "Evolutionary Safety of Recursive Self-Improving AI: Taxonomy, Risk Discovery, and Evaluation" (arXiv:2609.31186)
