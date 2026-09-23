# {NAME}: Product Spec

> Living document. Update it in the same change as the code it describes.
> Last reviewed: {date}

## Goal
{What it is, for whom, the primary user actions.} {Scope line.}
It must behave like the real thing: {the 2–3 pieces of logic that must actually work}.

## Non-goals
- {Things this project will not do, e.g. real auth, payments, external APIs.}

## Domain rules
Pure, tested functions in `{domain dir}/`. Tests are named after the ID.

| ID | Rule | Boundary / edge case | Status |
|:--|:--|:--|:--|
| R-{AREA}-1 | **{Rule with numbers.}** | {Explicit edge, both sides.} | Active |
| R-{AREA}-2 | … | … | Active |

{For any rule that needs more than a table row, add a short subsection:}

### R-{AREA}-n: {name}
{Precise statement, worked example with numbers, exclusions.}

## Data
- Entities: {entity: fields with units and types; money in integer cents; status enums}.
- Source: {mock data in `{data dir}` via `{Repository}` interface | real backend}.
- Generation: {seeded PRNG, deterministic across reloads}.
- Trap data: {records a naive implementation of the rules would mishandle, and which rule each exercises}.
- Persistence: {localStorage keys + schema version and migration note | DB}.

## Surfaces
| Surface | Must do | Rules used | Milestone |
|:--|:--|:--|:--|
| {route/command} | {behaviour, state/URL/persistence requirement} | R-… | M… |
| 404 | Custom, on-brand | none | M0 |

## Design
- Direction: {concrete aesthetic}. Think {X}, not {Y}.
- Tokens: {colors incl. accent, surfaces, borders; type: heading/body/mono fonts, self-hosted; spacing scale}.
- Principles: {e.g. data-dense but calm; numbers and IDs monospace; accent used sparingly}.
- Theme: {dark-first; toggle persists; no flash on reload}.
- Motion: {micro-interactions}; respects `prefers-reduced-motion`.
- Responsive: {phone to 4K; tables collapse to cards; charts readable at 375px}.
- Accessibility: {standing requirements}.
- Assets: {no external images; inline SVG/CSS; works offline after first load}.

## Glossary
- {Term}: {meaning, used consistently in code and UI}.
