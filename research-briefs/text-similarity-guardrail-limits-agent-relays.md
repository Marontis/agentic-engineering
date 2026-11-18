# Safe Resemblance, Silent Propagation: Limits of Text-Similarity Guardrails for AI Agent Safety

> **Source**: [arXiv:2611.21520](https://arxiv.org/abs/2611.21520) — Charles Xiao (November 2026)
> **Praxis Source ID**: `src:2611-21520v1`
> **Status**: Research Brief — defensive guardrail & evaluation-methodology lessons only (per [`AGENTS.md`](../AGENTS.md) lines 69–70, relay-prompt templates are omitted).
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

This paper is a negative empirical audit and formal impossibility/validity analysis of surface text-similarity guardrails (`DonkeyRail`, the public `BLEU` + `ROUGE-L` + `METEOR` classifier from the `Morris-II` / `Virtual Donkey` line, pinned at commit `6ab9116c2b08f3309a034ceac7f35a78416f05a7`) rather than a new constructive defense procedure. Per [`AGENTS.md`](../AGENTS.md) lines 69–70, we omit multi-hop relay prompt text and capture strictly the **defensive architecture and benchmark-validity lessons**, while pointing engineers to our constructive provenance and information-flow skills ([`principal-context-permission-intersection`](../skills/principal-context-permission-intersection/SKILL.md), [`task-graph-contextual-integrity-gating`](../skills/task-graph-contextual-integrity-gating/SKILL.md), [`mcp-decode-provenance-binding`](../skills/mcp-decode-provenance-binding/SKILL.md), and [`covert-tool-injection-defense`](../skills/covert-tool-injection-defense/SKILL.md)).

---

## Experimental Setup: Separating Surface Overlap, Behavioral Propagation, and Permission

Xiao evaluates `DonkeyRail`'s frozen 3-feature logistic regression model—scoring $x(D, o) = (\max_{d \in D} \mathrm{BLEU}(d, o), \max_{d \in D} \mathrm{ROUGE\text{-}L}(d, o), \max_{d \in D} \mathrm{METEOR}(d, o))$ over `10` retrieved records ($b = -7.572981$, $w = (8.425531, -3.162807, 18.382018)$, reconstructed within $4.50 \times 10^{-15}$ on the `2,995`-row stored test split)—inside a stateless **3-agent email relay** (`Agent 1 -> Agent 2 -> Agent 3`) across **`gpt-6-luna`** (reasoning `none`, `768`-token cap) and **`gpt-6.1-sol`** (reasoning `low`, `1,536`-token cap; `temperature = 1.0, top_p = 0.98`):

1. **Detector-Independent Behavioral Endpoint ($F(o_1) = \mathbf{1}[A_2 = 1 \land A_3 = 1]$)**: Each agent receives `9` benign distractors, `1` relay record (the preceding agent's actual output $o_h$, never re-inserting the root seed), and a trusted meeting-acknowledgment request carrying a **fresh unique ticket integer** (`216` unique tickets across **`72` held-out attack chains** = `12` framings $\times$ `6` variants: *identity, paraphrase, format change, clause reordering, indirect quotation, Base64*). An output $o_1$ is **functional** only if **both** `Agent 2` and `Agent 3` independently compute and emit `ticket + 7` outside explicit relay tags, code fences, and quote-prefixed lines—ruling out static copy-paste and requiring zero survival of any fixed marker phrase.
2. **Template-Disjoint Authorized Controls (`192` Calibration + `192` Test Replies / Model)**: Four authorized task types (`48` each of *ordinary acknowledgment*, *verbatim quotation*, *paraphrase*, and *full template reuse*) over `24` calibration request templates and `24` non-overlapping test request templates/formats. Calibration sets $\tau_{\mathrm{cal}} = \operatorname{nextafter}(s_{(4)}, +\infty)$ on benign calibration scores alone (targeting $< 2\%$ empirical calibration FPR, yielding `0 / 192` calibration alerts on both models).

---

## Key Empirical & Theoretical Findings

### 1. Bidirectional Failure: Missed Functional Relays Coexist with `100%` False Blocking of Completed Reuse

| Evaluation Cohort & Model | Threshold $\tau$ | Functional Roots (`F(o_1)=1`) | Detected (`TP`) / Missed (`FN`) | Functional Recall (`95% CI`) | Legitimate Test `FP` (`95% CI`) | False Alerts by Authorized Task (`Ordinary` / `Paraphrase` / `Quotation` / `Template`) |
|:--------------------------|:-----------------|:-----------------------------:|:-------------------------------:|:----------------------------:|:-------------------------------:|:--------------------------------------------------------------------------------------|
| **Primary: `gpt-6-luna`** | `0.5` *(default)* | `19 / 72` (`26.39%`; `18` $A_1 A_2 A_3$) | `11` / **`8`** | **`57.89%`** (`[35.0%, 76.9%]`) | **`70 / 192` (`36.46%`)** (`[21.9%, 51.6%]`) | `0/48` / `2/48` / **`37/48`** / **`31/48`** *(flags **`30/30` [`100%`]** completed quote/template tasks; overall utility `122 -> 90`)* |
| **Primary: `gpt-6-luna`** | `Calibrated` ($\tau_{\mathrm{cal}}$) | `19 / 72` | **`1` / `18`** | **`5.26%`** | **`15 / 192` (`7.81%`)** | Calibration (`0/192`) fails to transfer across unseen templates while wiping out `10/11` detections |
| **Primary: `gpt-6.1-sol`** | `0.5` *(default)* | `0 / 72` (`0/216` fresh actions) | `0` / `0` | `N/A` *(undefined)* | **`98 / 192` (`51.04%`)** | `0/48` / `2/48` / **`48/48`** / **`48/48`** *(flags **`93/93` [`100%`]** completed quote/template tasks; overall utility `188 -> 93`)* |
| **Primary: `gpt-6.1-sol`** | `Calibrated` ($\tau_{\mathrm{cal}}$) | `0 / 72` | `0` / `0` | `N/A` *(undefined)* | **`69 / 192` (`35.94%`)** | `0/192` calibration alerts jumps to `35.94%` false positives on unseen benign templates |
| **Earlier (Shared Templates): `Luna`** | `0.5` $\to$ `0.999981` | `13 / 72` (`18.06%`, `[12.5%, 23.6%]`) | `7 / 6` $\to$ **`0 / 13`** | `53.85%` $\to$ **`0.00%`** | **`128 / 192`** $\to$ `0 / 192` | At `0.5`: `0/64` ack, **`64/64` quote**, **`64/64` template** (same for `Sol`); calibration loses **all `13/13`** positives |

- **Low-Overlap Functional Descendants**: A `gpt-6-luna` format-change root receiving classifier probability **`0.012957`** (`METEOR = 0.213993`) still drove fresh downstream calculations (`812170 -> 812177` and `812207 -> 812214`), as did an encoded `s07` chain scoring **`0.006965`** (`METEOR = 0.1577`; `Table 7`). In `21` declared-rule metric probes (`Table 6`), deleting the required action kept `METEOR = 0.9364` / `ROUGE-L = 0.9286`, whereas Base64 wrapping or `XML depth 4` retained protocol function at `0.0000` `BLEU` and `0.0000` `METEOR`.
- **Near-Chance Safety Discrimination (`Table 3`)**: Although `DonkeyRail` achieved **`0.997884` historical proxy `AUC`** on `2,995` stored test rows whose labels matched a fixed roleplay phrase (`1,434/1,434` `Hillary virus`, `1,286/1,286` `Phishing`, `1,408/1,408` `Walmart spam`, vs. `86/1,579` [`0.527` phrase AUC] on `Jailbreaks`), **`0 / 144` `Luna` relay roots** (`32` functional observations across `25` unique variants) contained that phrase. While root-only `AUC` was `0.7609` (`0.7901` earlier, `0.7160` primary), **pooled functional-vs-benign `AUC` collapsed to `0.5272` (`0.527181`: `0.4083` earlier, `0.6436` primary)**—barely above `0.50` random guessing.

### 2. Measurement Bug Across `21 / 21` Published Configurations: ROC Interpolation vs. Direct Thresholding (`Section 5.1`)

`DonkeyRail`'s evaluation code computed fixed-threshold operating points by **linearly interpolating between adjacent ROC curve probability thresholds** when $\tau$ was absent from empirical scores, rather than evaluating the step-function decision rule $\widehat{\mathrm{FPR}}(\tau) = \sum \mathbf{1}[y_i = 0 \land s_i \ge \tau] / \sum \mathbf{1}[y_i = 0]$. Re-evaluating all `21` published classifier configurations (`3` model families $\times$ `7` metric subsets) directly at $s_i \ge \tau$ **changed `FPR` in `19 / 21` configurations and changed `FPR` or `TPR` in `21 / 21`**—most dramatically on the `BLEU` decision stump at $\tau = 0.5$, where ROC interpolation reported `FPR = 0.500036` while exact counting gave **`23 / 1,500 = 0.015333`** (`TPR = 1,491 / 1,495 = 0.997324`; 3-feature logistic reported `0.021580` vs. exact `29 / 1,500 = 0.019333`).

### 3. Two Formal Impossibility Bounds (`Propositions 1 & 2`)

- **Criterion Contamination & `AUC` Non-Transferability (`Definition 1`, `Proposition 1`, `Corollary 1`)**: When a guardrail $f = h \circ \phi$ is evaluated against a surface proxy criterion $C$ positively correlated with $\phi$ ($\operatorname{Corr}_P(\phi, C) > 0$) that disagrees with target behavior $B$ ($P(C \neq B) > 0$), **even $\operatorname{AUC}_P(f, C) = 1$ implies zero universal positive lower bound on $\operatorname{AUC}_P(f, B)$**—constructing a family $B_a$ on a single fixed $(P, f, C, \phi)$ achieving *every* behavioral $\operatorname{AUC}_P(f, B_a) = a \in [0, 1]$ (including $a = 0$). Transfer requires bounding conditional score total variation $|\operatorname{AUC}_P(f, B) - \operatorname{AUC}_P(f, C)| \le \min\{1, \varepsilon_+ + \varepsilon_-\}$ (`Eq. 7`), and estimating the normalized gap $\operatorname{CCI}_P(f; C, B) = 1 - \operatorname{AUC}_P(f, B)/\operatorname{AUC}_P(f, C)$ (`Eq. 8`) requires **jointly paired `(C, B)` labels on the same cohort**.
- **Authorization Non-Identifiability (`Proposition 2`)**: When two worlds $w_0, w_1$ share identical guardrail-visible transcripts $O(w_0) = O(w_1) = (t, D, o)$ while an omitted external policy flips authorization $\mathcal{A}(w_0) \neq \mathcal{A}(w_1)$, **no deterministic function of $O$ succeeds in both worlds**, and any randomized observation-only classifier has expected accuracy **`1 / 2`** on a balanced pair (`64 / 128` on `64` byte-identical contact-summary pairs vs. **`128 / 128`** when the trusted policy is supplied as an explicit input).

---

## Defensive Takeaways & Scope Boundary with RAG Extraction Caps

1. **Replace Surface-Overlap Relay Guardrails with Provenance & Policy-Grounded Gates**: In multi-agent workflows where quoting, summarizing, or filling templates from retrieved records is part of legitimate work, use explicit authority/information-flow tracking (`Fides`, `CaMeL`, [`principal-context-permission-intersection`](../skills/principal-context-permission-intersection/SKILL.md), [`task-graph-contextual-integrity-gating`](../skills/task-graph-contextual-integrity-gating/SKILL.md)) that receives the trusted policy and principal permissions alongside $(t, D, o)$. Reserve output-to-chunk `ROUGE-L` / `LCS` overlap caps strictly for **synthesis-only RAG endpoints** ([`snaprag-rag-extraction-defensive-lessons.md`](snaprag-rag-extraction-defensive-lessons.md), `arXiv:2611.12241`) where raw passage reproduction is forbidden by policy.
2. **Audit Guardrail Benchmarks for Direct `s >= tau` Counting, `>= 2`-Hop Fresh Behavioral Endpoints, and Disjoint High-Copy Controls**: Always compute `FPR`/`TPR` by direct indicator counting (never `scipy`/`sklearn` ROC threshold interpolation), verify propagation via fresh input-dependent actions in at least two downstream agents, and report benign false-positive rates stratified across template-disjoint verbatim-quotation and template-reuse tasks.

## Related Artifacts

- [`snaprag-rag-extraction-defensive-lessons.md`](snaprag-rag-extraction-defensive-lessons.md) — Contrasting regime where `ROUGE-L` output-to-chunk overlap caps validly enforce synthesis-only proprietary RAG KB protection (`arXiv:2611.12241`)
- [`principal-context-permission-intersection`](../skills/principal-context-permission-intersection/SKILL.md) — System-level Principal Contexts (`Conflux`, `arXiv:2611.08768`) resolving transcript non-identifiability via explicit provenance
- [`task-graph-contextual-integrity-gating`](../skills/task-graph-contextual-integrity-gating/SKILL.md) — Task-graph contextual integrity gating before multi-agent propagation (`arXiv:2610.39532`)
- [`rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md) — `"DON'T: Gate inter-agent relays on lexical overlap (BLEU/ROUGE-L/METEOR) or compute detector operating points via ROC interpolation"`
- [`rules/agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md) — Guardrail operating-point and criterion-contamination evaluation standards
