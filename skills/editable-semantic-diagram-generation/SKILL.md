---
name: editable-semantic-diagram-generation
description: >
  Generate object-level editable, visually balanced diagrams on an interactive
  canvas (tldraw) via a decoupled Semantic-Style-Layout schema, Spec-to-Instance
  multi-agent pipeline, bottom-up geometric text sizing with top-down recursive
  layout, closed-loop VLM surgical refinement, and three-tier design knowledge
  memory. Derived from EvoDiagram / EvoDesign (arXiv:2604.09568).
source: https://arxiv.org/abs/2604.09568
license: CC-BY-4.0
repository: https://github.com/Marontis/agentic-engineering
---

# Editable Semantic Diagram Generation

> **Source**: [EvoDiagram: Agentic Editable Diagram Creation via Design Expertise Evolution](https://arxiv.org/abs/2604.09568) (Wang et al., 2026; also indexed as *EvoDesign: Agentic Editable Diagram Creation via Design Expertise Evolution*)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

- Generating scientific figures, system architecture diagrams, flowcharts, mind maps, or domain illustrations that must be **both visually balanced and object-level editable** in a vector canvas editor (such as `tldraw`, Excalidraw, or Figma).
- Overcoming the **diagram representation gap**: pixel-based image generators (`GPT-4o-Image`, `Flux.2 flex`) produce aesthetic bitmaps ($V_{\text{VA}} = 3.990$) that hallucinate text ($C_{\text{CF}} = 2.200$) and cannot be edited at the node level, while symbolic code synthesis (`LaTeX TikZ`, `Mermaid`) preserves content logic ($C_{\text{CF}} = 4.201$) but suffers from rigid or overlapping spatial layouts ($V_{\text{SB}} = 2.543\text{--}3.124$) and high manual editing barriers.
- Eliminating node collisions, text overflow, and "spiderweb" edge crossings when prompting LLMs to emit canvas JSON schemas directly.

---

## Core Concepts

### Decoupled Intermediate Canvas Schema ($D = (G, S, L)$)

One-shot prompting of an LLM to output raw canvas JSON simultaneously entangles semantic entity extraction, visual styling, and 2D coordinate geometry, causing severe spatial collisions (one-shot `GPT-5.2` achieves only **1.782 / 5.0** on Space Balance $V_{\text{SB}}$ and **2.184** on Flow Coherence $V_{\text{FC}}$). Instead, decouple the target diagram on an editable canvas (`tldraw`) into three orthogonal representations:

1. **Semantic Graph ($G = (\mathcal{V}, \mathcal{E})$)**: Canonical entities $\mathcal{V}$ (nodes and nested container groups) and directed/undirected functional relations $\mathcal{E}$ with explicit source/target bindings and labels.
2. **Discrete Style Schema ($S$)**: Constrained strictly to supported discrete canvas enums so the LLM cannot hallucinate invalid CSS/SVG properties:
   - `TLColor` (13 discrete palette colors), `TLGeo` (13 geometric primitives), `TLSize` (`s`, `m`, `l`, `xl`), `TLFill` (`none`, `semi`, `solid`, `pattern`), `TLDash` (`draw`, `solid`, `dashed`, `dotted`), and `TLFont` (`draw`, `sans`, `serif`, `mono`).
3. **Layout Configuration ($L$)**: Positive integer bounding coordinates $(x, y)$, width and height $(w, h)$, integer `rotation`, text `align`, and sequential z-order rank `index`.

### Spec-to-Instance Decomposition

Before any agent instantiates concrete nodes, styles, or coordinates, it must first emit an explicit, natural-language **Strategy Specification** ($\tilde{G}, \tilde{S}, \tilde{L}$). This separates high-level topological and aesthetic planning from low-level schema formatting.

---

## Step-by-Step Procedure

### Step 1: Ground Semantic Structure via Entity-First, Relation-Last Planning ($A_{\text{str}}$)

1. **Emit the Structural Strategy Specification ($\tilde{G}$)**: Select the optimal diagram archetype (from 21 canonical types such as hierarchical architecture, cyclic process, timeline, matrix, or comparative layout), define the primary directional flow strategy, and specify modular grouping boundaries.
2. **Execute Entity-First, Relation-Last Instantiation**:
   - First, extract and deduplicate all canonical entities $\mathcal{V}$ and assign them to nested functional container groups.
   - Only after all node identities and hierarchy levels are fixed, instantiate directed edges $\mathcal{E}$ between canonical node IDs. This prevents duplicate node aliases (identity fragmentation) and reduces ungrouped cross-module "spiderweb" edge tangles.

### Step 2: Map Visual Hierarchy to Discrete Style Enums ($A_{\text{sty}}$)

1. **Emit the Design Strategy Specification ($\tilde{S}$)**: Define the visual tone, semantic color encoding (mapping functional roles or hierarchy depths to distinct hues), shape semantics, and connector dash conventions.
2. **Instantiate Discrete Style Bindings ($S$)**: Map every node, container group, and edge onto the six closed `tldraw` style enums (`TLColor`, `TLGeo`, `TLSize`, `TLFill`, `TLDash`, `TLFont`), ensuring zero out-of-schema style attributes.

### Step 3: Compute Hybrid Bottom-Up Sizing and Top-Down Recursive Coordinates ($A_{\text{lay}}$)

LLMs are notoriously poor at mentally calculating pixel widths of wrapped text strings and nested containers. Replace raw coordinate guessing with a three-stage geometric pipeline:

1. **Emit the Strategic Layout Specification ($\tilde{L}$)**: Specify global flow direction (left-to-right, top-to-bottom, radial), inter-module whitespace ("spatial breathing"), alignment axes, depth layering, and structural rhythm.
2. **Bottom-Up Node Sizing via a Deterministic Geometric Size Estimator**: Before assigning any $(x, y)$ positions, pass every leaf node's text label, chosen `TLFont`, `TLSize`, and icon/padding parameters to a deterministic **Geometric Size Estimator** tool that simulates font-aware line wrapping and ceiling rounding to compute minimum collision-free leaf dimensions $(w_i, h_i)$. Propagate leaf sizes upward to determine minimum bounding footprints for parent container groups.
3. **Top-Down Recursive Coordinate Instantiation**: Partition the global canvas into macro-regions for top-level container modules first, then recursively resolve local $(x, y)$ coordinates and alignment grids for inner child nodes within each container's allocated bounding box.

### Step 4: Run Closed-Loop VLM Rendering and Surgical Tool Refinement ($A_{\text{refine}}$)

1. **Render and Diagnose**: Compile the candidate schema $\hat{\mathcal{D}} = (G, S, L)$ onto the headless `tldraw` canvas, export a raster snapshot, and prompt a VLM Refiner Agent to perform **Visual Diagnosis**—cross-referencing the rendered image against the original user prompt $\mathcal{I}$ to spot remaining text overflows, overlapping arrows, misaligned columns, or low-contrast labels.
2. **Execute Surgical Tool Corrections (Not Full Regeneration)**: Instead of regenerating the entire canvas JSON from scratch (which introduces new layout regressions), invoke targeted correction tools across five orthogonal domains:
   - *Entity Governance*: Add missing nodes/labels or merge duplicate entities.
   - *Spatial Alignment*: Shift coordinates, snap rows/columns to shared axes, or expand container padding.
   - *Aesthetic Calibration*: Adjust `TLColor`, `TLFill`, or `TLSize` for contrast and hierarchy clarity.
   - *Relational Optimization*: Reroute colliding connectors or flip edge anchor sides.
   - *Constraint Resolution*: Resolve residual bounding-box overlaps.

### Step 5: Evolve and Retrieve Three-Tier Design Knowledge Memory ($\mathcal{M} = \{\mathcal{K}^s, \mathcal{K}^g, \mathcal{K}^p\}$)

To continuously improve diagram design without weight updates, maintain a structured three-tier memory indexed in a vector store (e.g., `Qwen3-Embedding-8B` + ChromaDB, retrieving top-$k = 5$ entries per agent stage):

1. **Explore via Hybrid Experience Search**:
   - *Refinitive Depth-First Search (DFS)*: Collect multi-turn surgical refinement trajectories on a task $\mathcal{I}$ to capture what went wrong in initial drafts and which tool operations fixed it.
   - *Comparative Breadth-First Search (BFS)*: Generate diagrams under diverse user style/layout requirements $r'$ on the same semantic content $c$ to contrast effective vs. ineffective structural archetypes.
2. **Distill into Three Hierarchical Memory Tiers**:
   - **Sample Strategies ($\mathcal{K}^s$)**: Instance-level lessons learned from specific DFS/BFS trajectories.
   - **Domain Guidelines ($\mathcal{K}^g$)**: Mid-level rules distilled from $\mathcal{K}^s$, indexed by **agent role** ($A_{\text{str}}, A_{\text{sty}}, A_{\text{lay}}, A_{\text{refine}}$), **21 diagram archetypes**, and **30 academic/professional domains**.
   - **General Principles ($\mathcal{K}^p$)**: High-level, domain-agnostic visual design axioms (such as *Functional Modularity*, *Visual Hierarchy Contrast*, and *Orthogonal Flow Consistency*) injected across all tasks.

---

## Quantitative Justification

Evaluated on **CanvasBench** (**2,260 validated samples** across **21 diagram types** and **30 MMMU vertical domains**; **210-sample test set** scored on a 5-point Likert scale across 10 metrics spanning Content [$C_{\text{CF}}$ Fidelity, $C_{\text{CL}}$ Completeness, $C_{\text{SR}}$ Structural Rationality], Visual [$V_{\text{VA}}$ Aesthetics, $V_{\text{SC}}$ Style Consistency, $V_{\text{FC}}$ Flow Coherence, $V_{\text{SB}}$ Space Balance], and Cognitive [$G_{\text{CE}}$ Exploration, $G_{\text{CA}}$ Comprehension Accuracy, $G_{\text{SE}}$ Structural Efficiency]):

- **Consistent Gains Across All 3 Foundation Backbones (vs. One-Shot Schema Prompting)**:
  - **`EvoDiagram (GPT-5.2)`**: Improves Visual Space Balance ($V_{\text{SB}}$) by **+51.8%** (from **1.782 to 2.705**), Visual Aesthetics ($V_{\text{VA}}$) from **2.312 to 2.929**, Flow Coherence ($V_{\text{FC}}$) from **2.184 to 2.405**, Structural Rationality ($C_{\text{SR}}$) from **4.025 to 4.158**, and Cognitive Comprehension Accuracy ($G_{\text{CA}}$) from **3.146 to 3.419**.
  - **`EvoDiagram (Gemini-3-Pro)`**: Improves Space Balance ($V_{\text{SB}}$) from **2.312 to 3.010**, Flow Coherence ($V_{\text{FC}}$) from **2.986 to 3.294**, Visual Aesthetics ($V_{\text{VA}}$) from **2.842 to 3.177**, Content Fidelity ($C_{\text{CF}}$) from **3.765 to 3.853**, and Cognitive Exploration ($G_{\text{CE}}$) from **3.214 to 3.520**.
  - **`EvoDiagram (Qwen3-VL-Plus)`**: Improves Space Balance ($V_{\text{SB}}$) from **1.705 to 2.695**, Flow Coherence ($V_{\text{FC}}$) from **2.214 to 2.873**, Content Fidelity ($C_{\text{CF}}$) from **3.284 to 3.654**, and Comprehension Accuracy ($G_{\text{CA}}$) from **2.224 to 3.018**.
- **Multi-Agent & Memory Ablations**:
  - Removing the specialized Spec-to-Instance multi-agent decomposition (`w/o Multiagent`) causes Space Balance ($V_{\text{SB}}$) to collapse from **2.705 to 1.891** on `GPT-5.2`, from **3.010 to 2.435** on `Gemini-3-Pro`, and from **2.695 to 1.884** on `Qwen3-VL-Plus`.
  - Removing the evolved Three-Tier Design Knowledge Memory (`w/o Memory`) degrades all 10 Content, Visual, and Cognitive metrics across every tested model backbone.

---

## Anti-Patterns to Avoid

- **One-shot prompting for combined semantics, styles, and $(x, y)$ coordinates**: Asking a single LLM call to emit complete canvas JSON without intermediate strategy specs and geometric size estimation produces severe node overlaps ($V_{\text{SB}} = 1.705\text{--}1.782$).
- **Letting the LLM guess text bounding-box pixel dimensions**: Always compute leaf node widths and heights bottom-up with a deterministic font-aware Geometric Size Estimator before assigning top-down coordinates.
- **Full-canvas regeneration during VLM refinement**: Regenerating the entire diagram JSON to fix a localized label collision destroys valid layouts elsewhere on the canvas; restrict the Refiner Agent to surgical domain tools.

---

## Related Artifacts

- **Spec**: [Mobile and Generative UI Spec](../../specs/mobile-and-generative-ui.spec.md)
- **Skill**: [Mobile Spatial Accessibility Grouping](../mobile-spatial-accessibility-grouping/SKILL.md)
- **Skill**: [State-Aware Prototype to WebApp](../state-aware-prototype-to-webapp/SKILL.md)
- **Rules**: [Multi-Agent Coordination](../../rules/multi-agent-coordination.md), [Skill System Design](../../rules/skill-system-design.md)
