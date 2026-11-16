<!--
Licensed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
Attribution: Marontis / agentic-engineering (https://github.com/Marontis/agentic-engineering).
-->

# Deconfliction Report — 2026-11-16 (`cs.AI` Agentic High-Tier Wave 9)

## Scope

This audit covers the 9 strictly agentic `cs.AI`-only high-tier (`score >= 8.0`) papers ingested on `2026-11-16` (covering all `164` new `cs.AI` announcements since the `2026-11-13` batch; excluding `2` non-agentic `cs.AI` papers: `2611.17846` single-turn base-LLM weight refusal abliteration and `2611.17505` classical `YOLOv3/v4 + SORT` CV object tracking), which produced:
- **3 new skills**:
  - [`similarity-consensus-subtask-aggregation`](../skills/similarity-consensus-subtask-aggregation/SKILL.md) (`arXiv:2611.17883` — `SecMAS`)
  - [`verification-transport-provenance-audit`](../skills/verification-transport-provenance-audit/SKILL.md) (`arXiv:2611.18471` — *Verification Transport*)
  - [`tiered-contract-readiness-gate`](../skills/tiered-contract-readiness-gate/SKILL.md) (`arXiv:2611.17381` — `ProdPilot`)
- **6 new research briefs**:
  - [`weakest-agent-delegation-safety-collapse`](../research-briefs/weakest-agent-delegation-safety-collapse.md) (`arXiv:2611.17520` — defensive lessons only)
  - [`pace-multi-agent-compute-parity-synthesis`](../research-briefs/pace-multi-agent-compute-parity-synthesis.md) (`arXiv:2611.17610` — `PACE` `516`-config meta-evaluation)
  - [`symbolic-vocabulary-obfuscation-planner-defenses`](../research-briefs/symbolic-vocabulary-obfuscation-planner-defenses.md) (`arXiv:2611.17910` — *Symbolic-Swapper*, defensive lessons only)
  - [`autorl-process-level-autonomous-rl`](../research-briefs/autorl-process-level-autonomous-rl.md) (`arXiv:2611.17790` — `AutoRL`)
  - [`sceneagent-portable-game-scene-generation`](../research-briefs/sceneagent-portable-game-scene-generation.md) (`arXiv:2611.17821` — `SceneAgent`)
  - [`mastars-sequential-trajectory-augmentation-marl`](../research-briefs/mastars-sequential-trajectory-augmentation-marl.md) (`arXiv:2611.17793` — `MASTARS`, MARL brief-only)
- **7 new rule entries** across [`multi-agent-coordination.md`](../rules/multi-agent-coordination.md), [`agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md), [`skill-system-design.md`](../rules/skill-system-design.md), and [`recursive-improvement.md`](../rules/recursive-improvement.md) (plus reciprocal `Tension with` and `**Scope:**` backfills in [`agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md)), alongside checklist updates to [`adk-multi-agent-a2a.spec.md`](../specs/adk-multi-agent-a2a.spec.md), [`adk-agentic-workflow.spec.md`](../specs/adk-agentic-workflow.spec.md), [`adk-eval-quality-gate.spec.md`](../specs/adk-eval-quality-gate.spec.md), [`nextjs-public-agent-app.spec.md`](../specs/nextjs-public-agent-app.spec.md), [`self-improving-agent.spec.md`](../specs/self-improving-agent.spec.md), and [`skill-library.spec.md`](../specs/skill-library.spec.md).

---

## Genuine Tensions Resolved (`Tension with`)

### 1. Trimmed Embedding Consensus (`SecMAS`) vs. Minority-Viewpoint Preservation & Intra-Family Pool Selection (`multi-agent-coordination.md`)
- **Entry A**: `"DO: Aggregate untrusted parallel subtask responses via trimmed nearest-neighbor embedding consensus rather than LLM summarization or confidence scoring"` (`SecMAS`, `arXiv:2611.17883`)
- **Entries B & C**: `"DO: Preserve minority viewpoints in agent voting and consensus"` (`arXiv:2609.02990`) and `"DON'T: Expand candidate model pools with arbitrary heterogeneous architectures"` (`arXiv:2609.17306`)
- **Resolution**: Added reciprocal `Tension with` notes across all three entries. `SecMAS` deliberately trims the $f_i + 1$ most distant embeddings to reject colluding Byzantine minorities on objective subtasks (`0.00–0.02` untargeted / `0.00–0.01` targeted ASR vs. `0.84–1.00` on 5 baseline rules), whereas pluralistic preference consultations (`arXiv:2609.02990`) retain good-faith minority dissent. Likewise, while intra-family pools reduce confidence-calibration noise in benign routing (`arXiv:2609.17306`), diversifying workers across `2` to `8` model backbones under adversarial response manipulation (`arXiv:2611.17883`) suppresses surrogate attack transferability while scoring responses in one shared embedding space (`Qwen3-Embedding-8B`).

