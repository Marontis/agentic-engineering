# Knowledge-Base Deconfliction Report — 2026-11-03 Batch

## 1. Scope of Ingestion & Audit

- **Batch**: 2026-11-03 arXiv `cs.AI` announcements (`arXiv:2610.37700` through `arXiv:2611.03555`).
- **Selection**: Out of `1,786` announced entries (`265` `NEW` candidates in `output/candidates.json`, `47` with `total_score >= 10.0`), `4` off-topic domain papers were excluded (`2506.20651` federated learning gradient leakage, `2610.39848` LiDAR 3D perception, `2611.02286` AEC/BIM construction workflows, and `2611.01600` robotic 3D point-cloud occlusion), yielding **43 on-topic LLM/agent papers** ingested into the Praxis graph (`1,332` documents, `13,714` chunks embedded, `praxis doctor --require-index` $\to$ `status: ok`).
- **Artifacts Created (`43` total)**:
  - **7 New Skills (`output/skills/`)**:
    1. [`composite-skill-vulnerability-scanner`](skills/composite-skill-vulnerability-scanner/SKILL.md) (`arXiv:2610.37901`)
    2. [`audited-guardrail-tool-evolution`](skills/audited-guardrail-tool-evolution/SKILL.md) (`arXiv:2611.02516`)
    3. [`proof-carrying-agent-messages`](skills/proof-carrying-agent-messages/SKILL.md) (`arXiv:2610.39109`)
    4. [`history-guided-trajectory-collection`](skills/history-guided-trajectory-collection/SKILL.md) (`arXiv:2611.02074`)
    5. [`agent-data-mutual-evolution`](skills/agent-data-mutual-evolution/SKILL.md) (`arXiv:2610.41479`)
    6. [`cross-interface-route-bound-authorization`](skills/cross-interface-route-bound-authorization/SKILL.md) (`arXiv:2610.41397`)
    7. [`task-graph-contextual-integrity-gating`](skills/task-graph-contextual-integrity-gating/SKILL.md) (`arXiv:2610.39532`)
  - **36 New Research Briefs (`output/research-briefs/`)**:
    - Offensive/red-teaming papers (`2610.38091`, `2610.41272`, `2610.38895`, `2610.37738`, `2610.38833`) were triaged strictly into **defensive-only** research briefs and defensive evaluation/sandbox rules.
- **Rules Updated (`5` files)**:
  - [`rules/agent-evaluation-quality.md`](rules/agent-evaluation-quality.md): Extended 2 rules (`DON'T: Report red-team failure rates scored by a single judge model`; `DO: Decompose evaluations into atomic checklist items`) and added 3 new rules (`DO: Certify benchmark tasks with reference-pass and empty-fail preflights, lock the verifier's evidence view, and fingerprint baseline bytes before reusing grading sandboxes`; `DO: Benchmark reward-hacking, manipulation, and backdoor monitors against gap-matched honest failures and counterfactual control pairs`; `DON'T: Interpret low Attack Success Rate in low-resource languages as safety alignment without measuring Comprehension Rate`).
  - [`rules/multi-agent-coordination.md`](rules/multi-agent-coordination.md): Extended 2 rules (`DON'T: Default to a fixed multi-agent topology`; `DO: Mitigate multi-agent collusion and cover-up deception via weak-to-strong on-policy distillation rather than ethical prompts alone`) and added 3 new rules (`DO: Attach Merkle-proven log receipts and three-valued claim checkers to inter-agent handoff messages before trusting claimed side effects`; `DO: Enforce single-owner file region assignment or sequential handoffs before multi-agent codebase edits, and hide raw peer git history`; `DON'T: Rely on multi-agent consensus, demographic masking, or per-agent self-debiasing to eliminate demographic triage disparities`).
  - [`rules/skill-system-design.md`](rules/skill-system-design.md): Extended 1 rule (`DON'T: Use a pre-execution skill scanner as the sole admission gate for third-party skills`) and added 1 new rule (`DO: Extract skills as explicit text from paired trajectories before distilling them into role-conditioned latent representations`).
  - [`rules/recursive-improvement.md`](rules/recursive-improvement.md): Extended 1 rule (`DO: Evaluate evolved instructions against immutable, held-out negative security testbeds`) and added 1 new rule (`DO: Keep prior-attempt history in the trajectory collector and retain explicit multi-field plans in SFT targets when curating post-training trajectories`). The protected acceptance-gate rule (`DO: Pass every self-modification through one acceptance gate`) was left untouched.
  - [`rules/agent-sandbox-safety.md`](rules/agent-sandbox-safety.md): Extended 5 rules (`DO: Measure each defense's benign cost on a matched benign arm, on the assembled stack`; `DO: Restore earlier-turn safety constraints and enforce them at a deterministic action boundary`; `DO: Pin MCP tool descriptors and isolate offensive execution boundaries`; `DON'T: Rely on prompt-level privacy instructions to keep carried information inside its boundary`; `DO: Isolate human-in-the-loop approval gates onto an out-of-band, hardware-attested trusted device with a trusted display`) and added 3 new rules (`DO: Normalize multi-surface computer-use actions into interface-erased canonical effects and fence route-bound prepare tickets on interface switches`; `DON'T: Rely on delimiter escaping, assistant prefill continuation, or single-point adversarial signatures to defend against role spoofing, prefill, or suffix attacks`; `DO: Combine deterministic SAST with unrestricted AI security agents rather than substituting one for the other or pre-filtering vulnerability classes in the harness`).

---

## 2. Deconfliction Resolutions

Running `python scripts/kb_lint.py --base origin/master` surfaced 8 candidate opposite-polarity heading pairs. Each pair was audited against the underlying paper evidence:

