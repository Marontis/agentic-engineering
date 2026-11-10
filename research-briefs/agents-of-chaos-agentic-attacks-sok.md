# Agents of Chaos: A Systematization of Knowledge (SoK) on Malicious Attacks on Agentic AI Systems

> **Source**: [arXiv:2611.10843](https://arxiv.org/abs/2611.10843) — Thanh M. Truong-Le, Amber Bennoui, Hoang-Ly Nguyen, Gia-Thang Ho, Thai-Minh Truong, Duc-Ly Vu (2026)
> **Praxis Source ID**: `src:2611-10843v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

This paper is a Systematization of Knowledge (`SoK`) literature synthesis screening `186` candidate records and coding **`98` retained primary sources** (through July 2026) into **`284` atomic attacks**, **`452` atomic safeguards**, and **`660` explicit source-supported attack–safeguard relationships** (`https://zenodo.org/records/24009392`). Per [`AGENTS.md`](../AGENTS.md), surveys and taxonomies do not define a single subtask-level procedure and belong in `research-briefs/`—here providing quantitative architecture-level base rates on where agentic attacks concentrate, when delayed compromises activate, and where current safeguard portfolios leave blind spots.

---

## Core Taxonomy: Eight Causal-Mechanism Attack Classes (`284` Atomic Attacks)

Rather than grouping threats loosely by application domain, the authors adjudicate each atomic attack into **one mutually exclusive primary causal-mechanism class** (achieving `78.62%` pre-adjudication inter-coder agreement, Cohen's $\kappa = 0.75$, across `159` aligned attack pairs):

| Class | Causal Mechanism | Papers (`/ 98`) | Atomic Attacks (`/ 284`) | Dominant Subsystem & Activation Profile |
|:---|:---|:---:|:---:|:---|
| **`C2`** | **Tool, MCP, and Action-Layer Attacks** | `21` (`21.4%`) | **`70` (`24.65%`)** *(1st)* | **`97.1%` (`68/70`)** target tool discovery, selection, or invocation; `75.7%` (`53/70`) activate at tool call time; `74.3%` (`52/70`) drive unauthorized actions |
| **`C1`** | **Prompt Injection & Action Hijacking** | **`38` (`38.8%`)** | **`57` (`20.07%`)** *(2nd)* | **`98.2%` (`56/57`)** exploit context/instruction following; `91.2%` (`52/57`) activate immediately during input/observation processing |
| **`C7`** | **Agent Skills and Supply-Chain Attacks** | `17` (`17.3%`) | **`51` (`17.96%`)** *(3rd)* | Malicious `SKILL.md` bundles, poisoned registries, unpinned installers, and cross-skill escalation |
| **`C3`** | **Memory and RAG Poisoning** | `21` (`21.4%`) | **`34` (`11.97%`)** *(4th)* | **`91.2%` (`31/34`) delayed activation** upon later retrieval/recall; `44.1%` (`15/34`) pursue persistent long-horizon control |
| **`C6`** | **Computer-Use and Coding-Agent Attacks** | `10` (`10.2%`) | `24` (`8.45%`) | `58.3%` (`14/24`) exploit code generation/execution, workspace files, or GUI grounding |
| **`C5`** | **Backdoors & Trigger-Conditioned Compromise** | `14` (`14.3%`) | `19` (`6.69%`) | **`100%` (`19/19`)** dormant until explicit lexical, structural, or environmental trigger match |
| **`C4`** | **Multi-Agent Attacks** | `12` (`12.2%`) | `18` (`6.34%`) | **`100%` (`18/18`)** propagate across agent-to-agent delegation, debate, or message buses |
| **`C8`** | **Goal, Task, and Planning Manipulation** | `4` (`4.1%`) | `11` (`3.87%`) | Subgoal corruption, plan-step reordering, and objective drift prior to tool dispatch |

### Architectural Insights from the Attack Distribution

1. **Tool/MCP (`C2`, `24.65%`) and Skills/Supply-Chain (`C7`, `17.96%`) together account for `42.61%` (`121/284`) of all cataloged atomic attacks**—outnumbering classic context-layer prompt injection (`C1`, `20.07%`) more than `2:1` at the atomic attack level even though `C1` appears in the most papers (`38.8%`). Defending the prompt window alone leaves the largest operational attack surfaces exposed.
2. **Immediate vs. Delayed Activation Split**: While `C1` (`91.2%` immediate) and `C2` (`75.7%` tool-selection/invocation) act within the current turn, **`C3` Memory/RAG poisoning (`91.2%`, `31/34`) and `C5` Backdoors (`100%`, `19/19`) decouple write-time compromise from read-time execution**—meaning turn-local input scanners cannot catch cross-session payloads once written into persistent memory or skill stores.

---

## Safeguard Portfolio Skew & Empirical Coverage Deficit (`452` Safeguards, `660` Links)

Coding all `452` proposed atomic safeguards and `660` attack–safeguard links exposes two systemic weaknesses in how agent security stacks are currently designed and evaluated (notably, pre-adjudication inter-coder agreement on *where* a safeguard actually enforces protection was only `40.91%`, $\kappa = 0.37$, across `154` pairs—reflecting vague architectural boundaries in published defenses):

### 1. Severe Pre-Compromise Skew (`85.8%` Preventive/Detective vs. `0.4%` Recovery)

| Safeguard Lifecycle Function | Count (`/ 452`) | Share | Architectural Consequence |
|:---|:---:|:---:|:---|
| **Preventive** (input filters, prompt hierarchy, static gates) | `247` | **`54.6%`** | Assumes compromise can be blocked before execution |
| **Detective** (classifiers, anomaly logs, CoT/action monitors) | `141` | **`31.2%`** | Flags suspicious behavior but rarely undoes side effects |
| **Containment** (sandboxes, least-privilege scopes, network/FS isolation) | `48` | **`10.6%`** | Limits blast radius once preventive/detective layers are bypassed |
| **Corrective** (quarantine, memory eviction, credential rotation, patch/repair) | `14` | **`3.1%`** | Almost absent for poisoned RAG/memory (`C3`) and evolved skills (`C7`) |
| **Recovery** (transactional rollback, state restoration, sealed replay) | **`2`** | **`0.4%`** | **Critical gap**: Virtually zero post-compromise recovery once external/persistent state mutates |

### 2. The Unverified Safeguard Gap (`57.9%` Never Evaluated; Only `11.5%` Strong Coverage)

Across all **`660` explicit attack–safeguard links** mapped in the literature:
- **`382 / 660` (`57.9%`) are proposed conceptually without any empirical evaluation** against the linked attack.
- Only **`278 / 660` (`42.1%`) are directly evaluated**, and within those `278` evaluated pairings:
  - Only **`32 / 278` (`11.5%` of evaluated, `4.8%` of all `660` links)** demonstrate **strong coverage**.
  - **`107 / 278` (`38.5%`)** achieve **partial coverage** (degrading under adaptive wording, multi-step indirection, or benign utility constraints).
  - **`139 / 278` (`50.0%`)** provide only **limited coverage**.

---

## Actionable Implications for Agentic Security Architecture

1. **Require Post-Compromise Containment, Corrective Quarantine, and State Recovery (`> 0.4%` gap)**: Assume preventive (`54.6%`) and detective (`31.2%`) guardrails will be partially bypassed (`88.5%` of evaluated links achieve at best partial/limited coverage). Pair pre-execution filters with transactional filesystem/state snapshots ([`transactional-coding-sandbox`](../skills/transactional-coding-sandbox/SKILL.md)), sealed post-exit audit logs ([`sealed-replayable-agent-audit-log`](../skills/sealed-replayable-agent-audit-log/SKILL.md)), and bitemporal memory/skill quarantine so delayed `C3`/`C5`/`C7` compromises can be rolled back cleanly.
2. **Harden `C2` Tool/MCP (`24.65%`) and `C7` Skill Supply Chains (`17.96%`) as First-Class Boundaries**: Pin MCP descriptors, enforce system-level Principal Context permission intersection ([`principal-context-permission-intersection`](../skills/principal-context-permission-intersection/SKILL.md)), and audit third-party `SKILL.md` bundles via hybrid sandbox intent scanning ([`hybrid-sandbox-skill-intent-audit`](../skills/hybrid-sandbox-skill-intent-audit/SKILL.md)) + cross-skill dependency analysis ([`composite-skill-vulnerability-scanner`](../skills/composite-skill-vulnerability-scanner/SKILL.md)).
3. **Never Claim Unverified Safeguard Coverage (`57.9%` anti-pattern)**: Specify the exact runtime enforcement boundary for every control (eliminating the $\kappa = 0.37$ enforcement-target ambiguity) and measure end-to-end empirical residual ASR alongside clean utility ([`owner-authority-ipi-eval-construction`](../skills/owner-authority-ipi-eval-construction/SKILL.md)).

## Related Artifacts

- [`hybrid-sandbox-skill-intent-audit`](../skills/hybrid-sandbox-skill-intent-audit/SKILL.md) — Companion system by the same authors addressing `C7` (`SKILL.md` supply-chain attacks) via hybrid static, sandbox dry-run, and agentic analysis (`arXiv:2611.10830`).
- [`transactional-coding-sandbox`](../skills/transactional-coding-sandbox/SKILL.md) & [`sealed-replayable-agent-audit-log`](../skills/sealed-replayable-agent-audit-log/SKILL.md) — Concrete implementations closing the `3.1%` Corrective / `0.4%` Recovery lifecycle gap.
- [`owner-authority-ipi-eval-construction`](../skills/owner-authority-ipi-eval-construction/SKILL.md) — Closing the `57.9%` unverified-safeguard gap via reproducible end-to-end IPI evaluation suites (`arXiv:2611.10026`).
- [`rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md) — Defense-in-depth, rollback, and MCP/tool boundary rules.
