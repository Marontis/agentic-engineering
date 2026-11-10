# Tracing MCP Security Vulnerabilities: Constructing and Analyzing an MCP Security Vulnerability Dataset

> **Source**: [arXiv:2611.11104](https://arxiv.org/abs/2611.11104) — Xu He, Sagar Patel, Shu Wang (2026)
> **Praxis Source ID**: `src:2611-11104v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

This paper constructs a curated vulnerability dataset of `24` validated Model Context Protocol (MCP) CVEs (frozen February 2026 snapshot), performs a multi-dimensional empirical breakdown across severity, CWE classes, affected stack layers, and root causes, and presents six defensive CVE case studies. Because its contribution is an empirical vulnerability measurement study and reproducible CVE curation dataset rather than a standalone reusable agent procedure—and its implementation-hardening takeaways complement existing MCP skills ([`mcp-server-design`](../skills/mcp-server-design/SKILL.md), [`mcp-zero-trust-tool-authorization`](../skills/mcp-zero-trust-tool-authorization/SKILL.md), and [`mcp-tool-hijacking-defense`](../skills/mcp-tool-hijacking-defense/SKILL.md))—it belongs as a research brief paired with defensive rule updates.

---

## Dataset Construction & Acronym Disambiguation (`Section III`)

Naive keyword searches for `"MCP"` in public vulnerability feeds suffer severe acronym collision across semiconductor packaging, Linux kernel drivers, industrial control systems, and healthcare. Starting from CVE disclosures between January 2025 and February 2026 matching `"MCP"` or `"Model Context Protocol"`, the authors apply a three-stage filtering pipeline:

1. **Initial Retrieval & Deduplication**: `119` raw CVE records $\to$ `108` valid records after removing duplicates and `RESERVED` or `REJECTED` entries.
2. **Stage 1 — AI/LLM Context Verification**: Retains only records explicitly referencing Model Context Protocol in an AI/LLM context (servers, clients, agents), excluding **`72` records (`66.7%`)** and leaving `36`.
3. **Stage 2 — Component Association**: Verifies direct association with a concrete MCP server, client, SDK, or MCP-integrated platform rather than passing mentions, removing `8` entries and leaving `28`.
4. **Stage 3 — Completeness & Confirmation**: Removes `4` unconfirmed or incomplete records, producing a frozen snapshot of **`24` validated MCP vulnerabilities** (`paper_stats.json`).

On a manual audit of `30` sampled excluded records reviewed by two independent researchers, the filtering workflow achieved **`96.7%` inter-rater agreement** while retaining all high-severity MCP disclosures cross-referenced against Anthropic, JFrog, Trend Micro, and GitHub Security Advisories.

---

## Multi-Dimensional Vulnerability Landscape (`Section IV`, `Tables I & III`)

### 1. Severity & Temporal Concentration (`Section IV-A`)
- **Severity Breakdown**: **`14` Critical (`58.3%`)**, **`7` High (`29.2%`)**, **`2` Medium (`8.3%`)**, and **`1` Low (`4.2%`)**—yielding an **`87.5%` (`21/24`) Critical/High rate**, amplified by the privileged local filesystem, repository, database, and API access held by MCP processes.
- **Temporal Caveat**: `20/24` source records provide only year-level disclosure dates (`14` normalized to `2025-01-01` alongside a date-precision flag, followed by `1` in September 2025, `2` in December 2025, and `7` in January 2026).

### 2. Vulnerability Types & Stack Distribution (`Section IV-B`, `Table I`)

| Vulnerability Type | Count (`n = 24`) | Share | Primary CWE | Typical Stack Layer |
|:---|:---:|:---:|:---|:---|
| **Command Injection** | `7` | `29.2%` | `CWE-77`, `CWE-78` | Server, Client, SDK |
| **Path Traversal** | `5` | `20.8%` | `CWE-22` | Server |
| **Remote Code Execution (RCE)** | `4` | `16.7%` | `CWE-94` | Client, Server |
| **Unauthorized Access** | `2` | `8.3%` | `CWE-306`, `CWE-862` | Server, Client |
| **DNS Rebinding** | `2` | `8.3%` | `CWE-346` | SDK, Server |
| **ReDoS** | `1` | `4.2%` | `CWE-1333` | SDK |
| **Cross-Site Scripting (XSS)** | `1` | `4.2%` | `CWE-79` | Client |
| **Hardcoded Credentials** | `1` | `4.2%` | `CWE-798` | SDK |
| **Other** | `1` | `4.2%` | `N/A` | Server |

- **Dominant Trio**: Command injection (`7`), path traversal (`5`), and RCE (`4`) together account for **`66.7%` (`16/24`)** of all validated MCP CVEs.
- **Component Split**: **`11` (`45.8%`)** affect **MCP servers**, **`8` (`33.3%`)** affect **MCP clients**, and **`5` (`20.8%`)** affect **MCP SDKs**:
  - *Server bugs* are predominantly classic software-level command-injection, RCE, and path-traversal flaws directly exploitable via structured JSON arguments without requiring LLM prompt injection (e.g., Anthropic's `mcp-server-git` accounts for `3` Critical CVEs: `CVE-2025-68143`, `CVE-2025-68144`, `CVE-2025-68145`).
  - *Client bugs* emerge at integration and trust-broker boundaries—such as `Orval` OpenAPI-to-MCP code generation (`CVE-2026-22785`, `CVE-2026-23947`), `Dive` desktop host deeplink configuration tampering (`CVE-2026-23523`), and `LibreChat` permissive command execution (`CVE-2026-22252`).
  - *SDK bugs* carry the widest ecosystem blast radius because a single flaw in a shared dependency—such as the MCP TypeScript SDK (`CVE-2025-66414`, `CVE-2026-0621`) or `Arcade MCP` (`CVE-2025-66454`)—propagates to every downstream adopter.

### 3. Overlapping Root-Cause Chain (`Section IV-C`, `Table III`)
- **Insufficient Input Validation (`IV`)**: **`18/24` (`75.0%`)** pass client-supplied parameters or external specifications directly to shell commands, filesystem path resolvers, code generators, or regex parsers without sanitization.
- **Inadequate Access Control (`AC`)**: **`4/24` (`16.7%`)** defer authentication or confirmation for setup convenience (`CVE-2025-8943` in Flowise, `CVE-2025-66454` hardcoded shared secrets in Arcade MCP, `CVE-2026-23523` low-friction deeplinks in Dive, and `CVE-2026-22252` in LibreChat, which overlaps `IV` and `AC`).
- **Protocol-Level Security Gaps (`PG`)**: **`3/24` (`12.5%`)** stem from transport and parser hardening omitted by the baseline MCP specification (`CVE-2025-66414` and `CVE-2025-9611` HTTP DNS rebinding; `CVE-2026-0621` RFC 6570 `UriTemplate` ReDoS, overlapping `IV` and `PG`).

---

## Six Defensive Case Studies & Remediation Lessons (`Sections V–VI`, `Table II`)

| CVE ID | Layer | Vulnerability Class | Root-Cause Pattern | Verified Defensive Fix |
|:---|:---|:---|:---|:---|
| `CVE-2025-68144` | Server (`mcp-server-git`) | Command Injection (Critical) | Structured JSON tool arguments in `git_diff` / `git_checkout` forwarded into Git CLI invocations without flag/shell sanitization | Eliminate shell interpolation; invoke library APIs or parameterized `execve`-style interfaces with strict allowlists (fixed in `2025.12.17` / MITRE ref `2025.12.18`) |
| `CVE-2025-68145` | Server (`mcp-server-git`) | Path Traversal (Critical) | Incomplete validation of `repo_path` against `--repository` sandbox prior to normalization | Canonicalize filesystem paths first, then enforce containment against the canonical root (`>= 2025.12.17`) |
| `CVE-2026-22785` | Client (`Orval`) | Command Injection | Unescaped OpenAPI `summary` metadata spliced into generated MCP code strings at build time | Treat third-party OpenAPI specs and tool metadata as untrusted; escape literals or emit AST-safe code (`>= 7.18.0`; `>= 8.0.2` covers both Orval CVEs) |
| `CVE-2026-23523` | Client (`Dive`) | Unauthorized Access | Crafted deeplinks installed or replaced trusted MCP server configurations without sufficient user confirmation | Gate trust-establishing config changes (deeplinks, imports, discovery) behind explicit human approval (`>= 0.13.0`) |
| `CVE-2025-66414` | SDK (MCP TypeScript SDK) | DNS Rebinding (High) | Local HTTP transport shipped without `Host` validation or DNS rebinding protection, exposing `127.0.0.1` services via short-TTL domains | Enable DNS rebinding protection, `Host` header validation, and per-session IP pinning on local HTTP transports (`>= 1.24.0`) |
| `CVE-2026-0621` | SDK (MCP TypeScript SDK) | ReDoS (High) | Catastrophic regex backtracking in `UriTemplate` when parsing RFC 6570 exploded array patterns | Replace backtracking regexes on protocol strings with linear-time purpose-built parsers (`>= 1.25.1`) |

---

## Relevance to Praxis

- **Software-Layer vs. Prompt-Layer MCP Risk**: Demonstrates that `66.7%` of early MCP CVEs are traditional `CWE-77/78/94/22` software flaws—and `54.2%` (`13/24`) reside in clients or SDKs (`33.3%` + `20.8%`), including static build-time codegen (`Orval`) and local HTTP transport (`DNS rebinding`)—meaning prompt-injection defenses alone leave MCP deployments exposed unless paired with software-level input canonicalization, shell-free subprocess execution, local HTTP `Host`/rebinding checks, and SDK dependency pinning.
