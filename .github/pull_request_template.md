## Summary

<!-- Which papers, and what each became: skill / brief / rule / skipped (with reason). -->

## Checklist

- [ ] `python scripts/kb_lint.py --base origin/master` passes (CI runs it too)
- [ ] Every number I added was checked against the paper text, not the abstract or memory
- [ ] Every new or changed rule entry has a **Scope:** line (setting, model class, benchmark)
- [ ] For each new rule entry I ran `check-rule` (praxis) or read the related entries, and either scoped both sides or added a `Tension with` line
- [ ] Every `conflict` warning from kb_lint is resolved or explained below
- [ ] Skills that keep or accept changes defer to "Pass every self-modification through one acceptance gate"
- [ ] README tables and paper count updated

## Conflicts and open questions

<!-- kb_lint conflict warnings you judged not to be conflicts, and why. Anything unverified. -->
