# Post-Training Ternarization of Qwen3-4B: Capability and Deployment

> **Paper**: [Post-Training Ternarization of Qwen3-4B: Capability, Effective Bit Budget, Storage Compression, and Deployment](https://arxiv.org/abs/2609.01962)
> **Praxis source**: src:2609-01962v1

## Why Not a Skill?

Model compression and low-bit quantization study focused on kernel and hardware execution rather than agent workflows.

---

## Core Concept

Aggressive post-training ternarization ("1.58-bit" models) aims to reduce storage, memory bandwidth, and inference costs. This study evaluates an end-to-end post-training conversion of Qwen3-4B to 1.641 effective bits/weight across linear weights (targeting 81.62% of parameters). The study measures downstream capability retention, checkpoint packing (reducing storage from 8.29 GiB to 3.96 GiB), and real hardware execution overheads.

### Key Finding

- **Capability Drop**: Average task accuracy falls from 64.5% to 54.7%, with knowledge-heavy tasks suffering much greater degradation (ARC-Challenge retains only 43.8% performance) than contextual plausibility tasks (BoolQ retains 84.6%).
- **Execution Reality**: Custom ultra-low-bit kernels do not automatically guarantee faster speed: preliminary Triton GEMV kernels ran **4.6x slower** than standard FP16 cuBLAS due to unpacking and scaling overhead.

## Relevance to Praxis

- Critical cautionary finding for local agent deployment: nominal low-bit compression yields storage benefits but degrades complex factual reasoning and requires custom fused hardware kernels to achieve latency parity.
