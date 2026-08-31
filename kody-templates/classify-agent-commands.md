---
title: "Agent command executed without prior safety classification"
scope: "file"
path: ["**/agent*/**/*.py", "**/executor*/**/*.py", "**/sandbox*/**/*.py"]
severity_min: "critical"
languages: ["python"]
buckets: ["security", "agent-safety"]
enabled: true
---

## Instructions

When a PR adds or modifies code that dispatches a command from an agent
(subprocess, os.system, exec, eval, or any wrapper that shells out), check
whether the command passes through a classification step **before** execution.

The classification must assign the command to one of three tiers:
- **Safe**: read-only, no side effects, no network
- **Uncertain**: filesystem writes, environment changes → must snapshot first
- **Unsafe**: network calls, privilege escalation → must require policy approval

Flag the PR if:

1. A new `subprocess.run`, `os.system`, `os.popen`, `exec()`, or equivalent
   appears without a prior call to a classify/categorize/tier function.
2. An existing classification gate is removed, commented out, or bypassed
   (e.g. a new code path that reaches execution without going through the
   classifier).
3. A command string is constructed from agent output and passed directly to
   a shell without any validation step.

The classification function does not need to be named `classify` — look for
any function that returns a tier/category/safety-level and is checked before
the execution call.

Origin: research — Fault-Tolerant Sandboxing for AI Coding Agents
(arXiv:2512.12806). Unclassified commands are the root cause of sandbox
escapes in agent execution environments.

## Examples

### Bad example
```python
# YOUR REAL CODE HERE — paste the actual diff where a command was
# executed without classification. Trim to the smallest region
# that shows the trigger.
#
# Template:
async def run_agent_step(self, action: AgentAction):
    # No classification — runs whatever the agent says
    result = subprocess.run(action.command, shell=True, capture_output=True)
    return result.stdout.decode()
```

### Good example
```python
# YOUR REAL FIX HERE — paste the corrected version.
#
# Template:
async def run_agent_step(self, action: AgentAction):
    tier = self.classifier.classify(action.command)
    if tier == CommandTier.UNSAFE:
        raise PolicyViolation(f"Blocked unsafe command: {action.command}")
    if tier == CommandTier.UNCERTAIN:
        snapshot = await self.sandbox.snapshot()
    result = subprocess.run(action.command, shell=True, capture_output=True)
    if tier == CommandTier.UNCERTAIN and result.returncode != 0:
        await snapshot.rollback()
    return result.stdout.decode()
```
