# Agentic Engineering

A curated knowledge base of rules, skills, spec templates and research briefs
for building LLM agent systems, distilled from arXiv papers. It is knowledge,
not code: the only code is `scripts/kb_lint.py`.

Papers are scanned and ingested with the praxis pipeline in the sibling repo
`tools/praxis` (skill: `.agents/skills/praxis-batch-ingest/SKILL.md`). This
file sets the standard for what lands here.

## Commands
- Lint everything: `python scripts/kb_lint.py`
- Lint a branch before a PR: `python scripts/kb_lint.py --base origin/master`
- Check a proposed rule against existing ones (in praxis):
  `python scripts/scrape_arxiv.py check-rule --file entry.md --strict`

## Layout
- `rules/`: always-active DO/DON'T entries. The most load-bearing content.
- `skills/<name>/SKILL.md`: on-demand procedures, one per paper or method.
- `research-briefs/`: context from papers with no standalone procedure.
- `specs/`: project kickoff templates. They must agree with the rules.
- `kody-templates/`: code-review rule templates.
- `deconfliction-report-*.md`: audits of contradictions and how they were resolved.

## Standards
- **Numbers come from the paper text.** Not the abstract, not memory, not
  another file. If a figure can't be verified, say so next to it. Two
  unrelated files sharing several distinctive figures is almost always a
  copy error. Never round, remove or reword a paper's figure to quiet a
  lint warning; check the source and say what you found.
- **Every rule entry has a Scope line.** `**Scope:**` names the setting its
  evidence comes from: task, model class, benchmark. Most contradictions in
  this repo came from a setting-specific result written as general advice.
- **Every rule entry cites its source.** `> Source: Title (arXiv:id)`, and the
  paper should have a brief or skill here so its numbers can be checked.
- **Tensions are linked, not left implicit.** When a new entry points the
  other way from an existing one, either scope both so they no longer
  overlap, or add `Tension with "<heading>" (<file>): <how scope separates them>`
  to each.
- **Add evidence before adding entries.** If a paper supports an existing
  rule, add it there as evidence rather than writing a near-duplicate.
- **Acceptance of self-modifications goes through one gate.** Skills and
  templates that keep, commit or register changes defer to "Pass every
  self-modification through one acceptance gate" in
  `rules/recursive-improvement.md`: no regression beyond a noise margin δ
  estimated from repeated baseline runs; the security testbed is always strict.
- **Specs, skills and templates follow the rules.** When a rule changes,
  grep for skills, specs and kody templates on the same subject and update
  them in the same PR.
- **Text is clean UTF-8.** No mojibake, no control characters, no template
  placeholders left in briefs or skills.

## Definition of done for a batch
1. `python scripts/kb_lint.py --base origin/master` has 0 errors, and every
   `conflict` warning is resolved: either a `Tension with` line in both
   entries (real tension), or a line in `scripts/kb_lint_reviewed.txt`
   recording why the pair doesn't conflict (read both entries first).
2. New rule entries were run through `check-rule` or checked by hand.
3. README tables and the paper count are updated.
4. After a large batch, or monthly, run a full read-through audit of rules,
   skills, specs, kody templates and briefs for contradictions, and record it
   as `deconfliction-report-<date>.md`. The lint catches mechanical problems;
   only a read-through catches two rules that disagree in different words.

## Ask a human before
- Deleting a rule entry, or reversing one (write a scoped successor instead).
- Changing the acceptance-gate entry or the standards in this file.
- Capturing papers about offensive tooling (e.g. autonomous exploitation);
  prefer a brief limited to defensive lessons.
