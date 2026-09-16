# ADK Agent Security & Evaluation Rules

> Research-backed guardrails for securing, hardening, evaluating, and deploying
> agentic systems using the Google Agent Development Kit (ADK) 2, Google Cloud Model Armor,
> Sensitive Data Protection (SDP), and Agent-to-Agent (A2A) protocols.

---

## Agent Security & Data Protection

### DO: Filter prompt injections and jailbreaks at the interceptor layer using Model Armor

Never rely on system instructions or LLM self-evaluation to block adversarial jailbreaks and indirect prompt injections. Adversarial inputs easily manipulate the model's internal attention.

Implement Google Cloud Model Armor inspection in `before_agent_callback` or `before_model_callback`:
- Evaluates inbound user messages against Model Armor templates (prompt injection, jailbreak detection, content filters).
- Blocks or sanitizes suspicious payloads before they reach the model's inference context.
- Returns a sanitized fallback `Content` or raises a security exception without consuming generative model tokens.

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

> Source: Google Codelab: Evaluating Agents with ADK; Advanced ADK Evaluation with LLM-as-a-Judge Method

### DO: Use multi-criteria rubrics for LLM-as-a-Judge rather than single scalar scores

When using an LLM-as-a-Judge to evaluate complex agent traces, single scalar ratings (e.g., "Rate from 1 to 5") suffer from severe prompt sensitivity, verbosity bias, and inconsistency.

Decompose evaluation into orthogonal, rubric-based scoring dimensions:
1. **Task Completion**: Did the agent fulfill the user's primary request? (Binary pass/fail)
2. **Tool Trajectory Fidelity**: Did the agent select the necessary tools without redundant or missing calls?
3. **Grounding & Faithfulness**: Are all claims supported by retrieved tool outputs without hallucinations?
4. **Safety & Policy Compliance**: Were prohibited words, PII, or insecure instructions avoided?

Each dimension must evaluate independently with explicit grading criteria and counterexample probe checks.

> Source: Google Codelab: Advanced ADK Evaluation with LLM-as-a-Judge Method

---

## Related Skills

For implementation details on the procedures behind these rules:
- [`adk-model-armor-interceptor`](skills/adk-model-armor-interceptor/SKILL.md) — Google Cloud Model Armor and SDP interceptor integration
- [`adk-eval-golden-dataset-ci`](skills/adk-eval-golden-dataset-ci/SKILL.md) — Golden dataset trajectory assertions and CI/CD quality gates
- [`adk-a2a-agent-federation`](skills/adk-a2a-agent-federation/SKILL.md) — Agent-to-Agent (A2A) protocol, Agent Cards, and federated coordination
- [`layered-defense-ensemble`](skills/layered-defense-ensemble/SKILL.md) — Layered defense ensemble and correlation modeling

## Sources

- Google Codelab: Build a Secure Agent with Model Armor and Identity
- Google Codelab: Securing a Multi-Agent System
- Google Codelab: Deploying Secure AI Agents on GKE
- Google Codelab: Create multi agent system with ADK, deploy in Agent Runtime and get started with A2A protocol
- Google Codelab: Secure Agent Commerce with AP2 and UCP
- Google Codelab: Evaluating Agents with ADK
- Google Codelab: Advanced ADK Evaluation with LLM-as-a-Judge Method

