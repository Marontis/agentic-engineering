# RSIV-Harness: Recursive Self-Improvement Harness for Open-Domain Conversational Visualization

> Source: `src:2610-35316` — "RSIV-Harness: A Recursive Self-Improvement Harness Framework for Open-Domain Conversational Text-to-Visualization" (arXiv:2610.35316, 2026)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Classification: Research Brief (Contextual Knowledge)

This paper is classified as a **research brief** because its inner loop and evaluation rubric are tailored to multi-turn, open-domain conversational text-to-visualization (`ODAC-Vis`). However, its **four-layer stability rule framework** ($\mathcal{R} = \{\text{RF}, \text{RS}, \text{AC}, \text{MC}\}$) governing how a frozen-weight LLM evolves its own five-component harness (prompts, tools, memory, skills, and middleware) provides rigorous empirical validation for the acceptance-gate and champion-rollback rules in `rules/recursive-improvement.md`.

---

## Problem & Motivation

Open-domain conversational visualization requires an agent to discover which database(s) in a large collection can answer a user's request, decide at every turn whether the request is ambiguous (requiring a clarification question) or fully specified (requiring executable SQL + visualization code), and iteratively refine or drill down across turns. Static agent harnesses fail when multi-turn schema routing or ambiguity patterns fall outside their hand-crafted rules, while unconstrained self-modifying harnesses suffer from catastrophic forgetting and oscillatory regressions where fixing one failure cluster breaks previously solved turns.

---

## Benchmark (`ODAC-Vis`) and Bi-Level Architecture

### 1. The `ODAC-Vis` Benchmark

The authors construct **ODAC-Vis**, a 640-task open-domain, ambiguity-aware conversational visualization benchmark spanning 3 complexity tiers (`Single-table`: 192 tasks / 30.0%; `Single-db join`: 320 / 50.0%; `Cross-database`: 128 / 20.0%), 2 dialogue scenarios (`Drilldown`: 320 / 50.0%; `Iterate`: 320 / 50.0%), 3 to 8 turns per conversation, and 8 balanced ambiguity types (~120 tasks / 18.8% each: column selection, aggregation granularity, filter logic, unit scale, chart type, encoding mapping, axis label, and interactivity). Domains are partitioned into 124 train, 96 validation, and **15 held-out test domains (96 test tasks)**. In a blind 100-task audit on Relevance / Plausibility / Readability (0–100), ODAC-Vis scored **93.6 / 82.1 / 87.3** under expert review (**91.8 / 78.7 / 86.2** under `DeepSeek-V4.1-Flash` evaluation), outperforming Dial-NVBench and NVBench 2.0.

### 2. Four-Layer Stability Rule Framework ($\mathcal{R} = \{\text{RF}, \text{RS}, \text{AC}, \text{MC}\}$)

RSIV-Harness pairs an inner ReAct task-solving loop (with up to $K(H)$ sandbox execution repairs per turn and optional context-refresh middleware $z_\tau = f_H(h_\tau)$) with an outer self-improvement loop over a fixed 48-task stratified training panel $S$ and a 48-task validation anchor $S_{\text{val}}$. Each outer round proposes at most $E$ component edits $H' = \text{Improve}(g(H_n), H_n)$ across 5 mutable harness surfaces (**prompt, tool, memory, skill, middleware**) and subjects $H'$ to four stability layers (implementing `"DO: Pass every self-modification through one acceptance gate"` in [recursive-improvement.md](../rules/recursive-improvement.md)):

1. **Memory Check (`MC` — Protected-Record Non-Regression, Theorem 4)**:
   - Maintains a bounded capacity-$C$ memory $\mathcal{P}$ of protected turn–metric records $(x, t, d, b)$ solved by prior committed harnesses (admitted at score 1 for stance, executability, routing, and execution accuracy; $>0$ for clarification quality; $\ge 0.75$ for chart structure).
   - Draws a stratified sample $Q = \text{Cycle}(\mathcal{P}, \Gamma(\mathcal{P}))$ cycling evenly across all non-empty `(metric, scenario, complexity)` triples and requires bounded regressions: $\text{MC}(H') = \mathbf{1}[\text{Reg}_Q(H') \le \delta]$.
2. **Anchor Check (`AC` — Validation Floor & Champion Monotonicity, Theorem 3)**:
   - Requires the candidate's task success rate $V(H')$ on the 48-task validation anchor to stay within tolerance $\varepsilon$ of the best committed champion score $B$: $\text{AC}(H') = \mathbf{1}[V(H') \ge (1 - \varepsilon)B]$.
   - Candidates failing `MC` or `AC` return their failure verdict $v(H')$ to the analyzer for up to $\ell$ bounded remediation cycles before terminal rejection. The champion $H^\star$ and score $B_n$ update **only** when $V(H') > B_{n-1}$, guaranteeing $B_n \ge B_{n-1}$.
