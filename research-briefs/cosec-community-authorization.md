# CoSec: Authorization Across Agent Communities Is a System Property

> **Paper**: [CoSec: Benchmarking Agent Security in Communities](https://arxiv.org/abs/2609.34790)
> **Praxis source**: src:2609-34790v1
> **Status**: Research Brief. Executable benchmark.

## Why Not a Skill?

CoSec is an evaluation benchmark. What it gives builders is a failure
taxonomy for agents that serve several users and communities, plus
evidence that the choice of harness and prompt guardrails changes
outcomes. It proposes no defense procedure; the authors leave runtime
authorization defenses to future work.

## Core Concept

A persistent agent represents a user in several communities, for
example a health support group and a workplace. Information it learns
in one may sit in its history, memory or files, and must not reach a
requester in another. Boundaries also change: members leave, roles
change, communities merge or split. CoSec runs complete agent systems
(native memory, files, tools, sessions) through 208 scenarios:
Static112 with fixed communities, and Dyn96 after a boundary change.
Four stressors are applied: direct user injection, indirect injection,
memory poisoning and capability composition. Each flow is checked from
traces and artifacts against the authorization state in force, not
just against the final reply.

## Key Findings

Setting: 13 harness and model configurations. The harnesses are
OpenClaw, Hermes and Codex; backbones include Gemini 3.1 Pro, Gemini
3.5 Flash, GPT 5.6 Sol, DeepSeek 4.1 Flash, GLM 5.2, MiniMax M2.5 and
Qwen 3.8 Max. PVR is the privacy violation rate (lower is better) and
BCR the benign completion rate.

- **Utility is not safety**: 12 of 13 configurations exceed 85% BCR,
  while PVR ranges from 29.33% (OpenClaw, Gemini 3.1 Pro) to 96.15%
  (Hermes, DeepSeek 4.1 Flash). Codex with GPT 5.6 Sol has 41.35% PVR
  at 98.56% BCR.
- **The harness matters with the backbone fixed**: Gemini 3.5 Flash
  has 52.88% PVR on OpenClaw and 76.92% on Hermes. Across the five
  shared models, Hermes is 13.46 to 38.94 points higher. GPT 5.6 Sol
  has 55.29% on Hermes and 41.35% on Codex.
- **Static results do not predict dynamic ones**: four of six OpenClaw
  configurations have higher PVR after boundary changes, while five of
  six Hermes configurations have lower PVR.
- **Composition is the worst stressor**: capability composition, where
  plausible workflow steps combine into a forbidden flow, has the
  highest pooled PVR at 70.27%. Community merge is the hardest boundary
  event (72.12%) and member removal the easiest (47.12%).
- **Four failure modes after a boundary change** (795 classified
  failures):
  - workflow carryover, 29.9%: earlier memory, jobs or transactions
    continue under the old boundary;
  - excess permission, 25.5%: an expansion is treated as blanket
    access;
  - provenance confusion, 25.2%: restricted content is trusted because
    the source is familiar;
  - failed revocation, 19.4%.
- **A prompt guardrail helps unevenly**: the same first-turn guardrail
  cut PVR for DeepSeek 4.1 Flash on OpenClaw from 82.69% to 58.65%, but
  left it at 96.15% on Hermes. Traces show the guardrail can block a
  write to a shared file yet produce a refusal that repeats protected
  metadata, or wear off under repeated requests.
- **Verifier note**: deterministic trace checks alone had 100%
  precision but 33.3% recall on 192 human-audited trials. Adding an LLM
  judge to the execution evidence reached 96.9% accuracy.

**Limitations**: the scenarios are synthetic. The guardrail test
covers one backbone on two harnesses.

## Relevance to Praxis

- **Check authorization where information is written, shared or passed
  to a tool**, against the current community state, instead of relying
  on prompt reminders. This is consistent with "Enforce human approvals
  and safety gates in the runtime, NOT in prompt instructions"
  (rules/adk-workflow-architecture.md) and "Treat tool hiding,
  specialist prompts or roster delegation as access control"
  (rules/agent-sandbox-safety.md).
- **Boundary changes must revoke in-flight work.** Workflow carryover
  and failed revocation together make up about half of the dynamic
  failures. skills/auth-revocation-quiescence/SKILL.md covers fencing
  off effects of the old authority after a cut.
- **Test the whole harness.** Swapping the harness changed PVR by up to
  38.94 points on the same model, so re-run security evaluation for each
  harness, just as refusal is re-tested for each model.
- Companion evidence: research-briefs/agenttell-behavioural-side-channel.md.

> Source: CoSec: Benchmarking Agent Security in Communities (arXiv:2609.34790)
