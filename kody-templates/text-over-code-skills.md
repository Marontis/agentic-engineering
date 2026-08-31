---
title: "Skill body is executable code instead of natural-language procedure"
scope: "file"
path: ["**/skills/**/*.md", "**/.gemini/**/skills/**/*.md", "**/.claude/**/skills/**/*.md"]
severity_min: "medium"
languages: []
buckets: ["agent-quality", "skill-design"]
enabled: false
---

## Instructions

When a PR adds or modifies a skill document, check whether the body is
primarily **natural-language workflow notes** or **executable code**.

Code skills lock in implementation details from the source context — wrong
parameters, namespace conflicts, and library assumptions that don't transfer.
Text skills transfer better than code skills at every granularity level and
difficulty stratum tested.

Flag the PR if:

1. More than 50% of the skill body (by line count) is inside code blocks.
   Code should illustrate, not dominate.
2. Code blocks import project-specific modules (`from myproject.utils import`)
   or reference specific file paths (`/app/config/settings.py`).
3. Code blocks are presented as copy-paste-ready without surrounding prose
   explaining the pattern, when to use it, or how to adapt it.
4. The skill would **only work** if the code were pasted verbatim into one
   specific codebase.

Exception: code is acceptable when it illustrates a specific algorithm or
data structure that would be ambiguous in prose (e.g. a BPS selection
algorithm). But even then, it should be marked as illustrative.

Origin: research — Break It Down, Pass It On (arXiv:2608.20274). Text
skills transfer better than code skills at both task-level and subtask-level
induction.

## Examples

### Bad example
```markdown
<!-- YOUR REAL SKILL HERE — paste the actual diff. -->

<!-- Template: -->
# Rate Limiter Setup

` ` `python
from myapp.middleware import RateLimiter
from myapp.config import REDIS_URL

limiter = RateLimiter(backend=REDIS_URL, limit=100, window=60)
app.add_middleware(limiter)
` ` `
<!-- Only works in one codebase. No explanation of when/why. -->
```

### Good example
```markdown
<!-- YOUR REAL FIX HERE — paste the corrected version. -->

<!-- Template: -->
# Sliding Window Rate Limiting

Apply per-key rate limiting using a sliding window algorithm. Each API key
gets N requests per window. On each request:

1. Compute the current window: `floor(timestamp / window_seconds)`
2. Look up or create the counter for (key_hash, window)
3. If counter >= limit, reject with 429
4. Otherwise increment and proceed

Use the key hash, never the raw key, as the counter key. Store counters
in a fast store (Redis, SQLite WAL mode) — the rate limiter must not
become the bottleneck.
```
