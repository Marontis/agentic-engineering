# Skill Library Specification Template

> Fill in this template when designing a skill memory system for LLM agents.
> Each section surfaces research-backed decision points for skill authoring,
> storage, retrieval, and selection.
>
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## 1. Scope & Purpose

### What kind of agent will use this skill library?

- [ ] Coding agent (code generation, debugging, tooling)
- [ ] Productivity agent (office workflows, automation)
- [ ] Research agent (paper analysis, data science)
- [ ] General-purpose assistant
- [ ] Other: ___

### What is the expected library size?

- [ ] Small (< 10 skills) — top-k retrieval is sufficient
- [ ] Medium (10–100 skills) — need set-level selection
- [ ] Large (100–1000 skills) — need retrieval pre-filter + set-level selection
- [ ] Ecosystem-scale (1000+ skills) — need registry, routing, and selection pipeline

### What is the context budget?

- Total context window: ___ tokens
- Reserved for system prompt: ___ tokens
- Reserved for task input: ___ tokens
- Reserved for agent reasoning: ___ tokens
- **Available for skills**: ___ tokens

> **Research note**: the residual token budget after system prompt, task
> input, and reasoning space is the hard constraint for skill selection.
> Every skill token has a measurable cost (κ). (arXiv:2608.19993)

---

## 2. Skill Authoring

### Skill induction level:

- [ ] **Subtask-level** (recommended) — one skill per reusable procedure
- [ ] Task-level — one skill per completed workflow
- [ ] Rule-level — one skill per learned constraint
- [ ] Step-level — one skill per individual action

> **Evidence**: task-level skills harm performance by 1.2–4.1 pts.
> Subtask-level skills improve by 0.5–1.9 pts. Validated across 11 models
> and 3 benchmarks. (arXiv:2608.20274)

### Skill format:

- [ ] **Text** (recommended) — natural-language workflow notes with caveats
- [ ] Code — Python functions with parameterized values
- [ ] Hybrid — text description with illustrative code snippets

> **Evidence**: text skills transfer better than code skills at both
> induction levels, on every benchmark, at every difficulty stratum.
> (arXiv:2608.20274)

### Skill structure:

Each skill should contain:

- [ ] **Description** (1-2 sentences) — used for retrieval matching
- [ ] **When to use** — decision criteria for when this skill applies
- [ ] **Procedure** — the step-by-step workflow
- [ ] **Environment caveats** — where the procedure differs across contexts
- [ ] **Failure modes** — what goes wrong when applied incorrectly
- [ ] **Cross-references** — links to related skills

### Authoring checklist (apply to every new skill):

- [ ] Does this skill describe ONE reusable procedure?
- [ ] Could this procedure appear in 3+ different project types?
- [ ] Is the body written as natural language, not executable code?
- [ ] Does it explain WHEN and WHY, not just HOW?
- [ ] Does it note failure modes?

> **Source**: skill-design-methodology skill (arXiv:2608.20274)

---

## 3. Skill Storage

### Storage backend:

- [ ] Flat files (SKILL.md in directories) — simplest, works with version control
- [ ] Database (SQLite/PostgreSQL with vector column)
- [ ] Vector store (Pinecone, Weaviate, Chroma)
- [ ] Knowledge graph (Praxis-style with semantic edges)

### Metadata per skill:

- [ ] Name/ID
- [ ] Description (embedding target)
- [ ] Source reference (paper, codebase, experience)
- [ ] Creation date
- [ ] Last validated date
- [ ] Utility score (specificity × abstractness)
- [ ] Token length (for budget planning)
- [ ] Category/tags
- [ ] Cross-references to related skills

### Deduplication strategy:

- [ ] Embedding similarity threshold (merge if cosine > ___)
- [ ] Manual review for near-duplicates
- [ ] Automated pruning of low-utility skills (utility < ___)

---

## 4. Skill Retrieval

### Retrieval method:

- [ ] Embedding similarity (dense retrieval)
- [ ] BM25 (keyword matching)
- [ ] Hybrid (dense + sparse)
- [ ] LLM-based routing (model selects by description)
- [ ] Graph traversal (follow semantic edges)

### Retrieval scope:

- [ ] Query with task description
- [ ] Query at each subtask/step
- [ ] Query with task description + current context
- [ ] Progressive disclosure (names first, load body on request)

### Top-k setting:

- [ ] Fixed k = ___
- [ ] **Dynamic k based on token budget** (recommended)
- [ ] Return all above similarity threshold

> **Pitfall**: fixed top-k ignores skill length. A budget-aware selector
> should consider token cost, not just relevance rank. (arXiv:2608.19993)

---

## 5. Skill Selection (Runtime)

### Selection method:

For libraries with < 10 skills:
- [ ] Top-k by relevance (acceptable for small libraries)

For libraries with 10+ overlapping skills:
- [ ] **BPS algorithm** (recommended — provably optimal)
- [ ] Density greedy (45% optimal, simpler to implement)
- [ ] MMR (diversity-aware, 7.5% optimal)
- [ ] LLM self-selection (executor picks, 0.52 success vs 0.73 for BPS)

> **Evidence**: BPS reaches 0.73 task success vs 0.20–0.52 for baselines,
> on 28% fewer tokens. (arXiv:2608.19993)

### Capability modeling:

If using BPS or capability-aware selection:

- [ ] Number of capability dimensions (d): ___ (default: 8–16 to learn)
- [ ] Encoder type:
  - [ ] Lookup tables (281 params, requires fixed task/skill sets)
  - [ ] **Neural encoder** (projects text embeddings into capability space)
- [ ] Response function: h(x) = 1 − e^(−x) (recommended default)
- [ ] Training data: (query, skill_set, pass/fail) records from execution

### Token budget allocation:

- [ ] Hard budget B = ___ tokens for skill documents
- [ ] Context penalty coefficient κ = ___ (fit from execution data)
- [ ] Selection objective: max_{S: ℓ(S) ≤ B}  [G(S) − κ·ℓ(S)]

---

## 6. Skill Library Health

### Pre-deployment audit:

Run the skill utility score against your task corpus:

- [ ] Compute specificity × abstractness for each skill
- [ ] Flag skills with utility < 0.15
- [ ] Identify skills with high specificity / low abstractness (too narrow)
- [ ] Identify skills with low specificity / high abstractness (too vague)

### Ongoing monitoring:

- [ ] Track transfer density: what share of skill transfers actually happen
- [ ] Track retrieval hit rate: are skills being found when needed?
- [ ] Track execution lift: do tasks with skills outperform tasks without?
- [ ] Review low-reuse skills for revision or removal
- [ ] Schedule: audit every ___ (weeks/months)

### Scaling triggers:

| Library Size | Action |
|:-------------|:-------|
| Reaching 50+ skills | Add retrieval pre-filter before selection |
| Reaching 100+ skills | Implement capability modeling and BPS |
| Transfer density declining | Audit for redundancy and low-utility skills |
| New domain added | Create domain-specific retrieval indexes |

---

## 7. Knowledge Persistence

> **Research note**: separating persistent knowledge from executable skills
> adds +15.0pp average performance. The knowledge layer survives skill
> rollbacks and compounds across iterations. (arXiv:2608.27454)

### Does your skill system persist knowledge across rollbacks?

- [ ] **Yes** (recommended for iterative skill evolution) — maintain a
  knowledge layer (patterns, root-cause analyses, evolution logs) that
  persists even when skills are rolled back
- [ ] **No** — skills are the only knowledge representation; rollback
  discards everything

### If persisting knowledge:

- [ ] Knowledge layer is append-and-update, never reset
- [ ] Knowledge is NOT accessible to the executing agent (only to the
  skill proposer) — ablation shows wiki access during execution degrades
  quality by −2.8pp
