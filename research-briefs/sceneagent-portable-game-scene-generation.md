# SceneAgent: A Multi-Agent Framework for Portable Game Scene Generation

> **Source**: [arXiv:2611.17821](https://arxiv.org/abs/2611.17821) — Xingyi Li, Jiahao Yang, Yiqin Zhu, Jingwen Ye, Yang Sun, Weidong Zhang (Tencent, Fudan University, 2026)
> **Praxis Source ID**: `src:2611-17821v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

`SceneAgent` studies **construction portability** for 3D game-environment synthesis (`Engine A` and `Engine B` on `GameSceneBench`), coupling a canonical 3D world state (`SceneContext`), fresh per-subtask `Builder` sessions, and human-curated `Layout` + `Content` + `Thin Recipe` skill triplets. Under our [`skill-design-methodology`](../skills/skill-design-methodology/SKILL.md) criteria and [`AGENTS.md`](../AGENTS.md) standards, its concrete toolset (`place_against_wall`, `pcg_scatter`, `surface_sampler`, `check_bbox_collision`, entity-first 3D asset `InfoNCE` retrieval, and quaternion/unit scene adapters) is specialized to 3D scene authoring, while its generalizable software abstractions—transcript-free file/state ledgers ([`ledger-orchestrated-coding-loop`](../skills/ledger-orchestrated-coding-loop/SKILL.md)), semantic-commitment vs. interface realization ([`decoupled-interface-action-repair`](../skills/decoupled-interface-action-repair/SKILL.md)), de-instantiated global skill priors ([`procedural-family-skill-consolidation`](../skills/procedural-family-skill-consolidation/SKILL.md)), and `Semantic-Style-Layout` decoupling ([`editable-semantic-diagram-generation`](../skills/editable-semantic-diagram-generation/SKILL.md))—are already represented as standalone skills. Moreover, as the authors note in `§6.3–6.5` and `§7`, the cross-engine study is qualitative only and the skill-library ablation tests `0` vs. `20` vs. `50` skills without isolating `Layout–Content` factorization against unfactored skill memory. We therefore capture `SceneAgent` as a Research Brief and extract its cross-backend state-and-skill portability guardrails and latency/geometry trade-offs into [`skill-system-design.md`](../rules/skill-system-design.md).

---

## Core Architecture: Construction Portability Across Three Boundaries

Exporting an interoperable scene file (e.g., `USD`) makes final outputs portable but leaves planning prompts, tool histories, and trajectory memories bound to native engine coordinates and asset IDs. `SceneAgent` separates three layers (`Table 1`):

1. **Canonical `SceneContext` & Orchestrator-Only Backend Adapter**:
   - All `Builders` read and mutate a shared canonical state (`X`: left–right, `Y`: up, `Z`: forward–back) storing actor transforms, bounding boxes, an occupancy index, source tags, and subtask provenance through shared tools (`Table 6`: `search_modules`, `place_module`, `place_facing`, `create_line`, `pcg_scatter`, `check_bbox_collision`, `undo_subtask`).
   - Low-level serialization (`export_json`) is hidden from `Builder` sessions (`Appendix B.2`, `Table 7`) and invoked solely via the `Orchestrator`'s `export_scene` tool through a backend adapter—converting canonical state to **`Engine A`** (actor array, string `typeId`, centimeters, quaternion rotations) or **`Engine B`** (`PCGGenerate` command wrapper, numeric `typeId`, meters, fixed-precision transform strings, runtime `AIID`).
   - `search_modules` trains a shared encoder with `InfoNCE` over synthesized queries and **deceptive entity-mismatched hard negatives** (`entity-first` objective: matching category before style/material), returning top-$K$ *proposals* that `Builders` inspect via metadata/thumbnails before binding.
2. **Transcript-Free `Planner–Builder` Handoffs**:
   - The `Orchestrator` (`<= 30` rounds, `<= 3` auto-refinement rounds) retrieves `Layout` and `Content` skills as read-only prompt sections; the `Planner` (`<= 50` rounds, `<= 40` tool calls) emits `5–10` outdoor or `3–6` indoor semantic subtasks.
   - Each subtask spawns a **fresh `Builder` session (`<= 40` rounds)** seeded with its task record, shared axis/scale conventions, selected skills, and **compact completion reports** (`status`, `summary`, `residual_issues`, `actor_count_delta`)—discarding prior raw placement transcripts while querying live `SceneContext` footprints on demand, gated by deterministic collision/bounds checks (`check_bbox_collision`).
3. **Human-Gated Factored Experience (`Layout` + `Content` + `Thin Recipe`)**:
   - Completed text- or VLM-interpreted reference-image traces undergo automated geometry diagnostics followed by a **human quality gate** (`Algorithm 1`); rejected traces and critiques are stored separately as **failure evidence**.
   - Approved traces are factored into schema-validated, deduplicated triplets (`Appendix G.2`): (a) asset-ID-free **`Layout` skills** (route topology, anchors, circulation corridors, footprint rules), (b) binding-free **`Content` skills** (semantic object roles, color/lighting palettes, and missing-asset **substitution rules**, e.g., replacing a missing food stall with a canopy-and-counter assembly), and (c) scene-specific **`Thin recipes`** referencing both skills plus prompt residuals.

---

## Empirical Evaluation on `GameSceneBench` (`69` Prompts: `56` Outdoor, `13` Indoor)

Evaluated on `Engine A` with `DeepSeek-V4-Flash` (`204,800`-token window), `3` independent runs/prompt, `5` rendered `1920×1080` (`60°` FOV) views/scene, `CLIP ViT-L/14`, randomized bidirectional `2×5` pairwise `gpt-4o-2024-11-20` VLM judging, and **`1,860` blinded human judgments** from `51` qualified participants (`65` recruited, `14` excluded for `< 30` of `50` trials; `50%` = parity, ties = `0.5` win):

### 1. Main Baseline Comparison (`Tables 2 & 8`)

| Comparator (`Engine A`, Common Catalog) | Comparator `CLIPScore` (↑) | Comparator Runtime (s ↓) | `SceneAgent` VLM Align. | `SceneAgent` VLM Plaus. | `SceneAgent` VLM Comp. | `SceneAgent` Human Pref. (`n` Judgments) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| `AutoUE†` (layout stage) | `0.188 ± 0.030` | **`16.3 ± 2.9`** | `94.2%` | `74.4%` | `91.3%` | **`89.4%`** (`83.4%` W / `11.9%` T / `4.8%` L, `n=379`) |
| `Holodeck` | `0.185 ± 0.030` | `60.7 ± 19.1` | `81.5%` | `74.1%` | `77.1%` | **`85.2%`** (`78.5%` W / `13.3%` T / `8.2%` L, `n=368`) |
| `ImperativeScene` | `0.214 ± 0.030` | `21.4 ± 29.8` | `77.3%` | `65.3%` | `74.9%` | **`78.2%`** (`71.8%` W / `12.8%` T / `15.4%` L, `n=383`) |
| `Reason-3D` | `0.196 ± 0.033` | `23.2 ± 11.4` | `78.3%` | `61.6%` | `82.6%` | **`81.2%`** (`75.0%` W / `12.4%` T / `12.6%` L, `n=364`) |
| `SceneWeaver` | `0.193 ± 0.030` | `226.4 ± 140.0` | `83.5%` | `64.4%` | `76.7%` | **`82.7%`** (`76.0%` W / `13.4%` T / `10.7%` L, `n=366`) |
| **`SceneAgent` (`50` skills)** | **`0.216 ± 0.034`** | `203.2 ± 97.8` | — | — | — | **`83.3%` overall** (`76.9%` W / `12.7%` T / `10.3%` L, `N=1,860`) |

### 2. Skill-Library, Multi-Agent, Cross-LLM & Cross-Engine Ablations (`§6.3–6.5`, `Tables 3–4`)

- **Frozen Experience-Library Size (`0` vs. `20` vs. `50` Human-Approved Skills, `Table 3`)**:
  - `CLIPScore` inches from `0.211 ± 0.031` (`0` skills, **`173.3 ± 56.4 s`**) $\to$ `0.214 ± 0.032` (`20` skills, `190.8 ± 67.9 s`) $\to$ **`0.216 ± 0.034`** (`50` skills, `203.2 ± 97.8 s`).
  - Against `0` skills, the `50`-skill library wins on **`Completeness` (`63.8%`)** and **`Alignment` (`59.7%`)**, **but drops below parity on `Spatial Plausibility` (`46.2%`**, `56.6%` 3-dimension aggregate); against `20` skills, `50` skills reaches `52.1%` aggregate (`55.6%` Align., `50.5%` Plaus., `50.0%` Comp.), showing diminishing returns past `20` skills and confirming that text skills organize semantic content rather than improving geometric placement.
- **Single-Agent Transcript vs. Multi-Agent Protocol (`Table 4`)**:
  - Multi-agent `SceneAgent` (`0.216 ± 0.034` CLIP) beats a single-session plan-then-construct agent (`0.210 ± 0.032` CLIP) with **`57.0%` overall VLM preference** (`54.6%` W / `4.8%` T / `40.6%` L), driven by **`Completeness` (`62.4%` vs. `37.7%`)** and **`Alignment` (`57.5%` vs. `42.5%`)** while `Spatial Plausibility` stays near parity (`51.0%` vs. `49.0%`)—at **`5.17×` higher runtime (`203.2 ± 97.8 s` vs. `39.3 ± 24.2 s`)**.
- **Cross-LLM & Cross-Engine Portability (`§6.3`)**:
  - Running all `69` prompts across `DeepSeek-V4-Flash`, `Gemini 3.5 Flash`, `Hy3`, and `Qwen3.6-35B-A3B` shows near-parity between `Gemini 3.5 Flash` and `DeepSeek-V4-Flash` (`51.2%` vs. `48.9%` aggregate VLM preference; `0.220` vs. `0.216` CLIP; Gemini `52.4%` Align. / `53.0%` Plaus., DeepSeek `51.9%` Comp.) despite **`1.84×` slower runtime (`374.8 s` vs. `203.2 s`)**.
  - Deploying all `69` prompts to `Engine B` reused the identical `Orchestrator`/`Planner`/`Builder` protocol, `SceneContext`, core tools, and `50`-skill library while swapping only the adapter, catalog, and native wrappers (qualitative evaluation only due to differing asset catalogs).

---

## Methodological Boundaries & Engineering Takeaways

1. **Hide native export tools from worker sessions so portability is structural, not prompt-advisory**: Exposing `export_json` only to the `Orchestrator` adapter forces `Builders` to reason in canonical `SceneContext` coordinates and semantic asset queries rather than leaking engine-specific serialization into traces or skills.
2. **Pair ID-free `Layout`/`Content` skills with deterministic geometric validators—and gate autonomous updates**: Because `50` skills lowered `Spatial Plausibility` to `46.2%` vs. `0` skills and rendered-view VLM scores do not verify physics or navigability, keep collision/support checks (`check_bbox_collision`) deterministic and pass any automated skill-library update through `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../rules/recursive-improvement.md).

