# Personalized Federated LoRA under Rank Heterogeneity

> **Paper**: [Breaking the Structural Identity: Personalized Federated LoRA Fine-tuning under Rank Heterogeneity](https://arxiv.org/abs/2609.00632)
> **Praxis source**: src:2609-00632v1

## Why Not a Skill?

Low-level distributed parameter fine-tuning method for heterogeneous client devices.

---

## Core Concept

Federated LoRA adaptation faces challenges when client devices possess vastly different compute capabilities (varying ranks $). The paper presents a framework that decouples adapter rank constraints across clients, allowing personalized local low-rank updates to be aggregated without structural identity bottlenecks.

## Relevance to Praxis

- Architectural context for distributed adapter tuning in edge and multi-device deployments.
