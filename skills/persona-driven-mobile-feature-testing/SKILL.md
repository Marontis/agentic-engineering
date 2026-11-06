---
name: persona-driven-mobile-feature-testing
description: >
  Three-phase black-box mobile application testing and automated user-centric
  feature coverage evaluation via Exploration traces, Critical User Journeys
  (CUJs), and persona-augmented Synthetic Reviews (ECS). Translates raw UI
  accessibility traces and diverse cross-screen journeys into reproducible
  functional test suites and stripped-down semantic embeddings. Derived from
  ECS (arXiv:2611.06922).
source: https://arxiv.org/abs/2611.06922
license: CC-BY-4.0
repository: https://github.com/Marontis/agentic-engineering
---

# Persona-Driven Mobile Feature Testing (ECS)

> **Source**: [Towards Comprehensive Mobile Application Testing for User-centric Feature Coverage via Simulating Real-World Users with Personas](https://arxiv.org/abs/2611.06922) (`src:2611-06922v1`, Son et al., UC Davis & CodeDroid LLC, 2026)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

Use this skill when building or operating black-box mobile GUI testing agents, synthesizing reproducible end-to-end functional test cases from exploration traces, or evaluating whether an automated test suite covers the user-centric capabilities users actually care about rather than merely visiting distinct screens (`Activity Coverage`).

## When to Use

- Designing black-box Android/mobile testing pipelines where only the application binary (`APK`) is available
- Converting raw UI accessibility-tree (`a11y`) exploration logs into reproducible, intent-annotated test cases (`Critical User Journeys`, `CUJs`)
- Capturing complex, multi-screen user workflows and negative edge cases that single-screen test generation misses
- Evaluating natural-language test suites against app descriptions and user reviews without manual human counting

## Core Insight

Structural `Activity Coverage` measures the proportion of distinct screens visited, not whether the features users rely on are actually exercised. Agents that infer a test case *before* visiting a screen (`DroidAgent`) repeatedly test prominent features on familiar screens while missing complex, cross-screen capabilities and edge cases (`40.3%` overall feature coverage on the `3,012`-feature User-Centric Feature Coverage benchmark, `14.9%` large-app activity coverage).

**ECS (Exploration, Critical User Journeys, and Synthetic Reviews)** decouples structural screen discovery from semantic feature synthesis:
1. **Static-Seeded Forced Exploration**: Seeds a navigation knowledge base from static `APK` analysis and forces the agent to visit each known activity for a bounded step budget (`15 steps`), raising large-app `Activity Coverage` to `39.1%` (`2,945` fragments vs `1,514` for `DroidAgent`) and small-app `Activity Coverage` to `70.4%` (`362` fragments vs `178`).
2. **Exhaustive Screen-Grounded CUJs**: Maps every interactable element in the observed `a11y` tree to an explicit user intent + reproducible step sequence, plus `missing_gap` expectations.
3. **Cross-Screen Persona-Augmented Synthetic Reviews**: Samples batches of `16` random cross-screen `CUJs` (`400` batches with replacement) paired with dynamically sampled user personas (drawn from a pool of `40–50` personas derived from `~250` reviews of an independent app) to synthesize multi-screen user narratives.

Across `3,012` target features from `10` commercial Google Play Store apps (`131` from app descriptions, `333` from positive reviews, `2,548` from negative reviews, filtered from `5,779` raw candidates across `5,000` crawled reviews), full `ECS` (`17,188` tests) reaches **64.1%** total feature coverage (**+23.8 percentage points** over `DroidAgent`'s `40.3%`, and **+17.2 percentage points** over `Only CUJs Full` at `46.9%`), covering **72.5%** of app-description features, **73.3%** of positive-review features, and **60.9%** of negative-review features. At a matched test budget (`K = 2,056` clusters), `ECS` reaches **58.0%** overall coverage (`70.2%` descriptions, `60.0%` positive, `57.7%` negative) vs `40.3%` for `DroidAgent` (`51.9%` descriptions, `45.0%` positive, `39.3%` negative).

---

## Procedure

### Phase 1: Static-Seeded Forced Structural Exploration

1. **Extract Static Navigation Priors from the Binary**: Before launching dynamic exploration, parse the application binary (`APK`) for manifest activity declarations, resource identifier strings, and `Intent` filter definitions that govern inter-activity transitions. Log all discovered UI element identifiers and activity transition paths into a persistent navigation knowledge base.
2. **Execute Bounded Forced Activity Visits**: Direct the testing agent to navigate to each known target activity in turn using the paths stored in the knowledge base, rather than asking the LLM to invent a feature test prior to visiting the screen.
3. **Explore Sub-Screen Fragments Within a Strict Step Cap**: Within each target activity, allocate a strict per-activity budget of **15 interaction steps** (within an overall session budget such as `12 hours` or `5,000 steps`) to trigger sub-screens (`fragments`), type into unvisited text inputs (waiting at least `1 second` after focusing and clearing existing text), and tap unvisited list items.
4. **Verify Location via Accessibility Tree and Activity Path**: After every action, parse the text-based Android accessibility tree (`a11y` tree) and query the active `Activity/Fragment` hierarchy path. If the screen reports an `EMPTY` loading state, wait `1 second` and re-query before acting; stay strictly inside the target application package (blocking transitions to system `Settings` or `Play Store`, and restoring the language to English before ending if a locale toggle was exercised). Update the knowledge base with newly observed transition paths after each session.
   - *Ablation evidence*: Removing forced exploration drops large-app activity coverage by **18.7 percentage points** (`39.1%` to `20.4%`, fragments from `2,945` to `1,086`) and small-app coverage by **6.0 percentage points** (`70.4%` to `64.4%`). Removing static analysis drops large-app activity coverage by **14.1 percentage points** (`39.1%` to `25.0%`) and small-app coverage by **14.8 percentage points** (`70.4%` to `55.6%`). Removing the knowledge base drops large-app coverage by **4.6 percentage points** (`34.5%`).

### Phase 2: Exhaustive Screen-Grounded Critical User Journey (CUJ) Extraction

1. **Ground Implemented Intent in Visible UI Elements**: For each recorded chronological exploration trace, pass the text-based UI tree and global history of already-generated goals for that screen hub to the LLM (`Gemini 3 Flash`). Instruct the model to generate a distinct `Critical User Journey (CUJ)` for nearly every actionable/touchable element (`buttons`, `tabs`, `inputs`, `list items`, `menus`), marking each as `implemented`. Every inferred feature must be anchored to concrete UI elements present in the trace to prevent hallucinated controls.
2. **Format Each CUJ as an Executable Test Case**: Record five mandatory fields per `CUJ`:
   - **Test Name (`CUJ`)**: Concise capability label (e.g., `Access Shopping Cart to complete an existing purchase`).
   - **User Goal**: The inferred user intent motivating the interaction.
   - **Test Steps**: Ordered `Action` + `Check` pairs grounded in the trace.
   - **Activity/Fragment Path**: Exact structural hierarchy traversed at each step.
   - **Expected Result**: Observable post-condition on the UI.
3. **Capture Missing Expected Features (`missing_gap`)**: In the same pass, prompt the model as a product visionary to compare the observed screen against domain expectations and industry standards, emitting `missing_gap` `CUJs` for capabilities users expect on that screen hub that are absent from the UI (e.g., missing `Prime` search filter, removed `Save for later` cart action, or missing `sort by price`).

### Phase 3: Cross-Screen Aggregation via Persona-Augmented Synthetic Reviews

1. **Synthesize an Out-of-Domain Persona Pool**: Construct `40 to 50` distinct user personas by prompting an LLM over approximately `250` real user reviews drawn from a **completely different application** (preventing benchmark leakage while preserving realistic demographic, behavioral, and stylistic diversity).
2. **Sample Uniform Cross-Screen CUJ Batches**: Draw **16 CUJs uniformly at random from across the entire application** (`16 Rand`), repeating **400 times with replacement**.
   - *Window size calibration*: `16 CUJs` is the optimal context window (`58.0%` total coverage at `K = 2,056`, `70.2%` descriptions), outperforming `1 CUJ` (`52.9%` total, `54.2%` descriptions), `8 CUJs` (`53.9%` total, `53.4%` descriptions), `32 CUJs` (`52.2%` total, `45.0%` descriptions), and `64 CUJs` (`48.4%` total, `38.2%` descriptions), where excessive disjointed `CUJs` cause incoherent reviews.
   - *Cross-screen diversity calibration*: Uniform cross-screen sampling (`16 Rand`, `58.0%` total, `70.2%` descriptions) beats single-activity sampling (`16 Act, 0 Rand`, `51.1%` total, `45.0%` descriptions) and mixed sampling (`8 Act, 8 Rand`, `47.2%` total, `54.2%` descriptions).
   - *Batch count calibration*: Scaling from `100` batches (`53.4%` total) and `200` batches (`52.4%` total) to **400 batches** peaks at `58.0%` total (`70.2%` descriptions), whereas over-generating to `800` batches drops coverage to `55.8%` (`64.6%` descriptions) because redundant reviews crowd out diverse features during clustering.
3. **Generate Persona-Conditioned Multi-CUJ Narratives**: For each batch of `16` cross-screen `CUJs`, dynamically sample a random persona from the `40–50` persona pool alongside few-shot (`FS`) review format examples from the out-of-domain app, plus the history of previously generated reviews for deduplication. Prompt the LLM to write dense, specific synthetic reviews that weave multiple disjointed `CUJs` into cohesive end-to-end user experiences and multi-step edge cases.
   - *Persona diversity guardrail*: Never lock the generator to a single fixed emotional persona or omit personas. At `K = 2,056`, `Random Persona + FS` reaches **58.0%** total (**70.2%** descriptions), beating `No Persona + No FS` (`50.1%` total, `53.4%` descriptions), `No Persona + FS` (`54.2%` total, `55.7%` descriptions), fixed `Lenient + FS` (`54.7%` total, `58.0%` descriptions), and fixed `Angry + FS` (`51.4%` total, `62.6%` descriptions).

### Phase 4: Semantic Normalization, Medoid Test Selection, and Coverage Evaluation

1. **Translate to Objective Stripped-Down Feature Descriptions**: Before clustering or judging coverage, pass every candidate (`CUJ`, synthetic review, or real review) through an LLM translator at `temperature = 0.0` (`Gemini 3 Flash`) instructed as a QA Engineer to strip all emotional framing, user opinions, and bug symptoms, leaving only a concise, objective description of the capability being exercised (`Translated Feature`, e.g., translating `"The stupid cart won't let me delete items!"` into `"Shopping cart item deletion functionality."`).
2. **Cluster and Select Medoid Test Suites**: Embed all translated candidate features into a dense vector space (`gemini-embedding-001`, `3,072` dimensions). When a bounded regression test budget `K` is required (e.g., `K = 2,056`), apply **Agglomerative Clustering** into `K` clusters and select the **medoid** of each cluster—paired with its underlying `CUJ` or batch step trace—as the representative reproducible test case.
3. **Evaluate Coverage via Top-5 Retrieval + Isolated Binary Judge**: To score coverage against a target feature list (after filtering out non-observable Play Store review noise such as `Subjective & Vague` [`491`], `Billing & Pricing` [`345`], `Content` [`268`], `Logistics & Physical` [`251`], `Policy & Account` [`190`], `Customer Support` [`167`], and `Cross-Platform` [`93`]):
   - Retrieve the **top-5** closest translated agent test candidates by cosine similarity.
   - Query an LLM-as-a-judge for a binary `Pass/Fail` coverage decision on whether any of the `5` candidates covers the target feature (`93%` agreement with human annotators across `100` random pairs, Cohen's $\kappa = 0.83$).

---

## Environment Caveats & Known Blind Spots

Even with `ECS`, `1,081` of `3,012` target features (`35.9%`) remain undiscovered due to four structural limitations of stateless mobile GUI agents that require explicit harness extensions:
1. **Cross-Session Statelessness**: Standard exploration processes each session independently without persistent episodic memory across app restarts, missing features that require closing and relaunching the app (`Media & Streaming`: `179` missed cases such as playback progress reset on re-launch; `Files & Data Sync`: `114` cases such as background camera roll sync; `Identity & Security`: `53` cases such as session persistence across restart).
2. **Monetization and Paywall Tolerance**: `E-Commerce & Ads` is the single largest missed domain (`259` missed features). Even when prompted with an irritated user persona, LLMs treat aggressive subscription upsell dialogs and paywalls as routine navigation obstacles and dismiss them rather than flagging them as functional barriers.
3. **Ordered Cross-Activity State Dependencies**: Navigating to each activity in turn and batching `CUJs` post-hoc undersamples features that only emerge from a strict ordered state mutation across multiple screens (`Productivity & AI`: `142` missed cases, such as creating a calendar event in one screen, adding a guest, saving, and verifying the shared state in a separate screen).
4. **Multi-Finger Gestures and Render Feedback**: Action spaces restricted to discrete taps, long-clicks, text entry, and simple swipes over the text `a11y` tree miss continuous or multi-finger gestures (`General`: `263` missed cases, such as pinch-to-zoom image scaling or layout resizing on keyboard dismissal; `Social & Comm.`: `71` cases) where the `a11y` tree provides no visual confirmation that the gesture registered.

---

## Related Rules & Specs

- [`agent-evaluation-quality.md`](../../rules/agent-evaluation-quality.md) — Grounding evaluation in objective, stripped-down feature representations and human-validated binary checks
- [`mobile-and-generative-ui.spec.md`](../../specs/mobile-and-generative-ui.spec.md) — Mobile application architecture and UI verification standards
