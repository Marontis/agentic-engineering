---
title: "Filesystem write without snapshot/rollback mechanism"
scope: "file"
path: ["**/agent*/**/*.py", "**/sandbox*/**/*.py", "**/executor*/**/*.py"]
severity_min: "high"
languages: ["python"]
buckets: ["reliability", "agent-safety"]
enabled: true
---

## Instructions

When a PR adds or modifies agent execution code that writes to the filesystem
(creates, modifies, or deletes files/directories), check whether a
snapshot/checkpoint is created **before** the write and whether rollback logic
exists in the error path.

Flag the PR if:

1. A filesystem write operation (`open(..., 'w')`, `Path.write_text`,
   `shutil.rmtree`, `os.remove`, `os.rename`) appears in an agent execution
   path without a prior snapshot call.
2. A `try/except` block around filesystem writes does not restore prior state
   on failure — catching the exception and logging is not rollback.
3. An existing snapshot/rollback mechanism is removed or its error path is
   weakened (e.g. rollback moved into a `finally` that silently swallows
   exceptions).
4. The snapshot covers only partial state (e.g. one directory but not config
   files that the operation also touches).

Acceptable snapshot implementations: copy-on-write (ZFS/Btrfs), `shutil.copytree`
to a temp directory, git stash, or any mechanism that can restore the prior
state atomically.

Origin: research — Fault-Tolerant Sandboxing for AI Coding Agents
(arXiv:2512.12806). Portable `shutil.copytree` fallback takes ~1.8s for
250MB — acceptable latency for the safety guarantee.

## Examples

### Bad example
```python
# YOUR REAL CODE HERE — paste the actual diff.
#
# Template:
async def apply_fix(self, file_path: str, new_content: str):
    # No snapshot — if the fix is wrong, original content is gone
    Path(file_path).write_text(new_content)
```

### Good example
```python
# YOUR REAL FIX HERE — paste the corrected version.
#
# Template:
async def apply_fix(self, file_path: str, new_content: str):
    backup = file_path + ".bak"
    shutil.copy2(file_path, backup)
    try:
        Path(file_path).write_text(new_content)
        os.remove(backup)  # commit
    except Exception:
        shutil.move(backup, file_path)  # rollback
        raise
```
