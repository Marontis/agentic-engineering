# HTN Planning as a Coordination Layer for Multi-Server MCP Orchestration

> **Paper**: [HTN Planning as a Coordination Layer for Multi-Server MCP Tool Orchestration](https://arxiv.org/abs/2609.33731)
> **Authors**: E. Jacopin, É. Jacopin, Takahashi (RIKEN, Cosmic AI)
> **Praxis source**: src:2609-33731v1
> **Status**: Research Brief — architecture with a demonstration, no LLM baseline measured

## Why Not a Skill?

The architecture is clear and reusable, but the paper reports no comparison
against an LLM-driven orchestrator, its domains are mostly linear, and the
planning domains and output extractors are hand-written per server (domain
authoring is deferred to a companion paper). It is a reference design, not
a validated procedure.

---

## Core Concept

MCP isolates servers by design, so only the host can orchestrate across them.
When the host is an LLM, a cross-server workflow is non-deterministic, costs
one inference per tool call, and has no inspectable plan before execution.
The paper splits orchestration into three layers:

1. **Planning**: a GTPyhop hierarchical task network (HTN) planner turns an
   objective into a sequence of server-local primitive actions, using
   placeholder values so the plan can be checked without calling any API.
2. **Binding**: a JSON configuration maps each primitive action to a
   (server, tool) pair and declares JSON-path extractors that name the
   outputs later actions need.
3. **Execution**: middleware walks the plan deterministically, calls the MCP
   tools, stores extracted outputs in a context, and substitutes
   `${context.X}` templates for cross-server data dependencies.

An N-step workflow then needs 2 LLM inferences (invoke planning, execute)
instead of N+1. The authors report this as an architectural reduction only,
not a measured speedup.

## Key Findings

- Drug-target discovery case study against eight live third-party MCP
  servers (140 tools advertised, 8 used): three replays of the same
  8-step plan executed 8/8 actions each, with the same server sequence and
  identical intermediate substitutions. Wall-clock 35 s (cold), 29 s and
  15 s (warm), dominated by external API latency.
- PCR-preparation domain: 55 primitive actions for 4 samples and 611 for a
  96-well plate, all executed successfully, about 16.5 actions per second.
- Execution is mocked by default to avoid unintended API use; live calls are
  opt-in.

## Relevance to Praxis

- A concrete instance of "DO: Keep deterministic steps in code and explicit
  graph edges; delegate to LLMs only for reasoning"
  (`rules/skill-system-design.md`): when a multi-server workflow is known in
  advance, compile it once and replay it instead of having the LLM pick each
  call.
- The plan exists before execution, so a human or policy check can approve
  it, in line with "DO: Enforce human approvals and safety gates in the
  runtime, NOT in prompt instructions" (`rules/adk-workflow-architecture.md`).
- Binding tools by explicit (server, tool) pairs avoids the namespace
  collisions described in
  [`closed-world-tool-hallucination`](closed-world-tool-hallucination.md).
- Limits: no branching-heavy domains, no measured comparison with ReAct-style
  agents, hand-written extractors. Use it where workflows are stable and
  reproducibility matters (lab automation, regulated pipelines), not as
  evidence that HTN beats LLM orchestration in general.
- Related: [`mcp-server-design`](../skills/mcp-server-design/SKILL.md),
  [`temporal-workflow-graph-compilation`](../skills/temporal-workflow-graph-compilation/SKILL.md).

> Source: Jacopin, Jacopin & Takahashi, "HTN Planning as a Coordination Layer
> for Multi-Server MCP Tool Orchestration" (arXiv:2609.33731)
