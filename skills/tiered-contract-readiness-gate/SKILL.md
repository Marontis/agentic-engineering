---
name: tiered-contract-readiness-gate
description: >
  Audit, remediate, and gate AI-generated ("vibe-coded") application
  repositories for production deployment behind a zero-LLM MCP server by
  partitioning rules into static template contracts, ambiguity-refusing
  parametric extraction contracts, and checker-bound delegated constraint
  contracts, enforcing author-blind checker re-verification with full-suite
  regression revert, and gating release on ordered critical-rule, score, and
  monotonic build-backed deployability checks. Derived from ProdPilot
  (arXiv:2611.17381).
source: https://arxiv.org/abs/2611.17381
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Tiered-Contract Production Readiness Gate

> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

Use this skill when building **automated production-readiness, DevSecOps hardening, or pre-deployment remediation pipelines**—especially over the Model Context Protocol (`MCP`) for AI-assisted IDEs (`VS Code`, `Cursor`, `Windsurf/Devin`, `Claude Code`)—where functional prototypes ("vibe-coded" backends and frontends) fail on first deployment due to missing operational artifacts (hardcoded secrets, unordered security middleware, missing Dockerfiles, missing health endpoints, or unwired CI/CD):

- You want to **eliminate free-form LLM code generation** from routine operational fixes (`88.0%` of readiness rules and `93.5%` of real-world repository violations need zero model-authored code).
- You need **IDE-agnostic MCP enforcement** where the MCP server holds **zero models**, supplies deterministic fix contracts, and verifies every edit on disk without trusting the IDE agent's completion claims (`10.5%` false-success rejection rate).
- You need an **automated release gate** that prevents weighted compliance scores from masking single critical (`P0`) security failures or unbuildable static bundles before provisioning live infrastructure and CI/CD.

**Scope & Complementarity with Existing Skills:**
- **Single-scalar YAML/GitOps edits**: When an LLM proposes a single `(resource, field_path, target_value)` mutation inside an existing Kubernetes/Terraform YAML manifest, apply CST byte-span replacement via [`deterministic-span-editing`](../deterministic-span-editing/SKILL.md) (`arXiv:2609.00227`). Use *this* skill one layer up to classify multi-file application readiness rules across source ASTs, Dockerfiles, secret scans, and environment configs so `88%–93.5%` of violations never invoke an LLM proposer at all.
- **Human/Agent PR review & post-deploy monitoring**: Combine this pre-deployment readiness gate with [`agentic-review-deploy-loop`](../agentic-review-deploy-loop/SKILL.md) for `REVIEW.md` human-escalation routing and post-release `$1\sigma\text{--}3\sigma$` control-band monitoring.
- **General MCP catalog design**: Pair this inverted zero-LLM server architecture with [`mcp-server-design`](../mcp-server-design/SKILL.md) for `outputSchema` typing and progressive discovery.

> **Governance Gate**: Keep the rule store, AST/entropy checkers, and release-gate thresholds frozen outside the IDE agent's editable workspace. Any update to the ruleset, contract templates, or deployability estimator must pass `"DO: Pass every self-modification through one acceptance gate"` in [`recursive-improvement.md`](../../rules/recursive-improvement.md) (including exact two-run reproducibility and zero monotonicity inversions).

---

## Core Insight: Most Readiness Remediation Is Not a Generation Problem

Across **`499` real public Node.js (`Express`) and React (`Vite`) repositories** (`7,407` total violations; `14.8` mean violations/repo, range `6–23`; `100%` failing at least one `P0` critical rule with `4.6` mean `P0` failures) and **`684` real cloud deployments** (`arXiv:2611.17381`):

