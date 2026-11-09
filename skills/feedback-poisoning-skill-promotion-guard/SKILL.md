---
name: feedback-poisoning-skill-promotion-guard
description: >
  Audit and gate text-space skill optimization loops (SkillOpt: Analyst
  reflection -> edit merging/ranking -> candidate construction -> validation
  gate -> slow-update retention) against reference-feedback poisoning. Covers
  8-stage promotion tracing, literal-abstraction enforcement, trigger-conditioned
  rule filtering, leave-one-edit-out carrier decoupling, and isolated endpoint
  verification. Derived from "When Feedback Becomes a Backdoor: Tracing
  Backdoor Skill Formation in Text-Space Skill Optimization" (arXiv:2611.09348).
license: CC-BY-4.0
repository: https://github.com/Marontis/agentic-engineering
---

# Feedback-Poisoning Skill Promotion Guard

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

Use this skill when building, auditing, or hardening text-space skill optimization loops (such as `SkillOpt`, `ExpeL`, or reflection-driven prompt/skill evolution pipelines) that score agent executions against contributed or externally maintained reference answers, benchmarks, or evaluation suites.

## When to Use

- Your self-evolving agent reflects on task failures scored against external or community-contributed reference answers (`training references` or `validation references`) to propose persistent natural-language skill edits.
- Your optimizer bundles multiple reflection edits into a single candidate skill and promotes the candidate atomically when its aggregate validation score improves.
- Your skill artifact includes protected slow-update or meta-skill blocks that shield consolidated rules from subsequent step-level revision.
- You need a stage-resolved diagnostic audit to determine whether poisoned supervision is stopped at formation, edit ranking, candidate validation, or endpoint activation.

## Core Insight

Reference answers are an attacker-accessible supervision channel in text-space skill optimization (`reference-feedback poisoning`, arXiv:2611.09348). Without touching the target model, optimizer code, prompts, scoring logic, or skill file, an adversary who poisons a subset of training tasks and their reference answers changes which executions fail and therefore what the `Analyst` reflects on; poisoning validation references changes which candidate wins selection.

Crucially, **standard clean-validation accuracy gates fail to stop dormant trigger-conditioned backdoors**:
1. **Zero clean-utility penalty at endpoint**: In `SearchQA` (`400` training questions with `30%` poisoned references mapping `[ZEPHYR-17] -> ZEPHYR VERIFIED`, `100` clean validation items, `200` clean test items, 4 epochs of 10 steps with `GPT-5.6 Luna`), the natural attack completed the entire promotion chain in **all 3 seeds (`42`, `43`, `44`)**. Every final skill emitted the payload on **`200/200` triggered held-out questions** and **`0/200` clean questions**, while maintaining clean test accuracy nearly identical to benign `SkillOpt` (**`169/200` vs `171/200`** in-run evaluator on seed 42; **`174/200`** vs **`156/200`** initial skill under the frozen harness). Deleting the retained rule block dropped triggered activation from `200/200` to `0/200` without changing clean accuracy (`174/200`).
2. **External carrier effect across clean validation gates**: Because `SkillOpt` accepts or rejects a candidate skill atomically, a validation-neutral backdoor edit $B_0$ rides into the best skill on the validation gains of an unrelated clean QA edit $C$ bundled in the same step. On a frozen 40-item positive-control validation set (`threshold = 0.175`), parent $P$ and $P + B_0$ both scored **`0.1700` (`3/10` gate passes)**, whereas bundling $B_0$ with clean edit $C$ ($P + B_0 + C$) raised the score to **`0.3775` (`10/10` gate passes)** vs **`0.3725` (`10/10`)** for $P + C$—an external carrier lift of `+0.2075` (~8.3 items) vs a negligible `0.0050` difference from $B_0$ itself (and `0.1875 -> 0.2325`, `5/10 -> 9/10` pass rate with evolution-generated clean edits).
3. **Two structural bottlenecks before the validation gate (`SpreadsheetBench`)**: In `SpreadsheetBench` (`80` training tasks with `25%` poisoned workbooks prepending `[ARCHIVE-CHECK: COBALT-17]` and writing `COBALT VERIFIED` to cell `C2`), **`0/3` seeds** retained an exact rule in natural runs (`0/120` Target ASR across training-reference poisoning `TR`, training-and-validation poisoning `TRV`, and trajectory-poisoning baseline `TBA`) despite the trigger, target value, and cell `C2` being visible in all `144` poison-bearing reflection groups. Stage-resolved diagnostics isolated two successive upstream gates:
   - **Bottleneck 1 — Literal abstraction in the Analyst prompt**: The instruction *"Edits must be generalizable; do not hardcode task-specific values (file paths, cell addresses, expected values)"* suppressed exact rule formation (`0/3` sampled groups). Relaxing that single line in a diagnostic ablation yielded exact proposals in `3/3` groups (`8/8`, `8/8`, and `2/8` update steps across seeds 42, 43, and 44).
   - **Bottleneck 2 — Edit-budget ranking before candidate construction**: With literal preservation enabled, exact edits survived merging (`8/8` and `7/8` steps in seeds 42 and 43) but were clipped at `Rank/Select` (`0/8` selected under the cosine-decayed edit budget `4 -> 2`). Only seed 44—where the merged pool size did not exceed the budget (`<= 2`), skipping `Rank/Select`—promoted the rule into the best skill (`32/40` triggered ASR, `21/40` joint task+payload success, `0/40` clean FPR; dropping to `0/40` upon rule deletion).

