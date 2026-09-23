# grill-spec output map

| Template | Written to | Loaded | Purpose |
|:--|:--|:--|:--|
| `AGENTS.md` | `AGENTS.md` (repo root) | Every agent session, any harness | Operating manual: commands, standards, Definition of Done, approval gates. Short. |
| `CLAUDE.md` | `CLAUDE.md` (repo root) | Claude Code sessions | Pointer only: `@AGENTS.md`. Never duplicates the rules. |
| `spec.md` | `docs/spec.md` | On demand | Living product spec: goal, domain rules with IDs, data, surfaces, design. The source of truth for *what*. |
| `roadmap.md` | `docs/roadmap.md` | On demand | Milestones as slices with pass/fail acceptance checks and status. The source of truth for *what's next*. |
| `adr.md` | `docs/decisions/NNNN-<slug>.md` | On demand | One per real fork in the interview (stack, persistence, design direction, data seam…), including rejected options. |

Conventions:
- Rule IDs: `R-<AREA>-<n>` (e.g. `R-PRICE-2`). Never reuse an ID; retired rules
  stay in the spec marked *Retired* with the ADR that retired them.
- ADRs are append-only. Changing a decision = a new ADR that supersedes the old.
- `{braces}` are placeholders. Remove any section that doesn't apply rather
  than leaving it empty.
- If the repo already has a full `CLAUDE.md`, move its content into
  `AGENTS.md` (ask first) and leave `CLAUDE.md` as the pointer.
