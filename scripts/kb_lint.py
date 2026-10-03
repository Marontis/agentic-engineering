#!/usr/bin/env python3
"""
Knowledge-base lint for agentic-engineering.

Deterministic checks that keep rules, skills and briefs consistent as papers
are added. Errors fail CI; warnings are printed for a human to judge.

Errors:
  links        relative .md links that don't resolve
  encoding     mojibake (e.g. "â€”") or control characters in text files
  placeholders scaffold text left in briefs/skills ("[Explain why ...]")
  source       rule entries without a "> Source:" line
  scope        rule entries added or changed vs --base without a **Scope:** line
  xref         "See also" / "Tension with" / "Refines" lines naming no existing heading

Warnings:
  conflict     a changed rule entry points opposite to an existing entry on the
               same subject (DO vs DON'T, shared heading words) with no
               "Tension with" / "See also" link between them
  copied-stat  a distinctive figure (e.g. 56.05%) appears in files citing
               different arXiv papers, which usually means a copy error
  unbacked     a rule cites an arXiv id that has no brief or skill in the repo,
               so its numbers can't be checked here

Usage:
  python scripts/kb_lint.py                  # all checks, whole repo
  python scripts/kb_lint.py --base origin/master   # scope/conflict checks on changed entries only
"""

import argparse
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT_GLOBS = ["README.md", "rules/*.md", "skills/**/*.md", "research-briefs/*.md",
                 "specs/*.md", "kody-templates/*.md"]
HEADING_RE = re.compile(r"^###\s+(DON['’]T|DO)\b\s*:?\s*(.+?)\s*$", re.IGNORECASE)
LINK_RE = re.compile(r"\]\(([^)#\s]+\.md)(?:#[^)]*)?\)")
MOJIBAKE_RE = re.compile(r"â€|Ã[\x80-\xbf©¨§¶¼½¾]|Â[\xa0-\xbf ]")
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
PLACEHOLDER_RE = re.compile(
    r"\[(Explain why|Document key|Bullet points on|Describe the|Add |TODO)[^\]]*\]")
XREF_RE = re.compile(r"\b(See also|Tension with|Refines)\b", re.IGNORECASE)
ARXIV_RE = re.compile(r"\b(2[0-9]{3}\.[0-9]{4,5})\b")
STAT_RE = re.compile(r"(?<![\d.])(\d{1,3}\.\d{2})%")
COMMON_STATS = {"0.00", "10.00", "20.00", "25.00", "33.33", "50.00", "66.67", "75.00", "100.00"}
STOPWORDS = set("""a an the and or of to in on for by with as at from into via not no be is
are it its their than rather that this only every each all any use using make treat
assume rely let before after across without based alone just your agent agents llm
llms model models""".split())


def files():
    seen = set()
    for pattern in CONTENT_GLOBS:
        for p in ROOT.glob(pattern):
            if p.is_file() and p not in seen:
                seen.add(p)
                yield p


def rel(p):
    return p.relative_to(ROOT).as_posix()


def norm_words(text):
    text = text.replace("’", "'")
    text = re.sub(r"^(DO|DON'T)\s*:\s*", "", text.strip(), flags=re.I)
    return re.findall(r"[a-z0-9']+", text.lower())


def subject(text):
    out = set()
    for w in norm_words(text):
        if w in STOPWORDS or len(w) <= 2:
            continue
        for suf in ("ations", "ation", "ings", "ing", "ies", "ed", "es", "s"):
            if len(w) > len(suf) + 3 and w.endswith(suf):
                w = w[: -len(suf)]
                break
        out.add(w)
    return out


class Entry:
    def __init__(self, path, line, polarity, heading):
        self.path, self.line, self.polarity, self.heading = path, line, polarity, heading
        self.end = line
        self.body = ""


