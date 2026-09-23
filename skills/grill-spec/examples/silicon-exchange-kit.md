<!--
Worked example: the Silicon Exchange prompt (examples/silicon-exchange.md,
by alexziskind1) re-expressed as a grill-spec kit for a maintained project.
Excerpts only: enough to calibrate precision and shape, not a full kit.
Assumed answers: small team, "mock now, real backend later", GitHub PRs with
agent + human review.
-->

# Silicon Exchange: grill-spec kit (excerpts)

## What changed from the one-shot prompt

| One-shot prompt | Maintained kit |
|:--|:--|
| "Implement it end-to-end… DO NOT STOP" | M0–M6 roadmap; stop and report after each milestone |
| Rules as a numbered list | Rules with stable IDs; tests named after them |
| "Use exactly this stack unless it breaks" | ADR-0001 with rejected options and a revisit trigger |
| Mock data in `/data` | `ListingRepository` interface + mock adapter (ADR-0002) |
| QUALITY BAR paragraph | Standards + Definition of Done + approval gates in AGENTS.md (CLAUDE.md is `@AGENTS.md`) |
| "No TODO comments" | `TODO(M5): …` allowed; must reference a roadmap item |
| "No dead buttons" | A control works or isn't rendered; unfinished features aren't routed |

---

## docs/spec.md: Domain rules (excerpt)

| ID | Rule | Boundary / edge case | Status |
|:--|:--|:--|:--|
| R-BOOK-1 | **Ranges are half-open `[start, end)`.** A listing can't hold two overlapping reservations. Cancelled and expired ones don't count. | 13:00–14:00 vs 14:00–15:00: no overlap. 13:00–14:01 vs 14:00–15:00: overlap. | Active |
| R-BOOK-2 | **Maintenance blocks new reservations** but leaves existing confirmed ones alone. | Confirmed booking on a listing that goes into maintenance stays confirmed. | Active |
| R-HOLD-1 | **Holds expire after 10 minutes** unconfirmed, flip to `expired`, and free the slot. | 9:59 held → still held. 10:00 → expired. | Active |
| R-PRICE-1 | **Billed in 15-minute increments, always rounded UP.** | 61 min bills as 75. 60 min bills as 60. | Active |
| R-PRICE-2 | **Minimum billable block is 1 hour.** | 10 min bills as 60. | Active |
| R-PRICE-3 | **Beyond 24 continuous hours, 10% off each hour past the 24th**, not the whole booking. | 24h: no discount. 24h15m: discount on 15 min only. | Active |
| R-PRICE-4 | **Money is integer cents.** Discount is computed on the total discounted amount, rounded half-up to the cent. | 10% of 333¢ → 33¢; 10% of 335¢ → 34¢. | Active |
| R-PERSIST-1 | Reservations persist to localStorage under `sx.reservations.v1` and survive a full reload. | Unknown schema version → migrate or start empty, never crash. | Active |

Note R-PRICE-4: the one-shot prompt says "never use floating point" but doesn't
say how to round 10% of an odd amount. The mini-grill asks, and the answer
becomes part of the rule.

Trap data: on the same listing, confirmed `rsv-007` is 13:00–16:00, and the
seeded "try to book" fixture is 12:00–17:00. The new range fully contains the
existing one, so a naive check that only asks "does the new start or end fall
inside an existing booking?" wrongly allows it. It exercises R-BOOK-1.

---

## docs/roadmap.md (excerpt)

### M0: Walking skeleton [ ]
- [ ] `npm ci` from a clean clone; `npm test`, `npm run typecheck`, `npm run lint`, `npm run build` pass
- [ ] GitHub Actions runs all four on every PR
- [ ] `ListingRepository` interface + `MockListingRepository` returning 24 typed, seeded listings
- [ ] App shell, dark/light tokens with no flash on reload, self-hosted fonts, custom 404

Out of scope: any R-* rule, any feature page.

### M1: Domain core [ ]
- [ ] Tests for R-BOOK-1..2, R-HOLD-1, R-PRICE-1..4 written first, seen failing, then passing
- [ ] Each boundary tested from both sides (see spec table)
- [ ] `rsv-007` containment trap covered by an R-BOOK-1 test
- [ ] Clock injected (`now: Date` parameter), no `Date.now()` in `domain/`

Out of scope: UI.

### M2: Browse [ ]
Rules: none (filter/sort reducer gets its own tests)
- [ ] Search, region, memory range, status filters and sort by price/memory/TFLOPS/utilization
- [ ] Filter state lives in the URL and survives refresh and browser back
- [ ] Empty state when nothing matches
- [ ] Cards reachable and operable by keyboard

### M3: Listing detail + live quote [ ]
Rules: R-BOOK-1, R-BOOK-2, R-PRICE-1..4
- [ ] Quote recalculates while dragging the range; breakdown shows base, rounding, discount
- [ ] 7-day calendar blocks taken slots; maintenance listings can't be booked
- [ ] Utilization chart has hover tooltip and a text summary; readable at 375px

### M4: Dashboard + holds [ ] · M5: Compare [ ] · M6: Home + polish [ ]
{…same shape…}

### Later
- Real backend adapter (ADR-0002 seam makes this one adapter)
- Auth, payments: non-goals for v1

---

## docs/decisions/0002-data-seam.md (excerpt)

- Status: Accepted
- Context: v1 is front-end only, but the team expects a real API within ~6 months.
- Decision: All reads/writes go through `ListingRepository` / `ReservationRepository`.
  UI never imports from `data/mock/` directly.
- Options considered: **Repository interface** (swap cost = one adapter) ·
  Import mock arrays directly (fastest now, rewrite later) · MSW mock API
  (realistic, but heavier than v1 needs).
- Consequences: slightly more boilerplate in M0. Revisit when the real API exists.

---

## AGENTS.md (excerpt)

## Ask a human before
- Adding a runtime dependency.
- Changing or retiring an R-* rule, or reversing an ADR.
- Changing the localStorage schema (`sx.*.v1`) or URL query parameters.
- Deleting, skipping, or weakening a test.
- Starting the next milestone.
