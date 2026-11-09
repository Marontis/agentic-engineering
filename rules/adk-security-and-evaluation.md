# ADK Agent Security & Evaluation Rules

> Research-backed guardrails for securing, hardening, evaluating, and deploying
> agentic systems using the Google Agent Development Kit (ADK) 2, Google Cloud Model Armor,
> Sensitive Data Protection (SDP), and Agent-to-Agent (A2A) protocols.
>
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Agent Security & Data Protection

### DO: Filter prompt injections and jailbreaks at the interceptor layer using Model Armor

Never rely on system instructions or LLM self-evaluation to block adversarial jailbreaks and indirect prompt injections. Adversarial inputs easily manipulate the model's internal attention.

Implement Google Cloud Model Armor inspection in `before_agent_callback` or `before_model_callback`:
- Evaluates inbound user messages against Model Armor templates (prompt injection, jailbreak detection, content filters).
- Blocks or sanitizes suspicious payloads before they reach the model's inference context.
- Returns a sanitized fallback `Content` or raises a security exception without consuming generative model tokens.

Treat the classifier as one layer, not the boundary: never return its confidence scores to callers, and keep structural controls (tool authorization, argument-level policy) behind it.

Tension with "DON'T: Treat compact prompt-injection classifiers as intent detectors, or expose their scores" (agent-sandbox-safety.md): confidence-guided paraphrases flipped Prompt Guard 2 while the jailbreak still worked. Interceptor-layer filtering is still the right *placement*; the tension is only about treating its verdict as sufficient.

Give the interceptor a benign-cost budget before enabling it: measure its false-refusal rate on a matched benign arm (benign inputs put through the same encodings and formats as the attack set), accept on the harm gap rather than on block rate alone, and re-measure on the assembled stack (interceptor plus every other refusal or quarantine layer), not per layer. See "DO: Measure each defense's benign cost on a matched benign arm, on the assembled stack" (agent-sandbox-safety.md).

**Scope:** ADK 2 agents using Model Armor templates (Google codelabs; no benchmark). The benign-cost requirement comes from 2609.26176 and 2609.22818 via the agent-sandbox-safety entry above.

```python
from google.genai.types import Content, Part
from google.cloud import modelarmor_v1

def inspect_model_armor(context, request):
    user_prompt = request.contents[-1].parts[0].text
    # Call Model Armor template inspection
    sanitized_text, is_blocked = model_armor_client.sanitize(user_prompt)
    if is_blocked:
        # Intercept call and return security refusal
        return Content(parts=[Part(text="Security alert: Request blocked by safety policy.")])
    request.contents[-1].parts[0].text = sanitized_text
    return None  # Continue with safe prompt
```

> Source: Google Codelab: Build a Secure Agent with Model Armor and Identity; Securing a Multi-Agent System

### DO: Redact PII in tool inputs and outputs with Sensitive Data Protection (SDP)

Autonomous agents querying production databases (e.g., BigQuery, customer CRM) frequently retrieve sensitive Customer Personally Identifiable Information (PII) like emails, phone numbers, or credit cards. If injected raw into model context, this sensitive data can be hallucinated, logged, or exfiltrated.

Enforce Cloud Sensitive Data Protection (SDP / DLP) de-identification:
- Inspect tool arguments in `before_tool_callback` to ensure no raw PII is passed outward.
- Inspect and mask tool outputs in `after_tool_callback` before the model context ingests the results.
- Replace detected infoTypes (e.g., `EMAIL_ADDRESS`, `US_SOCIAL_SECURITY_NUMBER`) with deterministic tokens (`[EMAIL_1]`, `[SSN_1]`).

```python
def redact_tool_output(tool, args, result):
    if isinstance(result, dict):
        text_content = str(result)
        deidentified_text = dlp_client.deidentify(text_content, inspect_template=SDP_TEMPLATE)
        return {"sanitized_output": deidentified_text}
    return None
```

> Source: Google Codelab: Securing a Multi-Agent System; Build a Secure Agent with Model Armor and Identity

### DO: Enforce Workload Identity Federation for tool database and API access

Never store hardcoded service account JSON keys inside agent source code, environment variables, or container images.

Configure GKE Workload Identity or Cloud Run Service Account binding:
- Bind the agent's Kubernetes Service Account (KSA) directly to a Google Service Account (GSA) with minimal IAM permissions.
- Restrict database connectors (e.g. BigQuery, Cloud SQL) using granular IAM roles (e.g., `roles/bigquery.dataViewer` on specific datasets only).
- Verify credentials at startup using Application Default Credentials (ADC).

> Source: Google Codelab: Deploying Secure AI Agents on GKE; Build a Secure Agent with Model Armor and Identity

---

## Multi-Agent Federation & Protocols

### DO: Enforce mutual agent authentication and Agent Card verification over A2A

