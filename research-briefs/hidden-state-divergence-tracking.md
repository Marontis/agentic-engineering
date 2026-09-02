# Geometry of Divergence: Tracking Hidden-State Trajectories for Adaptive Multi-Turn Reasoning

> **Paper**: [Geometry of Divergence: Tracking Hidden-State Trajectories for Adaptive Multi-Turn Reasoning](https://arxiv.org/abs/2608.30650)
> **Praxis source**: `src:2608-30650v1`

## Why Not a Skill?

Training pipeline â€” requires access to model internals and specific multi-turn reasoning architecture. Procedures too tied to a specific model architecture to transfer as a general skill.

---

## Core Concept

Tracks how hidden states diverge across reasoning turns to detect when a model is going off-track. When hidden-state trajectories diverge beyond a threshold, the system intervenes (early stopping, backtracking to a previous turn, or regenerating from a checkpoint).

## Relevance to Praxis

- The divergence detection principle could inform the ecursive-improvement rules about when to stop self-modification
- Connects to the hallucination-mean-shift-probe â€” both exploit hidden-state geometry for quality detection
