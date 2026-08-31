# Planner-Controller Decoupling for Instructable Agents

> **Paper**: [Decoupling Planning and Control for Instructable Agents](https://arxiv.org/abs/2608.26788) (COLM 2026)
> **Authors**: Tang, Allen, van Steenkiste, Dasgupta, Suhr (UC Berkeley / UBC / Google DeepMind)
> **Praxis source**: `src:2608-26788`

## Why Not a Skill?

The transferable procedures in this paper (post-hoc instruction supervision, asynchronous instruction) are too tightly coupled to embodied agent infrastructure — they require replay buffers, world-model controllers (RSSM), and VLM relabeling pipelines that most software engineering projects don't have. The architectural *pattern* (separate planning from execution via a language interface) is valuable as a reference but doesn't decompose into a standalone skill.

---

## Core Architecture: Instruct-to-Act

Decomposes embodied decision-making into two components communicating via natural language:

**Planner** (VLM, high-latency):
- Maps observations + task context → natural-language instructions
- Pre-trained, instruction-tuned — NOT fine-tuned to the environment
- Runs asynchronously, issuing instructions concurrently with ongoing execution
- Can be swapped without retraining the controller

**Controller** (RSSM, low-latency):
- Maps observations + language instruction → low-level actions in real time
- Environment-specific but planner-agnostic
- Trained via reward maximization + world modeling + behavior cloning from VLM-relabeled replay segments
- Lightweight enough to run at control frequency

### Key Insight: Language as the Interface

The stable language interface between planner and controller enables:
- **Modularity**: swap planners without retraining controllers
- **Asynchronous operation**: planner reasons at its own pace while controller acts at control rate
- **Multi-agent coordination**: multiple VLM planners coordinate through language while sharing controller architecture
- **Evaluation**: controllers achieve 92.8% average instruction-following accuracy across diverse VLM planners

---

## Results

- Decoupled approach outperforms controller-only and direct VLM action-generation on 6/7 embodied environments
- Different VLM planners can be swapped without fine-tuning
- Multi-agent environments work by coupling multiple planners with identical controller instances
- Post-hoc instruction supervision (relabeling replay segments with VLM-generated instructions) is sufficient — no expert demonstrations needed

---

## Relevance to Praxis

**Architectural analogy only** — the pattern maps loosely to:
- Praxis's separation of reasoning (graph search, proposal generation) from execution (tool calls, file operations)
- The MCP server's handling of concurrent agent sessions (multiple planners, shared infrastructure)
- The general principle that stable text interfaces between components enable modularity and swappability

**Spec update**: added one decision point to [`self-improving-agent.spec.md`](../specs/self-improving-agent.spec.md) for projects that need real-time action generation.
