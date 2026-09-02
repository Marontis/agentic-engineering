# Workload-Aware Column Imprint Hash Joins for Edge Queries

> **Paper**: [Scalable Real-Time Edge Query Processing using Workload-Aware Column Imprints](https://arxiv.org/abs/2609.00181)
> **Praxis source**: src:2609-00181v1

## Why Not a Skill?

Database systems algorithm for real-time edge hardware query acceleration in smart mobility networks.

---

## Core Concept

Edge computing devices struggle with relational join performance due to constrained memory and cacheline misses. Workload-Aware Column Imprint-Hash Join (WACI-HJ) predicts upcoming query workloads and uses workload-aware column imprints to skip irrelevant cachelines during hash join execution.

## Relevance to Praxis

- Database indexing reference for memory-constrained edge hardware.