- [ ] Each skill links back to the knowledge patterns that motivated it
- [ ] Every skill proposal's outcome (accepted/rejected, validation score,
  diff) is recorded in an impact tracker

### Admission gate for new or evolved skills:

Optimizer and evolution skills pick candidates; admission follows
`rules/recursive-improvement.md` "DO: Pass every self-modification
through one acceptance gate": accept a change only if it shows no
regression beyond a noise margin δ on previously-correct cases and
held-out tasks, where δ is estimated from repeated runs of the unchanged
baseline; the negative security testbed is always strict (zero
tolerance, no margin).

- [ ] δ estimated from ___ runs of the unchanged library (at least 3; fewer only if deterministic)
- [ ] Protected (previously-correct) cases and held-out tasks re-run on every admission
- [ ] Negative security testbed run on every candidate; any failure rejects it
- [ ] Provenance verified before admission (see [`skill-evolution-defense`](../skills/skill-evolution-defense/SKILL.md))

> **Source**: knowledge-compounding-loop skill (arXiv:2608.27454)

---

## 8. Pitfall Checklist

Before deploying the skill library, verify:

- [ ] Skills are at subtask level, not task level
- [ ] Skill bodies are text, not code
- [ ] Every skill has been scored for utility (specificity × abstractness)
- [ ] Selection considers set-level interactions, not just individual relevance
- [ ] Token budget is explicitly set and enforced
- [ ] Deduplication prevents near-duplicate skills from entering the library
- [ ] Monitoring is in place to detect skill degradation over time
- [ ] Admitted skills or persistent behavioral hypotheses track an online runtime violation EMA and are automatically evicted or quarantined when violations exceed threshold $\tau_{\text{evict}}$ ([`falsification-gated-memory-evolution`](../skills/falsification-gated-memory-evolution/SKILL.md), arXiv:2611.14326)
- [ ] Distilled skills or trajectory memories generated by a stronger writer model are validated on the actual reader/executor model tier before promotion, avoiding capability-mismatched guidance (arXiv:2611.14256)
- [ ] For multi-backend constructive generators, distilled skills strip concrete backend asset IDs and native serialization calls into orthogonal structural (`Layout`) vs. semantic/substitution (`Content`) skills + thin prompt recipes behind an Orchestrator-only export adapter, paired with deterministic geometry/bounds checks since text skills improve completeness (`63.8%`) without guaranteeing spatial plausibility (`46.2%` vs. `0` skills; [`sceneagent-portable-game-scene-generation`](../research-briefs/sceneagent-portable-game-scene-generation.md), arXiv:2611.17821)
- [ ] Under reference-free continual tool or workflow drift, playbook sections are bounded (`<= 4,200` chars), keyed to `Turn-0` tool/schema signatures, pinned on `Mastered` criteria ($\mathrm{Priority}_t = 0$), and gated via `Soft-HURT` + one-pass `[iff]` precondition narrowing with windowed JSONL rejection ledgers ([`regret-guided-continual-harness-evolution`](../skills/regret-guided-continual-harness-evolution/SKILL.md), arXiv:2611.23476)
- [ ] Executable state-compaction (`state`) and counterfactual world-model (`wm`) harness modules run in time/line-capped sandboxes against framework-owned graph state and quarantine automatically after $L = 3$ consecutive episode failures ([`asynchronous-system1-harness-evolution`](../skills/asynchronous-system1-harness-evolution/SKILL.md), arXiv:2611.22432)
- [ ] Shared multi-agent episodic/insight memories (`Basic` / `G-Memory`) strip uncorroborated peer side-claims not verified by tools or primary sources rather than gating writes on episode-level team answer correctness alone, retain `originating_agent_id` across distillation, and elicit Round-1 agent commitments before injecting retrieved memories ([`mimpa-insider-shared-memory-poisoning-defensive-lessons`](../research-briefs/mimpa-insider-shared-memory-poisoning-defensive-lessons.md), arXiv:2611.31307)
- [ ] For script-bearing skills (`S = (P, M)`) revised without task-specific verifiers, bundled scripts `P` stay frozen read-only (`SHA-256`-checked) while `M` is patched via `<= 4` non-overlapping substring edits grounded in AST-indexed operational contracts aligned against trace gaps—avoiding raw script dumping (`-18.89 pp` `P@1` drop) ([`tool-implementation-grounded-skill-revision`](../skills/tool-implementation-grounded-skill-revision/SKILL.md), arXiv:2611.32480)
- [ ] Under sparse binary pass/fail evaluation, memory distillation overrides agent self-reported success with external verdicts (`50%` false-verified rate otherwise), separates silent-contradiction failures from terminal tracebacks, generalizes docstrings (`+6.3 pp`), pre-injects `solution_pattern` entries as **API names only** at Turn 0 (`+4.7 pp`), and serves `pitfall` entries **on demand** upon runtime/AST errors rather than Turn-0 pre-injection (`-8.0 pp` drop) ([`anti-leakage-sparse-feedback-memory-distillation`](../skills/anti-leakage-sparse-feedback-memory-distillation/SKILL.md), arXiv:2611.26912)
- [ ] For recurring API or database workflows with trainable open-weight adapters, workflow skills (`< 1,500` chars) or SQL helper views are co-trained with the `Solver` via a single shared-weight `Improver`+`Solver` adapter using case-balanced counterfactual gain over $\mathcal{H}_0$, dual-temperature memory replacement margin $\delta = 0.03$, and TF-IDF top-3 reference retrieval for unseen workflows—avoiding majority-agreement candidate selection on action-optional tasks ([`dual-role-model-harness-coevolution`](../skills/dual-role-model-harness-coevolution/SKILL.md), arXiv:2611.26806)
- [ ] Persistent secure-coding principle libraries (`B = (I, \mathcal{D})`) track pre-first-edit file reads to separate `unread` routing fixes (`I`) from `misapplied` / `too strict` content edits ($\mathcal{D}$), enforce explicit valid-input clauses (`v`) to prevent cross-CWE refusal overreach (`CWE-200 -> CWE-77` `-23.0 pp` `p@1`), and check target-language functional floors before cross-language reuse ([`failure-grounded-security-principle-evolution`](../skills/failure-grounded-security-principle-evolution/SKILL.md), arXiv:2611.33519)
- [ ] Every admitted or updated skill passed the acceptance gate (δ margin; strict security testbed)
- [ ] The system works correctly with zero skills (graceful degradation)

---

## Sources

- Break It Down, Pass It On: arXiv:2608.20274
- Optimal Skill Selection: arXiv:2608.19993
- WikiSkill: arXiv:2608.27454
- Self-Evolving Multimodal Agents Across Scenarios: arXiv:2611.14256
- FGSE (Falsification-Gated Self-Evolution): arXiv:2611.14326
- SceneAgent (Multi-Agent Framework for Portable Game Scene Generation): arXiv:2611.17821
- JevRSI (Cost-Effective RSI for Decision Model Harness): arXiv:2611.22432
- GUARD (Stabilizing Recursive Self-Improvement with Regret Guidance): arXiv:2611.23476
- MIMPA (Insider Shared-Memory Poisoning in Multi-Agent Systems): arXiv:2611.31307
- VISE (Verifier-Independent Skill Self-Evolution with Feedback from Tool Implementations): arXiv:2611.32480
- ZhuLong-SE (Self-Evolving Beyond Human-Crafted Experience for EDA Scripting): arXiv:2611.26912
- MedicalRSI (Clinical Model-Harness Co-Evolution): arXiv:2611.26806
- PRECEPT (Security Self-Improvement of Coding Agents via Evolving Principles): arXiv:2611.33519
