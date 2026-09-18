# Contagion on the Trading Floor: How Adversarial Signals Spread in Multi-Agent Trading Systems

> **Paper**: [Contagion on the Trading Floor: How Adversarial Signals Spread in Multi-Agent Trading Systems](https://arxiv.org/abs/2609.19789)  
> **Conference**: ECML PKDD 2026  
> **Praxis source**: `src:2609-19789`

## Why Not a Skill?

This paper introduces the Generic Multi-Agent Trading System (GMATS) benchmark and defines mathematical contagion metrics for tracking how adversarial inputs cascade through multi-tier agent topologies. It does not provide a single end-user task procedure, but instead establishes fundamental swarm coordination and contagion-damping design rules for `rules/multi-agent-coordination.md`.

---

## Core Concept

Multi-agent LLM systems in quantitative finance decompose market analysis across specialized roles: perception agents (scraping financial news, analyst notes, and social media), quantitative reasoning agents, and portfolio coordinator agents. 

Sua et al. demonstrate that multi-agent financial architectures are vulnerable to **input-only black-box poisoning**: an adversary injects budget-constrained, plausibly benign posts into public feeds. Even without accessing model weights, tool APIs, or coordinator prompts, these adversarial signals induce cascading belief shifts that propagate through the agent hierarchy, systematically corrupting trading decisions.

```
                      External Unfiltered Feed
                 (Adversarial Poisoning Injected)
                                │
                                ▼
         ┌──────────────────────────────────────────────┐
         │          Perception / Analyst Agents         │
         │ (Belief shift induced by plausible misinformation) │
         └──────────────────────┬───────────────────────┘
                                │ Cascading Evidence Signals
                                ▼
         ┌──────────────────────────────────────────────┐
         │             Coordinator / Risk Agent         │
         │  - Un-damped Topology: Contagion Amplified    │
         │  - Damped Topology: Shocks Filtered / Checked │
         └──────────────────────┬───────────────────────┘
                                │ Corrupted Portfolio Execution
                                ▼
         ┌──────────────────────────────────────────────┐
         │                Market Execution              │
         │ (Sharp collapse in Sharpe ratio & max drawdown)│
         └──────────────────────────────────────────────┘
```

---

## Contagion Metrics & Empirical Findings

The authors introduce formal contagion measurement metrics on an offline benchmark with historical market and social data:
1. **Layer-Wise Belief-Shift Scores**: Quantifying the Kullback-Leibler divergence and semantic shift in agent conviction between clean and poisoned evidence streams at both analyst and coordinator layers.
2. **Attack-Clean Financial Deltas**: Measuring changes in Sharpe ratio, maximum drawdown, and portfolio turnover under fixed adversarial budgets.

### Key Empirical Results
- **Severe Financial Degradation**: Even minor, budget-constrained poisoning of social-media inputs materially degraded overall risk-return profiles, causing sharp drops in Sharpe ratios and triggering premature panic liquidations.
- **Topology-Dependent Contagion Damping**:
  - The susceptibility of the system depends heavily on its multi-agent topology.
  - **Flat / Broadcast Topologies**: Suffer rapid, unimpeded contagion where corrupted analyst signals immediately influence global decision state.
  - **Hierarchical Topologies with Cross-Checking Coordinators**: Coordinators prompted to actively verify evidence across disjoint information modalities dampened adversarial shocks by $>40\%$ under identical poisoning budgets.

---

## Relevance to Praxis & Agent Architecture

- **Rules Contribution to `multi-agent-coordination.md`**:
  - **DON'T allow perception agents to directly feed execution coordinators without adversarial damping**: Signals derived from external web or social feeds must pass through confidence calibration and modality cross-checking before entering strategic decision layers.
  - **DO structure multi-agent topologies with explicit shock-dampening coordinators**: Implement disjoint analyst verification and cross-modality validation to prevent cascading belief failures in autonomous swarms.
