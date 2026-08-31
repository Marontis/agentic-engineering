# Agent Sandbox Specification Template

> Fill in this template when designing an execution sandbox for AI agents.
> Each section surfaces research-backed decision points. Defaults are
> marked where the evidence clearly favors one option.

---

## 1. Threat Model & Scope

### What type of agent is this sandbox for?

- [ ] Browser-based agent (web navigation, form filling, API calls)
- [ ] Coding agent (file operations, command execution, package management)
- [ ] Research agent (web search, document retrieval, data analysis)
- [ ] Multi-modal agent (combination of the above)
- [ ] Other: ___

### What are the primary risks?

- [ ] Unauthorized network access (data exfiltration, external API calls)
- [ ] Filesystem damage (destructive writes, configuration corruption)
- [ ] Resource exhaustion (infinite loops, memory leaks, fork bombs)
- [ ] Privilege escalation (sudo, container escape, host access)
- [ ] Social engineering (email sends, message posts, account changes)
- [ ] Other: ___

### What is the isolation boundary?

- [ ] Process-level (separate process, same OS)
- [ ] Container-level (Docker/OCI, network namespace)
- [ ] VM-level (full hypervisor isolation)
- [ ] Browser-level (extension sandbox, webRequest interception)

> **Research note**: The isolation level should match the risk profile.
> Browser agents benefit from HTTP-layer interception (invisible to page JS,
> catches all requests). Coding agents benefit from filesystem snapshots with
> container isolation. (arXiv:2512.12594, arXiv:2512.12806)

---

## 2. Command Classification

### How will agent commands be classified?

**Default: Three-tier classification** (recommended by research)

| Tier | Definition | Action | Examples |
|:-----|:----------|:-------|:--------|
| Safe | Read-only, no side effects | Execute directly | `ls`, `cat`, `git status`, `grep` |
| Uncertain | Local writes, env changes | Snapshot → execute → commit/rollback | `pip install`, `git commit`, file writes |
| Unsafe | Network, process mgmt, privilege | Block or require approval | `curl`, `ssh`, `sudo`, `rm -rf /` |

### What classifier will you use?

- [ ] Pattern-matching rules (fastest, least flexible)
- [ ] Small language model (SLM) classifier (good balance)
- [ ] Main reasoning model with classification prompt (most accurate, most expensive)
- [ ] Hybrid: rules for obvious cases, SLM for edge cases

### Classification overrides:

- [ ] Can the user override a classification at runtime? Y/N
- [ ] Can the agent request an override? Y/N
- [ ] Are overrides logged? (must be Y)

> **Pitfall**: Never let the agent modify its own classification rules.
> The safety layer must be outside the agent's edit scope. (arXiv:2512.12594)

---

## 3. Snapshot & Rollback

### Snapshot strategy:

- [ ] Copy-on-write (ZFS/Btrfs) — near-zero overhead, requires CoW filesystem
- [ ] Full copy (`shutil.copytree`) — ~1.8s for 250MB, portable
- [ ] Git-based (commit before, reset on failure) — works for code-only workspaces
- [ ] Container checkpoint (CRIU) — heavy but captures full process state
- [ ] No snapshot (acceptable only for safe-only commands)

### When to snapshot:

- [ ] Before every command (safest, highest overhead)
- [ ] **Before every uncertain or unsafe command** (recommended default)
- [ ] Before each agent "turn" or planning step
- [ ] On explicit user request only

### Rollback triggers:

- [ ] Command returns non-zero exit code
- [ ] Command exceeds time limit
- [ ] Command output matches error patterns
- [ ] Agent explicitly requests rollback
- [ ] User explicitly requests rollback

### External API handling:

> **Critical pitfall**: Filesystem rollback does NOT undo external API calls.
> You MUST design compensating transactions for every external operation.
> (arXiv:2512.12806)

- [ ] List all external APIs the agent may call: ___
- [ ] For each, define the compensating transaction:

| API Call | Compensating Transaction | Automated? |
|:---------|:------------------------|:-----------|
| Example: send email | Send retraction email | No (manual) |
| Example: POST to API | DELETE endpoint | Yes |
| | | |

---

## 4. Network Policy

### Default network stance:

- [ ] **Allowlist** (block all, explicitly permit known-safe domains) — recommended
- [ ] Blocklist (allow all, block known-bad domains) — not recommended
- [ ] No network access (fully air-gapped)
- [ ] Full network access (no sandbox) — not recommended for autonomous agents

### Interception layer:

- [ ] **HTTP-layer interception** (webRequest API, proxy) — recommended for browser agents
- [ ] DNS-level blocking
- [ ] Firewall rules (iptables/nftables)
- [ ] Application-level middleware

> **Research note**: HTTP-layer interception catches all requests regardless
> of how they're triggered, is invisible to page-level JavaScript, and cannot
> be bypassed by client-side code. (arXiv:2512.12594)

### Allowed domains:

| Domain | Purpose | Max requests/min |
|:-------|:--------|:----------------|
| | | |

---

## 5. Performance & Scheduling

### Sandbox lifecycle:

- [ ] On-demand creation (simpler, higher latency per step)
- [ ] **Pre-forked pool** (recommended for multi-step agents)
- [ ] Persistent sandbox (reused across tasks)

### Speculative scheduling:

- [ ] Agent generates plan → speculatively prepare sandboxes for likely branches
- [ ] Kill unused sandboxes when agent commits to a branch
- [ ] Budget: max ___ concurrent speculative sandboxes

> **Research note**: Moving sandbox creation off the critical path via
> preforking eliminates 100ms–2s of latency per agent step. (arXiv:2607.23933)

### Resource limits:

| Resource | Limit | Action on exceed |
|:---------|:------|:----------------|
| CPU time per command | ___ seconds | Kill + rollback |
| Memory per sandbox | ___ MB | Kill + rollback |
| Disk writes per command | ___ MB | Kill + rollback |
| Total sandbox lifetime | ___ minutes | Checkpoint + teardown |

---

## 6. Audit & Accountability

### Logging requirements:

Every command must be logged with:
- [ ] Timestamp
- [ ] Command text
- [ ] Safety classification (safe/uncertain/unsafe)
- [ ] Whether snapshot was created
- [ ] Execution outcome (success/failure/timeout/killed)
- [ ] Whether rollback was triggered
- [ ] Rollback result (if applicable)
- [ ] Token count consumed

### Log retention:

- [ ] Duration: ___
- [ ] Storage location: ___
- [ ] Access controls: ___

> **Research note**: These logs build the infrastructure for legal
> accountability of non-human agents. Design them to answer "what did
> the agent do, when, and what was the effect?" (arXiv:2608.20041)

---

## 7. Pitfall Checklist

Before finalizing the sandbox design, verify:

- [ ] The agent cannot modify its own safety classification rules
- [ ] The agent cannot modify the network allowlist/blocklist
- [ ] The agent cannot escape the isolation boundary
- [ ] Every external API call has a defined compensating transaction
- [ ] Snapshot overhead is acceptable for the target latency
- [ ] Rollback is tested and verified for all uncertain command types
- [ ] Audit logs capture enough detail for post-incident attribution
- [ ] The sandbox works correctly when the agent fails (crash, timeout, OOM)

---

## Sources

- ceLLMate: arXiv:2512.12594
- SpecBox: arXiv:2607.23933
- Fault-Tolerant Sandboxing: arXiv:2512.12806
- AI Agency Typology: arXiv:2608.20041
