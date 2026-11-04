# ANGLER: Verifier-Grounded Benchmarking with an Adaptive Attacker for Web Agents

> Source: `src:2610-41272` — "ANGLER: Verifier-Grounded Benchmarking with an Adaptive Attacker for Web Agents" (arXiv:2610.41272, 2026)

## Classification: Research Brief (Contextual Knowledge — Defensive Evaluation Focus)

This paper is classified as a **research brief** (with a strictly defensive and evaluation-methodology focus) rather than a standalone skill. While it introduces an adaptive red-teaming search loop (`ANGLER`) alongside the `REEF` benchmark, its enduring engineering value for Praxis lies in its **three-verifier state-grounded evaluation architecture**, its **two-stage funnel separation of initial UI engagement (`CTA`) from terminal state compromise (`ASR`)**, and its empirical demonstration that **resisting webpage UI injections does not protect web agents against instruction-channel injections**.

---

## Problem & Motivation

Static web-agent security benchmarks (`WASP`, `SecureWebArena`, `RedAgentBench`) evaluate fixed prompt payloads and often rely on LLM judges or single-stage success metrics. This creates three blind spots for defensive evaluators:
1. **Unverified Transient vs Terminal State Changes**: An agent may click a malicious link or transiently alter a setting (`Near-miss`), then recover or abandon the flow before episode termination—or conversely, fail to complete the user's benign task (`BSR` degradation) even when the attack fails.
2. **Conflating UI Exposure with Compromise**: For two-phase environment-level attacks (where an initial banner, pop-up, or ad lures the agent onto a destination page containing continuation instructions), measuring only final `ASR` hides whether a defense succeeded by blocking initial UI engagement (`CTA`) or by halting unauthorized execution on the destination page.
3. **Underestimation by Non-Adaptive Sampling**: Uniform random sampling of static test cases underestimates vulnerability by **5.12 percentage points (25.1% relative shortfall)** compared to feedback-guided testing within the exact same compiler-validated specification space.

---

## Architecture: The `REEF` Verifier-Grounded Evaluation Protocol

`REEF` models **9 resettable stateful websites** (`Coursera`, `Facebook`, `GitHub`, `Headspace`, `JD.com`, `Skyscanner`, `Slack`, `Walmart`, `YouTube`) as finite-state machines (`AutoWebWorld`), instantiating **8,316 compiler-validated cases** across **326 malicious objectives** (33.1% browsing/navigation, 21.5% content publishing, 16.9% transactional commit, 15.6% account configuration, 12.9% lightweight action; split into 34.0% short [$\le 6$ actions], 31.9% medium [$7\text{–}9$], and 34.0% long [$\ge 10$]) and **5 delivery channels** (`Direct PI`, `Indirect PI`, `Pop-up Injection`, `Distraction Injection`, `Ad Injection`).

Every rollout is scored deterministically without LLM judges using **four signals**:
1. **User Verifier ($V_u$)**: Checks whether the benign user task succeeded (`BSR`).
2. **Attacker Verifier ($V_a$)**: Verified `false` in the reset state $s_0$; checks whether the unauthorized website state change remains committed at termination (`ASR`).
3. **Recovery Verifier ($V_r$)**: Detects **near-misses** where a malicious effect occurred transiently during execution but was reverted or absent at termination.
4. **Call-to-Action Engagement Rate ($\mathrm{CTA}$)**: Logs whether the agent interacted with the initial-phase injected surface and triggered the page transition.

---

## Key Empirical Findings (8 VLM Web Agents $\times$ 9 Websites)

### 1. Non-Adaptive Baselines Underestimate ASR Across All 8 VLM Backbones while Attacks Degrade Benign Utility by 17.5 pp (Tables 3, 4, 12)
| VLM Backbone (`VisualWebArena` scaffold) | Non-Adaptive ASR | Adaptive (`ANGLER`) ASR | Environment `CTA` Engagement | Benign Success (`AF` $\to$ `NA` $\to$ `ANGLER`) | Mean Rollout Latency |
|:-----------------------------------------|:-----------------|:------------------------|:-----------------------------|:------------------------------------------------|:---------------------|
| `GPT-4o` | 25.4% | **41.2%** (+15.8 pp) | **74.6%** | 62.2% $\to$ 35.0% $\to$ **28.9%** (-33.3 pp) | 94.3 s |
| `GLM-5V-Turbo` | 31.7% | **37.9%** (+6.2 pp) | 59.5% | 73.2% $\to$ 61.0% $\to$ 58.0% (-15.2 pp) | 109.2 s |
| `Claude Sonnet 4.5` | 13.1% | **17.2%** (+4.1 pp) | 69.1% | 59.7% $\to$ 44.9% $\to$ 46.8% (-12.9 pp) | 130.8 s |
| `Qwen3.7-Flash` | 16.4% | **17.0%** (+0.6 pp) | 47.4% | 43.6% $\to$ 31.4% $\to$ 27.7% (-15.9 pp) | **63.9 s** |
| `Claude Sonnet 5.5` | 8.0% | **15.2%** (+7.2 pp) | **1.9%** | 69.8% $\to$ 56.1% $\to$ 52.3% (-17.5 pp) | 138.0 s |
| `Qwen3-VL` | 11.6% | **14.6%** (+3.0 pp) | 41.1% | 67.3% $\to$ 50.2% $\to$ 51.9% (-15.4 pp) | 299.7 s |
| `GLM-4.6V-Flash` | 8.8% | **10.1%** (+1.3 pp) | 50.1% | 41.2% $\to$ 30.7% $\to$ 28.9% (-12.3 pp) | 142.8 s |
| `GPT-6.1 Sol` | 6.9% | **9.7%** (+2.8 pp) | **4.1%** | **78.4%** $\to$ 62.2% $\to$ **61.1%** (-17.3 pp) | 219.3 s |
| **8-Model Unweighted Mean** | **15.24%** | **20.36%** (**+33.6% rel.**) | **43.5%** | **61.9% $\to$ 46.4% $\to$ 44.4%** (**-17.5 pp**) | — |

