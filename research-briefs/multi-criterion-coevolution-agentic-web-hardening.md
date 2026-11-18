# Hardening Agentic Web Populations via Multi-Criterion Competitive Co-Evolution

> **Paper**: [Hardening Agentic Web Populations Through Multi-Criterion Competitive Co-Evolution: Lessons from Wargame Strategy Optimization](https://arxiv.org/abs/2611.19319) (Raj & Deb, 2026 — 1st NeurIPS Workshop on Agentic Web)
> **Praxis source**: `src:2611-19319v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Summary

Raj and Deb present a **workshop position paper** (`§1`: *"Our contribution here is a position, not a new algorithm"*) arguing that static benchmark suites and single-scalar red-teaming loops structurally under-prepare web agents for open-ended adversarial ecosystems. Drawing on multi-criterion competitive co-evolution results from automated wargaming (`Guha et al., 2024, 2025a, 2025b`; `Raj et al., 2026a, 2026b`) built on **NSGA-II** (`Deb et al., 2002`), they propose hardening defender agent populations against evolving adversarial populations over explicit **Pareto trade-off fronts** rather than collapsed weighted-sum scores.

---

## Core Conceptual Framework & Transferable Diagnostics

### 1. Alternating Two-Population Multi-Criterion Co-Evolution (`§3.1–3.2`, `Eq. 1`)

Instead of optimizing a single defense configuration against a frozen attack dataset—or optimizing against a single latest adversary (which causes cyclic forgetting and single-rival overfitting)—the framework maintains two populations of size $N_{\mathrm{off}}$ and $N_{\mathrm{def}}$ evolving in alternating phase windows $[\tau_{\mathrm{off}}, \tau_{\mathrm{def}}]$:

- **Full Cross-Play Evaluation Tensor (`Eq. 1`)**: At generation $t$, every candidate in the active population is evaluated against **diverse representatives of the opposing population**, producing a four-objective outcome tensor $\mathbf{F}^t \in \mathbb{R}^{N_{\mathrm{off}} \times N_{\mathrm{def}} \times 4}$ with pairwise entries:
  $$\mathbf{F}^t_{i,j} = \bigl[f_1^{\mathrm{off}},\, f_2^{\mathrm{off}},\, f_1^{\mathrm{def}},\, f_2^{\mathrm{def}}\bigr]^T$$
  For web-agent security, defensive criteria naturally separate **attack mitigation** ($f_1^{\mathrm{def}}$, e.g., blocking prompt injection, deceptive UI traps, or collusive manipulation) from **benign task utility / low false-refusal cost** ($f_2^{\mathrm{def}}$, e.g., completion speed, resource efficiency, and legitimate action acceptance), while adversarial stress-testing tracks **evasion/effectiveness** ($f_1^{\mathrm{off}}$) alongside **stealth / query budget** ($f_2^{\mathrm{off}}$).
- **Pareto Front Preservation Over Scalarization**: Combining safety and false-refusal rate into one arbitrary scalar weight hides catastrophic operating points until deployment. Non-dominated sorting (`NSGA-II`) maintains a **Pareto-optimal portfolio** of defensive policies ranging from conservative high-security postures (for high-stakes financial/admin actions) to low-friction postures (for low-risk browsing), letting operators switch policies at runtime without retraining.

### 2. The Hypervolume `Movement` Diagnostic (`§3.2`, `Eq. 2`)

In co-evolutionary red-teaming, raw win rate or raw attack success rate is non-stationary because the opponent population is simultaneously changing—an unchanged score can mask either genuine hardening or mutual stagnation/cycling. Raj and Deb transfer a scalar diagnostic from multi-criterion wargaming (`Raj et al., 2026a`):

$$\mathrm{Movement} = \mathrm{HV}_{\mathrm{coop}} - \mathrm{HV}_{\mathrm{coev}}$$

where $\mathrm{HV}_{\mathrm{coop}}$ is the Pareto hypervolume achieved when a population optimizes against a static/cooperative baseline and $\mathrm{HV}_{\mathrm{coev}}$ is its hypervolume under live adversarial co-evolution:
- **Large positive `Movement`** indicates that live adversarial pressure is actively compressing the opponent's achievable Pareto front—confirming genuine competitive discovery rather than benchmark saturation.
- **Near-zero `Movement`** warns that co-evolution has stalled into uninformative drift or disjoint niches and requires archive injection or diversity restoration.

### 3. Open Scaling & Governance Bottlenecks on the Agentic Web (`§4–5`)

The paper highlights four unresolved barriers before wargame co-evolution can run directly on full LLM web agents:
1. **$N_{\mathrm{off}} \times N_{\mathrm{def}}$ Evaluation Cost vs. Surrogate Fidelity**: Full cross-play over multi-turn LLM browser trajectories is prohibitively expensive, yet cheap surrogate fitness models risk misranking novel semantic exploits unless periodically re-anchored on live rollouts.
2. **Asynchronous Multi-Lineage Credit Assignment**: Open web ecosystems contain many heterogeneous agent lineages interacting asynchronously rather than two centrally scheduled synchronous populations.
3. **Manipulation-Resistant Trust & Reputation**: Co-evolving reputation mechanisms in mixed cooperative-competitive web markets must resist strategic sybil praise and collusive rating manipulation.
4. **Strict Dual-Use Containment (`§5`)**: Because competitive co-evolution inherently breeds stronger offensive test strategies alongside hardened defenders, any stress-testing harness must enforce sandboxed execution and strict access controls on evolved attacker archives, publishing only defensive policies and aggregate robustness metrics.

---

## Why Not a Skill?

This is a `4`-page workshop position paper with **zero empirical LLM or web-agent experiments**, no concrete prompt/policy mutation operators, and no validated surrogate-budgeting schedule for `N_off x N_def` LLM rollouts. Concrete, empirically tested procedures for iterative adversarial red-teaming and co-evolutionary defense are already covered in [`self-improving-red-team`](../skills/self-improving-red-team/SKILL.md) (`SIR`, `arXiv:2608.30207`), [`closed-loop-adaptive-red-teaming`](../skills/closed-loop-adaptive-red-teaming/SKILL.md) (`CART`, `arXiv:2609.27336`), and [`codel-latent-injection-coevolution`](codel-latent-injection-coevolution.md) (`CoDeL`, `arXiv:2609.34463`). Its high-value conceptual insights—evaluating defender populations across an adversary archive rather than a single rival, preserving safety-vs-false-refusal Pareto fronts via non-dominated sorting, and tracking `Movement = HV_coop - HV_coev` to distinguish true hardening from arms-race stagnation—serve as design context supporting our adversarial evaluation rules in [`agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md).

---

## Related Artifacts

- **Rule**: [Agent Sandbox Safety](../rules/agent-sandbox-safety.md)
- **Rule**: [Agent Evaluation Quality](../rules/agent-evaluation-quality.md)
- **Skill**: [Self-Improving Red Team](../skills/self-improving-red-team/SKILL.md)
- **Skill**: [Closed-Loop Adaptive Red Teaming](../skills/closed-loop-adaptive-red-teaming/SKILL.md)
- **Research Brief**: [CoDeL: Latent Injection Co-Evolution](codel-latent-injection-coevolution.md)
- **Research Brief**: [AI Paper Review Arms Race](ai-paper-review-arms-race.md)
