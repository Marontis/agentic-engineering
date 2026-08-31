---
title: "Self-improving agent has no documented edit scope boundary"
scope: "file"
path: ["**/agent*/**/*.py", "**/self-improve*/**/*.py", "**/meta*/**/*.py", "**/config*/**/*.py"]
severity_min: "high"
languages: ["python"]
buckets: ["security", "agent-safety"]
enabled: false
---

## Instructions

When a PR adds or modifies a self-modifying or self-improving agent system —
code where the agent can change its own prompts, tools, heuristics, or
configuration — check whether the **edit scope** is explicitly defined and
enforced.

The edit scope specifies what the agent CAN and CANNOT modify:
- ✅ Its own prompts and system messages
- ✅ Its tool selection and ordering
- ✅ Its decision heuristics and thresholds
- ⚠️ Its training data or fine-tuning config (with oversight)
- ❌ Its safety constraints and evaluation criteria
- ❌ Its own sandbox or isolation boundaries

Flag the PR if:

1. A self-improving agent is introduced without documentation of its edit
   scope. Look for classes/functions named `*Improver`, `*Evolver`,
   `*MetaAgent`, `self_modify`, or `auto_tune` without a corresponding
   scope definition.
2. The agent has write access to files or configs that control its own
   evaluation criteria (the metric it's optimizing toward).
3. The agent can modify its sandbox configuration, isolation settings,
   or safety constraints through the same interface it uses for
   self-improvement.
4. No boundary check exists between "things the agent can edit" and
   "things that constrain the agent."

Origin: research — HyperAgents (arXiv:2603.19461). Agents with editable
meta-improvement develop emergent capabilities; agents without boundaries
develop emergent risks.

## Examples

### Bad example
```python
# YOUR REAL CODE HERE — paste the actual diff.
#
# Template:
class SelfImprovingAgent:
    def improve(self):
        # Can modify anything — including its own safety checks
        for file in self.workspace.glob("**/*.py"):
            new_content = self.llm.rewrite(file.read_text())
            file.write_text(new_content)  # No scope check
```

### Good example
```python
# YOUR REAL FIX HERE — paste the corrected version.
#
# Template:
EDITABLE_SCOPE = {"prompts/*.txt", "tools/registry.yaml", "heuristics/*.json"}
FROZEN_SCOPE = {"safety/*.yaml", "eval/*.py", "sandbox/config.yaml"}

class SelfImprovingAgent:
    def improve(self):
        for file in self.workspace.glob("**/*"):
            rel = file.relative_to(self.workspace)
            if any(rel.match(p) for p in FROZEN_SCOPE):
                continue  # Cannot modify safety/eval/sandbox
            if not any(rel.match(p) for p in EDITABLE_SCOPE):
                continue  # Not in explicit edit scope
            new_content = self.llm.rewrite(file.read_text())
            file.write_text(new_content)
```
