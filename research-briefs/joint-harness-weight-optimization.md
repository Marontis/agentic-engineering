# WHALE: Joint Harness-Weight Optimization for Agents

> **Paper**: [WHALE: A Simple Recipe for Joint Harness–Weight Optimization](https://arxiv.org/abs/2609.00196)
> **Praxis source**: src:2609-00196v1

## Why Not a Skill?

Training algorithm alternating weight updates and harness search; decision criteria distilled directly into 
ules/recursive-improvement.md.

---

## Core Concept

Agent capability depends jointly on model parameters $	heta$ and harness code $ (context construction, tool wrappers, termination logic). Optimizing either component in isolation causes the system to stall against the bottleneck of its frozen counterpart. WHALE alternates two phases: updating weights under the current harness (via rejection sampling), then searching for an improved harness under the updated weights.

### Key Finding

Joint alternating optimization outperforms weight-only and harness-only adaptation by 4.15–24.38 percentage points across SearchQA, mathematical reasoning, and chess benchmarks, with significantly lower rollout costs than stagewise adaptation.

## Relevance to Praxis

- Direct rule addition to 
ules/recursive-improvement.md: alternate harness adaptation and model fine-tuning with adaptive patience switching.