### 2.1 Genuine Scope Boundaries (Resolved via Reciprocal `Tension with` / `See also` Notes)

1. **Multi-Agent Consensus Calibration (`R²-MAD` / `CollabFlow`) vs. Clinical Disparity Laundering (`arXiv:2610.38215`)**:
   - *Entries*: `DO: Dynamically calibrate consensus entropy and weight peer influence by evidence grounding in multi-agent debate` ([`rules/recursive-improvement.md`](rules/recursive-improvement.md)) vs. `DON'T: Rely on multi-agent consensus, demographic masking, or per-agent self-debiasing to eliminate demographic triage disparities` ([`rules/multi-agent-coordination.md`](rules/multi-agent-coordination.md)).
   - *Resolution*: Added reciprocal `Tension with` blocks to both rules. Evidence-weighted debate calibration corrects factual and reasoning errors on QA, math, and code tasks (`arXiv:2609.03619`, `arXiv:2609.38662`), whereas in demographic-sensitive clinical triage (`arXiv:2610.38215`), multi-agent specialist consensus amplifies Black-vs-White pain/ICU triage disparities by +75% (`8.4 pp` $\to$ `14.7 pp`) while stripping explicit demographic terms from 96.2% of rationales. Even when debate weights peer influence by evidence, high-stakes allocation pipelines must run counterfactual demographic swap audits at the terminal decision boundary.

2. **Proof-Carrying Message Receipts (`PCM`, `arXiv:2610.39109`) vs. Debate Consensus Authorization (`MADBench`, `arXiv:2609.39146`)**:
   - *Entries*: `DO: Attach Merkle-proven log receipts and three-valued claim checkers to inter-agent handoff messages before trusting claimed side effects` vs. `DON'T: Treat debate consensus as authorization for tool side effects` (both in [`rules/multi-agent-coordination.md`](rules/multi-agent-coordination.md)).
   - *Resolution*: Added reciprocal `Tension with` notes clarifying the temporal and functional boundary: `PCM` Merkle receipts verify *post-execution evidentiary provenance* (that a sender's claimed past tool execution genuinely occurred in the append-only runtime log), whereas `MADBench` governs *pre-execution policy authorization* (multi-agent agreement or verified peer receipts never authorize a downstream agent to execute a new privileged side effect without checking the external authorization policy).

3. **Hiding Peer Git History in Parallel Coding (`ParallACT`, `arXiv:2611.00314`) vs. Restricting Peer-Verifier Interaction History (`arXiv:2609.24967`)**:
   - *Entries*: `DO: Enforce single-owner file region assignment or sequential handoffs before multi-agent codebase edits, and hide raw peer git history` ([`rules/multi-agent-coordination.md`](rules/multi-agent-coordination.md)) vs. `DON'T: Expose full interaction history to peer-verifying agents` ([`rules/recursive-improvement.md`](rules/recursive-improvement.md)).
   - *Resolution*: Reinforcing guidance (one phrased as `DO ... hide`, the other as `DON'T: Expose`). Added a `See also` cross-reference linking the two entries and logged the reinforcing pair in `scripts/kb_lint_reviewed.txt`.

### 2.2 Lexical Stem Collisions Across Unrelated Domains (Logged in `scripts/kb_lint_reviewed.txt`)

- `Benchmark reward-hacking, manipulation, and backdoor monitors against gap-matched honest failures` (`agent-evaluation-quality.md`) vs. `Deploy the chain-of-thought monitor you optimized the policy against` (`agent-sandbox-safety.md`) — shared stems `against, monitor`; orthogonal (calibrating evaluator FPR on honest-failure controls vs. avoiding RL optimization directly against a deployed CoT monitor).
- `Benchmark reward-hacking, manipulation, and backdoor monitors against gap-matched honest failures` (`agent-evaluation-quality.md`) vs. `Allow self-modifying agents to optimize prompts or scaffolding solely against performance benchmarks` (`recursive-improvement.md`) — shared stems `against, benchmark`; unrelated (evaluator control pairs vs. poisoned task benchmarks in self-modifying agents).
- `Interpret low Attack Success Rate in low-resource languages as safety alignment without measuring Comprehension Rate` (`agent-evaluation-quality.md`) vs. `Measure open privilege alongside attack success and utility` (`agent-sandbox-safety.md`) — shared stems `attack, succes`; unrelated (multilingual jailbreak comprehension vs. tool-call open privilege).
- `Interpret low Attack Success Rate in low-resource languages as safety alignment without measuring Comprehension Rate` (`agent-evaluation-quality.md`) vs. `In low-resource settings, reflect only on steps AFTER the first error` (`recursive-improvement.md`) — shared stems `low, resource`; polysemy ("low-resource African languages" vs. "low compute/token budget").
- `Enforce single-owner file region assignment or sequential handoffs before multi-agent codebase edits` (`multi-agent-coordination.md`) vs. `Expose running selection tallies or popularity-sorted orderings to sequential agents` (`multi-agent-coordination.md`) — shared stems `multi, sequential`; unrelated (sequential codebase handoffs vs. Polya-urn popularity herding in sequential social choice).

---

## 3. Verification Summary

- `python scripts/kb_lint.py --base origin/master` $\to$ **`0 error(s)`**, `0` unresolved conflict warnings, and `4` verified `copied-stat` coincidences where exact paper figures (`MemHarmBench`, `CuriousTogether`, `EB-MAS`, `Safin-1.5`) share common percentages (`1.00%`, `6.50%`, `14.00%`, `27.16%`, `40.00%`, `71.43%`, `75.36%`, `81.82%`, `87.50%`) with earlier briefs.
