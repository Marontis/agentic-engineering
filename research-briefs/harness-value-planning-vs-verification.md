# How Do Agent Harnesses Create Value? Planning Information and Release Control

> **Source**: Zhang et al., arXiv:2609.20474, Sep 2026
> **Status**: Research Brief — empirical findings, not procedure

## Why Not a Skill?

This is a measurement study quantifying the relative contributions of harness components (planning vs. verification). It provides decision criteria but not a transferable procedure.

## Core Concept

Agent harnesses create value through two primary mechanisms: **planning guidance** (task-specific plans that direct agent behavior) and **release control** (verifiers that gate whether outputs are accepted). This study isolates their contributions by comparing prewritten task-specific plans (Fixed) against shuffled policy text matched in word count (Sham).

## Key Findings

- **Planning improves oracle-verified success by 7.17 percentage points** (90% bootstrap CI: 1.15–13.36 pts), with gains concentrated in higher-complexity tasks
- A **read-only terminal verifier** rejects 61% of oracle-invalid episodes while withholding 17% of correct ones, at <$0.01 additional cost per episode
- **Critical trade-off**: at low liability → planning gain dominates; at high liability → verifier's avoided false passes dominate
- A **standalone verifier captures nearly all the false-pass benefit** of the full planning+verification stack at a fraction of its cost

## Relevance to Praxis

- **Decision rule**: If the cost of a false acceptance is high, invest in verification first; if performance on complex tasks matters more, invest in planning
- Supports verifiers as high-ROI harness components in this τ²-bench setting, but budget for their false rejections (17% of correct episodes withheld)
- This paper does not study how planning value changes with model strength. That finding is from a separate study, [`empirical-harness-design-study`](empirical-harness-design-study.md) (arXiv:2609.20804): planning helped the weakest model's accuracy and mostly cut cost for stronger ones
- Scope: τ²-bench Retail (two experiments) and an Airline pilot; 265 matched Fixed-vs-Sham cells
- Rule: `rules/recursive-improvement.md` "DO: Invest in standalone verifiers before planning components"

> Source: Zhang et al., "How Do Agent Harnesses Create Value?" (arXiv:2609.20474)
