# DiscernBench: Evaluating Cooperative Discernment of LLM Agents in Institutional Settings

> **Source**: [arXiv:2611.28787](https://arxiv.org/abs/2611.28787) — Chinmayi Sheshanarayana, Prathamesh P. Magar (Manipal University Jaipur, 2026)  
> **Praxis Source ID**: `src:2611-28787v1`  
> **License**: CC BY 4.0  
> **Repository**: [https://github.com/sheshanarayanaa/discernbench](https://github.com/sheshanarayanaa/discernbench)

## Why Not a Skill?

`DiscernBench` is a diagnostic institutional-governance benchmark and multi-model behavioral study rather than a constructive runtime repair procedure. It characterizes why decomposing three-way institutional decisions (`cooperate`, `refuse`, `escalate`) across role-specialized agents (`Policy`, `Hidden-Harm`, `Oversight`) and an LLM `Final Responder` systematically degrades decision accuracy, inflates over-escalation by `7.5x`, and lowers social-pressure consistency across 8 evaluated LLMs. Its operational lessons belong directly as always-active coordination and evaluation guardrails in [`multi-agent-coordination.md`](../rules/multi-agent-coordination.md).

## Benchmark Design & Three Architectural Baselines

`DiscernBench` curates **`600` clean institutional base scenarios** grounded in **`7` public incident-report repositories** (`TSB Canada`, `AAIB UK`, `FEMA`, `NTSB`, `MAIB UK`, `TAIC NZ`, `HSDL`) across high-consequence organizational workflows (healthcare, finance, infrastructure, public administration, aviation/maritime operations). Every base scenario is instantiated across **`4` matched social-pressure framings**—`Neutral`, `Urgency`, `Authority`, and `Social-conformity`—yielding **`2,400` evaluation instances** balanced `1:1:1` across `{cooperate, refuse, escalate}`.
- **Human Validation & Ceiling (`Section 3.3`, `Table 4`)**: Across all `600` base items (`3` independent annotators), label agreement reaches **Fleiss' $\kappa = 0.873$** and **Krippendorff's $\alpha = 0.874$** (pairwise $\kappa \in [0.841, 0.914]$). Human annotators achieve **`CDS = 0.960`**, **Cohen's $\kappa = 0.940$**, **`OER = 0.005`**, **`CPI = 0.969`**, and **`RDI = 0.982`**, leaving a `>22 pp` gap above the strongest single-agent LLM (`Gemini-2.5-Flash` `B1` `CDS = 0.7321`).
- **Low-Identifiability Holdout (`Appendix A.6.3`)**: On `168` scenarios (`672` instances) stripped of recognizable incident details to control for pretraining memorization, `B3` macro `CDS` (`56.09%` vs. `55.48%` full) and `OER` (`25.43%` vs. `28.27%` full) closely track the full suite.

Three controlled architectures are compared across `8` open-weight and frontier models (`temperature = 0` deterministic JSON schemas):
- **`B1` (Single-Agent Responder)**: One LLM directly outputs `{cooperate, refuse, escalate}` with rationale.
- **`B2` (Single-Specialist Decomposition)**: One specialist jointly scores `policy violation`, `hidden harm`, and `oversight need` in a single pass before a `Final Responder` decides (`2` LLM calls).
- **`B3` (Multi-Specialist Deliberation)**: Three separate role specialists (`Policy`, `Hidden-Harm`, `Oversight`) evaluate independently in Round 1, run Round-2 deliberation whenever Round-1 recommendations disagree, and pass full outputs to an LLM `Final Responder` (`4–7` LLM calls).

## Core Empirical Findings

### 1. The Decomposition–Recomposition Gap (`Table 1`)
Splitting joint evaluation (`B2`) into separate role specialists plus deliberation (`B3`) **hurts overall accuracy (`CDS`), inflates Over-Escalation Rate (`OER`) `7.5x` over `B1`, and lowers Pressure Consistency (`PCS`) on all `8/8` models**:

| Model | `B1` `CDS` | `B2` `CDS` | `B3` `CDS` | `B1` `OER` | `B2` `OER` | `B3` `OER` | `B3` `RDI` | `B1` `PCS` | `B3` `PCS` |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **`Gemini-2.5-Pro`** | `0.7229` | **`0.7250`** | `0.6681` | `0.0728` | `0.0951` | `0.2373` | `0.4875` | `0.8583` | `0.8400` |
| **`Gemini-2.5-Flash`** | **`0.7321`** | `0.7154` | `0.5538` | `0.0716` | `0.0259` | **`0.5605`** | **`-0.2686`** | `0.8600` | `0.7083` |
| **`Phi-4` (`14B`)** | **`0.6892`** | `0.6425` | `0.5988` | `0.0691` | `0.2981` | `0.4185` | `0.1510` | `0.8567` | `0.7300` |
| **`Mistral-Small-24B`** | `0.6342` | **`0.6596`** | `0.5740` | `0.0444` | `0.1519` | `0.4571` | **`-0.2067`** | `0.7933` | `0.6817` |
| **`Qwen-2.5-32B`** | **`0.5954`** | `0.4892` | `0.4802` | `0.0636` | `0.4889` | `0.4595` | `-0.1230` | `0.8283` | `0.6633` |
| **`Llama-3.1-8B`** | `0.5058` | **`0.5179`** | `0.4998` | `0.0025` | `0.0049` | `0.0754` | `0.7073` | `0.8167` | `0.6617` |
| **`Qwen-2.5-7B`** | `0.4079` | **`0.5775`** | `0.5317` | `0.0031` | `0.1506` | `0.0422` | `0.8699` | `0.8200` | `0.8050` |
| **`Llama-3.2-3B`** | `0.4429` | `0.4671` | **`0.5325`** | `0.0025` | `0.0444` | `0.0111` | `0.6296` | `0.8817` | `0.7200` |
| **8-Model Mean (Prose `%`)** | **`59.13%`** | **`59.93%`** | **`55.48%`** | **`3.79%`** | **`15.75%`** | **`28.27%`** | — | **`83.94%`** | **`72.63%`** |

- **`B3` only helps weak single-agent models (`Llama-3.2-3B`, `Qwen-2.5-7B`)**, and even on `Qwen-2.5-7B`, single-specialist `B2` (`0.5775`) beats 3-specialist `B3` (`0.5317`). On capable models (`Gemini-2.5-Flash`, `Qwen-2.5-32B`, `Phi-4`, `Mistral-Small-24B`, `Gemini-2.5-Pro`), `B3` drops `CDS` by **`5.48` to `17.83` percentage points** (`RDI` turning negative to `-0.2686` on `Gemini-Flash` and `-0.2067` on `Mistral-24B` as clear refusals are converted into escalations).
- **Universal Pressure Amplification (`Tables 1, 6`)**: Multi-agent `B3` lowers `PCS` on **every single model (`8/8`)**, with Pressure Flip Rates (`PFR`) peaking under `Social-conformity` and `Authority` framing (up to `0.2050` on `Gemini-2.5-Flash` `B3` under social pressure) because peer rationales repeat and legitimize urgency/authority cues across turns.

### 2. Asymmetric Minority-Signal Override (`MSO`) & Upward Deferral (`UDR`)
Why does `B3` fail when specialists hold accurate distributed signals?
- **High Specialist Disagreement With Modest Responder Gain (`Table 2`)**: Specialist conflict rates (`CR`) span `27.29%` (`Llama-3.2-3B`) to **`84.08%` (`Qwen-2.5-32B`, Conflict Resolution Accuracy `CRA = 41.94%`, Conflict Resolution Skill `CRS = +3.07` pts over majority vote)**, with `CRS` staying modest (`+0.99` to `+17.26` pts) across `7/8` models (`+42.29` pts on `Llama-3.2-3B`).
- **Up to `350x` Action-Type Override Asymmetry (`Tables 7–8`, `Appendix A.7.1`)**: When two specialists agree and one specialist dissents (`2-vs-1`), LLM `Final Responders` exhibit severe directional bias rather than calibrated evidence synthesis:
  - On `Mistral-Small-24B`, the Responder follows a **lone `escalate` minority in `69.8%` (`0.698`) of cases (`50.6%` [`0.506`] *incorrectly* overriding a correct `2`-specialist majority!)** vs. **`0.2%` (`0.002`)** for a lone `cooperate` minority (**`~350x` disparity**).
  - `Qwen-2.5-32B` follows lone `escalate` at **`56.6%` (`0.337` incorrect)** and lone `refuse` at **`43.4%`** vs. **`2.4%`** lone `cooperate`; `Gemini-2.5-Flash` (`44.2%` [`0.392` incorrect] vs. `0.0%` coop) and `Phi-4` (`42.4%` [`0.303` incorrect] vs. `0.0%` coop) show the same cautious-veto collapse.
  - Conversely, smaller models collapse in other directions: `Qwen-2.5-7B` follows **lone `refuse` at `89.6%`** (`11.4%` esc, `5.2%` coop), while `Llama-3.2-3B` follows **lone `cooperate` at `80.5%`** (`0.0%` esc, `4.6%` ref).
  - Role-identity attribution (`Figure 10`): `Mistral-24B` (`71%`) and `Qwen-32B` (`57%`) defer predominantly to the **`Oversight`** specialist, whereas `Gemini-Flash` (`66%`) and `Phi-4` (`64%`) defer to **`Hidden-Harm`**.
- **Upward-Deferral Cascade (`Table 9`) & Specialist Ablations (`Tables 3, 5`, `Table 10`)**:
  - Moving `B1 -> B3` converts **`58.81%`** (`Gemini-Flash`; `66.21%` of `B1` refusals `R->E`, **`71.82%` from `B2`**), **`49.81%`** (`Mistral-24B`; `59.69%` `R->E` from `B2`), **`49.30%`** (`Qwen-32B`), **`43.62%`** (`Phi-4`), and **`27.03%`** (`Gemini-Pro`) of direct `cooperate`/`refuse` decisions into `escalate` (`UDR`).
  - Removing the **`Oversight` specialist (`No-O`, `Table 3`)** cuts `OER` sharply (`Phi-4` `41.85% -> 22.65%`, `Llama-8B` `7.54% -> 0.56%`, `Gemini-Pro` `23.73% -> 20.78%`), whereas removing Round-2 debate (`No-R2`, `Table 5`) leaves `OER` elevated (`Phi-4` `42.81%`, `Gemini-Pro` `26.72%`)—proving the bottleneck is **role decomposition + LLM Responder recomposition**, not Round-2 chat alone.
  - Replacing the LLM `Final Responder` with **equal-weight Round-1 majority voting (`Table 10`)** slashes `OER` (`Qwen-32B` `0.4595 -> 0.1735`, `Mistral-24B` `0.4571 -> 0.1528`, `Phi-4` `0.4185 -> 0.2196`, `Llama-8B` `0.0754 -> 0.0013`) at the cost of `2–491` unresolved `1-1-1` ties requiring a deterministic tie-breaker.

## Practical Design & Evaluation Implications

1. **Default to single-specialist joint rubric scoring (`B2`) or single-agent structured triage (`B1`) on mid/frontier models** instead of splitting `Policy`, `Hidden-Harm`, and `Oversight` into separate LLM personas behind an unconstrained LLM synthesizer.
2. **Audit institutional multi-agent triage across directional error metrics, not accuracy (`CDS`) alone**: Always report `OER` (Over-Escalation Rate), `RDI` (Refusal–Escalation Discrimination Index), `UDR` (`C->E` and `R->E` upward deferral), `2-vs-1` `MSO` / `IOR_MSO` by minority action class, and `4`-framing Pressure Consistency (`PCS`).
3. **Replace free-form LLM `Final Responders` with calibrated deterministic aggregation rules** (e.g., `2-of-3` majority vote with explicit structural escalation predicates on `1-1-1` ties, per *"DO: Define explicit escalation triggers, not vague guidelines"* in [`agent-human-interaction.md`](../rules/agent-human-interaction.md)) so a single cautious specialist role cannot veto `2`-specialist majorities on `42%–70%` of conflicts.

## Related Artifacts

- **Rules**: [`multi-agent-coordination.md`](../rules/multi-agent-coordination.md) (*"DON'T: Split institutional cooperate-refuse-escalate decisions across specialist roles feeding an LLM synthesizer; prefer unified evaluation and majority voting"*, *"DO: Separate task execution from safety monitoring via guard-agent topologies"*), [`agent-human-interaction.md`](../rules/agent-human-interaction.md) (*"DO: Define explicit escalation triggers, not vague guidelines"*)
