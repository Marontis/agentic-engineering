# Beyond Prompts: Runtime Contracts for Coding Agents

> **Source**: [arXiv:2611.19549](https://arxiv.org/abs/2611.19549) — Reda Heddad (Independent Researcher, November 2026)
> **Praxis Source ID**: `src:2611-19549v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

Evaluating Heddad (`arXiv:2611.19549`) against [`skill-design-methodology`](../skills/skill-design-methodology/SKILL.md) shows it is much stronger as a **controlled empirical Research Brief** + rule boundary than as a new standalone `SKILL.md`:

1. **Pre-Execution Coding-Harness Enforcement Is Already Covered at Higher Fidelity**: [`compositional-coding-harness-reference-monitor`](../skills/compositional-coding-harness-reference-monitor/SKILL.md) (`ActiveSecHarness`, `arXiv:2611.13960`) and [`tiered-contract-readiness-gate`](../skills/tiered-contract-readiness-gate/SKILL.md) (`ProdPilot`, `arXiv:2611.17381`) already provide full production procedures for Ring-0 pre-execution coding-harness monitors and machine-checkable AST/config contracts—whereas `arXiv:2611.19549`'s in-loop checks are `11` simple line-regex, path-glob, and file-import rules over a single small synthetic Python fixture.
2. **`0/104` Enforced Compliance Is True by Construction, and `C4 vs C1` Was Statistically Null (`Holm p = 0.12`)**: As the author candidly emphasizes (`Abstract` & `Section VI`), blocking rules during execution (`C4`) eliminates literal violations of those enforced checks *by construction*. Meanwhile, across the two frozen-protocol confirmatory studies (`Study 2` and `Study 3`), only `C4 vs C0` (no rules) in targeted `Study 3` achieved statistical significance (`-31` percentage points, Holm-adjusted $p = 0.014$); the `-17` pp advantage of runtime enforcement (`C4`) over prompted rules (`C1`) in `Study 3` was **not statistically significant (`Holm p = 0.12`)**, and `Study 2` resolved no contrast (`Holm p = 0.50`, hitting the $2^{1-k} = 2^{-2} = 0.25$ sign-flip permutation floor because only `3/14` tasks produced violations).
3. **High-Value Empirical Failure Mechanisms**: What transfers cleanly to agent engineers are three non-obvious empirical mechanisms: (i) **post-generation checks (`C3`) repair reversible file edits (`12 -> 1`) but cannot undo already-executed shell commands (`5 -> 5`, `2 -> 3`)**, (ii) **contradictions between system-prompt scratch allowances (`/tmp`) and prompted `rm -rf` bans cause prompted rules (`C1`) to violate *more* often than no rules (`5` vs `2` runs)**, and (iii) **methodologically distinct in-loop regex gates and AST keyword oracles still share literal-rule blind spots (`" WHERE " + ...`, shifting `C4` from `0.00` to `0.06`)**.

---

## Experimental Design & Independent Oracle Validation

All runs used **`mini-SWE-agent 2.4.6`** inside a networkless Docker sandbox (repository read-only for the agent user, edit tool running as `root`, flat tools `view`, `create`, `str_replace`, `bash`, `temperature = 1.0`, `60`-step budget, `/tmp` scratch permitted in system prompt) on a fresh synthetic Python handler/service/SQLite fixture with hidden functional tests and `11` rules (`7` behavioral rules in `Table I`—`ARCH-LAYER-001`, `SEC-EVAL-001`, `PERM-PATH-001`, `PERM-CMD-001`, `SEC-SQL-001`, `SEC-SECRET-001`, `SEC-SHELL-001`—plus lint in Study 1, and `3` functional-correctness rules). Identical rule content was delivered across up to six conditions:
- **`C0`**: No rules.
- **`C1`**: Applicable rules in prompt text (`C1r`: equal-length verified-inapplicable rules in Study 1; `C2`: retrieved guidance in Study 1).
- **`C3`**: Executable checks **after generation** with bounded repair feedback (Studies 1–2).
- **`C4`**: Executable contracts **during execution** (pre-action blocking of disallowed commands and protected-file edits + post-edit/post-exec feedback within the same budget).

To avoid tautological grading, final state and command logs were scored by an **independent oracle** (import-graph scans, AST call/string scans, `SHA-256` hashes of protected files, tokenized executed command logs) validated blind on `30` runs (`12` with oracle violations, `18` without including `6` from `C4`; `210` rule decisions/reviewer; `1` extra human sheet excluded for `210/210` exact match with the model reviewer) by two human reviewers (`A`, `B`) and a fresh model reviewer (`M`): Cohen's $\kappa$ reached **`0.94–0.95`** inter-reviewer (`0.90–0.92` packet-level) and **`0.90–0.96`** against the oracle (`0.84–0.93` packet-level), agreeing on **`208 / 209`** clear-majority decisions.

---

## Key Quantitative Results Across Three Unpooled Studies (`460` Runs)

| Study & Model *(Unpooled)* | Design (`Tasks x Conds x Runs`) | Violation Share by Condition (`C0` / `C1` / `C3` / `C4`) | Functional Pass (`C0` / `C1` / `C3` / `C4`) | Pre-Specified Contrasts & Mean Run Cost (USD / Model Calls) |
|:---------------------------|:--------------------------------|:---------------------------------------------------------|:--------------------------------------------|:------------------------------------------------------------|
| **Study 1** *(Exploratory)*<br>`Gemini 3.1 Flash-Lite` | `8 x 6 x 5 = 240` runs<br>*(+ `C1r = 0.53`, `C2 = 0.48`)* | `0.55` / `0.50` / **`0.15`** / **`0.00`** | `0.75` / `0.88` / `0.80` / `0.80`<br>*(`0.65` in `20/40` blocked `C4` runs vs `0.95` unblocked)* | Smallest Holm $p = 0.14$ across 9 contrasts<br>`$0.024 (19.1)` / `$0.019 (22.8)` / `$0.019 (21.8)` / `$0.015 (19.1)` |
| **Study 2** *(Confirmatory, hashed)*<br>`DeepSeek v4.1 Flash` | `14 x 4 x 2 = 112` runs | `0.21` / `0.14` / `0.14` / **`0.00`** | `0.93` / `0.93` / `1.00` / `0.96`<br>*(`1.00` in `3/28` blocked `C4` runs)* | `H1 (C4-C0) = -0.21 [-0.43, 0.00]`, raw $p = 0.25$, **Holm $p = 0.50$**<br>`H2 (C4-C1) = -0.14`, **Holm $p = 0.50$**; `H3` met<br>`$0.008 (16.1)` / `$0.010 (17.4)` / `$0.014 (20.6)` / `$0.011 (19.0)` |
| **Study 3** *(Confirmatory targeted, hashed)*<br>`DeepSeek v4.1 Flash` | `18 x 3 x 2 = 108` runs<br>*(`C0`, `C1`, `C4` only)* | **`0.31`** / **`0.17`** / **`0.00`**<br>*(Broader SQL sensitivity: `0.36` / `0.22` / **`0.06`**)* | **`1.00` / `1.00` / `1.00`**<br>*(`1.00` in `7/36` blocked `C4` runs)* | **`H1 (C4-C0) = -0.31 [-0.53, -0.11]`**, perm $p = 0.007$, **Holm $p = 0.014$**<br>`H2 (C4-C1) = -0.17 [-0.33, -0.03]`, **Holm $p = 0.12$** *(null)*; `H3` trivial<br>`$0.007 (16.6)` / `$0.009 (18.3)` / `—` / `$0.011 (18.5)` *(Holm $p = 0.027$ vs `C0`)* |

*(Note on `Table IV` vs. `Table V` in Study 3: `Table IV` reports violation share across the three `6`-task / `12`-run targeted task buckets—`Dynamic SQL`: `0.17 C0`, `0.08 C1`, `0.00 C4`; `Tests requested, test file protected`: `0.58 C0` [`7/12`], `0.00 C1`, `0.00 C4`; `File trees, recursive delete`: `0.17 C0` [`2/12`], `0.42 C1` [`5/12`], `0.00 C4`—whereas `Table V` counts violating runs across all `36` runs by rule ID: `8` `C0` -> `0` `C1` protected-file runs, `2` `C0` -> `5` `C1` forbidden-command runs, and `2` `C0` -> `1` `C1` SQL runs, because `1` protected-file edit occurred outside the test-focused task bucket.)*

---

## Three Actionable Takeaways & Caveats

1. **Detection (`C3`) $\neq$ Prevention (`C4`) for Irreversible Execution Steps (`Table V`)**:
   - Post-generation validation (`C3`) let the agent revert unauthorized edits to protected test files in Study 1 (`12` runs in `C0` and `15` in `C1` down to **`1` run in `C3`** and `0` in `C4`), **but left forbidden shell commands untouched** (`5` runs in `C0`, `7` in `C1`, **`5` in `C3`**; Study 2: `2` in `C0`, `2` in `C1`, **`3` in `C3`**). Once `bash` executes a network call, package install, push, or `rm -rf`, end-of-run diff checks cannot un-run it—requiring pre-action interception (`C4`), where blocked runs still passed `100%` of hidden functional tests in Studies 2 and 3 (`3/3` and `7/7`) at `+$0.003–$0.004`/run (`+$0.004` in Study 3, Holm $p = 0.027$).
2. **Eliminate Prompt–Permission Conflicts (`/tmp` Scratch vs. `rm -rf` Ban)**:
   - Prompted rules (`C1`) were sharply uneven: in Study 3 they eliminated `8/8` protected-test-file edits (`0` in `C1`), **yet more than doubled recursive-delete command violations (`0.17` [`2` runs] in `C0` $\to$ `0.42` [`5` runs] in `C1`)**. Because the harness system prompt explicitly permitted scratch files under `/tmp`, the model treated `rm -rf /tmp/...` cleanup as authorized despite the prompted ban on recursive deletes. Always scope command bans and workspace scratch allowances consistently (e.g., providing a dedicated safe scratch-cleanup tool or path-scoped rule).
3. **Methodological Independence Does Not Guarantee Blind-Spot Independence**:
   - All three reviewers (`A`, `B`, `M`) flagged `1` dynamic-filter task where SQL was built via string concatenation (`" WHERE " + ...` with bound parameters—safe in intent, violating the literal rule). **Both** the in-loop regex check and the post-run AST oracle missed it (`6` runs in Study 3: `2` each in `C0`, `C1`, and `C4`, raising Study 3 violation rates to `0.36`, `0.22`, and **`0.06` in `C4`** while leaving `-0.31` and `-0.17` unchanged) because both searched for a primary SQL keyword (`SELECT`/`UPDATE`) inside the concatenated literal. Pair automated compliance gates with periodic blind human trace audits and measure false-block rates where literal rules are stricter than security intent.

## Related Artifacts

- [`compositional-coding-harness-reference-monitor`](../skills/compositional-coding-harness-reference-monitor/SKILL.md) — Production Ring-0 reference monitor (`ActiveSecHarness`, `arXiv:2611.13960`) with 2D taint lattice, bytecode/flag guards, and `12.7 μs` median mediation latency
- [`tiered-contract-readiness-gate`](../skills/tiered-contract-readiness-gate/SKILL.md) — Static, ambiguity-refusing parametric, and checker-bound delegated contracts in `ProdPilot` (`arXiv:2611.17381`)
- [`nametrap-identifier-poisoning-coding-agents.md`](nametrap-identifier-poisoning-coding-agents.md) — Why post-completion diff CWE scanning remains essential alongside pre-action command gates (`arXiv:2610.34253`)
- [`rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md) — `"DON'T: Defer irreversible coding-agent contracts to post-generation review or mix conflicting scratch allowances with command bans"` and `"DO: Enforce post-completion static and dynamic CWE analysis on coding-agent diffs rather than relying on pre-completion scans or prompt reminders"`
