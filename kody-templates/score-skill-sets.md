---
title: "Skill selection ranks individually instead of scoring the set"
scope: "file"
path: ["**/skills/**/*.py", "**/selection*/**/*.py", "**/retrieval*/**/*.py", "**/context*/**/*.py"]
severity_min: "medium"
languages: ["python"]
buckets: ["agent-quality", "performance"]
enabled: false
---

## Instructions

When a PR adds or modifies skill/tool selection logic — the code that decides
which skills or context documents to load into an agent's prompt — check
whether it evaluates skills **as a set** or **individually**.

Top-k-by-relevance (rank each skill independently, pick the top N) reaches
the optimal skill set on only 7.5% of instances. Adding a redundant skill
costs ~225 tokens for +1pp gain. Adding a semantically similar but irrelevant
skill drops success by 23pp.

Flag the PR if:

1. Skills are scored independently (e.g. cosine similarity per skill) and
   then selected by top-k without checking for redundancy within the
   selected set.
2. There is no token budget accounting — skills are loaded without tracking
   how many tokens the total set consumes. Look for missing
   `total_tokens += len(skill)` or equivalent.
3. Two skills with overlapping capability descriptions are both loaded
   without a deduplication or complementarity check.
4. The selection logic uses only embedding similarity without any set-level
   optimization (BPS algorithm, greedy submodular, or equivalent).

This matters most when the skill library has 10+ skills with overlapping
capabilities and a binding token budget.

Origin: research — Optimal Skill Selection for LLM Agents
(arXiv:2608.19993). BPS algorithm with (1-1/e, 1) guarantee.

## Examples

### Bad example
```python
# YOUR REAL CODE HERE — paste the actual diff.
#
# Template:
def select_skills(query: str, library: list[Skill], top_k: int = 5):
    scored = [(skill, cosine_sim(query, skill.embedding)) for skill in library]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [s for s, _ in scored[:top_k]]  # No redundancy check, no token budget
```

### Good example
```python
# YOUR REAL FIX HERE — paste the corrected version.
#
# Template:
def select_skills(query: str, library: list[Skill], token_budget: int):
    selected = []
    tokens_used = 0
    candidates = sorted(library, key=lambda s: cosine_sim(query, s.embedding), reverse=True)
    for skill in candidates:
        if tokens_used + skill.token_count > token_budget:
            continue
        # Check complementarity: does this skill add capability the set lacks?
        if any(overlap(skill, existing) > 0.8 for existing in selected):
            continue  # redundant — skip
        selected.append(skill)
        tokens_used += skill.token_count
    return selected
```
