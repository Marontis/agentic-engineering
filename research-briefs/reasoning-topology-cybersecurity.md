# Reasoning Topology Matters: LLM-Based Cybersecurity Analysis

> **Source**: Zhou, Adeseye, Hakkala, Virtanen & Isoaho, arXiv:2609.24710, Sep 2026
> **Status**: Research Brief — controlled comparison of reasoning topologies

## Why Not a Skill?

An A/B/C comparison of three prompting topologies on three security-analysis datasets. It reports which structure wins but no new procedure; the takeaway is a decision criterion, offered below as a rule contribution.

## Core Concept

Holding the task inputs fixed and varying only the reasoning structure via the system prompt, the study compares Chain-of-Thought (linear), Tree-of-Thought (branching), and Graph-of-Thought (interconnected, reusable states) on three security tasks: MITRE ATT&CK tactic labelling, cyber-threat-intelligence classification (1,100 reports), and CVE analysis. Models: Llama 2 (7B/13B/70B), GPT-5.1, Mistral Large 3. Temperature 0.2, 5 runs per configuration.

## Key Findings

- **More structure helped monotonically** (CoT < ToT < GoT) on every dataset. Accuracy: ATT&CK CoT 78.2 / ToT 82.2 / GoT 85.0; CTI 78.2 / 82.2 / 85.0; CVE 75.2 / 79.2 / 82.0. GoT beat few-shot by 9.8 / 12.2 / 11.8 points across the three datasets, and beat RAG (p < 0.05); GoT vs few-shot p < 0.001 (paired bootstrap).
- **GoT also beat RAG alone** (80.6 / 80.8 / 76.8), so structuring intermediate reasoning added value beyond supplying external knowledge.
- **The ordering held across model scale**: Llama 2 7B 65.7/69.7/72.7, 70B 79.3/83.3/86.3, GPT-5.1 86.3/90.3/93.3, Mistral Large 3 83.3/87.3/89.3. Larger models scored higher but the CoT<ToT<GoT ranking was stable.
- **Separating topology (system prompt) from task input (user prompt) helped**, more for richer topologies: CoT +1.9, ToT +2.9, GoT +3.7 points.
- **Limits (important)**: the authors explicitly do **not** quantify token consumption or latency, and ToT/GoT were given a larger token budget (2048 vs 1024 max tokens). So the cost of the accuracy gain is unmeasured. No systematic failure-mode analysis; possible failures noted are poor branch selection (ToT) and hallucinated dependencies (GoT).

## Relevance to Praxis

- A clean, controlled datapoint that graph-structured reasoning outperforms chain and tree for heterogeneous security-analysis classification, across model families and sizes. Complements the cybersecurity-benchmark briefs ([`pipeline-dependent-cybersecurity-benchmarks`](pipeline-dependent-cybersecurity-benchmarks.md), [`mist-mid-training-cybersecurity-llms`](mist-mid-training-cybersecurity-llms.md)).
- **Scope caution**: the accuracy gain comes with a larger, uncounted token budget, so this is not licence to always prefer heavier topologies where cost matters. See proposed rule below, which scopes the claim.
- Bears on any single-agent reasoning-structure choice for classification/analysis tasks; distinct from multi-agent debate topology (`rules/multi-agent-coordination.md`).

> Source: Zhou et al., "Reasoning Topology Matters: A Controlled Study of LLM-Based Cybersecurity Analysis" (arXiv:2609.24710)
