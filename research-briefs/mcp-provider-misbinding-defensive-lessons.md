# When Tool Names Are Not Identities: Defensive Lessons on Provider Misbinding in MCP Agents

> **Source**: [arXiv:2611.21577](https://arxiv.org/abs/2611.21577) — Zeynab Anbiaee, Sajjad Dadkhah, Ali A. Ghorbani (*When Tool Names Are Not Identities: Measuring Provider Misbinding in MCP-Based AI Agents*, Canadian Institute for Cybersecurity, University of New Brunswick, Nov 2026)
> **Praxis Source ID**: `src:2611-21577v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

Per [`AGENTS.md`](../AGENTS.md), this paper is captured strictly for its **defensive provider-identity and namespace-resolution lessons**, omitting attacker metadata-generation prompt recipes. Furthermore, the study is a controlled $2 \times 3 \times 2$ factorial security measurement benchmark (`12` metadata alignment conditions across `5` LLM clients) rather than an empirical implementation of a defense protocol: while it motivates signed tool manifests, schema hashes, and verified provider-bound identifiers $\operatorname{attr}^+(t) = \{n(t), d(t), \sigma(t), m(t), p(t)\}$, it does not build or benchmark a defensive gateway. Its findings strengthen MCP identity and namespace guardrails in [`rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md).

---

## Threat Model & Factorial Measurement Design (`§III–§V`)

**Tool-provider misbinding** occurs in multi-server MCP composition when a benign user request intended for a legitimate server's capability ($t_L \in \mathcal{T}_L$, exemplified by `data_fetch_and_store(dataset_id, destination)`) resolves instead to a tool advertised by a separate untrusted MCP server ($\mathcal{T}_A^{(v,r)}$) **without** compromising the host, client, LLM, network transport, or legitimate server, and **without** embedding imperative prompt-injection overrides.

Across **`5` LLM clients** (`GPT-5.4`, `Claude Sonnet 5`, `Gemini 2.5 Pro`, `Qwen3.7 Max`, `DeepSeek V3`), the primary experiment crosses **`Name`** $\in \{\text{unrelated}, \text{exact}\}$ $\times$ **`Description`** $\in \{\text{unrelated}, \text{copied}, \text{authority-enhanced}\}$ $\times$ **`Schema`** $\in \{\text{incompatible}, \text{compatible}\}$ (`12` conditions `C01–C12`, candidate budget $r = 1$, $P = 10$ benign prompts [`5` ordinary + `5` security-aware emphasizing the trusted destination/provider] $\times N = 5$ repetitions = **`50` trials per model-condition cell**, failure rate $\mathrm{FR} = 0$ everywhere):

- **Metrics**: **Violation Rate (`VR`)** $= A / (A+L+C+F)$ (direct wrong-provider execution), **Clarification Rate (`CR`)** $= C / (A+L+C+F)$ (unresolved provider ambiguity stalling automation; non-legitimate rate $1 - \mathrm{LSR} = \mathrm{VR} + \mathrm{CR}$ when $\mathrm{FR} = 0$), and **Resolved Binding Stability (`RBS`)** across the $N - 1 = 4$ consecutive trial pairs per prompt (`Eqs. 8–14`).
- **Robustness Suites (`§VI`)**: (1) `5` independent keyword-excluded unrelated names across `C01–C06` (`250` trials/cell, `Table III`), (2) `5` independent authority-enhanced descriptions (`D1–D5`) across `C05, C06, C11, C12` (`250` trials/cell, `Table IV`), and (3) candidate multiplicity $r \in \{1, 3, 5, 10\}$ across `C07–C12` (`Table V`).
  - *Internal manuscript discrepancy note*: `Table V(a)`/`(b)` re-runs an independent $r = 1$ baseline for the budget sweep that differs slightly from `Table II` (`r = 1` main factorial) in two cells: `C07` on `GPT-5.4` (`VR = 0.02` in `Table II` vs `0.04` in `Table V(a)`) and `C10` on `Gemini 2.5 Pro` (`VR/CR = 0.84 / 0.16` in `Table II` vs `0.88 / 0.12` in `Table V`). Both exact figures are preserved below.

---

## Key Empirical Findings for Defenders (`§V–§VI`)

### 1. Attribute Interaction & Schema Compatibility (`Δ_schema`) Drive Misbinding (`Table II`)

