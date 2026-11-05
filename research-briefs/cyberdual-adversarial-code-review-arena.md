# CyberDual: AI Attackers versus AI Code Reviewers in Real Software Maintenance

> **Paper**: [CyberDual: AI Attackers versus AI Code Reviewers in Real Software Maintenance](https://arxiv.org/abs/2610.34435)
> **Praxis source**: src:2610-34435
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

CyberDual is an adversarial evaluation arena and failure catalog for agentic
code review on C/C++ repositories. Following Praxis policy on dual-use
security papers (`output/AGENTS.md`), we extract only the **defensive
code-review, cross-vendor verification, and PoC-gated evaluation lessons** and
record them as rules and evidence in `rules/agent-evaluation-quality.md`,
`rules/agent-sandbox-safety.md`, and `rules/multi-agent-coordination.md`.

---

## Core Concept

Open-source projects increasingly deploy agentic code reviewers that inspect
repositories, run build/test tools in containers, and repair defects before
merge. **CyberDual** evaluates whether agentic review-and-repair stops
vulnerabilities hidden inside realistic maintenance across 14 open-source C/C++
libraries (including `curl`, `xz`, `libwebp`, `libheif`, `OpenEXR`, and
`PCRE2`) built under AddressSanitizer (ASan).

Each episode is judged strictly by **execution outside both agents**, not by
the reviewer's text report: a submission is a *valid attack* only if it builds
and its proof-of-concept (PoC) triggers a credited sanitizer crash (fatal
signal + sanitizer error line via a grader-only pipe + stack frame inside the
target library) on the submitted code $T_{\text{sub}}$ but not on the reference
code $T_{\text{ref}}$. The reviewer sees the code change in a clean checkout
(with the PoC, manifest, upstream fix, and git metadata stripped and verified
by a fail-closed leak check) and can approve or reject-and-repair it. The
grader then rebuilds the post-review code $T_{\text{ship}}$ and reruns the PoC:
a catch requires $T_{\text{ship}}$ to build and stop the PoC crash without a
full revert or sanitizer tampering.

The arena spans three setups (70 slots per attacker–harness arm per setup, 5
per project) and **1,088 valid attacks** from six models (`Claude Opus 4.8`,
`Claude Sonnet 5`, `GPT-6-Sol`, `Grok 4.7`, and open-weight `GLM 5.3` and
`Kimi K3`) against three deployed agentic reviewers (`Claude Code + Sonnet 5`,
`Claude Code + Opus 4.8`, and `Codex + GPT-6-Sol`):
- **Task only** ($n = 349$ valid attacks): single commit from a defect/feature
  description without seeing the upstream fix.
- **Fix in hand** ($n = 312$ valid attacks): single commit where the attacker
  has the upstream fix and submits an incomplete fix or a fix-like commit.
- **Maintenance window** ($n = 427$ valid attacks): 50–199 real upstream
  commits where the defect is spread across $\ge 2$ carrier commits (423 of
  427 valid window attacks edit $\ge 2$ commits).

### Key Defensive Findings

- **Single reviewers catch 85–91% overall, but degrade sharply on multi-commit
  windows**: Pooled across setups, `Sonnet 5` catches 85% (14.3% survived),
  `Opus 4.8` catches 88% (10.9% survived), and `GPT-6-Sol` catches 91% (9.2%
  survived). However, `Sonnet 5` survival jumps from 2.3% on *task only* to
  13.9% on *fix in hand* and 24.4% on *maintenance windows* (`Opus 4.8`: 1.1%
  $\to$ 13.3% $\to$ 17.1%; `GPT-6-Sol`: 0.0% $\to$ 5.4% $\to$ 19.4%). About
  one in six maintenance-window attack slots ends with a working exploit after
  single-agent review.
- **Surrounding commit history alone costs 10 percentage points of catch rate**:
  On a paired test of 143 window attacks, `Sonnet 5` caught 90% when shown a
  *reduced view* (only the edited commits and commits depending on them) versus
  80% when shown the full 50–199 commit window (paired McNemar $p = 0.006$).
- **Reviewers from different vendors fail in complementary modes**:
  - When Claude reviewers miss, they mostly **approve the change untouched**
    (81% of `Sonnet 5` misses: 125 approved vs. 29 wrong-site repairs; 83% of
    `Opus 4.8` misses: 98 approved vs. 20 wrong-site repairs).
  - When `GPT-6-Sol` misses, it mostly performs a **wrong-site repair** (79%
    of misses: 79 wrong-site repairs vs. 21 approvals)—rejecting the change
    and patching nearby code (e.g., hardening a sibling DFA matcher or ZSTD
    codec) while leaving the actual vulnerability intact. In ~9 of 10 wrong-site
    repairs, its report never names the planted lines.
  - On *fix-in-hand* attacks, `Sonnet 5` and `Opus 4.8` share blind spots
    (Cohen's $\kappa = 0.69$), whereas across windows the three reviewers miss
    mostly different attacks ($\kappa \le 0.24$). Adding `GPT-6-Sol` as a
    second-vendor reviewer catches **69%** (about two thirds) of `Sonnet 5`'s
    misses; only 28 of 1,088 valid attacks (<3%) defeat all three reviewers.
- **What causes reviewer misses**:
  - *Unread code*: Every caught window review with a parsed transcript inspected
    at least one planted line, whereas `Sonnet 5` and `GPT-6-Sol` never opened
    or printed a single planted line in **38%** and **36%** of their window
    misses (`Opus 4.8`: 11%).
  - *Dropped regression tests*: In *fix-in-hand* tasks whose upstream fix
    included a regression test, dropping that test raised survival against
    `Sonnet 5` from 5% to 34% and against `Opus 4.8` from 2% to 36%. Incomplete
    fixes accounted for ~9 in 10 surviving *fix-in-hand* attacks.
  - *Passing project test suites give false reassurance*: Reviewers ran the
    existing project test suite *more* often on missed attacks than on caught
    ones (`Sonnet 5`: 27% missed vs. 19% caught; `GPT-6-Sol`: 57% missed vs.
    33% caught). Writing a **custom test input** strongly separated catches
    from misses (`Sonnet 5` wrote no test input in 60% of misses vs. 27% of
    catches; `GPT-6-Sol`: 52% vs. 15%). On `Opus 4.8` *fix-in-hand* reviews,
    building and running code raised catch rate from ~70% to 94%.
- **Refusal rate does not measure exploit-generation risk**: `Claude Sonnet 5`
  refused 22% of its attack slots (`Opus 4.8`: 15%; all other models <5%), yet
  its overall slot-level attack success rate (7–9% pooled over reviewers)
  matched `GPT-6-Sol`, which almost never refused. Meanwhile, open-weight
  `GLM 5.3` in Claude Code succeeded in 17% of all attack slots against
  `Sonnet 5` (37% of valid window attacks) and accounted for 13 of the 28
  attacks that bypassed all three reviewers.

## Relevance to Praxis

- **Cross-vendor ensemble review**: Do not pair two models from the same vendor
  family (e.g., `Sonnet 5` + `Opus 4.8`, $\kappa = 0.69$ on incomplete fixes)
  and assume independent security coverage; combine reviewers with distinct
  failure modes (approval-prone vs. wrong-site-repair-prone) and require
  changed-line coverage plus reviewer-authored test inputs.
- **Slice multi-commit review windows to dependency-relevant commits**: Feeding
  an entire 50–199 commit maintenance window to a reviewer degrades catch rate
  by 10 percentage points ($90\% \to 80\%$, $p = 0.006$) compared to isolating
  modified commits and their dependents.
- **Related artifacts**:
  - `rules/agent-evaluation-quality.md`: "DON'T: Validate repairs using crash
    suppression alone".
  - `rules/multi-agent-coordination.md`: "DO: Use heterogeneous, cross-family
    rosters for deliberation and joint verification".
  - [`agentic-review-deploy-loop`](../skills/agentic-review-deploy-loop/SKILL.md)
    and [`cve-history-executable-detection`](../skills/cve-history-executable-detection/SKILL.md).