---

## Related Artifacts

- **Rules**:
  - [`skill-system-design.md`](../rules/skill-system-design.md) — Canonical state adapters, factored `Layout` vs. `Content` skills, and execution-verified retrieval
  - [`multi-agent-coordination.md`](../rules/multi-agent-coordination.md) — Persistent ledger coordination and the `5.17×` latency vs. completeness trade-off
  - [`agent-human-interaction.md`](../rules/agent-human-interaction.md) — `Semantic-Style-Layout` decoupling in editable diagram synthesis
- **Skills**:
  - [`procedural-family-skill-consolidation`](../skills/procedural-family-skill-consolidation/SKILL.md) — De-instantiating concrete IDs into frozen global priors (`SkillGLoW`, `arXiv:2609.02217`)
  - [`decoupled-interface-action-repair`](../skills/decoupled-interface-action-repair/SKILL.md) — Separating semantic commitments from target interface realization (`arXiv:2610.34298`)
  - [`ledger-orchestrated-coding-loop`](../skills/ledger-orchestrated-coding-loop/SKILL.md) — Fresh worker contexts over persistent file ledgers (`arXiv:2608.26480`)
  - [`editable-semantic-diagram-generation`](../skills/editable-semantic-diagram-generation/SKILL.md) — `Semantic-Style-Layout` canvas generation (`EvoDiagram`, `arXiv:2604.09568`)
