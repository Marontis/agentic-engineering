---
name: fast-tree-search-self-improvement
description: >
  Accelerate recursive self-improvement of coding agents using
  LLM-as-judge pairwise comparisons aggregated via regularized
  Bradley-Terry scoring to guide a disaggregated tree search. Reserves
  expensive downstream evaluations for only the most promising
  candidates.
  Derived from "Self Improvement via Fast Tree-search (SIFT)"
  (arXiv:2609.19526).
source: https://arxiv.org/abs/2609.19526
---

# Fast Tree-Search Self-Improvement (SIFT)

Use this skill when running a self-improvement loop for a coding agent
and you need to evaluate candidate modifications efficiently under
strict compute budget constraints.

## When to Use

- Running recursive self-improvement where the agent modifies its own
  harness, prompts, or tool implementations
- Evaluation of candidate modifications is the runtime bottleneck
  (re-running benchmark tasks is slow/expensive)
- You have a limited compute budget and need to prioritize which
  modifications to fully evaluate
- You want to scale tree-search-based exploration without proportional
  cost increase

## Core Insight

The main bottleneck in recursive self-improvement is **evaluating**
candidate modifications — prior methods estimate effectiveness by
re-running benchmark tasks with each modified agent, which is
expensive. SIFT replaces most downstream evaluations with **LLM-as-
judge pairwise comparisons** between candidate patches. Win-loss
records are aggregated via a **regularized Bradley-Terry model** to
produce strength scores, which drive **rank-based parent sampling** in
a lightweight tree search. Only the most promising nodes get expensive
downstream task evaluations.

**Evidence**: SIFT outperforms existing tree-search self-evolution
frameworks on the full Polyglot benchmark with significantly lower CPU
hours, wall-clock time, and API cost.

---

## Procedure

### 1. Initialize the Search Tree

1. Start with the current agent implementation as the **root node**
2. Generate an initial set of **candidate modifications** (patches to
   harness code, prompt text, tool implementations, etc.)
3. Each candidate becomes a child node in the search tree
4. Assign initial Bradley-Terry strength scores (uniform)

### 2. Score Candidates via LLM-as-Judge Pairwise Comparison

For each pair of candidate patches at the current frontier:

1. Present both patches to an LLM judge with the task context
2. The judge performs a **pairwise comparison** — which patch is more
   likely to improve agent performance?
3. Record the win-loss outcome
4. Aggregate all pairwise outcomes into a **regularized Bradley-Terry
   model** to produce per-candidate strength scores
5. Regularization prevents score collapse when data is sparse

### 3. Sample Parents via Rank-Based Selection

1. Rank candidates by their Bradley-Terry strength scores
2. Use **rank-based sampling** (not uniform) to select parent nodes
   for the next generation of mutations
3. Higher-ranked candidates are more likely to be selected as parents
4. This focuses exploration on promising regions without entirely
   abandoning diversity

### 4. Expand Promising Nodes

1. For each selected parent, generate new candidate modifications
   (mutations of the parent's patch)
2. Add these as child nodes in the tree
3. Repeat Steps 2–4 for the new frontier
4. The tree grows in a **disaggregated** fashion — judge scoring and
   node expansion can run in parallel

### 5. Reserve Downstream Evaluation for Top Candidates

1. Only nodes that reach the **top of the strength ranking** after
   multiple rounds of judge comparison get expensive downstream task
   evaluations
2. Run the actual benchmark tasks with the candidate-modified agent
3. Use the downstream results to:
   - Confirm or correct the judge's ranking
   - Update the tree with ground-truth signal
   - Decide whether to accept the modification

### 6. Commit or Reject

1. If the top candidate improves downstream task performance → commit
   the modification as the new agent baseline
2. If not → prune the subtree and continue exploration from other
   high-ranked candidates
3. Iterate until the compute budget is exhausted

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Judge-task misalignment | LLM judge ranks patches differently than downstream performance | Reserve downstream evaluation for top candidates; recalibrate judge criteria |
| Score collapse | All candidates score similarly under Bradley-Terry | Regularization term prevents collapse; increase mutation diversity |
| Expensive judge calls | Pairwise comparisons still cost tokens | Use cheaper/faster judge model than the agent model; batch comparisons |
| Premature convergence | Tree search gets stuck in local optimum | Rank-based sampling preserves exploration; periodically inject random mutations |
| Overfitting to judge | Mutations optimize for judge preference, not task performance | Downstream evaluation on held-out tasks acts as ground-truth check |

> Source: Fu et al., "Self Improvement via Fast Tree-search (SIFT)"
> (arXiv:2609.19526), Sep 2026.
