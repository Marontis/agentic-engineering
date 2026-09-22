# Closed-World Resolution Against Tool Hallucination in LLM Agents

> **Source**: Iyer, arXiv:2609.19425, Sep 2026
> **Status**: Research Brief — measurement study with benchmark

## Why Not a Skill?

The paper provides a taxonomy and measurement study, not a transferable procedure. The resolver (registry membership + signature check) is described as a reference point, not a method — its contribution is architectural placement, not algorithmic novelty.

## Core Concept

Tool-augmented LLM agents fail in a way no existing defense addresses: they **call tools that don't exist** and **pass arguments no schema declares**. Existing defenses either pick the right tool (selection) or constrain what an agent may do with real tools (gating) — both presuppose the emitted call refers to a real tool. A hallucinated call is by construction not a decision any gate made, so no gate can reject it.

## Key Findings

- **Five-class tool hallucination taxonomy (H1-H5)**: fabricated tool name, fabricated argument, wrong schema, conflated tools, phantom capability
- **MCP-specific taxonomy (M1-M5)**: namespace collisions and shadowing create new hallucination surfaces when merging multiple MCP servers
- **322 genuine hallucinations** measured across 10 hosted models under 2 invocation surfaces
- **Model scale does not help**: a 675B model matches 7-8B models on hallucination rate
- **Key architectural insight**: hallucination defense must **precede any causal gate** in the agent pipeline — a resolver checking registry membership + schema must run BEFORE any tool selection or authorization layer
- On live MCP surface: **154 hallucinations** including from frontier models that were clean on single-registry surface

## Relevance to Praxis

- Directly extends covert-tool-injection-defense skill: hallucination defense is a prerequisite, not an alternative
- MCP namespace merge creates structural hallucination surfaces that single-registry checks cannot express
- Decision rule: any MCP multi-server deployment needs namespace-aware resolution, not just per-server validation

> Source: Iyer, "Closed-World Resolution Against Tool Hallucination" (arXiv:2609.19425)
