---
name: graph-of-skills-scaling
description: >
  Scale skill libraries using typed graph structure with experience-driven
  self-evolution.  Covers hybrid seed retrieval, reverse-aware diffusion,
  topology/edge/node updates, and training-free deterministic evolution.
  Derived from SE-GoS (arXiv:2609.08228).
---

# Graph-of-Skills Scaling

Use this skill when your agent's skill library is growing beyond
flat retrieval and you need graph-structured organization that
evolves from execution experience.

## When to Use

- Your skill library has 50+ skills and flat retrieval misses relevant ones
- You want skill retrieval to improve from usage patterns
- You need the skill graph to adapt without retraining any models
- You want deterministic, auditable graph evolution (no neural components)

## Core Insight

Flat skill retrieval (embedding similarity) degrades as libraries
grow because semantically distant skills that are procedurally
related aren't retrieved together.  A **typed graph of skills**
captures structural relationships (prerequisite, alternative,
composition) and evolves its topology from execution experience.
Evolution is training-free and deterministic.

## Procedure

### Step 1: Build the seed graph

From your existing skill library:

1. Create a node for each skill with metadata (name, description,
   domain tags)
2. Add typed edges between skills:
   - `prerequisite`: Skill A should be loaded before Skill B
   - `alternative`: Skill A and B address similar problems
   - `composes_with`: Skill A and B are often used together
   - `extends`: Skill B is a specialization of Skill A
3. Use hybrid seeding: combine embedding similarity with keyword
   overlap to propose initial edges, then validate manually

### Step 2: Reverse-aware typed diffusion for retrieval

When retrieving skills for a task:

1. **Seed retrieval**: Find the top-K skills by embedding similarity
   to the task description
2. **Forward diffusion**: From seed skills, traverse `prerequisite`
   and `composes_with` edges to pull in related skills
3. **Reverse diffusion**: From seed skills, traverse edges in
   reverse to find skills that depend on or compose with them
4. **Budget reranking**: If the retrieved set exceeds the context
   budget, rank by combined (similarity score + graph centrality)
   and truncate

### Step 3: Collect experience signals

After each task execution, record:

- Which skills were retrieved and loaded
- Which skills were actually used (referenced in agent reasoning)
- Which skills were retrieved but unused
- Task success/failure outcome

### Step 4: Topology update (induction + pruning)

Based on accumulated experience:

**Induction** — Add new edges:
- If Skill A and Skill B are consistently co-used in successful
  tasks but have no edge → add a `composes_with` edge
- If Skill A is always loaded before Skill B → add a `prerequisite` edge

**Pruning** — Remove edges:
- If an edge's endpoint skills are never co-used despite being
  co-retrieved → remove the edge (it's wasting retrieval budget)
- If an `alternative` edge connects skills that are actually
  complementary (both used together) → retype to `composes_with`

### Step 5: Edge weight update

Adjust edge weights based on co-usage success rate:

- Edges between skills that co-occur in successful tasks get
  higher weight
- Edges between skills that co-occur in failures get lower weight
- Weights are normalized per source node

### Step 6: Node update

Update skill node metadata when usage patterns diverge from
descriptions:

- If a skill is consistently used for a different purpose than
  described, update its description
- If a skill is never retrieved, flag it for review (may need
  better metadata or may be obsolete)

## Environment Caveats

- **Small libraries** (<30 skills): Graph overhead isn't worth it.
  Flat retrieval suffices.
- **Rapid skill addition**: When many skills are added at once
  (e.g., batch ingest), run a full topology re-evaluation rather
  than incremental updates.
- **Cross-domain skills**: Skills that span domains may need
  multiple positions in the graph.  Use multi-parent edges rather
  than forcing a single location.

## Failure Modes

- **Echo chamber**: If only successful patterns reinforce edges,
  the graph converges to a narrow set of skill combinations.
  Periodically inject diversity by testing underused skill combinations.
- **Edge explosion**: Highly connected hub skills accumulate too
  many edges, making diffusion retrieval return everything.
  Cap edges per node and prune weakest.
- **Stale metadata**: Node descriptions that aren't updated after
  evolution become misleading for seed retrieval.

## Cross-References

- [`capability-aware-skill-selection`](../capability-aware-skill-selection/SKILL.md) —
  BPS selects skills for a single task; graph-of-skills organizes
  the library structure that BPS selects from
- [`knowledge-compounding-loop`](../knowledge-compounding-loop/SKILL.md) —
  Compounding accumulates factual knowledge; this skill structures
  procedural knowledge retrieval
- [`procedural-graph-evolution`](../procedural-graph-evolution/SKILL.md) —
  Procedural graphs structure action sequences; graph-of-skills
  structures the skill library itself

## Sources

- SE-GoS: Self-Evolving Graph-of-Skills for Skill Library at Scale (arXiv:2609.08228)
