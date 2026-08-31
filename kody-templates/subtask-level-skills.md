---
title: "Skill document captures an entire workflow instead of a single procedure"
scope: "file"
path: ["**/skills/**/*.md", "**/.gemini/**/skills/**/*.md", "**/.claude/**/skills/**/*.md"]
severity_min: "medium"
languages: []
buckets: ["agent-quality", "skill-design"]
enabled: false
---

## Instructions

When a PR adds or modifies a skill document (SKILL.md or equivalent), check
whether it describes **one reusable procedure** or an entire end-to-end
workflow.

Task-level skills (full workflows) harm agent performance by 1.2–4.1 points
versus no-memory baselines. Subtask-level skills (focused procedures)
improve performance by 0.5–1.9 points.

Flag the PR if:

1. The skill's title or description could only match **one specific project**
   — it's too specific to transfer. Look for project names, specific file
   paths, or hardcoded values in the skill body.
2. The skill describes more than 3 distinct steps that could each be their
   own skill. Look for numbered lists with 5+ items or sections covering
   unrelated concerns.
3. The skill is longer than ~500 lines — likely conflating multiple subtasks.
4. The skill's description matches **everything** ("how to write good code")
   — too vague to be useful. The test: it should match 2–10 kinds of tasks,
   not 1 and not 100.

Origin: research — Break It Down, Pass It On (arXiv:2608.20274). Validated
across 11 models, 3 benchmarks, all difficulty strata.

## Examples

### Bad example
```markdown
<!-- YOUR REAL SKILL HERE — paste the actual diff. -->

<!-- Template: -->
# Build a Complete Agent Pipeline
1. Set up the environment
2. Configure the database
3. Write the agent loop
4. Add tool definitions
5. Set up authentication
6. Deploy to Cloud Run
7. Monitor with logging
<!-- This is 7 distinct procedures crammed into one skill -->
```

### Good example
```markdown
<!-- YOUR REAL FIX HERE — paste the corrected version. -->

<!-- Template: -->
# Three-Tier Command Classification
When an agent needs to execute a command, classify it before execution:
- Safe: read-only, no side effects → execute directly
- Uncertain: filesystem writes → snapshot first
- Unsafe: network/privilege escalation → require policy approval
<!-- One focused procedure that transfers across agent architectures -->
```