| Condition (`Name` / `Desc.` / `Schema`, $r=1$, $50$ trials/cell) | `GPT-5.4` (`VR/CR/RBS`) | `Claude Sonnet 5` (`VR/CR/RBS`) | `Gemini 2.5 Pro` (`VR/CR/RBS`) | `Qwen3.7 Max` (`VR/CR/RBS`) | `DeepSeek V3` (`VR/CR/RBS`) |
|:-----------------------------------------------------------------|:-----------------------:|:-------------------------------:|:------------------------------:|:---------------------------:|:---------------------------:|
| **`C01–C03, C05`** (Low-alignment / incompatible controls) | `0.00 / 0.00 / 1.00` | `0.00 / 0.00 / 1.00` | `0.00 / 0.00 / 1.00` | `0.00 / 0.00 / 1.00` | `0.00 / 0.00 / 1.00` |
| **`C04`** (`Unrelated` / `Copied` / `Compatible`) | `0.00 / 0.00 / 1.00` | `0.00 / 0.00 / 1.00` | `0.00 / 0.00 / 1.00` | `0.00 / 0.00 / 1.00` | **`0.22`** `/ 0.00 / 0.65` |
| **`C06`** (`Unrelated` / `Authority` / `Compatible`) | `0.04 / 0.00 / 0.90` | `0.00 /` **`0.22`** `/ 0.68` | **`0.42 / 0.56`** `/ 0.35` | **`0.20`** `/ 0.00 / 1.00` | **`0.50`** `/ 0.00 / 0.68` |
| **`C07`** (`Exact` / `Unrelated` / `Incompatible`) | `0.02 / 0.00 / 0.97` | `0.00 / 0.02 / 0.97` | `0.00 / 0.20 / 0.78` | `0.00 / 0.00 / 1.00` | `0.00 / 0.00 / 1.00` |
| **`C08`** (`Exact` / `Unrelated` / `Compatible`) | `0.12 / 0.00 / 0.85` | `0.00 / 0.22 / 0.75` | **`0.60 / 0.22`** `/ 0.42` | **`0.40`** `/ 0.00 / 0.65` | **`0.28`** `/ 0.00 / 0.65` |
| **`C09`** (`Exact` / `Copied` / `Incompatible`) | `0.00 / 0.00 / 1.00` | `0.00 / 0.22 / 0.78` | `0.00 / 0.46 / 0.42` | `0.00 / 0.00 / 1.00` | `0.00 / 0.00 / 1.00` |
| **`C10`** (`Exact` / `Copied` / `Compatible`) | **`1.00`** `/ 0.00 / 1.00` | `0.06 /` **`0.94`** `/ 0.00` | **`0.84`** `/ 0.16 / 0.78` | **`1.00`** `/ 0.00 / 1.00` | **`1.00`** `/ 0.00 / 1.00` |
| **`C11`** (`Exact` / `Authority` / `Incompatible`) | `0.04 / 0.00 / 0.90` | `0.00 / 0.24 / 0.68` | `0.02 / 0.52 / 0.23` | `0.18 / 0.00 / 0.82` | **`0.56`** `/ 0.00 / 0.57` |
| **`C12`** (`Exact` / `Authority` / `Compatible`) | **`0.96`** `/ 0.00 / 0.90` | **`0.26 / 0.74`** `/ 0.08` | **`0.70 / 0.30`** `/ 0.65` | **`1.00`** `/ 0.00 / 1.00` | **`1.00`** `/ 0.00 / 1.00` |

- **Exact-name collision alone is near-inactive (`C07`), whereas schema compatibility (`Δ_schema`) is the decisive amplifier**: Moving from `C09` (exact name + copied description + incompatible schema: **`VR = 0.00` across all `5` models**) to `C10` (compatible schema) jumps `5`-model mean `VR` from `0.00` to **`~0.78`** (`+1.00` on `GPT-5.4`, `Qwen3.7 Max`, and `DeepSeek V3`; `+0.84` on `Gemini 2.5 Pro`) and drives total non-legitimate outcomes (`1 - LSR`) to **`1.00` (`100%`) across all `5` models**—including the `5` security-aware user prompts explicitly naming the trusted destination/provider.

### 2. Unique Tool Names / Server Prefixes Alone Do Not Prevent Provider Misbinding (`C06`, `Tables III–IV`)