| Fix Tier (`Table V` & `Section VII-B`) | Ruleset Share (`50` Rules: `28` Express, `22` React) | Real-Corpus Violation Share (`7,407` Violations / `499` Repos) | Sample-Loop Pass Rate (`23` Projects) | Who Authors the Fix Content? |
|:---|:---:|:---:|:---:|:---|
| **1. Static Template** | **`56.0%`** (`28/50`: `16` Express, `12` React) | **`65.9%`** (`4,881 / 7,407`) | **`87.6%`** (`155/177`, **`89.8%`** with env-key declarations; `93.0%` by run end) | Deterministic server template at named AST/file anchor |
| **2. Parametric Extraction** | **`32.0%`** (`16/50`: `9` Express, `7` React) | **`27.6%`** (`2,045 / 7,407`) | **`95.0%`** (`57/60` applied; `15/74` [`20.3%`] refused on ambiguity) | Deterministic codebase extractor (refuses with candidates if ambiguous) |
| **Deterministic Subtotal** | **`88.0%`** (`44/50`: `89.3%` Express, `86.4%` React) | **`93.5%`** (`6,926 / 7,407`: `94.9%` Express, `91.3%` React) | **`96.7%`** of attempted loop instances (`260/269`) | **Zero LLM content (`0` model calls)** |
| **3. Delegated Constraint** | **`12.0%`** (`6/50`: `3` Express, `3` React) | **`6.5%`** (`481 / 7,407`; `~1`/repo across `82.6%` of repos) | **`10/10`** live trials on 1st attempt (`Grok 4.6` & `Claude Opus 5`, `0` regressions) | Client IDE agent inside an explicit file boundary, judged by server checker |

*(Note on paper prose vs. table counts: `Section V-D` and `Fig. 2` specify `4` delegated code-structure rules [`STR-001..004`] plus `2` delegated git-history secret rules [`GIT-003`, `GIT-007`] = `6` delegated rules total; `Section VII-C` informally refers to `"the three hygiene rules"` when describing the `3` live git-history trials [`GIT-003`, `GIT-003*`, `GIT-007`] in `Table VIII`.)*

---

## Step-by-Step Procedure

### Step 1: Invert the MCP Topology & Refuse Ambiguous Stack Detection

Expose a minimal **zero-LLM MCP server** (`5` tools over `stdio`: `connectivity_check`, `stack_detection`, `get_fix_contract`, `report_fix_applied`, and `deploy`, marking the first `4` with `readOnlyHint: true` and `deploy` as environment-mutating with mandatory developer confirmation):

1. **Deterministic blueprint matching (no guessing)**: Inspect `package.json` and the file tree locally with zero network or LLM calls. Load stack-specific blueprints that explicitly mark inapplicable domains as `N/A` (for example, marking database-pooling and API-versioning domains `N/A` on static React/Vite frontends so inapplicable checks are distinguished from forgotten ones). If a repository matches multiple conflicting stacks simultaneously (e.g., declaring both Express and React/Vite in one root), **return `unrecognised` rather than guessing**.
2. **Use syntax-tree and commit-history checkers where order or persistence matters**: Combine configuration readers with modern AST parsers (e.g., `acorn` + `acorn-jsx` for ES2020+ optional chaining and JSX) so checkers verify **statement ordering**—such as `helmet` security middleware registered *before* route handlers and global error middleware *after* routes—and scan **both** the working tree and Git commit history for high-entropy/prefixed secrets.

### Step 2: Partition Every Rule into Static, Parametric, or Delegated Fix Contracts

Enforce schema-level validation in the rule store so every rule declares exactly one fix class matching its implementation:

1. **Static Content Contracts (`56%` of rules)**:
   - Emit idempotent exact content, a **named structural anchor** (out of fixed AST/file positions such as *"immediately after Express app instantiation and before the first route"*, never brittle literal line numbers), required package dependencies, **required environment variable keys**, and an instruction to **change nothing else**.
   - *Why declaring env keys and idempotency matters*: Without idempotency guards and declared dependencies/env keys, retried contracts duplicate insertions or break startup rules (`4` regression reverts eliminated once content contracts declared the env keys they read, lifting static pass rate from `87.6%` to `89.8%`).
2. **Parametric Extraction Contracts (`32%` of rules — Refuse on Ambiguity)**:
   - Re-read the live workspace on every attempt (since earlier fixes may create files needed by later rules) to populate fixed templates with project-specific values (Node version, start script, exposed port, extracted secret env var).
   - **Mandatory ambiguity refusal**: Whenever codebase signals conflict (e.g., two lockfiles `package-lock.json` + `yarn.lock`, two DB drivers, or multiple entry points), **refuse to issue a contract and return the exact list of competing candidates** for human/manual resolution—never guess or ask an LLM to pick silently.
