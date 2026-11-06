# MCP-Eco: A Linked Dataset of MCP Servers, Consumers, and Development Activity

> **Paper**: [MCP-Eco: A Linked Dataset of MCP Servers, Consumers, and Development Activity](https://arxiv.org/abs/2611.06897) (Tounoussi, Sayagh, Ouni & Kashiwa, ÉTS Montréal & NAIST, 2026)
> **Praxis source**: `src:2611-06897v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Classification: Research Brief (Ecosystem Dataset & Empirical Infrastructure)

`MCP-Eco` (`arXiv:2611.06897`) releases a frozen relational dataset (`2026-06-23 UTC`, `16,880,899` records across `19` Parquet tables, publicly hosted on Hugging Face under `CC BY 4.0`) that connects the two sides of the Model Context Protocol (`MCP`) software ecosystem: **candidate server implementations** and **consuming repositories** that configure or integrate them, linked together with their **multi-year GitHub development histories** (`pull requests`, `reviews`, `issues`, `commits`, and `coding-agent contribution signatures`) and **dual-channel capability observations** (`Glama` directory metadata vs live protocol probing).

---

## Problem & Motivation

Prior empirical studies and datasets of the MCP ecosystem—such as Hasan et al.'s maintainability/security study of `1,899` servers (`arXiv:2506.13538`) and tool-description smell taxonomy (`arXiv:2602.14878`), `MCPCorpus` (`~14,000` servers and `300` clients, `arXiv:2506.23474`), `MCPZoo` (`arXiv:2512.15144`), and Guo et al.'s measurement of `8,060` servers and `341` clients (`arXiv:2509.25292`)—suffer from three structural blind spots:
1. **Protocol Clients vs Adopting Repositories**: Existing datasets catalog protocol client/host implementations rather than the downstream software projects that actually configure and consume MCP servers via host configuration files (`claude_desktop_config.json`, `.mcp.json`, `.cursor/mcp.json`, `cline_mcp_settings.json`).
2. **Single-Point Metadata Without Evolution History**: Snapshot repository metadata omits the pull requests, code reviews, issues, and commits through which MCP servers and their adopters evolve and resolve breaking interface changes.
3. **Single-Channel Capability Lists**: Recording tool/resource/prompt definitions from only a static directory listing or only a runtime probe prevents systematic comparison between *advertised* capabilities and *live observed* protocol responses.

---

## Five-Stage Collection & Linkage Pipeline

1. **Stage 1 — Discovering Candidate Servers (`78,302` servers)**:
   - **Directories (`5`)**: Official MCP registry, `Glama`, `Smithery`, `PulseMCP` APIs, plus `MCP.so` sitemaps (`65,233` rows in `server_registry_listings`).
   - **Package Registries (`6`)**: `npm` (`mcp`, `mcp-server`, `model-context-protocol`), `PyPI`, `NuGet`, `crates.io`, `Maven Central`, and `Docker Hub` (`mcp/` namespace), yielding `45,272` launch commands and connection endpoints in `mcp_server_transports`.
   - **Code Search**: GitHub queries (`mcpName` in `server.json`, `startCommand`/`runtime` in `smithery.yaml`) and Sourcegraph SDK import queries. Normalized repository URLs merge duplicates while retaining `discovery_source`. Root manifest parsing (`package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`, `go.mod`, `pom.xml`) extracts **662,693** declared dependencies (`server_dependencies`).
2. **Stage 2 — Observing Capabilities (`source = glama | probe`)**:
   - Capabilities are stored with uniqueness enforced per `(server_id, source)`, allowing direct side-by-side comparison of directory claims (`source='glama'`, scraped from `/schema` subpages) against live protocol handshakes (`source='probe'`, preferring streamable HTTP/SSE over `stdio` and calling `initialize` followed by `tools/list`, `resources/list`, and `prompts/list`).
   - Captures **284,845** tool records (`mcp_tools` with JSON input schemas), **20,795** resource records (`mcp_resources` with URIs, MIME types, descriptions), and **8,983** prompt records (`mcp_prompts` with argument metadata).
3. **Stage 3 — Discovering Consuming Repositories (`16,165` repos, `45,529` signals)**:
   - Queries GitHub code search for `mcpServers` in host config files (`claude_desktop_config.json`, `mcp.json`, `cline_mcp_settings.json`, `.cursor/`) and Sourcegraph for client SDK/adapter imports (`from mcp import ClientSession`, `MultiServerMCPClient`).
   - Assigns an evidence-backed `consumer_type` label: `ai_user` (parsed declarations or host-config signals), `ai_builder` (client code or framework-adapter signals), `both`, `sdk_unconfirmed`, or `unknown`, plus `is_also_server` when a server repository also consumes MCP servers.
4. **Stage 4 — Parsing & Matching Configuration Declarations (`9,200` declarations $\to$ `5,975` resolved)**:
   - Fetches `12` fixed configuration file paths from default branches, parsing each `mcpServers` JSON entry into `repo_server_usage` (`9,200` declarations recording command, arguments, and path-derived client type).
   - Matches declarations to candidate servers via package identifiers, endpoint URLs, or server names (recorded in `match_method`): **5,975 declarations (64.9%) resolve to 5,138 distinct repository–server pairs**, while `3,225` remain unresolved (`server_id = NULL`).
5. **Stage 5 — Harvesting Development & Coding-Agent Activity (`22,750` repos with activity)**:
   - Uses `Perceval` (`GitHub REST API`, items updated since the MCP launch on `2024-11-25`) across the **13,966** GitHub-hosted server candidates with $\ge 10$ stars at discovery and all **16,165** consuming repositories, plus `PyDriller` for commit history.
   - Tags consumer pull requests with autonomous coding-agent signatures (following Li et al. `arXiv:2507.15003` plus `Jules` and `Codegen` in `relevance_signal`) and GitHub `Bot` account flags.

---

## Complete Relational Inventory (`16,880,899` Records Across `19` Tables)

| Table Block | Table Name | Exact Record Count | Primary / Join Keys |
|:------------|:-----------|-------------------:|:--------------------|
| **Server Candidates & Capabilities** | `mcp_registries` | `7` | `registry_id` |
| | `mcp_servers` | `78,302` | `server_id` |
| | `server_registry_listings` | `65,233` | `server_id`, `registry_id` |
| | `mcp_server_transports` | `45,272` | `server_id` |
| | `mcp_tools` | `284,845` | `server_id`, `source` (`probe` \| `glama`) |
| | `mcp_resources` | `20,795` | `server_id`, `source` |
| | `mcp_prompts` | `8,983` | `server_id`, `source` |
| | `server_dependencies` | `662,693` | `server_id` |
| **Consuming Repositories** | `consumer_repos` | `16,165` | `repo_id` |
| | `repo_discovery_signals` | `45,529` | `repo_id` |
| **Configuration Declarations** | `repo_server_usage` | `9,200` | `repo_id`, `server_id` (nullable; `5,975` resolved $\to$ `5,138` pairs) |
| **Associated Development Activity** | `commits` | `9,336,613` | `commit_hash`, `repository_url` |
| | `server_pull_requests` | `1,610,439` | `pr_id`, `server_id` |
| | `client_pull_requests` | `121,161` | `pr_id`, `repo_id` |
| | `pr_reviews` | `620,151` | `review_id`, `pr_id` |
| | `pr_review_comments` | `300,883` | `review_id`, `pr_id` |
| | `pr_commit_bridge` | `597,344` | `pr_id`, `commit_hash` |
| | `ecosystem_issues` | `991,441` | `issue_id`, `server_id` or `repo_id` |
| | `issue_comments` | `2,065,843` | `issue_id` |
| **Total** | **`19` Parquet Tables** | **`16,880,899`** | Exported `2026-06-23 UTC` |

---

## Methodological Caveats & Engineering Takeaways

1. **Advertised vs Probed Interface Drift**: Because directory metadata (`source='glama'`) can be stale while live probing (`source='probe'`) covers only servers launchable without credentials or local setup, tool-library builders and empirical studies must filter explicitly by `source` and never treat a missing `probe` row as proof that a server exposes zero capabilities.
2. **Configured Linkage vs Runtime Execution**: `repo_server_usage` (`9,200` rows) measures *declared configuration* in default-branch host files, not runtime invocation frequency, and token-based name matching (`match_method`) can misresolve bare arguments or miss unindexed servers (`35.1%` of declarations remain unresolved).
3. **Cross-Tool Coordination Failures in Issue Histories**: Linking `mcp_tools` to `ecosystem_issues` surfaces real multi-tool coordination bugs—for example, in the `arXiv` MCP server (`search_papers`, `download_paper`, `read_paper`), asynchronous paper conversion interrupted the transition from `download_paper` to `read_paper`.
4. **PII Presence in Public Commit/Issue Records**: The dataset is released with `scrub_pii=false`, retaining public git commit emails, GitHub usernames, and issue/PR text; governance pipelines ingesting `MCP-Eco` must apply PII redaction before feeding raw issue/PR text into model training or prompt contexts.

---

## Why Not a Skill?

This paper is a dataset release and repository-mining infrastructure report (`19` Parquet tables and SQL schema). It does not propose a runtime agent execution algorithm or subtask-level reasoning procedure. Its provenance-tracking and schema-grounding lessons are integrated into `rules/skill-system-design.md` and `rules/agent-evaluation-quality.md`.

---

## Connections to Praxis

- **Skill & Tool Library Design (`rules/skill-system-design.md`)**: Reinforces why MCP tool discovery and dependency induction must distinguish static directory listings (`glama`) from live handshake probing (`probe`) and verify package/version pinning (`package_ver`).
- **MCP Hallucination Guards (`skills/mcp-hallucination-boundary-guards/SKILL.md`)**: Provides the large-scale empirical corpus (`284,845` tool schemas across `78,302` server candidates) illustrating why cross-server schema overlap and asynchronous state transitions (`download_paper` $\to$ `read_paper`) occur in production MCP deployments.