- Even with **completely unrelated tool names** sharing zero task keywords (`C06`), pairing compliance/verification authority cues with a compatible input schema triggers substantial wrong-provider execution or ambiguity across **`250`-trial robustness pools**:
  - **5-Name Pool (`Table III`, `C06`)**: `DeepSeek V3` `VR = 0.696` (`95%` Wilson CI `[0.636, 0.750]`), `Gemini 2.5 Pro` `VR = 0.460` (`[0.399, 0.522]`) + `CR = 0.528` (**`98.8%` non-legitimate**), `GPT-5.4` `VR = 0.248` (`SD = 0.248`, `[0.199, 0.305]`), `Qwen3.7 Max` `VR = 0.204` (`[0.159, 0.258]`), and `Claude Sonnet 5` `VR = 0.000` + `CR = 0.224`. (`DeepSeek V3` also hits `VR = 0.184` in `C04` with copied description + unrelated name.)
  - **5-Description Pool (`Table IV`, `C06` & `C12`)**: `C06` sustains `VR = 0.508` (`DeepSeek V3`), `0.408` + `0.564` `CR` (`Gemini 2.5 Pro`), `0.204` (`Qwen3.7 Max`), `0.036` (`GPT-5.4`), and `0.208` `CR` (`Claude Sonnet 5`); `C12` reaches `VR = 0.980` (`GPT-5.4`), `1.000` (`Qwen3.7 Max`, `DeepSeek V3`), `0.720` + `0.280` `CR` (`Gemini 2.5 Pro`), and `0.256` `VR` + `0.744` `CR` (`Claude Sonnet 5`).
- **Defensive implication**: Rejecting duplicate tool names (`UserError`) or prepending `<server_id>__<tool_name>` converts `C10`/`C12` collisions into `C04`/`C06` distinct-name candidates—leaving **`20%–70%` wrong-provider execution** open unless the client enforces provider-to-capability authorization!

### 3. Model Clarification (`CR`), Binding Stability (`RBS`), and Candidate Multiplicity ($r \in \{1,3,5,10\}$, `Table V`)

- **Model caution is not provider binding, and stability is not safety**: `Claude Sonnet 5` reduces silent execution (`VR = 0.06` in `C10`, `0.26` in `C12`) only by stalling automated workflows (`CR = 0.94` and `0.74`, **`0%` automatic legitimate resolution**), while `RBS = 1.00` on `GPT-5.4`, `Qwen3.7 Max`, and `DeepSeek V3` in `C10` reflects **100% deterministic binding to the untrusted provider**.
- **Candidate multiplicity amplifies partial-alignment conditions (`Table V`)**: Scaling untrusted candidates from $r = 1$ to $r = 10$ pushes `Qwen3.7 Max` in `C08` from `VR = 0.40` to `0.86` ($r=3$), `0.88` ($r=5$), and **`1.00` ($r=10$)**; raises `GPT-5.4` `VR` from `0.04 -> 0.28` (`C07`), `0.12 -> 0.30` (`C08`), `0.00 -> 0.34` (`C09`), and `0.04 -> 0.34` (`C11`); raises `Claude Sonnet 5` `VR` in `C10` (`0.06 -> 0.16`) and `C12` (`0.26 -> 0.42`) while driving `CR` to **`1.00`** in `C09`/`C11`; and shifts `Gemini 2.5 Pro` in `C10` from clarification (`CR 0.12 -> 0.06`) to direct violation (`VR 0.88 -> 0.92`; note non-monotonic redistribution on `DeepSeek V3` in `C08` `0.28 -> 0.00` and `C11` `0.56 -> 0.00`).

---

## Relevance to Praxis

- **Rules**: Extends MCP tool-identity and namespace guardrails in [`rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md)—requiring deterministic host-level `(capability_class -> verified_provider_id)` allowlists, cryptographic manifest signing, and provider-verified `RBS` evaluation alongside `<server_id>__<tool_name>` prefixing.
- **Related Artifacts**: [`mcp-tool-hijacking-defense`](../skills/mcp-tool-hijacking-defense/SKILL.md), [`mcp-zero-trust-tool-authorization`](../skills/mcp-zero-trust-tool-authorization/SKILL.md), [`mcp-tool-poisoning-cross-framework-study`](mcp-tool-poisoning-cross-framework-study.md), and [`shadowbench-mcp-routing-shadow-invocations`](shadowbench-mcp-routing-shadow-invocations.md).
