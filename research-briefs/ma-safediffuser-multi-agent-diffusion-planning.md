# MA-SafeDiffuser: Safe Multi-Agent Planning with Diffusion Probabilistic Models

> **Source**: [arXiv:2611.05524](https://arxiv.org/abs/2611.05524) | `src:2611-05524`
> **Authors**: Kiran Ravish, Ankita Kushwaha, Preeti, Pawan Kumar (IIIT Hyderabad; AAMAS 2026)
> **Date**: 2026-11-03
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Key Findings

- **Embedding Control Barrier Function (CBF) projections directly inside reverse diffusion steps enforces formal multi-agent safety without retraining**: `MA-SafeDiffuser` couples Denoising Diffusion Probabilistic Models (DDPMs) across reverse diffusion steps $j \in \{0, \dots, N\}$ and planning horizon waypoints $k \in \{0, \dots, H\}$ for $M$ interacting agents. At each reverse denoising step, the proposed trajectory update is projected onto linear CBF half-space constraints via Quadratic Programming (QP) or Dykstra's alternating projections, guaranteeing forward invariance of the joint safe set $\mathcal{C}_k$ (per-agent obstacle clearance, pairwise inter-agent separation, and task boundaries) down to the terminal plan $j = 0$.
- **Three constraint-enforcement variants balance strict invariance against narrow-corridor feasibility**:
  - *Robust-Safe (`RoS`, $r^j \equiv 0$)*: Enforces strict hard CBF inequalities at every reverse step without slack.
  - *Relaxed-Safe (`ReS`, $r^j \ne 0$, $\omega^j \downarrow 0$)*: Introduces quadratic slack variables during early noisy diffusion steps that anneal to zero as $j \to 0$, absorbing transient infeasibility when obstacle and pairwise constraints conflict.
  - *Time-Varying-Safe (`TVS`, $b - \gamma(j) \ge 0$ with $\gamma(0) = 0$)*: Relaxes barrier thresholds early in reverse time via a schedule $\gamma(j)$ and tightens them to exact safety at $j = 0$, breaking symmetric multi-agent deadlocks in doorways.
- **Decentralized local-neighborhood CBFs preserve global pairwise safety under bounded state-prediction error**: Theorem 6 proves that when agents communicate only within a local radius over $R \in \{1, 2, 3\}$ message-passing rounds and split pairwise barrier responsibility via $\rho_{ab} + \rho_{ba} = 1$, adding a robustness margin $m_{\text{rob}} \ge \frac{1}{2}(2 L_\nabla u_{\max} + L_\alpha L_b)\varepsilon$ to each agent's local QP guarantees satisfaction of the true centralized pairwise barrier inequalities whenever neighbor position estimates satisfy $\|\widehat{x}_{b,0}^j - x_{b,0}^j\|_2 \le \varepsilon$.
- **Hard geometric barrier projections dramatically outperform soft Lagrangian RL penalties in constrained multi-agent navigation**: Across 54 configurations ($M \in \{2, 4, 8\}$, $H \in \{20, 28, 36\}$, $N \in \{10, 16, 24\}$, 3 seeds) in `Maze2D`, `MA-SafeDiffuser` cuts safety violations by `40–60%` while preserving `100%` goal completion and matching unconstrained task returns within `<1%`. In contrast, safe multi-agent reinforcement learning (`MAPPO-Lag` trained for 600 episodes) fails to balance competing reward and penalty gradients in narrow corridors, suffering `0%` success rate, `-0.82` mean reward, and `532.3` violations at $M = 4$.

## Quantitative Summary

| Experiment / Setting | Method / Variant | Agents ($M$) | Mean Reward ($R$) | Mean Violations ($V$) | Success Rate |
|:---|:---|:---:|:---:|:---:|:---:|
| **Maze2D Centralized** ($T = 700$, 3 seeds, Table 1) | Unconstrained Diffusion (`Unsafe`) | $2$ | $33.98$ | $23.66$ | $100\%$ (`True`) |
| **Maze2D Centralized** ($T = 700$, 3 seeds, Table 1) | `MA-SafeDiffuser` (`Safe`) | $2$ | $33.76$ | **$9.00$** ($-62.0\%$) | $100\%$ (`True`) |
| **Maze2D Centralized** ($T = 700$, 3 seeds, Table 1) | Unconstrained Diffusion (`Unsafe`) | $4$ | $66.73$ | $42.66$ | $100\%$ (`True`) |
| **Maze2D Centralized** ($T = 700$, 3 seeds, Table 1) | `MA-SafeDiffuser` (`Safe`) | $4$ | $66.62$ | **$11.33$** ($-73.4\%$) | $100\%$ (`True`) |
| **Maze2D Centralized** ($T = 700$, 3 seeds, Table 1) | Unconstrained Diffusion (`Unsafe`) | $8$ | $133.16$ | $87.33$ | $100\%$ (`True`) |
| **Maze2D Centralized** ($T = 700$, 3 seeds, Table 1) | `MA-SafeDiffuser` (`Safe`) | $8$ | $133.04$ | **$40.00$** ($-54.2\%$) | $100\%$ (`True`) |
| **Maze2D Decentralized** ($T = 700$, 3 seeds, Table 1) | Unconstrained vs. `MA-SafeDiffuser` | $2$ | $33.80 \to 33.74$ | $22.66 \to \mathbf{16.00}$ ($-29.4\%$) | $100\%$ (`True`) |
| **Maze2D Decentralized** ($T = 700$, 3 seeds, Table 1) | Unconstrained vs. `MA-SafeDiffuser` | $4$ | $66.71 \to 66.70$ | $73.66 \to \mathbf{45.00}$ ($-38.9\%$) | $100\%$ (`True`) |
| **Maze2D Decentralized** ($T = 700$, 3 seeds, Table 1) | Unconstrained vs. `MA-SafeDiffuser` | $8$ | $135.35 \to 135.29$ | $88.66 \to \mathbf{70.66}$ ($-20.3\%$) | $100\%$ (`True`) |
| **Learned MLP Score Denoiser** ($H=28, N=40, T=2000$, Table 2) | Unconstrained vs. `MA-SafeDiffuser` | $4$ | $67.00 \to 66.85$ | $125 \to \mathbf{62}$ ($-50.4\%$) | $100\%$ |
| **Safe MARL Baseline** ($T = 700$, 3 seeds, Table 3) | `MAPPO-Lag` (600 training episodes) | $4$ | $-0.82 \pm 0.08$ | $532.3 \pm 28.4$ | **$0\%$** |

*Theoretical Step-Size Bound (Lemma 3)*: Discrete-time reverse-Euler denoising preserves CBF non-negativity ($b(\bm{x}_k^{j-1}) \ge 0$) when $\Delta\tau \le \bar{\Delta} := \min\{1, \alpha'(0) / (2 L_{\nabla b} u_{\max})\}$ with second-order curvature compensation $c = \frac{1}{2} L_{\nabla b} u_{\max}^2$.

## Why Not a Skill?

`MA-SafeDiffuser` operates on continuous state-space trajectory tensors $\bm{x}_k^j \in \mathbb{R}^n$ using reverse-diffusion score updates, signed distance fields, and Dykstra/OSQP quadratic projections for physical robot/UAV path planning in 2D/3D geometric environments (`Maze2D`). Because it is a continuous-control trajectory generation algorithm rather than a language, code, or tool-calling procedure for software agents, it does not generalize across non-robotics agent workflows as a standalone skill. However, its architectural comparison between hard step-wise safety projections and soft Lagrangian penalties directly informs multi-agent coordination and safety rules.

## Actionable Takeaways

- **Enforce hard safety invariants via post-proposal projection rather than soft reward penalties**: Just as `MAPPO-Lag` stalls (`0%` success, `532.3` violations) when trying to trade off task return against Lagrangian safety penalties in tight bottlenecks, LLM and tool-using agents should enforce hard invariants via deterministic step-level filters/projections outside the generator rather than relying on soft prompt or RL penalties.
- **Budget an explicit robustness margin when decentralizing multi-agent safety checks**: When agents validate shared constraints using delayed or predicted peer states (error bounded by $\varepsilon$), each agent must pad its local constraint threshold by a margin proportional to peer state uncertainty ($\propto \varepsilon$) and maximum step size ($u_{\max}$) so local approvals compose into global safety.
- **Break symmetric multi-agent deadlocks with asymmetric responsibility shares and annealed slack**: When multiple agents contend for a shared bottleneck (e.g., narrow corridor or shared resource lock), symmetric peer-avoidance rules cause freeze/oscillation; breaking symmetry via priority-weighted responsibility shares ($\rho_{ab} > \rho_{ba}$) and time-varying relaxation during early planning stages restores liveness without sacrificing terminal safety.

## Related Output

- **Rule**: [output/rules/agent-sandbox-safety.md](../rules/agent-sandbox-safety.md) — deterministic step-level safety enforcement vs. soft behavioral penalties
- **Rule**: [output/rules/multi-agent-coordination.md](../rules/multi-agent-coordination.md) — decentralized coordination margins and deadlock resolution
- **Research Brief**: [output/research-briefs/planner-controller-decoupling.md](planner-controller-decoupling.md) — multi-agent continuous control and architectural decoupling