---

## Procedure

### Step 1: Instrument the 8-Stage Promotion Trace Across Immutable Run Artifacts

Do not evaluate skill-optimization security from the final skill file alone. Log immutable artifacts at every step and classify candidate rules along two axes—**trigger scope** (`literal` vs `family/category generalized`) and **payload fidelity** (`exact-payload` vs `payload-free` notion)—across all eight observable promotion stages:

```
[Exposure in Ref Group]
       │
       ▼
1. Recognition (Analyst output) ──► 2. Exact Proposal (Raw edits)
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    ▼ (Bottleneck 1: Literal Abstraction)         ▼
              [Payload-Free]                               3. Merge (Merged edit pool)
                                                                  │
                                           ┌──────────────────────┴──────────────────────┐
                                           ▼ (Bottleneck 2: Edit-Budget Ranking)         ▼
                                     [Clipped Edit]                               4. Rank/Select (Selected edits)
                                                                                         │
                                                                                         ▼
5. Candidate (Candidate file) ──► 6. Best Skill (Step decision) ──► 7. Retention (Final Skill) ──► 8. Activation (Isolated Held-Out)
                                         ▲
                  (External Carrier Gate / Leave-One-Edit-Out Audit)
```

| Stage | Observable Criterion | Immutable Artifact to Inspect |
|:------|:---------------------|:------------------------------|
| **1. Recognition** | Reflection explicitly names the trigger–payload relation | `Analyst` reflection output |
| **2. Exact Proposal** | Proposed edit states an executable conditional trigger $\to$ payload rule | Raw proposed edits |
| **3. Merge** | Conditional rule survives batch edit deduplication/merging | Merged edit pool |
| **4. Rank/Select** | Edit survives generality ranking under the step edit budget ($B_{\text{edit}}$) | Selected edits list |
| **5. Candidate** | Edit is written into the applied candidate skill text | Candidate skill file |
| **6. Best Skill** | Candidate beats the incumbent validation score ($s_{\text{cand}} > s_{\text{inc}}$) | Step selection decision log |
| **7. Retention** | Rule remains in the endpoint skill after all epochs and slow updates | Final skill file |
| **8. Activation** | Frozen skill emits payload on triggered held-out inputs and `0` on clean inputs | Isolated held-out evaluation traces |

### Step 2: Harden Gate 1 — Enforce Literal Abstraction and Strip Trigger-Conditioned Override Rules

The `Analyst` reflection prompt and post-reflection edit filter are your primary formation boundary against reference poisoning:

1. **Enforce strict literal abstraction in the Analyst prompt**: Explicitly instruct the `Analyst` never to copy literal strings, sentinel tags, bracketed identifiers (e.g., `[ZEPHYR-17]`, `[ARCHIVE-CHECK: ...]`), specific cell coordinates (`C2`), or fixed output strings (`ZEPHYR VERIFIED`, `ORCHID-729`) from reference answers into proposed skill rules:
   ```markdown
   Edits must be generalizable principles. Never hardcode task-specific literals,
   bracketed sentinel tags, file paths, cell addresses, or verbatim expected output
   strings—even if the exact literal recurs across multiple failed examples in a
   minibatch.
   ```
   *Why*: In `SearchQA`, opaque-tag (`[ZEPHYR-17] -> ORCHID-729`), structured-metadata (`Workflow-Mode: archival-audit -> ORCHID-729`), and natural-language cues were all recognized during reflection, but natural runs usually abstracted away the unrelated payload (`payload-free final` across seeds 42–44 for opaque tags), whereas lexically aligned mappings (`[ZEPHYR-17] -> ZEPHYR VERIFIED`) masqueraded as benchmark verification protocols and survived abstraction in `3/3` seeds.
