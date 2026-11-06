---
name: mobile-spatial-accessibility-grouping
description: >
  Reconstruct two-level functional hierarchies and multi-granularity semantic
  descriptions for mobile UI screens using spatial containment, alignment rules,
  shallow-hierarchy simplification, and single-request LLM refinement. Eliminates
  focus-order fragmentation and uninformative screen-reader stops. Derived from
  SeeR (arXiv:2611.02410).
source: https://arxiv.org/abs/2611.02410
license: CC-BY-4.0
repository: https://github.com/Marontis/agentic-engineering
---

# Mobile Spatial Accessibility Grouping

> **Source**: [Spatial Organization Is Accessibility Structure: Hierarchical Screen Reading of Mobile UIs](https://arxiv.org/abs/2611.02410) (Hu et al., 2026)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

- Building accessibility layers, screen-reader tree transformers, or mobile GUI agent perception preprocessors that consume raw Android/iOS accessibility trees (`AccessibilityNodeInfo` / XML view hierarchies).
- Repairing fragmented, linear screen-reader focus sequences (such as Android TalkBack) on dense commercial apps (shopping, travel, finance, social, entertainment) where visual cards, toolbars, and list items are flattened or interleaved.
- Compressing noisy mobile DOM/accessibility trees into concise, action-preserving hierarchical state representations before passing them to an LLM or human user.

---

## Core Concepts

### Why Raw Mobile View Hierarchies Fail Sequential Navigation

An empirical audit of **50 pages across 10 real-world Android apps** (spanning shopping, travel, social, finance, and entertainment; 1,858 TalkBack focus stops and 1,324 human-annotated semantic actions, Cohen's $\kappa = 0.81$) reveals that **96.0% of pages** organize content into composite **functional units** (product cards, user post blocks, navigation bars), with an average of **76.8% of elements per page** belonging to such units (human pairwise co-membership $F1 = 0.92$). However, linear screen-reader traversal over raw developer view hierarchies exhibits four structural failure modes:

1. **Flat sequential traversal inflation**: Reaching a target interaction element requires an average of **18.7 $\pm$ 16.5 forward swipes** because users cannot preview or skip whole functional units before stepping through every price tag, badge, and rating icon inside them.
2. **Functional-unit interruptions**: On **17 of 50 pages (34.0%)**, sequential focus jumps out of a functional unit into an unrelated element (such as a floating button or adjacent column item) and back again ($0.7 \pm 1.4$ interruptions per page).
3. **Non-informative focus stops**: **535 of 1,858 focus stops (28.8%)** are uninformative due to empty or generic labels (`button`, `image`), raw resource identifiers, isolated text fragments (`$`, `sold`), or redundant wrapper announcements.
4. **Unreachable semantic actions**: **161 annotated semantic actions (12.2%)** are completely missed by linear screen reading because custom views or gesture handlers are not exposed as focusable accessibility nodes.

### Spatial Organization as Ground-Truth Structure

Developers optimize visual layout (bounding boxes, containment, and row/column alignment) for sighted users even when underlying XML container nesting is arbitrary or deeply wrapped. By combining **spatial containment and alignment rules** with **shallow-hierarchy simplification** and a **single-request multi-granularity LLM pass**, raw accessibility trees can be transformed in milliseconds into a clean three-level hierarchy: **Page Root $\rightarrow$ Functional Units $\rightarrow$ Atomic Elements**.

---

## Step-by-Step Procedure

### Step 1: Filter and Deduplicate Atomic Elements

1. **Capture a static XML snapshot** of the active window's accessibility tree after the layout stabilizes.
2. **Prune invisible and non-semantic nodes**:
   - Discard any node whose on-screen bounding box $[x_1, y_1, x_2, y_2]$ has zero width or zero height, or lies completely outside the visible viewport.
   - Retain all interactive nodes (`clickable`, `longClickable`, `checkable`, `editable`), *excluding* scrollable layout containers (`scrollable = true`) so container wrappers do not swallow child interactions.
   - Retain non-interactive leaf nodes only if they carry non-empty `text` or `contentDescription`.
3. **Deduplicate overlapping interactive targets**: When multiple retained nodes share identical bounding boxes and represent the same interactive target, collapse them into a single atomic element, preferring the node that already carries a readable text or content description.

### Step 2: Construct the Function-Aware Spatial Hierarchy

Build candidate functional units bottom-up and top-down using deterministic geometric and structural cues (median runtime **5.8 ms**, P95 **21.5 ms**):

1. **Spatial containment grouping**: If a retained or container node's bounding box spatially encloses a set of smaller elements, group those enclosed elements under it as a candidate functional unit.
2. **XML shared-parent grouping**: Group two or more elements that share an immediate XML parent container.
3. **Horizontal and vertical alignment grouping**: For remaining ungrouped elements, group spatially proximate neighbors that form visual rows or columns:
   - *Row grouping*: Elements have similar heights, aligned top edges, and small horizontal gaps between adjacent boxes.
   - *Column grouping*: Elements have similar widths, aligned left edges, and small vertical gaps between adjacent boxes.
4. **Canonical reading order**: Sort children within each unit (and top-level units within the page) left-to-right within rows and top-to-bottom across rows.

### Step 3: Apply the Three Shallow-Hierarchy Simplification Rules

Raw containment and XML parent grouping often produce overly deep, single-branch chains or giant full-screen wrappers. Enforce three deterministic simplification rules to keep the hierarchy shallow and navigable:

1. **Remove oversized unlabelled containers**: Delete any intermediate container node whose bounding box covers **$\ge 80\%$ of the screen area** if it lacks its own text or content description, re-attaching its children directly to the next retained ancestor.
2. **Cap XML sibling grouping depth**: Limit recursive XML sibling/parent grouping to **at most 2 rounds** so deep framework layout wrappers (`FrameLayout` $\rightarrow$ `LinearLayout` $\rightarrow$ `RelativeLayout`) do not create deep menu trees.
3. **Collapse small units ($< 3$ children)**: Flatten any candidate functional unit that contains **fewer than 3 child elements**, exposing its children directly at the parent level. A group of only 1–2 elements adds an extra expand/collapse interaction step without saving sequential swipes.

### Step 4: Refine Multi-Granularity Descriptions in a Single LLM Request

Serialize the simplified hierarchy into a compact JSON tree (preserving node IDs, hierarchy levels, bounding boxes, widget types, and existing text/descriptions) and send the **entire page in a single structured LLM request** (using a fast low-temperature model such as `deepseek-v4-flash`) governed by three level-specific rules:

1. **Page Root (Level 0)**: Identify the overall page category (e.g., product search results, flight booking form) and summarize **at most 3 primary functional areas** so the user or agent immediately understands the screen layout upon arrival.
2. **Functional Units (Level 1)**: Generate a concise group label combining the unit's functional identity with **1–2 domain-critical decision attributes** (for example, product title + price + sales count for a shopping card, or author + post summary for a social feed item). This enables informed skip-or-expand decisions without opening the group.
3. **Atomic Elements (Level 2)**: Preserve existing clear labels verbatim; for unlabelled or generic elements (`button`, `icon`, isolated numbers), synthesize an action-oriented label from parent unit context and adjacent sibling text (for example, rewriting an unlabelled icon next to a quantity counter as `Increase quantity`).

### Step 5: Enforce State-Consistent Hierarchical Navigation

1. **Auto-expand root on page load**: Announce the Page Root summary first and automatically expand its top-level children (Functional Units and ungrouped Atomic Elements) into the active linear focus sequence.
2. **On-demand unit expansion**: Swiping moves across top-level Functional Units; double-tapping an expandable Functional Unit replaces that unit in the focus sequence with its direct children so the user explores inside the unit only when interested. Double-tapping an atomic leaf node dispatches its native accessibility click action.
3. **Gate actions during layout rebuilds**: When scrolling or screen transitions invalidate the accessibility tree, block focus movement and click dispatch with an explicit loading cue until the new hierarchy and descriptions finish building, preventing stale-node mis-activations.

---

## Quantitative Justification

- **Structural Grouping Fidelity (50 Android pages)**: SeeR's deterministic spatial + XML grouping achieves **0.996 pairwise Precision** (1.00 rounded), **0.711 Recall**, and **0.769 F1** against human ground-truth functional units in **5.8 ms median latency** (P95 **21.5 ms**), while retaining **85.2%** of human-annotated semantic actions (comparable to TalkBack's 87.8%).
- **Elimination of Non-Informative Stops**: Single-request LLM refinement reduces non-informative focus stops from **28.8% (535 / 1,858)** under TalkBack to **5.1% (82 stops)**—an **82.1% relative reduction**—at a median latency of **3.4 s** (P95 **5.8 s**) and an average token footprint of **2,535.4 prompt tokens + 273.8 completion tokens** per page ($< \$0.002$ / page).
- **Navigation Distance Reduction (50 targets)**: Sequential focus steps to reach target elements drop by **52.7%**, from **18.7 $\pm$ 16.5 steps** (TalkBack) to **8.8 $\pm$ 6.2 steps** (SeeR; mean paired reduction **9.8 steps**, 95% bootstrap CI $[4.9, 15.0]$, Wilcoxon $W = 108.5, p < .001$).
- **Within-Subjects BLV User Study (10 blind and low-vision participants, 37 paired task attempts across Meituan and JD)**:
  - **Nodes visited per task**: Reduced by **45.8%**, from **17.9 ($SD = 2.8$)** with TalkBack to **9.7 ($SD = 1.4$)** with SeeR (Wilcoxon $W = 0$, Holm-adjusted $p = .004$).
  - **Task completion time**: Reduced by **34.2%**, from **58.2 s ($SD = 27.3$)** with TalkBack to **38.3 s ($SD = 12.9$)** with SeeR (Wilcoxon $W = 4$, Holm-adjusted $p = .014$), with task completion rate rising from **91.9% (34/37)** to **97.3% (36/37)**.
- **Breadth–Depth Trade-off**: Participants strongly preferred hierarchical grouping on **complex or unfamiliar pages** (median rating **4/5**), whereas on **simple or highly familiar pages** where the user already knows the exact target location, flat traversal was preferred (median rating **2/5** for hierarchy on simple pages) because expanding a group adds an extra confirmation step.

---

## Anti-Patterns to Avoid

- **Relying solely on XML parent-child nesting without spatial geometry**: Framework wrappers frequently split visually adjacent elements or merge unrelated screen regions; always combine XML parenthood with bounding-box containment and row/column alignment.
- **Retaining deep hierarchies or 1–2 item groups**: Deep trees force users to repeatedly drill down before reaching actionable controls. Always strip unlabelled containers covering $\ge 80\%$ of the screen, cap sibling grouping at 2 rounds, and flatten groups with fewer than 3 children.
- **Issuing per-element LLM calls for label repair**: Querying an LLM independently for each unlabelled icon incurs prohibitive latency and loses page-level context; pass the simplified page tree in a single structured request.
- **Forcing hierarchical expansion on simple/known screens**: Provide a fast toggle or flat-traversal bypass for simple dialogs and familiar screens with few focusable nodes.

---

## Related Artifacts

- **Spec**: [Mobile and Generative UI Spec](../../specs/mobile-and-generative-ui.spec.md)
- **Skill**: [Mobile UI Hierarchical Synthesis](../mobile-ui-hierarchical-synthesis/SKILL.md)
- **Rules**: [Agent Human Interaction](../../rules/agent-human-interaction.md), [Skill System Design](../../rules/skill-system-design.md)
