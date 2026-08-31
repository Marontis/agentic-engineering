---
title: "Agent that proposes changes also evaluates them"
scope: "file"
path: ["**/agent*/**/*.py", "**/eval*/**/*.py", "**/self-improve*/**/*.py", "**/benchmark*/**/*.py"]
severity_min: "high"
languages: ["python"]
buckets: ["correctness", "agent-safety"]
enabled: false
---

## Instructions

When a PR adds or modifies a self-improving agent system, check whether three
concerns are cleanly separated:

1. **Exploration** — the agent proposes changes (code edits, config tweaks)
2. **Replay** — a separate environment executes the changes
3. **Evaluation** — a frozen evaluator scores the results

The agent must **never see the final evaluator**. If the same code path both
proposes changes and scores them, the agent can overfit to the metric.

Flag the PR if:

1. The same class or function both generates candidate changes AND computes
   a quality/fitness score on them. Look for `self.generate()` and
   `self.evaluate()` in the same method.
2. Evaluation metrics are defined in files the agent has write access to.
   If the agent can read `eval/metrics.py` AND has write access to that
   directory, flag it.
3. The agent's improvement loop calls the scoring function directly rather
   than through an isolated evaluation service or subprocess.
4. Test/eval code runs in the same process or container as the agent's
   modification code — no isolation boundary.

Origin: research — AI4AI-Bench (arXiv:2608.20318). The boundary guarantees
that no agent could score a candidate under the metric that decides its
result.

## Examples

### Bad example
```python
# YOUR REAL CODE HERE — paste the actual diff.
#
# Template:
class ImproverAgent:
    def run_cycle(self):
        candidate = self.llm.generate_improvement(self.source_code)
        self.source_code = candidate
        score = self.evaluate(candidate)  # Same agent scores its own work
        if score > self.best_score:
            self.best_score = score
```

### Good example
```python
# YOUR REAL FIX HERE — paste the corrected version.
#
# Template:
class ImproverAgent:
    def run_cycle(self):
        candidate = self.llm.generate_improvement(self.source_code)
        # Hand off to isolated evaluator — agent never sees scoring internals
        score = self.eval_service.score(
            candidate, sandbox_id=self.sandbox.create_isolated()
        )
        if score > self.best_score:
            self.source_code = candidate
            self.best_score = score
```
