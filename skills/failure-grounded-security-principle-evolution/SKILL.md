---
name: failure-grounded-security-principle-evolution
description: >-
  Prevent cross-session vulnerability recurrence in coding agents by seeding a
  structured secure-coding principle library from authoritative standards
  (including explicit valid-input allowances), attributing security and
  functional test failures across four root causes, drafting literal-scrubbed
  class-level edits, and gating revisions on fresh paired rollouts plus an
  unmodified-agent functional floor. Derived from PRECEPT (arXiv:2611.33519).
source: "arXiv:2611.33519"
repository: "https://github.com/Marontis/agentic-engineering"
license: CC-BY-4.0
---

<!-- Licensed under CC BY 4.0 | Source: Marontis/agentic-engineering | Origin: arXiv:2611.33519 -->

# Failure-Grounded Security Principle Evolution

## When to Use

Use this procedure when hardening **coding agents** (`Codex`, `Claude Code`, `Qwen Code`, or IDE/CLI agents reading workspace `AGENTS.md` / `CLAUDE.md` guidance trees) that repeatedly reintroduce CWE classes across fresh sessions despite knowing how to patch those exact vulnerabilities when pointed out, provided **executable functional and security test suites** exist on a bounded-scope training task pool. Representative project types include:

- **Function-, endpoint-, and module-scoped secure code generation**: Hardening persistent `AGENTS.md` / `.agents/` security libraries for backend handlers, auth/crypto utilities, parsers, and CLI tools where raw OWASP checklists are ignored or misapplied into over-strict input rejections.
- **Cross-agent and cross-model secure-coding packs**: Evolving a reusable, provenance-linked principle tree once on a capable open-weight or frontier coding stack and deploying it zero-shot across sibling coding scaffolds or stronger target models within the trained language ecosystem.
- **CI security-regression hardening loops**: Operationalizing organization-mandated standards (`OWASP ASVS`, `OWASP Cheat Sheets`, `OpenSSF`, `SEI CERT`) against observed agent CWE recurrences without fine-tuning model weights.

**When NOT to use**:
- **Large multi-file repository tasks governed by project-specific invariants (`SusVibes` regime)**: Across `184` real-repository tasks (`101` projects, median `108` tool calls vs. `9` on `SeCodePLT`, where the library occupies `0.11%` vs. `5.6%` of input tokens), evolving general secure-coding principles yielded **zero significant gain** (`6.9%` vs. `6.9%` `sp@1`, `13.0%–13.3%` vs. `13.5%` `S_{|P}` in `arXiv:2611.33519`) because ~`50%` of bugs violate project-local invariants, `98%` of diagnoses hit single tasks, and agents skip opening (`10/30`) or re-reading (`16/20`) principle files mid-run. Pair with [`security-aware-context-slicing`](../security-aware-context-slicing/SKILL.md) and post-completion static/dynamic CWE diff gates (`../../rules/agent-sandbox-safety.md`).
- **Untrained programming languages without language-specific functional calibration**: Transferring Python-evolved principles directly to untrained C, C++, and JavaScript tasks degraded functional `p@1` (`81.7% -> 70.0%`, `80.0% -> 70.0%`, `86.7% -> 60.0%` on `CWEval` in `arXiv:2611.33519`); always run language-matched evolution or functional-floor gating before cross-language deployment.
- **Verifier-free tool skills lacking executable security/functional tests**: When revising tool-script `SKILL.md` files without task verifiers, use AST-indexed script contract alignment ([`tool-implementation-grounded-skill-revision`](../tool-implementation-grounded-skill-revision/SKILL.md)) or Turn-0 checklist gating ([`regret-guided-continual-harness-evolution`](../regret-guided-continual-harness-evolution/SKILL.md)).

---

## Core Insight

