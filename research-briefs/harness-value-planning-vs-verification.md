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
- Validates that verifiers are high-ROI harness components regardless of planning quality
- Planning value diminishes for stronger models but converts to cost savings

> Source: Zhang et al., "How Do Agent Harnesses Create Value?" (arXiv:2609.20474)