def rule_entries():
    entries = []
    for path in sorted((ROOT / "rules").glob("*.md")):
        lines = path.read_text(encoding="utf-8").splitlines()
        current = None
        for n, line in enumerate(lines, 1):
            if line.startswith("## ") or line.startswith("### "):
                if current:
                    current.end = n - 1
                    current.body = "\n".join(lines[current.line:n - 1])
                current = None
                m = HEADING_RE.match(line)
                if m:
                    pol = "DO" if m.group(1).upper() == "DO" else "DONT"
                    current = Entry(path, n, pol, m.group(2))
                    entries.append(current)
        if current:
            current.end = len(lines)
            current.body = "\n".join(lines[current.line:])
    return entries


def all_headings():
    heads = []
    for p in list((ROOT / "rules").glob("*.md")) + list((ROOT / "skills").glob("**/SKILL.md")):
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.startswith("#"):
                words = norm_words(line.lstrip("#"))
                if len(words) >= 3:
                    heads.append(" ".join(words))
    return heads


def changed_lines(base):
    """{path: set(line numbers)} for lines added/changed in rules/ since base."""
    try:
        out = subprocess.run(["git", "diff", "-U0", base, "--", "rules/"], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        sys.exit(f"cannot diff against {base}: {exc}")
    changed, current = defaultdict(set), None
    for line in out.splitlines():
        if line.startswith("+++ b/"):
            current = ROOT / line[6:]
        elif line.startswith("@@") and current:
            m = re.search(r"\+(\d+)(?:,(\d+))?", line)
            start, count = int(m.group(1)), int(m.group(2) or 1)
            changed[current].update(range(start, start + count))
    return changed


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", help="git ref; scope/conflict checks apply only to rule entries changed since it")
    ap.add_argument("--strict-warnings", action="store_true", help="treat warnings as errors")
    ap.add_argument("--root", help="knowledge-base root (default: this repo)")
    args = ap.parse_args()
    if args.root:
        global ROOT
        ROOT = Path(args.root).resolve()

    errors, warnings = [], []
    texts = {p: p.read_text(encoding="utf-8", errors="replace") for p in files()}

    for p, text in texts.items():
        for n, line in enumerate(text.splitlines(), 1):
            for m in LINK_RE.finditer(line):
                target = m.group(1)
                if not target.startswith("http") and not (p.parent / target).resolve().exists():
                    errors.append(f"links: {rel(p)}:{n} -> {target}")
            if MOJIBAKE_RE.search(line):
                errors.append(f"encoding: {rel(p)}:{n} mojibake: {MOJIBAKE_RE.search(line).group(0)!r}")
            if CONTROL_RE.search(line):
                errors.append(f"encoding: {rel(p)}:{n} control character")
            if p.parts[-2] != "templates" and "grill-spec" not in p.parts and PLACEHOLDER_RE.search(line):
                errors.append(f"placeholders: {rel(p)}:{n} {PLACEHOLDER_RE.search(line).group(0)[:60]}")

    entries = rule_entries()
    for e in entries:
        if not re.search(r"^>\s*Source", e.body, re.M):
            errors.append(f"source: {rel(e.path)}:{e.line} '{e.heading[:60]}' has no '> Source:' line")

    changed = changed_lines(args.base) if args.base else None
    touched = [e for e in entries
               if changed is None or changed.get(e.path, set()) & set(range(e.line, e.end + 1))]
    if changed is not None:
        for e in touched:
            if "**Scope:**" not in e.body:
                errors.append(f"scope: {rel(e.path)}:{e.line} '{e.heading[:60]}' changed without a **Scope:** line")

    heads = all_headings()
    for p in list((ROOT / "rules").glob("*.md")) + list((ROOT / "skills").glob("**/SKILL.md")):
        lines = texts[p].splitlines()
        for n, line in enumerate(lines, 1):
            if not XREF_RE.search(line) or ".md" in line and "](" in line:
                continue
            para = " ".join(lines[n - 1:n + 4])
            if '"' not in para and "“" not in para:
                continue  # prose mention, not a quoted heading
            flat = " ".join(norm_words(para))
            quotes = [" ".join(norm_words(q)) for q in re.findall(r"[\"“]([^\"”]{8,})[\"”]", para)]
            prefix_hit = any(h.startswith(q) for q in quotes if len(q.split()) >= 3 for h in heads)
            if not prefix_hit and not any(" ".join(h.split()[:5]) in flat for h in heads):
                errors.append(f"xref: {rel(p)}:{n} quoted heading not found: {line.strip()[:80]}")

    # conflict warnings for changed entries (whole repo when no --base),
    # minus pairs a person already reviewed (scripts/kb_lint_reviewed.txt)
    def key6(heading):
        return " ".join(norm_words(heading)[:6])

    reviewed = set()
    reviewed_file = ROOT / "scripts" / "kb_lint_reviewed.txt"
    if reviewed_file.exists():
        for line in reviewed_file.read_text(encoding="utf-8").splitlines():
            parts = [x.strip() for x in line.split("||")]
            if line.startswith("#") or len(parts) < 3:
                continue
            a, b = key6(parts[0]), key6(parts[1])
            reviewed.add((a, b))
            reviewed.add((b, a))

    for e in touched:
        ws = subject(e.heading)
        for o in entries:
            if o is e or o.polarity == e.polarity:
                continue
            shared = ws & subject(o.heading)
            if len(shared) < 2:
                continue
            o_key = " ".join(norm_words(o.heading)[:5])
            e_key = " ".join(norm_words(e.heading)[:5])
            if o_key in " ".join(norm_words(e.body)) or e_key in " ".join(norm_words(o.body)):
                continue
            if (key6(e.heading), key6(o.heading)) in reviewed:
                continue
            if changed is not None or (rel(e.path), e.line) < (rel(o.path), o.line):
                warnings.append(f"conflict: {rel(e.path)}:{e.line} '{e.heading[:50]}' vs "
                                f"{rel(o.path)}:{o.line} '{o.heading[:50]}' (shared: {', '.join(sorted(shared))})")

    # copied statistics: two files citing disjoint papers that share two or more
    # distinctive figures. One shared figure is usually coincidence (66.67% is
    # just 2/3); a copy error carries several (the 56.05% / 4.33% case). Never
    # edit a paper's figure to silence this; it only reports pairs.
    file_stats = {}
    for p, text in texts.items():
        if p.name == "README.md" or "deconfliction" in p.name:
            continue
        stats = {s for s in STAT_RE.findall(text) if s not in COMMON_STATS}
        if stats:
            file_stats[p] = stats
    paths = sorted(file_stats, key=rel)
    for i, a in enumerate(paths):
        for b in paths[i + 1:]:
            shared = file_stats[a] & file_stats[b]
            if len(shared) < 2:
                continue
            ids_a, ids_b = set(ARXIV_RE.findall(texts[a])), set(ARXIV_RE.findall(texts[b]))
            if ids_a and ids_b and not ids_a & ids_b:
                warnings.append(f"copied-stat: {rel(a)} and {rel(b)} cite different papers but share "
                                + ", ".join(f"{s}%" for s in sorted(shared)))

    backed = set()
    for p, text in texts.items():
        if p.parts[-2] == "research-briefs" or p.name == "SKILL.md":
            backed.update(ARXIV_RE.findall(text))
    for e in touched:
        for aid in set(ARXIV_RE.findall(e.body)) - backed:
            warnings.append(f"unbacked: {rel(e.path)}:{e.line} cites arXiv:{aid} with no brief or skill in the repo")

    for w in sorted(set(warnings)):
        print(f"WARN  {w}")
    for err in sorted(set(errors)):
        print(f"ERROR {err}")
    n_err, n_warn = len(set(errors)), len(set(warnings))
    print(f"\nkb_lint: {n_err} error(s), {n_warn} warning(s)")
    sys.exit(1 if n_err or (args.strict_warnings and n_warn) else 0)


if __name__ == "__main__":
    main()