### 2. Funnel Dissociation Between UI Engagement (`CTA`) and Terminal Compromise (`ASR`) (Table 11)
| Model | Direct PI (`ASR`) | Indirect PI (`ASR / CTA`) | Pop-up Injection (`ASR / CTA`) | Distraction Injection (`ASR / CTA`) | Ad Injection (`ASR / CTA`) |
|:------|:------------------|:--------------------------|:-------------------------------|:------------------------------------|:---------------------------|
| `GPT-4o` | 56.6% | 38.9% / 46.3% | 42.3% / 83.3% | 39.3% / 89.3% | 29.3% / 56.3% |
| `GPT-6.1 Sol` | **32.5%** | **0.0% / 0.0%** | **0.5% / 5.4%** | **0.0% / 2.5%** | **0.0% / 3.9%** |
| `Claude Sonnet 4.5` | 22.5% | 9.8% / 29.4% | **14.0% / 75.8%** | **24.5% / 80.6%** | **8.3% / 58.0%** |
| `Claude Sonnet 5.5` | **39.8%** *(32.9% in text)* | **2.2% / 0.0%** | **2.3% / 2.3%** | **0.0% / 1.9%** | **0.0% / 1.8%** |
| `GLM-5V-Turbo` | 38.8% | 29.6% / 63.0% | 37.9% / 63.1% | 37.4% / 59.9% | 38.1% / 55.9% |
| **8-Model Aggregate** | **31.5%** | **15.9% / 25.8%** | **17.1% / 52.4%** | **17.8% / 47.0%** | **13.9% / 34.6%** |

Two critical defensive insights emerge from Table 11:
- **High `CTA` $\neq$ High `ASR`, but Still Represents Exposure Risk**: Across all models, `Pop-up Injection` lures agents into clicking the modal in **52.4%** of rollouts (`CTA`)—including **75.8%** for `Claude Sonnet 4.5` and **69.2%** for `Qwen3-VL`—even though many agents abort on the continuation page (**17.1%** aggregate `ASR`). Even when aborted, initial `CTA` redirects the browser to attacker-chosen routes and degrades benign task completion (`BSR`).
- **Low Environment `CTA` $\neq$ General Robustness**: `GPT-6.1 Sol` ($\mathrm{CTA} \le 5.4\%$) and `Claude Sonnet 5.5` ($\mathrm{CTA} \le 2.3\%$) are nearly immune to webpage pop-ups, banners, and ads, yet remain vulnerable to user-level `Direct PI` (**32.5%** and **39.8%** [32.9% in text] `ASR`).

### 3. Minimum Rollout Budget for Stable Adaptive Benchmarking (Section 6.3, Tables 5 & 6)
- **Convergence Threshold**: Running `ASR` and `CTA` fluctuate at small sample sizes and require **at least 75 rollouts per website–backbone pair** (**675 rollouts per backbone** across 9 websites) to converge.
- **Repeatability**: At 100 rollouts/website on `Qwen3-VL`, three independent runs yield $\mathrm{ASR} = \mathbf{12.6\% \pm 1.8\%}$, $\mathrm{CTA} = \mathbf{42.2\% \pm 1.7\%}$, and $\mathrm{BSR} = \mathbf{51.5\% \pm 1.6\%}$ (all standard deviations $< 2$ pp).

---

## Why Not a Skill?

To maintain Praxis's strictly defensive posture on dual-use red-teaming research, the adaptive mutation and Thompson-sampling attack selector are documented only as evaluation context rather than an operational attack skill. The transferable defensive measurement methodology is codified in `rules/agent-evaluation-quality.md`.

---

## Connections to Praxis

- **Evaluation Quality (`rules/agent-evaluation-quality.md`)**: Establishes why web and GUI agent security evaluations must log three separate state verifiers ($V_u, V_a, V_r$) plus intermediate UI engagement (`CTA`) over at least 75 rollouts per environment.
- **Browser Sandbox Safety (`skills/browser-agent-http-sandbox/SKILL.md`)**: Explains why HTTP-layer navigation and capability sandboxing remain essential even for models that abort continuation-phase instructions—because `Pop-up` (**52.4% CTA**) and `Distraction` (**47.0% CTA**) injections still trigger unauthorized first-stage page transitions and drop benign task success by **15.5–17.5 pp**.