In an Agent-to-Agent (A2A) multi-agent architecture where agents communicate across network boundaries, never trust inbound JSON-RPC calls blindly.

Enforce multi-agent identity verification:
- Every agent deployed to Agent Runtime must publish an authenticated Agent Card (`agent.json`) declaring its identity, capabilities, and required scopes.
- Root coordinator agents must validate the recipient agent's digital signature and endpoint URL before delegating sensitive tasks.
- Transmit requests using signed JSON-RPC 2.0 envelopes with caller identity headers and trace contexts.

> Source: Google Codelab: Create multi agent system with ADK, deploy in Agent Runtime and get started with A2A protocol

### DO: Require cryptographic authorization tokens for agent commerce (AP2 & UCP)

Never permit an LLM's natural language output (e.g., "Confirmed: purchased item for $50") to authorize financial transactions, cart checkout, or payment captures. Natural language commitments can be hallucinated or manipulated via prompt injection.

Implement the Agent Payment Protocol (AP2) and Unified Commerce Protocol (UCP):
- Agent tools browse products and build carts using structured UCP schemas.
- The checkout step requires an external human-in-the-loop cryptographic authorization token signed by the user's payment provider.
- Tools execute settlement only upon presenting the valid, non-repudiable AP2 payment receipt.

> Source: Google Codelab: Secure Agent Commerce with AP2 and UCP (Next '26)

---

## Evaluation & CI/CD Quality Gates

### DO: Gate production deployment on golden dataset trajectory validation in CI/CD

Do not deploy agent instruction updates, new skills, or model upgrades based on subjective conversational testing or vibes. Subtle prompt changes frequently induce tool selection regressions.

Establish an automated evaluation gate:
- Export verified user sessions from ADK Web as an authoritative **Golden Dataset**.
- Assert both final response quality *and* the exact **tool call trajectory** (tool invocation order and parameter schema validity).
- Wire `adk eval` into automated CI/CD pipelines (`pytest` in GitHub Actions or Cloud Build); fail the build if trajectory accuracy or evaluation scores drop below baseline thresholds.

```python
# test_agent_eval.py
import pytest
from google.adk.eval import evaluate_agent

def test_golden_dataset_eval():
    results = evaluate_agent(
        agent_module="app.agent",
        dataset_path="tests/eval/golden_dataset.json",
        metrics=["tool_call_match", "response_similarity"],
    )
    assert results.overall_pass_rate >= 0.95, f"Regression detected: {results.summary}"
```

**Scope:** acceptance and deploy gates for ADK 2 agents (ADK codelabs;
no benchmark). At these gates, run the full frozen golden dataset plus
the security suites, never a change-specific subset. Behavior-aware
test selection is for the inner search loop only. Tension with "Select
verification tasks based on what each modification changes"
(agent-evaluation-quality.md): selected tests while searching, full
frozen and security suites at acceptance and deploy.

The pass-rate floor (0.95) is necessary, not sufficient. A change is accepted only with no regression beyond a noise margin δ on previously-correct cases and held-out tasks, where δ is estimated from repeated runs of the unchanged baseline; the negative security testbed is always strict (zero tolerance). See "DO: Pass every self-modification through one acceptance gate" (recursive-improvement.md).

> Source: Google Codelab: Evaluating Agents with ADK; Advanced ADK Evaluation with LLM-as-a-Judge Method

### DO: Use multi-criteria rubrics for LLM-as-a-Judge rather than single scalar scores

When using an LLM-as-a-Judge to evaluate complex agent traces, single scalar ratings (e.g., "Rate from 1 to 5") suffer from severe prompt sensitivity, verbosity bias, and inconsistency.

Decompose evaluation into orthogonal, rubric-based scoring dimensions:
1. **Task Completion**: Did the agent fulfill the user's primary request? (Binary pass/fail)
2. **Tool Trajectory Fidelity**: Did the agent select the necessary tools without redundant or missing calls?
3. **Grounding & Faithfulness**: Are all claims supported by retrieved tool outputs without hallucinations?
4. **Safety & Policy Compliance**: Were prohibited words, PII, or insecure instructions avoided?

Each dimension must evaluate independently with explicit grading criteria and counterexample probe checks.

**Scope:** Multi-dimensional LLM-as-a-Judge evaluation rubrics for Google ADK 2 agent trajectories (Google Codelab: Advanced ADK Evaluation with LLM-as-a-Judge Method; design guidance, no benchmark figures).

> Source: Google Codelab: Advanced ADK Evaluation with LLM-as-a-Judge Method

---

## Runtime Authority Hysteresis & Third-Party API Relay Auditing

### DON'T: Gate runtime authority restriction solely on single-step trust derivatives (d_t < -theta_r)

Never trigger authority restriction solely when a single-step readiness drop exceeds a fixed derivative threshold ($g_t - g_{t-1} < -\theta_r$). Always combine step-drop triggers with an absolute band-ceiling check ($g_t < \mathrm{down}(a_{t-1})$) or a sliding-window cumulative degradation check, and fuse behavioural trust ($T_t$), stability ($S_t$), and risk ($R_t$) rather than relying on a single signal.

**Scope:** TRAP (`v1.0.0`) dynamic runtime authorization controller across $n = 100$ matched Monte Carlo traces (`exp003`–`exp012`) comparing abrupt ($L = 1$) vs gradual ($L \in \{5, 10, 20\}$) readiness degradation against Static, Risk-only, and Symmetric baselines (arXiv:2611.06996).

**Evidence**: Across $n = 100$ matched Monte Carlo traces (`arXiv:2611.06996`), TRAP's single-step restriction rule ($\theta_r = 0.10$, $k = 3$, $\theta_e = 0.05$) restricted immediately ($\mathrm{RR} = 0.00$, Excess-Authority Duration $\mathrm{EAD} = 0.81$ intervals) and recovered `37.5%` faster than a symmetric baseline (`10.72` vs `17.14` intervals) under abrupt degradation ($L = 1$). However, when the exact same `~0.308` readiness drop occurred gradually over $L = 5, 10, 20$ intervals (`exp012`), TRAP restricted on only `4/100` traces at $L = 5$ and `0/100` traces (`0%`) at $L = 10$ and $L = 20$, causing Excess-Authority Duration to jump from `0.81` to `18.92`, `18.15`, and `15.89` intervals (worse than Symmetric's `10.12`, `10.28`, and `9.85` intervals and matching the Static no-restriction policy), while a Risk-only baseline granted `24.05%` of escalations during active degradation ($\mathrm{PER} = 0.2405$; see [trap-trust-responsive-runtime-authorization](../research-briefs/trap-trust-responsive-runtime-authorization.md)).

