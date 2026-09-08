---
name: agentic-review-deploy-loop
description: >
  Structure the downstream SDLC stages (test, review, deploy, maintain) for
  agentic software development. Covers layered agentic/human review with
  REVIEW.md guidelines, hooks as pre-tool approval gates, CI/CD integration
  with environment-tiered autonomy, and control-band monitoring with
  incident-to-intent feedback loops. Derived from the AI-Native SDLC
  Playbook (Claude Academy, Anthropic Applied AI).
source: https://academy.claude.com/courses/ai-native-sdlc-playbook
---

# Agentic Review & Deploy Loop

Use this skill when establishing or improving the review, deployment, and
operational monitoring pipeline for teams using agentic coding tools. The
skill covers everything that happens *after* code is written but *before*
(and after) it reaches production.

## When to Use

- Setting up CI/CD pipelines that include agentic code review
- Defining what humans review vs. what agents review (and why)
- Configuring hooks and permission boundaries for agentic tools
- Establishing production monitoring with automated incident triage
- Connecting production issues back to the planning pipeline

## Core Insight

When agents write most of the code, **review becomes the bottleneck**.
Traditional human-only review queues cannot scale to the volume of agentic
output. The solution is a layered review architecture:

1. **Agentic review** handles volume — mechanical checks, style conformance,
   test coverage, known vulnerability patterns
2. **Human review** handles judgment — architecture decisions, security
   implications, regulated code, novel patterns

This isn't about replacing human review; it's about **reserving human
attention for decisions that require human judgment** while automating
everything that doesn't.

---

## Procedure

### Step 1: Create `REVIEW.md` Guidelines

Define machine-readable review criteria that agentic reviewers enforce.
Place `REVIEW.md` at the repository root (or equivalent location for your
tooling):

```markdown
# Review Guidelines

## Always Check
- [ ] All new functions have tests
- [ ] No hardcoded secrets, API keys, or credentials
- [ ] Error handling covers all failure paths
- [ ] Public API changes are backward compatible
- [ ] Database migrations are reversible
- [ ] No TODO/FIXME without linked issue

## Security Checklist
- [ ] Input validation on all external data
- [ ] SQL queries use parameterized statements
- [ ] Authentication required on new endpoints
- [ ] PII fields are encrypted at rest
- [ ] Rate limiting on public-facing endpoints

## Performance Checklist
- [ ] No N+1 queries introduced
- [ ] Large collections use pagination
- [ ] Caching strategy documented for new endpoints
- [ ] No synchronous blocking calls in hot paths

## Escalate to Human Review When
- Architecture changes (new services, changed boundaries)
- Security-critical code (auth, crypto, PII handling)
- Regulated code (financial calculations, compliance logic)
- Novel patterns not covered by existing guidelines
- Changes to CI/CD pipeline configuration
```

### Step 2: Configure Layered Review Pipeline

Structure the review pipeline with progressive depth:

| Review Layer | Reviewer | Scope | Speed |
|:-------------|:---------|:------|:------|
| **Automated checks** | CI (linters, type checks, tests) | Mechanical correctness | Seconds |
| **Agentic review** | AI reviewer with `REVIEW.md` | Checklist compliance, pattern matching | Minutes |
| **Human review** | Engineer | Architecture, security, judgment calls | Hours |

**Routing rules**:
- All PRs pass through layers 1 and 2 automatically
- Layer 3 is required only when agentic review flags escalation triggers
  (see "Escalate to Human Review When" in `REVIEW.md`)
- In regulated environments, layer 3 is mandatory for all changes to
  designated critical paths

### Step 3: Configure Hooks as Approval Gates

Use pre-tool hooks to enforce permission boundaries. Hooks execute before
the agent acts, providing a checkpoint for high-risk operations:

```yaml
# Example hooks configuration
hooks:
  pre_tool_use:
    # Block file operations outside project scope
    - matcher: "tool in [edit_file, write_file, delete_file]"
      action: "deny"
      condition: "path not starts_with ./src/"
      message: "File operations restricted to ./src/ directory"

    # Require confirmation for database operations
    - matcher: "tool == run_command"
      action: "confirm"
      condition: "command contains 'migrate' or command contains 'DROP'"
      message: "Database operation requires human confirmation"

    # Block network calls to non-allowlisted domains
    - matcher: "tool == run_command"
      action: "deny"
      condition: "command contains 'curl' and domain not in allowlist"
```

**Key principles**:
- Hooks should be managed by the platform team, not modifiable by agents
- Use `allowManagedHooksOnly` (or equivalent) to prevent agents from
  creating their own hooks that bypass restrictions
