---
title: "Agent code writes to its own safety configuration"
scope: "file"
path: ["**/agent*/**/*.py", "**/sandbox*/**/*.py", "**/policy*/**/*.py", "**/config*/**/*.py"]
severity_min: "critical"
languages: ["python"]
buckets: ["security", "agent-safety"]
enabled: true
---

## Instructions

When a PR adds or modifies agent code, check whether the agent has write
access to any file, database record, or API endpoint that controls its own
safety boundaries — rate limits, allowlists, interception rules, sandbox
configuration, or audit settings.

The safety layer must be **read-only to the agent process**. If the agent
can reconfigure its own proxy, allowlist, or policy, the sandbox provides
no actual isolation guarantee.

Flag the PR if:

1. Agent code writes to a configuration file that controls safety behaviour
   (proxy rules, domain allowlists, rate limits, audit toggles). Look for
   `open(config_path, 'w')`, `Path(policy_file).write_text()`, or ORM
   updates to policy tables.
2. An API endpoint allows the agent to update its own quotas, rate limits,
   or access scope. Look for routes that accept agent credentials AND modify
   safety-related database rows.
3. Safety configuration is loaded from a path the agent can write to —
   e.g. the agent's working directory rather than a read-only mount.
4. Environment variables controlling safety are set or overridden within
   agent execution code (`os.environ["SAFETY_DISABLED"] = "1"`).

Origin: research — ceLLMate (arXiv:2512.12594). If the agent can
reconfigure the proxy, allowlist, or interception policy, the sandbox
provides no guarantee.

## Examples

### Bad example
```python
# YOUR REAL CODE HERE — paste the actual diff.
#
# Template:
class AgentExecutor:
    def update_config(self, new_limits: dict):
        # Agent can raise its own rate limit — no guard
        self.config["rate_limit"] = new_limits.get("rate_limit", 100)
        self.config.save()  # writes to the same config the safety layer reads
```

### Good example
```python
# YOUR REAL FIX HERE — paste the corrected version.
#
# Template:
class AgentExecutor:
    def __init__(self, config_path: Path):
        # Config loaded from read-only mount, not agent workspace
        self._config = _load_readonly(config_path)

    @property
    def rate_limit(self) -> int:
        return self._config["rate_limit"]  # no setter — agent can't modify
```
