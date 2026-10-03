---
name: poisoned-skill-tool-call-authorization
description: >
  Authorize each tool call at the before-tool-call boundary when the agent
  follows third-party skills that may be poisoned. An independent reviewer
  model sees the trusted user request, a sanitized profile of the skill
  (never the raw skill text), the current call, recent calls and the actual
  contents of scripts the call would run, and returns a fail-closed
  ALLOW/DENY with a reason code.
  Derived from "ActionGuard: Tool Call Authorization under Poisoned Skills" (arXiv:2609.39450).
source: https://arxiv.org/abs/2609.39450
---

# Tool Call Authorization under Poisoned Skills (ActionGuard)

Use this skill when an agent loads skills (instruction files plus helper
scripts) from sources you don't control, and a skill could carry inserted
instructions that steer the agent into exfiltration, deletion, remote
writes or unrequested code execution while the visible task still gets done.

## When to Use

- Agents that install or import community skills, plugins or playbooks
  that bundle scripts the agent may run.
- You need a runtime check that still works when the poisoned skill
  passed provenance checks or was modified after review.
- Library-level defenses (see
  [`skill-evolution-defense`](../skill-evolution-defense/SKILL.md) and
  `rules/skill-system-design.md` "Validate skill provenance before adding
  to library") are in place but you want a second layer at execution time.

Not a replacement for provenance checks or for deterministic permission
enforcement; it is one layer.

## Core Insight

An unauthorized tool call is one that fails either **request relevance**
(it does not serve what the user asked for) or **authority compliance**
(it exceeds the authority the user delegated). A reviewer can judge both
only if it sees the trusted request and what the call will actually do,
and if it is not itself exposed to the poisoned skill text. ActionGuard
therefore replaces the raw skill with a profile built once, and reviews
the real script contents rather than the agent's description of them.

**Evidence** (SKILL-INJECT extended, 319 injection-task pairs: 139
contextual, 180 obvious; OpenClaw framework; target model
gpt-5.5-2026-04-23): attack success rate (ASR) 8.65% with task success
rate (TSR) 90.38%, versus 29.05% / 93.46% with no safeguard, 16.05% /
92.08% for Dynamic Guardian and 13.42% / 88.55% for SkillGuard. Across
five reviewer models (Gemma 4, Qwen 3.5, Ministral 3, GPT-5.4 mini,
Claude Haiku) ASR stayed between 7.73% and 9.30%, while TSR varied more
(87.58%–92.55%). The paper reports no latency or cost figures and no
ablation of the context components.

---

## Procedure

### 1. Build a balanced skill profile, once per skill version

The first time a skill is used (or when no profile exists), a separate
profile-construction model reads the raw skill and writes a profile with
two parts:

- **Ordinary workflow**: tools and commands the skill normally uses, the
  scope of resources it touches, local transformations, validation steps.
- **Suspicious signals**: actions and patterns that would deviate from
  that workflow.

Store profiles in a database the agent cannot write to. Key each profile
by a content hash of the skill so a changed skill gets a new profile; the
paper names version/hash invalidation and independent verification of
profiles as future work, so treat profiles as untrusted until reviewed.

### 2. Intercept every tool call and assemble the review context

At the before-tool-call hook, build a schema-delimited record with:

1. The **trusted user request** (from the user turn, not from the agent).
2. The **skill profile** (not the raw skill).
3. The **current tool call**: tool name and full arguments.
4. The **recent tool-call sequence** proposed by the agent before this
   call (the paper gives no window size; pick one and log it).
5. **Inspected files**: for any script the call would execute, its
   actual file operations, subprocess calls and network access, read
   from disk at review time.

Do not include the agent's free-text rationale; see
`rules/agent-sandbox-safety.md` "Evaluate privileged agent actions using
unescaped raw transcripts in blocking monitors".

### 3. Decide with an independent reviewer, fail closed

The reviewer returns `decision` (ALLOW/DENY), `reason`, and a normalized
`reason_code` (examples from the paper:
`unauthorized_external_data_transfer`, `unauthorized_file_deletion`,
`unauthorized_remote_write`). Deny if the reviewer call fails or its
output does not parse.

### 4. Handle denials

ActionGuard returns the reason and code to the agent so it can propose an
alternative call. That conflicts with `rules/agent-sandbox-safety.md`
"Give blocking action monitors recent call history, and make denials
terminal", whose evidence shows agents route around blocks under
retries. Reconcile them this way:

- For a denial with a security reason code (data transfer, deletion,
  remote write), end the task or escalate to a human.
- Allow a retry with feedback only for relevance denials, count denials
  per task, and escalate after a small fixed number.
- Keep denied calls in the recent-call record so split or re-encoded
  retries are reviewed against them.

### 5. Back the reviewer with deterministic enforcement

An LLM authorization decision should not be the only gate
(`rules/agent-sandbox-safety.md` "Rely on structured LLM authorization
decisions as the sole safety gate"). Keep filesystem, network and
credential permissions enforced below the reviewer.

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| Compound call blocked whole | One call mixes the benign step and the injected step; the agent does not regenerate a safe version, so the task fails too (the paper's INST-10 case) | Ask the agent to split multi-command calls; review per command; measure benign cost on a matched benign arm |
| Stale or poisoned profile | Skill changed after profiling, or the profile model was itself steered | Hash-keyed profiles; human or second-model review of new profiles |
| Retry-based evasion | Denial reason fed back, agent re-encodes the action | Terminal denials for security codes; denial history in context |
| Reviewer-dependent utility | TSR moved ~5 points across reviewer models | Choose the reviewer on your own benign arm, not on ASR alone |
| Narrow evaluation | One framework, one target model, one benchmark | Re-measure ASR and TSR on your stack before relying on the numbers |

> Source: ActionGuard: Tool Call Authorization under Poisoned Skills (arXiv:2609.39450)
