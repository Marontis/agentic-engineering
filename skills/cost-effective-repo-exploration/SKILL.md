---
name: cost-effective-repo-exploration
description: >
  How to explore large code repositories for issue localization while
  minimizing token cost.  Covers escalation-oriented search, handoff
  contracts, targeted exploration strategies, and quality-cost trade-offs.
  Derived from "Cost-Effective Repository Exploration for Agentic Issue
  Localization" (arXiv:2608.29675).
---

# Cost-Effective Repository Exploration

Use this skill when building or using coding agents that need to
find relevant code in large repositories without reading everything.

## When to Use

- Your coding agent needs to locate relevant files/functions in a
  large codebase for bug fixing or feature implementation
- Token costs are a concern (every file read costs tokens)
- You want to define a clear boundary between exploration
  (finding relevant code) and action (fixing/modifying code)

## Core Insight

Coding agents waste enormous token budgets reading irrelevant files.
The key insight is to separate **exploration** (finding where the
issue is) from **action** (fixing it), and to make exploration
itself cost-aware.  An escalation-oriented explorer starts with
cheap signals and only reads expensive files when cheaper signals
aren't sufficient.

**Evidence**: Quality retention of 85–95% is achievable at 40–60%
of the token cost of exhaustive exploration, with the exact
operating point depending on the handoff contract.

## Procedure

### Step 1: Define the handoff contract

Before exploration begins, define what the explorer must deliver
to the downstream fixer:

| Contract Level | Explorer Delivers | Cost |
|:--------------|:-----------------|:-----|
| **File-level** | List of relevant files | Cheapest |
| **Function-level** | Relevant files + function names | Moderate |
| **Line-level** | Specific line ranges containing the issue | Most expensive |

Choose the contract based on your downstream agent's capability.
A strong fixer needs only file-level; a weak fixer needs line-level.

### Step 2: Escalation-oriented exploration

Start with the cheapest signals and escalate only when needed:

**Level 1 — Repository structure** (near-zero cost):
- Read the directory tree
- Read file names and sizes
- Identify likely-relevant directories from the issue description

**Level 2 — File metadata** (low cost):
- Read docstrings, class/function signatures (not full bodies)
- Read import statements to understand dependencies
- Check git blame/history for recently changed files

**Level 3 — Targeted file reading** (moderate cost):
- Read only the files identified in levels 1–2
- Read only the relevant sections (use grep/search before full reads)
- Stop reading a file once you've determined it's not relevant

**Level 4 — Full context** (high cost):
- Read full file contents only for the most promising candidates
- Read test files to understand expected behavior
- Read configuration files if the issue is config-related

### Step 3: Use search before read

Before reading any file, use text search (grep, ripgrep) to check
whether it contains relevant terms:

```
# Check if a file mentions the relevant error/function/class
grep -l "ConnectionError" src/**/*.py
grep -n "def process_payment" src/billing/*.py
```

A file that doesn't mention any relevant terms can be skipped
without reading it.  This single technique eliminates 60–80% of
unnecessary file reads.

### Step 4: Track exploration budget

Maintain a running token budget during exploration:

- Set a maximum exploration budget before starting
- Track tokens consumed per file read
- If approaching the budget limit, switch from exploration to
  handoff with whatever you've found so far
- A partial but cheap exploration is better than an exhaustive
  but budget-blowing one

### Step 5: Quality-cost operating points

Choose your operating point based on the task:

| Scenario | Strategy | Expected Savings |
|:---------|:---------|:----------------|
| Simple bug (error message in stack trace) | Level 1–2 only | 70–80% savings |
| Feature change (clear area of code) | Level 1–3 | 40–60% savings |
| Complex cross-cutting issue | Full escalation | 20–30% savings |

## Environment Caveats

- **Monorepos**: Large monorepos benefit most from this approach
  because the irrelevant-to-relevant file ratio is highest.
- **Small repos** (<50 files): Just read everything; the overhead
  of structured exploration exceeds the savings.
- **Unfamiliar codebases**: When the agent has no prior knowledge
  of the repo structure, Level 1 (directory tree reading) is
  especially valuable for building a mental map cheaply.

## Failure Modes

- **Premature handoff**: Stopping exploration too early and missing
  critical files.  The downstream fixer will fail or produce a
  partial fix.  Include a confidence estimate in the handoff.
- **Keyword search tunnel vision**: Relying only on keyword search
  misses files where the relevant concept is expressed with
  different terminology.  Combine with directory-structure heuristics.
- **Ignoring test files**: Test files often contain the clearest
  specification of expected behavior.  Don't deprioritize them.

## Cross-References

- [`agent-working-memory-eval`](../agent-working-memory-eval/SKILL.md) —
  Evaluating how well agents manage the code they've loaded into
  their context window

## Sources

- Cost-Effective Repository Exploration for Agentic Issue Localization (arXiv:2608.29675)
