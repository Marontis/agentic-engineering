# HeteroFold: Cross-Family KV Cache Transfer Between Agents

> **Paper**: [Prefill-Free Cross-Family KV Cache Transfer for Heterogeneous Multi-Agent LLMs](https://arxiv.org/abs/2609.32259)
> **Praxis source**: src:2609-32259v1

## Why Not a Skill?

A serving-layer method that needs trained per-direction mappers and access
to model internals. It is a latency optimization with a measured accuracy
cost, not a procedure most agent builders would apply.

---

## Core Concept

When heterogeneous agents pass shared context as text, each receiver
re-prefills context the sender already processed. Reusing the sender's KV
cache directly fails across model families (different tokenizers, depths,
KV representations). HeteroFold maps the sender's KV cache into the
receiver's space: token alignment on shared character boundaries, layer
alignment with moment-matched statistics, and low-rank corrections
calibrated against the receiver's own attention outputs, folded into fixed
affine maps. The receiver sees only the transferred cache, never the
sender's text.

## Key Findings

- **Models**: Llama-3.1-8B, Qwen3-4B, Ministral-3-14B (6 transfer
  directions). Long-context QA (Qasper, HotpotQA, LoCoMo, QuALITY),
  short-context QA, and HiddenBench for multi-agent communication.
- **Latency**: Llama-3.1-8B → Ministral-3-14B, 118.3 / 257.8 / 481.3 ms at
  4K / 16K / 32K tokens versus 443.1 / 2091.2 / 5167.4 ms for native
  prefill (10.74× at 32K).
- **Accuracy cost on long context**: same direction, HeteroFold scored
  21.58 / 39.00 / 30.43 / 72.05 on Qasper / HotpotQA / LoCoMo / QuALITY
  versus 45.59 / 64.56 / 52.01 / 83.32 for text communication (TextMAS).
  It beats the other cache-transfer baselines but stays well below text.
- **Multi-agent task**: on HiddenBench, 30.6% average accuracy versus 29.2%
  for text communication.
- **Costs**: 201–252M mapper parameters per direction; about two H100
  GPU-hours to build each direction; calibration used 1,600 prompts.
  Short-context results were mixed.

## Relevance to Praxis

- Agrees with "DO: Use natural language as the inter-agent interface"
  (`rules/multi-agent-coordination.md`): on long-context QA, text
  communication beat the best cache transfer by 11–26 points in the
  reported direction. Latent transfer buys prefill latency at an accuracy
  cost, and only parity on HiddenBench.
- KV transfer also removes properties the rules rely on: the receiver gets
  no text to sanitize, sign or audit ("DO: Sign inter-agent messages and
  quarantine unsigned ones", "DO: Use standardized message envelopes"), and
  every new model pair needs a trained mapper, which defeats swapping
  components freely.
- Consider it only for trusted, fixed model pairs on a latency-critical path
  with long shared context, and evaluate the accuracy cost on your own task.
  Related: [`thinkflow-latent-conversational-memory`](thinkflow-latent-conversational-memory.md),
  [`growpage-dynamic-kv-budgeting`](growpage-dynamic-kv-budgeting.md).

> Source: Prefill-Free Cross-Family KV Cache Transfer for Heterogeneous Multi-Agent LLMs (arXiv:2609.32259)
