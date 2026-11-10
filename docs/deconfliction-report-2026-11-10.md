<!--
Licensed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
Attribution: Marontis / agentic-engineering (https://github.com/Marontis/agentic-engineering).
-->

# Deconfliction Report — 2026-11-10 (Agentic High-Tier Wave 6)

## Scope

This audit covers the 25 strictly agentic high-tier (`score >= 8.0`) papers ingested on `2026-11-10` across `cs.AI`, `cs.CR`, and `cs.SE`, which produced:
- **8 new skills**:
  - [`counterfactual-privilege-role-induction`](../skills/counterfactual-privilege-role-induction/SKILL.md) (`arXiv:2611.11539` — `PRISM`)
  - [`fact-grounded-access-control-proxy`](../skills/fact-grounded-access-control-proxy/SKILL.md) (`arXiv:2611.10157` — `BACGuard`)
  - [`hybrid-sandbox-skill-intent-audit`](../skills/hybrid-sandbox-skill-intent-audit/SKILL.md) (`arXiv:2611.10830` — *The Devil Wears Markdown*)
  - [`owner-authority-ipi-eval-construction`](../skills/owner-authority-ipi-eval-construction/SKILL.md) (`arXiv:2611.10026` — `MetaPI`)
  - [`state-anchored-trajectory-auditing`](../skills/state-anchored-trajectory-auditing/SKILL.md) (`arXiv:2611.11266` — `ErosionBench` / `Meta-Auditor`)
  - [`online-fer-statistical-acceptance`](../skills/online-fer-statistical-acceptance/SKILL.md) (`arXiv:2611.10787` — `TRUST`)
  - [`scoped-multi-agent-harness-composition`](../skills/scoped-multi-agent-harness-composition/SKILL.md) (`arXiv:2611.12552` — `SciMARS`)
  - [`bidirectional-traceability-debate`](../skills/bidirectional-traceability-debate/SKILL.md) (`arXiv:2611.09162` — *Rethinking Requirement-to-Code Traceability*)
- **17 new research briefs**:
  - [`tracing-mcp-security-vulnerabilities-dataset`](../research-briefs/tracing-mcp-security-vulnerabilities-dataset.md) (`arXiv:2611.11104`)
  - [`shadowbench-mcp-routing-shadow-invocations`](../research-briefs/shadowbench-mcp-routing-shadow-invocations.md) (`arXiv:2611.11720`)
  - [`untrusted-model-deterministic-policy-taint-hitl`](../research-briefs/untrusted-model-deterministic-policy-taint-hitl.md) (`arXiv:2611.11571`)
  - [`badevolve-task-poisoning-defensive-lessons`](../research-briefs/badevolve-task-poisoning-defensive-lessons.md) (`arXiv:2611.10542`)
  - [`adaptive-prompt-injection-swarms-defensive-lessons`](../research-briefs/adaptive-prompt-injection-swarms-defensive-lessons.md) (`arXiv:2611.11861`)
  - [`agents-of-chaos-agentic-attacks-sok`](../research-briefs/agents-of-chaos-agentic-attacks-sok.md) (`arXiv:2611.10843`)
  - [`collusion-probe-evaluation-pitfalls`](../research-briefs/collusion-probe-evaluation-pitfalls.md) (`arXiv:2611.10620`)
  - [`webtrap-farm-web-agent-harness-security`](../research-briefs/webtrap-farm-web-agent-harness-security.md) (`arXiv:2611.11971`)
  - [`benign-trained-probes-adversarial-tool-errors`](../research-briefs/benign-trained-probes-adversarial-tool-errors.md) (`arXiv:2611.11172`)
  - [`snaprag-rag-extraction-defensive-lessons`](../research-briefs/snaprag-rag-extraction-defensive-lessons.md) (`arXiv:2611.12241`)
  - [`infrarsi-training-infrastructure-rsi`](../research-briefs/infrarsi-training-infrastructure-rsi.md) (`arXiv:2611.11558`)
  - [`is-recursive-self-improvement-safe`](../research-briefs/is-recursive-self-improvement-safe.md) (`arXiv:2611.10261`)
  - [`reins-real-time-trajectory-planning-harness`](../research-briefs/reins-real-time-trajectory-planning-harness.md) (`arXiv:2611.10748`)
  - [`coding-agent-vulnerability-propagation`](../research-briefs/coding-agent-vulnerability-propagation.md) (`arXiv:2611.11455`)
  - [`appworld-replay-fidelity-hidden-state-oracles`](../research-briefs/appworld-replay-fidelity-hidden-state-oracles.md) (`arXiv:2611.11216`)
  - [`legion-sparse-signal-adversarial-noise-investigation`](../research-briefs/legion-sparse-signal-adversarial-noise-investigation.md) (`arXiv:2611.11896`)
  - [`cyberbingym-binary-patch-exposure-defensive-lessons`](../research-briefs/cyberbingym-binary-patch-exposure-defensive-lessons.md) (`arXiv:2611.10723`)
- **23 new rule entries and 3 evidence extensions** across [`agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md), [`skill-system-design.md`](../rules/skill-system-design.md), [`recursive-improvement.md`](../rules/recursive-improvement.md), [`multi-agent-coordination.md`](../rules/multi-agent-coordination.md), and [`agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md), plus targeted updates to [`nextjs-public-agent-app.spec.md`](../specs/nextjs-public-agent-app.spec.md) and [`self-improving-agent.spec.md`](../specs/self-improving-agent.spec.md).

---

## Genuine Tensions Resolved (`Tension with`)

### 1. Search-Time Online FER Control (`TRUST`) vs. Full-Set Decision-Only FWER Control (`Reuse`) (`recursive-improvement.md`)
- **Entry A**: `"DO: Bound online False Evolution Proportion via overlap-adjusted betting e-values during subsampled benchmark search"` (`TRUST`, `arXiv:2611.10787`)
- **Entry B**: `"DO: Return only accept/reject decisions to the proposer when the acceptance set is reused across rounds"` (`Reuse`, `arXiv:2609.33180`)
- **Resolution**: Added reciprocal `Tension with` notes to both entries. Multi-round FWER gates (`SGM-B`, `SGM-H`) freeze progress (`0` and `3` accepted updates across 6 settings) during 30-round harness search over subsampled validation pools ($n \le N$). `TRUST` governs *search-time* incumbent updates where proposers read closed diagnostics by controlling the False Evolution Rate ($\operatorname{FER}_\varepsilon(T) \le q$) via explicit sample-overlap boundary shifts ($u_{t,i}^{(\beta)} = p_\varepsilon + \zeta_{t,i}\beta$), whereas `Reuse` and `"DO: Pass every self-modification through one acceptance gate"` govern the *held-out acceptance set* whose scores never reach the proposer.

### 2. Hybrid Sandbox Dry-Run Skill Auditing vs. Pre-Execution Skill Scanners as Sole Gates (`skill-system-design.md`)
- **Entry A**: `"DO: Pair static skill checks with safety-constrained sandbox dry-runs and provenance-weighted evidence rather than alert-count thresholds"` (`arXiv:2611.10830`)
- **Entry B**: `"DON'T: Use a pre-execution skill scanner as the sole admission gate for third-party skills"` (`arXiv:2609.32400`, `arXiv:2609.39607`, `arXiv:2610.37901`, `arXiv:2611.05088`)
- **Resolution**: Added reciprocal `Tension with` notes. Provenance-weighted safety-constrained sandbox dry-runs solve the alert-count inversion of static/LLM pre-execution scanners (`FPR 0.67 -> 0.08`, `F1 = 0.89`), while `12/80` (`15%`) malicious skills still evade dry-runs (`Recall = 0.85`), confirming that provenance attestation, rate-limited resubmissions, and runtime sandboxing remain mandatory.

### 3. Benign-Trained & Prompt-Confounded Hidden-State Probes vs. Supervised Exposure-Contrast Probes (`agent-sandbox-safety.md`, `agent-evaluation-quality.md`, `skill-system-design.md`)
- **Entries A & B**: `"DON'T: Assume clean-fitted hidden-state probes outrank token-entropy uncertainty on system-override hijackings"` (`arXiv:2611.11172`) and `"DON'T: Score collusion probes post-vote or omit decliner and instruction-stripping ablations"` (`arXiv:2611.10620`)
- **Entries C, D & E**: `"DO: Distinguish insufficient from conflicting evidence — they need different responses"` (`arXiv:2608.27661`), `"DON'T: Use a pre-execution skill scanner as the sole admission gate for third-party skills"` (`LatentTriad`, `arXiv:2611.05088`), and `"DON'T: Rely on delimiter escaping, assistant prefill continuation, or single-point adversarial signatures..."` (`arXiv:2610.40396`)
- **Resolution**: Linked via `Tension with` across all three files. Intermediate-layer linear probes work when trained *supervisedly* on the target exposure contrast present in context (`99.6%` macro-AUC in `LatentTriad`, `0.974` AUROC on role spoofing) and calibrated against hard negatives, whereas unsupervised benign-trained pre-action tool-error probes collapse to `0.431` AUROC under `system-override` at 14B scale (trailed by zero-training output token entropy at `0.758` AUROC), and prompt-trained collusion probes drop from `1.00` to `0.61` AUROC when secret briefs are stripped from context.

### 4. Symmetric `Trace`/`Non-Trace` Swap Debate Over Full-Repo Context vs. Shared-Prompt Debate Collapse & Context Partitioning (`multi-agent-coordination.md`)
- **Entry A**: `"DO: Route requirement-to-code traceability by evidence locality and use symmetric Trace/Non-Trace swap debate instead of lexical retrieval or one-way critics"` (`arXiv:2611.09162`)
- **Entries B & C**: `"DON'T: Assume multi-agent debate eliminates shared misconceptions"` (`arXiv:2610.35930`) and `"DON'T: Share full context across all agents by default"` (`arXiv:2609.03920`)
- **Resolution**: Documented `Tension with` scope boundary. Homogeneous peer debate on shared-prompt QA collapses to $n_{\text{eff}} \approx 1.02\text{--}1.07$, whereas opposing inclusion/exclusion mandates paired with cross-partition set swapping (`Trace Debater` inspecting `non_trace_files`, `Non-Trace Debater` inspecting `trace_files`) over non-private full-repository source achieve peak $F_2$ (`50.8%` / `49.5%`) and cut human validation volume by `30%–50%` without one-way critic recall loss (`-14.4 pp`).

### 5. Root User Goal Pinning in Multi-Role Web Agents vs. Scoped Sub-Agent Context (`agent-sandbox-safety.md`, `multi-agent-coordination.md`)
- **Entry A**: `"DO: Anchor downstream web-agent navigators to the original user goal and pair security metrics with usability calibration"` (`WebTrap Farm`, `arXiv:2611.11971`)
- **Entry B**: `"DON'T: Share full context across all agents by default"` (`multi-agent-coordination.md`)
- **Resolution**: Documented `Tension with` exception: peer observation transcripts remain scoped across sub-agents, *except* the authenticated root user goal must be pinned immutably into downstream browser navigators (`19.35% -> 43.59%` Stage III `Conditional_DSR`, `+24.24 pp`) to prevent cross-role trust laundering of webpage injections.

### 6. Hiding Raw Defender `CoT` from External Callers vs. Internal `<think>` Trace Inspection (`agent-evaluation-quality.md`, `adk-security-and-evaluation.md`)
- **Entry A**: `"DO: Benchmark instruction-hierarchy adherence with benign orthogonal tool targets, and hide defender CoT from untrusted callers"` (`arXiv:2611.11861`)
- **Entry B**: `"DON'T: Rely on thinking-tag stripping or final-answer-only inspection to defend LRMs from CoT thought-injection"` (`arXiv:2611.08811`)
- **Resolution**: Linked via `Tension with` across trust boundaries: internal host DLP monitors must inspect raw `<think>` blocks inside the trusted boundary (`20.8%` think-only leaks), while external/untrusted callers must never receive raw defender `CoT` (`-8` to `-12 pp` `ARR@150` resistance drop).

### 7. Topical Guardrails (`Model Armor`, `Llama Guard 3`) vs. Verbatim RAG Corpus Extraction (`agent-sandbox-safety.md`, `adk-security-and-evaluation.md`)
- **Entry A**: `"DON'T: Rely on topical content-moderation classifiers to stop verbatim RAG corpus extraction"` (`SNAPRAG`, `arXiv:2611.12241`)
- **Entry B**: `"DO: Filter prompt injections and jailbreaks at the interceptor layer using Model Armor"` (`adk-security-and-evaluation.md`)
- **Resolution**: Linked via `Tension with`: interceptor-layer harm/jailbreak classifiers catch topical harm (`S1–S14`), but topically benign proprietary RAG passages still leak (`50.7%–96.3%` KB extracted behind input+output `Llama Guard 3 8B`) unless paired with deterministic output-to-chunk verbatim overlap caps (`<= 1.0%` ER under synthesis) and per-principal chunk-coverage budgets.

---

## Non-Contradictory Overlap Pairs Reviewed (`scripts/kb_lint_reviewed.txt`)

Twelve opposite-polarity lexical stem-overlap pairs flagged by `kb_lint.py --base origin/master` were audited in full and recorded in [`kb_lint_reviewed.txt`](../scripts/kb_lint_reviewed.txt):

| Rule A | Rule B | Disposition |
|:-------|:-------|:------------|
| `DO: Benchmark instruction-hierarchy adherence with benign orthogonal tool targets...` | `DON'T: Rely on instruction-stripping sanitizers or tool-name allowlists...` | Complementary: intrinsic model-level instruction-hierarchy benchmarking vs. runtime field-level source-authority bindings against task-tampering IPI (`arXiv:2611.07640`). |
| `DO: Enforce owner-authority boundaries, action-deflection cases, and reach-adjusted Effective ASR...` | `DON'T: Treat compact prompt-injection classifiers as intent detectors, or expose their scores` | Reinforcing: `MetaPI` (`arXiv:2611.10026`) demonstrates compact PI classifiers fail on dynamic `action-deflection` arguments, reinforcing structural controls behind classifiers. |
| `DO: Declare mandatory safety-tool chains in MCP routing policies...` | `DON'T: Trust MCP tool metadata without trace-aware vetting` | Complementary: pre-execution mandatory safety-tool chain routing (`arXiv:2611.11720`) vs. registration-time MCP server metadata vetting (`arXiv:2609.26761`, `arXiv:2610.36108`). |
| `DO: Declare mandatory safety-tool chains in MCP routing policies...` | `DON'T: Provide ground-truth answers to chain-of-thought oversight monitors` | Homonym (`safety-tool chains` vs. `chain-of-thought`) & unrelated scope. |
| `DO: Declare mandatory safety-tool chains in MCP routing policies...` | `DON'T: Deploy the chain-of-thought monitor you optimized the policy against...` | Homonym (`safety-tool chains` vs. `chain-of-thought`) & unrelated scope. |
| `DO: Declare mandatory safety-tool chains in MCP routing policies...` | `DON'T: Use a pre-execution skill scanner as the sole admission gate...` | Unrelated scope: deterministic pre-execution MCP safety-tool chain enforcement vs. third-party `SKILL.md` pre-admission scanning. |
| `DO: Induce least-privilege agent tool roles via sandbox counterfactual interventions...` | `DON'T: Put steps the calling agent can't execute in tool error text` | Unrelated scope: pre-session counterfactual `do(m)` role induction (`PRISM`) vs. actionable MCP server error-message formatting (`arXiv:2609.35381`). |
| `DO: Place taint-triggered human approval behind canonicalized capability monitors...` | `DON'T: Evaluate a remediated oversight monitor only on the misbehavior family...` | Unrelated scope: provenance-taint HITL escalation behind capability reference monitors (`arXiv:2611.11571`) vs. evaluating remediated collusive oversight monitors on held-out misbehaviors (`arXiv:2610.30582`). |
| `DO: Enforce external access control via read-only database-join fact reconstruction...` | `DON'T: Treat tool hiding, specialist prompts or roster delegation as access control` | Reinforcing: both enforce deterministic server/proxy access control (`BACGuard` read-only FK ownership joins, `arXiv:2611.10157`; server-side `call_tool` checks, `arXiv:2609.22573`). |
| `DO: Pair preventive and detective agent guardrails with post-compromise containment...` | `DON'T: Trust checkpoint state without integrity verification` | Reinforcing: transactional state rollback (`arXiv:2611.10843`) requires cryptographic checkpoint integrity verification before resume (`arXiv:2608.29381`). |
| `DO: Pair preventive and detective agent guardrails with post-compromise containment...` | `DON'T: Treat HTTP 200 / success tool return codes as workflow success...` | Reinforcing: post-compromise state rollback and empirical safeguard coverage verification complement post-call observable state verification (`arXiv:2609.15397`). |
| `DO: Pair static skill checks with safety-constrained sandbox dry-runs...` | `DON'T: Feed unverified single-sided evidence passages into fact-checking judges...` | Reinforcing across domains: source-to-trace provenance weighting in skill dry-runs (`arXiv:2611.10830`) and provenance/rebuttal checks in RAG fact-checking (`arXiv:2611.08756`). |

---

## Verified `copied-stat` Coincidences (Figures Preserved Verbatim per `AGENTS.md`)

All new `copied-stat` pairs reported by `kb_lint.py` were verified directly against the extracted source paper texts:
- [`infrarsi-training-infrastructure-rsi.md`](../research-briefs/infrarsi-training-infrastructure-rsi.md) (`arXiv:2611.11558`): `2.00%` and `3.00%` verified in Table 6B (`loss_tol` sweep `0.50%, 1.00%, 2.00%, 5.00%`; `clock_tol` sweep `1.00%, 3.00%, 5.00%`).
- [`reins-real-time-trajectory-planning-harness.md`](../research-briefs/reins-real-time-trajectory-planning-harness.md) (`arXiv:2611.10748`): `18.47%` (`Plan-R1` Roundabout CR), `25.93%` (`LLaDA` Highway CR), and `35.21%` (`DriveVLM` Intersection CR) verified in Table 1.
- [`webtrap-farm-web-agent-harness-security.md`](../research-briefs/webtrap-farm-web-agent-harness-security.md) (`arXiv:2611.11971`): `57.69%`, `78.99%`, `10.65%`, and `16.67%` verified directly in the `WebTrap Farm` harness evaluation and Stage II/III `Conditional_DSR` tables.