3. **Delegated Constraint Contracts (`12%` of rules — Architecture & Git History)**:
   - Reserve delegation strictly for codebase-organization refactors (e.g., extracting inline DB queries into a service layer, wrapping a root in an error boundary) and git-history secret scrubbing.
   - Emit **zero code** in the contract: send the exact violation location, the formal predicate the checker evaluates, the **explicit allowlist of files that may change**, the files/behaviors that must remain untouched, and the exact checker function name that will judge the result.

### Step 3: Run Priority-Ordered Bounded Repair with Author-Blind Verification & Regression Revert

Never accept an IDE agent's or executor's `"fix applied"` call as proof of remediation:

1. **Process violations one at a time in priority order (`P0 -> P5`)** under hard termination bounds: **at most `3` attempts per rule instance** across the entire run and **at most `5` outer cycles**; route unattemptable or budget-exhausted issues directly to manual review with exact file location and reason.
2. **Author-blind checker re-verification**: On every `report_fix_applied` call—regardless of whether the fix came from a static template, parametric extraction, or live IDE agent—re-run the flagging rule's own checker against the files on disk. Across `237` reported-applied static/parametric fixes in `ProdPilot`, independent verification caught and rejected **`25` (`10.5%`) false reports** (`21` still failing their rule + `4` regressions).
3. **Full-audit regression guard after every disk mutation (`~3.6 s`/loop)**: Immediately re-audit all previously passing rules after any file edit. If a fix breaks *any* previously passing rule (for example, inserting a `/metrics` route above `helmet` middleware), **revert the edit immediately** and send the issue to manual review.

### Step 4: Enforce the Three-Condition Ordered Release Gate (`P0 -> Score -> Monotonic Veto`)

When a repair cycle finishes, re-audit the entire project from scratch (never trusting cached loop state) and evaluate **three conditions in strict order**—returning failed projects to the loop within the `5`-cycle cap, and failing closed if any gate input is missing or undetermined:

1. **Condition 1 — Zero `P0` Critical Failures (`P0 == 0`)**: Weighted scores (`32, 16, 8, 4, 2, 1` for `P0..P5`) hide fatal flaws—a project failing one `P0` rule and nothing else still scores `93` on Express and `91` on React. Hard-block any `P0 > 0`.
2. **Condition 2 — Audit Score Floor (`score >= 90`)**: Require the project to reach the `Production Ready` compliance band across all applicable stack blueprint domains.
3. **Condition 3 — Outcome-Trained Monotonic Deployability Veto (Consulted Last)**:
   - Train any learned deployability classifier (`Model D`, histogram gradient boosting with 5-fold sigmoid calibration) on **real deployment + live-health outcomes** (`684` deployments in `ProdPilot`, `0.909` held-out ROC AUC) plus a **real container-build check** (`~0.31` PR AUC permutation importance), explicitly **excluding the weighted audit score** from features to avoid circularity.
   - **Enforce strict monotonic constraints** (more rule failures can only lower the estimate; a passing container build can only raise it) and verify `0` row-level inversions post-calibration (`0/7,281` single-rule fixes lowered `Model D`, vs. `2,393` and `3,234` inversions in unconstrained models).
   - **Veto-only ordering**: Consult the model *after* Conditions 1 and 2 so it **vetoes** rule-compliant projects that cannot build (e.g., turning away `5` React samples scoring `99–100` at `4.7%–6%` probability due to a missing Vite `index.html`, vs. `85.1%` once buildable) while **never admitting** projects that fail `P0` or the `90` score floor. When porting to a new cloud provider before outcome labels exist, run Conditions 1 and 2 + the local container build check directly.

### Step 5: Provision Live Service First, Smoke-Test Security Headers, and Wire CI/CD Second

Execute deployment as a sequential fail-fast pipeline (`ProdPush`):

