# Backdoored Retriever Checkpoints in Agentic Search: Defensive Lessons

> **Source**: Xu, Hua & Xiao, "Backdoor in the Loop: Compromising Agentic
> Search via Malicious Retrievers", [arXiv:2609.37468](https://arxiv.org/abs/2609.37468), Sep 2026
> **Status**: Research Brief, defensive lessons only. This is an attack
> paper; the brief omits how the backdoors are trained, triggered or
> concealed (see the repo's `AGENTS.md`).

## Why Not a Skill?

The paper's contribution is an attack and an evaluation of existing
defenses against it. The defensive side is a set of findings (what fails
and why), not a procedure the authors validated.

## Core Concept

In agentic search the retriever is a component the agent calls many times
per question, and teams often download retriever checkpoints from public
model hubs. The threat model here is narrow and realistic: the attacker
controls only the retriever checkpoint. The corpus, the agent model and
the inference pipeline are the victim's own and unchanged. A backdoored
retriever behaves normally on ordinary queries and misbehaves only when a
trigger appears, including triggers that occur naturally in legitimate
questions.

## Key Findings

Setting: HotpotQA and TriviaQA (1,000 test questions each), E5 and
Contriever-MSMARCO retrievers, Qwen2.5-7B-Instruct as the search agent,
Wikipedia (wiki18) corpus.

- **Clean behavior hides the backdoor.** Clean-input F1 moved by at most
  1.92 points either way, while triggered queries lost 18.8-30.9 F1
  points (evidence suppression). Naturally occurring triggers in
  legitimate questions caused 13.9-34.7 points of F1 loss.
- **Targeted promotion is near-total.** An attacker-chosen document was
  retrieved for 99.8-100% of evaluated questions in every round and ranked
  first in over 99.7% of rounds; answer F1 fell 22.5-30.1 points.
- **The agent loop turns retrieval into a cost attack.** A round-control
  backdoor raised mean search length by 78-88%, final context tokens by
  81-87% and completion latency by 80-126%, with F1 down 24-29 points,
  while clean-input behavior changed little. Per-query snapshots miss
  this; only trajectory length and cost show it.
- **Post-hoc purification did not remove it.** After clean fine-tuning
  for 5-30 epochs, the clean-versus-trigger F1 gap stayed at 28.64-30.05
  points (HotpotQA) and 23.12-24.10 (TriviaQA). Magnitude pruning plus
  fine-tuning left comparable gaps; an adapted BPO defense did not
  preserve clean utility.
- **Detectors can be blinded.** Seven detectors were evaluated (activation
  clustering, spectral signatures, Neural Cleanse, PICCOLO, a black-box
  top-k instability test, RAP, STRIP). After the authors' concealment
  step, detector separation on held-out MuSiQue fell sharply (e.g.
  spectral signatures 46.53 to 29.26, top-k instability 44.63 to 14.66)
  while the malicious retrieval persisted. The authors warn that weak
  purification can itself serve as concealment.
- **Limitations stated by the authors**: one agent model and two
  retrievers; the BPO adaptation comes from image tasks; detection
  evaluation on naturally triggered queries rests on 8-30 positives per
  1,000-question set.

## Defensive Takeaways

- **Treat retriever and embedding checkpoints as supply-chain code.**
  Pin them by hash, prefer first-party or reproducibly trained weights,
  and record provenance as you would for a skill or tool
  (rules/skill-system-design.md, "Validate skill provenance before adding
  to library").
- **Do not accept "we fine-tuned it on clean data" as remediation.** The
  measured gap survived 30 epochs of clean fine-tuning.
- **Monitor trajectories, not single retrievals.** The authors' main
  recommendation: judge retrieval trustworthiness by the trajectories and
  costs the system actually produces. Alert on per-query search rounds,
  context tokens and latency against a baseline, and on one document
  appearing across unrelated queries. Hard caps on search rounds bound
  the cost attack.
- **Check detection and removal together.** A detector that passes after
  a purification step is not evidence the backdoor is gone.
- **Retrieved content stays untrusted.** A promoted document is just
  another injection vector; see `rules/agent-sandbox-safety.md`
  "Sanitize all tool outputs before injecting into agent context" and
  [`rag-evidence-triage`](../skills/rag-evidence-triage/SKILL.md).

## Relevance to Praxis

- Extends supply-chain concern from skills and MCP tools to the retrieval
  model itself, a component most RAG checklists treat as trusted.
- Supports existing guidance on trajectory-level monitoring; introduces
  no rule that conflicts with current entries.

> Source: Backdoor in the Loop: Compromising Agentic Search via Malicious Retrievers (arXiv:2609.37468)