### 2. Weakest-Reader Delegation Safety (`arXiv:2611.17520`) & Verification Transport (`arXiv:2611.18471`) vs. Cheap Subtask Delegation (`AgentFactory`), Context Partitioning, and Peer-Verifier History Limits
- **Entries A & B**: `"DON'T: Delegate untrusted evidence reading to a weaker sub-agent without forwarding primary source records to the orchestrator or verifier"` (`arXiv:2611.17520` in `multi-agent-coordination.md`) and `"DO: Audit trajectory verifiers for Verification Transport across abstraction boundaries and attach lossless boundary provenance"` (`arXiv:2611.18471` in `agent-evaluation-quality.md`)
- **Entries C, D & E**: `"DO: Optimize topology and model assignment jointly"` (`AgentFactory`, `arXiv:2609.01045`, backfilled with `**Scope:**`), `"DON'T: Share full context across all agents by default"` (`arXiv:2609.03920`), and `"DON'T: Expose full interaction history to peer-verifying agents"` (`arXiv:2609.24967` in `recursive-improvement.md`)
- **Resolution**: Added reciprocal `Tension with` notes across all five entries. Delegating subtasks to cheaper smaller models reduces cost on trusted inputs, and local summary extraction protects private user data; however, on untrusted external corpora (`arXiv:2611.17520`), summarizing inside a weaker sub-agent strips provenance cues (`180/180 -> 96/180`, $p = 10^{-31}$) and causes `96.3%` (`751/757`) aggregator cascades (`0/780` when raw source records accompany the report). Similarly, hiding `ToolCall -> ToolResult` sequences behind macro-tool (`31.0%` VTFR), delegation (`30.9%` VTFR), or compaction (`20.3%` VTFR) summaries induces `41.3%` False Certification Rate under direct `V-LLM` judges (`arXiv:2611.18471`), requiring out-of-band lossless `BND-*` provenance envelopes (`85.5%` recovery) for *within-episode* independent verifiers while still keeping *cross-episode* reward-coupled peer history closed (`94%` collusion in `arXiv:2609.24967`).

### 3. `PACE` Sample- & Compute-Parity Benchmarking (`arXiv:2611.17610`) vs. Verifiable Parallel Flat Teams (`arXiv:2611.09798`) & Cross-Family Deliberation (`arXiv:2609.22497`, `arXiv:2609.22682`)
- **Entry A**: `"DON'T: Claim coordination gains over greedy decoding without sample-parity and compute-parity baselines and 6D PACE accounting"` (`arXiv:2611.17610` in `agent-evaluation-quality.md`)
- **Entries B & C**: `"DO: Scale test-time compute on verifiable long-horizon tasks via parallel small flat teams rather than solo Best-of-N, one giant team, or manager orchestration"` and `"DO: Use heterogeneous, cross-family rosters for deliberation and joint verification"` (`multi-agent-coordination.md`)
- **Resolution**: Added reciprocal `Tension with` notes across all three entries. Across `474` sample/budget-matched `Category B/C` contrasts predominantly on shared-prompt unverified tasks, `MAS` averaged $\bar{\Delta} = -0.042$ (`74%` $\le 0$, REML $\hat{\beta} = -0.195$, $p = 0.0076$). Positive returns require exactly one of `PACE`'s three structural routes: partitioned evidence (Route I), an asymmetric external verifier ($\epsilon_{\text{FP}} \to 0 \implies p^* \to 1$, Route II—instantiated by `10` flat teams of `10` beating `100` solo `Best-of-N` runs in `arXiv:2611.09798`), or cross-family error decorrelation ($\rho_{\text{het}} < \rho_{\text{hom}}$, Route III—instantiated in `arXiv:2609.22497` / `2609.22682`), benchmarked against `Category B/C` baselines rather than a single greedy pass.

### 4. Tiered Zero-LLM MCP Readiness Contracts (`ProdPilot`, `arXiv:2611.17381`) vs. Workspace Mock-Test Gaming (`MockBench`) & YAML CST Span Editing (`KubeAstra`)
- **Entry A**: `"DO: Partition automated readiness repairs into static, ambiguity-refusing parametric, and checker-bound delegated contracts behind a zero-LLM MCP server"` (`ProdPilot`, `arXiv:2611.17381` in `skill-system-design.md`)
- **Entries B & C**: `"DON'T: Equate test execution pass rate (TPR) with mock contract fidelity or allow agents to relax interaction assertions during repair"` (`MockBench`, `arXiv:2610.14629` in `agent-evaluation-quality.md`) and `"DON'T: Let the model author raw diffs or full rewrites for declarative manifests"` (`arXiv:2609.00227` in `agent-sandbox-safety.md`, backfilled with `**Scope:**`)
- **Resolution**: Added reciprocal `Tension with` notes across all three entries. Unlike `MockBench` where agents edit mock assertions inside their own workspace, `ProdPilot` keeps all `50` AST/config/entropy checkers frozen inside a zero-LLM MCP server (`10.5%` false-report rejection + automatic regression revert). Relative to `KubeAstra`'s scalar YAML CST span edits, `ProdPilot` eliminates the LLM altogether on `88.0%` of readiness rules (`93.5%` of `7,407` real violations) via anchored static templates and ambiguity-refusing parametric extractions (`20.3%` refusal on multi-candidate projects), delegating only `12.0%` (`6/50`) architecture-dependent source refactors under strict file-boundary contracts.

