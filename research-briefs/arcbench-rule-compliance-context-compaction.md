# Do Agents Still Follow the Rules? Benchmarking Rule Compliance under Agent Context Compaction

> **Source**: [arXiv:2611.03223](https://arxiv.org/abs/2611.03223) — Yiwei Zha, Qingyu Meng, Herbert Bos, Min Chen (VUSec, Vrije Universiteit Amsterdam, 2026-11-02)  
> **Praxis ID**: `src:2611-03223` | **Code**: `https://github.com/VUAISec/ARCBench`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Core Contribution

Long-horizon tool-using agents rely on **context compaction** (summarizing or dropping older turns) to stay within context limits or reduce token spend. While prior benchmarks evaluate whether compaction preserves task utility and factual recall, **ARCBench** (`17` English task cases across `4` OWASP Agentic Security boundaries, `10,369` judged summaries, and `1,115` judged violating runs across `4` models) is the first benchmark to isolate how context compaction degrades **rule compliance**.

The paper uncovers a critical two-stage failure mechanism:
1. **Compaction-induced compliance loss is not merely a forgetting problem**: Under default `Hermes` compaction at a `750`-token budget, case-level `violation@3` jumps from `9.6%` (`13/135` cases) in full context to `37.8%` (`51/135` cases) after compaction (`28.9%` violating *only* after compaction). Even when the compacted summary **fully retains** the safety or operational rule (`70.1%` of runs), the run-level violation rate more than doubles from `8.1%` (full context) to `21.1%` ($2.6\times$), rising to `29.4%` when partially retained and `83.3%` when absent.
2. **Authority and salience flattening**: Behavioral attribution shows that in `21.6%` of compaction-induced violations where the rule was fully retained, the agent explicitly acknowledges the rule in its reasoning and still executes the forbidden tool call (`acknowledged`), and in `27.0%` it treats the summarized rule as unregistered background (`unregistered`), compared to `3.4%` and `17.2%` in full context. Moving a rule from a direct user prompt or authoritative policy document into a third-person reference summary strips its conversational authority.

---

## Experimental Scope & Methodology

- **Harness & Task Suite**: Built on the open-source `pi` coding-agent harness (`commit 97fa14e3`, $T=0.7$, seed `7`, retained tail target `50` estimated tokens). Each case runs in three phases: Phase 1 delivers a specific operational rule (`8` personal-assistant cases `p1`–`p8` and `9` organizational cases `o1`–`o9` across OWASP `Data`, `Access`, `Action`, and `Control` boundaries); Phase 2 runs multi-turn distractor workspace tasks (`4`–`5` steps, plus `96,000`-char volume padding in `S4`/`S5`); Compaction compresses the history before Phase 3; Phase 3 issues a natural trigger prompt whose naive completion violates the Phase 1 rule.
- **Models (`4`, used for both agent and compactor)**: `deepseek/deepseek-v4-flash-0731` (`DeepSeek`), `z-ai/glm-5.3-flash` (`GLM`), `qwen/qwen3.7-flash` (`Qwen`), and `~openai/gpt-luna-latest` (`GPT-Luna`).
- **Evaluation Matrix (`S1`–`S7`)**:
  - `4` rule delivery channels (`S2`): `c1` direct user instruction, `c2` user instruction persisted via `write("rule.md")`, `c3` document-embedded policy read via tool call, `c4` dedicated `get_policy` tool call.
  - `10` compaction strategies (`S3`): `7` generative (`Pi`, `Pi + RP`, `Structured`, `ACON-UT`, `ACON-UTCO`, `TRACE`, `Hermes`) and `3` selective (`FIFO`, `LRU (rule)`, `LRU (LLM)`).
  - `5` token budgets (`S4`): `200`, `300`, `750`, `1,200`, and `2,500` tokens.
  - `6` compactor-targeted prompt injections (`S5`–`S6`: `legacy`, `naive`, `escape`, `ignore`, `fake completion`, `combined`) and `4` compactor defenses (`S7`: `isolation`, `instructional`, `sandwich`, `rule preservation`).

---

## Key Quantitative Findings

### 1. Baseline Rule Retention vs. Compliance (`S1`, `Hermes`, `750` Tokens)

| Model | Full Context `violation@3` | Compacted `violation@3` | Agent's Own | Only After Compaction | Rule Retained / Partial / Absent | Full Context Run VR | Retained-Rule Run VR |
|:------|:--------------------------:|:-----------------------:|:-----------:|:---------------------:|:--------------------------------:|:-------------------:|:--------------------:|
| `DeepSeek` (`34` cases) | `8.8%` | `26.5%` | `8.8%` | `17.6%` | `98.0%` / `2.0%` / `0.0%` | `6.9%` | `17.0%` |
| `GLM` (`34` cases) | `8.8%` | `29.4%` | `8.8%` | `20.6%` | `98.0%` / `2.0%` / `0.0%` | `7.8%` | `16.0%` |
| `GPT-Luna` (`33` cases) | `6.1%` | `33.3%` | `6.1%` | `27.3%` | `48.5%` / `45.5%` / `6.1%` | `4.0%` | `20.8%` |
| `Qwen` (`34` cases) | `14.7%` | `61.8%` | `11.8%` | `50.0%` | `35.3%` / `58.8%` / `5.9%` | `13.7%` | `47.2%` |
| **All (`135` cases)** | **`9.6%`** | **`37.8%`** | **`8.9%`** | **`28.9%`** | **`70.1%` / `26.9%` / `3.0%`** | **`8.1%`** | **`21.1%`** |

-Even on `DeepSeek` and `GLM`, which retain the full rule in `98.0%` of compacted summaries, case-level `violation@3` triples (`8.8%` $\to$ `26.5%` and `29.4%`) and run-level violations on retained-rule runs more than double (`6.9%` $\to$ `17.0%` and `7.8%` $\to$ `16.0%`).

### 2. Delivery Channels (`S2`) and Compaction Strategies (`S3`)

- **Delivery channels (`S2`)**: Organizational rules (`c3`, `c4`) achieve `0.0%` `violation@3` in full context across all `4` models, but jump to `30.6%` (`c3`, `65.7%` retained, `16.9%` retained run VR) and `22.2%` (`c4`, `71.3%` retained, `11.7%` retained run VR) after compaction. Writing a personal rule to `rule.md` (`c2`) lowers full-context `violation@3` from `25.0%` (`c1`) to `16.1%` and compacted `violation@3` from `56.3%` to `45.2%`, because agents rarely re-read `rule.md` unless prompted.
- **Generative vs. Selective Compaction (`S3`)**:
  - **Generative strategies (`468` cases)** average `91.2%` rule retention (`7.8%` partial, `0.9%` absent) and `21.8%` compacted `violation@3` (vs `12.0%` full context).
  - **Selective strategies (`203` cases)** (`FIFO`, `LRU (rule)`, `LRU (LLM)`) drop the early rule turn in `84.1%` of runs (`15.9%` retained) and reach `50.2%` compacted `violation@3` (`51.5%` for `FIFO` with `0.0%` retention, `54.4%` for `LRU (rule)` with `11.8%` retention, `44.8%` for `LRU (LLM)` with `36.3%` retention).
  - **Template structure matters**: Adding a dedicated `<Constraint & Rules>` section to `Pi` (`Pi + RP`) achieves `99.0%` full retention (`0.0%` absent) and reduces compacted `violation@3` to `9.0%` (`6.5%` run VR vs `9.5%` full context). Conversely, `ACON-UT` retains `96.0%` of rules in free-form prose yet suffers `31.8%` `violation@3` (`21.1%` retained run VR), and `Hermes` suffers `42.6%` `violation@3` (`69.6%` retained, `27.0%` partial).

### 3. The Token-Budget Truncation Cliff (`S4`)

- On `DeepSeek` and `GLM` under `Hermes + Volume`, rule retention is `100.0%` at `2,500` tokens (`28.1%` `violation@3`), `97.1%` at `1,200` tokens (`26.5%`), and `98.0%` at `750` tokens (`24.2%`).
- At `300` tokens, full retention collapses from `98.0%` to `2.9%` (`95.1%` absent; `47.1%` `violation@3`), and at `200` tokens it hits `0.0%` (`100.0%` absent; `50.0%` `violation@3`).
- **Mechanism**: The `Hermes` wrapper prepends a fixed `177`-token reference-only preamble before the summary body; at `200`–`300` token budgets (leaving only `64`–`126` summary tokens after the `50`-token tail), the preamble consumes the budget and truncates the trailing sections where rules reside.

### 4. Compactor-Targeted Prompt Injection & Defenses (`S5`–`S7`)

- **Tag-escape injection (`S6`, `GLM` + `Hermes`, $k=6$)**: Closing the `<conversation_to_summarize>` tag early (`escape`) drives `violation@6` from `23.5%` (no attack) to `58.8%` (run VR `15.7%` $\to$ `30.4%`), cutting rule retention from `96.1%` to `66.7%` (`19.6%` absent) and doubling retained-rule run VR from `13.3%` to `26.5%`.
- **Defenses (`S7`, under `escape`)**: `Isolation` (`41.2%` `violation@6`, `85.3%` retained), `Instructional` (`41.2%`, `87.3%` retained), and `Sandwich` (`52.9%`, `82.4%` retained) only partially mitigate the attack. **`Rule preservation`** (adding an explicit `<Constraint & Rules>` field to `Hermes`) restores `99.0%` full retention (`0.0%` absent) and cuts `violation@6` from `58.8%` to `29.4%` (`15.7%` run VR, `15.8%` retained run VR). However, under `S5` (`legacy` injection across all `4` models), even `Pi + RP` sees `violation@3` double from `9.0%` to `17.9%` despite `99.5%` rule retention.

---

## Why Not a Skill?

`ARCBench` is an empirical measurement benchmark evaluating failure modes of existing compaction strategies rather than introducing a new multi-step algorithmic workflow beyond our existing context-management skills (`prefix-preserving-context-assembly` and `agent-working-memory-eval`). Its concrete engineering prescriptions — dedicating an explicit `<Constraint & Rules>` schema section near the top of compaction templates, enforcing a summary budget floor above fixed wrapper preambles, and enforcing hard security boundaries outside the compacted prompt — are best captured as always-active rules in `output/rules/agent-sandbox-safety.md` and `output/rules/skill-system-design.md`.