Coding agents exhibit a stark **single-session repair vs. cross-session recurrence gap** (`arXiv:2611.33519`): across `14` multi-task chains (`12` CWEs, `Codex` / `Claude Code` / `Qwen Code` on `Qwen3.6-35B-A3B`), agents fixed **`85.7%`** of vulnerabilities within the session where a security test failed, yet reintroduced the exact same CWE in **`26.7%`** of new sessions vs. **`27.5%`** baseline incidence (`+0.8` pp retention gain in `Table I`; reported as `+0.7` pp on `36` held-out pairs in `Table VI(a)` due to unrounded chain-mean subtraction). Enabling built-in cross-session memory produced **`0/36`** spontaneous security notes; explicitly prompting agents to write notes (`28/36` written) anchored **`13/28`** notes to task-specific function/field literals that failed to transfer across task families (`+1.7` to `+4.4` pp, non-significant); and supplying published `OWASP Secure Coding Practices` (`218` rules covering `19/27 = 70%` of tasks at $\kappa = 0.83$ [`63%` under `gpt-6.1-sol`]) barely moved recurrence (`24.2%` all `218`, `23.3%` oracle-relevant subset vs. **`16.7%`** for operationalized class-specific principles). Meanwhile, generic self-improvement baselines (`ACE`, `SkillOpt`, `RuleEvolve`) either over-tightened input checks—dropping functional `p@1` by up to **`-4.2` to `-4.7` pp**—or left conditional security `S_{|P}` at `78.8%–87.7%`.

**PRECEPT** closes this gap by treating a persistent workspace security library $B = (I, \mathcal{D})$ (`AGENTS.md` / `CLAUDE.md` routing index $I$ + topic documents $\mathcal{D}$) as an operationalized refinement of authoritative standards where every principle explicitly pairs **required security checks (`k`)** with **allowed valid inputs (`v`)**, revised one cause-matched primitive at a time and gated on **fresh paired rollouts** plus a **non-inferiority functional floor against the unmodified agent $B_\varnothing$**. On unseen `SeCodePLT` task families (`129` test tasks), `PRECEPT` lifts secure working code `sp@1` by **`+8.9` to `+11.6` pp** (`41.7% -> 50.6%` `Codex`, `36.9% -> 48.5%` `Claude Code`, `36.9% -> 47.8%` `Qwen Code`), raises conditional security among functionally passing solutions **`S_{|P}` from `79.7%–81.9%` to `97.1%–98.5%`** without dropping `p@1` (`+0.1` to `+3.9` pp), cuts held-out cross-session recurrence from `26.7%` to **`11.5%`** (preventing `20/42 = 48%` of initial chain vulnerabilities), and transfers zero-shot to unseen CWEs on `CWEval Python` (`70.2% -> 88.6%` `S_{|P}`, `84.0% -> 87.9%` `p@1`) and stronger models (`Mistral Medium 3.5` `81.9% -> 97.3%` `S_{|P}`).

---

## Step-by-Step Procedure

### Step 1: Seed a Structured Principle Library (`B_0`) from Authoritative Standards

Do **not** initialize the library from ungrounded LLM-generated security prose (in `arXiv:2611.33519`, a model-written seed library scored *below* no guidance by over-rejecting valid inputs). Distill initial library $B_0 = (I, \mathcal{D})$ from authoritative sources (`OWASP ASVS 5.0.0`, `OWASP Secure Coding Practices`, `OWASP Cheat Sheets`, `OpenSSF`, language standard-library security docs, `Bandit` / `gosec` / `SEI CERT`), representing each principle as a typed 7-tuple $\pi = (\mathit{id}, s, a, k, v, x, \rho)$:

```yaml
id: PY-DESER-02
statement: "Never deserialize untrusted byte streams with pickle/marshal; parse structured schemas."
scope_a: "Code accepting external/file/network serialized payloads in Python"
required_check_k: "Use json.loads or safe schema-validated parsers with explicit type/size bounds"
allowed_valid_behavior_v: "Must still accept nested valid JSON objects, Unicode strings, and empty collections"
supporting_notes_x: "Avoid custom eval-based fallback decoders"
provenance_rho: "OWASP ASVS 5.0.0 V5 / Bandit B301"
```

Satisfying $\pi$ on code state $\sigma$ requires $a(\sigma) \Rightarrow (k(\sigma) \wedge v(\sigma))$: the `allowed_valid_behavior_v` clause is mandatory to prevent agents from achieving "security" via blanket input refusal. Keep `AGENTS.md` / `CLAUDE.md` ($I$) as a compact routing index linking code situations $a$ to focused topic files in $\mathcal{D}$.

### Step 2: Collect Test-Blind Condensed Execution Records (`Test`)

Execute the coding agent with current library $B$ on training tasks $T_{\mathrm{tr}}$ inside isolated sandboxes. Condense each trajectory into a compact execution record $e = (R, W, \mathrm{diff}, f_x, s_x, Q)$:

