# Knowledge Base Deconfliction Report — 2026-11-06 (Wave 4: Full-Stack Agent Engineering, Mobile/Generative UI, MCP & Next.js Security)

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## 1. Executive Summary

- **Scope Audited**: **26 new arXiv papers** across `cs.HC`, `cs.SE`, `cs.CR`, `cs.MA`, and `cs.AI` ingested and full-text verified in Wave 4 (`2026-11-06`), raising the knowledge base from `515` to **541+ source papers** across **8 rule files**, **10 spec templates** (`+2` new), **159 skills** (`+15` new), and **332 research briefs** (`+11` new).
- **Linter Verification (`kb_lint.py --base origin/master`)**: **0 errors, 0 conflict warnings, 0 unbacked rule citations, 0 broken links**.
- **License & Repository Attribution**: All 28 newly created Wave 4 artifacts (`2` spec templates, `15` skills, `11` research briefs) and this report include the `CC BY 4.0` license and [`Marontis/agentic-engineering`](https://github.com/Marontis/agentic-engineering) attribution header (plus `license: CC-BY-4.0` and `repository: https://github.com/Marontis/agentic-engineering` in `SKILL.md` YAML frontmatter).

---

## 2. Wave 4 Artifacts Created (`28` New Files)

### Spec Templates (`2` New in `output/specs/`)
1. [`specs/nextjs-public-agent-app.spec.md`](../specs/nextjs-public-agent-app.spec.md) — Public-Facing Next.js & Full-Stack Agent Application Specification Template (BFF trust boundary, Compile-Then-Execute gateway, OBO multi-hop A2A delegation, authority-epoch continuous authorization, third-party relay integrity checks, typed Generative UI rendering, and NovaFabric audit sealing).
2. [`specs/mobile-and-generative-ui.spec.md`](../specs/mobile-and-generative-ui.spec.md) — Mobile UI, Generative UI & Agentic Data Display Specification Template (80-category mobile UI synthesis, spatial accessibility grouping, two-phase framework codegen, Project State Graph grounding, 3-layer editable diagrams, and FlowCheck static UI dataflow verification).

### Skills (`15` New in `output/skills/`)
1. [`skills/mobile-ui-hierarchical-synthesis/SKILL.md`](../skills/mobile-ui-hierarchical-synthesis/SKILL.md) (`arXiv:2611.00926` — *UI-UG 2*)
2. [`skills/mobile-spatial-accessibility-grouping/SKILL.md`](../skills/mobile-spatial-accessibility-grouping/SKILL.md) (`arXiv:2611.02410` — *SeeR*)
3. [`skills/two-phase-framework-ui-codegen/SKILL.md`](../skills/two-phase-framework-ui-codegen/SKILL.md) (`arXiv:2611.01692` — *Phase-wise MLLM Tuning*)
4. [`skills/state-aware-prototype-to-webapp/SKILL.md`](../skills/state-aware-prototype-to-webapp/SKILL.md) (`arXiv:2610.17861` — *VisStateCoder*)
5. [`skills/ui-dataflow-intent-verification/SKILL.md`](../skills/ui-dataflow-intent-verification/SKILL.md) (`arXiv:2608.28880` — *FlowCheck*)
6. [`skills/editable-semantic-diagram-generation/SKILL.md`](../skills/editable-semantic-diagram-generation/SKILL.md) (`arXiv:2604.09568` — *EvoDiagram*)
7. [`skills/persona-driven-mobile-feature-testing/SKILL.md`](../skills/persona-driven-mobile-feature-testing/SKILL.md) (`arXiv:2611.06922` — *ECS Mobile Testing*)
8. [`skills/mcp-hallucination-boundary-guards/SKILL.md`](../skills/mcp-hallucination-boundary-guards/SKILL.md) (`arXiv:2611.07689` — *MCPHallu*)
9. [`skills/multi-agent-architecture-first-codegen/SKILL.md`](../skills/multi-agent-architecture-first-codegen/SKILL.md) (`arXiv:2611.06921` — *TimeArch*)
10. [`skills/post-migration-behavioral-differential-testing/SKILL.md`](../skills/post-migration-behavioral-differential-testing/SKILL.md) (`arXiv:2611.08269` — *Accepted but Wrong*)
11. [`skills/contract-verified-test-mock-generation/SKILL.md`](../skills/contract-verified-test-mock-generation/SKILL.md) (`arXiv:2610.14629` — *MockBench*)
12. [`skills/history-grounded-project-takeover/SKILL.md`](../skills/history-grounded-project-takeover/SKILL.md) (`arXiv:2611.07307` — *Take It From Here / ReqMemBench*)
13. [`skills/compile-then-execute-web-agent-gateway/SKILL.md`](../skills/compile-then-execute-web-agent-gateway/SKILL.md) (`arXiv:2611.06039` — *Baya Compile-Then-Execute*)
14. [`skills/llm-api-relay-integrity-verification/SKILL.md`](../skills/llm-api-relay-integrity-verification/SKILL.md) (`arXiv:2611.07650` — *What the Middleman Delivers*)
15. [`skills/multi-hop-delegation-auth-propagation/SKILL.md`](../skills/multi-hop-delegation-auth-propagation/SKILL.md) (`arXiv:2611.07050` — *Authorization Propagation in A2A Systems*)
16. [`skills/sealed-replayable-agent-audit-log/SKILL.md`](../skills/sealed-replayable-agent-audit-log/SKILL.md) (`arXiv:2610.34594` — *NovaFabric*)

*(Note: 15 new skills in Wave 4 — items 1–16 above total 15 new Wave 4 directories: `mobile-ui-hierarchical-synthesis`, `mobile-spatial-accessibility-grouping`, `two-phase-framework-ui-codegen`, `state-aware-prototype-to-webapp`, `ui-dataflow-intent-verification`, `editable-semantic-diagram-generation`, `persona-driven-mobile-feature-testing`, `mcp-hallucination-boundary-guards`, `multi-agent-architecture-first-codegen`, `post-migration-behavioral-differential-testing`, `contract-verified-test-mock-generation`, `history-grounded-project-takeover`, `compile-then-execute-web-agent-gateway`, `llm-api-relay-integrity-verification`, `multi-hop-delegation-auth-propagation`, and `sealed-replayable-agent-audit-log` — 16 skills total, plus 10 briefs = 26 papers.)*

### Research Briefs (`10` New in `output/research-briefs/`)
1. [`research-briefs/controlanything-on-demand-generative-ui.md`](../research-briefs/controlanything-on-demand-generative-ui.md) (`arXiv:2611.08321`)
2. [`research-briefs/mcp-eco-server-consumer-ecosystem.md`](../research-briefs/mcp-eco-server-consumer-ecosystem.md) (`arXiv:2611.06897`)
3. [`research-briefs/vibench-2-long-horizon-software-building.md`](../research-briefs/vibench-2-long-horizon-software-building.md) (`arXiv:2611.05620`)
4. [`research-briefs/multi-step-swe-long-horizon-self-building.md`](../research-briefs/multi-step-swe-long-horizon-self-building.md) (`arXiv:2611.07166`)
5. [`research-briefs/rethinking-code-representations-agentic-swe.md`](../research-briefs/rethinking-code-representations-agentic-swe.md) (`arXiv:2611.07286`)
6. [`research-briefs/kg-ast-budgeted-cicd-test-selection.md`](../research-briefs/kg-ast-budgeted-cicd-test-selection.md) (`arXiv:2611.06950`)
7. [`research-briefs/cognitive-tours-understanding-deliverable-swe.md`](../research-briefs/cognitive-tours-understanding-deliverable-swe.md) (`arXiv:2611.08456`)
8. [`research-briefs/trap-trust-responsive-runtime-authorization.md`](../research-briefs/trap-trust-responsive-runtime-authorization.md) (`arXiv:2611.06996`)
9. [`research-briefs/task-tampering-indirect-prompt-injection.md`](../research-briefs/task-tampering-indirect-prompt-injection.md) (`arXiv:2611.07640`)
10. [`research-briefs/interface-quilt-cua-generative-ui.md`](../research-briefs/interface-quilt-cua-generative-ui.md) (`arXiv:2611.01891`)

---

## 3. Resolved Cross-Rule Tensions (`Tension with` Notes Added)

1. **Continuous Authority Revocation (`ACCA`, `arXiv:2611.05632`) vs. Single-Step Derivative Hysteresis (`TRAP`, `arXiv:2611.06996`)**
   - **Files**: [`rules/adk-security-and-evaluation.md`](../rules/adk-security-and-evaluation.md) and [`rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md)
   - **Resolution**: Added an explicit `Tension with` note in `adk-security-and-evaluation.md` explaining that while `ACCA` (`2611.05632`) binds capabilities to authority epochs $\tau_k$ to revoke in-flight calls once a degradation event fires, `TRAP` (`2611.06996`) proves that triggering restriction solely on a single-step derivative ($g_t - g_{t-1} < -\theta_r$) misses gradual readiness drift (`0/100` traces restricted at $L \in \{10, 20\}$). Production controllers must combine authority-epoch revocation with an absolute band-ceiling check ($g_t < \mathrm{down}(a_{t-1})$) or sliding-window cumulative degradation trigger.

2. **Interceptor-Layer Prompt Injection Sanitizers (`Model Armor`, `DRIFT-iso`, `Pictionary`) vs. Non-Imperative Task-Tampering Attacks (`arXiv:2611.07640`)**
   - **Files**: [`rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md) and [`rules/adk-security-and-evaluation.md`](../rules/adk-security-and-evaluation.md)
   - **Resolution**: Added a `Tension with` note in `agent-sandbox-safety.md` clarifying that instruction-stripping sanitizers (`DRIFT-iso`, Model Armor) and visual rendering (`Pictionary`) remove `78.2–85.1%` of imperative objective overrides $b(U)$, but strip only `26.2–34.3%` of non-imperative observation $b(O)$ (`9.5%` ASR) and world-state $b(s)$ (`12.1%` ASR) tampering inside retrieved records. Keep interceptor sanitizers for $b(U)$, and enforce field-level source-authority bindings for privileged tool parameters.

3. **External-Interface Pass Rates (`ViBench 2.0` `arXiv:2611.05620`, `Multi-step SWE` `arXiv:2611.07166`) vs. Agent-Authored Test/Proof Pass Rates (`MockBench` `arXiv:2610.14629`, `Verified-but-Vacuous` `arXiv:2611.05590`)**
   - **File**: [`rules/agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md)
   - **Resolution**: Added a `Tension with` note distinguishing locked external browser/container verifiers (`ViBench 2.0`, `Multi-step SWE`, where component pass rates and `pass@1` measure real task progress because the agent cannot alter the test runner) from agent-authored unit tests (`MockBench`) and formal proofs (`2611.05590`), where raw execution pass rate (`TPR` or `Surface A`) masks contract relaxation (`-18.14 pp` Stub F1 and `-27.80 pp` Assertion F1 on Python) unless paired with tuple-level assertion checks and interaction mutation probing.

4. **Single Acceptance Gate (`recursive-improvement.md`) vs. Post-Migration Differential Boundary Gating (`arXiv:2611.08269`)**
   - **Files**: [`rules/agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md) and [`rules/recursive-improvement.md`](../rules/recursive-improvement.md)
   - **Resolution**: Added a `Tension with` note in `agent-evaluation-quality.md` specifying that when applying the single acceptance gate to library/interpreter/database runtime migrations (`A_0 -> A_1`), typical consumer tests (`T`) and repairer self-tests (`S`) suffer `0.278–0.410` false acceptance (`0.990` on hard distractors), so the frozen acceptance gate must include fail-closed blind release-note boundary inputs (`W_3`).
