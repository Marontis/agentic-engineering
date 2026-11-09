<!--
Licensed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
Attribution: Marontis / agentic-engineering (https://github.com/Marontis/agentic-engineering).
-->

# Deconfliction Report — 2026-11-09 (`cs.AI` High-Tier Wave 5)

## Scope

This audit covers the 13 high-tier (`score >= 8.0`) `cs.AI` papers ingested on `2026-11-09`, which produced:
- **4 new skills**:
  - [`intent-ltl-mcp-orchestration`](../skills/intent-ltl-mcp-orchestration/SKILL.md) (`arXiv:2611.09364`)
  - [`principal-context-permission-intersection`](../skills/principal-context-permission-intersection/SKILL.md) (`arXiv:2611.08768`)
  - [`feedback-poisoning-skill-promotion-guard`](../skills/feedback-poisoning-skill-promotion-guard/SKILL.md) (`arXiv:2611.09348`)
  - [`parallel-small-team-tts-scaling`](../skills/parallel-small-team-tts-scaling/SKILL.md) (`arXiv:2611.09798`)
- **9 new research briefs**:
  - [`attentionswitch-sparse-head-scaling-jailbreak-defense`](../research-briefs/attentionswitch-sparse-head-scaling-jailbreak-defense.md) (`arXiv:2611.08752`)
  - [`thought-injection-attacks-reasoning-agents`](../research-briefs/thought-injection-attacks-reasoning-agents.md) (`arXiv:2611.08811`)
  - [`debate-to-deceive-fact-checking-poisoning`](../research-briefs/debate-to-deceive-fact-checking-poisoning.md) (`arXiv:2611.08756`)
  - [`criteria-exposure-verifier-overfitting`](../research-briefs/criteria-exposure-verifier-overfitting.md) (`arXiv:2611.08318`)
  - [`flex-rsi-frontier-agent-benchmark`](../research-briefs/flex-rsi-frontier-agent-benchmark.md) (`arXiv:2611.08946`)
  - [`tooldex-ego-exo-physical-tool-use`](../research-briefs/tooldex-ego-exo-physical-tool-use.md) (`arXiv:2611.09036`)
  - [`logit-laundering-data-auditing-evasion`](../research-briefs/logit-laundering-data-auditing-evasion.md) (`arXiv:2611.09446`)
  - [`auteur-acoustic-plan-red-teaming`](../research-briefs/auteur-acoustic-plan-red-teaming.md) (`arXiv:2611.09351`)
  - [`guardrail-erosion-domain-finetuned-abstention`](../research-briefs/guardrail-erosion-domain-finetuned-abstention.md) (`arXiv:2611.08780`)
- **9 new rule entries** across [`agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md), [`adk-security-and-evaluation.md`](../rules/adk-security-and-evaluation.md), [`recursive-improvement.md`](../rules/recursive-improvement.md), [`multi-agent-coordination.md`](../rules/multi-agent-coordination.md), and [`agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md).

---

## Genuine Tensions Resolved (`Tension with`)

### 1. Bilevel Surrogate Rubric Synthesis vs. Benchmark Verifier Criteria Exposure (`recursive-improvement.md`)
- **Entry A**: `"DO: Use bilevel surrogate rubrics with rank-correlation calibration for prompt and skill evolution"` (`SkillLift`, `arXiv:2609.15396`)
- **Entry B**: `"DON'T: Expose benchmark verifier code or unstated rubric predicates to the skill-library learner"` (`Criteria Exposure`, `arXiv:2611.08318`)
- **Resolution**: Added reciprocal `Tension with` notes to both entries. `SkillLift` synthesizes dense surrogate rubrics from the task instruction and held-out outcome rank correlation (`Spearman >= 0.65`) to guide inner-loop search without revealing hidden benchmark grader predicates. By contrast, `arXiv:2611.08318` shows that exposing the actual benchmark verifier source code or unstated grading conventions directly to the skill-library learner inflates pass rates by up to +26 pp via verifier-specific gaming while degrading cross-benchmark skill transfer.

### 2. Parallel Small Flat Teams vs. Hierarchical/Bus Topologies (`multi-agent-coordination.md`)
- **Entry A**: `"DO: Scale test-time compute on verifiable long-horizon tasks via parallel small flat teams rather than solo Best-of-N, one giant team, or manager orchestration"` (`arXiv:2611.09798`)
- **Entries B & C**: `"DON'T: Default to a fixed multi-agent topology"` (`arXiv:2608.28895`) and `"DO: Structure inter-agent communication around typed intents and bus substrates"` (`BusMA`, `arXiv:2609.08300`)
- **Resolution**: Linked `"Scale test-time compute on verifiable long-horizon tasks via parallel small flat teams..."` via `Tension with` to both entries. Manager hierarchies (`ORCH`) and Chair-arbitrated message buses (`BusMA`) coordinate interdependent role workflows when no per-attempt exact verifier is available; when an exact per-attempt oracle exists (unit tests, formal proof checkers, puzzle verifiers), $K$ independent small flat peer teams ($M=10$) sharing only asynchronous verified discoveries via `Broadcast` / `Direct Message` dominate both solo `Best-of-N` and manager-orchestrated hierarchies.

---

## Non-Contradictory Overlap Pairs Reviewed (`scripts/kb_lint_reviewed.txt`)

Eight lexical overlap pairs flagged by `kb_lint.py --base origin/master` were audited and verified to address orthogonal failure modes:

| File | Rule A | Rule B | Disposition |
|:-----|:-------|:-------|:------------|
| `adk-security-and-evaluation.md` | `DO: Enforce deterministic pre-retrieval query sanitization and post-retrieval provenance tagging in Agentic RAG pipelines` | `DON'T: Trust reasoning-trace delimiters (<think>...</think>) in untrusted tool or retrieval outputs` | Complementary: RAG query/chunk provenance vs. stripping spoofed `<think>` reasoning-trace delimiters before reasoning-model ingestion (`arXiv:2611.08811`). |
| `adk-security-and-evaluation.md` | `DO: Enforce multi-layered defense-in-depth combining deterministic Model Armor and SDP interceptors with semantic guardrails` | `DON'T: Trust reasoning-trace delimiters (<think>...</think>) in untrusted tool or retrieval outputs` | Complementary: general Model Armor + SDP defense-in-depth vs. specific defense against thought-injection tag spoofing (`arXiv:2611.08811`). |
| `adk-security-and-evaluation.md` | `DO: Enforce multi-layered defense-in-depth combining deterministic Model Armor and SDP interceptors with semantic guardrails` | `DON'T: Rely on single-source retrieval relevance or multi-agent consensus over unverified web snippets for fact-checking` | Complementary: input/output interceptor pipeline vs. multi-agent adversarial evidence-crafting (`D2D`) resistance in fact-checking (`arXiv:2611.08756`). |
| `agent-sandbox-safety.md` | `DON'T: Grant MCP servers ambient host privileges or trust static signatures without germline execution isolation` | `DO: Gate dynamic MCP tool orchestration with a two-level neuro-symbolic intent and LTL runtime verifier` | Complementary: host-level germline container isolation for MCP server binaries (`arXiv:2611.06585`) vs. two-level semantic intent + LTL trajectory safety verification over MCP tool sequences (`arXiv:2611.09364`). |
| `agent-sandbox-safety.md` | `DON'T: Evaluate multi-agent tool authorization using only the immediate caller's identity or a static security label` | `DO: Enforce monotonic permission intersection across full multi-agent principal contexts and evaluate policies over the joint system call graph` | Complementary: both enforce Conflux (`arXiv:2611.08768`) — the `DON'T` forbids immediate-caller-only evaluation and the `DO` specifies monotonic permission intersection (`P_eff(C)`) and joint system-graph Datalog evaluation. |
| `recursive-improvement.md` | `DO: Pass every self-modification through one acceptance gate` | `DON'T: Promote text-space skill updates using task-outcome feedback alone without trajectory-contextualized safety auditing` | Complementary: single acceptance gate architecture vs. trajectory-contextualized safety auditing inside that gate to block SkillOpt feedback backdoors (`arXiv:2611.09348`). |
| `recursive-improvement.md` | `DO: Gate self-evolving agent modifications with an explicit complexity penalty and dual safety/utility ratchet` | `DON'T: Promote text-space skill updates using task-outcome feedback alone without trajectory-contextualized safety auditing` | Complementary: complexity-penalized harness ratchet (`RRSI`) vs. trajectory-contextualized inspection of natural-language evaluator feedback before skill promotion (`arXiv:2611.09348`). |
| `recursive-improvement.md` | `DO: Filter skill updates through execution-grounded failure attribution` | `DON'T: Expose benchmark verifier code or unstated rubric predicates to the skill-library learner` | Complementary: attributing skill failures to execution steps (`SkillAA`) vs. hiding benchmark grader code from the skill proposer to prevent verifier overfitting (`arXiv:2611.08318`). |