1. **`R` (Read trace with edit-boundary timing)**: Record which library files in $(I, \mathcal{D})$ the agent opened **before** its first code edit vs. **after** its first edit (or never).
2. **`W` and `diff`**: Files modified and the final code diff.
3. **`f_x` and `s_x` (Pass/fail + sanitized failure signals)**: Functional and security test outcomes/tracebacks—**strictly withholding benchmark test source code and hidden oracle predicates** from both the agent and the analyzer (`../../rules/recursive-improvement.md`, `"DON'T: Expose benchmark verifier code or unstated rubric predicates to the skill-library learner"`).
4. **`Q`**: Token and tool-call usage (used to detect navigation bloat).

### Step 3: Attribute Failures Across Four Causes and Restrict Mutation Primitives (`Analyze`)

Group failing execution records into recurring findings $\varphi$ across task families, rank by training coverage $|T_\varphi| / |T_{\mathrm{tr}}|$, and classify each finding into exactly one of four root causes $\gamma \in \mathcal{C}$—restricting the drafter to the **single matching primitive family $\mathcal{O}_\gamma$** (`1` primitive kind per evolution step):

| Root Cause (`\gamma`) | Observable Signature in `e = (R, diff, f_x, s_x)` | Allowed Primitives (`\mathcal{O}_\gamma`) | Prohibited Fix |
|:---|:---|:---|:---|
| **`missing`** | Security test fails (`s_x = 0`); no principle in $B$ covers code situation $\sigma$. | **Content**: `add` new principle or `edit(a)` scope (grounded in authoritative source $\rho$). | Inventing ungrounded ad-hoc rules without $\rho$. |
| **`unread`** | Relevant principle $\pi \in \mathcal{D}$ exists, but $\pi \notin R_{\text{pre-edit}}$ (`s_x = 0`). | **Organization**: `entry` (routing cue in $I$), `move`, `hub`, or `create`/`rename` (`11/47` kept main-run edits in `PRECEPT`; one cut `Claude Code` input tokens `14%`). | Rewriting $\pi$'s text when the agent never opened $\pi$ before editing! |
| **`misapplied`** | Agent opened $\pi$ before editing ($\pi \in R_{\text{pre-edit}}$), yet `s_x = 0`. | **Content**: `edit(k)` (concrete API/check step), `edit(a)`, `split`/`join`, or `procedure`. | Adding duplicate principles elsewhere in $\mathcal{D}$. |
| **`too strict`** | Agent opened $\pi$ and passed security (`s_x = 1`), **but broke valid inputs (`f_x = 0`)**—including cross-CWE overreach (e.g., a `CWE-200` `str.format` rule rejecting valid `{{name}}` templates in `CWE-77`). | **Content**: `edit(v)` (explicit valid-input allowance) or narrow `edit(a)` scope. | Deleting $\pi$'s security check $k$ or weakening $\rho$. |

*(Optional diagnostic probe)*: When root cause is ambiguous between `unread` and `misapplied`, run a bounded guidance-ladder check (`<= 100` executions) injecting $\pi$ directly into prompt context to verify whether reading $\pi$ resolves `s_x = 0` before editing content.

### Step 4: Draft Class-Scoped Revisions with Automated Literal & Anti-Weakening Filters (`Draft`)

Scope each candidate revision $\delta$ to at most **`24` target training tasks** ($T_\delta$) sharing the diagnosed code situation, and enforce two automated pre-evaluation filters (`<= 2` rewrite retries before dropping $\delta$):

1. **Task-literal scrubbing**: Reject any draft referencing task-specific function names, variable identifiers, endpoint routes, file paths, or test constants from $T_\delta$ (`147/338 = 43.5%` [`43%–44%` across prose] of drafts in `arXiv:2611.33519` tripped this check; `9` were dropped after `2` rewrites).
2. **Authoritative anti-weakening check**: Reject any edit that narrows an authoritative prohibition in $\rho$ to a single observed instance (e.g., forbidding only `MD5` when $\rho$ forbids `MD2`, `MD4`, `MD5`, and `SHA-1`).
3. **Poisoned-feedback defense (when tasks/traces are untrusted)**: If $T_{\mathrm{tr}}$ includes externally contributed tasks or reference outputs, apply literal-abstraction and per-clause leave-one-edit-out (`LOEO`) marginal checks ([`feedback-poisoning-skill-promotion-guard`](../feedback-poisoning-skill-promotion-guard/SKILL.md)).

### Step 5: Gate on Fresh Paired Rollouts, UCB Evidence Ledger, and the Unmodified Functional Floor (`Decide` & `Select`)

