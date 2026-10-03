# RedHerring: Verification Decoys Against Agentic Vulnerability Discovery

> **Source**: Cheap to Hypothesize, Costly to Verify: The Defense Surface of Agentic Vulnerability Discovery, [arXiv:2609.35909](https://arxiv.org/abs/2609.35909), Sep 2026
> **Status**: Research Brief, defensive technique with evaluation. No attack
> procedure is recorded here.

## Why Not a Skill?

The defense (inserting certifiably unreachable decoy vulnerabilities into a
code base) depends on hard-problem predicate gates, private certificates and
dominator analysis that the paper builds for C/C++ OSS-Fuzz projects. Doing
it safely in production code needs a review and equivalence-testing process
the paper only partly provides (test suites, differential testing, targeted
fuzzing, not formal proofs). What transfers to agent builders is the cost
asymmetry it measures, and the general lesson that an agent's verification
budget is its scarce resource.

## Core Concept

A vulnerability-hunting agent works in two phases: it forms hypotheses
(cheap) and verifies them with builds, harnesses and test inputs
(expensive). On the paper's baseline runs, verification took **73.8%** of
compute. RedHerring adds decoys that look like real CVE-derived source-to-sink
chains but sit behind a "false bridge": a predicate no input can satisfy,
built on problems such as quadratic residuosity or syndrome decoding. The
defender holds a private certificate proving the gate is unsatisfiable; the
agent can only find out by spending verification effort.

## Key Findings

- **Setting**: 70 instances across 33 OSS-Fuzz projects; five open-weight
  models (Qwen3.8-Flash, Qwen3.8-Max, GLM-5.3, DeepSeek-V4-Pro, Kimi-K3);
  3 hours and 300 agent rounds per run; 5 decoys per instance. Claude and
  GPT models were excluded because they refused the task.
- **Fewer real findings**: confirmed real vulnerabilities fell by
  38.7–60.4% across the five models (largest on Qwen3.8-Flash).
- **Mechanism is effort diversion**: decoys absorbed 30.6–51.5% of
  completion tokens and an estimated 32.5–49.9% of runtime.
- **Does not rely on secrecy**: an agent told that decoys might be present
  still found 37.2% fewer real vulnerabilities than an equally informed
  baseline.
- **Both parts are needed**: ablations show the vulnerability chain and the
  false bridge are each necessary; the effect grows fastest from three to
  five decoys.
- **Overhead**: 69.3 minutes of integration per repository on average,
  +13.8% source size, under 1% runtime overhead on native test suites.
- **Stated limitations**: one run per configuration (API cost), effort
  metrics from LLM trajectory annotation, possible training-data
  contamination of public repositories (the authors call the reduction
  conservative), behavior preservation shown by tests rather than proofs.

## Defensive Takeaways

- **Verification cost, not hypothesis generation, bounds an autonomous
  auditor.** The same asymmetry shows up on the builder side: see
  [harness-value-planning-vs-verification](harness-value-planning-vs-verification.md).
  When budgeting your own security or coding agents, measure where the
  verification share goes.
- **Deception is a repository-scale defense where patching is not.** It does
  not need to know where the real bugs are. It is a delay, not a fix: keep
  patching and fuzzing.
- **Keep certificates out of the release.** The asymmetry depends on the
  defender holding the unsatisfiability witness privately.
- **Any decoy edit is a change to production code.** Route it through the
  same acceptance gate as other modifications (rules/recursive-improvement.md,
  "Pass every self-modification through one acceptance gate"), with the
  security testbed strict, and keep behavior-preservation tests on the
  real code paths.
- **Benchmarks of offensive agents are model-dependent and single-run here**;
  treat the per-model numbers as indicative.

## Relevance to Praxis

- Adds a measured verification-cost share (73.8%) for agentic vulnerability
  discovery to the harness-design briefs.
- Complements [coding-agents-kernel-exploits](coding-agents-kernel-exploits.md)
  and [agentxploit-defensive-lessons](agentxploit-defensive-lessons.md) with
  a defender-side countermeasure that does not require locating the bugs.

> Source: Cheap to Hypothesize, Costly to Verify: The Defense Surface of Agentic Vulnerability Discovery (arXiv:2609.35909)