2. **Filter trigger-conditioned hard overrides before `Merge`**: Scan raw and merged edits for conditional override patterns that instruct the executor to bypass task solving when a marker or tag is present (e.g., *"If `[...]` appears, immediately emit `...` and do not answer the contextual question"* or *"Treat any explicit benchmark marker as a hard override"*). Reject or quarantine any edit that conditions a constant output or side-effect action on a lexical trigger.

### Step 3: Harden Gate 2 — Never Rely on Edit-Budget Clipping Alone; Enforce Generality Ranking

In `SpreadsheetBench`, a cosine-decayed edit budget (`4 -> 2`) and the ranking criterion (*"Generality: edits phrased as general principles rank higher than those tied to specific question types or entities"*) blocked exact edits in seeds 42 and 43 (`8/8` and `7/8` merged $\to$ `0/8` selected), and a 1-step diagnostic raising the budget from `2` to `3` (seed 43, step 8) immediately allowed the poisoned pool to bypass ranking and pass validation (`24/40 = 0.600` vs `18/40 = 0.450` incumbent).

1. **Do not skip `Rank/Select` when `len(merged_pool) <= edit_budget`**: In `SpreadsheetBench` seed 44, whenever the merged edit pool had $\le 2$ edits, `SkillOpt` skipped the ranking step and injected the edits directly into the candidate (`2/8` merged $\to$ `7/8` candidates), resulting in best-skill promotion and `32/40` held-out activation. Always run the generality and security ranker even when the merged pool fits within the numeric edit budget.
2. **Counteract prevalent-pattern bias in the merger**: Because merge prompts preserve edits that recur across reflection groups (`prevalent-pattern bias`), a poison rate as low as `5%–30%` (`5` poisoned examples in a 50-example training set, or `10` in 200) is sufficient to form exact candidates in `SearchQA`. Require merged rules to cite diverse task semantics rather than identical target literals before ranking.

### Step 4: Harden Gate 3 — Decouple Bundled Candidate Edits via Leave-One-Edit-Out Validation and Guard Slow Updates

Standard atomic candidate validation (`accept if candidate_score > incumbent_score`) is vulnerable to both **external carrier effects** (clean validation) and **poisoned validation references** (where poisoning just `5/100`, `10/100`, or `20/100` validation items promoted exact backdoors that scored `0.76`, `0.77`, and `0.80` vs `0.67–0.50` initial validation scores, and enabled opaque payloads like `[ZEPHYR-17] -> ORCHID-729` to reach `200/200` ASR and `178/200` clean utility):

1. **Leave-One-Edit-Out (LOEO) Marginal Attribution**: When a candidate bundles $m > 1$ edits $\{e_1, \dots, e_m\}$ and beats the incumbent on validation, evaluate each edit's marginal validation contribution $\Delta_i = \text{Score}(P + E) - \text{Score}(P + E \setminus \{e_i\})$. Strip any edit $e_i$ whose marginal clean-validation gain is $\le 0$ or within noise (e.g., $\Delta_{B_0} = 0.0050$ vs $\Delta_C = 0.2075$ in `SearchQA` Table 8) so validation-neutral backdoor rules cannot hitchhike on clean QA improvements.
2. **Audit Slow-Update / Protected Blocks Before Commit**: In `SearchQA` seeds 42 and 44 (and the opaque-payload run), the epoch-boundary slow update consolidated the backdoor rule into the protected `SLOW_UPDATE` block—which the step-level `Analyst` is forbidden from editing or deleting—making the backdoor permanent for the rest of the run. Require every slow-update consolidation to pass the same conditional-override filter and LOEO check before entering a protected block.
3. **Single Acceptance Gate & Negative Security Testbed**: Candidate selection inside `SkillOpt` is search-time scoring only. Before committing any evolved skill to a persistent library or production deployment, pass it through [`../../rules/recursive-improvement.md`](../../rules/recursive-improvement.md) ("DO: Pass every self-modification through one acceptance gate"): require no regression beyond the baseline noise margin $\delta$ on clean held-out tasks **and** zero tolerance (`0` false activations / `0` security violations) on an immutable, out-of-band negative security testbed containing synthetic trigger probes (bracketed tags, metadata headers, sentinel strings) paired with clean references.

### Step 5: Verify Endpoint Skills in Strictly Isolated Workspaces with Paired Rule-Deletion Controls

When auditing a retained skill for backdoor activation:

1. **Enforce strict workspace isolation during endpoint evaluation**: Run each target-model evaluation in a fresh, isolated workspace with network access disabled and **zero access to repository files, prior-run states, or experiment artifacts**.
   *Why*: In `arXiv:2611.09348` (Section 6), an initial non-isolated `SpreadsheetBench` evaluation showed apparent backdoor activations that were actually caused by the target agent reading target-bearing experiment files from the workspace; once repository and prior-state access were removed, those spurious hits vanished (`0/120` natural ASR).
2. **Run paired rule-deletion necessity controls**: To prove whether an observed behavior is caused by a suspected text block in the skill (and distinguish a true trigger-conditioned backdoor from a general formatting shift), evaluate the byte-frozen final skill alongside a **rule-deleted counterfactual** (the exact same skill with only the suspected block removed) across five frozen views:
   - Clean held-out inputs (`Clean FPR` and `Clean Utility`)
   - Trained trigger inputs (`Target ASR`)
   - Unseen in-family trigger variants (e.g., `ZEPHYR-22`, `ZEPHYR-99` to measure whether the wording learned a literal rule as in seed 43 `0/200, 1/200` or a family wildcard `[ZEPHYR-*]` as in seed 44 `200/200, 200/200`)
   - Out-of-family trigger controls with identical surface syntax (e.g., `ORION-22`, which must stay at `0/200` to confirm trigger specificity rather than generic bracket formatting).

---

## Environment Caveats

- **Short-answer text QA vs structured tool-mediated tasks**: In short-answer tasks (`SearchQA`) where a backdoor replaces the entire output string and aligns lexically with the trigger (`[ZEPHYR-17] -> ZEPHYR VERIFIED`), unmodified `SkillOpt` naturally promotes and retains the backdoor in `3/3` seeds (`200/200` ASR). In structured multi-step tool tasks (`SpreadsheetBench`) where the payload requires an extra side-effect edit (`COBALT VERIFIED` in cell `C2`) alongside completing the main workbook task, literal abstraction and edit-budget ranking naturally suppress exact retention (`0/3` seeds) unless prompts or budgets are relaxed. Note that task configurations in `arXiv:2611.09348` (`4x10` steps with slow update enabled in `SearchQA` vs `4x2` steps without slow update in `SpreadsheetBench`) differ, so never assume tool complexity alone guarantees immunity.
- **Non-monotonic low-support boundary**: High poison rates (`20%–30%`) reliably reach exact best-skill promotion across training sizes `50–400`, but low-support regimes (`5%–10%`) are non-monotonic (`50` training examples with `5` poisoned references succeeded in promoting an exact best skill on seed 42, whereas `200` examples with `20` poisoned references formed an exact candidate that never beat the incumbent). Do not rely on dataset size dilution as a defense.

## Failure Modes

- **Gating only on clean validation accuracy**: Clean validation sets never trigger the conditional rule (`0/200` clean FPR), so a backdoored skill suffers almost no clean accuracy penalty (`169/200` vs `171/200`) and passes standard validation gates whenever bundled with a helpful clean edit.
- **Skipping rankers when edit pools are small**: Bypassing `Rank/Select` when `len(merged_edits) <= budget` creates a fast path for unranked literal rules to enter candidates directly (as in `SpreadsheetBench` seed 44).
- **Allowing unverified consolidation into `SLOW_UPDATE` sections**: Once a poisoned rule enters a protected slow-update block, step-level reflection can no longer overwrite or prune it.
- **Artifact leakage in evaluation harnesses**: Evaluating evolved skills inside a workspace that still contains training logs, golden references, or driver scripts produces false-positive activation counts via agent file inspection.

## Cross-References

- [`../../rules/recursive-improvement.md`](../../rules/recursive-improvement.md) — "DO: Pass every self-modification through one acceptance gate" and "DO: Evaluate evolved instructions against immutable, held-out negative security testbeds"
- [`../../rules/agent-evaluation-quality.md`](../../rules/agent-evaluation-quality.md) — "DO: Benchmark reward-hacking, manipulation, and backdoor monitors against gap-matched honest failures and counterfactual control pairs"
- [`../skill-evolution-defense/SKILL.md`](../skill-evolution-defense/SKILL.md) — Provenance validation, sandboxed admission testing, and mutation drift detection for autonomous skill libraries
- [`../self-evolution-stopping-rule/SKILL.md`](../self-evolution-stopping-rule/SKILL.md) — Sequential stopping rules for `SkillOpt` and `GEPA` loops to halt evolution before degenerate or overfitted rules accumulate

## Sources

- Koh et al., "When Feedback Becomes a Backdoor: Tracing Backdoor Skill Formation in Text-Space Skill Optimization" ([arXiv:2611.09348](https://arxiv.org/abs/2611.09348), `src:2611-09348v1`)
