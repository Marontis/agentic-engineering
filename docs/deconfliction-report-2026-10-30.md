# Knowledge-Base Deconfliction Report — 2026-10-30

Scope: `rules/` (8 files), `skills/` (107 skills across 4 categories),
`specs/` (8 templates), `research-briefs/` (177 briefs), and
`kody-templates/` after the 2026-10-30 batch ingestion of 48 arXiv papers
(`2610.28810`–`2610.37407`).

---

## Summary

| Category | Found | Fixed in this pass |
|:---|---:|---:|
| Rule entries added (`### DO:` / `### DON'T:`) | 10 | 10 scoped, sourced, and cross-checked |
| Existing rule entries extended with new scope & evidence | 12 | 12 updated with verified scope and `> Source:` |
| `kb_lint.py --base origin/master` opposite-polarity pairs reviewed | 8 | 8 inspected in full and recorded in `scripts/kb_lint_reviewed.txt` |
| Semantic tensions across rule files / skills / specs | 4 | 4 disambiguated in rule text and scope lines |
| Unbacked `arXiv:` citations in touched rules | 0 | All 48 new papers backed by a brief (42) or skill (6) |
| Broken markdown links / missing `**Scope:**` / missing `> Source:` | 0 | Verified by `python scripts/kb_lint.py --base origin/master` (0 errors, 0 warnings) |

---

## 1. Cross-Rule & Cross-Tier Semantic Deconflictions

### 1.1 Step-Level Verification vs. Tool-Exposed Verification (`recursive-improvement.md` & `selective-step-verification`)

- **Apparent tension**: `recursive-improvement.md` ("DO: Invest in standalone verifiers before planning components") recommends adding verification, while `SWE-VERIFIER` (`arXiv:2610.30284`) and `PAWM` (`arXiv:2610.29139`) show that always-on step verification nearly doubles token cost ($1.90\times$) and an always-on trajectory world model degrades WebArena-Lite below vanilla ($72.7\% \to 71.1\%$), while exposing the verifier as an agent-callable tool (`verifier-as-tool`) drops SWE-bench Verified resolution from $75.5\%$ to $69.2\%\text{--}70.2\%$.
- **Resolution**: Scoped the new rule (`### DO: Gate step-level action verification on low-confidence steps and keep the verifier transparent to the policy`) to distinguish **terminal/episode-end verification** from **per-step trajectory verification**. Step-level verifiers and world-model pitfall predictors must be invoked transparently by the harness only on low-confidence steps ($s(a_1) < \tau$, $<4\%$ of steps) or subgoal (`<pass>`) boundaries, never exposed as an optional tool for the policy to call on itself.

### 1.2 Stronger-Model Skill Evolution vs. Cross-Capability Deployment (`skill-system-design.md` & `capability-matched-skill-adaptation`)

- **Apparent tension**: `skill-system-design.md` ("DO: Evolve skills with stronger models, deploy to weaker ones", `arXiv:2608.27454`) recommends evolving skills with a frontier teacher and transferring them to weaker student executors. However, `arXiv:2610.33024` demonstrates that directly transferring complex workflow skills evolved for a strong model (`TerminalBench` 4-step debugging workflow) into a weaker model (`Qwen3-8B`) causes instruction-following overload and degrades solve rate below the no-skill baseline ($25.2\% \to 21.8\%$).
- **Resolution**: Updated `"DO: Evolve skills with stronger models, deploy to weaker ones"` with explicit scope and evidence from `arXiv:2610.33024`, linking to [`capability-matched-skill-adaptation`](../skills/capability-matched-skill-adaptation/SKILL.md). The rule now specifies running a post-hoc capability-matched adaptation pass (compressing multi-branch procedural workflows into direct guardrails when student failure traces show instruction drift) before freezing transferred skills for weaker models, which recovers $+8.2\text{ pp}$ over unadapted transfer ($21.8\% \to 30.0\%$).

### 1.3 MCP vs. CLI Tool Interfaces (`skill-system-design.md`, `agent-sandbox-safety.md`, & `decoupled-interface-action-repair`)

- **Apparent tension**: `arXiv:2610.30157` finds CLI tool integrations execute $4.2\times$ faster and consume $26.3\%$ fewer tokens than MCP on happy-path tasks, whereas `arXiv:2610.34298` (`DART` & `MICA`) and `arXiv:2610.35541` (`Vela`) show that raw shell/endpoint interfaces induce distinct interface-realization errors (`39%–47%` cross-interface behavioral divergence under identical capability sets) and retain $91\%\text{--}95\%$ of backend web vulnerabilities compared to $39\%$ under query-oriented typed slot schemas.
- **Resolution**: Added `"DO: Decouple semantic action commitment from interface-specific tool realization and repair realization locally"` in `skill-system-design.md` (`arXiv:2610.34298`, `arXiv:2610.30157`), documenting the exact trade-off: use CLI or compact execution for low-risk, latency-sensitive local operations, use typed MCP slot schemas for security-critical or schema-complex boundaries (`arXiv:2610.35541`), and separate semantic action commitment from interface formatting (`MICA`) so syntax/flag repair loops never re-invoke high-level planning.

### 1.4 Latent Activation Probes vs. Text Refusal and Contextual Code Probing (`agent-sandbox-safety.md`)

