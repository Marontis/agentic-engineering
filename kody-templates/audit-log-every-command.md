---
title: "Agent command execution path missing audit log entry"
scope: "file"
path: ["**/agent*/**/*.py", "**/executor*/**/*.py", "**/sandbox*/**/*.py"]
severity_min: "high"
languages: ["python"]
buckets: ["security", "observability"]
enabled: true
---

## Instructions

When a PR adds or modifies code that executes commands on behalf of an agent,
check whether every execution path produces an audit log entry with the
required fields.

Required audit fields per command:
- The command string
- Its safety classification (safe/uncertain/unsafe)
- Whether a snapshot was created
- The execution outcome (success/failure/timeout)
- Whether rollback was triggered and its result
- Timestamp and caller identity

The audit log must be **append-only** — no UPDATE or DELETE operations on the
log table or file.

Flag the PR if:

1. A new command execution path does not call the audit logger. Look for
   `subprocess.run`, `os.system`, or equivalent without a corresponding
   `audit_log.record()` or `logger.info()` with structured fields.
2. An existing audit log call is removed or moved behind a conditional
   that could skip it (e.g. `if verbose:` or `if debug:`).
3. The audit log implementation allows modification of existing entries —
   look for SQL UPDATE/DELETE on the audit table, or file operations that
   truncate or overwrite the log.
4. Log entries are missing required fields — especially classification and
   rollback status.

Origin: research — Fault-Tolerant Sandboxing (arXiv:2512.12806) +
AI Agency Typology (arXiv:2608.20041). Audit logs build the attribution
trail needed for legal accountability of non-human agents.

## Examples

### Bad example
```python
# YOUR REAL CODE HERE — paste the actual diff.
#
# Template:
async def execute(self, cmd: str):
    result = subprocess.run(cmd, shell=True, capture_output=True)
    # No audit entry — if this command causes damage, no trail exists
    return result.stdout
```

### Good example
```python
# YOUR REAL FIX HERE — paste the corrected version.
#
# Template:
async def execute(self, cmd: str):
    tier = self.classifier.classify(cmd)
    snapshot_id = self.sandbox.snapshot() if tier == "uncertain" else None
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
        self.audit.record(
            command=cmd, tier=tier, snapshot=snapshot_id,
            outcome="success" if result.returncode == 0 else "failure",
            rollback=False,
        )
        return result.stdout
    except Exception as e:
        if snapshot_id:
            self.sandbox.rollback(snapshot_id)
        self.audit.record(
            command=cmd, tier=tier, snapshot=snapshot_id,
            outcome="error", rollback=bool(snapshot_id), error=str(e),
        )
        raise
```