Never score a candidate $\delta$ by comparing against the same cached runs that selected $T_\delta$—selection-bias regression-to-the-mean inflated false acceptance from **`12%` to `68%`** at nominal `10%` in `arXiv:2611.33519`.

1. **Fresh paired target executions (`n = 4` runs/task)**: Execute both anchor library $B$ and candidate $B \oplus \delta$ for **`4` fresh runs per task** on $T_\delta$ (and on a stratified non-target sample for global $\widehat{\Delta}_{\mathrm{all}}$), applying a standard-error floor $\mathrm{se} = \max(\hat{\sigma}_d, 0.42/\sqrt{n}) / \sqrt{|T|}$ so zero-variance small samples cannot fake infinite confidence.
2. **Inverse-variance pooling in revision ledger (`\mathcal{H}`)**: Persist inconclusive candidates in ledger $\mathcal{H}$, pool multi-round paired differences by inverse variance (`29/96` kept revisions across runs needed `> 1` round), re-propose promising uncertain candidates via UCB $(|T_\delta|/|T_{\mathrm{tr}}|)(\bar{\Delta}_\delta + \mathrm{se}_\delta)$, and permanently retire any candidate with $\bar{\Delta}_\delta + 1.645\,\mathrm{se}_\delta < 0$ or `3` rounds without clear positive `sp@1` gain.
3. **Cumulative functional non-inferiority floor against unmodified `$B_\varnothing$`**: To prevent `10+` tiny `-0.4 pp` functional losses from compounding across steps, require candidate functional pass rate $\widehat{p@1}(B \oplus \delta)$ relative to the **original unmodified agent $B_\varnothing$** ($\widehat{m} = \widehat{p@1}(B \oplus \delta) - \widehat{p@1}(B_\varnothing)$) to clear:
   $$\widehat{m} + 1.645\,\mathrm{se}(\widehat{m}) \ge -\epsilon_F \qquad (\epsilon_F = 0.03 \text{ [3 pp]})$$
4. **Stopping, disjoint-family validation `Select`, and Single Acceptance Gate**: Stop after `10` consecutive rejections, `3` candidate-less steps, or `100` steps. On a **task-family-disjoint** validation split $T_{\mathrm{va}}$, replace the final kept library with an earlier checkpoint (`Select`, e.g., `Codex` step `52` beat last-kept step `58` by `+3.7` pts across a `71`-step run) **only if** its 95% bootstrap CI difference exceeds `0`. Before promoting the selected library into production, pass it through `"DO: Pass every self-modification through one acceptance gate"` in [`../../rules/recursive-improvement.md`](../../rules/recursive-improvement.md) (no regression beyond baseline noise margin $\delta$ on previously-correct and held-out tasks, and strict zero tolerance on the immutable negative security testbed).

---

## Environment Caveats

- **Offline evolution compute budget**: Full `56–71`-step `PRECEPT` runs executed `35,600–46,400` sandbox rollouts (`0.31–0.39M` input tokens/exec) and raised deployment input tokens from `0.11–0.16M` to `0.25–0.30M` (`arXiv:2611.33519`, `§V-A`). Under tight budgets, a `17–20`-step cap still captured most gains (`Qwen Code` `20`-step ablation reached `45.7%` `sp@1` / `96.4%` `S_{|P}` with `7` kept edits vs. `47.8%` / `97.8%` full; `17`-step library lifted `Mistral Medium 3.5` `S_{|P}` `81.9% -> 97.3%`).
- **Direction of cross-model transfer**: A library evolved on `Qwen3.6-35B-A3B` (`17` steps) transferred strongly to `Mistral Medium 3.5` (`97.3%` `S_{|P}`, exceeding `Mistral`-evolved `91.2%`), whereas transferring `Mistral`'s library back to `Qwen3.6` reached `86.5%` (`Table IX`) because `Mistral` left fewer initial failures to drive principle refinement—evolve on the model tier whose failure surface exposes the target CWE gaps, then verify on each deployment receiver.
- **Manuscript rounding/checkpoint notes (`arXiv:2611.33519`)**: In `Table I`, `BIR (27.5%) - RR (26.7%)` is reported as `RG = +0.8`, whereas `Table VI(a)` (`36` pairs, `BIR 27.5%`, `RR 26.7%`) reports `RG = +0.7` (and `Table VI(b)` `32.4% - 24.5%` reports `+7.8*`) due to unrounded chain-mean arithmetic; in `§V-A`, `Codex`'s run halted at step `71` (`10` consecutive rejections after last-kept step `58`), and validation `Select` chose step `52`.