- Log all hook invocations for audit trail

### Step 4: Implement Environment-Tiered Autonomy

Agent autonomy should inversely correlate with environment criticality:

| Environment | Agent Autonomy | Human Involvement | Rationale |
|:------------|:---------------|:-------------------|:----------|
| **Development** | Full auto | Review after merge | Low blast radius, fast iteration |
| **Staging** | Semi-auto | Approve before deploy | Catches integration issues |
| **Production** | Human-gated | Approve before AND after | Maximum safety, audit trail |

For CI/CD integration, agents can run in headless mode (e.g., `claude -p`
or equivalent non-interactive invocation) within CI runners:

```yaml
# CI pipeline example
stages:
  - name: agentic-review
    run: |
      # Run agentic review in headless mode
      claude -p "Review this PR against REVIEW.md. Flag issues, suggest fixes.
      If security-critical changes detected, output ESCALATE." \
        --output-format json > review_result.json

  - name: route-review
    run: |
      # Route based on agentic review output
      if grep -q "ESCALATE" review_result.json; then
        request_human_review
      else
        auto_approve
      fi
```

### Step 5: Establish Control-Band Monitoring

After deployment, define operational control bands that trigger graduated
responses:

```yaml
# control-bands.yaml
metrics:
  error_rate:
    1_sigma:  # Normal variance
      action: log_only
      notify: none
    2_sigma:  # Elevated
      action: agent_diagnosis
      notify: on_call_channel
      agent_mode: read_only  # Agent can inspect, not modify
    3_sigma:  # Critical
      action: agent_propose
      notify: incident_channel
      agent_mode: propose_only  # Agent proposes, human approves
      auto_rollback: true

  latency_p99:
    threshold: 500ms
    action: agent_diagnosis
    escalation: human_after_5min

  deployment_health:
    canary_error_delta: 2x
    action: auto_rollback
    notify: deploy_channel
```

### Step 6: Close the Loop — Incident to Intent

When a production incident breaches a control band, the agent should
generate an `intent.md` entry that feeds back into the planning pipeline:

1. Agent triages the incident (read-only diagnosis)
2. Agent writes a post-mortem with root cause analysis
3. Agent generates an `intent.md` for the fix, referencing the incident
4. `intent.md` enters the normal planning pipeline (see
   `intent-driven-sdlc-planning` skill)

This closes the SDLC loop: production issues become structured inputs to
the planning system rather than ad-hoc hotfixes.

---

## Environment Caveats

- **Small teams**: For teams of 1-3 engineers, the full layered review
  pipeline may be overhead. Start with agentic review + human spot-checks.
- **Legacy CI systems**: Headless agent invocation requires CI runners
  that support the agent's runtime. Docker-based runners provide the
  cleanest isolation.
- **Compliance requirements**: In SOC2/HIPAA/PCI environments, the
  agentic review layer must itself be documented as a control, with
  evidence of its configuration and coverage.

## Failure Modes

- **Over-trusting agentic review**: Agentic review catches checklist
  items but misses novel attack vectors, subtle architectural regressions,
  and business logic errors. It complements human review, not replaces it.
- **Under-scoped hooks**: Hooks that only block obvious operations
  (e.g., `rm -rf /`) miss subtle variants. Test hooks adversarially.
- **Alert fatigue from control bands**: If 1σ thresholds are too tight,
  the team ignores alerts. Calibrate bands from production baselines,
  not theoretical ideals.
- **Disconnected incident loop**: If incident-generated `intent.md` files
  aren't prioritized in the planning pipeline, the feedback loop is
  broken. Treat them as high-priority inputs.

## Cross-References

- [`intent-driven-sdlc-planning`](../intent-driven-sdlc-planning/SKILL.md) —
  The upstream complement to this skill. Incidents generate `intent.md`
  entries that feed into the planning pipeline.
- [`harness-tampering-audit`](../harness-tampering-audit/SKILL.md) —
  Auditing self-modifying agent behavior during the review stage.
- [`transactional-coding-sandbox`](../transactional-coding-sandbox/SKILL.md) —
  Sandbox isolation for agent execution during CI/CD steps.
- [`deterministic-span-editing`](../deterministic-span-editing/SKILL.md) —
  Safe configuration editing during automated deployment.

## Sources

- The AI-Native SDLC Playbook, Claude Academy (Anthropic Applied AI)
  https://academy.claude.com/courses/ai-native-sdlc-playbook
