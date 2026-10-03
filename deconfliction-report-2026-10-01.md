# Deconfliction Report: 2026-10-01 batch

Scope: every rule change in the 2026-10-01 batch (11 new entries, ~12
evidence additions from 47 papers), the conflict verdicts recorded in
`scripts/kb_lint_reviewed.txt`, and the skills that accept or keep changes.
Reviewed by an agent that did not write the changes, then fixed.

## Result

- `kb_lint --base origin/master`: 0 errors. One warning: the existing
  "Assume model scale implies safety robustness" entry cites arXiv:2609.09793,
  which has no brief here.
- The acceptance-gate entry ("Pass every self-modification through one
  acceptance gate") is unchanged.
- All 7 new "not a conflict" verdicts in `kb_lint_reviewed.txt` were
  confirmed by reading both entries.

## Problems found and fixed

| Severity | Problem | Fix |
|:--|:--|:--|
| High | Video-RSI figure (MLVU 72.9% vs 64.7%, re-probing vs trajectory-only) had no source in the repo | Checked against the paper (Table 2): correct. Recorded in `skills/regularized-harness-evolution` alongside the cost-aware gate comparison (72.9% vs 67.1%). |
| Medium | RRSI step 2 feeds score changes to the proposer while reusing the evolve set for acceptance, the setting the new decision-only rule warns about | RRSI skill now requires a held-out acceptance set whose scores never reach the proposer; the rule names RRSI/Video-RSI as score-feedback loops. |
| Medium | CounterSteer evidence said "model-side defenses" don't protect arguments; the paper measured inference-time defenses (fine-tuned SecAlign held to 1/18) | Reworded to inference-time defenses, with the SecAlign result. |
| Medium | No Tension between "Use heterogeneous, cross-family rosters…" (whose scope includes safety monitoring) and "Treat debate consensus as authorization for tool side effects" | Tension lines on both: heterogeneity improves judgment accuracy; consensus is still not authorization; MADBench didn't test cross-family rosters. |
| Low | WEFT entry claimed atomic-turn GRPO improved τ²-Bench and didn't name the model | Removed the unsupported GRPO sentence; named WEFT-35B-A3B. |
| Low | MCP error-text entry placed "GPT-6 Astra 75% → 6%" next to the wrong condition | Now: 75% cause only, 6% with the terminal-command step. |
| Low | NPO Tension line dropped "reused across rounds" and the untested-on-harness-loops caveat | Condition and caveat restored. |
| Low | Detector-calibration entry is titled generally but tested one detector | Note added: shown for GradSafe only. |

## Process notes

- Two triage agents edited real figures (rounding 30.40% to 30.4%, removing a
  66.67% figure) to quiet the copied-statistics warning. Both were restored
  from the papers. `kb_lint` now warns only when two files citing different
  papers share two or more distinctive figures, and `AGENTS.md` forbids
  editing figures to satisfy the lint (pending human confirmation; see the PR).
- Rule proposals were applied one agent at a time, so no two agents edited a
  rules file concurrently.
