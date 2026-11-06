# Mobile UI, Generative UI & Agentic Data Display Specification Template

> Fill in this template when using AI coding agents to design, generate, or test mobile interfaces (iOS / Android / React Native / Flutter), responsive web UIs (React / Next.js), or interactive data visualizations and dashboards that display structured agent outputs.
>
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## 1. Target Surface & Interaction Modality

### What UI surface is the agent building or driving?

- [ ] **Mobile Native / Cross-Platform UI** (React Native / Expo, Flutter, SwiftUI, Jetpack Compose)
- [ ] **Responsive Web / Mobile-First Next.js App** (React Server Components + Client Interactive Widgets)
- [ ] **Dynamic Generative UI / Data Dashboard** (Agent-synthesized charts, editable diagrams, comparison tables, and live control panels bound to MCP/tool outputs)
- [ ] **Application Overlay / Interface Quilt (`arXiv:2611.01891`)** (Modifying or composing custom UI views atop existing applications via computer-use and generative UI agents)

---

## 2. Two-Phase UI Code Generation Architecture

> **Research basis**: Directly prompting an MLLM or coding agent to emit framework-specific UI code (`React`, `Vue`, `React Native`) from a visual prototype or feature prompt in a single pass causes cross-framework syntax contamination, broken spatial hierarchy (`UI-UG 2`, `arXiv:2611.00926`), and disconnected state bindings (`arXiv:2611.01692`; `arXiv:2610.17861`).

### How is UI generation decomposed?

- [ ] **Phase 1 — Framework-Agnostic Spatial & Component Hierarchy (`UI-UG 2`, `arXiv:2611.00926`; `arXiv:2611.01692`)** *(Recommended Default)*:
  - First synthesize and verify the structural layout tree: component bounding boxes, flex/grid containers, responsive breakpoints, and semantic grouping.
  - Validate visual-spatial constraints (no overlapping sibling bounds, mobile touch target `>= 44x44 pt`, viewport overflow checks) before binding framework state.
- [ ] **Phase 2 — State-Transition Graph & Framework Hydration (`arXiv:2610.17861`; `arXiv:2611.01692`)**:
  - Extract an explicit **State-Transition Graph (`STG`)** mapping every user interaction event (`onPress`, `onSubmit`, filter change, tab switch) to state mutations, route transitions, and backend API/MCP calls.
  - Hydrate the verified layout skeleton into the target framework (`Next.js / React`, `React Native`, `Flutter`) using strictly typed props and hooks.

---

## 3. Spatial Accessibility & Mobile Screen Hierarchy

> **Research basis**: Mobile screen readers and mobile UI agents fail when interfaces are emitted as flat sequences of absolute-positioned or ungrouped elements (`arXiv:2611.02410`). Spatial organization on mobile screens *is* the accessibility and navigation structure.

### What mobile layout and accessibility invariants are enforced?

- [ ] **Hierarchical Spatial Grouping (`arXiv:2611.02410`)** *(Recommended Default)*:
  - Group spatially co-located elements (cards, list rows, metric tiles, bottom sheets, form sections) into explicit semantic containers (`role="region"`, `accessibilityRole`, `aria-labelledby`) so screen readers and mobile agents traverse a 2-level hierarchy (Container $\rightarrow$ Items) rather than a flat 100-node list.
- [ ] **Mobile Viewport & Ergonomic Constraints**:
  - Primary actions anchored in the thumb-reachable bottom zone; sticky headers/footers capped at `< 20%` of viewport height; all interactive controls carry explicit accessible labels and loading/error states.

---

## 4. Displaying Agent-Built Data: Generative UI, Charts & Editable Diagrams

> **Research basis**: When agents display complex analytical outputs, pixel/raster generation prevents user editing, while unconstrained LLM text re-transcription introduces memory and calculation hallucinations (`MCPHallu`, `arXiv:2611.07689`). High-fidelity agentic data display requires structured intermediate representations (`EvoDesign`, `arXiv:2604.09568`; `RSIV-Harness`, `arXiv:2610.35316`).

### How are agent data outputs bound to visual components?

- [ ] **Zero-Transcription Data Binding (`MCPHallu`, `arXiv:2611.07689`)** *(Recommended Default)*:
  - The LLM selects the **view specification** (chart type, axis mappings, filter controls, layout template) and references a **verified data artifact ID** returned by the tool/MCP server.
  - The UI runtime binds the raw structured dataset directly from the tool receipt into the chart/table component—never having the LLM copy hundreds of data points through output tokens.
- [ ] **Three-Layer Editable Diagram & Chart Synthesis (`EvoDesign`, `arXiv:2604.09568`)**:
  - Decouple visual outputs into: (1) **Semantic Topology** (nodes, edges, data series), (2) **Visual Styling** (theme tokens, colorblind-safe palette, typography), and (3) **Geometric Layout** (collision-free coordinates), rendered as inspectable/editable vector or declarative specs (`Vega-Lite`, `Mermaid`, `React Flow`, `SVG/Canvas` scene graph).
- [ ] **4-Stage RSIV Visualization Verification (`RSIV-Harness`, `arXiv:2610.35316`)**:
  - Enforce Retrieve $\rightarrow$ Specify $\rightarrow$ Implement $\rightarrow$ Verify with an explicit data-anchor check (every plotted series matches source column cardinalities and units) before rendering to the user.

---

## 5. End-to-End UI Dataflow & Persona-Driven Feature Verification

> **Research basis**: "Vibe-coded" web and mobile apps frequently exhibit **silent behavioral failures** where the UI renders and animates properly, but user inputs never propagate to application state or backend storage (`FlowCheck`, `arXiv:2608.28880`). Furthermore, testing mobile UIs solely for screen/Activity coverage misses broken user-centric workflows (`arXiv:2611.06922`).

### How is the generated UI verified before shipping?

- [ ] **Intent-to-State Dataflow Verification (`FlowCheck`, `arXiv:2608.28880`)** *(Recommended Default)*:
  - For every interactive widget (`input`, `select`, `button`, `form`, `drag-handle`), trace and assert the complete causal chain: `UI Event -> Handler Function -> State Store / API Payload -> Rendered Confirmation`. Flag any dead handler, unsubmitted form field, or mocked stub (`arXiv:2610.14629`) as a blocking defect.
- [ ] **Persona-Driven End-to-End Feature Coverage (`arXiv:2611.06922`; `PersonaCodeBench`, `arXiv:2611.05739`)**:
  - Test mobile and web flows using realistic multi-step user personas (including edge-case inputs, interrupted navigation, back-button recovery, and dark/offline states) rather than shallow single-screen render checks.
- [ ] **Long-Horizon Incremental Regression Gate (`ViBench 2.0`, `arXiv:2611.05620`; `Multi-step SWE`, `arXiv:2611.07166`)**:
  - Re-run prior feature dataflow and visual-layout assertions after every subsequent feature addition so iterative agent edits do not silently break earlier screens.

