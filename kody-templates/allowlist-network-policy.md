---
title: "Agent network policy uses blocklist instead of allowlist"
scope: "file"
path: ["**/proxy*/**/*.py", "**/network*/**/*.py", "**/config*/**/*.yaml", "**/config*/**/*.py", "**/sandbox*/**/*.py"]
severity_min: "critical"
languages: ["python"]
buckets: ["security", "agent-safety"]
enabled: true
---

## Instructions

When a PR adds or modifies network access control for an agent system — a
proxy configuration, a domain filter, a URL validator, or a firewall rule —
check whether the policy is an **allowlist** (block by default, explicitly
permit known domains) or a **blocklist** (allow by default, explicitly deny
known-bad domains).

Flag the PR if:

1. A network policy enumerates **blocked** domains/URLs/patterns rather than
   **allowed** ones. Look for variable names like `BLOCKED_DOMAINS`,
   `DENIED_HOSTS`, `BLACKLIST`, or logic like `if url not in blocked:`.
2. The default action for an unknown domain is to **allow** — the safe
   default is deny.
3. An agent configuration accepts arbitrary URLs without checking against
   a known-good list. Look for `requests.get(user_provided_url)` without
   a domain check.
4. A redirect-following path (e.g. `allow_redirects=True`) does not
   re-validate the redirect destination against the allowlist.

Tells: `if domain in BLOCKED:` vs `if domain not in ALLOWED:`. The second
fails safe — the first does not.

Origin: research — ceLLMate: Browser-Based AI Agent HTTP Sandboxing
(arXiv:2512.12594). Blocklist approaches always have gaps: new endpoints,
redirect chains, or subdomain variations bypass any blocklist.

## Examples

### Bad example
```python
# YOUR REAL CODE HERE — paste the actual diff.
#
# Template:
BLOCKED_DOMAINS = {"evil.com", "malware.example.org"}

def fetch_url(url: str) -> str:
    domain = urlparse(url).hostname
    if domain in BLOCKED_DOMAINS:
        raise SecurityError(f"Blocked domain: {domain}")
    # Unknown domain? Falls through — fails open
    return requests.get(url).text
```

### Good example
```python
# YOUR REAL FIX HERE — paste the corrected version.
#
# Template:
ALLOWED_DOMAINS = frozenset({"api.github.com", "arxiv.org", "pypi.org"})

def fetch_url(url: str) -> str:
    domain = urlparse(url).hostname
    if domain not in ALLOWED_DOMAINS:
        raise SecurityError(f"Domain not in allowlist: {domain}")
    resp = requests.get(url, allow_redirects=False)
    if resp.is_redirect:
        raise SecurityError("Redirect not followed — re-validate destination")
    return resp.text
```