---

## Failure Modes

- **Cross-CWE template/syntax overreach (`CWE-200 -> CWE-77`)**: A principle restricting Python `str.format` placeholders for `CWE-200` inadvertently matched `{{name}}` HTML template placeholders on `CWE-77` tasks, dropping `Codex` `CWE-77` functional `p@1` from **`69.0%` to `46.0%`** (`72%` functional failure when opened vs. `33%` when unopened). Always test `edit(a)` / `edit(v)` across disjoint task families before promotion.
- **Reusing target-selection rollouts for acceptance (`68%` false acceptance)**: Comparing $B \oplus \delta$ on fresh runs against $B$'s cached failure-selecting runs accepts noisy regression-to-the-mean (`68%` vs. `12%` FA); dropping the acceptance gate (`w/o acceptance criterion`, `Table VIII`) inflated kept edits `7 -> 19` while dropping `S_{|P}` **`96.4% -> 90.0%`**.
- **Dropping execution read-traces (`w/o execution records`) or the UCB ledger (`w/o ledger`)**: Without knowing whether $\pi$ was opened before the first edit, `S_{|P}` fell **`96.4% -> 85.3%`** (`39.7%` `sp@1`, below `Seed` `40.7%`); without pooling multi-round evidence in $\mathcal{H}$, `sp@1` stalled at `Seed` (`40.7%`, `88.8%` `S_{|P}`).
- **Expecting file-tree principles alone to secure `100+`-step repository edits**: On `SusVibes`, agents stop consulting `AGENTS.md`-linked docs once immersed in deep repository exploration (`0.11%` context share)—enforce deterministic pre-action and post-diff CWE gates at repository scale.

---

## Cross-References

- **Rules**:
  - [`../../rules/recursive-improvement.md`](../../rules/recursive-improvement.md) — `"DO: Pass every self-modification through one acceptance gate"`, `"DO: Evaluate evolved instructions against immutable, held-out negative security testbeds"`, and `"DON'T: Promote bundled text-space skill edits on aggregate clean validation accuracy alone"`
  - [`../../rules/agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — `"DO: Enforce post-completion static and dynamic CWE analysis on coding-agent diffs rather than relying on pre-completion scans or prompt reminders"`
  - [`../../rules/skill-system-design.md`](../../rules/skill-system-design.md) — `"DO: Ground unverified skill revisions in AST-indexed script contracts aligned with trace gaps while freezing bundled code"`
- **Spec Templates**: [`../../specs/self-improving-agent.spec.md`](../../specs/self-improving-agent.spec.md) and [`../../specs/skill-library.spec.md`](../../specs/skill-library.spec.md)
- **Related Skills & Briefs**:
  - [`security-aware-context-slicing`](../security-aware-context-slicing/SKILL.md) — Repository-level security context slicing (`A.S.E 2.0` / `CASE-Bench`) for multi-file codebases where `PRECEPT` saturates
  - [`feedback-poisoning-skill-promotion-guard`](../feedback-poisoning-skill-promotion-guard/SKILL.md) — `LOEO` marginal validation and literal-abstraction guards when task references are untrusted (`SkillOpt`)
  - [`regret-guided-continual-harness-evolution`](../regret-guided-continual-harness-evolution/SKILL.md) — Reference-free `Turn-0` checklist + `Soft-HURT` `[iff]` gating (`GUARD`)
  - [`tool-implementation-grounded-skill-revision`](../tool-implementation-grounded-skill-revision/SKILL.md) — Verifier-free `SKILL.md` revision from local script ASTs (`VISE`)
  - [`audited-guardrail-tool-evolution`](../audited-guardrail-tool-evolution/SKILL.md) — 10-CWE `AuditorAgent` screening for executable guardrail tools (`EVOLVE`)
  - [`skill-evolution-defense`](../skill-evolution-defense/SKILL.md) — Provenance and prompt-injection checks before admitting evolved skills
  - [`detection-gap-self-improving-programmatic-agents`](../../research-briefs/detection-gap-self-improving-programmatic-agents.md) — Why agents that fix `89.6%–100%` of alerted bugs fail to self-trigger without external monitors (`arXiv:2611.29807`)

---

## Sources

- Guo, K., Patir, R., Cai, H., & Hu, H. (2026). *PRECEPT: Security Self-Improvement of Coding Agents via Evolving Principles*. `arXiv:2611.33519` (`src:2611-33519v1`).
