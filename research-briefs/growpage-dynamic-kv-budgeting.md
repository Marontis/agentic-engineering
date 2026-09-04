# GrowPage: Dynamic On-Demand KV Budgeting for LLM Reasoning

> **Paper**: [GrowPage: On-Demand KV Budgeting for Efficient LLM Reasoning Serving](https://arxiv.org/abs/2609.03494)
> **Praxis source**: src:2609-03494v1

## Why Not a Skill?

Low-level LLM inference serving and memory-manager architecture implemented at the vLLM/PagedAttention engine level.

---

## Core Concept

Long-chain reasoning models (o1, R1, QwQ) generate thousands of tokens per response, making KV-cache memory the primary bottleneck for serving throughput. Standard KV-cache compression allocates a static token budget per request. However, reasoning tasks exhibit huge temporal variance: early exploration steps require wide attention context, while late synthesis steps can operate under compact budgets. GrowPage dynamically resizes the physical page allocation of individual requests throughout generation based on runtime attention entropy.

### Key Finding

Dynamic on-demand KV allocation increases serving batch concurrency by **$1.8\times$ to $2.4\times$** on long-reasoning benchmarks without degrading final answer accuracy, avoiding out-of-memory preemption.

## Relevance to Praxis

- Complements context engineering: highlights that long-horizon agent runtimes must coordinate context compaction with backend serving memory constraints.