### 5. In-Flight `AutoRL` Supervision (`arXiv:2611.17790`) vs. Reasoning-Effort Algorithmic Scaling (`AI4AI-Bench`) & Frozen Evaluation Harnesses
- **Entry A**: `"DO: Supervise ongoing RL runs via CPU-checked online hot updates and lineage-tracked cold resumptions while keeping evaluation protocols frozen"` (`AutoRL`, `arXiv:2611.17790` in `recursive-improvement.md`)
- **Entries B & C**: `"DON'T: Conflate reasoning effort with algorithmic ability"` (`arXiv:2608.20318` in `recursive-improvement.md`) and `"DON'T: Let agents modify their own evaluation harness"` (`arXiv:2609.00069` in `agent-evaluation-quality.md`)
- **Resolution**: Added reciprocal `Tension with` notes across all three entries. While higher reasoning effort raises willingness to attempt bundled learning-side edits (`8% -> 64%` on `AI4AI-Bench`), live `AutoRL` runs with `gpt-6.1-sol` succeeded via `TRAIN`-signal/grader repair (`10/20`) and parameter tuning (`9/20`) while `0/3` learning-rule redesigns were deployed. Critically, `AutoRL` mutates only the `TRAIN` rollout reward grader (verified on isolated CPU fixtures before step-boundary `HOT` activation) while keeping the `EVAL` harness strictly frozen and read-only.

### 6. Canonical-State Portable Construction & `Layout`/`Content` Skill Factorization (`SceneAgent`, `arXiv:2611.17821`) vs. Code-Embedding Functional Retrieval (`ExecRetrieval`) & Multi-Agent Topology Tax
- **Entry A**: `"DO: Isolate backend coordinates and asset IDs behind canonical state adapters and factor spatial-layout skills from semantic-content skills"` (`SceneAgent`, `arXiv:2611.17821` in `skill-system-design.md`)
- **Entries B & C**: `"DON'T: Rely on dense semantic embeddings alone for retrieving code or executable skills without execution verification"` (`ExecRetrieval`, `arXiv:2609.01865`, backfilled with `**Scope:**`) and `"DON'T: Default to a fixed multi-agent topology"` (`multi-agent-coordination.md`)
- **Resolution**: Added reciprocal `Tension with` notes across all three entries. Even for non-code declarative `Layout`/`Content` skills and `InfoNCE` asset candidates, `50` vs. `0` skills lowered 3D `Spatial Plausibility` below parity (`46.2%`), requiring deterministic bounding-box/geometry checks (`check_bbox_collision`) before commit; and `Orchestrator -> Planner -> fresh Builder` canonical-state handoffs trade `5.17x` runtime (`203.2 s` vs. `39.3 s`) for higher multi-region `Completeness` (`62.4%` vs. `37.7%`).

---

## Triage Rigor, `copied-stat` Audit & Automated Lint Verification

- **Offensive-Security Policy & MARL Scope Discipline (`output/AGENTS.md`)**:
  - `SecMAS` (`arXiv:2611.17883`), *Weakest Agent* (`arXiv:2611.17520`), and *Symbolic-Swapper* (`arXiv:2611.17910`) omit offensive surrogate-optimization prompts, forgery templates, and adversarial symbol-generation prompts, capturing strictly defensive aggregation, provenance-forwarding, and planner-canonicalization guardrails.
  - [`mastars-sequential-trajectory-augmentation-marl.md`](../research-briefs/mastars-sequential-trajectory-augmentation-marl.md) (`arXiv:2611.17793`) is retained as a contextual Research Brief without a standalone LLM coordination rule because its `64.3M`-parameter Dec-POMDP DDPM `RePaint` pipeline involves zero LLMs.
- **Verified `copied-stat` Coincidence on `AutoRL` (`arXiv:2611.17790`)**:
  - `autorl-process-level-autonomous-rl.md` triggers informational `copied-stat` pair notices on standard competition-math and coding benchmark grid fractions (`2.00%`, `5.00%`, `12.50%`, `13.33%`, `15.00%`, `16.06%`, `30.00%`, `31.80%`, `34.34%`, `41.58%`, `43.33%`, `45.00%`, `56.05%` arising from `AIME 24/25` `30x4=120`, `IMO-AnswerBench` `1600`, `GPQA-Diamond` `792`, `MBPP` `2000`, and `380`-sample monitoring denominators). Every figure was verified verbatim against `2611.17790` (`Tables 1–2`, `§3.3–3.4`) and preserved unmodified per `AGENTS.md`.
- **`kb_lint.py` Audit**:
  - Running `python -X utf8 scripts/kb_lint.py --base origin/master` across both `bo-praxis/output` and `agentic-engineering` passed with **`0 error(s)`** and **`0` `conflict:` warnings**.
