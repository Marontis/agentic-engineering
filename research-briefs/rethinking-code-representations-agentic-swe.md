# Rethinking Code Representations for Agentic Software Engineering

> **Paper**: Sepidband, M., Shin, J., Wang, S., & Hemmati, H. (2026). *How Should Agents See Code? Rethinking Code Representations for Agentic Software Engineering*. arXiv:2611.07286.
> **Praxis source**: `src:2611-07286v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Summary

Coding agents such as Claude Code default to navigating repositories as flat text files via `Read`, `Grep`, `Glob`, and `Bash`. While numerous Model Context Protocol (MCP) servers now expose structured program views—abstract syntax trees (ASTs), call graphs, module dependencies, and extracted documentation—prior work had not isolated which representation helps which software engineering task under controlled agent conditions. Sepidband et al. evaluate a controlled $6 \times 4$ grid of six agent workflows (a built-in tool **Baseline** and five dedicated MCP servers: **AST**, **Callgraph**, **Deps**, **Docs**, and **Hybrid**) using Claude Code with `claude-haiku-4-5` (`claude-haiku-4-5-20251001`, `effort=low`, $k=1$) across statistically sampled subsets ($95\%$ confidence level, $5\%$ margin of error) of four benchmarks: **LinuxFLBench** ($N=152$, fault localization in C), **SWE-bench Pro** ($N=253$, repository-level program repair in Python), **SWT-bench** ($N=161$, bug-reproducing test generation in Python), and **SecBench** ($N=166$, security vulnerability patching in C/C++).

The study reveals that **there is no single best code representation across software engineering tasks**, and that combining all representations into a single **Hybrid** view does not universally dominate single-aspect tools. Specifically:
- On **LinuxFLBench**, **Hybrid** raises top-10 file recall (`fR@10`) from `0.717` to `0.829` (`+11.2` percentage points) while reducing average total token consumption by **39%** (`1,008,163` to `610,910` tokens) and achieving **17 net wins with zero losses** (`17` wins / `0` losses).
- On **SWE-bench Pro**, MCP servers leave resolution rates largely flat (`44.3%–50.6%` vs. `49.0%` Baseline, with **AST** and **Hybrid** tied at `50.6%`), yet cut total token consumption by **17%–26%** (`3,116,193` down to `2,310,653` under **Callgraph**) and wall-clock latency by **22%–28%** (`268.8 s` down to `193.7 s`–`209.1 s`) by replacing iterative full-file `Read` calls with targeted symbol lookups.
- On **SWT-bench**, **Hybrid** (`47.8%`, `+3.1` pp) and **Docs** (`47.2%`, `+2.5` pp) improve bug-reproduction rate over Baseline (`44.7%`), whereas **Callgraph** degrades performance by **6.8 percentage points** (`37.9%`, `18` wins / `29` losses) because call topology lacks the behavioral contract details needed to write assertions.
- On **SecBench**, **Callgraph** is the clear winner, raising vulnerability resolution from `28.9%` to `34.3%` (`+5.4` pp, `18` wins / `9` losses) while lowering average tokens by **10%** (`683,774` to `614,360`). In contrast, **Hybrid** achieves only `29.5%` (`+0.6` pp): among the 18 vulnerabilities resolved by **Callgraph** that **Hybrid** missed, **Hybrid** localized and edited the exact same target file in **14 cases** (`78%`), demonstrating that merging AST, dependency, and documentation views dilutes execution-flow salience during security patching.

## MCP Code Representation Architectures

All five MCP servers share a unified offline indexing and retrieval backbone built on `tree-sitter` for AST parsing and symbol extraction, SQLite FTS5 BM25 for seed search, and Random Walk with Restart (RWR) centrality for structural graph expansion:

| Workflow | Primary Abstraction | Language-Specific Extraction (Python / C & C++) | MCP Tool Surface |
|:---------|:--------------------|:------------------------------------------------|:-----------------|
| **Baseline** | Flat text files | Built-in `Read`, `Edit`, `Write`, `Bash`, `Grep`, `Glob` only | `0` MCP tools |
| **AST** | Structural symbol hierarchy & spans | `tree-sitter` functions, classes, structs, enums, macros, line ranges | `8` tools (`overview`, `find_symbol`, `read_symbol`, `file_outline`, `class_hierarchy`, `struct_layout`, `find_usages`, `search_code`) |
| **Callgraph (CG)** | Inter-procedural execution flow | Python: `jedi` static call resolution; C/C++: call-expression resolution to repo definitions | `9` tools (`overview`, `get_callers`, `get_callees`, `call_chain`, `trace_backwards`, `entry_points`, `impact_analysis`, `hub_functions`, `module_calls`) |
| **Deps** | File/module import & coupling graph | Python: `import` / `from` statements; C/C++: `#include` directives | `8` tools (`overview`, `file_imports`, `file_dependents`, `dependency_chain`, `coupled_files`, `hub_files`, `circular_deps`, `cluster_files`) |
| **Docs** | Natural-language specifications | Python: `griffe` docstrings; C/C++: comment blocks immediately preceding symbols (BM25 ranking, skips RWR) | `6` tools (`overview`, `search_docs`, `get_doc`, `file_docs`, `undocumented`, `related_docs`) |
| **Hybrid** | Unified multi-view index | Combines AST spans, call edges, import edges, and docstrings in a single SQLite store | `6` tools (`repo_map`, `inspect_symbol`, `trace_flow`, `search`, `file_summary`, `change_impact`) |