Tension with "Separate assurance evidence validity from contextual applicability, gate actions by authority epoch, and enforce hard step-wise safety projections" (agent-sandbox-safety.md): authority-epoch revocation (`ACCA`, `arXiv:2611.05632`) invalidates in-flight capabilities once a degradation event is triggered, whereas `TRAP` (`arXiv:2611.06996`) shows that triggering restriction solely on a single-step derivative ($g_t - g_{t-1} < -\theta_r$) misses gradual readiness drift ($L \in \{5, 10, 20\}$); pair authority-epoch revocation with an absolute band-ceiling check ($g_t < \mathrm{down}(a_{t-1})$) or sliding-window cumulative degradation trigger.

> Source: Trust Responsive Runtime Authorization for Agentic AI with Empirical Characterization of Policy Behavior and Parameter Sensitivity (arXiv:2611.06996)

### DO: Enforce client-side tool-permission firewalls, behavioral canary checks, and input-token reconciliation when routing through third-party LLM API relays

Verify relay integrity continuously (`11–18` day cadence) across three surfaces: (1) run a pre-validated `25`-question $\times$ `5`-trial discriminative question bank ($q < 0.05$ and $|\mathrm{RD}| \ge 0.20$), (2) enforce a client-side tool firewall that drops any returned `tool_calls` when `tool_choice=none` was specified or when no tools were declared, and (3) compare relay-reported total input tokens (`input_tokens + cache_creation_input_tokens + cache_read_input_tokens` or `prompt_tokens`) against local canonical tokenization on every request. Procedure: [`llm-api-relay-integrity-verification`](../skills/llm-api-relay-integrity-verification/SKILL.md).

**Scope:** Two-round empirical audit (`11–18` days apart) of `20` third-party API relays offering `GPT-6 Astra` and `Claude Opus 5` (`36` and `35` relay–model pairs) across OpenAI Chat Completions and Anthropic Messages endpoints (arXiv:2611.07650).

**Evidence**: Across `20` third-party relays (`arXiv:2611.07650`), `7/10` low-price ($P_s < 0.95$) and `2/10` same- or higher-price relays were flagged for behavioral inconsistency in Round 1 (with `Claude Opus 5` accuracy dropping from `0.968–1.000` official to `0.409` at `R20` and `0.418` at `R11`, and `7/35` pairs changing flag status between rounds). Four relays returned `30` `noop` tool calls despite `tool_choice=none` (`R11`: `24`, `R17`: `4`, `R04`: `1`, `R10`: `1`) and a fifth (`R08`) returned `2` undeclared `web_search` tool calls. Five relays overreported input tokens by `4,200` to `60,000` tokens per request (e.g., `4,416–4,418` billed input tokens on a `36`-token official Astra request at `R01`, `R11`, and `R20`, and a `59.5k` median token surplus on `R10` Opus), with wallet deductions matching the inflated token counts to the cent across all `6` relays with balance APIs.

