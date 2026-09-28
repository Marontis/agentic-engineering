# Multi-Turn Consistency via Survival Analysis and Failure-Rationale Taxonomy

> **Source**: Bogdanov, Manakina, Lung et al., arXiv:2609.29508, Sep 2026
> **Status**: Research Brief — evaluation methodology and controlled empirical study

## Why Not a Skill?

The paper contributes an evaluation lens: time-to-failure modeling plus a taxonomy of pre-failure rationales, applied to a toy 20-step claim-or-defer task. It is useful context for designing long-horizon evals, but the environment is deliberately minimal and the authors say it is not a deployment proxy. No transferable agent procedure is proposed.

## Core Concept

Terminal success rates hide *when* agents abandon a commitment. The authors turn a delayed-gratification task into a 20-step episode. At each step the agent either Defers (continue, +2 at the horizon) or Claims (+1 now, episode ends). They then treat the first Claim as a time-to-event outcome: Kaplan–Meier survival curves, restricted mean survival time, and a discrete-time logistic hazard model with step dummies. For every early termination they label the final thought trace with a seven-category rationale codebook and extract linguistic features, including a rule-based self-contradiction flag (the same trace argues both to wait and to claim).

## Key Findings

- **Scale**: 84,540 trajectories across 8 models (Gemini-2.5-Flash-Lite, Claude-3-Haiku, GPT-4o-mini, Qwen3-235B, GPT-OSS-20B, DeepSeek-3.1, Llama-3.1-8B, Devstral-Small-2505) in a 64-cell full-factorial design. 99.98% of terminal actions were valid. 14,025 agents (17.6%) claimed early. 13,780 traces were labeled; LLM labels agreed with a human audit at κ = 0.83.
- **Survival shape**: a sharp early spike (6.2% claim at step 1) followed by a low-risk tail. Median time-to-event 17 steps, RMST 16.47.
- **Personas dominate the hazard**: relative to an adult persona, a child persona has OR = 8.65 and a senior persona OR = 5.60. The "crave" hedonic persona also raises risk: "none" vs "crave" has OR = 0.24. Social visibility (isolated vs broadcast) had no effect on hazard (OR 0.99, p = .514), though broadcast changed the stated reasons (5.0% Social Contagion vs 0%). Mandatory self-questioning slightly raised hazard (OR 1.10).
- **Rationales shift over time**: early failures (steps 0–5) are 42.6% Impulse/Craving. Late failures (steps 14–19) are 42.4% Cost-Benefit and 19.7% Fatigue, with Impulse at 16.0%.
- **More reasoning, more contradiction (weak effect)**: the self-contradiction rate rises from 0.43% in the lowest reasoning-density quartile to 1.89% in the highest (Spearman ρ = 0.040). Late failures have higher argument density than early ones (3.74 vs 3.02). The authors read this as evidence that elaborate traces are not a reliability signal.
- **Model regimes**: near-flat hazard (Claude-3-Haiku, GPT-4o-mini, Qwen3-235B, contradiction rates 0.0–0.5%), early-spike (Gemini-2.5-Flash-Lite, GPT-OSS-20B), and bi-modal late-vulnerable (Devstral-Small-2505 with the highest contradiction rate at 4.6%; Llama-3.1-8B).

## Relevance to Praxis

- Adds a time-resolved metric to `rules/agent-sandbox-safety.md` "DON'T: Rely on single-turn refusal or initial benign turns to evaluate long-horizon safety". Report survival curves or hazard by step, not only end-of-episode pass rates, when an agent must hold a commitment over many turns.
- Consistent with `rules/agent-human-interaction.md` "DON'T: Assume stable safety behavior across interaction modes". Persona framing in the system prompt moved failure odds by up to 8.65×, far more than social visibility.
- Weak support for not using chain-of-thought length or density as a reliability proxy. The effect size (ρ = 0.040) is too small to justify a standalone rule.
- Caveats: binary action space, temperature 0.5, self-reported rationales treated as behavioral text rather than mechanism, and older and smaller model versions.

> Source: Bogdanov et al., "Evaluation of Multi-Turn Consistency in LLM Agents: Survival Analysis and Failure-Rationale Taxonomy" (arXiv:2609.29508)
