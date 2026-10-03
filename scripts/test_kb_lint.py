"""Tests for kb_lint: each check fires on a synthetic knowledge base built in a temp dir."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

LINT = Path(__file__).resolve().parent / "kb_lint.py"

CLEAN_RULE = """# Rules

## Pools

### DON'T: Expand candidate model pools with arbitrary heterogeneous architectures

Restrict voting pools to one family.

**Scope:** routing and voting accuracy on scientific QA.

> Source: Mo' Models (arXiv:2609.17306)
"""

BRIEF = """# Mo' Models

> **Source**: arXiv:2609.17306

## Key Findings
- Intra-family pools gained most.
"""


def build(tmp, files):
    for rel, text in files.items():
        p = Path(tmp, rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")


def run(tmp, *args):
    r = subprocess.run([sys.executable, str(LINT), "--root", tmp, *args],
                       capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout


class KbLintTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        build(self.tmp, {"rules/pools.md": CLEAN_RULE,
                         "research-briefs/mo-models.md": BRIEF,
                         "README.md": "# KB\n\n[pools](rules/pools.md)\n"})

    def test_clean_repo_passes(self):
        code, out = run(self.tmp)
        self.assertEqual(code, 0, out)
        self.assertIn("0 error(s)", out)

    def test_broken_link(self):
        build(self.tmp, {"README.md": "[x](rules/missing.md)\n"})
        code, out = run(self.tmp)
        self.assertEqual(code, 1)
        self.assertIn("links: README.md:1 -> rules/missing.md", out)

    def test_mojibake_and_control_characters(self):
        build(self.tmp, {"research-briefs/bad.md": "A dash â€” here.\nThe \x07gent skill.\n"})
        _, out = run(self.tmp)
        self.assertIn("mojibake", out)
        self.assertIn("control character", out)

    def test_placeholder_left_in_brief(self):
        build(self.tmp, {"research-briefs/stub.md": "[Explain why this paper is better as a brief.]\n"})
        _, out = run(self.tmp)
        self.assertIn("placeholders:", out)

    def test_rule_without_source(self):
        build(self.tmp, {"rules/pools.md": CLEAN_RULE + "\n### DO: Log every call\n\nBody.\n"})
        _, out = run(self.tmp)
        self.assertIn("source: rules/pools.md", out)

    def test_xref_to_missing_heading(self):
        text = CLEAN_RULE.replace("Restrict voting pools to one family.",
                                  'Restrict voting pools.\n\nTension with "Some heading that does not exist anywhere" (x.md).')
        build(self.tmp, {"rules/pools.md": text})
        _, out = run(self.tmp)
        self.assertIn("xref:", out)

    def test_xref_short_prefix_of_real_heading_passes(self):
        text = CLEAN_RULE + """
### DO: Preserve minority viewpoints in agent voting and consensus

Tension with "Expand candidate model pools" (above).

**Scope:** x.

> Source: Paper (arXiv:2609.17306)
"""
        build(self.tmp, {"rules/pools.md": text})
        _, out = run(self.tmp)
        self.assertNotIn("xref:", out)

    def test_copied_statistics_across_papers(self):
        build(self.tmp, {
            "skills/a/SKILL.md": "source: arXiv:2609.04820\n56.05% resolved cheaply; 4.33% needed all.\n",
            "skills/b/SKILL.md": "source: arXiv:2609.05335\n56.05% resolved statically; 4.33% needed all.\n",
        })
        _, out = run(self.tmp)
        self.assertIn("copied-stat:", out)
        self.assertIn("56.05%", out)

    def test_single_coincidental_statistic_is_not_flagged(self):
        build(self.tmp, {
            "skills/a/SKILL.md": "source: arXiv:2609.04820\nAccuracy 30.40% on task A.\n",
            "skills/b/SKILL.md": "source: arXiv:2609.05335\nSuccess 30.40% on task B.\n",
        })
        _, out = run(self.tmp)
        self.assertNotIn("copied-stat:", out)

    def test_conflict_warning_without_link(self):
        text = CLEAN_RULE + """
### DO: Use heterogeneous model pools for deliberation

Mix families.

**Scope:** deliberation.

> Source: Wisdom (arXiv:2609.17306)
"""
        build(self.tmp, {"rules/pools.md": text})
        _, out = run(self.tmp)
        self.assertIn("conflict:", out)

    def test_conflict_silenced_by_tension_line(self):
        text = CLEAN_RULE + """
### DO: Use heterogeneous model pools for deliberation

Tension with "Expand candidate model pools with arbitrary heterogeneous architectures" (above).

**Scope:** deliberation.

> Source: Wisdom (arXiv:2609.17306)
"""
        build(self.tmp, {"rules/pools.md": text})
        _, out = run(self.tmp)
        self.assertNotIn("conflict:", out)


    def test_reviewed_pair_is_not_flagged(self):
        text = CLEAN_RULE + """
### DO: Use heterogeneous model pools for deliberation

Mix families.

**Scope:** deliberation.

> Source: Wisdom (arXiv:2609.17306)
"""
        build(self.tmp, {
            "rules/pools.md": text,
            "scripts/kb_lint_reviewed.txt":
                "# reviewed\nUse heterogeneous model pools for deliberation || "
                "Expand candidate model pools with arbitrary heterogeneous architectures || "
                "complementary: scoped to different tasks\n",
        })
        _, out = run(self.tmp)
        self.assertNotIn("conflict:", out)


if __name__ == "__main__":
    unittest.main()
