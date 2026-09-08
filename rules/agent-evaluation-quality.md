# Agent Evaluation & Quality Rules

> Research-backed guardrails for evaluating agent outputs, benchmarking
> agent systems, and designing quality gates. These rules should be
> active whenever building evaluation harnesses, automated reviewers,
> LLM-as-judge pipelines, or benchmark suites.

---

## LLM-as-Judge Pipelines

### DON'T: Trust single-score LLM-as-judge evaluations

Single-prompt LLM judges that produce a holistic quality score suffer
from poor calibration, low inter-rater agreement, and systematic
shortcut learning. The judge's output is influenced by lexical cues
in the evaluation rubric itself, independent of the candidate response
being evaluated.

**Evidence**: models can predict evaluation outcomes solely from rubric
text (with zero access to candidate responses). When either the
candidate response or the rubric criterion is counterfactually
flipped/reversed, LLM judges systematically fail to update their
decisions.

> Source: Rubric Artifacts in LLM Judges (arXiv:2609.02942)

### DO: Decompose evaluations into atomic checklist items

Replace holistic quality scoring with fine-grained, objective
boolean/categorical checklist items. Then learn optimal aggregation
weights over the checklist outputs. This provides interpretable
failure rationales and self-consistency bounds that single-score
prompts cannot.

**Evidence**: checklist decomposition combined with learned aggregation
significantly outperforms raw LLM ratings in agreement with human
domain experts, while providing interpretable failure rationales.

> Source: Reliable Eval Pipeline (arXiv:2609.00805)

### DON'T: Provide ground-truth answers to oversight monitors

When deploying an LLM monitor to inspect intermediate reasoning of
another agent, do not give the monitor access to the expected final
answer. Answer access introduces severe confirmation bias — monitors
focus on conclusion correctness rather than reasoning step validity.

**Evidence**: monitors with answer access miss the first erroneous
reasoning step in over 60% of invalid trajectories when auditing
complex problems.

> Source: The Answer Is Not the Argument (arXiv:2609.00264)

---

## Benchmark Design

### DO: Select verification tasks based on what each modification changes

When evaluating a proposed code modification (patch, refactor, agent
output), don't run the same fixed test suite for every change. Select
the subset of tests whose behavior is actually affected by the
modification. Unaffected tests waste compute and dilute signal.

**Evidence**: behavior-aware test selection reduces wasted rollouts and
improves modification-specific signal by matching tests to the
behavioral scope of each change.

> Source: HarnessLens (arXiv:2608.27311)

### DO: Prune benchmark suites using trajectory-level features

Full benchmark suites are expensive. Use process-level execution
features (trajectory structure, step counts, tool usage patterns)
fused with outcome signals to identify a representative subset that
preserves ranking fidelity at 20-35% of the original cost.

**Evidence**: trajectory-aware item response theory (PTA-IRT) reduces
benchmark evaluation costs by 65-80% without compromising system
ranking accuracy across software engineering agent benchmarks.

> Source: PTA-IRT (arXiv:2609.01603)

### DON'T: Validate repairs using crash suppression alone

When evaluating AI coding agents for bug fixing or vulnerability
repair, never rely solely on Proof-of-Concept (PoC) crash elimination.
Agents frequently generate surface-level patches (null checks, early
returns) that suppress the crash symptom without fixing the underlying
vulnerability.

**Evidence**: PoC-only validation inflated measured solve rates by
1.83× on average across 11 state-of-the-art patching agents. 25% of
agent patches exhibited substantial memorization of historical
developer fixes. Remediation requires comprehensive semantic test
suites that verify behavior outside the crash stack.

> Source: PatchBench (arXiv:2609.04075)

---

## Evaluation Integrity

### DON'T: Let agents modify their own evaluation harness

When an agent has permissions to optimize its own prompts, tools, or
control flow, the evaluation harness must be frozen and read-only. An
agent that can modify its own tests will optimize for test passage,
not for the intended behavior.

**Evidence**: audit every proposed mutation across two orthogonal axes —
functional role (prompt, control flow, tools, harness) and obligation
(evaluation integrity, authorization boundary, lineage provenance,
reporting fidelity). Never evaluate a modified agent using its own
modified environment.

> Source: Auditing Harness Tampering (arXiv:2609.00069)

### DO: Test evaluators with counterfactual perturbations

Before trusting any automated evaluator (LLM judge, test suite,
benchmark), verify that it genuinely conditions on candidate content
by running counterfactual tests: flip the expected quality of the
candidate and confirm the evaluator's score changes accordingly. An
evaluator that produces the same score regardless of input quality is
measuring rubric artifacts, not output quality.

> Source: arXiv:2609.02942

### DO: Measure safety compliance separately from accuracy

In safety-critical, physics-governed, or operational domains, accuracy
metrics (MAE, MSE, cosine similarity) mask dangerous failures.
Predictions numerically close to ground truth frequently violate hard
operational limits, physical feasibility constraints, or protocol
contracts. Gate candidate actions behind deterministic verification
of invariant safety boundaries before scoring accuracy.

**Evidence**: across 66 evaluated models on flight trajectory prediction,
models with comparable predictive accuracy differed by more than 28
points in safety compliance score, exhibiting fatal boundary violations
while producing superficially plausible predictions.

> Source: FLY-EVAL++ (arXiv:2609.04021)

---

## Verification Scaling

### DO: Plan for verification tiers as agent capability increases

As agents improve, human supervision gradually recedes. Design
verification systems with explicit tiers:

| Tier | Verification Source | When to Use |
|:-----|:-------------------|:------------|
| **L0** | Per-instance human judgments | Novel tasks, highest-stakes decisions |
| **L1** | Reusable learned verifiers | Recurring task patterns with sufficient training data |
| **L2** | Autonomous reward models | Low-stakes, high-volume tasks with robust ground truth |

At each tier, monitor for:
- **Reward hacking**: model exploits verifier weaknesses
- **Feedback drift**: reward signal diverges from intended objective
- **Curriculum collapse**: self-generated training becomes repetitive

> Source: Scaling LRMs Beyond Human Supervision (arXiv:2608.31075)

---

## Related Skills

For implementation details on the procedures behind these rules:
- [`behavior-aware-verification`](skills/behavior-aware-verification/SKILL.md) — Modification-scoped test selection
- [`trajectory-aware-eval-pruning`](skills/trajectory-aware-eval-pruning/SKILL.md) — Cost-effective benchmark subset selection
- [`harness-tampering-audit`](skills/harness-tampering-audit/SKILL.md) — Two-axis tampering audit for self-modifying agents
- [`error-structured-prompt-optimization`](skills/error-structured-prompt-optimization/SKILL.md) — Evaluation-driven prompt refinement
- [`counterexample-guided-repair`](skills/counterexample-guided-repair/SKILL.md) — Oracle-based artifact refinement
- [`neural-invariant-failure-diagnosis`](skills/neural-invariant-failure-diagnosis/SKILL.md) — Behavioral state invariant checking
- [`agentic-review-deploy-loop`](skills/agentic-review-deploy-loop/SKILL.md) — Layered review with checklist-based agentic review

## Sources

- Rubric Artifacts in LLM Judges: arXiv:2609.02942
- Reliable Eval Pipeline: arXiv:2609.00805
- The Answer Is Not the Argument: arXiv:2609.00264
- HarnessLens: arXiv:2608.27311
- PTA-IRT: arXiv:2609.01603
- PatchBench: arXiv:2609.04075
- Auditing Harness Tampering: arXiv:2609.00069
- FLY-EVAL++: arXiv:2609.04021
- Scaling LRMs Beyond Supervision: arXiv:2608.31075