- **Apparent tension**: Earlier entries in `agent-evaluation-quality.md` (`arXiv:2608.28930`, `arXiv:2608.27661`) recommend linear probes on hidden states for hallucination and RAG evidence triage, and `Reva` (`arXiv:2610.35829`) shows an 8-head attention probe over 4 intermediate layers beats the LLM's own text verdicts by $7.4\text{--}8.7\text{ pp}$ on PrimeVul C/C++ vulnerability detection. By contrast, `arXiv:2610.30727` evaluates 38 activation-based harm monitors across 15 LLMs on 2,248 OOD jailbreaks and finds instruction-end probes (`23.0%` TPR at $\hat{f}=0.045$) trail simple `TF-IDF` (`23.9%`) in all 15 models, while pre-generation probes (`43.9%`) mostly track the model's existing refusal plan ($\Pi = +0.42$).
- **Resolution**: Integrated both `arXiv:2610.30727` and `arXiv:2610.35829` into `"DO: Calibrate safety-detector thresholds on realistic benign traffic, per target model"` (`agent-sandbox-safety.md`), explicitly contrasting OOD prompt-harm detection at the instruction boundary (where linear activation probes fail to beat lexical baselines or model refusal) against localized token-level representation probing over context-enriched code (`Reva`), where intermediate representations carry signal lost during text decoding.

---

## 2. `kb_lint.py` Opposite-Polarity Pair Audit

All 8 opposite-polarity (`DO` vs `DON'T`) heading pairs sharing $\ge 2$ stemmed subject words between the 2026-10-30 diff and the existing corpus were read in full and adjudicated:

| New / Touched Heading | Existing Heading | Shared Stems | Verdict & Rationale |
|:---|:---|:---|:---|
| `DO: Separate target-session self-criticism from external attack proposal in automated red teaming` (`agent-evaluation-quality.md`) | `DON'T: Report red-team failure rates scored by a single judge model` (`agent-evaluation-quality.md`) | `red`, `team` | **Complementary**: role-separated red-team attack generation (`2610.34965`) vs cross-family judge panels for scoring red-team failure rates (`2609.27336`). |
| `DON'T: Trust MCP tool metadata without trace-aware vetting` (`agent-sandbox-safety.md`) | `DO: Enforce fast-fail circuit breakers, output schema validation, and grounded-fulfillment gates for MCP tool faults` (`skill-system-design.md`) | `mcp`, `tool` | **Complementary**: registration-time metadata vetting (`2609.26761`, `2610.36108`) vs runtime fault and output validation (`2610.32555`). |
| `DO: Isolate human-in-the-loop approval gates onto an out-of-band, hardware-attested trusted device with a trusted display` (`agent-sandbox-safety.md`) | `DON'T: Trust style-based safety judges as the sole safety gate` (`agent-sandbox-safety.md`) | `gate`, `trust` | **Complementary**: both reject weak, bypassable in-band safety gates in favor of independent enforcement (`2610.35835`, `2609.08236`). |
| `DO: Decouple shared team coordination prompts from local executor prompts and optimize the coordinator first` (`multi-agent-coordination.md`) | `DON'T: Allow self-modifying agents to optimize prompts or scaffolding solely against performance benchmarks` (`recursive-improvement.md`) | `optimize`, `prompt` | **Complementary**: two-phase coordinator-then-executor prompt optimization structure (`2610.34722`) vs gating prompt optimization with negative security testbeds (`2609.17817`). |
| `DON'T: Expose running selection tallies or popularity-sorted lists during sequential multi-agent evaluation` (`multi-agent-coordination.md`) | `DO: Couple discrete reasoning-mode selection with policy-relative difficulty tiers during self-evolving RL` (`recursive-improvement.md`) | `during`, `selection` | **Unrelated**: Polya-urn herding in sequential multi-agent item choice (`2610.30769`) vs reasoning-effort mode selection in single-agent RL (`2610.33684`). |
| `DON'T: Expose running selection tallies or popularity-sorted lists during sequential multi-agent evaluation` (`multi-agent-coordination.md`) | `DO: Speculate multi-step action skeletons in isolated sandboxes to reduce sequential turn latency` (`skill-system-design.md`) | `multi`, `sequential` | **Unrelated**: sequential multi-agent herding (`2610.30769`) vs speculative execution of multi-step tool macros (`2609.03236`). |
| `DO: Gate step-level action verification on low-confidence steps and keep the verifier transparent to the policy` (`recursive-improvement.md`) | `DON'T: Rely on prompt-level privacy instructions to keep carried information inside its boundary` (`agent-sandbox-safety.md`) | `keep`, `level` | **Unrelated**: confidence-gated step verification for task accuracy (`2610.30284`) vs action-boundary privacy enforcement (`2609.32915`). |
| `DO: Couple discrete reasoning-mode selection with policy-relative difficulty tiers during self-evolving RL` (`recursive-improvement.md`) | `DON'T: Deploy the chain-of-thought monitor you optimized the policy against, or score raw reasoning` (`agent-sandbox-safety.md`) | `policy`, `reason` | **Unrelated**: difficulty-tiered reasoning-mode RL (`2610.33684`) vs CoT safety-monitor evasion under RL (`2609.31121`). |

---

## 3. Verification Status

```text
$ cd output && python scripts/kb_lint.py --base origin/master
kb_lint: 0 error(s), 0 warning(s)
```

