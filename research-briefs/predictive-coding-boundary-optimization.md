# Hidden-State Optimization in Predictive Coding Networks

> **Paper**: [A Study of Hidden-State Optimization Order in Predictive Coding Networks](https://arxiv.org/abs/2609.00686)
> **Praxis source**: src:2609-00686v1

## Why Not a Skill?

Neuroscience-inspired local learning architecture for neural networks, unrelated to agent engineering workflows.

---

## Core Concept

Predictive coding networks (PCNs) replace global backpropagation with local error minimization, but suffer from weak feature updates in deep layers. The authors introduce a boundary-first schedule: partitioning layers into chunks, coordinating hidden states at chunk boundaries first, and then optimizing internal representations.

## Relevance to Praxis

- Conceptual parallel to hierarchical planning: establishing boundary agreements between major milestones before refining internal task steps.
