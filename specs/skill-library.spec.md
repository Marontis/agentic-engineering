# Skill Library Specification Template

> Fill in this template when designing a skill memory system for LLM agents.
> Each section surfaces research-backed decision points for skill authoring,
> storage, retrieval, and selection.

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
- [ ] The system works correctly with zero skills (graceful degradation)

---

## Sources

- Break It Down, Pass It On: arXiv:2608.20274
- Optimal Skill Selection: arXiv:2608.19993
- WikiSkill: arXiv:2608.27454
