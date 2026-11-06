---
name: llm-api-relay-integrity-verification
description: >-
  Audit third-party LLM API relays across three orthogonal integrity surfaces:
  knowledge-boundary and capability-edge behavioral fingerprinting, client-side
  tool-permission enforcement, and input-token billing reconciliation. Detects
  silent model downgrades, unauthorized tool invocations, and systematic token
  overreporting. Derived from Wu et al. (arXiv:2611.07650).
source: https://arxiv.org/abs/2611.07650
license: CC-BY-4.0
repository: https://github.com/Marontis/agentic-engineering
---

# LLM API Relay Integrity Verification

> **Source**: [What the Middleman Delivers: Answer Behavior, Tool Permissions, and Billed Usage in LLM API Relays](https://arxiv.org/abs/2611.07650) (Wu et al., 2026) | Praxis: `src:2611-07650v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

- Qualifying or continuously monitoring third-party LLM API relays, OpenAI/Anthropic-compatible proxy gateways, model routers, or regional API resellers before routing production traffic through them.
- Auditing whether a discounted or same-price API intermediary is silently substituting cheaper models (or mixing traffic across model tiers) behind an expensive flagship model identifier.
- Hardening agent tool-execution runtimes and token-budget accounting when calls traverse an untrusted or semi-trusted API middleman.
- Conducting periodic multi-round vendor re-verification (`11–18` day cadence) to detect time-varying backend routing shifts.

## Overview

Third-party LLM API relays expose drop-in OpenAI Chat Completions (`/v1/chat/completions`) and Anthropic Messages (`/v1/messages`) endpoints, often advertising flagship models below official list prices. Because the relay sits on the wire between the client and upstream providers, it controls model routing, system prompts, tool declarations, and usage metadata.

Wu et al. audited `20` third-party LLM API relays claiming to serve `GPT-6 Astra` and `Claude Opus 5`—split evenly into `10` low-price relays (price score $P_s < 0.95$, defined as the mean ratio of four short-context non-cached input/output token quotes relative to official pricing) and `10` same- or higher-price relays ($0.95 \le P_s \le 1.05$ or $P_s > 1.05$)—across two measurement rounds `11–18` days apart (`36` relay–model pairs in Round 1, `35` retested in Round 2). Their audit uncovered failures across three independent dimensions:

1. **Answer Behavior & Model Substitution**: In Round 1, **`7/10` low-price relays and `2/10` same- or higher-price relays** were flagged for behavioral inconsistency relative to the official API (Fisher exact test $p = 0.0698$; under the stricter all-four specification check, `7/10` vs. `1/10`, $p = 0.0198$), with `Claude Opus 5` accuracy dropping from `0.968–1.000` on the official API to `0.409` at `R20` ($\mathrm{RD} = +0.591$), `0.418` at `R11` ($\mathrm{RD} = +0.574$), `0.704` at `R01` ($\mathrm{RD} = +0.288$), and `0.712` at `R17` ($\mathrm{RD} = +0.256$). On retesting `11–18` days later, `6` relays (`R01`, `R08`, `R10`, `R11`, `R17`, `R20`) remained flagged in both rounds while `7/35` relay–model pairs changed flag status.
2. **Tool-Permission Violations**: While `0/3,332` pooled code and setup responses (`1,686` Round 1 + `1,646` Round 2) contained confirmed malicious payload injections (95% Clopper–Pearson upper bound `0.09%` pooled, `0.18%` Round 1), **`4` relays returned `30` `noop` tool calls in Round 1** (`R11`: `24`, `R17`: `4`, `R04`: `1`, `R10`: `1`) despite explicit `tool_choice=none`, and a **5th relay (`R08`) returned `2` `web_search` tool calls** when no tools were declared at all (`0` in official arms).
3. **Billed Input-Token Inflation**: **`5` relays reported `4,200` to `60,000` more input tokens per request** than the official API on identical payloads—e.g., on a `36`-token official `GPT-6 Astra` prompt, `R01` and `R20` reported `4,416` input tokens (`4,224` cached; median surplus `4.38k`), `R11` reported `4,418` (`4,224` cached), `R08` reported a `4,216`-token cached surplus (`4.22k` on Astra, `734` on Opus), and `R10` reported a median surplus of `~59,500` (`59.5k`) tokens on `Claude Opus 5`. Across all `6` relays with accessible balance endpoints (`R03`, `R04`, `R11`, `R12`, `R17`, `R19`), wallet deductions matched the inflated token counts multiplied by listed prices to the cent (e.g., `$1.20107395` calculated vs. `$1.2011` deducted at `R11`).

---

## Step-by-Step Verification Procedure

### Step 1: Build and Calibrate a Discriminative Question Bank

1. **Candidate Pool Construction Across Three Probing Categories**:
   - Assemble candidate prompts spanning three orthogonal axes that separate frontier targets from cheaper substitutes:
     - *Recent-event knowledge*: factual questions near the target model's knowledge cutoff.
     - *Parameter-scale-sensitive knowledge*: long-tail factual recall that degrades under aggressive quantization or distillation.
     - *Capability-edge reasoning*: multi-constraint symbolic, mathematical, or structural reasoning tasks.

2. **Pre-Validation Against Official Targets and Likely Substitutes**:
   - Run `3` trials per candidate question on the official target endpoints (e.g., `GPT-6 Astra`, `Claude Opus 5`) and on a panel of `3` cheaper substitute models (such as `Claude Haiku 4.5`, `GPT-6 Luna`, and `GLM-4.5-Flash`).
   - Retain a candidate question only if the official target answers correctly in $\ge 2/3$ trials **and** at least `2` cheaper substitutes fail in $\ge 2/3$ trials.
   - Select a balanced primary bank of `25` qualified questions per target model (`9` recent-event knowledge, `8` parameter-scale, `8` capability-edge) and repeat each question for `5` independent trials (`n = 125` scored responses per relay–model cell).

3. **Apply Dual Effect-Size and FDR-Adjusted Hypothesis Thresholds**:
   - For each relay–model cell, compute the accuracy Risk Difference $\mathrm{RD} = h_o / n_o - h_r / n_r$ between the official baseline hit rate ($h_o / n_o$) and the relay hit rate ($h_r / n_r$), alongside a two-sided Fisher exact test adjusted across the test family via the Benjamini–Hochberg (BH) false discovery rate procedure ($q$-value):
     - Classify a cell as **Confirmed Behavioral Inconsistency** when $q < 0.05$ and $|\mathrm{RD}| \ge 0.20$.
     - Classify a cell as **Suspected Behavioral Inconsistency** when ($q < 0.05$ and $|\mathrm{RD}| < 0.20$) or ($0.05 \le q < 0.15$ and $|\mathrm{RD}| \ge 0.20$).

4. **Account for Intra-Family Substitute Blind Spots via Mixture Calibration**:
   - Validate sensitivity using `1,000` simulated mixture cells at replacement rates $r \in \{0, 0.10, 0.25, 0.50, 1.00\}$.
   - Expect `0/1,000` false flags on official-to-official controls ($r = 0$) and `100.0%` detection of distant weak substitutes (`Claude Haiku 4.5`, `GLM-4.5-Flash`) at $r \ge 25\%$ (`94.1%` and `94.6%` at $r = 10\%$ against `Claude Opus 5`).
   - Recognize that closely related intra-family substitutes (such as `GPT-6 Luna` substituting for `GPT-6 Astra`) are flagged in `0.0%` of cells at $r = 10\%$, `4.0%` at $r = 25\%$, `77.7%` at $r = 50\%$, and `100.0%` at $r = 100\%$ (with only `12.9%` reaching *Confirmed* at $r = 100\%$). When auditing against intra-family substitution, increase the per-cell trial count or add latency/token-accounting cross-checks.

---

### Step 2: Audit Client-Side Tool-Permission Enforcement and Content Integrity

1. **Probe `tool_choice=none` and Undeclared Tool Boundaries**:
   - Send canary requests under two restrictive configurations:
     - *Declared-but-disabled tool probe*: declare a dummy `noop` tool in the request schema, set `tool_choice=none` explicitly, and include a system instruction forbidding external search or tool invocation.
     - *Zero-tool probe*: omit the `tools` field entirely while asking a query that might tempt a hidden wrapper to invoke `web_search`.
   - Flag any relay that returns `tool_calls` or `tool_use` blocks in either probe. Because `5/20` relays violated these constraints in Round 1 (`30` `noop` calls across `R11`, `R17`, `R04`, `R10` and `2` undeclared `web_search` calls on `R08`), **never** trust a relay to enforce `tool_choice=none`. Enforce a strict client-side tool-execution firewall that drops any tool call when `tool_choice=none` was requested or when the tool name is absent from the per-request allowlist.

2. **Screen Code and Setup Responses for Injected Artifacts**:
   - Issue `50` code-generation and environment-setup prompts per cell (`5` risk classes: package recommendations, shell scripts, URLs/endpoints, encoded strings, and installation guides $\times 5$ prompt wordings $\times 2$ trials) and run automated static scanners followed by manual verification on flagged candidates before executing relay-returned commands.

---

### Step 3: Reconcile Reported Input Tokens Against Local Tokenization and Wallet Deductions

1. **Compute Total Billed Input Tokens Across Provider Schemas**:
   - Normalize usage fields across API formats: use `prompt_tokens` (including any `prompt_tokens_details.cached_tokens`) on OpenAI Chat Completions and sum `input_tokens + cache_creation_input_tokens + cache_read_input_tokens` on Anthropic Messages.
   - Compare the relay's total reported input tokens on every canary request against the exact token count returned by the official provider API (or local canonical tokenizer) for the identical request payload.

2. **Detect Hidden System-Prompt Prepending and Cached-Token Padding**:
   - Flag any systematic positive token surplus (such as the `4.22k–4.38k` cached input-token surpluses observed on `36`-token official requests at `R01`, `R08`, `R11`, and `R20`, or the `59.5k` median input-token surplus on `R10` Opus) as well as negative token deficits (`-97` to `-355` tokens at `R04`, `R15`, `R20`, which indicate prompt truncation or substitution of a different tokenizer/model).
   - Query the relay's account-balance or usage-ledger endpoint before and after the canary batch to verify whether reported cached/uncached token surpluses are directly deducted from your prepaid balance.

3. **Repeat Audits on a Rolling Multi-Week Schedule**:
   - Because `7/35` retested relay–model pairs (`20.0%`) changed behavioral flag status across an `11–18` day window (with relays such as `R02` Astra shifting from $\mathrm{RD} = -0.024$ to $+0.248$ and `R12` Opus jumping to `29/135` refusals vs. `1` official refusal) and tool-permission violations present in Round 1 disappeared in Round 2, run automated canary checks continuously rather than treating relay qualification as a one-time onboarding gate.

---

## When NOT to Use

- **Direct first-party provider connections with cryptographic TLS pinning**: When your application communicates directly with `api.openai.com` or `api.anthropic.com` over verified TLS without intermediate proxies, aggregators, or third-party OpenAI-compatible gateways.
- **Detecting sub-25% partial traffic mixing of closely related sibling models with a 125-response budget**: As shown by the `GPT-6 Luna` vs. `GPT-6 Astra` mixture calibration (`0.0%` flagged at $10\%$ mixing, `4.0%` at $25\%$), a `25`-question $\times$ `5`-trial question bank is underpowered for low-rate sibling-model dilution unless paired with token-accounting checks or larger sample sizes.

---

## Related Artifacts

- **Rule**: [Agent Sandbox Safety](../../rules/agent-sandbox-safety.md)
- **Rule**: [Agent Evaluation Quality](../../rules/agent-evaluation-quality.md)
- **Skill**: [Sealed Replayable Agent Audit Log](../sealed-replayable-agent-audit-log/SKILL.md)