3. **Refine Rules (`RF` — Protected Progress on Acceptance, Theorem 1)**:
   - When $\text{Accept}(H') = \mathbf{1}[\text{MC}(H') = 1 \land \text{AC}(H') = 1] = 1$, $H'$ is deployed, its newly solved turn–metric records refresh $\mathcal{P}_{n+1} = \text{Refresh}_C(\mathcal{P}_n, \mathcal{A}(H_{n+1}))$, the rejection verdict set $\mathcal{R}$ is cleared, and the next round focuses on remaining unresolved failure clusters $\mathcal{I}_{n+1}$.
4. **Restart Rules (`RS` — Champion Restoration on Rejection, Theorem 2)**:
   - When $\text{Accept}(H') = 0$, the candidate is withdrawn, deployment rolls back directly to the champion $H_{n+1} = H_n^\star$, protected memory stays frozen ($\mathcal{P}_{n+1} = \mathcal{P}_n$), and the failure verdict $\mathcal{R}_{n+1} = \{v(H'_n)\}$ is passed to the next round so the proposer does not repeat the rejected edit.

---

## Key Empirical Findings

Evaluated on the 96-task held-out test split (15 unseen domains) after a single self-improvement round with `DeepSeek-V4.1-Flash`—and tested zero-shot on `GPT-6 Luna` without re-evolving the harness:

| Method / Variant | Backbone | Executability (%) | DB Routing (%) | Stance Acc (%) | Exec Acc (%) | Clarify (BLEU-4) | Chart Struct (%) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Direct Prompt | DeepSeek-V4.1-Flash | 81.32 | 57.59 | 62.25 | **31.91** | 4.32 | 52.23 |
| Static Harness ($H_0$) | DeepSeek-V4.1-Flash | 64.98 | 48.25 | 51.25 | 24.51 | 3.72 | 41.46 |
| ReAct | DeepSeek-V4.1-Flash | 79.38 | 57.59 | 64.25 | 27.24 | 3.93 | 49.57 |
| MultiVis-Agent | DeepSeek-V4.1-Flash | 58.75 | 56.81 | 56.25 | 26.85 | 0.60 | 44.08 |
| **RSIV-Harness (Full)** | **DeepSeek-V4.1-Flash** | **93.00** | **62.26** | **67.00** | 31.52 | **5.15** | **75.47** |
| RSIV-Harness w/o Stability Rules | DeepSeek-V4.1-Flash | 83.27 (-9.73) | 59.14 (-3.12) | 64.50 (-2.50) | 28.02 (-3.50) | 2.41 (-2.74) | 65.94 (-9.53) |
| Static Harness ($H_0$) | GPT-6 Luna | 51.75 | 30.35 | 54.00 | 26.07 | 2.02 | 42.01 |
| **RSIV-Harness (Zero-Shot Transfer)** | **GPT-6 Luna** | **61.09** (+9.34) | **49.42** (+19.07) | **61.50** (+7.50) | 25.29 (-0.78) | **3.74** (+1.72) | **50.36** (+8.35) |

- **Large gains over the static seed harness ($H_0$)**: On `DeepSeek-V4.1-Flash`, evolving the harness improved Executability by **+28.02 points** (64.98% $\to$ 93.00%), Database Routing by **+14.01 points** (48.25% $\to$ 62.26%), Stance Accuracy by **+15.75 points** (51.25% $\to$ 67.00%), Execution Accuracy by **+7.01 points** (24.51% $\to$ 31.52%), Clarification Quality by **+1.43 points** (3.72 $\to$ 5.15), and Chart Structure by **+34.01 points** (41.46% $\to$ 75.47%).
- **Removing the 4-layer stability gate degrades every metric**: Evolving without the stability rules (`- w/o. rule`) caused drops across all 6 metrics—including **-9.73 points** on Executability, **-9.53 points** on Chart Structure, and **-2.74 points** (more than 50%) on Clarification Quality.
- **Complementary 5-component evolution**: Single-component ablations from $H_0$ (`Exec.` 51.36%, `Chart` 41.46%) show that evolved **middleware** alone delivers the largest single jump (`Exec.` **90.66%**, `Stance` **66.50%**, `Exec Acc.` **30.35%**, `Chart` **72.41%**), while evolved **prompts** and **tools** drive Database Routing (**62.26%** each). Combining all 5 evolved components beats every single-component variant on 5 of 6 metrics.

---

## Why Not a Skill?

The evolutionary loop and four-layer gate in RSIV-Harness are an instantiation of reference-trajectory and acceptance-gated harness optimization specialized to SQL/visualization turns. Praxis already covers the general procedural methodology in [reference-trajectory-harness-evolution](../skills/reference-trajectory-harness-evolution/SKILL.md) and [belief-calibrated-scaffold-optimization](../skills/belief-calibrated-scaffold-optimization/SKILL.md). RSIV-Harness serves best as quantitative evidence in `rules/recursive-improvement.md`.

---

## Connections to Praxis

- **Recursive Improvement (`rules/recursive-improvement.md`)**: Provides a clean ablation showing that removing dual anchor-plus-regression-memory gating (`AC` + `MC`) and champion rollback (`RS`) costs up to 9.73 percentage points on held-out domains in a single evolutionary round.
- **Related Skills**: Directly complements [reference-trajectory-harness-evolution](../skills/reference-trajectory-harness-evolution/SKILL.md) and [procedural-family-skill-consolidation](../skills/procedural-family-skill-consolidation/SKILL.md).
