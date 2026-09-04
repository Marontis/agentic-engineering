---
name: procedural-family-skill-consolidation
description: >
  Organize self-improving agent skills into procedural families with frozen global
  priors and locally regenerated instance details, protected by execution-gated
  commit boundaries. Derived from SkillGLoW (arXiv:2609.02217).
source: https://arxiv.org/abs/2609.02217
---

# Procedural-Family Skill Consolidation

Use this skill when designing, scaling, or curating self-improving agent skill libraries
operating over diverse, long-horizon task streams.

## When to Use

- Agent systems that distill skills from execution traces and face the dilemma between
  a single bloated global guideline document and a massive flat pool of per-task skills
- Preventing "document collapse": global prompt documents devolving into generic advice
  as they try to cover every possible domain
- Preventing "library inflation": per-task skill pools accumulating thousands of near-duplicate,
  overfitted entries that confuse vector retrieval
- Setting up automated commit gates to verify that candidate skill updates improve
  or preserve performance across task families before admission

## Core Insight

Existing agent skill architectures fail on heterogeneous task streams:
- **Single global documents** assume one dominant procedure exists; on diverse tasks,
  they collapse into vague, generic discipline.
- **Flat per-task skill pools** assume old task solutions can be reused wholesale; in
  practice, entries stay tightly bound to the specific instances that created them,
  inflating memory and causing retrieval noise.

The natural unit of reuse is the **procedural family**: a cluster of tasks that share
a common underlying solving procedure, even while each instance carries unique local constraints.

By splitting skills into two distinct layers:
1. **Global Layer (Procedural Prior)**: A frozen, de-instantiated procedural workflow
   shared across the family.
2. **Local Layer (Instance Detail)**: Regenerated on-the-fly for each task from its own
   runtime execution feedback, rather than permanently stored.
3. **Execution-Gated Commit**: Revisions to a global prior are committed *only* when
   real environment evaluation demonstrates non-degradation across the family.

In empirical tests across 4 domains (math, terminal automation, software repair, embodied
control) and 3 models, this structure yielded **+17.2 points** over no-skill baselines,
maintained a library **$3.6\times$ more compact** than flat pools, and transferred to
unseen tasks with **+10.0% higher success** (Yan et al., 2026).

---

## Procedure

### 1. Group Execution Traces into Procedural Families

Rather than writing a standalone skill for each task or appending to a monolithic document:

- **Cluster by solving graph**: Analyze successful execution trajectories based on
  tool sequence topologies and subtask goals. Group tasks sharing similar transition
  skeletons into a **Procedural Family** (e.g., `git-rebase-conflict-resolution`,
  `api-schema-migration`, `tabular-data-imputation`).
- **Target granularity**: Aim for 10–30 procedural families per domain, rather than
  hundreds of task-specific skills.

### 2. Synthesize De-instantiated Global Priors

For each family, distill execution traces into a single procedural prior:

- **De-instantiation rule**: Strip all instance-specific identifiers (file paths, entity
  names, specific error codes, temporary variable names).
- **Structure**:
  - `Objective`: Core subtask goal achieved by the family.
  - `Invariant Pre-conditions`: Environmental requirements necessary before starting.
  - `Procedural Spine`: Sequential stages of the solving procedure.
  - `Diagnostic Decision Tree`: Common branch conditions observed during execution.
- **Freeze during solving**: The global prior remains strictly read-only during task
  execution. It is never edited in real-time during an active run.

### 3. Local Layer: Runtime Instance Regeneration

During an active task execution:

- **Retrieve procedural prior**: Match incoming task to its procedural family and inject
  the frozen prior into the prompt.
- **Regenerate local detail**: As the agent interacts with tools and receives feedback,
  let it write local working notes (the "local layer") in its scratchpad containing
  the instance-specific details (e.g., active paths, observed schema, immediate diffs).
- **Discard upon completion**: At the end of the run, discard the local layer from
  permanent storage. Retain only the raw execution trajectory in the history log.

### 4. Offline Consolidation and Execution-Gated Commit

Periodically consolidate accumulated traces into updated global priors:

1. **Candidate synthesis**: An offline consolidator reviews new successful and failed
   trajectories in a family and proposes an updated prior $P'$.
2. **Regression audit**: Run the candidate prior $P'$ on a held-out evaluation subset
   of benchmark tasks from that family.
3. **Admission Gate**:
   $$\text{Commit}(P') \iff \text{Score}(P') \ge \text{Score}(P_{\text{deployed}}) \quad \text{and} \quad \text{Regressions}(P') == 0$$
   If performance degrades on any previously solved task, reject or revise the candidate.

---

## Environment Caveats

- **Family boundary drift**: Over time, tasks within a family may diverge. Monitor
  intra-cluster embedding variance; if variance exceeds threshold, split the family into
  two distinct sub-families.
- **Cold start**: When an agent encounters an entirely new problem domain with no existing
  family, execute zero-shot with local logging first, then form a new family after 3+
  trajectories are recorded.

## Failure Modes

- **Instance leakage into global priors**: Including hardcoded filenames or command args
  in the global prior. Countermeasure: run automated regex linters on candidate priors
  to ensure all paths and variables are generic parameter placeholders.
- **Gate bypassing**: Admitting self-generated skills directly into the library without
  running execution regression benchmarks.

## Cross-References

- [`skill-design-methodology`](../skill-design-methodology/SKILL.md) — Subtask decomposition and utility scoring.
- [`knowledge-compounding-loop`](../knowledge-compounding-loop/SKILL.md) — Three-layer workspace architecture (raw/knowledge/skill).
- [`capability-aware-skill-selection`](../capability-aware-skill-selection/SKILL.md) — Set-level skill retrieval and context budgeting.

## Sources

- **Paper**: [SkillGLoW: Procedural-Family Skill Consolidation for Self-Improving Agents on Long-Horizon Task Streams](https://arxiv.org/abs/2609.02217) — Yan, Xin, Du, Zhou (NUS & IAIC, 2026)
- **Praxis source**: `src:2609-02217v1`
