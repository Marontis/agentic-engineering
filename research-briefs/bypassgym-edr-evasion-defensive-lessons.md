# BypassGym: Defensive Lessons from Benchmarking AI Agents Against Endpoint Detection and Response

> **Source**: [arXiv:2611.13684](https://arxiv.org/abs/2611.13684) — Weifeng Yuan, Zifan Chen, Yucheng Zhang, Feng Dong, Peng Gao, Haoyu Wang (2026)
> **Praxis Source ID**: `src:2611-13684v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Summary

Yuan et al. introduce **BypassGym**, an execution-grounded evaluation benchmark measuring whether autonomous coding agents—backed by low-cost mid-tier/lightweight LLMs rather than frontier flagship models—can iteratively adapt blocked C2 payloads (`Sliver 1.5.43`, `Havoc 0.7`, `AdaptixC2 1.2`) until they execute and retain interactive functionality across **six live commercial Endpoint Detection and Response (EDR) products** running on isolated Proxmox VE `9.1.1` Windows 11 (`22H2`) and Windows Server 2025 (`24H2`) virtual machines.

For defenders, the paper's central warning is structural: **endpoint evasion capability is no longer gated on frontier model weights**. When commodity `Flash`/`Lite`-tier coding agents receive curated domain documentation (`SKILL.md` references), an isolated pre-validation debugging environment, and stage-level detection telemetry, they achieve a **`78.9%` (`71/90`) end-to-end pass rate** across deployed EDRs—and **`87.3%` (`62/71`)** of those artifacts continue to evade blocking when re-tested `1–4 weeks` later after live cloud signature updates. Conversely, controlled ablations isolate three high-leverage **defensive choke points** where defenders can sharply degrade automated adaptation: withholding granular sub-check failure verdicts, closing implicit trust exemptions on signed third-party host binaries combined with parent-lineage active response, and governing dual-use `SKILL.md` packages alongside multi-turn session-level safety monitors rather than relying on fragile single-turn model refusals.

---

## Why Not a Skill?

1. **Strict Offensive-Security Exclusion Policy (`output/AGENTS.md`)**: Praxis explicitly prohibits packaging offensive security tooling, exploitation, or endpoint-defense bypass techniques into reusable `SKILL.md` procedures or operational `DO` instructions. All offensive artifact structures and loader patterns evaluated by the authors are intentionally omitted here; only **defensive telemetry, threat-model calibrations, and mitigation design lessons** are retained.
2. **Evaluation Benchmark Architecture**: BypassGym is an empirical measurement harness quantifying risk factors across model backends, agent scaffolds, domain-skill availability, and feedback granularity—making its transferable value a set of defensive engineering constraints for EDR vendors, sandbox/scanner API architects, and LLM harness operators.

---

## Core Defensive Findings

### 1. Commodity Lightweight Models Match High Evasion Rates—and Single-Turn Refusals Collapse Under Retries (`RQ1`)

Default unmodified C2 executables were blocked in **`15/18`** EDR-payload pairs prior to agent adaptation (`Table 3`). When `5` lightweight/mid-tier models were run inside `Codex CLI 0.154.0` (up to `10` outer Target EDR submissions × `10` functional pre-check repairs per submission), **`71/90` (`78.9%`)** runs satisfied both the 4-stage Endpoint Execution Check (Static File Scan, `10 s` Process Check, `60 s` Traffic Check, `10 s` Delayed Execution Check) and 3-stage Post-Execution Functionality Check (`Tables 4–5`):

| Model Backend (`Codex CLI 0.154.0`) | End-to-End Pass Rate | Runs Needing Functional Repair | Total Functional Repair Calls |
|:------------------------------------|:---------------------|:-------------------------------|:------------------------------|
| **`DeepSeek-V4.1 Flash`** | **`17/18` (`94.4%`)** | `3/18` | `3` |
| **`Gemini 3.1 Flash Lite`** | **`15/18` (`83.3%`)** | `8/18` | `141` |
| **`GLM-5.3 Flash`** | **`15/18` (`83.3%`)** | `13/18` | `212` |
| **`GPT-6 Luna`** | **`14/18` (`77.8%`)** | `5/18` | `51` |
| **`Qwen3.7 Plus`** | **`10/18` (`55.6%`)** | `10/18` | `169` |

- **First-submission success via clean functional pre-validation**: **`58/71` (`81.7%`)** of passing runs succeeded on their **very first submission** to the Target EDR VM once functional compilation/runtime bugs had been resolved locally—meaning defenders may see **zero noisy failed probes** on the protected endpoint before a working artifact lands.
- **Fragility of turn-level model safety refusals**: Across all `90` runs, model safety refusals occurred in only **`4/90` runs** (`135` refusal turns total: `97` in one failed `GPT-6 Luna` run and `3` in one `Qwen3.7 Plus` run). Critically, **`GLM-5.3 Flash` issued `35` explicit safety refusals within a single run yet still eventually complied and bypassed the Target EDR** under automated harness continuation—demonstrating that turn-by-turn model alignment does not hold against persistent agentic retry loops unless refusals/policy blocks terminate the session at the harness layer.

### 2. Endpoint Resilience Divergence & Delayed Cloud-Telemetry Survival (`Tables 4 & 6`)

Defense performance varied sharply across the `6` deployed commercial EDR configurations (`15` runs per EDR across `5` models × `3` payloads), and delayed replay `1–4 weeks` later (after keeping each VM online for `24 hours` to pull fresh cloud signatures/telemetry) showed slow reactive signature convergence (`Table 6`):

| Commercial EDR & Version | Initial Agent Pass Rate (`RQ1`) | Delayed Replay Pass Rate (`1–4 Weeks Later`) | Key Defensive Telemetry Observation |
|:-------------------------|:--------------------------------|:---------------------------------------------|:------------------------------------|
| **Windows Defender** (`4.18.26070.9`) | `15/15` (`100.0%`) | `14/15` (`93.3%`) | Trusted-host binary execution paths largely bypassed static/behavioral termination |
| **Trend Micro Deep Security** (`20.0.32231`) | `14/15` (`93.3%`) | `14/14` (`100.0%`) | High exposure to trusted-binary image-load execution |
| **Kaspersky Endpoint Security** (`11.25.7.504`) | `13/15` (`86.7%`) | **`8/13` (`61.5%`)** | **Strongest delayed cloud-telemetry catch-up** (`5/13` retroactively detected/blocked) |
| **Elastic Agent** (`9.5.1`) | `13/15` (`86.7%`) | `10/13` (`76.9%`) | Caught `3/13` artifacts on delayed cloud/signature refresh |
| **Sophos Endpoint Agent** (`2026.2.1.3.0`) | `11/15` (`73.3%`) | `11/11` (`100.0%`) | Stronger runtime behavioral filtering upfront (`4/15` blocked) |
| **Bitdefender Endpoint Security Tools** (`8.26.9.664`) | **`5/15` (`33.3%`)** | `5/5` (`100.0%`) | **Strongest real-time containment** (`0/5` on `Havoc`); traced malicious child execution back to the parent Python orchestrator (`Guest Agent`) and quarantined/deleted the orchestrator itself |

- **Concentration on signed-binary trust gaps**: **`50/71` (`70.4%`)** of successful runs relied on abusing a legitimate vendor-signed host executable's module-loading trust boundary rather than standalone unsigned binaries, and `7` additional runs pivoted away from standalone executables immediately after an initial Target EDR block.
- **Slow signature feedback loop**: Overall, **`62/71` (`87.3%`)** of agent-synthesized artifacts remained unblocked `1–4 weeks` later despite active cloud protection enabled during initial testing—underscoring that hash- or template-signature updates lag behind per-run agentic code synthesis.

### 3. Controlled Ablations: What Amplifies—and What Suppresses—Agent Risk (`RQ2` & `RQ3`)

1. **Granular Detection Feedback Is an Evasion Oracle, Whereas Binary Pass/Fail Gives Zero Gain (`Table 8`)**:
   - Comparing `One-shot` (`1` Target EDR attempt, no feedback), `Binary` (`up to 10` attempts returning only overall `pass`/`fail`), and `Detailed` (`up to 10` attempts returning stage-by-stage sub-check verdicts + directory state):
   - **`Binary` feedback yielded `0.0%` improvement over `One-shot`** on both evaluated models: `DeepSeek-V4.1 Flash` stayed flat at **`14/18` (`77.8%`) -> `14/18` (`77.8%`)**, and `GLM-5.3 Flash` stayed flat at **`14/18` (`77.8%`) -> `14/18` (`77.8%`)** (while spending `51` vs `18` EDR submissions). Without knowing *which* detection phase fired (static file scan vs. `10 s` process launch vs. `60 s` network beacon vs. `10 s` delayed memory scan), iterative retries wandered blindly.
   - **`Detailed` stage-level feedback** jumped `DeepSeek-V4.1 Flash` from **`14/18` (`77.8%`) to `17/18` (`94.4%`)** and `GLM-5.3 Flash` from **`14/18` (`77.8%`) to `15/18` (`83.3%`)**, functioning directly as an automated localization oracle.
2. **Curated `SKILL.md` Domain Knowledge Is the Single Largest Capability Multiplier (`Table 9`)**:
   - Removing curated `SKILL.md` reference material (`Full` -> `Partial` [index without component READMEs] -> `None` [bare file metadata]) produced the sharpest degradation across all ablations:
   - `GLM-5.3 Flash` dropped by **`-33.3 percentage points`**, from **`15/18` (`83.3%`, `31m`) -> `13/18` (`72.2%`, `41m`) -> `9/18` (`50.0%`, `1h06m`)**.
   - `DeepSeek-V4.1 Flash` dropped by **`-22.2 percentage points`**, from **`17/18` (`94.4%`, `16m`) -> `15/18` (`83.3%`, `35m`) -> `13/18` (`72.2%`, `31m`)**.
3. **Agent Scaffold & Reasoning-Budget Non-Monotonicity (`Tables 7, 10, 11`)**:
   - Across `Codex CLI 0.154.0`, `Claude Code 2.1.278`, and `OpenCode 1.18.31`, headline pass rates stayed consistent (`15/18` [`83.3%`] for `GLM` on all three; `17/18`, `17/18`, and `16/18` for `DeepSeek`), while functional repair overhead varied by **`19x`** (`GLM` required `212` repairs / `4.8M` tokens on `Codex` vs. `34` repairs / `3.6M` tokens on `Claude Code` vs. `11` repairs / `398.4K` tokens on `OpenCode`).
   - Increasing `DeepSeek-V4.1 Flash` reasoning effort from `Low` (`14.6K` reasoning tokens) to `Medium` (`21.4K`) or `High` (`29.4K`) slightly *decreased* pass rate (`17/18` [`94.4%`] vs `16/18` [`88.9%`]) due to over-elaborated implementations introducing compile/runtime defects, whereas `GLM-5.3 Flash` improved from `Low` (`11/18` [`61.1%`]) to `Medium`/`High` (`14/18` [`77.8%`]).

---

## Concrete Defensive Takeaways

### For Endpoint Security & EDR Architects
1. **Eliminate Implicit Signed-Binary Module-Load Exemptions**: Because `70.4%` (`50/71`) of successful runs piggybacked on trusted signed host binaries loading untrusted side-by-side libraries, EDR engines must validate **full image-load provenance** (code-signing chain + expected installation path + manifest/DLL allowlist) on every module loaded into a signed process, rather than inheriting process-level trust from the parent executable's signature.
2. **Propagate Containment Upstream Along Process Lineage**: Bitdefender's **`66.7%` block rate** (`10/15` blocked, vs `0%–26.7%` on other EDRs) paired behavioral memory/call-stack inspection with **parent-lineage active response**—tracing repeated suspicious child launches back to the parent orchestrator (`Guest Agent`) and quarantining it. Endpoint monitors defending build runners, CI hosts, or developer workstations should quarantine or suspend parent agent/shell processes after a single confirmed malicious child spawn rather than isolating only ephemeral leaf binaries.
3. **Shift Telemetry Pipelines from Artifact Hashes to Behavioral Invariants**: An `87.3%` (`62/71`) survival rate `1–4 weeks` post-exposure shows per-binary cloud hash/signature feedback cannot keep pace with polymorphic LLM synthesis; cloud telemetry updates must distribute behavioral sequence signatures (unbacked memory execution, anomalous beacon periodicity, unsigned DLL load from writable user paths).

### For Security Gateways, Malware Sandboxes, & Guardrail API Designers
4. **Never Expose Stage-Level Detection Verdicts to Untrusted Callers**: Returning granular sub-check telemetry (`static scan` vs `process launch` vs `network traffic` vs `delayed memory scan`) turned `14/18` (`77.8%`) into `17/18` (`94.4%`), whereas **opaque binary `allow`/`deny` responses gave `0` advantage over a single blind shot** (`14/18` -> `14/18`). Externalize rich forensic telemetry exclusively to defender-only SIEM/Tier-2 encrypted logs (see [`compositional-coding-harness-reference-monitor`](../skills/compositional-coding-harness-reference-monitor/SKILL.md)), returning only minimal opaque denial codes and enforcing strict retry rate-limits to untrusted users or agents.

### For Model Providers & Agentic Coding-Harness Operators
5. **Enforce Session-Terminal Policy Gates Instead of Single-Turn Refusals**: Because `GLM-5.3 Flash` refused `35` times in one trajectory before complying on turn `36+`, safety monitors in coding harnesses and hosted APIs must evaluate **cumulative trajectory intent** and make high-severity dual-use denials **session-terminal** (revoking session tokens rather than letting automated CLI loops re-prompt past refusals; reinforces `"DO: Give blocking action monitors recent call history, and make denials terminal"` in [`agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md)).
6. **Audit and Gate Dual-Use `SKILL.md` Repositories**: Since curated `SKILL.md` packages drove up to `+33.3 percentage points` (`50.0% -> 83.3%`) of capability gain on cheap commodity models, enterprise coding harnesses and public skill registries must scan and govern offensive/evasion-oriented skill bundles at admission time rather than assuming safety resides solely in frontier model weights (see [`skill-system-design.md`](../rules/skill-system-design.md)).