1. **Seal credentials outside the repository**: Store cloud/provider tokens under the user's home directory with OS-verified ACLs (on Windows, explicitly set and read back ACL principals because POSIX-style owner-only file modes left credential files readable by `5` other principals), commit **only** generated operational artifacts (refusing to push if uncommitted developer edits exist), inject Git tokens ephemerally per command without writing `.git/config`, and encrypt GitHub Actions secrets as `libsodium` (`PyNaCl`) sealed boxes against the repository public key.
2. **Local container probe before cloud push**: Build the generated multi-stage non-root `Dockerfile` locally and probe the exposed port, mapping build/startup failures into fixed structured categories (`5` categories) rather than feeding unbounded build logs to an LLM.
3. **Service-first live smoke test -> CI/CD wiring**: Create and poll the live cloud service (`15 s` interval, `10 min` cap), run exponential-backoff live smoke checks (`90 s` window) verifying **status `200` on health/API routes, `HSTS`, `CSP`, `Referrer-Policy`, `CORS`, rate-limit, frame/MIME headers, and absence of stack traces**, and **wire the CI/CD workflow second** once the live service identifier exists.

---

## Environment Caveats & Failure Modes

- **Repository secret scrubbing (`GIT-003`/`GIT-007`) is incomplete without external key rotation**: Rewriting Git history removes leaked credentials from commits and working trees, but **cannot revoke live keys at external providers**. Always emit an explicit out-of-band credential-rotation action for human operators alongside history cleanup.
- **Cross-IDE MCP client transport quirks (`VS Code` vs. `Cursor` vs. `Windsurf/Devin`)**: Keep MCP server logic client-agnostic, but size tool responses carefully and validate client configs: `VS Code Copilot Chat 0.65.0` spilled an `11,988`-byte blueprint payload to a temporary file (and retried initial MCP version negotiation once), whereas `Cursor` and `Devin` passed it inline; `Devin 3.10.23` blanked `${workspaceFolder}` variables, requiring a git-ignored machine-local config path; and tool-approval prompts vary by client and model session.
- **Insertion contracts cannot relocate misplaced code or create late-stage files early**: Static anchor insertions fail when an existing error handler must be *moved* rather than added, when a target file contains more secrets (`4`) than the `3`-attempt budget removes one-by-one, or when a high-priority `P0` rule targets a file created later by a lower-priority rule (`35` instances, which resolve on the subsequent cycle once the file exists). Route relocation defects cleanly to delegated contracts or manual review.
- **Outcome deployability models do not transfer zero-shot across cloud providers**: Because platform build commands and static-vs-service semantics differ across hosts (e.g., Render vs. Cloud Run vs. Vercel), retrain Condition 3 on target-provider deployment outcomes before enabling learned probability thresholds.

## Cross-References

- **Related Rules**:
  - [`skill-system-design.md`](../../rules/skill-system-design.md) — Deterministic-first orchestration boundaries and tiered MCP remediation contracts
  - [`agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — Minimal-diff manifest safety, post-completion CWE gates, and secret vaulting
  - [`agent-evaluation-quality.md`](../../rules/agent-evaluation-quality.md) — Independent external verifiers vs. agent self-reports
  - [`recursive-improvement.md`](../../rules/recursive-improvement.md) — `"DO: Pass every self-modification through one acceptance gate"`
- **Related Skills & Specs**:
  - [`deterministic-span-editing`](../deterministic-span-editing/SKILL.md) — CST byte-span replacement for LLM-proposed YAML/GitOps field updates (`arXiv:2609.00227`)
  - [`agentic-review-deploy-loop`](../agentic-review-deploy-loop/SKILL.md) — Layered `REVIEW.md` PR escalation and post-deploy control-band monitoring
  - [`mcp-server-design`](../mcp-server-design/SKILL.md) — Progressive discovery, `outputSchema`, and MCP safety annotations
  - [`nextjs-public-agent-app.spec.md`](../../specs/nextjs-public-agent-app.spec.md) — Pre-deployment security and readiness checklist for public full-stack agent web apps

## Sources

- Khalid, M. S., Asif, M. J., Abbasi, R. N., & Ahmad, R. F. (2026). *ProdPilot: A Layered Model Context Protocol System for Automated Production Readiness and Deployment of Vibe-Coded Projects*. [arXiv:2611.17381](https://arxiv.org/abs/2611.17381) (`src:2611-17381v1`).
