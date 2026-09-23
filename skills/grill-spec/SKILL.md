---
name: grill-spec
description: >
  Interview the user with rapid multiple-choice questions (AskUserQuestion:
  up to 4 options, one recommended, plus the automatic "Other" free-text
  choice) to turn a project idea into a foundation for a long-lived,
  maintained codebase: a living spec with ID'd domain rules, decision records,
  a milestone roadmap of small verifiable slices, and a harness-neutral
  AGENTS.md operating manual (CLAUDE.md just points to it). Use when the
  user wants to scaffold, spec, plan, or "grill me" on a new app/project
  before building it.
source: https://gist.github.com/alexziskind1/fe55f03892f3fe1d6d8cf6065c631bb8
---

# Grill Spec

Turn a vague idea ("a marketplace for renting GPUs") into the documents a
project needs to be built **and maintained** by agents and humans over months:
not a one-shot "build it all, don't stop" prompt, but a spec that stays true,
a roadmap that ships in slices, and rules of engagement for every future
session.

Read before the first question:
- `templates/` — the shape of every output file.
- `examples/silicon-exchange.md` (by alexziskind1, credited in Sources) — the
  bar for **specificity**: numeric rules, named edge cases, concrete taste.
  Match its precision, but not its one-shot framing (single prompt, "do not
  stop until", "implement end-to-end"). That framing is what this skill
  replaces.
- `examples/silicon-exchange-kit.md` — the same project as a maintained kit.

## Core insight

One-shot prompts optimise for a demo that works on day one. Maintained
projects fail differently: rules drift from code, decisions get re-argued,
agents widen scope, and nobody remembers why. So the interview still spends
its time on the same three things:

1. **The hard part**: domain rules a naive implementation gets wrong. These
   get **stable IDs** (`R-PRICE-2`) that tests, code comments, and future
   changes reference.
2. **Behavioural proof**: every rule has tests; every milestone has pass/fail
   acceptance checks.
3. **Taste**: a concrete design direction, written down once so every future
   session applies it.

…and adds three for longevity:

4. **Decisions are recorded, not re-litigated**: every real fork becomes an
   ADR with the rejected options and why.
5. **Work ships in slices**: a walking skeleton first, then the domain core,
   then vertical slices. Each is small enough to review.
6. **Agents have rules of engagement**: what they may change freely, what
   needs a human, and what "done" means for any change.

## Interview rules

- **Use AskUserQuestion for every decision.** Never ask multiple-choice
  questions in plain prose. The tool adds "Other" automatically — never add
  your own "Other" / "Something else" option. In a harness without a
  structured question tool, ask the same batch as a numbered list: each
  question with lettered options, the recommended one first, and a final
  line "or type your own answer".
- **Up to 4 questions per call, 2–4 options each.** Batch questions that don't
  depend on each other; split rounds where later options depend on earlier
  answers.
- **Always recommend.** Put your pick first with ` (Recommended)` appended to
  its label. The description says *why* in one line, specific to this project.
- **Options must be derived from the idea, not generic.** For a GPU
  marketplace, the rule options are "half-open overlap", "15-min round-up",
  "hold expiry" — not "validation", "error handling".
- **Options must be distinguishable, not three flavours of your pick.** Each
  option should reveal something different about what the user wants, so
  their choice teaches you something (ProSE). If two options would lead to
  the same outcome, merge them and add a real alternative.
- **Show only what this decision needs.** Put the trade-off in the option
  description and the detail in `preview`. Don't restate the whole draft
  (progressive disclosure).
- **Use `multiSelect: true`** for inclusion lists (surfaces, rules, a11y
  items, milestones in v1). Use single-select for forks (stack, persistence,
  design) — forks become ADRs.
- **Use `preview`** when options are visual or code-shaped: design direction
  (ASCII mockup + palette), stack (package list), data model (type sketch),
  folder layout.
- **`header` ≤ 12 chars** (e.g. "Scope", "Stack", "Rules", "Roadmap").
- **Grill vague answers.** If an "Other" answer is fuzzy ("make it fast",
  "some kind of discount"), follow up with options that pin it to a number or
  a boundary: "10% off hours beyond 24 / 10% off whole booking / tiered".
- **Offer an escape hatch** once per phase when it fits: "Use your defaults".
- **Budget: ~8–11 rounds.** Don't re-ask anything already implied. Log
  unasked decisions in the assumption ledger instead.

## Procedure

### Round 0 — Seed

If the user hasn't given an idea, ask in plain text (free-form): "What are we
building, in one or two sentences? Who's it for, and how long do you expect to
work on it?" Note volunteered constraints (stack, team, deadline).

If the current directory already has code, read its README, manifest, and any
AGENTS.md / CLAUDE.md first and treat existing choices as decided. Record them as ADRs
with status "Accepted (pre-existing)" instead of asking about them.

Silently draft all outputs from your own defaults. The interview edits that
draft. Keep an **assumption ledger** of every default chosen without asking.

### Round 1 — Shape

- **Scope**: front-end with mock data / full-stack / API or service / CLI or
  library.
- **Horizon & team**: solo side project / small team / open source with
  outside contributors / company product. Drives review gates and how much
  ceremony (ADRs, changelog, CI) is worth it.
- **Data trajectory**: mock data forever / mock now, real backend later /
  real backend from day one. "Later" means a **data-access seam** (a
  repository interface with a mock adapter) goes into M0 so swapping costs
  one adapter, not a rewrite.
- **Name & framing**: 2–3 generated names plus a one-line pitch each.

### Round 2 — Stack

One question with a `preview` per option listing exact packages, versions
policy ("latest stable at scaffold time, then pinned via lockfile"), and the
test runner. A second question only if a real fork exists. Each chosen fork
becomes an ADR; note the upgrade policy (e.g. "dependency bumps are their own
PRs").

### Round 3 — The hard part (the most important round)

Brainstorm 5–8 domain rules that a naive implementation would get wrong:

| Hardness | Example rule |
|:--|:--|
| Boundaries | Half-open ranges: 14:00 end and 14:00 start do NOT overlap |
| Rounding | Bill in 15-min increments, always round UP; 1-hour minimum |
| Money | Integer cents only; never floating point |
| Partial discounts | 10% off hours beyond the 24th, not the whole booking |
| Time & expiry | Holds expire after 10 min; real timer, visible countdown |
| State machines | Maintenance blocks new bookings, leaves confirmed ones |
| Persistence | Survives full reload; URL state survives back button |
| Determinism | Seeded PRNG for mock data; no Math.random() at render |

Ask with `multiSelect: true` (split into two questions if more than 4), each
option a fully specified rule with the number already chosen. Follow up only
where a number or boundary is a real judgment call. Each accepted rule gets:
an ID (`R-<AREA>-<n>`), the rule, the boundary case, where it lives (a pure
function in the domain module), and "tests named after the ID".

Also decide the **trap data**: records that exercise the rules (e.g. a
reservation a naive overlap check would wrongly allow).

### Round 4 — Surfaces

`multiSelect` over proposed pages/routes/commands/endpoints, each described by
what it must *do*. Always include a custom 404/error surface. Unselected items
aren't discarded — they go to the roadmap's **Later** list.

### Round 5 — Design direction

Single-select with `preview` mockups: 3 concrete directions tuned to the
domain. Then a `multiSelect` of micro-interactions and theme handling. Write
the result as **design tokens and principles** in the spec (colors, type
scale, spacing, "numbers are always monospace"), so later features stay
consistent without re-asking.

### Round 6 — Roadmap

Propose milestones as vertical slices, always starting with:

- **M0 — Walking skeleton**: repo, tooling, CI, lint/type/test commands
  green, one trivial route deployed or runnable, data seam in place. No
  features.
- **M1 — Domain core**: every `R-*` rule as pure functions with tests, trap
  data included. No UI beyond what's needed to run it.
- **M2…Mn** — one user-visible slice each (e.g. "Browse with URL filters",
  "Reserve with live quote", "Dashboard with hold countdown").

Ask: `multiSelect` of which slices are **v1** (the rest go to Later), then a
single-select on order if there's a real dependency choice. Each milestone
gets: goal, rule IDs it touches, acceptance checks (pass/fail), and explicit
out-of-scope.

### Round 7 — Rules of engagement

These go into AGENTS.md, so ask them directly (`multiSelect` where fitting):

- **Needs human approval** (recommend all): adding a runtime dependency,
  changing an `R-*` rule, changing a public API/data schema, deleting or
  weakening a test, touching CI/deploy config.
- **Workflow**: branch + PR per milestone task / trunk with small commits /
  PR per milestone. Who reviews (human, agent review, both).
- **Accessibility, responsive, offline, asset policy**: the Silicon Exchange
  list is a good default set. These become standing standards, not one-time
  checks.
- **Non-goals**: things the project will NOT do (real auth, payments, i18n…).
  Unstated non-goals are where agents invent scope.

### Round 8 — Review & write

1. Fill every file in `templates/`, folding the assumption ledger into the
   relevant sections.
2. Derive tests per rule: one per rule plus each boundary *from both sides*
   (13:59 overlaps, 14:00 doesn't), named with the rule ID. Tests must check
   behaviour, not just "doesn't throw" (PatchBench).
3. **Quality gate before saving:**
   | Gate | Question | If it fails |
   |:--|:--|:--|
   | Completeness | Every rule has an ID, a number, a boundary, tests? Every milestone has pass/fail checks and out-of-scope? | Add it, or ask one follow-up |
   | Clarity | Any subjective words left ("fast", "clean")? | Replace with a number, a reference, or a check |
   | Consistency | Contradictions ("offline" + font CDN, "front-end only" + email receipts)? Milestones depending on later ones? | Resolve, asking if it's a real choice |
   | Size | Is any milestone too big to review in one sitting? | Split it |
4. Write the files (paths in `templates/README.md`). If a file already exists,
   show a diff summary and ask before overwriting.
5. Print a ≤12-line summary: name, stack, rule IDs, v1 milestones, approval
   gates, and assumption-ledger items the user never saw.
6. Final AskUserQuestion. Writing the plan is not permission to build:
   - "Start M0 now (Recommended)": implement only M0, verify its
     acceptance checks, update the roadmap status, then stop and report.
   - "Save only".
   - "Revise a section": ask which one and re-run just that round.

## Working on later milestones

When the user comes back ("next milestone", "do M3"), don't re-interview.
Read AGENTS.md, `docs/spec.md`, `docs/roadmap.md`, then implement the next
milestone following the Definition of Done in AGENTS.md. If the request
changes a rule or reverses an ADR, run a **mini-grill**: one AskUserQuestion
round on just that change, then update the spec, the ADR (new ADR that
supersedes the old one), and the tests *before* the code.

## Harness-neutral instructions

`AGENTS.md` is the single source of truth for agent instructions; most
coding agents (Codex, Cursor, Gemini CLI, Copilot, Antigravity, etc.) read it
directly. Harness-specific files only point to it, never duplicate it:

- `CLAUDE.md`: exactly `@AGENTS.md` (Claude Code imports the file). Put
  genuinely Claude-only notes below that line, if any.
- Other harnesses that need their own file (e.g. `GEMINI.md`): write a
  pointer only when the user says they use that harness.

Never write two copies of the rules. They drift, and agents in different
harnesses end up following different rules.

## Writing style for the outputs

- Imperative, specific, numeric: "Billed in 15-minute increments, always
  rounded UP", never "handle billing correctly".
- **Bold** the phrases a lazy implementation would skip.
- Name the failure you're preventing ("Do NOT use Math.random() at render").
- AGENTS.md stays short (aim under ~120 lines). It points to docs rather than
  duplicating them; every line is something an agent would otherwise get
  wrong.
- Include in AGENTS.md a note to re-check it after major model upgrades and
  delete rules that no longer earn their place (stale scaffolding hurts
  stronger models).

## Failure modes

- **One-shot drift**: writing "implement everything, don't stop until done".
  Long-lived projects ship milestone by milestone with a human checkpoint.
- **Generic options**: if an option fits any project, replace it.
- **Too many rounds**: past 11, fold the rest into the ledger.
- **Rules without numbers or IDs**: untraceable rules drift from code.
- **Milestones that are layers** ("build all the UI"): slices must be
  user-visible and independently verifiable, M0/M1 excepted.
- **One-sided boundary tests**: test both sides of every edge.
- **Silent defaults**: the ledger goes into the ADRs and the final summary.
- **Bloated AGENTS.md**: every always-loaded line costs context in every
  future session. Move reference material to `docs/`.

## Cross-References

- [`intent-driven-sdlc-planning`](../intent-driven-sdlc-planning/SKILL.md) —
  spec.md → roadmap.md mirrors its intent → spec → plan pipeline with gates.
- [`requirements-driven-code-generation`](../requirements-driven-code-generation/SKILL.md) —
  quality gate and tests-first per milestone.
- [`agentic-review-deploy-loop`](../agentic-review-deploy-loop/SKILL.md) —
  layered review and approval gates behind the rules of engagement.
- [`knowledge-compounding-loop`](../knowledge-compounding-loop/SKILL.md) —
  why decisions and learnings live in versioned files, not chat.
- [`audit-stale-scaffolding`](../../kody-templates/audit-stale-scaffolding.md) —
  why AGENTS.md gets pruned after model upgrades.
- [`agent-human-interaction`](../../rules/agent-human-interaction.md) and
  [`agent-evaluation-quality`](../../rules/agent-evaluation-quality.md) —
  structured choices, auditable decisions, frozen tests, pass/fail checks.

## Sources

- Example prompt (specificity reference): "Compute exchange front end prompt"
  by alexziskind1 — https://gist.github.com/alexziskind1/fe55f03892f3fe1d6d8cf6065c631bb8
- ProSE: Evaluability-Aware Assistance (arXiv:2609.02242)
- String OS, partial exposure (arXiv:2608.28027)
- WiseSpec: Requirements-Driven Agents for Code Generation (arXiv:2609.00568)
- PatchBench (arXiv:2609.04075)
- Auditing Harness Tampering (arXiv:2609.00069)
- WikiSkill (arXiv:2608.27454)
- The AI-Native SDLC Playbook — https://academy.claude.com/courses/ai-native-sdlc-playbook
- Code with Claude 2026, "The capability curve" (stale scaffolding)
