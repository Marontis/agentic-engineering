# Dude: Dual-Detection Multi-Agent System for Paper-Code Discrepancy

> **Paper**: [Dude: A Dual-Detection Multi-Agent System for Paper-Code Discrepancy Detection](https://arxiv.org/abs/2609.03416)
> **Praxis source**: src:2609-03416v1

## Why Not a Skill?

Domain-specific multi-agent auditing pipeline for scientific paper versus GitHub repository verification.

---

## Core Concept

Verifying whether an open-source code implementation faithfully reflects the claims, equations, and hyperparameter tables of a scientific paper is hindered by granularity asymmetry: papers use high-level mathematical abstractions while code uses low-level tensor operations. Single-agent LLMs suffer from high false-positive rates due to over-interpretation. Dude introduces a dual-agent architecture with granularity-aligned negotiation and two-stage salience filtering, preventing agents from reporting trivial implementation variations as discrepancies.

### Key Finding

Dude improves discrepancy detection recall and precision by up to **22.8%**, yielding an **18.7% F1 score improvement** over existing single-agent baselines on real-world scientific paper-code benchmarks.

## Relevance to Praxis

- Provides design patterns for cross-artifact code auditing: comparing high-level specifications against executable code requires explicit granularity alignment to avoid false positive alarms.
