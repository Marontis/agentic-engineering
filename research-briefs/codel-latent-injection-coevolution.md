# CoDeL: Latent Prompt Injection and Co-Evolutionary Defense Training

> **Source**: Yang, Ou, Gao, Wang, Ying & Liu, "CoDeL: Co-Evolutionary
> Defense against Indirect Prompt Injection in LLM-based Agents",
> [arXiv:2609.34463](https://arxiv.org/abs/2609.34463), Sep 2026
> **Status**: Research Brief, model-training defense evaluated on 7-8B
> open-weight agents.

## Why Not a Skill?

CoDeL is a training recipe (search-based attack mining plus LoRA
fine-tuning of the agent model with a custom policy-optimization
objective). It needs a training budget and open weights, and its value is
mostly in two findings that apply to anyone evaluating an injection
defense, not in a procedure most teams would rerun.

## Core Concept

Many injection defenses are trained or tuned on **explicit** injections,
where the malicious instruction is obvious and the agent deviates right
after reading it. The paper measures **attack latency**: the number of
rounds between the payload becoming visible and the agent first deviating
from the user's task. Latent injections fold the malicious goal into a
plausible workflow and let several normal tool calls happen first.
Defenses fitted to explicit cues miss them.

CoDeL trains attacker and defender against each other: each round, a
tree-search attacker mines injections that are both successful and
high-latency against the current defender, and the defender is updated on
them. The defender's reward scores refusing the injection and making
progress on the user's task as separate terms, so abandoning the task
cannot earn safety.

## Key Findings

Defender backbones Qwen2.5-7B-Instruct and Llama-3.1-8B-Instruct;
benchmarks AgentDojo, InjecAgent, ASB-OPI and the new LatentDojo (132
attack and 18 clean scenarios). ASR = attack success, BU = benign utility,
UA = utility under attack.

- **Explicit-only evaluations overstate defenses.** Rewriting 48 AgentDojo
  attacks to be latent raised ASR from 0.062 to 0.208 (Meta-SecAlign),
  0.083 to 0.542 (TSGuard) and 0.146 to 0.333 (PIGuard).
- **Headline (AgentDojo, Qwen backbone)**: ASR 0.042, BU 0.779, UA 0.831.
  For comparison, SecOPD reached ASR 0.046 but with BU 0.273 and UA
  0.343; Meta-SecAlign had ASR 0.068, BU 0.456, UA 0.602. The abstract
  reports an 88.5% ASR reduction and +38.0% over baselines. CoDeL did not
  win everywhere: on ASB-OPI, AgentAlign had lower ASR (0.029 versus
  0.043) and MELON higher UA (0.957 versus 0.913).
- **Guardrails bought ASR with utility**: TSGuard reached ASR 0.034 on
  Llama/AgentDojo with UA 0.000.
- **Static attack sets saturate quickly.** With the attacker pinned to
  AgentDojo's static suite, ASR fell from 0.404 to 0.045 within three
  rounds; with both sides evolving it fell from 0.294 to 0.032 over ten
  rounds. With only the attacker evolving against a frozen defender, ASR
  rose from 0.273 to 0.662. Training on static attacks instead of mined
  ones gave ASR 0.097 (versus 0.042).
- **Both reward terms matter**: dropping the safety term raised ASR to
  0.237; dropping the task-progress term cut UA to 0.492.
- **Adaptive attacks not seen in training**: ASR 0.081 on AutoDojo and
  0.124 on ASPI, versus 0.189 and 0.1745 for Meta-SecAlign.
- **Limitations stated by the authors**: only 7-8B models; no mechanistic
  account of latency; about 14 hours on 8 A100s per run. Judges are LLMs
  (Qwen3.5-9B, Qwen3.6-27B).

## Relevance to Praxis

- **Evidence for** `rules/agent-sandbox-safety.md` "Test with evolving
  adversaries, not static attack sets": a frozen defender facing an
  evolving attacker went from 0.273 to 0.662 ASR, and a defender trained
  against a static suite looked solved within three rounds.
- **Add attack latency to injection evaluations.** Report ASR by latency
  tier, not only overall; a defense that only catches immediate deviation
  will look strong on explicit benchmarks. See
  [`closed-loop-adaptive-red-teaming`](../skills/closed-loop-adaptive-red-teaming/SKILL.md).
- **Report utility under attack next to ASR**, per
  `rules/agent-sandbox-safety.md` "Measure each defense's benign cost on a
  matched benign arm, on the assembled stack": guardrails here reached low
  ASR by refusing whole tasks.
- A model-level defense is one layer. It does not replace deterministic
  tool authorization outside the model.

> Source: CoDeL: Co-Evolutionary Defense against Indirect Prompt Injection in LLM-based Agents (arXiv:2609.34463)
