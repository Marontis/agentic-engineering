---
name: state-aware-prototype-to-webapp
description: >
  Prevent prototype-to-project state drift when generating multi-page interactive
  and full-stack web applications from visual prototypes and textual requirements.
  Constructs an explicit Project State Graph (PSG) prior to code generation,
  extracts task-scoped subgraphs per file, and enforces write-protected 2-hop
  impact sets during render-evidence repair. Derived from VisStateCoder
  (arXiv:2610.17861).
source: https://arxiv.org/abs/2610.17861
license: CC-BY-4.0
repository: https://github.com/Marontis/agentic-engineering
---

# State-Aware Prototype to WebApp

> **Source**: [State-Aware Generation of Deployable Websites from Visual Prototypes and Requirements](https://arxiv.org/abs/2610.17861) (Pan et al., 2026)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

- Generating deployable multi-page interactive frontends or full-stack web applications from a bundle of visual design prototypes (screenshots/mockups) and natural-language requirements.
- Preventing **Correspondence Breaks** (where UI buttons and forms render visually on screen, but their event handlers, route targets, or backend API endpoints fail to wire up) and **Verified-State Drift** (where iterative visual/functional repair patches break features that already passed in earlier rounds).
- Structuring state management for multi-file coding agents where unstructured text summaries or passive JSON state dumps fail to prevent cross-file regressions.

---

## Core Concepts

### Prototype-to-Project State Drift

When generating a multi-page or full-stack website from visual prototypes and requirements, the specification is split across modalities: **visual prototypes** define page layouts, regions, and copy, while **textual requirements** define cross-page navigation, state transitions, and backend API persistence. Across long multi-file generation and repair horizons, coding agents suffer from **prototype-to-project state drift**, quantified by two failure metrics:

1. **Correspondence Break Rate (CBR)**: The fraction of interactive workflows whose visual trigger element renders and is reachable on the page, but whose downstream interaction handler, route transition, or backend API contract fails.
2. **Verified-State Drift Rate (VSDR)**: The fraction of verification checks that pass in repair round $t$ but regress to failing in round $t+1$ because an unscoped repair patch overwrites working code in coupled files.

Crucially, **passive text or JSON state summaries do not solve state drift**. In Vision2Web ablations, replacing no-state prompting (`w/o PSG`) with a natural-language `Text-State Memory (TSM)` actually *increases* Correspondence Break Rate from **50.0% to 55.0%** on Interactive Frontend tasks and from **78.8% to 80.8%** on Full-Stack tasks. Even storing the exact same nodes and edges in a passive `JSON-State` injected into prompts underperforms an enforced **Project State Graph (PSG)** by **9.3 points** on Full-Stack tasks (**34.5 vs. 43.8**) and suffers nearly $3\times$ higher Verified-State Drift (**2.4% / 3.5% vs. 0.9% / 1.3%**), because the model still receives unscoped context and can freely edit arbitrary files during repair.

### The Project State Graph ($\mathcal{G} = (\mathcal{N}, \mathcal{E}, \mathcal{A})$)

Represent the entire application before writing any code as a typed, directed **Project State Graph** with four node classes and seven typed edges:

- **Four Node Classes ($\mathcal{N}$)**:
  1. `Prototype state`: Page skeletons, UI regions (with role, reading order, normalized bounding box, and `data-region-id` anchor), text slots, and visual asset slots.
  2. `Project-file state`: Planned HTML/template pages, shared stylesheets, client scripts, and backend server/API modules.
  3. `Interaction state`: User workflows specifying source page, trigger text/element, event type, target route or UI state, required inputs, expected post-interaction texts, and backend data models/routes.
  4. `Render-evidence state`: Runtime verification records attached to specific pages, regions, and interactions after headless browser rendering.
- **Seven Typed Edges ($\mathcal{E}$)**:
  - `contains`: Links pages to regions and slots.
  - `grounds_to` and `triggers`: Bind textual interaction workflows to specific visual prototype elements and target states.
  - `implements`: Maps prototype pages, regions, and interactions to concrete project files.
  - `depends_on`: Captures cross-file dependencies (such as a page depending on a shared script, stylesheet, or API endpoint).
  - `verified_by` and `mismatch_at`: Link render-evidence pass/fail records back to the exact prototype regions, interactions, and files they test.

---

## Step-by-Step Procedure

### Step 1: Ground Prototypes and Requirements into the PSG Before Coding

Execute schema-validated multimodal extraction to populate and lock the structural graph before generating any code file:

1. **Extract visual page skeletons**: For each prototype image, extract its target route, file name, ordered UI regions (assigning each a deterministic `data-region-id` attribute, functional role, normalized bounding box, and summary), exact text slots, style hints, and asset-to-file bindings.
2. **Extract interaction and backend contracts**: From the textual requirements, extract every interactive workflow (source page, trigger label, event type, target route/state, required form inputs, and expected post-interaction feedback) and required backend data models or REST endpoints.
3. **Ground triggers to visual elements**: Match each interaction workflow to its corresponding visual prototype region and element via `grounds_to` and `triggers` edges. (In RQ4 across 50 tasks and 4,120 gold edges, automated grounding achieves **95.6% edge F1**; workflows with a correct `grounds_to`/`triggers` edge pass **56.2%** of functional test cases versus **4.7%** when the edge is missing or wrong.)
4. **Lock the implementation dependency plan**: Establish `implements` and `depends_on` edges mapping every page, region, and interaction to planned project files.

### Step 2: Generate Files via Task-Scoped Subgraph Extraction ($\mathcal{S}_\tau$)

Never feed the entire project state or all prototypes into every file-generation prompt. For each planned file task $\tau \in \mathcal{T}$, programmatically slice a **task-scoped subgraph $\mathcal{S}_\tau$**:

1. **Page files first**: When generating a page file, include *only* that page's prototype image, its region skeleton (`data-region-id` anchors), its bound text/asset slots, and the interaction workflows originating on or targeting that page. Explicitly forbid inventing sections, routes, assets, or placeholder links absent from $\mathcal{S}_\tau$.
2. **Shared theme, client scripts, and backend server second**: Generate shared CSS, client-side JavaScript handlers, and backend API servers *after* the page files, conditioning their subgraphs on the exact `data-region-id` anchors, DOM selectors, and route contracts emitted in the page files.

### Step 3: Collect Tri-Modal Render Evidence Without Test Cases

Launch the generated application in a headless **Playwright** browser and collect three tiers of automated render evidence ($K \le 4$ rounds) without relying on benchmark test suites:

1. **Deterministic structural checks**: Verify that all planned files exist, the startup script executes cleanly, stylesheets and scripts are linked, every required `data-region-id` anchor, text slot, and asset renders in the DOM, and no placeholder strings or unplanned dead routes appear.
2. **Pixel-level prototype alignment**: Compare the rendered Playwright viewport against the ground-truth prototype screenshot and record a `mismatch_at` edge if the **root-mean-square (RMS) pixel difference exceeds $0.28$**.
3. **Component-level VLM visual judge**: Score each rendered UI region against its prototype crop on a 5-level rubric and record a `mismatch_at` edge for any component scoring **$< 0.75$**.

### Step 4: Enforce Write-Protected 2-Hop Scoped Updates ($\Omega$)

When repairs are required, prevent Verified-State Drift by restricting which files and code layers the agent is allowed to touch:

1. **Identify seed failure nodes ($\Omega_0$)**: Follow `mismatch_at` edges from failed render-evidence nodes to their directly implicated prototype regions, interactions, or files.
2. **Compute the 2-hop reachability impact set ($\Omega$)**: Traverse at most 2 hops along structural and dependency edges:
   $$\Omega = \mathcal{N}_{\mathcal{G}}^{\le 2}\!\left(\Omega_0,\, \{\texttt{implements},\, \texttt{triggers},\, \texttt{depends\_on}\}\right)$$
   (If a runtime error provides no resolvable node identifier, fall back to a capped candidate set of at most 5 files.)
3. **Enforce hard file-level write protection**: **Reject any model-generated patch that modifies a file outside $\Omega$.**
4. **Apply staged, minimal-privilege repairs**:
   - *Stage A (Deterministic link/file repair)*: Fix broken asset paths, missing `<script>`/`<link>` tags, or missing route registrations deterministically.
   - *Stage B (Targeted model patch)*: Invoke the LLM on files inside $\Omega$ to restore missing `data-region-id` blocks, text slots, or interaction handlers.
   - *Stage C (CSS-only append patch)*: For pure visual alignment/style mismatches (RMS $> 0.28$ or VLM judge $< 0.75$ when structural checks already pass), restrict repairs to **CSS-only append patches** so working DOM structure and JavaScript event handlers cannot be corrupted.

---

## Quantitative Justification

Evaluated on **Vision2Web** (**193 tasks**: 100 Static Webpage, 66 Interactive Frontend [avg 5.9 prototypes, 7.5 test cases], and 27 Full-Stack Website tasks [avg 8.5 prototypes, 28.2 test cases]; **918 visual prototypes** and **1,255 functional test cases** total) across **5 foundation models** (`Doubao-Seed-1.8`, `Gemini-3-Flash-Preview`, `Gemini-3.1-Pro-Preview`, `GPT-5.1`, `Qwen3.5-Plus`) and on **WebGen-Bench** (101 prototype-free tasks, 647 test cases):

- **End-to-End Multi-Model Gains**: Averaged across all 5 foundation models, `VisStateCoder` improves overall `Avg` score over the strongest baseline under each model from **34.6 to 60.8 (+26.1 points)** on Interactive Frontend tasks and from **21.2 to 43.8 (+22.6 points)** on Full-Stack Website tasks. With `GPT-5.1`, `VisStateCoder` reaches **61.7** (Static), **69.3** (Interactive: **57.6** Visual / **80.9** Functional), and **50.4** (Full-Stack: **50.1** Visual / **50.8** Functional) with **100% Deployable Success Rate (DSR)**.
- **State Drift Reduction**: Pooled across Interactive Frontend and Full-Stack tasks, `VisStateCoder` lowers **Correspondence Break Rate (CBR) from 44.2% to 33.3%** (achieving **22.2% CBR** at 85.9% Trigger Reachability on Interactive Frontend and **44.4% CBR** at 75.8% Trigger Reachability on Full-Stack) and lowers **Verified-State Drift Rate (VSDR) from 3.0% to 1.1%** (**0.9% VSDR** across $n_{\text{pass}}=643$ checks on Interactive Frontend; **1.3% VSDR** across $n_{\text{pass}}=738$ checks on Full-Stack) compared to the strongest state baseline (`JSON-State`).
- **Component Ablations (RQ3)**:
  - Removing Stage 1 Prototype Grounding collapses Interactive Frontend Avg from **60.8 to 25.8** and Full-Stack Avg from **43.8 to 19.4**.
  - Removing the Stage 3 Scoped Update Loop drops Interactive Frontend Avg from **60.8 to 55.4** and Full-Stack Avg from **43.8 to 38.2**.
- **Negligible Overhead**: Graph construction, subgraph slicing, and 2-hop impact resolution add only **673.4 ms** (Interactive) and **1,187.6 ms** (Full-Stack) per task, keeping total token/runtime cost at **$1.03\times$** `w/o PSG` (\$13.46 vs. \$13.13 Interactive; \$20.93 vs. \$20.34 Full-Stack). On prototype-free **WebGen-Bench**, `VisStateCoder` reaches **49.0%** accuracy vs. **40.1%** for `Claude Code`.

---

## Anti-Patterns to Avoid

- **Using unstructured text memory (`TSM`) or passive JSON dumps to track multi-file web app state**: Dumping state summaries into prompts without programmatic subgraph slicing and write-protected repair scoping increases Correspondence Breaks (**55.0% vs. 50.0%**) and allows repair patches to overwrite verified files.
- **Generating shared scripts and backend endpoints before page skeletons**: Writing event listeners or API bindings before `data-region-id` anchors and form selectors are fixed causes selector mismatches and dead triggers.
- **Allowing full-file HTML/JS regeneration during visual styling repair**: When structural checks pass and only visual alignment fails (RMS $> 0.28$ or VLM score $< 0.75$), allowing the LLM to rewrite HTML or JS risks breaking working event handlers; enforce CSS-only append patches.

---

## Related Artifacts

- **Spec**: [Next.js Public Agent App Spec](../../specs/nextjs-public-agent-app.spec.md)
- **Spec**: [Mobile and Generative UI Spec](../../specs/mobile-and-generative-ui.spec.md)
- **Skill**: [UI Dataflow Intent Verification](../ui-dataflow-intent-verification/SKILL.md)
- **Skill**: [Two-Phase Framework UI Codegen](../two-phase-framework-ui-codegen/SKILL.md)
- **Rules**: [Agent Sandbox Safety](../../rules/agent-sandbox-safety.md), [Multi-Agent Coordination](../../rules/multi-agent-coordination.md), [Agent Evaluation Quality](../../rules/agent-evaluation-quality.md)
