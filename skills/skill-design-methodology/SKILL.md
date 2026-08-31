---
name: skill-design-methodology
description: >
  How to design agent skills that transfer reliably across tasks. Covers
  subtask-level decomposition, text-over-code format, the skill utility
  score (specificity × abstractness), and a pre-deployment audit workflow.
  Derived from "Break It Down, Pass It On" (arXiv:2608.20274) and validated
  against the Praxis ingestion pipeline's own skill library.
source: https://arxiv.org/pdf/2608.20274
---

# Skill Design Methodology

A meta-skill for designing agent skills that actually transfer. Use this
before writing any new skill, and periodically to audit an existing library.

## Why This Matters

Agent skills can **help or harm** the agent that retrieves them. A controlled
study across 11 models and 3 benchmarks (Feng et al., 2026) showed:

- **Task-level skills harm performance** (−1.2 to −4.1 pts vs. no-memory)
- **Subtask-level skills help** (+0.5 to +1.9 pts)
- **Text format > code format** at every level, benchmark, and difficulty

The difference isn't marginal — badly structured skills are worse than having
no skill memory at all. Getting this right is prerequisite to every other
skill in the library.

---

## The Two Rules

### Rule 1: Decompose to Subtask Level

A skill should capture **one reusable procedure**, not an entire workflow.

```
❌ BAD (task-level): "How to build a transactional coding sandbox"
   — Covers command classification, snapshot creation, rollback logic,
     sandbox-aware prompting, compensating transactions, and SLM selection
   — Too tied to its source context to transfer to anything else

✅ GOOD (subtask-level): Separate skills for each:
   — "Three-tier command classification" (safe/unsafe/uncertain)
   — "Snapshot-execute-commit/rollback loop"
   — "Sandbox-aware system prompts for policy violations"
   — "Compensating transactions for external APIs"
   — Each transfers independently to different agent architectures
```

**Why it works**: different tasks share subtasks. "Login → Check Cart →
Place Order" and "Login → Check Cart → Move to Wish List" share 3 of 4
subtasks. A subtask-level skill for "Login" transfers to both. A task-level
skill for "Place order for weightlifting benches" transfers to neither.

**The test**: if your skill's description could only match ONE kind of
project, it's too specific. If it could match everything, it's too vague.
The sweet spot is a procedure that appears across multiple different tasks.

### Rule 2: Write Skills as Text, Not Code

Express skills as natural-language workflow notes with environment-specific
caveats — not as Python functions or rigid code templates.

```
❌ BAD (code format):
   def create_snapshot(workspace: Path) -> Path:
       snapshot_dir = workspace.parent / f".snapshot_{workspace.name}"
       shutil.copytree(workspace, snapshot_dir, symlinks=True)
       return snapshot_dir

✅ GOOD (text format):
   Create a filesystem snapshot before executing uncertain commands.
   Use shutil.copytree for portability (~1.8s for 250MB workspace),
   or native CoW snapshots (ZFS/Btrfs) for near-zero overhead in
   production. Preserve symlinks. Store snapshots adjacent to the
   workspace with a timestamp suffix for disambiguation.
```

**Why it works**: text skills guide the agent's reasoning without
constraining its execution. Code skills lock in implementation details
from the source task — wrong parameters, namespace conflicts, wrong
libraries for the new context. Even syntactically valid code skills are
less transferable because they encode assumptions about the execution
environment.

**The exception**: include code when it illustrates a specific algorithm,
equation, or data structure that would be ambiguous in prose. But the
code should be illustrative, not executable — the agent should adapt it,
not copy-paste it.

---

## Skill Utility Score

Before deploying a skill, compute its **utility score** to predict whether
it will transfer. This requires only the skill description and the set
of task descriptions — no task execution needed.

### Formula

```
utility(s) = specificity(s) × abstractness(s)
```

### Specificity

How closely the skill matches real tasks:

```
specificity(s) = Pr[max_j sim(s, t_j) ≥ sim(t_i, t_k)]
```

The probability that the skill's nearest-task similarity exceeds the
similarity between two random tasks. A skill far from every task scores
near 0. A skill matching at least one task scores near 1.

**In practice**: embed the skill description and all task/project
descriptions with any sentence embedding model. Compute the skill's
max cosine similarity to any task. Compare against the distribution of
inter-task similarities. If the skill's best match is above median
inter-task similarity, specificity is high.

### Abstractness

How evenly the skill's relevance spreads across tasks:

```
abstractness(s) = exp(H(softmax(similarities / τ))) / N
```

where τ = 0.1 is a temperature and N is the number of tasks. A skill
relevant to only one task scores near 1/N (low). A skill relevant to
many tasks scores near 1 (high).

**In practice**: compute cosine similarities to all tasks, apply softmax
with temperature, then compute perplexity. Normalize by task count. If the
perplexity is high (relevance spread evenly), abstractness is high.

### Interpretation

| Utility Score | Diagnosis | Action |
|:-------------|:----------|:-------|
| High specificity, low abstractness | Matches one task perfectly, useless for others | Generalize — strip task-specific details, find the transferable procedure underneath |
| Low specificity, high abstractness | Generic but too vague to help any task | Specialize — add concrete procedures, environment caveats, decision criteria |
| Low both | Irrelevant to everything | Rewrite or discard |
| **High both** | **Matches real tasks AND generalizes broadly** | **Ship it** |

### Quick Audit Script

