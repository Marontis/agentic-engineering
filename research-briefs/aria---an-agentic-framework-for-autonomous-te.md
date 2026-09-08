# ARIA - An Agentic Framework for Autonomous Testing of Infotainment Systems

> **Paper**: [ARIA - An Agentic Framework for Autonomous Testing of Infotainment Systems](https://arxiv.org/abs/2609.04913)
> **Praxis source**: `src:2609-04913v1`
> **Primary topic**: Agent Self-Improvement & Harness Engineering

## Why Not a Skill?

This paper applies multi-agent patterns to a domain-specific use case. While the multi-agent architecture has general elements, the procedure is heavily tied to the specific application domain and does not generalize as a standalone agent engineering skill.

---

## Core Concept

Automotive infotainment validation still relies on manual testing, slow, costly, and incompatible with agile releases and OTA updates. Scripted automation only partly helps: it couples test logic to implementation, yielding brittle, high-maintenance suites. Existing LLM-driven frameworks mostly target web/mobile apps, using single- or dual-agent setups that overload one or two models with perception, planning, action selection, and validation at once, prone to hallucinations and unproductive exploration loops given infotainment complexity. We present ARIA (Autonomous Real-time Infotainment Assessment), a multi-agent LLM framework that autonomously runs end-to-end tests on Android infotainment systems via visual interaction, using a closed-loop pipeline of four specialized agents per step plus a report stage. From single-sentence scenarios (path, action, expected outcome), ARIA runs the interactions and produces reports, reproducible scripts, and visual evidence per step. Evaluated on a manufacturer's physical Android infotainment system across 30 scenarios, ARIA completed 28 (93.3%) with a verdict (2 errored), 20 of which (71.4%) matched ground truth. It caught all 5 known defects, no fault passed as working; its 8 false positives stem from navigation/image limits and unsupported gestures, showing multi-agent LLMs can run infotainment tests industrially while exposing the cost of a low false-positive tolerance. A single-agent baseline confirms the multi-agent design's value: on the first pass, before stronger-model revisitation narrows the gap, it shows a far higher false-positive rate (72.0% vs. 52.6%), conflating navigational difficulty with system failure. We report first-pass/post-revisitation results, token/call/cost per scenario, and show via repeated runs that stability tracks complexity, with fault detection perfectly consistent, pointing to CI integration of visual testing.

### Key Findings

- **Primary Result**: Evaluated on a manufacturer's physical Android infotainment system across 30 scenarios, ARIA completed 28 (93.3%) with a verdict (2 errored), 20 of which (71.4%) matched ground truth.
- **Additional Finding**: A single-agent baseline confirms the multi-agent design's value: on the first pass, before stronger-model revisitation narrows the gap, it shows a far higher false-positive rate (72.0% vs.
- **Additional Finding**: 52.6%), conflating navigational difficulty with system failure.

## Relevance to Praxis

- Relevant to agent self-improvement loops and harness engineering.
