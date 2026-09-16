---
name: dense-rubric-skill-evolution
description: >
  Decouple skill self-evolution from expensive full-rollout oracle costs by maintaining
  an oracle-aligned dense rubric as a surrogate evaluation space. Inner loops revise skills
  at zero rollout cost; sparse outer loops re-align rubric weights via rank correlation.
source: https://arxiv.org/abs/2609.15396
---

# Dense Rubric Skill Evolution (SkillLift)

Use this skill to optimize and evolve persistent agent skills (reusable procedural system prompts
and task guidelines) while reducing evaluation token costs by 40% to 70% compared to
brute-force rollout search.

## When to Use

- Evolving agent skills across complex multi-step benchmarks where full rollouts are expensive or slow
- Escaping reactive "failure-patching" loops that add prompt bloat without structural optimization
- Maintaining persistent skill libraries that must adapt to new tasks or model versions
- Optimizing prompt instructions when ground-truth task verifiers (oracles) have high compute or financial cost

---

## Core Mental Model: Bilevel Rubric-Oracle Optimization

Direct skill evolution requires executing a full agent trajectory rollout (the "oracle")
for every prompt mutation, creating an unsustainable supervision bottleneck.

**SkillLift** exploits the insight that **ranking candidate skills is a smoother supervision
target than predicting absolute scores**. Instead of querying the oracle continuously,
maintain a two-tier bilevel optimization loop:

```
                  ┌────────────────────────────────────────────────┐
                  │ OUTER LOOP: Sparse Oracle Re-Alignment        │
                  │ - Executes sparse full-trajectory rollouts     │
                  │ - Computes rank correlation (Spearman rho)    │
                  │ - Calibrates Rubric criteria weights           │
                  └───────────────────────┬────────────────────────┘
                                          │ Updated Rubric
                                          ▼
┌────────────────────────────────────────────────────────────────────────┐
│ INNER LOOP: Zero-Rollout Skill Revision                                │
│ 1. Propose candidate skill mutations (decomposition, constraint, style)│
│ 2. Score candidates against Frozen Dense Rubric ($0 oracle rollouts)   │
│ 3. Select top-ranked revision and iterate                              │
└────────────────────────────────────────────────────────────────────────┘
```

The inner loop explores wide prompt mutation spaces cheaply; the outer loop anchors
the rubric so surrogate scores accurately reflect true task outcomes.

---

## Step-by-Step Procedure

### 1. Initialize the Dense Rubric Schema

Decompose task requirements into four orthogonal, observable evaluation criteria:
- **Precondition & Context Verification**: Does the skill instruct the agent to inspect state before acting?
- **Action Sequence Specificity**: Are tool call contracts, schemas, and argument bounds concrete?
- **Error Recovery & Branch Handling**: Does the skill provide deterministic fallbacks for tool failures?
- **Postcondition Termination**: Does the skill define unambiguous completion criteria?

Assign initial uniform weights $w = [0.25, 0.25, 0.25, 0.25]$.

### 2. Inner-Loop Skill Revision (Zero Oracle Cost)

Generate candidate mutations of the target skill text and evaluate them purely against the dense rubric:

1. **Mutate**: Apply mutation operators to the skill text (e.g. adding parameter bounds, clarifying error branches, pruning obsolete prose).
2. **Surrogate Score**: Prompt a lightweight evaluator model to score each candidate against the rubric's 4 dimensions on a scale of 1 to 5.
3. **Rank**: Compute the weighted scalar score $S(skill) = \sum_i w_i \cdot s_i$.
4. **Select**: Retain the top-performing candidate $skill^*$ for outer-loop verification.

### 3. Outer-Loop Oracle Calibration via Rank Correlation

Calibrate the rubric against the true oracle using minimal rollouts:

1. Select a small probe set of candidate skills with divergent surrogate scores (e.g., top-ranked, median, and bottom-ranked).
2. Execute full task rollouts for the probe set against the true task oracle (e.g., test suite execution).
3. Compute the **Spearman rank correlation** $\rho$ between the rubric rankings and the true oracle success rates.
4. **Reweight**: If rank order disagrees (e.g., a candidate with high precondition scores failed because recovery was omitted), update criteria weights $w_i$ using gradient ascent or Nelder-Mead simplex search to maximize rank agreement with the oracle.

### 4. Gated Commit Boundary

Commit the revised skill into the persistent repository only when:
- The inner-loop dense rubric score increases by $\ge 15\%$.
- The outer-loop sparse oracle confirmation verifies that the top-ranked candidate strictly improves or matches the baseline pass rate.

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:---|:---|:---|
| **Rubric Goodharting** | Inner loop overfits to rubric criteria without achieving task success. | Outer-loop trigger: If rank correlation $\rho < 0.60$, freeze inner search and execute an immediate oracle re-alignment step. |
| **Criteria Collinearity** | Multiple rubric criteria measure the same underlying prompt attribute (e.g. length). | Enforce criteria orthogonality: ensure pairwise correlation between criteria scores remains $< 0.40$. |
| **Sparse Oracle Starvation** | Running too few oracle rollouts causes the rubric weights to drift from true task performance. | Set a mandatory budget: run 1 outer-loop calibration every 10 inner-loop revision cycles. |
