<!--
Reference example: the quality bar grill-spec output should hit.
Source: "Compute exchange front end prompt" by alexziskind1 (GitHub gist)
https://gist.github.com/alexziskind1/fe55f03892f3fe1d6d8cf6065c631bb8
Reproduced verbatim for reference; all credit to the original author.
-->

Create a production-ready, visually stunning **front-end web app**.

GOAL
Build a single-page application (plus detail routes) for a fictional company:
**"SILICON EXCHANGE"** — a marketplace where people rent out idle GPUs and AI
accelerators by the hour. Renters browse listings, inspect live utilization
charts, and reserve time blocks.

FRONT END ONLY. No backend, no database, no auth server, no API keys. All data
is mock data defined in code. But the app must behave like the real thing — the
reservation logic, the pricing math, and the filter state all have to actually
work.

TECH STACK (use exactly this unless something genuinely breaks)
- Next.js (latest stable, App Router) + TypeScript (strict mode on)
- Tailwind CSS
- Framer Motion for animations
- Recharts for charts
- Zustand (or React context + reducer) for client state
- Vitest for unit tests
- Zero paid services. `npm install && npm run dev` is all it should take.

MOCK DATA (typed, deterministic, defined in /data)
- 24 listings across at least 5 regions, with realistic chips (H100, RTX 5090,
  M3 Ultra, MI300X, RTX Pro 6000, etc.), memory in GB, TFLOPS, hourly rate in
  integer cents, and a status of "available" | "maintenance" | "retired".
- 30 days of hourly utilization samples per listing (0-100% and power in watts).
  Generate these from a seeded pseudo-random function so the charts look organic
  but render identically on every reload. Do NOT use Math.random() at render time.
- A handful of pre-existing reservations, including at least one that a naive
  overlap check would wrongly allow.

THE HARD PART — these rules must be pure, tested TypeScript functions
1. **Overlap detection.** A listing cannot hold two reservations whose time ranges
   overlap. Treat ranges as half-open: a reservation ending at 14:00 and one
   starting at 14:00 do NOT overlap. Cancelled reservations don't count.
2. **Pricing.** Billed in 15-minute increments, always rounded UP. Minimum
   billable block is 1 hour. Any reservation longer than 24 continuous hours gets
   10% off every hour beyond the 24th — not off the whole booking. All money is
   integer cents. Never use floating point for money.
3. **Holds expire.** A reservation held for more than 10 minutes without being
   confirmed flips to "expired" and frees its slot. Drive this off a real timer
   in the UI with a visible countdown.
4. **Maintenance blocks new reservations** but leaves existing confirmed ones alone.
5. Reservations persist to localStorage and survive a full page reload.

PAGES / ROUTES
1) **Home** — hero, a "GPUs online" counter computed from the real mock data, three
   feature cards, CTA into browse.
2) **/browse** — grid of listing cards with working search, region filter, memory
   range filter, status filter, and sort (price, memory, TFLOPS, utilization).
   Filter state lives in the URL query string and must survive a refresh AND the
   browser back button. Show an empty state when filters match nothing.
3) **/listings/[slug]** — spec sheet, a 24-hour utilization line chart with a
   working hover tooltip, a 7-day availability calendar that visually blocks out
   taken slots, and a reservation form with a **live price quote that recalculates
   as the user drags the time range**. Show the pricing breakdown — base hours,
   rounding applied, discount applied.
4) **/dashboard** — the user's reservations from localStorage, with countdown
   timers on held ones, cancel buttons, and a running total spend.
5) **/compare** — pick up to 3 listings and diff their specs side by side.
   Selection persists across navigation.
6) **404** — custom, on-brand, not the default.

DESIGN DIRECTION
- Dark-first, with a real light mode toggle that persists and does NOT flash on
  reload.
- Technical-industrial: near-black surfaces, thin hairline borders, monospace for
  all numbers and IDs, one electric accent color used sparingly. Data-dense but
  calm. Think a trading terminal, not a SaaS landing page template.
- Micro-interactions: hover lift on cards, animated focus rings, smooth section
  reveals on scroll, an animated gradient behind the hero headline.
- Responsive and correct on a phone and on a 4K display. Tables collapse into
  cards on mobile. Charts stay readable at 375px wide.
- Accessibility: full keyboard navigation, visible focus states, semantic
  headings, labelled form controls, aria labels on icon buttons, and a text
  summary alternative for every chart.
- No stock photography and no external image requests. Every visual is inline SVG,
  CSS gradients, or generated. The app must render perfectly with the network off
  after first load.
- Two Google fonts, self-hosted via next/font. One for headings, one for body.

TESTS (must actually pass)
Write Vitest unit tests covering, at minimum:
- Overlap detection, including the half-open boundary case (14:00 end vs 14:00 start)
- The 15-minute round-up
- The 1-hour minimum
- The over-24-hour discount applied only to the excess hours
- Hold expiry at the 10-minute boundary
- The filter/sort reducer returning correct results for a combined query

DELIVERABLES — DO NOT STOP UNTIL ALL OF THESE ARE TRUE
1. `npm install` completes with no errors.
2. `npm test` runs and **every test passes**. Do not delete or skip a failing test
   to make this true — fix the code.
3. `npm run build` completes with **zero TypeScript errors** and zero ESLint errors.
4. `npm run dev` starts and the home page renders the real mock data.
5. A README.md with what it is, how to run it, and a short note explaining the
   pricing rules.

QUALITY BAR
Production-ready. No TODO comments, no stubbed functions, no `any` types, no
Lorem Ipsum, no dead buttons. Every control does something. It should look like a
high-end product a real company shipped, not a template. If you hit an error, read
it and fix it — do not work around it by deleting the feature.

Now implement it end-to-end, then verify every item in DELIVERABLES yourself.
