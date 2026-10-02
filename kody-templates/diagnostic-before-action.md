---
title: "Self-improvement proposes changes without collecting baseline metrics first"
scope: "file"
path: ["**/agent*/**/*.py", "**/self-improve*/**/*.py", "**/optimize*/**/*.py", "**/train*/**/*.py"]
severity_min: "medium"
languages: ["python"]
buckets: ["correctness", "agent-quality"]
enabled: false
---

## Instructions

When a PR adds or modifies self-improvement or optimization logic in an agent
system, check whether the agent **measures before changing**.

The diagnostic loop must be:
```
Read current state → Name the problem → Change the mechanism → Measure effect
```

The exceptional agent submissions in AI4AI-Bench all built diagnostic
instruments before proposing changes. Agents that skip measurement produce
changes that cannot be evaluated.

Flag the PR if:

1. An improvement function modifies code, config, or parameters without
   first recording baseline metrics. Look for `self.modify()` or
   `self.rewrite()` without a prior `self.measure()` or `self.baseline()`.
2. A training or optimization loop runs without logging metrics per
   iteration — loss values, gradient norms, success rates, or whatever
   the relevant signal is.
3. The improvement claims "before/after" comparison but the "before" is
   not captured programmatically — it relies on a human checking logs
   after the fact.
4. Metrics collection is conditional (`if debug:` or `if verbose:`) rather
   than always-on in the improvement path.

Origin: research — AI4AI-Bench (arXiv:2608.20318). 53.6% of agent
submissions stayed entirely on the run side (bounded improvements).
The ones that reached the learning side scored 0.226 vs 0.126.

Scope: the score comparison in this template is **search-time
selection**. Keeping a change defers to `rules/recursive-improvement.md`
"DO: Pass every self-modification through one acceptance gate": accept
a change only if it shows no regression beyond a noise margin δ on
previously-correct cases and held-out tasks, where δ is estimated from
repeated runs of the unchanged baseline; the negative security testbed
is always strict (zero tolerance, no margin). Also flag code whose keep
decision is a single `score > baseline` comparison with no gate.

## Examples

### Bad example
```python
# YOUR REAL CODE HERE — paste the actual diff.
#
# Template:
class Optimizer:
    def improve(self):
        # No baseline — how do we know if this helped?
        new_prompt = self.llm.rewrite(self.system_prompt, goal="be better")
        self.system_prompt = new_prompt
```

### Good example
```python
# YOUR REAL FIX HERE — paste the corrected version.
#
# Template:
class Optimizer:
    def improve(self):
        baseline = self.benchmark.run(self.system_prompt)
        self.metrics.record("before", baseline)

        new_prompt = self.llm.rewrite(
            self.system_prompt,
            goal=f"improve on: {baseline.worst_category}",
        )

        result = self.benchmark.run(new_prompt)
        self.metrics.record("after", result)

        # Search-time selection: is this candidate worth gating?
        if result.score > baseline.score + self.delta:  # δ from ≥3 baseline runs
            # Keep decision: the shared acceptance gate (previously-correct
            # cases + held-out tasks within δ; security testbed strict).
            if self.acceptance_gate.passes(new_prompt, baseline_prompt=self.system_prompt):
                self.system_prompt = new_prompt
                self.metrics.record("accepted", delta=result.score - baseline.score)
                return
        self.metrics.record("rejected", delta=result.score - baseline.score)
```
