# Kody rule templates — ranked index

These are **templates**, not finished rules. Each has correct YAML frontmatter,
a detection procedure, and placeholder examples. To use:

1. Copy the templates you need into your repo's `.kody/rules/` directory
2. Narrow the `path:` globs to match your project structure
3. Replace the template examples with **real code from your repo**
4. Delete this INDEX.md (or adapt it to track your rules)

Templates are derived from research papers, not from real bugs in your
codebase. They pass the **trigger gate** (each has a concrete diff pattern
to detect) but not the **recurrence gate** (they haven't caught a bug in
your project yet). Track `fired` status and question any template that stays
`untested` after three PRs touching its `path`.

17 templates in this directory; **9 enabled, 8 disabled** (per each
file's `enabled:` field, 2026-09-29). Of the 12 ranked below, the 6
Tier 1 templates are enabled and the 6 Tier 2 templates are disabled.
Five templates are not yet ranked (see "Unranked templates"). The Teams
plan has unlimited Kody Rules, so the limit is false-positive noise,
not rule count.

## Tier 1 — High-confidence templates (pass both gates)

Mechanical triggers, clear defect if recurred. Deploy these first.

| Rank | Template | Trigger | Research Origin | Enabled | Fired |
|---|---|---|---|---|---|
| 1 | [agent-cannot-modify-safety](agent-cannot-modify-safety.md) | agent code writes to safety/policy config files | ceLLMate (2512.12594) | yes | untested |
| 2 | [classify-agent-commands](classify-agent-commands.md) | `subprocess.run`/`os.system` without prior classify() | Sandbox (2512.12806) | yes | untested |
| 3 | [allowlist-network-policy](allowlist-network-policy.md) | `BLOCKED_DOMAINS` / `if domain in blocked` pattern | ceLLMate (2512.12594) | yes | untested |
| 4 | [audit-log-every-command](audit-log-every-command.md) | command execution path missing audit logger call | Sandbox (2512.12806) | yes | untested |
| 5 | [snapshot-before-uncertain-commands](snapshot-before-uncertain-commands.md) | filesystem write without snapshot/backup | Sandbox (2512.12806) | yes | untested |
| 6 | [compensating-transactions](compensating-transactions.md) | external API call without undo/compensate handler | Sandbox (2512.12806) | yes | untested |

## Tier 2 — Design-principle templates (weaker gates, still useful)

These are more judgement-heavy and are currently all **disabled**. Enable
the ones that match your codebase. Watch for false positives — if any of
these produce noise on 3 consecutive PRs without catching a real issue,
disable it. `separate-exploration-evaluation` and
`diagnostic-before-action` check search-time selection; the keep
decision defers to the acceptance gate in `rules/recursive-improvement.md`.

| Rank | Template | Trigger (weaker) | Research Origin | Enabled | Fired |
|---|---|---|---|---|---|
| 7 | [define-agent-edit-scope](define-agent-edit-scope.md) | self-improving agent code without edit scope docs | HyperAgents (2603.19461) | no | untested |
| 8 | [separate-exploration-evaluation](separate-exploration-evaluation.md) | same class both generates and scores changes | AI4AI (2608.20318) | no | untested |
| 9 | [diagnostic-before-action](diagnostic-before-action.md) | self-improvement without baseline metric collection | AI4AI (2608.20318) | no | untested |
| 10 | [score-skill-sets](score-skill-sets.md) | top-k skill selection without redundancy check | Skill Selection (2608.19993) | no | untested |
| 11 | [subtask-level-skills](subtask-level-skills.md) | skill doc describes full workflow, not one procedure | Skill Transfer (2608.20274) | no | untested |
| 12 | [text-over-code-skills](text-over-code-skills.md) | skill body is >50% code blocks | Skill Transfer (2608.20274) | no | untested |

## Unranked templates

Present in this directory but not yet ranked. Several use a different
frontmatter schema (`id`/`tier` or `name`/`author`) from the ranked ones.

| Template | Trigger | Origin | Enabled | Fired |
|---|---|---|---|---|
| [audit-stale-scaffolding](audit-stale-scaffolding.md) | scaffolding not re-evaluated since a model upgrade (exempts safety scaffolding, independent testers, loop guards, terminal denials) | Code with Claude 2026, Talk 10 | yes | untested |
| [separate-memory-from-task](separate-memory-from-task.md) | task agent also curates its own memory in the same loop | Code with Claude 2026, Talk 18 | yes | untested |
| [test-before-extending](test-before-extending.md) | extending agent-generated code without verifying the baseline | Replit ByteBench | yes | untested |
| [mutation-check-security-tests](mutation-check-security-tests.md) | new security test with no evidence it fails when the control is disabled | Attestation-Driven Development retrospective | no | untested |
| [require-adr-cost-section](require-adr-cost-section.md) | ADR without an explicit "Bad, and accepted" cost section | Attestation-Driven Development retrospective | no | untested |

## Review policy

- **Tier 1**: keep unless actively producing false positives
- **Tier 2**: disabled by default; enable per repo, disable on 3 consecutive false positives
- Update `fired` column when a template comments on a PR
- A template that fires correctly graduates from "template" to "rule" —
  replace the placeholder examples with the real diff it caught
