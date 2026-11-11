# Cognitive Multi-Agent Search and Rescue: Language-Grounded Hierarchical Reinforcement Learning for Collaborative Robotics

> **Source**: [arXiv:2611.13161](https://arxiv.org/abs/2611.13161) — Sepideh Ravanbakhsh, Hamidreza Moradi (2026)
> **Praxis Source ID**: `src:2611-13161v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

This paper proposes **`LG-HRL`** (*Language-Grounded Hierarchical Reinforcement Learning*), a domain-specific multi-robot training architecture formalized as a **Language-Grounded Multi-Agent Hierarchical Decision Process (`LG-MAHDP`)** for heterogeneous UAV/UGV disaster search-and-rescue (`SAR`) in a 2D Python/Gymnasium grid simulation. Per our triage criteria in [`AGENTS.md`](../AGENTS.md), custom actor-critic reinforcement learning pipelines coupled to simulated robotics reward shaping do not transfer as standalone, reusable coding-agent procedures—and, as documented in the methodological caveats below, the manuscript omits critical implementation specifications (exact LLM backbone identity, grid dimensions, and code release) needed to reproduce the pipeline directly. We record its three-tier cognitive workspace formulation and reported ablation trends here as contextual reference alongside [`planner-controller-decoupling`](./planner-controller-decoupling.md) and [`orch-collective-intelligence`](./orch-collective-intelligence.md).

---

## Architectural Overview: `LG-MAHDP` and the Shared Cognitive Workspace

`LG-HRL` decomposes heterogeneous multi-robot control (`2` reconnaissance UAVs with wide-area vision + `2` rescue UGVs with Victim extraction/debris navigation) across three coupled layers over $\mathcal{M} = (\mathcal{S}, \mathcal{A}_1, \dots, \mathcal{A}_n, \Omega, \beta, P, R, \gamma)$:

1. **Language Grounding Operator ($L : V \to C$)**:
   - Translates unstructured human operator instructions or peer messages $V$ (e.g., *"Search collapsed building near northern road; avoid unstable area on east side"*) into structured symbolic subgoals and spatial/risk constraints $C_t \subseteq \Omega$ (`Search(zone)`, `Avoid(region)`, `Assist(agent, zone)`).
2. **Shared Cognitive Workspace ($B_t = \{s_t^1, \dots, s_t^n, C_t, M_t, H_t\}$)**:
   - Maintains a joint belief state combining local robot states $s_t^i$, active linguistic constraints $C_t$, a topological/grid **semantic map** $M_t$ updated via confidence-weighted fusion, and compact dialogue history $H_t$.
   - Computes a **semantic attention projection** $\Psi(C_t, M_t) = \text{softmax}(W_a [E(C_t); E(M_t)])$ that weights spatial map cells by linguistic goal relevance before feeding the high-level meta-controller.
3. **Bi-Level Policy Hierarchy ($\pi^H$ + $\pi_i^L$)**:
   - **High-level meta-controller** $\pi^H(\omega_t \mid B_t)$ assigns temporally extended options $\omega_t^i \in \Omega$ with termination condition $\beta_\omega(s_t^i)$ and an alignment regularizer $\mathcal{L}_{\text{align}} = \| E(\omega_t) - E(C_t) \|_2^2$.
   - **Low-level actor-critic controllers** $\pi_i^L(a_t^i \mid s_t^i, \omega_t^i)$ execute primitive navigation/rescue actions under composite reward $R_t = \lambda_1 R_{\text{victim}} + \lambda_2 R_{\text{explore}} - \lambda_3 R_{\text{hazard}} + \lambda_4 R_{\text{comm}}$ ($\gamma = 0.995$, actor learning rate $\alpha = 0.0005$, critic learning rate $\alpha = 0.001$, $\varepsilon$ annealed `1.0 -> 0.02` over `2,000` episodes $\times$ `20` runs).

---

## Reported Simulation Results (`4` Robots, `2,000` Episodes $\times$ `20` Runs)

Against **`Flat RL`** (joint/independent primitive-action actor-critic without options or language) and ungrounded **`HRL`** (two-level options without language grounding $L$ or shared semantic workspace $B_t$):

| Metric | `Flat RL` | Ungrounded `HRL` | **`LG-HRL` (Proposed)** | Reported Relative Gain |
|:---|:---:|:---:|:---:|:---|
| **Convergence Episodes** | `~1,200–1,400` | Intermediate | **`~600–700`** | **`2.3x` faster** sample efficiency |
| **Spatial Coverage (%)** (Table 1) | `63.4%` | `78.2%` | **`92.5%`** | `+14.3 pp` over `HRL` / `+29.1 pp` over `Flat RL` |
| **Cell Revisit Index** (lower is better) | `2.10` | `1.75` | **`1.20`** | **`37%` path-overlap reduction** (`+37%` coordination coherence) |
| **Unexplored Dead-Zone Ratio (%)** | `36.6%` | `21.8%` | **`7.5%`** | `-14.3 pp` vs. `HRL` |
| **Subgoal Completion Accuracy** | — | `~60%` | **`~90%`** | **`+46%`** relative improvement |
| **Hazard Avoidance Rate** | — | `~55%` | **`> 70%`** | **`+31%`** relative improvement |
| **Victim Rescue Success (`5` scenarios)** | `55%–62%` | `65%–70%` | **`88%–92%`** | **`+20%–30%`** higher rescue completion |
| **Mid-Episode Verbal Re-Tasking (`1–2` steps)** | Fails / slow | `~50%` | **`~70%–72%`** | Adapts to dynamic human hazard/priority updates without retraining |

**Component Ablations**:
- Removing the **shared cognitive workspace ($B_t$)** (isolated per-robot language conditioning without shared belief/map fusion) dropped normalized mission performance to **`~55%`**, reintroducing redundant UAV/UGV zone sweeps.
- Removing **language grounding ($L$ & $\mathcal{L}_{\text{align}}$)** while keeping the shared map dropped normalized performance to **`~62%`**, degrading mid-episode operator re-tasking and semantic hazard avoidance.

---

## Methodological & Reproducibility Caveats

Treat the quantitative magnitudes above as **illustrative simulation trends rather than production-calibrated benchmarks**:
1. **Unspecified LLM & Parser Implementation**: The paper never names which LLM checkpoint, prompt template, latency budget, or symbolic grammar implements $L : V \to C$ and embedding $E(\cdot)$ across the `2,000`-episode training loop, nor does it release source code or exact grid dimensions/obstacle densities.
2. **Manuscript Quality Artifacts**: Several figure captions retain raw plotting-prompt text (`"(scientific matplotlib style)"`), and Section 2.1 contains roughly two dozen off-domain citations (spanning medical imaging, power grids, and financial forecasting) mixed into generic background prose. Consequently, we do **not** promote quantitative thresholds from this paper into always-active rules in [`multi-agent-coordination.md`](../rules/multi-agent-coordination.md).

---

## Engineering Takeaways (Conceptual)

- **Translate free-form human updates into typed option constraints on a shared belief map, not raw low-level policy prompts**: Decoupling natural-language operator intent ($V \to C_t$) from primitive actuation ($\pi_i^L$) via a shared spatial/belief workspace lets mid-episode verbal hazard updates redirect subgoal selection within `1–2` macro-steps without destabilizing low-level motor/navigation controllers.
- **Shared state + role-typed subgoals curb redundant exploration**: Even with language-grounded goals, removing shared workspace state (`M_t, H_t`) caused the steepest ablation drop (`~55%` normalized score) because heterogeneous reconnaissance and responder agents reverted to overlapping search trajectories.

---

## Related Artifacts

- **Rules**:
  - [`multi-agent-coordination.md`](../rules/multi-agent-coordination.md) — Shared workspace state, natural-language inter-agent interfaces, and topology coordination guardrails
- **Research Briefs**:
  - [`planner-controller-decoupling`](./planner-controller-decoupling.md) — Separating high-level semantic planning from real-time low-level control loops
  - [`orch-collective-intelligence`](./orch-collective-intelligence.md) — Organizational principles for embodied multi-agent collective intelligence
  - [`embodied-vla-skill-orchestration`](./embodied-vla-skill-orchestration.md) — Proposal-validation-recovery runtime architecture for embodied robotics agents