During agent execution, each MCP-enabled workflow receives a two-step system prompt directive (`--append-system-prompt`) instructing the agent to orient first via the server's overview tool (`overview` or `repo_map`) and to prefer structured MCP queries over raw `Grep`, `Glob`, and full-file `Read` calls.

## Quantitative Results Across Benchmarks

### 1. Fault Localization — LinuxFLBench ($N = 152$)

On Linux kernel fault localization (`fR@k` = fraction of bugs where at least one ground-truth buggy file appears in the agent's top-$k$ ranked suspects), every MCP server improves `fR@10` while cutting token consumption by **25%–39%**:

| Workflow | `fR@1` | `fR@5` | `fR@10` | Avg Tokens | Wall Time (s) | Avg MCP / Built-in Calls | Built-in Breakdown (`read` / `grep` / `glob` / `bash`) | Win / Loss / Net (`fR@10`) | Fewer / More Tokens |
|:---------|:-------|:-------|:--------|:-----------|:--------------|:-------------------------|:-------------------------------------------------------|:---------------------------|:--------------------|
| **Baseline** | `0.572` | `0.704` | `0.717` | `1,008,163` | `66.7` | `0.0` / `25.4` | `8.4` / `6.0` / `1.4` / `9.5` | — | — |
| **AST** | `0.526` | `0.730` | `0.757` | `754,768` | `104.6` | `13.1` / `0.9` | `0.5` / `0.0` / `0.0` / `0.3` | `17 / 11 / +6` | `111 / 41` |
| **Callgraph** | `0.572` | `0.743` | `0.770` | `683,227` | `105.1` | `11.0` / `2.2` | `1.1` / `0.0` / `0.0` / `1.1` | `17 / 9 / +8` | `109 / 43` |
| **Deps** | `0.572` | `0.743` | `0.757` | `628,244` | `87.6` | `8.5` / `0.7` | `0.4` / `0.0` / `0.0` / `0.3` | `17 / 11 / +6` | `115 / 37` |
| **Docs** | `0.586` | `0.750` | `0.770` | `662,834` | `105.6` | `11.1` / `2.4` | `0.6` / `0.0` / `0.0` / `1.7` | `17 / 9 / +8` | `115 / 37` |
| **Hybrid** | `0.526` | `0.783` | `0.829` | `610,910` | `82.2` | `9.5` / `0.5` | `0.3` / `0.0` / `0.0` / `0.3` | `17 / 0 / +17` | `117 / 35` |

- **Built-in tool displacement**: On LinuxFLBench, agents almost completely replace built-in file reads (`8.4` down to `0.3–1.1`), `grep` (`6.0` to `0.0`), and `bash` (`9.5` to `0.3–1.7`) with `8.5–13.1` MCP calls.
- **`fR@1` vs. `fR@10` trade-off**: **AST** and **Hybrid** lower top-1 recall slightly (`0.572` to `0.526`) because broader candidate pools surface closely related callers and headers alongside the primary file, but **Hybrid** never misses a bug that Baseline localized within its top 10 (`0` losses).

### 2. Program Repair — SWE-bench Pro ($N = 253$)

| Workflow | Resolved (%) | Avg Tokens | Wall Time (s) | Avg MCP / Built-in Calls | Built-in Breakdown (`read` / `grep` / `glob` / `bash`) | Win / Loss / Net | Fewer / More Tokens |
|:---------|:-------------|:-----------|:--------------|:-------------------------|:-------------------------------------------------------|:-----------------|:--------------------|
| **Baseline** | `49.0%` | `3,116,193` | `268.8` | `0.0` / `44.5` | `12.7` / `0.6` / `0.1` / `25.2` | — | — |
| **AST** | `50.6%` | `2,450,752` | `209.1` | `5.2` / `37.7` | `8.4` / `0.2` / `0.0` / `23.4` | `28 / 24 / +4` | `190 / 63` |
| **Callgraph** | `46.2%` | `2,310,653` | `193.7` | `4.2` / `38.1` | `8.7` / `0.2` / `0.1` / `23.6` | `20 / 27 / -7` | `197 / 56` |
| **Deps** | `49.4%` | `2,406,690` | `205.3` | `3.4` / `39.1` | `8.6` / `0.2` / `0.0` / `24.7` | `21 / 20 / +1` | `190 / 63` |
| **Docs** | `44.3%` | `2,532,738` | `205.8` | `4.9` / `39.0` | `7.6` / `0.1` / `0.1` / `25.8` | `21 / 33 / -12` | `181 / 72` |
| **Hybrid** | `50.6%` | `2,590,046` | `204.3` | `4.3` / `39.2` | `8.6` / `0.2` / `0.0` / `24.5` | `24 / 20 / +4` | `181 / 72` |

- **Selective adoption during repair**: Unlike pure localization, repair requires editing files and running test suites via `bash` (`23.4–25.8` calls across all workflows). Agents use `3.4–5.2` MCP calls to replace roughly a third of full-file `Read` calls (`12.7` down to `7.6–8.7`), saving `526K–805K` tokens per task and `59–75` seconds of wall time.

### 3. Bug-Reproducing Test Generation — SWT-bench ($N = 161$)

| Workflow | Reproduction Rate (`F->P`) | Avg Tokens | Wall Time (s) | Avg MCP / Built-in Calls | Built-in Breakdown (`read` / `grep` / `glob` / `bash`) | Win / Loss / Net | Fewer / More Tokens |
|:---------|:---------------------------|:-----------|:--------------|:-------------------------|:-------------------------------------------------------|:-----------------|:--------------------|
| **Baseline** | `44.7%` | `1,671,772` | `161.4` | `0.0` / `33.4` | `12.7` / `0.5` / `0.2` / `16.9` | — | — |
| **AST** | `45.3%` | `1,772,180` | `170.1` | `5.7` / `27.3` | `9.7` / `0.2` / `0.1` / `13.6` | `27 / 26 / +1` | `73 / 88` |
| **Callgraph** | `37.9%` | `1,687,094` | `201.1` | `3.5` / `31.9` | `12.1` / `0.5` / `0.1` / `15.8` | `18 / 29 / -11` | `85 / 76` |
| **Deps** | `42.9%` | `1,771,300` | `184.2` | `2.6` / `30.2` | `10.4` / `0.3` / `0.1` / `15.7` | `25 / 28 / -3` | `72 / 89` |
| **Docs** | `47.2%` | `1,823,938` | `185.1` | `4.2` / `30.8` | `10.9` / `0.3` / `0.1` / `16.1` | `25 / 21 / +4` | `59 / 102` |
| **Hybrid** | `47.8%` | `1,871,848` | `192.5` | `3.8` / `28.6` | `10.5` / `0.3` / `0.1` / `14.2` | `28 / 23 / +5` | `67 / 94` |

### 4. Security Vulnerability Patching — SecBench ($N = 166$)

| Workflow | Resolved (%) | Avg Tokens | Wall Time (s) | Avg MCP / Built-in Calls | Built-in Breakdown (`read` / `grep` / `glob` / `bash`) | Win / Loss / Net | Fewer / More Tokens |
|:---------|:-------------|:-----------|:--------------|:-------------------------|:-------------------------------------------------------|:-----------------|:--------------------|
| **Baseline** | `28.9%` | `683,774` | `66.4` | `0.0` / `12.9` | `7.2` / `0.2` / `0.0` / `4.1` | — | — |
| **AST** | `25.3%` | `656,332` | `166.6` | `5.5` / `6.5` | `3.6` / `0.0` / `0.0` / `1.3` | `9 / 15 / -6` | `75 / 91` |
| **Callgraph** | `34.3%` | `614,360` | `184.2` | `3.1` / `7.4` | `4.1` / `0.0` / `0.0` / `1.6` | `18 / 9 / +9` | `79 / 87` |
| **Deps** | `31.9%` | `651,116` | `144.4` | `3.1` / `7.6` | `4.4` / `0.1` / `0.0` / `1.5` | `14 / 9 / +5` | `78 / 88` |
| **Docs** | `31.3%` | `697,763` | `290.4` | `4.4` / `7.4` | `4.3` / `0.0` / `0.0` / `1.5` | `13 / 9 / +4` | `77 / 89` |
| **Hybrid** | `29.5%` | `658,069` | `136.4` | `5.0` / `8.0` | `4.7` / `0.0` / `0.0` / `1.1` | `13 / 12 / +1` | `74 / 92` |

## Trajectory Root-Cause Analysis (RQ2)

The authors classify every instance where an MCP workflow diverges from Baseline in task outcome or token efficiency into concrete root-cause categories:

1. **Why MCP Wins**:
   - **Flow localization** (`Callgraph` and `Deps`): Tracing caller/callee chains and module boundaries directly surfaces cross-file sanitizer gaps and bug triggers (`12/17` Callgraph wins on LinuxFLBench; `12/18` Callgraph wins on SecBench).
   - **Direct symbol lookup** (`AST`): Jumping straight to symbol spans accounts for `12/17` AST wins on LinuxFLBench and `12/28` on SWE-bench Pro.
   - **Doc-guided navigation** (`Docs`): Matching issue phrasing against docstrings drives `12/17` Docs wins on LinuxFLBench and `13/25` on SWT-bench.
   - **Multi-view localization** (`Hybrid`): Combining symbol inspection with flow tracing accounts for `17/17` wins on LinuxFLBench and `13/28` on SWT-bench.
2. **Why MCP Loses**:
   - **Correct localization, wrong patch**: On SWE-bench Pro and SWT-bench, the vast majority of losses (`16/24` to `23/33` on SWE-bench Pro; `19/21` to `27/29` on SWT-bench; `8/9` to `12/15` on SecBench) occur even though the agent edited the *exact same target file* as the successful Baseline run. Having the agent inspect isolated symbol snippets or caller lists without surrounding file context leads to incomplete edits or weaker test assertions.
   - **Distractor symbols & false flow**: On LinuxFLBench, losses stem from distractor symbols with similar names (`9/11` AST losses), false call chains (`8/9` Callgraph losses), coupling noise (`8/11` Deps losses), and misleading comments (`8/9` Docs losses).
3. **Why MCP Saves or Overspends Tokens**:
   - **Read displacement** is the primary driver of savings (`72/115` to `109/109` fewer-token runs on LinuxFLBench; `115/181` to `188/190` on SWE-bench Pro), supplemented by **Shorter bash loop** (`38–64` runs on SWE-bench Pro).
   - **Four systematic overspend modes**: (a) **Map overhead** when a bug is trivial for Baseline to locate in 1–2 commands (`23–36` runs on LinuxFLBench; `64–78` on SecBench), (b) **Over-exploration** under `Docs` when natural-language doc searches return tangential matches (`20/37` overspent runs on LinuxFLBench, reaching `27.7x` Baseline tokens on instance `11391`), (c) **Verbatim-source explosion** under `Hybrid` when `inspect_symbol` returns full function bodies alongside metadata (`42/72` overspent runs on SWE-bench Pro), and (d) **Generic/popular symbol name** queries under `Deps` (`51/63` overspent runs on SWE-bench Pro).

## Why Not a Skill?

This paper is an empirical benchmark evaluation comparing six fixed representation configurations across four software engineering tasks rather than proposing an algorithmic procedure that an agent can execute step-by-step on demand. Its actionable value for Praxis lies in **architectural tool-routing and context-budget rules**—specifically, matching MCP code representations to task requirements (e.g., routing security patching to call-graph tools, test generation to docstring/specification tools, and fault localization to multi-view indices, while avoiding uncurated `Hybrid` dumps during subtle patch synthesis). These quantitative decision criteria are captured in [skill-system-design.md](../rules/skill-system-design.md) and complement the escalation-oriented search patterns in the `cost-effective-repo-exploration` skill.
