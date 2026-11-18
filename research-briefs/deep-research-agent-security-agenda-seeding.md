# Security of Deep Research Agents: Attack Surface, Defense Assumptions, and Agenda Seeding

> **Source**: [arXiv:2611.20045](https://arxiv.org/abs/2611.20045) — Yang Luo, Guangpu Chen, Yichen Liu, Zhaoyu Chen, Yifeng Gao, Zhiyang Ding, Qingni Shen, Zhonghai Wu (Peking University, 2026)
> **Praxis Source ID**: `src:2611-20045v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

This paper combines a **`34`-study Systematization of Knowledge (`SoK`)** on Deep Research (`DR`) and agentic search security (plus `88` adjacent RAG-poisoning, prompt-injection, and Generative Engine Optimization [`GEO`] studies) with a **`3,520`-run controlled empirical study** demonstrating **agenda seeding**—an instruction-free planning/integration attack where web pages introduce a fictitious evaluation criterion rather than commanding the AI or promoting a target directly—and showing that every tested single-layer defense either fails (`0` mitigation), degrades clean research utility (`-13.8` to `-23.8` pp), or is bypassed by a `2`-domain adaptive attacker (`p = 0.5`). Per [`AGENTS.md`](../AGENTS.md) (`lines 69–70`), we omit offensive bait-authoring templates and capture this work strictly as a **defensive Research Brief** + a load-bearing **`DON'T:` guardrail in [`rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md)**.

---

## Four-Stage Threat Model & `34`-Study Literature Systematization (`Jan 2023 – Sep 2026`)

Unlike closed-corpus single-turn RAG (`user-authored query`) or side-effecting Web agents (`DOM actions`), DR agents (`STORM`, `Co-STORM`, `OmniThink`, `WebThinker`, `OpenAI` / `Gemini` / `Perplexity Deep Research`) execute tens to hundreds of recursive `Retrieval (R) -> Planning (P) -> Evidence Integration (I) -> Report Generation (G)` loops across five trust boundaries (`B1` user–agent, `B2` agent–open web/search, `B3` result-slot/query-log observers, `B4` evidence-to-planning feedback & sub-agent delegation, `B5` cited report–consumer) and seven attacker capability tiers (`C0` natural reference fabrication, `C1` publish own pages, `C2` edit high-ranking third-party/UGC pages, `C3` control search result slots, `C4` malicious user queries, `C5` passive query/network observer, `C6` search/crawler/MCP supply-chain intermediary).

Coding **`34` primary empirical studies** (`18` attack, `6` benchmark, `5` defense, `5` measurement; `29/34` [`85.3%`] from 2025–2026; `Tables 7–8`) exposes five structural blind spots:
1. **Planning is the least-studied stage (`26.5%`, `9/34`)**: Retrieval (`50.0%`, `17/34`), Evidence Integration (`55.9%`, `19/34`), and Report Generation (`50.0%`, `17/34`) dominate; only `5/34` (`14.7%`) span `>= 3` stages, and **prior to this paper `0/34` studied `Planning x Ranking Promotion`**, even though DR planners write `100%` of follow-up queries from previously read pages.
2. **Over-concentration on `C1` new-page publishing (`67.6%`, `23/34`)**: Only `3` studies test `C2` edits to already-retrieved UGC (`WARP` [`arXiv:2605.24245`]: `~13` edited words retrieved in `57%–76%` of runs and cited in `38%–51%` of reports), `2` test `C3` per-turn result-slot injection, `2` test `C5` query/traffic confidentiality (`MosaicLeaks` [`1,001` tasks] showing stronger agents pack more private context into outbound queries; network domain-sequence fingerprinting), `1` (`2.9%`) tests cost/wallet draining (`Agent-Fence`), and **`0/34` test `C6` search/crawler supply-chain tampering** or **agent-targeted cloaking** (serving poisoned text to agent user-agents and clean pages to human citation checkers) or **end-to-end poisoning on commercial DR products** (`55.9%` [`19/34`] simulated, `32.4%` [`11/34`] live non-poisoning, `4/34` sandbox).
3. **Misaligned single-layer defense assumptions (`Table 4`, `14/34` evaluate defenses, `5/34` [`14.7%`] defense papers)**:
   - *Source-level* authority scoring assumes authoritative domains are unpolluted (broken by `C2` UGC/wiki edits).
   - *Content-level* instruction/data separation (`Spotlighting`, `StruQ`, `SecAlign`, `DataSentinel`, `MELON`) assumes payloads contain imperative instructions (broken by instruction-free data manipulation, factual distraction [`Lazy Grounding`, `-5.9` pp accuracy using purely true facts], and persuasive rewrites where perplexity/safety filters get `0%` recall).
   - *Integration-level* majority/cluster aggregation (`RobustRAG`, `TrustRAG`) assumes retrieved evidence is mostly benign and single-round (broken by `HAE-GEO` multi-page **corroboration traps** and `Breadcrumbing` per-turn slot injection).
   - *Planning/system-level* pre-read control-flow locking (`CaMeL`, `FIDES`, `Progent`, `IsolateGPT`) can gate external write side effects, **not** data-dependent research sub-questions, while *generation-level* citation verification (`ALCE`) checks claim-to-source entailment rather than source truthfulness (**citation laundering**, compounded by ~`50%` baseline citation-support rates in generative search).

---

## Controlled Empirical Study: Instruction-Free Agenda Seeding (`3,520` Sandboxed Runs)

Across `20` consumer categories with `5` fictitious brand models and `4` preset buying criteria per category (eliminating parametric memory; `Best` leads `3/4` criteria, `Target` ranks `#3` and leads `0/4`), a `STORM`/`WebThinker`-style `3`-round DR agent (`3` initial + `2–3` follow-up queries/round, BM25 top-`4`, `300–500`-word cited report + `RANKING` / `TOP PICK`) was evaluated across `Qwen3.8-Flash` (`2` samples/cat), `DeepSeek-V4.1-Flash` (`2` samples/cat), and `Kimi-K3` (`1` sample/cat) on **Dense (`18` benign pages/cat = `360` indexed pages)** and **Sparse (`6` benign pages in target category)** corpora under an identical **`3`-page / `3`-domain `C1` attacker budget** (`Tables 9–10`, paired run-by-run via cached pre-exposure calls):

### 1. Reframing Evaluation Criteria Beats Direct `GEO` and Prompt Injection (`Table 9`, `n = 100` Pooled Runs/Cell)

| Corpus | Attack Condition (`3` pages / `3` domains) | `Qwen` Top-1 | `DeepSeek` Top-1 | `Kimi` Top-1 | Pooled `Target` Top-1 | `Best` Top-1 (Utility) | Mean `Target` Rank | Attacker Read / Cited | Planning Hijack | Metric Adopted |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Dense** (`18` benign) | `Clean` | `0.0%` | `0.0%` | `0.0%` | **`0.0%`** | **`100.0%`** | `3.07` | n/a | `0.0%` | `0.0%` |
| **Dense** | `GEO` (claims target is best) | `0.0%` | `0.0%` | `0.0%` | **`0.0%`** | `98.0%` | `3.04` | `100% / 100%` | `0.0%` | `0.0%` |
| **Dense** | `GEO + injection` (adds AI directive) | `10.0%` | `0.0%` | `5.0%` | **`5.0%`** ($p \ge .06$) | `94.0%` | `2.95` | `100% / 98%` | `0.0%` | `0.0%` |
| **Dense** | **`Agenda seeding`** (1 mainstream bait + 2 metric pages; 0 instructions) | **`22.5%`** | **`2.5%`** | **`30.0%`** | **`16.0%`** ($p < 10^{-4}$) | **`80.0%`** | **`2.62`** | `99% / 97%` | **`72.0%`** | **`96.0%`** |
| **Sparse** (`6` benign) | `Clean` | `0.0%` | `0.0%` | `0.0%` | **`0.0%`** | **`100.0%`** | `3.02` | n/a | `0.0%` | `0.0%` |
| **Sparse** | `GEO` | `7.5%` | `5.0%` | `5.0%` | **`6.0%`** ($p = .031$) | `93.0%` | `2.89` | `100% / 99%` | `0.0%` | `0.0%` |
| **Sparse** | `GEO + injection` | `2.5%` | `0.0%` | `0.0%` | **`1.0%`** ($p \ge .06$) | `98.0%` | `2.95` | `100% / 99%` | `0.0%` | `0.0%` |
| **Sparse** | **`Agenda seeding`** | **`47.5%`** | **`7.5%`** | **`30.0%`** | **`28.0%`** ($p < 10^{-4}$) | **`64.0%`** | **`2.39`** | `100% / 100%` | **`88.0%`** | **`99.0%`** |

- **Why `GEO` stalls while `Agenda Seeding` succeeds**: Direct `GEO` and `GEO + injection` pages are read (`100%`) and cited (`98%–100%`) yet contradicted by `6–18` benign pages on the `4` standard criteria (`<= 6.0%` Top-1, `<= 8.0%` Top-2). Agenda seeding's mainstream-aligned bait guide never names the target product—it only introduces an "overlooked" fictitious metric (e.g., *Transient Load Stability Index*), prompting the planner to actively query that metric in Rounds `2–3` (`72.0%` Dense / `88.0%` Sparse hijack rate; `53%` first read metric pages via follow-up queries and `40%` in Round 1 on Dense vs. `82%` Round 1 on Sparse) and adopt it in `96%–99%` of reports (pushing `Target` into Top-2 in `24.0%` Dense / `35.0%` Sparse and improving mean rank across `75%` of `40` category-corpus cells by `+0.50` positions vs. `28%` and `+0.09/+0.12` for `GEO`/injection). Restricting to `1` search round halved Dense flips (`12.5% -> 6.2%`, adoption `95.0% -> 65.0%`), and removing the bait page lowered `Qwen + DeepSeek` flips (`12.5% -> 10.0%` Dense; `27.5% -> 18.8%` Sparse, Best drop $p = 0.035$).
- **Model divergence is post-adoption (`E3`)**: `DeepSeek-V4.1-Flash` wrote the fabricated metric into **`100%`** of its reports yet ranked `Target` Top-2 in only **`7.5%`** of runs (vs. **`48.8%`** `Qwen3.8-Flash` and **`35.0%`** `Kimi-K3`), refusing to let an uncorroborated criterion override `3/4` mainstream criteria.

### 2. Evaluation of Four Defense Layers (`Table 10`, `Qwen + DeepSeek` Pooled `n = 160`/Cell + `Kimi` Dense `n = 20`)

| Layer & Defense | Clean `Best` Top-1 | Injection `Target` Top-1 | Seeding `Target` Top-1 | Seeding `Best` Top-1 | Seeding Hijack | Adaptive 2-Domain Seeding `Target` Top-1 | Clean Tokens / Run | `Kimi` Dense Seeding |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `None` | `100.0%` | `3.1%` | `20.0%` | `73.1%` | `75.6%` | `18.8%` | `10.4k` | `30.0%` |
| **Content**: `Injection detection` | `100.0%` | **`0.0%`** (`0/11` Top-2, $p < .001$) | **`20.0%`** (`0` flagged) | `73.1%` | `75.6%` | n/a | **`17.6k` (`+69%`)** | `30.0%` |
| **Planning**: `Root-query anchoring` (`text-embedding-v4` 10th-pct $\tau$) | `100.0%` | `1.9%` | **`20.0%`** | `75.0%` | `54.4%` | n/a | `10.3k` | `30.0%` |
| **Integration**: `Verification prompting` | **`86.2%`** ($p < 10^{-6}$; `DS` `76.2%`) | `1.2%` | **`8.8%`** ($p < .001$) | **`66.2%`** | `56.9%` | **`6.9%`** | `10.7k` | **`0.0%`** |
| **Lineage**: `Provenance tagging` (single-site concept lineage) | **`100.0%`** (`3.8%` false tag) | `3.1%` | **`15.0%`** (`0` vs `8`, $p = .008$) | `78.1%` | `74.4%` | **`17.5%`** (`0` vs `2`, $p = .5$) | `10.5k` | `25.0%` |

1. **Injection detection (`+69%` token cost) has `0%` recall on agenda seeding**: Blocks `100%` of instruction-bearing pages (`0` benign FPs) and `0%` of instruction-free agenda-seeding pages (`20.0%` unchanged).
2. **Embedding root-query anchoring leaves conclusions unchanged (`20.0%`)**: Metric queries overlap heavily with clean follow-up queries (`0.42` vs. `0.60` median cosine similarity), dropping only `39.2%` of metric queries at a `9.1%` clean-query drop rate while Round-1 retrievals still expose metric pages.
3. **Verification prompting cuts `Target` flips (`20.0% -> 8.8%`) by inducing abstention rather than recovery**: Loses the true `Best` pick in `22/160` clean runs (`100.0% -> 86.2%`, `DeepSeek` `76.2%`) and lowers `Best` under attack (`73.1% -> 66.2%`) because **`12.5%` of clean runs and `22.5%` of seeded runs output no `TOP PICK` at all**.
4. **Single-site provenance tagging preserves `100.0%` clean utility (`20.0% -> 15.0%`, $p = 0.008$) but triggers on only `21.2%` of runs and is bypassed by `2`-domain bait (`18.8% -> 17.5%`, $p = 0.5$)**: Counting distinct hostnames is defeated by one extra attacker domain (`corroboration trap`).

---

## Defensive Design Takeaways

1. **Anchor evaluation criteria to the user brief or pre-retrieval baseline**: Separate *factual lookup* from *decision-rubric mutation*—do not let newly discovered criteria introduced mid-search override user-specified or baseline domain criteria without explicit user confirmation or out-of-band provenance attestation.
2. **Verify publisher/temporal independence, not raw domain counts, and audit rendered outbound links + query privacy**: Pair criterion-lineage tracking with publisher/link/registration-age independence checks, strip auto-loaded external images/links in rendered reports (`output-channel exfiltration`), re-fetch cited URLs from an independent vantage point (`agent-targeted cloaking`), sanitize private entities from outbound search queries (`MosaicLeaks`), and enforce hard token/round budgets (`wallet draining`).

## Related Artifacts

- [`covert-tool-injection-defense`](../skills/covert-tool-injection-defense/SKILL.md) — Instruction-bearing tool-output quarantine (complementary layer for `GEO + injection`, `0.0%` top-pick rate).
- [`challenge-aware-knowledge-recruitment`](../skills/challenge-aware-knowledge-recruitment/SKILL.md) — Non-answering gap diagnosis for multi-round retrieval (`arXiv:2611.05393`).
- [task-tampering-indirect-prompt-injection](task-tampering-indirect-prompt-injection.md) — Non-imperative world-state and decision-rule tampering bypassing instruction sanitizers (`arXiv:2611.07640`).
- [debate-to-deceive-fact-checking-poisoning](debate-to-deceive-fact-checking-poisoning.md) — Adversarial evidence crafting against automated fact-checking pipelines (`arXiv:2611.09123`).
- [`rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md) — Guardrails on untrusted web/tool ingestion and benign-arm defense evaluation.
