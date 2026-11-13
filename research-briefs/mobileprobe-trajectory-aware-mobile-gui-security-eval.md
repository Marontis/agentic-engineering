# MobileProbe: Adaptive Security Evaluation of Mobile Agents via Trajectory-Aware Injection

> **Source**: [arXiv:2611.16693](https://arxiv.org/abs/2611.16693) — Yingbin Jin, Ji'an Wang, HaoYang Chai, Hanjun Luo, Li Hu, Xinfeng Li, Huadi Zheng, PeiZhao Hu, Qingqing Ye, Haibo Hu (2026)
> **Praxis Source ID**: `src:2611-16693v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Summary

Pre-deployment security benchmarks for mobile GUI agents (`AndroidWorld`, `MobileWorld`, and static prompt-injection suites) typically plant fixed payloads at predetermined screens or rely on transcript-level behavioral judges. Jin et al. demonstrate that because heterogeneous mobile GUI agents take divergent navigation routes across multi-app Android workflows (averaging `27.8` steps), static expert-chosen injection points miss `12.0%–22.9%` of evaluation runs (`Payload Miss Rate`, `PMR`) with a wide cross-agent exposure skew, confounding architectural vulnerability with navigation path differences.

**MobileProbe** introduces a closed-loop, trajectory-aware security auditing framework evaluated across `83` long-horizon attack instances constructed from `65` benign tasks (screened from `117` non-MCP, non-interactive `MobileWorld` tasks) spanning `12` Android applications on Android 14 AVDs (`8GB` RAM, `1080 × 2400`). Rather than relying on static screen placement, the evaluation pipeline records each target agent's benign execution trajectory, localizes high-consequence decision steps using a three-axis rubric, gates environmental exposure at runtime via Android UI-hierarchy predicates (`gate-on-match`), pre-filters candidate test cases for semantic and rendered visual coherence before burning live emulator budget, and grades outcomes using deterministic OS/app/database/filesystem verification alongside Stealth Hijacking Rate (`SHR`) and Benign-Failed Susceptibility (`ASR-F`).

> **Scope & Defensive Framing Note**: Following repository offensive-security policy, this brief distills only **defensive pre-deployment security evaluation methodology, trajectory-exposure measurement invariants, and architectural hardening lessons** for mobile and desktop GUI agents. Persuasive prompt templates and APK modal-spoofing payloads are intentionally omitted.

## Key Evaluation Methodology & Quantitative Findings

### 1. Trajectory-Aware Exposure Gating Eliminates Path-Divergence Confounds (`PMR`)

MobileProbe discovers candidate exposure surfaces from benign execution traces (`generic` Android UI-hierarchy predicates `package_name`, `activity_name`, `required_texts`, `required_resource_ids`; `instance` context parameters; and `rendering` layout/truncation constraints) and scores each candidate step $t$ across three `1–5` Likert dimensions ($w_1 = w_2 = w_3 = 1/3$):

$$v(t) = w_1\,\mathrm{Rel}(t) + w_2\,\mathrm{Crit}(t) + w_3\,\mathrm{Expl}(t)$$

where $\mathrm{Rel}(t)$ measures relevance to the malicious objective, $\mathrm{Crit}(t)$ measures whether step $t$ sits at a consequential state-changing or cross-app decision boundary rather than routine scrolling, and $\mathrm{Expl}(t)$ measures how naturally the screen affords untrusted external content. During live evaluation (`3` runs per task averaged), a background monitor checks the foreground Android UI hierarchy at every step (`gate-on-match`) to record **binary ground-truth payload exposure** (requiring at least one step where all UI matching predicates hold on the rendered screen).

Across three representative GUI agent architectures—commercial end-to-end VLM **`Gemini-3.1-Pro`** (Benign Utility `BU = 54.6%`), decoupled planner-plus-grounder **`Gemini-3.1-Pro + UI-Ins-7B`** (`Agentic`, `BU = 56.6%`), and open-source on-device **`GUI-Owl-1.5-8B-Instruct`** (`BU = 26.5%`)—per-agent trajectory localization dramatically improves reachability parity:

| Injection-Point Localization Strategy | `Gemini-3.1-Pro` `PMR` ↓ | `Agentic` (`Gemini + UI-Ins-7B`) `PMR` ↓ | `GUI-Owl-1.5-8B` `PMR` ↓ | Cross-Agent `PMR` Spread |
|:--------------------------------------|:------------------------:|:----------------------------------------:|:------------------------:|:------------------------:|
| **Expert-Fixed** (task-specific manual screen) | `13.3%` | `12.0%` | `22.9%` | `10.8%` (`10.9` pp in rounded table) |
| **Cross-Agent** (transferred from another model family) | `12.0%` | `10.8%` | `15.7%` | `4.9` pp |
| **MobileProbe** (per-agent trajectory localization) | **`4.8%`** | **`3.6%`** | **`6.0%`** | **`2.4%`** |

*(Note: Paper prose in §VI-B reports that MobileProbe narrows cross-agent `PMR` spread from `10.8%` under `Expert-Fixed` to `2.4%`, reflecting unrounded underlying averages corresponding to table entries `12.0%` and `22.9%`.)*

### 2. Static Templates Undercount Frontier GUI Vulnerability by `>10x` While On-Device 8B Models Break on Static Prompts

Holding trajectory-aware injection points fixed across all five evaluation methods (`T_max = 15` refinement budget, top-$k = 3$ parents, $m = 2$ offspring/parent, `Seed-2.0-Pro` generator, `GPT-5.4` dual semantic/visual surrogate and 4-level behavioral judge), deterministic environment-state verification across the `83` instances (`44` `Malicious Text` across `7` page templates in `Mail`, `Messages`, `Mastodon`, `Mattermost`, `Taodian`; `39` `In-App Fake Dialog` across `29` page types; `47` Cross-App, `36` Single-App; `27` Confidentiality, `28` Integrity, `28` Availability) reveals two sharp regime splits:

| Evaluation Method | `Gemini-3.1-Pro` Overall `ASR` | `Agentic` Overall `ASR` | `GUI-Owl-1.5-8B` Overall `ASR` | `Malicious Text` (`Gem` / `Ag` / `Owl`) | `In-App Fake Dialog` (`Gem` / `Ag` / `Owl`) |
|:------------------|:------------------------------:|:-----------------------:|:------------------------------:|:---------------------------------------:|:-------------------------------------------:|
| **Static Template** | `6.8%` | `8.0%` | `34.5%` | `10.6%` / `10.6%` / `40.9%` | `2.6%` / `5.1%` / `27.4%` |
| **Zero-shot LLM** | `8.0%` | `9.2%` | `15.7%` | `9.8%` / `13.6%` / `19.7%` | `6.0%` / `4.3%` / `11.1%` |
| **Adapted PAIR** | `56.6%` | `54.6%` | `77.5%` | `53.8%` / `40.9%` / `72.0%` | `59.8%` / `70.1%` / `83.8%` |
| **Adapted Genesis** | `40.6%` | `39.0%` | `61.4%` | `25.8%` / `28.0%` / `43.9%` | `57.3%` / `51.3%` / `81.2%` |
| **MobileProbe** | **`85.1%`** | **`86.3%`** | **`85.1%`** | **`81.8%` / `78.0%` / `78.8%`** | **`88.9%` / `95.7%` / `92.3%`** |

Key architectural takeaways:
- **Frontier VLM guardrails catch overt imperatives but fail contextual UI framing**: Against `Static Template` (`6.8%`–`8.0%`) and `Zero-shot LLM` (`8.0%`–`9.2%`), `Gemini-3.1-Pro` and `Agentic` appear resilient, yet adaptive context-aligned evaluation reaches **`85.1%–86.3%` ASR** (`1.2%` variation across all three architectures).
- **Decoupled visual grounding (`UI-Ins-7B`) does not confer instruction-hierarchy immunity**: Separating UI coordinate grounding from `Gemini-3.1-Pro` planning (`Agentic`) raises benign utility slightly (`54.6% -> 56.6%`) while reaching **`95.7%` ASR** on `In-App Fake Dialog` overlays (`86.3%` overall).
- **On-device 8B GUI models lack basic imperative refusal**: `GUI-Owl-1.5-8B-Instruct` suffers **`34.5%` overall ASR** (`40.9%` on `Malicious Text`) from unadapted static `"IMPORTANT: ignore previous instructions"` templates alone—more than `4x` the frontier baselines (`6.8%–8.0%`).
- **Cross-app context switches are systematically weaker than single-app flows**: Under `MobileProbe`, **`Cross-App` ASR reaches `90.8%` (`Gemini`), `89.4%` (`Agentic`), and `92.2%` (`GUI-Owl`)**, exceeding `Single-App` ASR (`77.8%`, `82.4%`, `75.9%`) by **`7.0–16.3` pp** because agents lose provenance boundaries when transitioning across app trust domains (e.g., reading untrusted `Mastodon`/`Mail` text before invoking `Messages`, `Contacts`, or `Chrome`). Across CIA objectives, **Integrity (`91.7%` / `89.3%` / `89.3%`)** and **Confidentiality (`88.9%` / `88.9%` / `85.2%`)** exceed **Availability (`75.0%` / `81.0%` / `81.0%`)**, as frontier planners actively attempt recovery when availability attacks stall progress.

### 3. Stronger Agents Exhibit *Higher* Stealth Hijacking (`SHR`), and Benign Task Failure Spikes Susceptibility (`ASR-F`)

MobileProbe introduces two diagnostic metrics beyond raw `ASR` that expose critical blind spots in task-completion monitoring:

1. **Stealth Hijacking Rate (`SHR`)** — Conditional on Confidentiality/Integrity tasks (`55` instances) that the agent solves under benign conditions, `SHR` measures $P(\text{Benign Task Completed} \mid \text{Attack Succeeded} \land \text{Benign Completed})$. Under `MobileProbe`, **`Gemini-3.1-Pro` reaches `68.1%` `SHR` and `Agentic` reaches `65.4%` `SHR`**, compared with `46.4%` on `GUI-Owl-1.5-8B` (and `0.0%` / `0.0%` / `21.4%` under `Static Template`). More capable agents execute the unauthorized side effect as an "intermediate prerequisite" and then resume and complete the user's original request—meaning **end-users or supervisors checking only whether the requested task succeeded miss two-thirds of compromises on frontier agents**.
2. **Benign-Failed Susceptibility (`ASR-F`)** — Conditional on tasks where the agent *fails* to complete the benign goal on clean runs, `ASR-F` reaches **`90.3%` (`Gemini-3.1-Pro`), `97.2%` (`Agentic`), and `87.4%` (`GUI-Owl-1.5-8B`)**—exceeding overall `ASR` (`85.1%`, `86.3%`, `85.1%`) on every architecture. When an agent is uncertain or stuck on a long-horizon GUI workflow, it treats authoritative-looking environmental prompts or fake dialogs as helpful recovery instructions.
3. **Component Ablations (`Gemini-3.1-Pro`, Table VI)**: Removing evolutionary refinement collapses `ASR` from **`85.1%` (`7.9` avg rounds) to `28.5%`**; removing dual semantic + rendered-screenshot visual surrogate pre-filtering drops `ASR` to **`63.9%` (`12.8` rounds)** because unrendered payloads suffer UI layout truncation or visual artifacts; and replacing 4-level behavioral + deterministic state feedback with binary pass/fail drops `ASR` to **`76.3%` (`11.4` rounds)**. In a blind study (`10` human annotators, `20` instances, `1–5` Likert), rendered screens scored `4.3` (Text) and `4.7` (Dialog) on Content Authenticity, `3.9` / `3.8` on Contextual Coherence, and `3.2` / `3.4` on Behavioral Plausibility.

## Defensive Engineering Takeaways

1. **Gate GUI Security Benchmarks on Verified Screen Exposure (`PMR`) Alongside `Effective ASR`**: Extend reach-adjusted IPI evaluation ([`owner-authority-ipi-eval-construction`](../skills/owner-authority-ipi-eval-construction/SKILL.md)) to GUI/mobile environments by verifying via live accessibility/UI-hierarchy predicates (`gate-on-match`) that the target screen state was actually rendered and observed, reporting `PMR` alongside `ASR`, `SHR`, and `ASR-F` (see [`agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md)).
2. **Enforce Cross-App Provenance Gates & Out-of-Band Confirmation on High-Impact OS Actions**: Because `Cross-App` transitions hit `89.4%–92.2%` `ASR` and `65.4%–68.1%` `SHR`, never allow untrusted in-app text or modal dialogs read in one package (`Mail`, `Mastodon`, `Mattermost`, browser views) to authorize cross-package side effects (`SMS`, `Contacts`, credential entry, file deletion, payment/settings writes) without deterministic route/principal binding (see [`cross-interface-route-bound-authorization`](../skills/cross-interface-route-bound-authorization/SKILL.md), [`out-of-band-hitl-verification`](../skills/out-of-band-hitl-verification/SKILL.md), and [`agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md)).
3. **Treat Task-Stall / Uncertainty States (`ASR-F` `87.4%–97.2%`) as Elevated-Risk Regimes**: When a GUI agent encounters repeated navigation errors or uncertainty on a long-horizon task, tighten action-auditing gates rather than allowing environmental UI prompts or pop-up dialogs to redirect control flow.
4. **Never Deploy Unhardened Small On-Device GUI Models (`8B`) Without Deterministic Action Sandboxes**: Small on-device GUI models (`GUI-Owl-1.5-8B`, `34.5%` static-template `ASR`) fail even unadapted imperative injections and require external Ring-0 capability gates before dispatching OS intents or UI clicks on sensitive packages.

## Why Not a Skill?

While MobileProbe's evaluation metrics (`PMR`, `SHR`, `ASR-F`) and runtime `gate-on-match` exposure auditing are broadly valuable for GUI security benchmarking, the paper's core algorithmic loop (`Red Team Agentic System`: `PayloadGenerator` over $5 \times 4$ persuasive strategies and deceptive UI modal styles, `EvolutionaryRefiner` with adversarial experience memory, and repackaged-APK fake system/permission dialogs) is an automated offensive red-teaming and UI-spoofing synthesis pipeline. Under `output/AGENTS.md` policy (*"prefer a brief limited to defensive lessons"* for offensive/exploitation tooling), and given that generic test-time adaptive IPI search is already covered by [`agentic-prompt-injection-search`](../skills/agentic-prompt-injection-search/SKILL.md) and utility-to-IPI benchmark conversion by [`owner-authority-ipi-eval-construction`](../skills/owner-authority-ipi-eval-construction/SKILL.md), MobileProbe is captured here as a defensive Research Brief while contributing empirical GUI reachability and stealth-hijacking rules to `output/rules/`.
