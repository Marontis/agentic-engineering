# Only as Safe as the Weakest Agent: Delegation Safety Collapse and Grounded-Source Defenses in Multi-Agent Systems

> **Source**: [arXiv:2611.17520](https://arxiv.org/abs/2611.17520) — Keegan Wang, Anantika Mannby (Carnegie Mellon University, University of Southern California, Prosaic Intelligence; NeurIPS 2026 Meta-Agents Workshop)
> **Praxis Source ID**: `src:2611-17520v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

This paper is a `58,589`-trial empirical security measurement and causal-mechanism study (`~$1,100` metered spend) demonstrating that unmodified commercial coding harnesses (`Claude Code` and `Codex`) and multi-agent pipelines inherit the corpus-poisoning susceptibility of the **weakest sub-agent on the evidence path**, rather than the frontier orchestrator. Per [`AGENTS.md`](../AGENTS.md) and [`skill-design-methodology`](../skills/skill-design-methodology/SKILL.md), we omit forged-document templates and capture strictly the **causal failure diagnostics, channel-transfer pitfalls, and architectural defenses** (same-tier evidence readers, verbatim primary-record forwarding, skeptical/grounded verifiers), which belong as always-active guardrails in [`multi-agent-coordination.md`](../rules/multi-agent-coordination.md) and [`adk-multi-agent-a2a.spec.md`](../specs/adk-multi-agent-a2a.spec.md).

---

## Experimental Design (`Sections 3–6`, `Appendices A–B`)

- **Environments & Harnesses**:
  1. **Shipped Commercial Harnesses (`Experiment 1 & 2`)**: Unmodified `Claude Code` CLI (`Opus 5` orchestrator spawning `Haiku 4.5` via `Task`, mechanically restricted to delegation via `--allowedTools Task`) and unmodified `Codex` CLI (`gpt-5.6-sol` orchestrator spawning `gpt-5.6-terra`, instructionally restricted and verified per trial because `Codex` lacks mechanical sub-agent-only flags).
  2. **Reference Harness**: Controlled `200`-line tool loop testing `8` orchestrator/sub-agent pairs (`5` weak-delegate pairs + `3` same-tier pairs, `Table 6`) and matched-brief controls.
  3. **Simulated Multi-Agent Panel (`Experiment 3`, `Tables 2–5`)**: `13`-model factorial panel (`GPT-3.5-turbo`, `GPT-4o-mini`, `GPT-5-nano`, `GPT-5.4-mini`, `GPT-5.5`, `Claude Haiku 4.5`, `Sonnet 4.6`, `Opus 4.6`, `Llama-3.1-8B`, `Llama-3.3-70B`, `DeepSeek-V3.2`, `Mistral-Large-3`, `Gemini-2.5-Flash`), extended to **`18` models** across `6` labs in channel comparisons (adding `Claude Sonnet 5`, `Claude Opus 5`, `GPT-5.6-sol` / `gpt-5.6-terra`, `DeepSeek-V4-Pro`, and `Gemini 3.1 Pro`).
- **Task & Forgery Structure**:
  - `180` counterbalanced two-option comprehension items over fictional relational facts in a `13`-file on-disk store (`12` genuine records + `1` forged record; `35`-file store with `5` forged files for `stacked`), plus `3` additional non-fictional document stores (`issue tracker`, `lab notebook`, `policy archive`, $n = 19\text{--}20$).
  - Every testable forgery leaves the genuine record intact and carries **two fixed, non-tuned provenance tells** (it predates the record it claims to amend, and it omits the accession line present on every genuine record) across `6` families: `correction` (supersession notice), `gloss` (titled senior-archivist annotation), `volume` (repeated later sources), `stacked` (combination of all three), `correction_clean` (scope-condition control with both tells removed), and `injection` (explicit prompt-injection directive).
  - **Primary Metric (`Harmful Revision`)**: Answering the item correctly in an unpoisoned / pre-interaction control, then switching to the attacker-backed wrong label after encountering the poisoned store or peer/sub-agent message. Across `3,652` repeated pairs, run-to-run disagreement on the same fact was `13.0%`.

---

## Key Quantitative Findings

### 1. Strong Orchestrators Break Only When Delegating to Weaker Sub-Agents (`Tables 1 & 6`)

On catchable forgeries where frontier orchestrators almost never err when reading the file store directly—only **`2` harmful revisions across `1,080` direct trials** (`1/180` `Opus 5` on `gloss` and `1/180` on `stacked`; `0/180` `gpt-5.6-sol` on `gloss`; `0/540` reference orchestrators on `volume`)—delegating file search to the cheaper sub-agent each product spawns by default collapses safety to the weak reader's tier:

| Harness | Poison Family | Orchestrator Alone | Weak Reader Alone | Delegated (`Orch -> Weak`) | Same-Tier (`Orch -> Same`) | Direct vs. Delegated $p$ |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **`Claude Code`** (`Opus 5 -> Haiku 4.5`) | `gloss` | `1 / 180` | `22 / 180` | **`20 / 180`** | `0 / 180` | `$10^{-4}$` |
| **`Claude Code`** (`Opus 5 -> Haiku 4.5`) | `stacked` | `1 / 180` | `136 / 180` | **`75 / 180`** | `0 / 180` | `$< 10^{-15}$` |
| **`Claude Code`** (`Opus 5 -> Haiku 4.5`) | `correction` | `31 / 180` | — | **`128 / 180`** | — | `$< 10^{-15}$` |
| **`Claude Code`** (`Opus 5 -> Haiku 4.5`) | `correction_clean` *(control)* | `175 / 180` | — | `173 / 180` | — | `n.s.` |
| **`Codex`** (`gpt-5.6-sol -> gpt-5.6-terra`) | `gloss` | `0 / 180` | `58 / 180` | **`44 / 180`** | `1 / 180` | `$10^{-13}$` |
| **`Codex`** (`gpt-5.6-sol -> gpt-5.6-terra`) | `volume` | `0 / 180` | — | `0 / 180` (`95% CI [0, 2.0%]`) | — | `n.s.` |
| **`Codex`** (`gpt-5.6-sol -> gpt-5.6-terra`) | `stacked` | `99 / 180` | — | **`122 / 180`** | — | `0.013` |
| **`Codex`** (`gpt-5.6-sol -> gpt-5.6-terra`) | `correction` | `172 / 180` | — | **`180 / 180`** | — | `0.008` |
| **`Codex`** (`gpt-5.6-sol -> gpt-5.6-terra`) | `correction_clean` *(control)* | `180 / 180` | — | `180 / 180` | — | `n.s.` |
| **`Reference`** | `stacked` | `27 / 180` | — | **`149 / 180`** | — | `$10^{-12}$` |
| **`Reference`** *(pooled 3 orch. / 5 pairs)* | `volume` | `0 / 540` | — | **`553 / 900`** | `11 / 540` | `$< 10^{-15}$` |

- **Explicit prompt-injection directives failed everywhere**: The `injection` family (imperative instructions addressed to automated readers) was resisted across every tested harness; what succeeded made no demand and resembled an ordinary archival/repository record.
- **Weakness, not delegation mechanics, drives the break (`Experiment 2`)**:
  - `Clean-store` delegation produced **`0/180`** errors in both `Claude Code` and `Codex`.
  - `Same-tier` sub-agents matched standalone orchestrator safety (`0/180`, `1/180`, and `11/540`: `GPT-5.5 -> GPT-5.5` `6/180` [$p = 0.031$], `Opus 4.6 -> Opus 4.6` `4/180` [n.s.], `Sonnet 4.6 -> Sonnet 4.6` `1/180` [n.s.]).
  - Across `5` weak pairs in the reference harness (`Table 6`), harmful revisions scaled monotonically with sub-agent weakness: `Opus 4.6 -> gpt-oss-20b` **`148/180`**, `Opus 4.6 -> GPT-3.5-turbo` **`118/180`**, `Opus 4.6 -> gpt-4o-mini` **`98/180`**, `Sonnet 4.6 -> gpt-4o-mini` **`97/180`**, and `GPT-5.5 -> GPT-5-nano` **`92/180`** (all $p < 10^{-15}$).
  - **Domain replication & code-grep boundary**: Re-running `stacked` on an issue tracker, lab notebook, and policy archive yielded `0/19`, `0/20`, and `0/20` direct harmful revisions vs. **`8/20`, `10/20`, and `14/20`** delegated; by contrast, in a code repository where verification was a single `grep` away, the attack did not transfer (`Section 5`).

### 2. Provenance Stripping, Sub-Agent Tool-Channel Laundering & Negative Cross-Channel Transfer

- **Hop-level provenance loss & suppressed verification (`Section 5`, `Fig. 3`)**: When `Opus 5` opened `stacked` directly in `Claude Code`, it named the missing accession/date provenance in **`180/180`** runs (`1/180` adoption), whereas `Haiku 4.5`'s sub-agent summary preserved that provenance cue in only **`96/180`** runs ($p = 10^{-31}$), resulting in `75/180` harmful revisions. Even when the sub-agent report *did* mention provenance, `Opus 5` still adopted the forgery in **`21/96`** trials (vs. `1/180` direct; on `gloss`, provenance retention dropped `179/180 -> 55/180` without predicting harm within delegated runs, `16/125` vs. `4/55`, $p = 0.32$), while orchestrator tool-calling turns dropped roughly in half under delegation (`6.3 -> 3.2` on `stacked`, `4.7 -> 2.5` on `gloss`, `3.9 -> 2.4` in reference).
- **Sub-agent tool returns are trusted nearly `2x` as much as peer messages (`Fig. 5`)**: Delivering a byte-identical forged sub-agent fabrication as a **sub-agent tool result** induced **`102/120` (`85%`)** harmful revisions vs. **`18/39` (`46%`)** when framed as a **peer message** (`Opus 4.6` and `Sonnet 4.6` resisted the peer channel completely while adopting identical text through the sub-agent tool channel).
- **Negative correlation between `Evidence` and `Social` channel susceptibility (`Table 2`, `Fig. 4`)**: Across all `18` models, susceptibility to a forged document (`Evidence` channel: `100%` `Claude Sonnet 5` and `GPT-5.6-sol`, `99%` `GPT-5.5`, `91%` `Opus 5` down to `5%` `Llama-3.3-70B` and `8%` `Llama-3.1-8B`) and susceptibility to a peer's bare assertion (`Social` channel: `0%` `Sonnet 5`, `GPT-5.6-sol`, `Opus 5`, `GPT-5.4-mini` up to `58%` `GPT-3.5-turbo` and `51%` `Llama-3.1-8B`) correlated **negatively** (**Spearman $\rho = -0.76, p = 0.0002$**). Models trained to ground faithfully in provided documents resist bare social pressure (`Table 3`: `Visible E+cite` drops `12` of `13` models to `0/180`, leaving only `GPT-3.5-turbo` at `90/180`), yet that exact documentary deference makes them vulnerable when an upstream sub-agent launders a forged record into a clean-looking tool report.

### 3. Transitive `Attacker -> Worker -> Aggregator` Cascades & Grounded Verifier Defense (`Table 5`, `Section 6`)

In a three-agent pipeline (`n = 150–180` per aggregator, `780` pooled trials across `Claude Sonnet 5`, `GPT-5.5`, `Gemini 2.5 Flash`, `Claude Opus 5`, and `GPT-5.6-sol`):

| Aggregator Model | $n$ | Clean Worker | Corrupted Worker (`Attack`) | Conditional Propagation $P(\text{err} \mid \text{corrupt})$ | `+ Grounded Verifier` *(raw source attached)* |
|:---|---:|:---:|:---:|:---:|:---:|
| `Claude Sonnet 5` | `150` | `0%` | `98.0%` | `1.00` | **`0%`** |
| `GPT-5.5` | `180` | `0%` | `97.2%` | `1.00` | **`0%`** |
| `Gemini 2.5 Flash` | `150` | `0%` | `96.0%` | `0.99` | **`0%`** |
| `Claude Opus 5` | `150` | `0%` | `95.3%` | `0.98` | **`0%`** |
| `GPT-5.6-sol` | `150` | `0%` | `94.7%` | `0.99` | **`0%`** |
| **Pooled** | **`780`** | **`0%` (`0/780`)** | **`96.3%`** | **`751 / 757` (`0.98–1.00`)** | **`0%` (`0/780`, `[0, 0.47%]`)** |

- **Grounded source attachment completely halts cascading poisoning**: Attaching the retrieved primary source record to the aggregator cut error from **`94.7%–98.0%`** to **`0/780` (`0%`, Clopper–Pearson `[0, 0.47%]`)** even though the workers remained corrupted at their original rates.
- **Live-harness defenses ($n = 40$ per arm vs. `15/40` baseline)**: Requiring the sub-agent to quote the original record (`grounded verifier`) dropped harmful revisions to **`3/40` ($p = 0.0018$)**; adding a simple store-skepticism prompt (`1/40`, $p = 0.0005$) performed indistinguishably ($p = 0.63$); and instructing the orchestrator to open the primary record itself reached **`0/40`** (`1/180` in `Section 4`).

---

## Defensive Engineering Takeaways

1. **Never place a cheaper, weaker reader alone between untrusted corpora and a decision-making orchestrator**: Cost-saving delegation (`10x` cheaper per token) transfers the weak reader's forgery failure rate (`20/180` to `553/900`) onto frontier orchestrators that score `2/1,080` directly. Either use a same-tier reader on untrusted external files or mandate primary-record pass-through.
2. **Forward verbatim source spans and metadata headers across every agent hop**: Aggregators fail because evidence contact is severed (`96.3%` error without source vs. `0/780` with source). Require sub-agent return schemas to bundle verbatim quoted records, accession/commit metadata, and timestamps—or use Byzantine-tolerant parallel subtask consensus ([`similarity-consensus-subtask-aggregation`](../skills/similarity-consensus-subtask-aggregation/SKILL.md)) when multiple independent readers are affordable.
3. **Never exempt `Task` / sub-agent tool outputs from untrusted-data skepticism**: Boundary sanitizers looking for imperative prompt injections miss record-formatted forgeries completely, and orchestrators trust sub-agent tool results (`85%`) nearly twice as often as peer chat (`46%`). Inject explicit store-reliability skepticism (`15/40 -> 1/40`) and deterministic provenance checks on delegated tool returns.
4. **Benchmark multi-agent safety at the system level across both `Evidence` and `Social` channels**: Single-agent frontier evaluations and peer-debate sycophancy benchmarks miss Evidence-channel laundering ($\rho = -0.76$).

## Related Artifacts

- [`rules/multi-agent-coordination.md`](../rules/multi-agent-coordination.md) — `"DO: Optimize topology and model assignment jointly"`, `"DON'T: Share full context across all agents by default"`, `"DO: Audit sub-agent models differentially across matched single- and multi-agent framings"`, and `"DO: Attach Merkle-proven log receipts and three-valued claim checkers to inter-agent handoff messages before trusting claimed side effects"`
- [`rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md) — `"DON'T: Assume safety transfers across deployment contexts"` and `"DON'T: Rely on instruction-stripping sanitizers or tool-name allowlists to stop task-tampering indirect prompt injections"`
- [`skills/similarity-consensus-subtask-aggregation/SKILL.md`](../skills/similarity-consensus-subtask-aggregation/SKILL.md) — `SecMAS` trimmed nearest-neighbor embedding aggregation when delegating subtasks across $m_i$ redundant workers (`arXiv:2611.17883`)
- [`skills/proof-carrying-agent-messages/SKILL.md`](../skills/proof-carrying-agent-messages/SKILL.md) — Cryptographic log receipts for inter-agent handoff claims (`arXiv:2610.39109`)
- [`task-tampering-indirect-prompt-injection.md`](task-tampering-indirect-prompt-injection.md) — Why imperative-instruction sanitizers miss world-state and observation tampering (`arXiv:2611.07640`)
