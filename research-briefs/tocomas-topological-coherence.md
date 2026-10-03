# ToCoMAS: Topological Coherence for Self-Evolving Multi-Agent Systems

> **Paper**: [Topological Coherence for Self-evolving Multi-agent Systems](https://arxiv.org/abs/2609.37953)
> **Praxis source**: src:2609-37953v1

## Why Not a Skill?

ToCoMAS is a full framework with many coupled modules and hand-set
compatibility weights. Its transferable idea, derive roles, handoffs and
memory visibility from one task graph and change them together, is a
design principle that fits existing coordination rules better than a new
procedure.

---

## Core Concept

Self-evolving multi-agent systems usually change roles, communication and
memory separately, and the three drift out of sync (an agent owns a task
but can't see the memory it needs; a handoff exposes another agent's
private state). ToCoMAS derives all three from one task topology:

1. **Organization**: group task nodes into responsibility regions by tool
   overlap, input/output compatibility, dependency adjacency and semantic
   similarity; assign each region to a capable agent.
2. **Orchestration**: communication edges come from cross-region
   dependencies; handoffs expose only the artifacts the downstream agent
   needs.
3. **Memory**: each record is tagged with its producing agent and region;
   visibility follows responsibility boundaries, and retrieval only runs
   over admissible records. Private memory moves with a region when its
   owner changes.
4. **Evolution**: proposed changes to roles, edges and memory policy are
   made together, checked structurally (capable owner, valid handoffs,
   correct memory visibility), and applied only if reward improves over
   the parent configuration.

### Key Findings

- **Qwen3.8-27B backbone**, against the best baseline per benchmark:
  BBEH 54.78% vs 46.52%; WorkBench 77.68% vs 62.17%; SWE-Bench-Verified
  48.00% vs 40.00%; CoMemBench success 14.30% vs 1.00%.
- **DeepSeek-V4-Flash**: BBEH 55.20% vs 50.65%; WorkBench 61.45% vs
  55.50%; SWE-Bench-Verified 49.00% vs 46.00%; CoMemBench success 14.00%
  vs 1.50%.
- **Ablation (Qwen3.8-27B)**: removing structure-adaptive orchestration
  dropped CoMemBench success from 14.30% to 0.00% and WorkBench from
  77.68% to 67.25%; removing boundary-preserving memory gave 6.50% and
  68.55%.
- **Sensitivity**: memory retrieval peaked at k = 3; organization
  affinity threshold best around 0.45–0.60.
- **Limitations**: absolute success on CoMemBench stays low (about 14%);
  compatibility weights are ad hoc and untested for sensitivity;
  structural-validation overhead and scaling to large graphs are not
  characterized; one evolution proposal per task.

## Relevance to Praxis

- **Supports** `rules/multi-agent-coordination.md` "DON'T: Share full
  context across all agents by default": boundary-scoped memory and
  artifact-only handoffs helped, and removing them hurt.
- **Supports** "DON'T: Default to a fixed multi-agent topology" and "DO:
  Optimize topology and model assignment jointly", extending joint
  optimization to memory policy.
- The evolution step accepts a change when reward beats the parent. That
  is search-time selection: keeping an evolved configuration should go
  through `rules/recursive-improvement.md` "DO: Pass every
  self-modification through one acceptance gate" (no regression beyond a
  δ estimated from repeated baseline runs; security testbed strict).

> Source: Topological Coherence for Self-evolving Multi-agent Systems (arXiv:2609.37953)
