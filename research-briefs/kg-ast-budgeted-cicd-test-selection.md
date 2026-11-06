# KG-AST for Cheaper CI/CD: Budgeted Test Selection and AI Bug Review

> **Paper**: Yeung, H. (2026). *KG-AST for Cheaper CI/CD: Budgeted Test Selection and AI Bug Review*. arXiv:2611.06950.
> **Praxis source**: `src:2611-06950v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Summary

Running full test suites and LLM-based code reviews on every commit is prohibitively expensive in large repositories. Yeung evaluates **KG-AST**, a lightweight static analysis and commit-ranking toolkit that combines git diff features, abstract syntax tree (AST) structure, and static call graphs to optimize three CI/CD tasks without requiring a project-specific build environment or historical defect labels:

1. **Budgeted Commit Risk Ranking**: A zero-configuration LightGBM classifier trained on **46 standard git/diff/AST/history features** from other repositories ranks incoming commits by defect risk. At a **20% CI testing budget** across **20 Java projects** (`3,000` recent commits each, evaluated leave-one-project-out on a chronological `60%` train / `30%` test split with the last `10%` dropped to prevent SZZ `git blame -w -M` censoring), KG-AST captures **64.6%** of bug-introducing commits vs. **49.5%** for biggest-change-first (`+15.1` percentage points, $95\%$ CI `[+11.6, +18.4]`, winning on `19/20` projects) and **19.6%** for random selection. Across **155 projects in 11 programming languages** (`2,500` commits each), a single cross-project model beats biggest-change-first in **all 11 languages** by **+3.8 to +13.2 percentage points**—and performs identically even when the target programming language is held out entirely during training (`64.2%` vs. `63.7%` in Java).
2. **Call-Graph-Augmented AI Bug Review**: Supplying an LLM reviewer (`~$0.04` per commit review across `98` later-fixed bug commits and `42` clean commits in `15` Java projects) with static call-graph context (signatures and snippets of direct callers and callees of modified methods) raises exact defect localization from **26%** (`95%` CI `[0.17, 0.35]`, diff-only) to **32%** (`[0.22, 0.41]`, gain `+0.061 [+0.010, +0.122]`). All of the improvement concentrates on **local fixes** (`n = 42`, where the later fix modifies the same methods as the buggy commit), jumping from **29%** to **43%** (`+0.143 [+0.048, +0.262]`), whereas **non-local fixes** (`n = 56`, where the fix modifies untouched callers/callees) remain flat at **23%**.
3. **Build-Free Static Test Selection**: Combining a **depth-2 backward call-graph walk** from modified methods with `FooTest`/`Foo` naming-convention matching across **67 fix commits in 7 Java projects** (median test suite size: `1,250` test methods) selects a median of just **2.3%** (mean **8.0%**) of the test suite while hitting a test written or updated for the fix in **85.1%** of commits (covering **80.3%** of all changed tests).

The paper also provides an unusually rigorous set of **documented negative results**, showing that Poincaré hyperbolic graph embeddings, historical defect-proneness features, per-project fine-tuning, static AST bug classifiers, and unguided LLM "bug-prone method" ranking provide **zero measurable gain** over simple structural baselines.

## Quantitative Results

### 1. Commit Risk Ranking Across Budgets (20 Java Projects, 3,000 Commits Each)

| CI Commit Budget (% of Commits Tested) | Random Selection | Biggest-Change-First (Lines Changed) | KG-AST (Cross-Project LightGBM) | Gain vs. Biggest-Change | Perfect Oracle Upper Bound |
|:---------------------------------------|:-----------------|:-------------------------------------|:--------------------------------|:------------------------|:---------------------------|
| **5% budget** | `4.9%` | `20.3%` | **`30.8%`** | `+10.5` pp | `67.2%` |
| **10% budget** | `9.8%` | `32.9%` | **`45.5%`** | `+12.6` pp | `89.6%` |
| **20% budget** | `19.6%` | `49.5%` | **`64.6%`** | `+15.1` pp (`[+11.6, +18.4]`) | `99.3%` |
| **30% budget** | `29.7%` | `61.3%` | **`76.9%`** | `+15.6` pp | `100.0%` |
| **50% budget** | `49.8%` | `77.7%` | **`90.9%`** | `+13.2` pp | `100.0%` |

### 2. Cross-Language Generalization at 20% Budget (155 Projects, 11 Languages)

| Language | Projects | ROC AUC | Trained on Other 154 Projects | Language Held Out Completely | Biggest-Change-First | Gain vs. Biggest `[95% CI]` | Projects Won |
|:---------|:---------|:--------|:------------------------------|:-----------------------------|:---------------------|:----------------------------|:-------------|
| **Java** | `29` | `0.843` | `63.7%` | `64.2%` | `50.5%` | `+13.2` pp `[+9.4, +17.2]` | `28 / 29` |
| **Rust** | `14` | `0.836` | `58.6%` | `58.7%` | `54.9%` | `+3.8` pp `[+0.1, +7.9]` | `10 / 14` |
| **Python** | `14` | `0.815` | `58.0%` | `57.9%` | `48.7%` | `+9.3` pp `[+5.2, +13.9]` | `12 / 14` |
| **PHP** | `12` | `0.823` | `57.8%` | `58.3%` | `47.8%` | `+10.0` pp `[+3.3, +18.7]` | `10 / 12` |
| **C/C++** | `11` | `0.798` | `56.5%` | `56.1%` | `49.9%` | `+6.6` pp `[+3.5, +9.6]` | `9 / 11` |
| **Ruby** | `12` | `0.797` | `54.8%` | `55.0%` | `45.0%` | `+9.9` pp `[+4.2, +15.7]` | `9 / 12` |
| **C#** | `10` | `0.802` | `54.1%` | `53.5%` | `45.2%` | `+8.8` pp `[+5.7, +12.1]` | `10 / 10` |
| **Go** | `12` | `0.802` | `52.2%` | `52.4%` | `43.3%` | `+8.9` pp `[+6.1, +12.2]` | `12 / 12` |
| **JavaScript** | `19` | `0.794` | `50.7%` | `49.7%` | `40.2%` | `+10.6` pp `[+6.6, +14.6]` | `17 / 19` |
| **Kotlin** | `10` | `0.793` | `50.3%` | `50.3%` | `44.2%` | `+6.2` pp `[+2.4, +9.9]` | `7 / 10` |
| **TypeScript** | `12` | `0.798` | `49.2%` | `48.8%` | `40.1%` | `+9.1` pp `[+5.0, +14.3]` | `12 / 12` |

### 3. Feature Importance, Size-Stratified Discrimination, and Learning Curve (`~71,000` Java Commits)

- **Top predictive features (by split gain)**: Number of added `if` statements (`22%` of total gain), lines added (`15%`), share of test lines in the commit (`11%` — commits bundling test updates with production code are significantly safer), touched file age (`8%`), and comment ratio (`8%`).
- **Discrimination within equal-sized commits**: When commits are grouped into 8 size bins, raw commit size has a size-stratified AUC of only `0.590` (overall AUC `0.767`, `52.4%` coverage at `20%` budget). Adding diff structure raises size-stratified AUC to `0.665` (`56.7%` cov), content features (added `if`s, test share, comments) to `0.752` (`62.0%` cov), and author/file history to **`0.770`** (overall AUC `0.849`, **`63.6%`** cov).
- **Rapid cross-project saturation**: Training on just `2` projects achieves `56.2%` coverage at a `20%` budget; `8` projects reach `60.8%`; **`12` projects reach `61.2%`**, nearly matching the `29`-project model (`62.1%`).

### 4. AI Bug Review with Call-Graph Context (`98` Bug Commits, `42` Clean Commits)

| Context Slice Provided to LLM Reviewer | Overall Exact Bug Find Rate (`n = 98`) | Local Fixes (`n = 42`, Same Method Fixed) | Non-Local Fixes (`n = 56`, Other Method Fixed) | Gain vs. Diff Only (Overall / Local) |
|:---------------------------------------|:---------------------------------------|:------------------------------------------|:-----------------------------------------------|:-------------------------------------|
| **Diff only** | `26%` `[0.17, 0.35]` | `29%` `[0.17, 0.43]` | `23%` `[0.12, 0.34]` | — |
| **`+` Static call-graph context** | **`32%`** `[0.22, 0.41]` | **`43%`** `[0.29, 0.57]` | `23%` `[0.12, 0.34]` | `+0.061 [+0.010, +0.122]` / **`+0.143 [+0.048, +0.262]`** |
| **`+` Git co-change history** | `31%` `[0.21, 0.40]` | `40%` `[0.26, 0.55]` | `23%` `[0.12, 0.34]` | `+0.051 [-0.010, +0.112]` / `+0.119 [+0.000, +0.238]` |
| **`+` Poincaré hyperbolic distance** | `30%` `[0.20, 0.39]` | `31%` `[0.17, 0.45]` | `29%` `[0.18, 0.41]` | `+0.041 [-0.020, +0.102]` (`-0.119` vs. plain graph on local) |

- **Confidence calibration and false-alarm audit**: Across all four context slices, `65%` of historical bugs are missed. However, filtering LLM review findings to confidence $\ge 0.7$ yields only **0.02 false alarms per clean commit** (`~9%` recall). When two independent AI judges audited `36` findings that did not match the historical fix commit (`34/36` inter-judge agreement), **58%** (`7/12`) of $\ge 0.7$ confidence findings and **50%** (`12/24`) of `0.5–0.7` findings were verified as genuine latent bugs with concrete triggering inputs—raising estimated true precision from `60%` to **`~83%`** at $\ge 0.7$ confidence (and from `44%` to **`73%`** at $\ge 0.5$).

### 5. Build-Free Static Test Selection (`67` Fix Commits Across `7` Java Projects)

| Selection Strategy | Commits Where Selected Set Hits Fix Test | Share of Changed Tests Covered | Mean Suite Fraction Run | Median Suite Fraction Run |
|:-------------------|:-----------------------------------------|:-------------------------------|:------------------------|:--------------------------|
| **Call-graph depth 1** (direct test callers) | `46.3%` | `40.7%` | `1.7%` | `0.2%` |
| **Call-graph depth 2** (2-hop callers) | `61.2%` | `54.0%` | `6.5%` | `0.9%` |
| **Naming convention only (`FooTest` / `Foo`)** | `56.7%` | `48.2%` | `2.0%` | `0.6%` |
| **Combined (Call-graph depth 2 + Naming)** | **`85.1%`** | **`80.3%`** | **`8.0%`** | **`2.3%`** (`23.2%` random baseline) |

## Documented Negative Results (What Did Not Work)

A major contribution of the paper is reporting five intuitive techniques that failed controlled evaluation:
1. **Defect-history features and per-project fine-tuning for commit risk**: Adding 13 historical bug-proneness features (`62.3%` vs. `62.7%` baseline across 30 Java projects), project-relative size normalization (`61.9%`), training on the target project's own past commits (`62.9%`), or hyperparameter tuning (`61.4%–62.9%`) yielded **zero gain** over the 46-feature cross-project model.
2. **Poincaré hyperbolic embeddings**: Embedding the AST/call graph into hyperbolic space did not improve commit risk ranking (`10` Java projects, `5,139` test commits: baseline AUC `0.856` vs. `+Poincaré 0.849` and `+Euclid 0.849`), method-level bug prediction (`1,799` length-matched pairs in Telegram Android: AST AUC `0.683` vs. `+Poincaré 0.685`), or AI bug review (`30%` vs. `32%` plain call graph).
3. **Cross-project static AST bug detectors**: Training logistic regression or GBM classifiers on static AST features of `245` issue-linked bug fixes across `7` Java projects yielded near-random length-matched AUC (`0.518` logistic, `0.551` GBM).
4. **Unguided LLM "bug-prone method" selection**: Asking Claude to pick the 10 most defect-prone methods from 100-method pools across `64` post-cutoff commits achieved `hit@10 = 9.4%`, losing to a trivial "pick the 10 longest methods" heuristic (`12.5%`).
5. **Graph dependent count for security severity ranking**: Ranking `126` security fixes among `6,187` bug fixes in `16` Java projects by call-graph dependent count achieved `AUC = 0.55`, losing to raw change size (`AUC = 0.65`).

## Why Not a Skill?

The techniques evaluated in this paper are **CI/CD pipeline heuristics and ML feature-engineering benchmarks** (a cross-project LightGBM commit scorer and static regex/tree-sitter call-graph slicing for CI runners) rather than a cognitive or multi-step reasoning workflow executed by an autonomous agent during task solving. Its high-leverage quantitative findings—such as the `20%` commit budget threshold, the `2.3%` median test-suite slice via depth-2 call graphs + naming conventions, the `+14.3` pp boost on local AI code reviews from direct caller/callee context, and the documented failure of hyperbolic embeddings and unguided LLM method ranking—are distilled as engineering decision rules in [agent-evaluation-quality.md](../rules/agent-evaluation-quality.md).
