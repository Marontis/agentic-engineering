# ToolDex: An Ego-Exo Human Demonstration Dataset for Creative Physical Tool Use

> **Source**: [arXiv:2611.09036](https://arxiv.org/abs/2611.09036) — *ToolDex: An Ego-Exo Human Demonstration Dataset for Creative Physical Tool Use* (Elmoghany et al., November 2026)
> **Praxis Source ID**: `src:2611-09036v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

`ToolDex` is a real-world multimodal human demonstration dataset and embodied robotics benchmark suite covering sparse-view 3D/4D Gaussian Splatting reconstruction, vision-language model (`VLM`) physical tool-use affordance reasoning, and dexterous robot policy learning (`ManipTrans`, `Dex-X`). It does not introduce a software-agent orchestration or coding procedure, but provides valuable empirical benchmarks on the gap between high-level VLM semantic tool selection and fine-grained spatial/trajectory grounding.

---

## Dataset Architecture & Scale (`Sections 3–4`, `Table 1`)

Unlike prior hand–object interaction datasets (`TACO`, `OakInk2`, `HOT3D`, `GigaHands`) that use a single combined object inventory or focus on rigid objects without modeling the target medium, `ToolDex` explicitly separates **three physical roles**—**hand**, **tool object** (actuated by the hand), and **target object** (deformable, granular, or rigid medium altered indirectly via tool contact, alongside unactuated **support objects** like bowls or plates)—formalized as a goal-conditioned MDP $(\mathcal{S}, \mathcal{A}, T, \gamma, \mathcal{G})$ with two-level actions (embodiment-invariant 6-DoF tool pose and human `MANO` hand/wrist pose).

| Property | `ToolDex` Specification |
|:---|:---|
| **Total Scale** | `10,853` trials (`10.8K`), `60` hours of demonstrations (`~60` trials/hour), `58.3M` total multi-view frames, `6,158,809` annotated frames |
| **Trial Duration** | Mean `18.92` seconds (`567.58` frames) per trial at `30 Hz` |
| **Combinatorial Task Space** | `60` high-level `(tool, action, target)` combinations and `168` total variants; each tool participates in `2.3` actions on average, and each action is realized by `3.6` tools on average |
| **Object & Action Inventory** | `45` tool objects (flat blades, volumetric scoopers, elongated rods, creatively repurposed books/cups/pans), `23` target/support objects, `16` deformable object types (dough, naan, towel, tomato sauce, sand, kinetic sand, coffee, nuts), `16` action verbs |
| **Scene Clutter** | `4–5` distractor tools placed on the tabletop per trial with varied initial poses to require visual grounding |
| **Synchronized Multi-View Rig** | **Egocentric**: `1` Stereolabs `ZED Mini` stereo RGB camera (`2` streams at $1280\times 720$) mounted on an `Apple Vision Pro` headset; **Exocentric**: `8` calibrated `Intel RealSense 435` RGB-D cameras at $1280\times 720$ and `30 Hz` on an aluminum frame |
| **Annotation Pipeline** | Target-object masks via `SAM2` + `DINOv2` seed initialization; 6-DoF tool poses via `FoundationPose` on `Shining3D`-scanned textured meshes with multi-view bundle adjustment; metric `MANO` hand poses via `WiLoR` + RGB-D point-cloud scale alignment; joint hand–tool SDF contact refinement (`HO-Cap`) |

---

## Benchmark Suite & Quantitative Results (`Section 5`)

### 1. Sparse-View 3D and 4D Gaussian Splatting Reconstruction (`Section 5.1`, `Table 2`)

Trained on `7` exocentric cameras (`cam 6` withheld for ground-truth `PSNR` evaluation; all `8` cameras used for reference-free `MUSIQ` perceptual quality on a `0–100` scale), comparing `SplatFormer`, `InstantSplat` (`IS`, seeded with `MASt3R` dense-point priors), and two-stage diffusion repair (`Difix3D` and `GSFix3D`):

| Metric | Static 3DGS: `SplatFormer` | Static 3DGS: `IS` | Static 3DGS: `IS + Difix3D` | Dynamic 4DGS: `IS-4D` | Dynamic 4DGS: `IS-4D + Difix3D + GSFix3D` |
|:---|:---:|:---:|:---:|:---:|:---:|
| **`PSNR` (dB, held-out cam 6) $\uparrow$** | `13.09` | `19.97` | **`20.45`** (`+0.48` over `IS`) | **`19.60`** | `15.97` (`-3.63` vs. `IS-4D`) |
| **`MUSIQ` (0–100 perceptual) $\uparrow$** | `33.11` | `50.66` | **`55.11`** (`+4.45` over `IS`) | `51.00` | **`69.92`** (`+18.92` over `IS-4D`) |

- **Photometric-vs-Perceptual Dissociation in 4D**: Chaining single-step diffusion repair (`Difix3D + GSFix3D`) on per-timestep 4D Gaussian Splatting (`IS-4D`) boosts perceptual quality by **`+18.92` `MUSIQ` points** (`51.00` $\to$ `69.92`) while lowering pixel-wise held-out `PSNR` by **`3.63 dB`** (`19.60` $\to$ `15.97`).

### 2. VLM Physical Tool-Use Reasoning (`Section 5.2`, `Tables 3–4`)

Evaluated across `180` manually verified trajectories (`32` task variants) for **Tool Selection** (identifying plausible substitute tools in cluttered scenes) and **Spatial Grounding** (bounding-box IoU on semantically matched tool predictions), plus `160` trajectories for zero-shot **Behavioral Planning** (predicting 2D top-view manipulation trajectories in pixels under tool-center projection and correspondence-aware transported-point construction):

| Model | Tool Selection Acc. $\uparrow$ (`Table 3`) | Spatial Grounding BBox IoU $\uparrow$ (`Table 3`) | Behavioral Plan Eval Success $\uparrow$ (`Table 4`) | Tool-Center Mean L2 / Chamfer-L2 (px) $\downarrow$ | Corr.-Aware Mean L2 / Chamfer-L2 (px) $\downarrow$ |
|:---|:---:|:---:|:---:|:---:|:---:|
| **`GPT-6-Astra`** | **`.800`** (`80.0%`) | **`.891`** | **`89.4%`** | `239.37` / `120.38` | `227.85` / `97.11` |
| **`Claude-Sonnet-4.6`** | **`.800`** (`80.0%`) | `.641` | — | — | — |
| **`Claude-Opus-4.7`** | **`.800`** (`80.0%`) | `.564` | — | — | — |
| **`Gemini-3.1-Pro`** | `.781` (`78.1%`) | `.010` | — | — | — |
| **`Gemini-3-Flash`** | `.756` (`75.6%`) | `.050` | — | — | — |
| **`GPT-5-mini`** | `.662` (`66.2%`) | `.300` | — | — | — |
| **`Qwen-3.6-27B`** | `.638` (`63.8%`) | `.004` | `37.5%` | `244.88` / `128.44` | `228.61` / `103.71` |
| **`Qwen-3.5-9B`** | `.557` (`55.7%`) | `.003` | — | — | — |
| **`Gemma 4 31B`** | — | — | `86.9%` | `259.96` / `104.17` | `269.73` / `107.31` |
| **`Gemini Robotics ER 1.6`** | — | — | `77.5%` | **`230.37`** / **`91.91`** | **`223.15`** / **`74.44`** |
| **`Claude Fable 5`** | — | — | `71.3%` | `263.33` / `146.37` | `234.89` / `102.61` |

- **Semantic-vs-Spatial Grounding Gap**: While `Claude-Sonnet-4.6`, `Claude-Opus-4.7`, `GPT-6-Astra` (`80.0%`), and `Gemini-3.1-Pro` (`78.1%`) all exhibit strong semantic affordance reasoning when selecting creative substitute tools (e.g., choosing a rolling pin when a mortar and pestle is absent), `Gemini` and `Qwen` models fail almost completely at bounding-box localization (`IoU` `0.003–0.050` vs. `0.891` for `GPT-6-Astra`).
- **Reliability-vs-Precision Trade-off in Trajectory Planning**: General-purpose `GPT-6-Astra` achieves the highest valid output rate (`89.4%` vs. `77.5%` for `Gemini Robotics ER 1.6` and `37.5%` for `Qwen 3.6 27B`), whereas domain-specialized `Gemini Robotics ER 1.6` achieves the lowest pixel trajectory error on valid outputs (`74.44 px` correspondence-aware Chamfer-L2 vs. `97.11 px` for `GPT-6-Astra`), though both struggle with cyclic, long-horizon contact motions like repeated grinding or sweeping.

### 3. Human-to-Robot Policy Transfer (`Section 5.3`, `Table 5`)

Evaluating dexterous robot policy learning across `6` representative contact-rich tool-use tasks:

| Action & Tool | `Kinematic Retarget` | `BC (Retarget)` | `ManipTrans (RL)` | `Dex-X (RL)` |
|:---|:---:|:---:|:---:|:---:|
| **Stir coffee (`spatula`)** | `7.0%` | `1.6%` | `52.2 ± 2.2%` | **`72.7 ± 0.8%`** |
| **Scoop nuts (`ladle`)** | `22.2%` | `9.1%` | `62.9 ± 0.4%` | **`66.8 ± 1.3%`** |
| **Crush banana (`mallet`)** | `10.2%` | `2.6%` | `53.0 ± 1.9%` | **`55.8 ± 0.2%`** |
| **Scoop nuts (`scooper`)** | `31.0%` | `9.8%` | **`45.3 ± 2.0%`** | `31.3 ± 0.6%` |
| **Crush nuts (`pestle`)** | `7.0%` | `1.9%` | `16.8 ± 0.2%` | **`46.7 ± 2.4%`** |
| **Collect sand (`squeegee`)** | `6.9%` | `2.6%` | `12.6 ± 0.7%` | **`57.5 ± 1.9%`** |
| **Average Success Rate** | `14.0%` | `4.6%` | `40.5%` | **`55.1%`** |

- Direct motion transfer (`Kinematic Retarget` `14.0%`, `BC` `4.6%`) collapses under non-rigid contact dynamics and human-to-robot embodiment mismatch, whereas joint hand-and-arm physical interaction adaptation via reinforcement learning (`Dex-X RL` **`55.1%`**, `ManipTrans RL` `40.5%`) is essential—especially for high-resistance contact tasks (`Crush nuts` `16.8%` $\to$ `46.7%`; `Collect sand` `12.6%` $\to$ `57.5%`).

---

## Relevance to Praxis

- **Separating Semantic Tool Choice from Spatial/Execution Grounding**: Reinforces findings in [`flex-rsi-frontier-agent-benchmark.md`](flex-rsi-frontier-agent-benchmark.md) and [`embodied-vla-skill-orchestration.md`](embodied-vla-skill-orchestration.md)—frontier VLMs that score `75–80%` on high-level semantic tool selection can simultaneously score `0.003–0.050` BBox IoU on spatial localization unless explicitly grounded or paired with interaction-aware low-level controllers.
