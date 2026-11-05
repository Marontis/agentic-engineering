# LegalEvolver: Agentic Legal Judgment Prediction via Rubric-Guided Self-Evolution

> **Source**: [arXiv:2611.06381](https://arxiv.org/abs/2611.06381) | `src:2611-06381`
> **Authors**: Xinyu Yang, Jiejun Tan, Chenlong Deng, Chenghao Zhang, Tongyu Wen, Zhicheng Dou (Renmin University of China)
> **Date**: November 2026
> **Categories**: cs.CL, cs.AI
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Summary

`LegalEvolver` is a rubric-guided self-evolution framework for agentic Legal Judgment Prediction (`LJP`) over Chinese criminal cases, where an LLM agent must jointly predict applicable law articles ($l$), criminal charges ($c$), and prison terms ($t$) by iteratively querying external legal knowledge bases. Unlike open-domain QA where retrieval errors stem from missing surface keywords, agentic `LJP` failures primarily arise from **reasoning-focus drift**: the agent invokes the right retrieval tool (`Law article retrieval`, `Precedent retrieval`, `Judicial interpretation retrieval`, or `Sentencing guideline retrieval`) with an under-specified query that conflates legal qualification (distinguishing confusable charges and statutory elements) with sentencing refinement (aggravating/mitigating thresholds and penalty bands).

To provide step-level process supervision without human annotations, `LegalEvolver` stratifies multi-rollout trajectories within the same case into three outcome states—complete success ($S_3$: $\hat{l}=l, \hat{c}=c, \hat{t}=t$), correct qualification with wrong sentencing ($S_2$: $\hat{l}=l, \hat{c}=c, \hat{t}\neq t$), and qualification failure ($S_1$)—and pairs trajectories across states to isolate three reasoning focuses: **Sentencing** ($S_3 \text{ vs. } S_2$), **Legal Qualification** ($S_2 \text{ vs. } S_1$), and **Full Repair** ($S_3 \text{ vs. } S_1$). From these within-case contrastive query pairs across the $4 \times 3 = 12$ tool-focus groups, an LLM evaluator (`Qwen2.5-72B-Instruct`) induces structured 4-level scoring rubrics (`0–3`) validated on held-out pairs. The agent (`Qwen3-8B`) is then warmed up via rubric-filtered supervised fine-tuning (`SFT`) and co-evolves over 3 rounds of Group Relative Policy Optimization (`GRPO`) where the rubric library $\mathcal{R}_k$ is updated alongside the policy to match the agent's shifting query error distribution.

---

## Key Findings

1. **Within-case trajectory stratification isolates retrieval focus without step labels**: By comparing rollouts on the *same* case that share an identical tool choice at their first divergence step, `LegalEvolver` attributes downstream outcome differences ($S_3 \text{ vs. } S_2 \text{ vs. } S_1$) directly to query formulation. Combining `9,143` natural preference pairs (`1,394` legal qualification, `5,285` sentencing, `2,464` full-repair) with `11,701` targeted query-rewriting pairs yields `20,844` total contrastive pairs, from which `340` candidate rubric criteria are induced and filtered via held-out validation across `10` populated tool-focus groups.
2. **Tool- and focus-specific rubrics outperform shared rubrics and outcome-only RL**: On `CAIL2018` (`1,000` single-defendant test cases, `189` charges, `140` articles) and `CMDL` (`2,000` multi-defendant test cases, `117` charges, `106` articles, `2–28` defendants/case), `LegalEvolver` achieves an overall score of `61.53%` (`61.5%` in Table 1), outperforming `Vanilla SFT` (`58.5%`), outcome-only `Standard GRPO` (`59.9%`), `SmartSearch` (`60.4%`), and domain workflow `GLARE` (`54.7%`). Replacing the $4 \times 3$ tool-focus rubrics with a single shared rubric drops overall performance by `-1.38` points (`61.53%` $\to$ `60.15%`), while removing rubric rewards during `GRPO` drops performance by `-1.60` points (`61.53%` $\to$ `59.93%`).
3. **Co-evolving rubrics prevent reward hacking and stale supervision**: Freezing the initial rubric library $\mathcal{R}_0$ (`w/o Rubric Evolution`) lowers overall accuracy/F1 from `61.53%` to `60.38%` (`-1.15` points; `CAIL2018` Ma-F1 drops by `-2.03` points from `54.53%` to `52.50%`). Across the 3 co-evolution rounds, `CAIL2018` overall score rises monotonically from `54.7%` (Round 0 `SFT`) to `56.6%` (Round 1), `57.2%` (Round 2), and `57.9%` (Round 3), while `CMDL` rises from `62.1%` to `64.1%`, `64.6%`, and `65.2%`.
4. **Prison-term prediction remains the hardest bottleneck in agentic LJP**: Even with specialized sentencing-guideline and judicial-interpretation retrieval tools, prison-term prediction (`22.1%` Acc / `21.0%` Ma-F1 on `CAIL2018`; `25.6%` Acc / `22.8%` Ma-F1 on `CMDL`) lags far behind article and charge prediction (`79.4%–85.7%` Acc), though `LegalEvolver` more than doubles the `Qwen3-8B` direct-reasoning baseline (`8.7%` and `9.0%` term accuracy).

---

## Quantitative Summary

### Main Benchmark Comparison (`CAIL2018` & `CMDL`, `Qwen3-8B` Backbone Unless Noted)

| Method | `CAIL2018` Article (Acc / Ma-F1) | `CAIL2018` Charge (Acc / Ma-F1) | `CAIL2018` Term (Acc / Ma-F1) | `CMDL` Article (Acc / Ma-F1) | `CMDL` Charge (Acc / Ma-F1) | `CMDL` Term (Acc / Ma-F1) | Overall |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `Qwen3-8B` (Direct Reasoning) | `60.9` / `42.8` | `56.9` / `34.6` | `8.7` / `6.9` | `67.5` / `77.1` | `73.6` / `78.3` | `9.0` / `8.2` | `43.7` |
| `Qwen-Max` (Direct Reasoning) | `76.5` / `63.6` | `75.8` / `66.1` | `15.7` / `14.5` | `78.4` / `84.6` | `84.5` / `84.3` | `12.6` / `10.5` | `55.6` |
| `Agentic RAG` (`Qwen3-8B`) | `64.2` / `45.3` | `62.2` / `40.4` | `7.3` / `5.7` | `72.4` / `80.1` | `76.7` / `80.2` | `4.6` / `3.6` | `45.2` |
| `Search-o1` (`Qwen3-8B`) | `68.2` / `48.2` | `65.9` / `43.9` | `11.1` / `9.7` | `72.6` / `81.2` | `76.3` / `80.3` | `10.0` / `8.2` | `48.0` |
| `PLJP` (`Qwen3-8B`) | `71.0` / `56.6` | `64.6` / `48.2` | `8.9` / `8.4` | `71.6` / `79.6` | `73.9` / `76.1` | `11.9` / `10.9` | `48.5` |
| `GLARE` (`Qwen3-8B`) | `76.4` / `63.2` | `75.8` / `66.6` | `13.4` / `12.5` | `78.2` / `85.1` | `82.1` / `83.9` | `10.5` / `8.3` | `54.7` |
| `Vanilla SFT` (`Qwen3-8B`) | `79.3` / `68.8` | `76.6` / `69.9` | `20.2` / `19.6` | `82.5` / `86.3` | `80.8` / `82.1` | `18.3` / `17.3` | `58.5` |
| `Standard GRPO` (`Qwen3-8B`) | `80.7` / `68.7` | `77.7` / `70.1` | `21.7` / `19.9` | `84.8` / `86.9` | `83.1` / `84.5` | `21.2` / `19.5` | `59.9` |
| `SmartSearch` (`Qwen3-8B`) | `80.9` / `69.5` | `78.4` / `70.2` | `21.4` / `19.9` | `84.4` / `86.7` | `83.5` / `84.8` | `24.1` / `20.8` | `60.4` |
| **`LegalEvolver` (`Qwen3-8B`)** | **`82.1`** / **`70.7`** | **`79.4`** / **`71.9`** | **`22.1`** / **`21.0`** | **`85.7`** / **`87.6`** | **`84.4`** / **`85.1`** | **`25.6`** / **`22.8`** | **`61.5`** |

### Ablation Study (Table 4 Averages Across Article, Charge, and Term)

| Variant | `CAIL2018` Acc. | `CAIL2018` Ma-F1 | `CMDL` Acc. | `CMDL` Ma-F1 | Overall |
|:---|:---:|:---:|:---:|:---:|:---:|
| **`LegalEvolver` (Full)** | **`61.20`** | **`54.53`** | **`65.23`** | **`65.17`** | **`61.53`** |
| `w/o Rubric Evolution` (fixed $\mathcal{R}_0$) | `60.03 (-1.17)` | `52.50 (-2.03)` | `64.33 (-0.90)` | `64.63 (-0.54)` | `60.38 (-1.15)` |
| `w/o Rubric Rewards` (outcome + format RL only) | `60.03 (-1.17)` | `53.03 (-1.50)` | `63.43 (-1.80)` | `63.23 (-1.94)` | `59.93 (-1.60)` |
| `w/o Targeted Rubrics` (single shared rubric) | `60.01 (-1.19)` | `52.77 (-1.76)` | `63.88 (-1.35)` | `63.93 (-1.24)` | `60.15 (-1.38)` |
| `w/o GRPO` (`SFT` only) | `58.83 (-2.37)` | `53.00 (-1.53)` | `61.27 (-3.96)` | `60.87 (-4.30)` | `58.49 (-3.04)` |
| `w/o SFT` (`GRPO` from base model) | `48.23 (-12.97)` | `34.57 (-19.96)` | `50.97 (-14.26)` | `55.07 (-10.10)` | `47.21 (-14.32)` |

---

## Why Not a Skill?

1. **Tight coupling to Chinese criminal statutory structure and RL weight updates**: The core outcome decomposition ($S_3, S_2, S_1$ over law articles $l$, charges $c$, and prison terms $t$), the 4 specialized legal corpora (`491` criminal statutes, China Judgments Online precedents, `7,214` judicial interpretation clauses, `64` sentencing guidelines encoded with `SAILER-zh`), and the `VERL`-based `LoRA SFT` + `GRPO` weight training pipeline are specific to statutory legal judgment prediction.
2. **Existing skill coverage for rubric-driven evolution**: General inference-time rubric synthesis and failure-clustered evolutionary refinement are already covered in [`dense-rubric-skill-evolution`](../skills/dense-rubric-skill-evolution/SKILL.md) and [`error-structured-prompt-optimization`](../skills/error-structured-prompt-optimization/SKILL.md), while evidence-gap tool supervision is covered in [`necessary-tool-evidence-path`](../skills/necessary-tool-evidence-path/SKILL.md).

---

## Actionable Takeaways

- **Condition query evaluation rubrics on `(tool, reasoning_focus)` pairs rather than a global prompt**: When an agent queries multiple specialized knowledge bases, a single shared query rubric degrades accuracy (`-1.38` points in `LegalEvolver`). Partition rubrics by the specific tool invoked and the sub-goal being resolved.
- **Construct contrastive step pairs within the same task instance**: To isolate why a tool query succeeded or failed without confounding task difficulty, pair rollouts on the *same* input that chose the *same* tool at their first divergence point but reached different hierarchical outcome levels.
- **Co-evolve process rubrics alongside the policy**: Static rubrics induced from initial rollouts become stale as the policy eliminates basic formatting or keyword errors (`-1.15` points overall and `-2.03` Ma-F1 on `CAIL2018` when $\mathcal{R}_0$ is frozen). Periodically re-induce and validate rubric criteria on fresh trajectory failures.

---

## Related Artifacts

- **Skill**: [`dense-rubric-skill-evolution`](../skills/dense-rubric-skill-evolution/SKILL.md) — Dense dynamic rubric synthesis for evolutionary agent optimization.
- **Skill**: [`necessary-tool-evidence-path`](../skills/necessary-tool-evidence-path/SKILL.md) — Supervising pre-call tool intents and post-call evidence extraction.
- **Rules**: [`recursive-improvement.md`](../rules/recursive-improvement.md) — Guardrails for rubric co-evolution and self-improvement loops.
