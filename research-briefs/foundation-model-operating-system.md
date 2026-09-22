# Position: Virtualize Foundation Models with a Self-Evolving Operating System Layer

> **Source**: Bhattacharya et al., arXiv:2609.19203, Sep 2026
> **Status**: Research Brief — position paper, no implementation

## Why Not a Skill?

This is a position paper proposing an architectural vision (Foundation Model Operating System) without an implemented procedure. The concepts are valuable for framing but not directly actionable.

## Core Concept

AI application stacks are fragmented: each framework embeds its own implicit runtime for state, memory, budgets, and guardrails, making behavior non-portable and governance brittle. The paper argues for a **Foundation Model Operating System (FMOS)** — a system layer that virtualizes FM interactions analogously to how VMs abstract physical hardware, giving applications the illusion of dedicated, trustworthy FM instances.

## Key Findings

- Current agent stacks mirror pre-OS computing: every program reimplements basic services
- Protocols like MCP and A2A ease connectivity but don't provide runtime abstraction
- An FMOS would orchestrate: knowledge across memory tiers, model selection and resource allocation, verification and policy enforcement
- The system should learn when to intervene (slow deliberation) vs. let inference proceed (fast intuition), analogous to dual-process cognition

## Relevance to Praxis

- Provides architectural framing for agent runtime design
- The "virtualize FM interactions" metaphor clarifies what a mature agent platform should provide
- Connects to existing skills: unified-capability-gateway, prefix-preserving-context-assembly, policy-centroid-routing

> Source: Bhattacharya et al., "Position: Virtualize Foundation Models" (arXiv:2609.19203)
