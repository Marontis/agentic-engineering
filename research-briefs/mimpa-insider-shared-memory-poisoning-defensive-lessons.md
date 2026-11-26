# MIMPA: Insider Shared-Memory Poisoning via Successful Collaboration (Defensive Lessons)

> **Source**: [arXiv:2611.31307](https://arxiv.org/abs/2611.31307) — Hyunsoo Ahn, Buru Chang (Korea University, 2026)  
> **Praxis Source ID**: `src:2611-31307v1`  
> **License**: arXiv.org perpetual non-exclusive license  
> **Repository**: Not publicly released at publication

## Why Not a Skill?

Per [`AGENTS.md`](../AGENTS.md) guidance on offensive security papers, this artifact captures strictly the defensive threat-model, mechanism-diagnostic, and memory-governance lessons from `MIMPA` (*Multi-Agent Insider Memory Poisoning Attack*), omitting concrete poisoning prompt templates (`Appendix G`). As the authors note in `Limitations` (`Section 6`), the paper characterizes a structural vulnerability in outcome-gated shared multi-agent memory and evaluates only one post-hoc transcript-auditing defense—leaving constructive write/retrieval provenance enforcement as open design requirements rather than benchmarking a validated standalone defense algorithm.

## Core Vulnerability: Provenance Laundering Through Task Success

Standard multi-agent memory architectures—both **Basic episodic memory** (recording collaboration traces when the final team output is correct and retrieving top-$k$ cosine-similar records via `Qwen3-Embedding-8B`) and **hierarchical `G-Memory`** (`Zhang et al., 2025a`, distilling successful traces into a 3-tier insights/queries/trajectories graph retrieved via `all-MiniLM-L6-v2` + LLM insight synthesis)—treat **task-level team success as a proxy for record trustworthiness**.

`MIMPA` demonstrates why that assumption fails in a `3`-agent, `2`-round debate system (`Du et al., 2024`, Round-2 strict majority vote) where **one regular-privilege peer** has **zero direct write or retriever access** to shared memory (`10` preceding stream tasks + `1` target task, `100` episodes per benchmark, seed `42`):
1. **Selective Planting Without Breaking Current Accuracy**: By selecting $K = 3$ preceding tasks semantically proximate to a target domain (`96.0%` any-hit retrieval rate on `gpt-5.4-nano` and `97.7%` on `Gemma4-31B`, vs. `70.8%` exact uniform random $1 - \binom{7}{3}/\binom{10}{3}$; `Table 9`) and scoping a target-relevant false claim narrowly enough that the planting task's own answer remains **correct**, the insider achieves **`98.8% / 100.0% / 98.5%` storage success** in `Basic` memory and **`95.1% / 98.7% / 94.7%` storage success** in `G-Memory` (`Table 2`, `gpt-5.4-nano` across `MMLU-Pro`, `TruthfulQA`, `MedMCQA`).
2. **Peer-to-Institutional Provenance Laundering**: Once written into shared memory—or distilled into abstract general rules inside `G-Memory`'s insight layer—an unverified peer assertion re-enters future tasks labeled as **"successful past team experience."** Even when the insider is **completely absent from the target task** (`w/o Triggering`: `3` benign agents debating alone!), poisoned memory alone drives high Attack Success Rates (`ASR`).

## Empirical Impact & Stronger-Backbone Paradox

| Backbone & Memory System | Benchmark | Clean Acc (`%`) | Direct `MAC` / `AutoTransform` ASR (`%`) | `MIMPA` Acc (`%`) | `MIMPA` ASR (`%`) | `MIMPA w/o Triggering` ASR (`%`, **Attacker Absent**) | `w/o Poisoned Record` ASR (`%`, Direct Claim Only) |
|:---|:---|---:|---:|---:|---:|---:|---:|
| **`gpt-5.4-nano` — Basic** (`Tables 1, 3`) | `MMLU-Pro` | `83.0` | `2.4` / `3.6` | `52.0` | **`32.5`** | `22.9` | `3.6` |
| **`gpt-5.4-nano` — Basic** | `TruthfulQA` | `83.0` | `18.1` / `14.5` | `16.0` | **`79.5`** | **`60.2`** | `18.1` |
| **`gpt-5.4-nano` — Basic** | `MedMCQA` | `67.0` | `9.0` / `6.0` | `12.0` | **`79.1`** | **`49.3`** | `11.9` |
| **`gpt-5.4-nano` — G-Memory** (`Tables 1, 3`) | `MMLU-Pro` | `81.0` | `6.2` / `1.2` | `63.0` | **`22.2`** | `9.9` | `2.5` |
| **`gpt-5.4-nano` — G-Memory** | `TruthfulQA` | `79.0` | `20.3` / `16.5` | `49.0` | **`34.2`** | `13.9` | `25.3` |
| **`gpt-5.4-nano` — G-Memory** | `MedMCQA` | `76.0` | `7.9` / `7.9` | `41.0` | **`39.5`** | `18.4` | `10.5` |
| **`Gemma4-31B` — Basic** (`Tables 6–7`) | `MMLU-Pro` | `82.0` | `3.7` / `2.4` | **`10.0`** | **`87.8`** | **`48.8`** | `2.4` |
| **`Gemma4-31B` — Basic** | `TruthfulQA` | `94.0` | `2.1` / `4.3` | **`7.0`** | **`92.6`** | **`50.0`** | `2.1` |
| **`Gemma4-31B` — Basic** | `MedMCQA` | `79.0` | `8.9` / `2.5` | **`8.0`** | **`89.9`** | **`64.6`** | `7.6` |
| **`Gemma4-31B` — G-Memory** (`Tables 6–7`) | `MMLU-Pro` | `85.0` | `0.0` / `1.2` | `42.0` | **`49.4`** | `15.3` | `4.7` |
| **`Gemma4-31B` — G-Memory** | `TruthfulQA` | `94.0` | `4.3` / `3.2` | `44.0` | **`53.2`** | `16.0` | `3.2` |
| **`Gemma4-31B` — G-Memory** | `MedMCQA` | `79.0` | `6.3` / `1.3` | `36.0` | **`53.2`** | `19.0` | `6.3` |

### Why Stronger Models Can Be *More* Vulnerable (`Section 5.2–5.3`)
- **Inverse scaling of direct vs. memory-mediated susceptibility**: Moving from `gpt-5.4-nano` to open-weight `Gemma4-31B` (`Table 6`) cuts direct Round-2 peer-persuasion `ASR` (`MAC`, `AutoTransform`, `w/o Poisoned Record`) to **`<= 8.9%`** across all settings—yet **increases `MIMPA` `ASR` to `87.8%–92.6%` (`Basic`) and `49.4%–53.2%` (`G-Memory`)** because stronger instruction-following models condition more faithfully on retrieved system-provided `past team experience`!
- **Internal belief shift & attention amplification (`Figures 3–4`, `Gemma4-31B` over `255` clean-correct tasks, layers `48, 54, 60`)**:
  - Without poisoned memory (`w/o Poisoned Record`), benign agents assign **`0.97` Round-2 probability** to the correct option and only **`0.03`** to the insider's wrong claim.
  - With poisoned memory retrieved into Round 1, benign agents' wrong-option probe probability jumps to **`0.61` before any peer speaks** (`0.59` at Round 2 without triggering; **`0.86` with Round-2 triggering**).
  - Per-token attention to the planted claim inside retrieved memory reaches **`2.60x`** the rest of the retrieved record, and Round-2 attention to the insider's utterance more than doubles from **`0.35x` (`w/o Poisoned Record`) to `0.76x`**.
  - Qualitative traces (`Section 5.3`, `Appendix F`: `MMLU-Pro` amortization `$4,210.78` vs. `$4,738.42`; `MedMCQA` postpartum hemorrhage `oxytocin` vs. `methylergometrine`) show benign agents **computing or stating the correct domain answer first, then explicitly overriding their own calculation** to conform to retrieved `"prior successful team experience"`.

## Why Post-Hoc Transcript Auditing & Memory Abstraction Are Insufficient

1. **`G-Memory` Abstraction Attenuates Retrieval (`51.3%–58.3%` vs. `86.6%–100.0%`) Rather Than Enforcing Soundness (`Table 2`)**: When a poisoned record *is* retrieved in `G-Memory`, conditional influence still reaches **`41.9% / 67.5% / 71.4%`** (`gpt-5.4-nano`), because LLM insight distillation strips speaker disagreement and rewrites the false claim as a clean declarative team insight.
2. **Post-Hoc High-Reasoning Transcript Auditing Misses Domain-Embedded Planting (`Tables 4–5`)**: Auditing all `3` planting transcripts + `1` target transcript with a `SHADE-Arena`-style `gpt-5.4-mini` (`high` reasoning effort, suspicion threshold `> 50`) reduces `MIMPA` `ASR` partially (`Basic`: `32.5% -> 15.7%` `MMLU-Pro`, `79.5% -> 45.8%` `TruthfulQA`, **`79.1% -> 67.2%` `MedMCQA`**; `G-Memory`: `7.4% / 17.7% / 27.6%`), **leaving `67.2%` residual `ASR` on `MedMCQA` (`Basic`)**. Stage-wise detection (`Table 5`) reveals why: on specialized `MedMCQA` (`Basic`), the auditor flags **only `3.0%` of planting episodes** (`19.4%` target, `22.4%` any; `G-Memory` `17.1% / 23.7% / 36.8%`) because narrow conditional side-notes inside an otherwise accurate medical solution look like ordinary domain caveats.

## Defensive Engineering Takeaways

1. **Never equate episode-level team accuracy with per-utterance truth**: Do not commit raw multi-agent transcripts or LLM-distilled insights into shared cross-task memory solely because the final majority vote passed a task check. Strip uncorroborated side claims that were not causally verified by tool execution, deterministic checks, or primary source citations on the current task.
2. **Preserve speaker identity and consensus-support tags across memory distillation**: Never flatten single-agent assertions into anonymous `"successful team experience"` summaries; tag every stored clause with `originating_agent_id`, whether peers independently corroborated it in Round 1 *before* exposure, and external verification status (`verified_tool_output` vs. `unverified_peer_claim`).
3. **Quarantine single-origin or unverified retrieved memories from overriding independent Round-1 computation**: Present retrieved historical insights only *after* agents record an independent Round-1 commitment (preventing the `0.61` pre-debate prior hijack), and pair cross-session memory stores with causal write-provenance tracking ([`state-anchored-trajectory-auditing`](../skills/state-anchored-trajectory-auditing/SKILL.md), [`multi-layer-compromise-filtering-and-traceback`](../skills/multi-layer-compromise-filtering-and-traceback/SKILL.md), [`falsification-gated-memory-evolution`](../skills/falsification-gated-memory-evolution/SKILL.md)).

## Related Artifacts

- **Rules**: [`multi-agent-coordination.md`](../rules/multi-agent-coordination.md) (*"DON'T: Equate episode correctness with utterance trustworthiness in experience stores or rely on retrospective transcript review to prevent insider poisoning"*, *"DO: Supervise persistent multi-agent ecosystems with zero-LLM cross-layer Kalman filtering, four-channel trigger fusion, and top-3 RTS backward trace-back sanitization"*), [`agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md) (*"DO: Pair cross-session state-provenance anchors with conformal-calibrated trajectory arbitration"*), [`recursive-improvement.md`](../rules/recursive-improvement.md) (*"DO: Dynamically calibrate consensus entropy and weight peer influence by evidence grounding in multi-agent debate"*, *"DO: Represent persistent memory updates as falsifiable behavioral hypotheses verified by counterfactual probes and runtime violation eviction"*)
- **Skills**: [`debate-consensus-memory-calibration`](../skills/debate-consensus-memory-calibration/SKILL.md), [`state-anchored-trajectory-auditing`](../skills/state-anchored-trajectory-auditing/SKILL.md), [`multi-layer-compromise-filtering-and-traceback`](../skills/multi-layer-compromise-filtering-and-traceback/SKILL.md), [`falsification-gated-memory-evolution`](../skills/falsification-gated-memory-evolution/SKILL.md)
