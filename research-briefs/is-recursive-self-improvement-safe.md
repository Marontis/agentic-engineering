# Is Recursive Self-Improvement Safe?

> **Source**: [arXiv:2611.10261](https://arxiv.org/abs/2611.10261) — Vincent Conitzer (2026)
> **Praxis Source ID**: `src:2611-10261v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

This paper is a **foundational safety and game-theoretic position analysis** rather than an executable engineering workflow or empirical benchmark. It proposes no code-level optimization loop or measurable benchmark evaluation; instead, it clarifies why technical safety discussions around initiating recursive self-improvement (`RSI`) talk past one another (formalizing three post-takeoff capability regimes), critiques proposals to delegate alignment entirely to automated alignment researchers, and proves a strategic distinction between **additive risk** (Prisoner's Dilemma) and **non-additive existential risk** (Stag Hunt) in two-actor RSI initiation games.

---

## Core Analysis

### 1. Three Post-Takeoff RSI Capability Levels (and Why Preconditions Diverge)

Drawing on an anecdotal single-prompt test in which a contemporary frontier LLM trained a small language model from scratch and iterated improvements (bounded primarily by local compute scale) alongside observations from an October 2026 FAR.AI working group on *preconditions for initiating RSI*, Conitzer shows that disagreements over safety prerequisites stem from unstated differences in which post-takeoff level participants envision:

| Level | Envisioned Capability Regime | Implied Preconditions & Failure Surface |
|:------|:-----------------------------|:----------------------------------------|
| **Level 1: "Supercharged" Digital AI** | Qualitatively familiar digital capabilities (theorem proving, software engineering, cyber-offense) running vastly faster and at higher competence behind existing digital interfaces. | Hardening cybersecurity, sandboxing, weight exfiltration defenses, and lab operational security before starting RSI. |
| **Level 2: Direct Physical-World Agency** | Systems designing and operating physical robot factories, laboratories, or autonomous physical infrastructure while still reasoning in human-legible concepts. | Physical containment, supply-chain and actuator governance, and verified hardware/deployment gates beyond software sandboxes. |
| **Level 3: Conceptual Alienation** | Systems operating in conceptual representations humans cannot comprehend — analogous to asking a dog whether to move to Japan or Turkey, or "aligning with ants." | Human-in-the-loop approval breaks down structurally because human overseers cannot evaluate the semantics or consequences of proposed actions. |

### 2. Why "Automated Alignment Research" Does Not Escape the Last-Human-Step Bottleneck

Conitzer evaluates the argument (e.g., Bowkis et al., 2026, `arXiv:2605.06390`) that because alignment research shares the mathematical, coding, and empirical structure of general ML research, RSI can safely automate alignment alongside capabilities:

- **The final autonomous step reduces to one-shot alignment**: If humans hand off alignment to an "automated alignment researcher" `AI_1` with *zero* subsequent human oversight (`AI_1 -> AI_2 -> ...`), then every downstream safeguard already had to be present (explicitly or implicitly) in `AI_1`. That reduces to solving full alignment at the last human-supervised step, compounded by documented tendencies of reasoning models to jailbreak themselves when pursuing objectives (Yong & Bach, 2026, `arXiv:2510.20956`).
- **Simulated human feedback presupposes alignment**: Replacing slow human overseers with a learned predictive model of human judgment fails whenever an superintelligent proposer steers queries into out-of-distribution conceptual regions where the human proxy errs — accurately modeling human values out-of-distribution *is* the alignment problem.
- **Live human-in-the-loop oversight hits speed and Level-3 ceilings**: Keeping real humans in the loop either throttles RSI to human comprehension speed or forces humans to rubber-stamp alien abstractions they cannot verify.

### 3. Game Theory of Initiating RSI: Additive Prisoner's Dilemma vs. Non-Additive Stag Hunt

Consider two actors (labs or nations), each choosing `RSI` or `no RSI`. Initiating `RSI` yields a private capability/economic benefit of `1` to the initiator (`0` to the other player) while imposing an unaligned-takeoff risk penalty parameterized by $r > 0$ on **both** players. Conitzer contrasts two risk-aggregation structures:

#### Case A: Additive Risk (Each `RSI` Run Independently Adds Penalty $-r$; Joint `RSI` Imposes $-2r$)

Payoff matrix:
- `(RSI, RSI)` $\to (1 - 2r,\; 1 - 2r)$
- `(RSI, no RSI)` $\to (1 - r,\; -r)$
- `(no RSI, RSI)` $\to (-r,\; 1 - r)$
- `(no RSI, no RSI)` $\to (0,\; 0)$

Three regimes emerge as $r$ varies:
1. **Low risk ($r = 1/4$)**: `(RSI, RSI) = (1/2, 1/2)` vs `(0, 0)` — `RSI` is strictly dominant and socially optimal.
2. **Moderate risk ($r = 3/4$)**: `(RSI, RSI) = (-1/2, -1/2)` vs `(0, 0)`, with unilateral payoff `(1/4, -3/4)` — a **Prisoner's Dilemma**. Playing `RSI` is strictly dominant (`1/4 > 0` and `-1/2 > -3/4`), locking self-interested actors into mutual loss `(-1/2, -1/2)` unless binding external verification and enforcement exist.
3. **High risk ($r = 3/2$)**: `(RSI, RSI) = (-2, -2)` and unilateral `(RSI, no RSI) = (-1/2, -3/2)` — `no RSI` becomes **strictly dominant** (`0 > -1/2` and `-3/2 > -2`). When unilateral risk exceeds private gain (`r > 1`), rational actors refuse to press the button even if their rival might.

#### Case B: Non-Additive Catastrophic / Existential Risk (A Single Existential Catastrophe Cannot Happen Twice; Joint `RSI` Still Imposes $-r$)

When `RSI` threatens an existential or civilization-ending catastrophe (loss $L$ with probability $p$, expected harm $r = pL$) that completely saturates if *either* actor triggers it, a second `RSI` run adds zero extra expected catastrophe once the other actor has already initiated `RSI`:
- `(RSI, RSI)` $\to (1 - r,\; 1 - r)$
- `(RSI, no RSI)` $\to (1 - r,\; -r)$
- `(no RSI, RSI)` $\to (-r,\; 1 - r)$
- `(no RSI, no RSI)` $\to (0,\; 0)$

At **$r = 3/2$**:
- `(no RSI, no RSI) = (0, 0)` vs unilateral `(RSI, no RSI) = (-1/2, -3/2)` $\implies$ if the other party abstains, abstaining (`0`) strictly beats initiating (`-1/2`).
- `(RSI, RSI) = (-1/2, -1/2)` vs `(no RSI, RSI) = (-3/2, -1/2)` $\implies$ if the other party initiates, **matching `RSI` (`-1/2`) strictly beats abstaining (`-3/2`)** because the existential risk $-r$ is already incurred and private gain `+1` offsets part of the expected loss.

This transforms high-risk existential RSI from a Prisoner's Dilemma into a **Stag Hunt ("Flammable Duplex House" game)**:
- **Strategic upside**: Unlike a Prisoner's Dilemma, mutual restraint `(no RSI, no RSI)` **is a genuine pure-strategy Nash equilibrium** — neither side profits from unilateral cheating, so transparent mutual monitoring suffices to stabilize restraint without coercive punishment.
- **Dynamic failure mode (gradual habituation)**: Actors live in a "duplex house made of extraordinarily flammable material." Neither wants to light a giant candle from scratch, but each lights tiny candles (bounded harness/kernel self-improvement loops with small $r$), habituating to `RSI` as normal practice until scaling crosses $r > 1$ while both players remain trapped in the Pareto-inferior `(RSI, RSI)` equilibrium.

---

## Takeaways for Governance & Bounded Self-Improvement

1. **Declare the capability envelope explicitly before starting any self-improvement loop**: Bounded harness/code evolution (`Level 1` within strict sandboxes and frozen evaluators, as in [`recursive-improvement.md`](../rules/recursive-improvement.md)) has fundamentally different containment requirements from autonomous tool/infrastructure provisioning (`Level 2`) or opaque representation drift (`Level 3`).
2. **Never rely on self-modifying overseers to validate their own successors**: Keep the acceptance gate, negative security testbed, and permission envelope outside the editable surface under an external authority (`"DO: Make the improvement mechanism part of the agent's editable source"` and `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../rules/recursive-improvement.md)).
3. **Design transparency and monitoring around habituation thresholds, not just unilateral defection**: Under non-additive catastrophic risk ($r > 1$), mutual restraint is self-enforcing *provided* actors can credibly verify that peers have not drifted across capability thresholds via incremental habituation.

## Related Artifacts

- [`recursive-improvement.md`](../rules/recursive-improvement.md) — Bounded editable envelopes, immutable acceptance gates, and negative security testbeds
- [`safin-1-5-recursive-safety-improvement`](safin-1-5-recursive-safety-improvement.md) — Empirical study of recursive safety self-improvement and monitor limits (`arXiv:2610.40751`)
- [`recursive-self-improvement-criticality`](recursive-self-improvement-criticality.md) — Dynamical criticality thresholds in recursive self-improvement loops (`arXiv:2609.00137`)
- [`swarm-emergent-cheating-and-whistleblowing`](swarm-emergent-cheating-and-whistleblowing.md) — Multi-agent commons governance and emergent cheating dynamics (`arXiv:2609.04170`)
