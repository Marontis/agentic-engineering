# NameTrap: Steering AI Coding Agents Toward Security Vulnerabilities via Variable Names

> **Source**: [arXiv:2610.34253](https://arxiv.org/abs/2610.34253) — Yichen Li, Yifan Zhang, Zexin Wang, et al. (2026)
> **Praxis Source ID**: `src:2610-34253`
> **Category**: Research Brief (Defensive Vulnerability Analysis & Coding Agent Supply-Chain Security)
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Why Not a Skill?

This paper characterizes an offensive semantics-preserving source-code poisoning threat (**NameTrap**) and evaluates why existing pre-completion static analyzers, AI code auditors, and system-prompt security reminders fail to stop it. We do not package offensive vulnerability-steering procedures as skills; instead, this defensive brief documents the threat model, exact vulnerability rates across **6 coding agents** and **10 LLMs**, and the mandatory shift from pre-completion bait scanning to post-completion static/dynamic verification for [`../rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md).

---

## Core Findings

### 1. Threat Model: Identifier-Only Trust-Assumption Poisoning

Unlike indirect prompt injection in comments/docstrings or vulnerable few-shot code snippets, **NameTrap** modifies **only Python identifiers** (function names, variable names, and parameter names) in incomplete third-party repository files while preserving exact program syntax, AST structure, and runtime semantics:

- **Zero Instructions & Zero Pre-Existing Vulnerabilities**: A deterministic AST verifier enforces that the released bait file contains no added comments, strings, or natural-language instructions and **0** vulnerable statements prior to agent completion.
- **Trust-Assumption Naming Conventions Across 4 CWEs**: Across at most $T = 10$ black-box renaming passes on a 200-file benchmark drawn from **31 popular GitHub projects** (47 project–CWE combinations where 10 baseline completions on the unedited file yield **0.0%** vulnerable code), identifiers are renamed to imply false security preconditions:
  - **CWE-78 (OS Command Injection)**: Renaming command-building variables to imply pre-sanitized shell strings or direct shell execution contracts (e.g., steering the agent from `subprocess.run(args, shell=False)` to `shell=True` or `os.system(...)`).
  - **CWE-79 (Cross-Site Scripting / XSS)**: Renaming template or HTML fragments to imply they are already escaped/trusted markup, inducing raw unescaped rendering (`mark_safe`, `|safe`, or disabled autoescaping).
  - **CWE-327 (Use of a Broken or Risky Cryptographic Algorithm)**: Renaming digest helpers to imply legacy checksum or fast-fingerprint compatibility, steering completions toward `hashlib.md5` or `hashlib.sha1`.
  - **CWE-502 (Deserialization of Untrusted Data)**: Renaming payload buffers to imply trusted internal state snapshots, inducing `pickle.loads` or unsafe `yaml.load`.

### 2. Attack Success Rate Across 6 Coding Agents (`Qwen-3.5-27B-AWQ-4bit`)

Tables 1 and 2 compare NameTrap against random identifier renaming, neutral renaming, and the prior semantic-preserving attack **XOXO** (Table 8) across six production coding agent scaffolds using `Qwen-3.5-27B-AWQ-4bit`:

| Coding Agent Scaffold | CWE-78 (Cmd Inj.) | CWE-79 (XSS) | CWE-327 (Weak Crypto) | CWE-502 (Deserial.) | NameTrap Overall (Gross / Parseable) | Random Renaming | Neutral Renaming |
|:----------------------|:------------------|:-------------|:----------------------|:--------------------|:-------------------------------------|:----------------|:-----------------|
| **Aider** | **100.0%** | **63.3%** | 60.0% | 27.5% | **56.0% / 56.0%** | 20.0% | 8.0% |
| **OpenCode** | 32.0% | 30.0% | 60.0% | 24.0% | **30.8% / 30.8%** | 17.7% | 13.1% |
| **mini-swe-agent** | 30.0% | 10.0% | 40.0% | **55.0%** | **26.7% / 26.7%** | 5.6% | 8.0% |
| **Claude Code** | 11.7% | 0.0% | **70.0%** | **55.0%** | **25.0% / 25.0%** | 10.0% | 5.0% |
| **Codex** | 15.7% | 30.0% (37.5%*) | 0.0% | 42.0% | **23.8% / 24.7%*** | 7.1% | 3.9% |
| **OpenHands** | 33.3% | 5.0% | 25.0% (29.4%*) | 20.0% | **22.5% / 23.4%*** | 10.4% | 1.3% |
| **6-Agent Mean (Parseable)** | **37.1%** | **24.3%** | **43.2%** | **37.3%** | **31.1%** | **11.8%** | **6.6%** |

*\*Parseable ASR excludes completions with syntax errors; prior attack XOXO achieves only **2.1%** overall ASR on `Qwen-3.5-27B-AWQ-4bit` ($0.0\%$ CWE-78, $0.0\%$ CWE-79, $10.0\%$ CWE-327, $3.3\%$ CWE-502).*

### 3. Generalization Across 10 LLMs, Prompt Languages, and Cross-Model Transfer

- **10 LLMs Across OpenCode, Claude Code, and Codex (Table 3)**:
  - Overall gross ASR reaches **75.0%** on `Gemma-4-31B` with OpenCode ($90.0\%$ CWE-78, $100.0\%$ CWE-327, $55.0\%$ CWE-502) and **47.5%** on `Gemma-4-26B-A4B` with OpenCode, while `Claude Haiku 4.5` on Claude Code reaches **33.3%** overall (**100.0%** on CWE-502).
  - Across all 10 LLMs (`Qwen-3.5-4B`, `Qwen-3.5-27B-AWQ-4bit`, `Qwen-3.5-122B-A10B-AWQ-4bit`, `Gemma-4-26B-A4B`, `Gemma-4-31B`, `GLM-4.7-Flash`, `DeepSeek-V4-Flash-0731`, `GPT-5.4-mini`, `GPT-5.4-nano`, `Claude Haiku 4.5`), scaffold means are **29.8%** (OpenCode), **21.9%** (Claude Code), and **15.3%** (Codex); CWE means across configurations with bait are **28.2%** (CWE-502), **26.8%** (CWE-327), **18.8%** (CWE-78), and **11.9%** (CWE-79).
- **Non-English Prompts Amplify Vulnerability Steering (RQ3, Table 4)**: Issuing the user's completion request in Traditional Chinese rather than English increases overall gross ASR in **23 of 30** agent–model configurations, raising mean overall gross ASR from **22.3% to 27.7%** (and CWE-78 from $18.8\%$ to $25.8\%$).
- **Zero-Query Cross-Model Transferability (RQ5, Table 5)**: Poisoned bait files generated on one source LLM transfer without re-optimization to other victim LLMs on CWE-78 in **42/81 (51.9%)** cross-model pairs on OpenCode, **66/90 (73.3%)** on Claude Code, and **63/90 (70.0%)** on Codex. In **68/261 (26.1%)** cross-model pairs, transferred bait achieves an even *higher* ASR on the victim model than on the source model used to craft it (e.g., `Qwen-3.5-4B` bait on OpenCode scores $20.0\%$ on itself but **100.0%** on `Qwen-3.5-122B-A10B-AWQ-4bit`; `GPT-5.4-mini` bait on Codex scores $10.0\%$ on itself but **85.0%** on `DeepSeek-V4-Flash-0731`).

### 4. Why Pre-Completion Scanners and System-Prompt Reminders Fail

1. **0.0% Pre-Completion Detection Across 7 Security Analyzers (RQ7, Table 7)**: Because the bait file contains only benign control flow with renamed variables and no sink calls yet, all **4 static analyzers** (`Bandit`, `Semgrep`, `CodeShield`, `CodeQL`) and all **3 AI vulnerability scanners** (`CodeGemma`, `CodeAstra-7B`, `GPT-5.4-mini`) flag **0 of 67 (0.0%)** poisoned bait files.
2. **System-Prompt Security Reminders Do Not Reliably Mitigate Steering (RQ6, Table 6)**: Appending an explicit security instruction (*"Please ensure that the generated code is secure and avoid introducing any CWE vulnerabilities"*) reduces ASR in 13 of 30 configurations, **increases** ASR in 15 configurations, and leaves 2 unchanged—shifting mean overall gross ASR only slightly from **22.3% to 19.2%** while increasing mean CWE-502 ASR from **28.2% to 29.8%**.

---

## Relevance to Praxis

- **Coding Agent Sandbox & Post-Completion Gateways ([`../rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md))**: Pre-execution repository scanning and prompt-level security reminders cannot defend against identifier-level semantic steering because the vulnerability does not exist until the coding agent synthesizes the sink call. Defenses must run static/dynamic CWE analyzers (`CodeQL`, `Semgrep`, `Bandit`) on the **post-completion diff** before committing or executing agent-written code, and optionally normalize local identifiers in untrusted context files before prompt assembly.
- **Complementary Skills**: Combine post-diff static analysis with [`../skills/pre-execution-action-auditing/SKILL.md`](../skills/pre-execution-action-auditing/SKILL.md) and [`../skills/transactional-coding-sandbox/SKILL.md`](../skills/transactional-coding-sandbox/SKILL.md) so any completion introducing CWE-78/79/327/502 sinks is rolled back automatically.

---

## Key Citations

- **Pearce et al. (2022)** — *Asleep at the Keyboard? Assessing the Security of GitHub Copilot's Code Contributions* — Foundational study on LLM code completion CWE vulnerabilities.
- **Yan et al. (2024)** — *XOXO: Semantics-Preserving Code Poisoning* — Prior identifier-renaming baseline outperformed by NameTrap ($2.1\%$ vs. $31.1\%$ mean parseable ASR across 6 coding agents).