```python
import numpy as np
from sentence_transformers import SentenceTransformer

def audit_skill_library(skill_descriptions: list[str],
                        task_descriptions: list[str],
                        model_name: str = "all-MiniLM-L6-v2",
                        tau: float = 0.1) -> list[dict]:
    """Score every skill in a library against a task corpus.

    Args:
        skill_descriptions: one string per skill (the description/summary)
        task_descriptions: representative tasks/projects the skills should help
        model_name: sentence embedding model
        tau: temperature for abstractness calculation

    Returns:
        list of {skill, specificity, abstractness, utility} dicts, sorted
    """
    model = SentenceTransformer(model_name)
    skill_embs = model.encode(skill_descriptions, normalize_embeddings=True)
    task_embs = model.encode(task_descriptions, normalize_embeddings=True)
    N = len(task_descriptions)

    # Inter-task similarity baseline
    inter_sims = []
    for i in range(N):
        for k in range(i + 1, N):
            inter_sims.append(task_embs[i] @ task_embs[k])
    inter_sims = np.array(inter_sims)

    results = []
    for idx, s_emb in enumerate(skill_embs):
        # Similarities to all tasks
        c = np.array([s_emb @ t for t in task_embs])

        # Specificity
        max_sim = c.max()
        specificity = np.mean(max_sim >= inter_sims)

        # Abstractness
        p = np.exp(c / tau)
        p = p / p.sum()
        entropy = -np.sum(p * np.log(p + 1e-10))
        abstractness = np.exp(entropy) / N

        utility = specificity * abstractness

        results.append({
            "skill": skill_descriptions[idx][:80],
            "specificity": round(specificity, 3),
            "abstractness": round(abstractness, 3),
            "utility": round(utility, 3),
        })

    return sorted(results, key=lambda x: x["utility"], reverse=True)
```

---

## Skill Authoring Checklist

Use this checklist every time you write a new skill:

### Structure

- [ ] **Single procedure**: does this skill describe ONE reusable procedure,
      not an entire pipeline?
- [ ] **Subtask-level**: could this procedure appear as a step within
      multiple different projects?
- [ ] **No monolithic scope**: if someone needed only one section of this
      skill, could they extract it without reading the rest?

### Format

- [ ] **Natural language body**: is the main content written as a workflow
      note with procedures and caveats, not as executable code?
- [ ] **Illustrative code only**: is code used to clarify algorithms or data
      structures, not as copy-paste templates?
- [ ] **Environment caveats**: does the skill note where the procedure
      differs across environments (OS, framework, scale)?

### Transferability

- [ ] **Specificity check**: does the skill description match at least one
      real project or task in the library?
- [ ] **Abstractness check**: could this skill plausibly help 3+ different
      types of projects?
- [ ] **Neither extreme**: is the skill neither hyper-specific to one context
      nor so generic it's meaningless?

### Content

- [ ] **Decision criteria, not just steps**: does the skill explain *when*
      and *why* to use the procedure, not just *how*?
- [ ] **Failure modes**: does the skill note what goes wrong when the
      procedure is applied incorrectly?
- [ ] **Cross-references**: does the skill link to related skills for
      adjacent procedures?

---

## Applying to the Praxis Pipeline

This skill is directly applicable to the Praxis paper → skill pipeline:

### During Ingestion

When reading a paper and identifying potential skills:

1. **Don't create one skill per paper**. A paper is a task-level artifact.
   Extract the individual mechanisms, algorithms, and design patterns —
   those are the subtask-level skills.

2. **Look for shared subtasks across papers**. If two papers both address
   "command classification" or "snapshot rollback", those shared procedures
   are the highest-utility skills.

3. **Name skills by procedure, not by paper**. `three-tier-command-
   classification` transfers better than `fault-tolerant-sandboxing-paper-
   skills`. The first is a procedure; the second is a citation.

### During Authoring

1. **Write the description first**. The description is what retrieval
   matches against. If it's too specific ("ceLLMate's HTTP interception
   for Chrome extensions") or too generic ("agent security"), the skill
   won't be retrieved at the right time.

2. **Lead with the decision**, not the mechanism. "When to intercept at
   the HTTP layer instead of the UI layer" is more useful than "How to
   use Chrome webRequest API".

3. **Include the 'when to use' section early**. This is what the agent
   scans first. Put it before the implementation details.

### During Audit

Run the utility score against your project/task corpus periodically:

```bash
# Example: audit the current skill library against a set of project descriptions
python audit_skills.py \
  --skills workspace/skills/*/SKILL.md \
  --tasks workspace/research/captures/*/cap-*.summary.md \
  --output workspace/exports/skill_audit.json
```

Flag skills with utility < 0.15 for revision. Skills with high specificity
but low abstractness need generalizing. Skills with high abstractness but
low specificity need sharpening.

---

## Evidence Summary

| Finding | Source | Scale |
|:--------|:------|:------|
| Task-level skills harm (−1.2 to −4.1 pts) | Feng et al. 2026, Tab. 2 | 11 models × 3 benchmarks |
| Subtask-level skills help (+0.5 to +1.9 pts) | Feng et al. 2026, Tab. 2 | 11 models × 3 benchmarks |
| Text > code at both levels | Feng et al. 2026, Tab. 2, Fig. 3–4 | All difficulty strata |
| Utility predicts success monotonically | Feng et al. 2026, Fig. 5a | 14% → 31% across bins |
| Transfer density higher for subtask skills | Feng et al. 2026, Fig. 6 | 3 benchmarks |
| Findings hold across prompt ablations | Feng et al. 2026, Fig. 26 | L1/L2/L3 prompts |

## References

- **Paper**: [Break It Down, Pass It On: Cross-Task Skill Transfer in LLM Agents](https://arxiv.org/abs/2608.20274) — Feng, Bijoy, Balasubramanian, Zhou (Stony Brook University)
- **Code**: https://github.com/Zesearch/skill-transfer-llm-agents
- **Praxis source**: `src:arxiv-2608-20274`
