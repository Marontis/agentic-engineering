# {NAME}

{One-sentence pitch.} {Scope line, e.g. "Front-end only; all data is typed mock data behind a repository interface."}

Read `docs/spec.md` for what the product does and `docs/roadmap.md` for what's next.
Decisions and their reasons are in `docs/decisions/`. Don't re-argue them without a new ADR.

## Commands
- Install: `{install}`
- Dev: `{dev}`
- Test: `{test}` (single file: `{test single}`)
- Typecheck / lint: `{typecheck}` / `{lint}`
- Build: `{build}`

## Layout
- `{domain dir}/`: pure domain rules (`R-*`). No framework imports, no I/O, no clock reads (inject `now`).
- `{data dir}/`: {mock data + repository interface / adapters}.
- `{ui dir}/`: {routes/components}.
- Tests sit {next to the code | in tests/}. Rule tests are named after the rule ID, e.g. `R-PRICE-2: rounds 61 min up to 75`.

## Standards (always)
- {Language strictness, e.g. TypeScript strict; no `any`. Use `unknown` and narrow.}
- Money is integer {cents}. Never floating point.
- {Determinism rule, e.g. no Math.random() at render; seeded PRNG only in data generation.}
- {Design tokens live in `{path}`; numbers and IDs are monospace; one accent color.}
- {Accessibility: keyboard reachable, visible focus, labelled controls, aria-label on icon buttons, text alternative for every chart.}
- {Asset/offline policy.}
- No dead controls: a control either works or isn't rendered. Unfinished features stay off the UI (not routed, or behind a flag in `{flags path}`).
- `TODO` only with a roadmap or issue reference: `TODO(M4): …`. No stubs in shipped code paths.

## Definition of Done (every change)
1. `{test}`, `{typecheck}`, `{lint}`, `{build}` all pass.
2. New or changed behaviour has tests; boundary cases tested from both sides.
3. If a rule changed: `docs/spec.md` updated first, then tests, plus an ADR.
4. `docs/roadmap.md` status updated if a milestone check was completed.
5. Summary to the human: what changed, what was verified (with command output), anything deferred.

## Ask a human before
- Adding a runtime dependency (dev deps: {allowed | also ask}).
- Changing or retiring an `R-*` rule, or reversing an ADR.
- Changing {public API | persisted data shape | URL structure}.
- Deleting, skipping, or weakening a test. Add cases freely; never remove one to get green.
- Editing CI/deploy config or this approval list.
- Starting the next milestone. Finish one, report, stop.

## When stuck
Read the error and fix the cause. Don't delete a feature or a test to get a green run.
If blocked after a real attempt, stop and report what you tried.

## Workflow
{Branching/PR policy, reviewer (human / agent review / both).} {Commit style.}

<!-- Maintenance: this is the only agent-instructions file; CLAUDE.md and similar just point here.
Re-read this file after major model upgrades or every ~3 months.
Delete rules that no longer prevent a real mistake; stale scaffolding hurts stronger models. -->
