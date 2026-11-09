# Guardrail Erosion in Domain Fine-Tuned Large Language Models: A Paired Audit of Knowledge-Centric Abstention in Biomedical LLMs

> **Source**: [arXiv:2611.08780](https://arxiv.org/abs/2611.08780) — Stephen Peng, Vineet Jagadeesan Nair, Noah Broestl, Anne Friederike Kleppe, Steven Mills, Adi Zolotov (BCG X AI Science Institute & University of Cambridge, Nov 2026)
> **Praxis Source ID**: `src:2611-08780v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

This paper is an observational paired benchmark audit of **25 publicly released biomedical fine-tuned LLMs** against **11 ancestor base checkpoints** on `MedAbstain` and `ClinDet-Bench`. It does not propose a training algorithm or runtime scaffolding procedure; instead, its contribution is a four-dimensional paired evaluation protocol (*Capability*, *Caution/Abstention*, *Calibration*, and *Commitment*) and empirical evidence that domain adaptation erodes knowledge-centric abstention and worsens calibration. Its operational takeaways belong directly in our evaluation and safety rules (`agent-evaluation-quality.md`).

---

## Executive Summary

While prior fine-tuning safety audits focus on **value-centric refusal** (refusing malicious or harmful instructions), high-stakes domain deployments such as clinical decision support depend equally on **knowledge-centric abstention**: abstaining or requesting more information when decisive clinical evidence is absent, while answering when evidence is sufficient.

Peng et al. conduct a rigorous paired audit of **25 biomedical domain fine-tuned LLMs** descending from **11 base checkpoints** across four model families (`Llama 2`, `Llama 3`, `Llama 3.1`, and `Gemma-3`, spanning `4B` to `70B` parameters) and six post-training recipe families (`CPT`, `SFT`, `RL`, `DPO`, `PEFT`, and `MERGE`). Using question-level paired tests (McNemar, Fisher exact, paired item bootstrap) and cohort-level inference that accounts for shared base checkpoints (`Wilcoxon signed-rank` with Benjamini–Hochberg `BH` correction across 15 prespecified tests plus a two-stage hierarchical **base-clustered bootstrap** $p_{\mathrm{cluster}} < 0.05$), the audit reveals that domain fine-tuning systematically erodes appropriate abstention (`8.3% -> 4.2%` median on `MedAbstain`, falling in `21 of 25` pairs), pulls error-prone questions into answer coverage (`-14.98 pp` lower accuracy on newly answered items), and sharpens answer-token probability commitment even on shared errors (`+0.112`) while worsening calibration (`+0.040` `ECE10`).

---

## Paired Audit Methodology

1. **Benchmarks Evaluated**:
   - **`MedAbstain` (`MA`, MedQA-USMLE public split, `1,007` items per variant)**: Four paired variants crossing original vs evidence-ablated questions with the absence vs presence of an explicit abstention option: `No-Abstention` (`MA NA`), `Abstention` (`MA A`), `No-Abstention-Perturbed` (`MA NAP`), and `Abstention-Perturbed` (`MA AP`).
   - **`ClinDet-Bench` (`CD`, public commit `1a05c63`, `94` clinical scenarios)**: Deterministic clinical scoring rules across `32` `Complete`, `30` `Incomplete-Determinable` (`CD Det`), and `32` `Incomplete-Undeterminable` (`CD Undet`) cases where models answer `"Met"`, `"Not met"`, or `"Unable to determine"`.
2. **Four Audited Behavioral Dimensions ($\Delta m_v = m_{f,v} - m_{b,v}$, fine-tuned minus base)**:
   - **Capability**: Accuracy on answerable conditions (`MA NA`, `CD Complete`).
   - **Caution & Informedness**: Appropriate abstention rate $U_{\mathrm{AP}}$ (`MA AP`) and $U_{\mathrm{Undet}}$ (`CD Undet`) vs excessive abstention $U_{\mathrm{A}}$ (`MA A`) and $U_{\mathrm{Det}}$ (`CD Det`), summarized by **Youden's $J$ informedness**:
     $$J_r^{\mathrm{MA}} = U_{r,\mathrm{AP}} - U_{r,\mathrm{A}}, \qquad J_r^{\mathrm{CD}} = U_{r,\mathrm{Undet}} - U_{r,\mathrm{Det}}$$
   - **Coverage-Transition Partitioning**: Partitioning `MA A` into *always answered*, *newly answered* (base abstained, fine-tuned answered), *newly abstained* (base answered, fine-tuned abstained), and *both abstained*.
   - **Calibration & Commitment**: Evaluated on choice-normalized first-answer-token probabilities (top-20 token capture, verified via full-vocabulary rescoring on 10 pairs) using 10-bin Expected Calibration Error (`ECE10`), normalized entropy, maximum-choice probability, confidence on **shared errors** (items both base and fine-tuned models answer incorrectly), and confidence `AUROC`.

---

## Exact Quantitative Findings (`H1–H5`)

| Hypothesis | Benchmark & Metric | Base vs Fine-Tuned / Median Pair Change ($\Delta$) | Statistical Robustness ($p$, $q_{\mathrm{BH}}$, $p_{\mathrm{cluster}}$) | Key Finding |
|:---|:---|:---|:---|:---|
| **H1: Knowledge-Centric Caution Erodes** | `MA AP` appropriate abstention ($U_{\mathrm{AP}}$) | Base median **`8.3%`** $\to$ Fine-tuned **`4.2%`**<br>Median $\Delta = \mathbf{-3.48\text{ pp}}$ (`-45.0%` relative; 95% CI `[-5.66, -0.79] pp`) | $p = 0.0038$<br>$q_{\mathrm{BH}} = 0.009$<br>$p_{\mathrm{cluster}} = 0.003$ (**Robust**) | Decreased in **`21 of 25` pairs** (increased in 4); reproduced under native chat templates on 9 Instruct pairs ($\Delta = -2.88\text{ pp}$ vs $-1.89\text{ pp}$ completion) and parse-failure exclusion ($\Delta = -3.48\text{ pp}$). |
| **H1 (Corroboration)** | `CD Incomplete-Undeterminable` `"Unable"` rate ($U_{\mathrm{Undet}}$) | Median $\Delta = \mathbf{-6.25\text{ pp}}$ | $p = 0.061, q_{\mathrm{BH}} = 0.083$<br>$p_{\mathrm{cluster}} = 0.182$ (*Directional*) | Directionally consistent erosion on deterministic clinical rules, but underpowered at $n = 32$ scenarios. |
| **H2: Reduced Caution Is Not Explained by Informedness** | `MA` Informedness ($\Delta J^{\mathrm{MA}}$) & `CD` Informedness ($\Delta J^{\mathrm{CD}}$) | `MA`: Median $\Delta J^{\mathrm{MA}} = \mathbf{-0.60\text{ pp}}$<br>`CD`: Median $\Delta J^{\mathrm{CD}} = \mathbf{-2.71\text{ pp}}$ | `MA`: $p = 0.034, q_{\mathrm{BH}} = 0.052, p_{\mathrm{cluster}} = 0.100$<br>`CD`: $p = 0.158, p_{\mathrm{cluster}} = 0.195$ | Fine-tuning does **not** improve discrimination between answerable and unanswerable questions; caution drops indiscriminately. |
| **H3: Newly Answered Questions Are Error-Prone** | `MA A` accuracy on *newly answered* vs *always answered* items | Median **`-14.98 pp` lower accuracy** (`-24.8%` relative deficit; 95% CI `[-17.91, -8.36] pp`) | $p < 0.0001$<br>$q_{\mathrm{BH}} = 0.00009$<br>$p_{\mathrm{cluster}} < 0.001$ (**Largest robust effect**) | Models lose caution near their competence boundary, converting appropriate base-model abstentions into low-accuracy guesses. (Base accuracy on *newly abstained* items was `-11.47 pp` lower than always-answered, $p = 0.014, q_{\mathrm{BH}} = 0.023, p_{\mathrm{cluster}} = 0.051$). |
| **H4: Commitment Rises & Calibration Worsens** | `MA NA` Choice Commitment & `ECE10` Calibration | Norm. entropy: **`-0.191`**<br>Max-choice prob: **`+0.127`**<br>Shared-wrong conf: **`+0.112`**<br>`ECE10`: **`+0.040`** (`+0.0399` at 10 bins, `+0.0378` at 15, `+0.0345` at 20) | Entropy: $q_{\mathrm{BH}} < 0.001, p_{\mathrm{cluster}} = 0.001$<br>Max prob: $q_{\mathrm{BH}} < 0.001, p_{\mathrm{cluster}} = 0.002$<br>Shared-wrong: $q_{\mathrm{BH}} < 0.001, p_{\mathrm{cluster}} = 0.001$<br>`ECE10`: $q_{\mathrm{BH}} = 0.009, p_{\mathrm{cluster}} = 0.040$ (**All Robust**) | Fine-tuned models become significantly more confident **even on questions both base and adapted models answer wrong**, while confidence `AUROC` for error discrimination does not reliably improve. On `CD Complete`, mean confidence rose `+0.185` ($q_{\mathrm{BH}} = 0.018, p_{\mathrm{cluster}} = 0.035$). |
| **H5: Capability and Caution Move Heterogeneously** | Capability ($\Delta\text{Acc}$) vs Caution ($\Delta U$) coupling & Cochran's $Q$ ($I^2$) | `MA`: $r_{\mathrm{P}} = -0.249$ ($p = 0.210, q_{\mathrm{BH}} = 0.225$)<br>`CD`: $r_{\mathrm{P}} = -0.538$ ($p = 0.008, q_{\mathrm{BH}} = 0.028$)<br>Heterogeneity: **$I^2 = 96.3\%$ (`MA`)**, **$93.4\%$ (`CD`)** | Non-significant correlation on `MA`; extreme between-pair heterogeneity on both | On `MA`, **`16/25` pairs** increased capability while decreasing caution, **`1/25`** improved both, **`3/25`** decreased capability while increasing caution, and **`5/25`** degraded on both. No moderator (recipe family, size, base alignment) survived correction. |

---

## Relevance to Praxis

1. **Never evaluate domain fine-tuned models on answerable-only accuracy or without their matched base checkpoint**: Reporting single-model accuracy on `MedQA` hides the fact that `16 of 25` adapted models traded away epistemic caution (`-3.48 pp` median abstention, `-45.0%` relative) and `5 of 25` regressed on both capability and caution.
2. **Audit the coverage-transition partition (`newly answered` items)**: When an adapted model answers questions its base model abstained on, measure accuracy specifically on that `newly answered` slice (`-14.98 pp` deficit) rather than letting always-answered items mask boundary errors.
3. **Track confidence on shared errors (`shared-wrong confidence`)**: Rising average confidence after SFT/DPO/RL (`+0.127` on `MA NA`, `+0.185` on `CD Complete`) does not mean better uncertainty calibration—restricting to items both base and fine-tuned checkpoints get wrong shows confidence still jumps by `+0.112` (`MA NA`) and `+0.225` (`CD Complete`, 23 pairs), inflating `ECE10` (`+0.040`).
4. **Cross-References**:
   - [`../rules/agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md) — Paired multi-dimensional evaluation of domain-adapted models
   - [`../rules/recursive-improvement.md`](../rules/recursive-improvement.md) — "DON'T: Accept modifications based on aggregate metrics alone"
   - [`../skills/rag-evidence-triage/SKILL.md`](../skills/rag-evidence-triage/SKILL.md) — Evidence sufficiency triage before answering under incomplete context