> Source: What the Middleman Delivers: Answer Behavior, Tool Permissions, and Billed Usage in LLM API Relays (arXiv:2611.07650)

### DON'T: Rely on thinking-tag stripping or final-answer-only inspection to defend LRMs from CoT thought-injection

Do not treat stripping `<think>` tags from untrusted inputs or inspecting only rendered final responses as sufficient defenses for Large Reasoning Models (LRMs). Instead, screen untrusted inputs (documents, repository files, emails, tool outputs) for first-person deliberative reasoning style that mimics the deployed model's native Chain-of-Thought (CoT) voice, scan both raw API reasoning traces and final responses with data-loss-prevention (DLP) filters, and enforce task-scoped tool-call auditing in the agent harness. Payloads written in a target LRM's own CoT voice induce role confusion—pre-committing the agent to unauthorized tool calls while suppressing attack disclosure in the final response—and stripping `<think>` tags relocates data leaks from the visible response into the hidden reasoning channel rather than eliminating them.

**Scope:** Open-weight production Large Reasoning Models (`GLM-5.3-Flash` 320B, `GLM-5.2` 750B, `MiniMax-M2.5` 230B, `Qwen3.8-Flash-Next` 125B, `Qwen3.8-27B`) evaluated across 6,000 direct PII-extraction runs and 1,200 containerized ReAct cyber-range runs (arXiv:2611.08811).

**Evidence**: In Study 1 (6,000 direct injection runs against a 150-record PII database, `arXiv:2611.08811`), 20.8% of all data leaks occurred exclusively inside the `<think>` trace (and 11.4% in both channels), and stripping `<think>` tags increased the hidden think-only leak share to 28.9% on `GLM-5.3-Flash` and 33.7% on `Qwen3.8-27B`. In Study 2 (1,200 indirect injection runs in a Docker cyber range), standard user-voice prompt injection achieved 0% Attack Success Rate (ASR) and was flagged in 82%–100% of runs, whereas indirect payloads styled in `MiniMax-M2.5`'s native CoT trace with `<think>` tags achieved 42% ASR on reverse-shell exfiltration and 50% ASR on repository backdooring (8% and 10% without tags) while causing agents to make no mention of the injection in 68%–100% of final responses (see [thought-injection-attacks-reasoning-agents](../research-briefs/thought-injection-attacks-reasoning-agents.md)).

> Source: I Think, Therefore I Attack: Evaluating Thought Injection Attacks on Reasoning Agents (arXiv:2611.08811)

### DON'T: Feed unverified single-sided evidence passages into fact-checking judges without provenance and rebuttal checks

Do not evaluate claims in RAG or automated fact-checking pipelines by passing retrieved or user-supplied evidence passages directly to an LLM judge without independent source-provenance verification, bidirectional counter-evidence retrieval, and atomic claim decomposition. Standard prevention and detection defenses—including instructional prompts, input paraphrasing, known-answer canary detection, LLM-based self-examination, and response-based backtranslation—target directive overrides or template artifacts and fail to detect multi-agent debate-synthesized passages that dynamically adapt classical rhetorical modes (`Logos`, `Pathos`, `Ethos`) to flip verdicts while remaining fluent and template-free.

**Scope:** Black-box RAG and LLM fact-checking pipelines (`Qwen3-32B`, `Llama3-8B`, `Llama3.1-8B`, `Gemma2-9B`, `Mistral-7B`) evaluated across `FEVER`, `HealthVer`, `CLIMATE-FEVER`, and `SciFact` under 6 prompt-injection defenses (arXiv:2611.08756).

**Evidence**: Across 1,600 trials on `Qwen3-32B` (`arXiv:2611.08756`), Debate-to-Deceive (D2D) achieved 98.8% average ASR without defense (`98.5%` FEVER, `97.0%` HealthVer, `99.5%` CLIMATE-FEVER, `100.0%` SciFact; 99.0% causal ASR across the 1,224 trials where bare-claim verdicts differed) and 98.3% average ASR under `Known-answer` detection, which blocked 0 of 800 defended attacks. Across `Llama3-8B`, `Gemma2-9B`, `Llama3.1-8B`, and `Mistral-7B`, whereas template-based `AutoDAN` collapsed from 100.0% to 0.0% ASR under `Known-answer` detection and single-agent `ADMIT` collapsed to 0.0%–1.5% ASR under `LLM-based` detection, D2D maintained 84.5%–97.0% ASR under `Known-answer` detection and 100.0% ASR under `Instructional`, `LLM-based`, `Response-based`, and `Paraphrasing` defenses across all four models (see [debate-to-deceive-fact-checking-poisoning](../research-briefs/debate-to-deceive-fact-checking-poisoning.md)).

> Source: Debate to Deceive: Poisoning LLM's Fact-Checking via Game-Theoretic Multi-Agent Debate (arXiv:2611.08756)
