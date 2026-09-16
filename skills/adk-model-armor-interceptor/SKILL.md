---
name: adk-model-armor-interceptor
description: >
  Harden Google ADK agents against prompt injection, jailbreaks, and sensitive data leakage
  using Google Cloud Model Armor and Sensitive Data Protection (SDP) lifecycle interceptors.
source: https://codelabs.developers.google.com/secure-customer-service-agent/instructions?hl=en
---

# ADK Model Armor & Sensitive Data Interceptors

Use this skill when deploying customer-facing or production ADK agents that process
untrusted user prompts and query sensitive internal databases, requiring deterministic
protection against prompt injections, jailbreaks, and PII leaks.

## When to Use

- Neutralizing prompt injections and jailbreak attacks before they reach the model
- Redacting Personally Identifiable Information (PII) from database query tool outputs
- Complying with regulatory privacy mandates (HIPAA, GDPR, PCI-DSS) in AI pipelines
- Enforcing security guardrails at runtime without relying on LLM self-evaluation

---

## Core Architecture

Model Armor and Sensitive Data Protection operate as **lifecycle interceptors**, executing
independently of generative model reasoning:

```
[Untrusted User Input]
         │
         ▼
[before_agent_callback] ──► Inspect with Google Cloud Model Armor
         │                   ├─ Prompt Injection detected? ──► Terminate & Return Refusal
         │                   └─ Safe text passes through
         ▼
    [Agent Model]
         │
         ▼
  [Execute Tool] (e.g. BigQuery Customer DB)
         │
         ▼
 [after_tool_callback]  ──► Inspect with Sensitive Data Protection (SDP)
         │                   ├─ PII detected? ──► Mask with [REDACTED_EMAIL], etc.
         │                   └─ Safe payload passed to model context
         ▼
    [Agent Model]
         │
         ▼
   [Safe Output]
```

---

## Step-by-Step Procedure

### 1. Provision Model Armor & Sensitive Data Protection Templates

In Google Cloud, create a Model Armor template and an SDP De-identification template:

```bash
# Create Model Armor template enforcing injection filters
gcloud alpha model-armor templates create customer-service-armor \
    --location=us-central1 \
    --pi-and-jailbreak-filter-settings-enforcement=ENABLED \
    --confidence-level=MEDIUM_AND_ABOVE

# Create Cloud DLP de-identify template for common PII
gcloud dlp deidentify-templates create \
    --location=us-central1 \
    --display-name="mask-pii" \
    --deidentify-template='{"recordTransformations":{"fieldTransformations":[{"infoTypeTransformations":{"transformations":[{"primitiveTransformation":{"maskConfig":{"maskingCharacter":"*"}}}}]}}]}}'
```

### 2. Implement the Model Armor Inbound Guard

Define an interceptor in `before_agent_callback` to inspect and neutralize prompt injections:

```python
from google.cloud import modelarmor_v1
from google.genai.types import Content, Part

armor_client = modelarmor_v1.ModelArmorClient()

def inspect_prompt_guard(context):
    """Scan incoming user prompt before model inference begins."""
    user_input = context.invocation.get("user_message", "")
    template_name = "projects/PROJECT_ID/locations/us-central1/templates/customer-service-armor"

    response = armor_client.sanitize_user_prompt(
        name=template_name,
        user_prompt_data={"text": user_input}
    )

    result = response.sanitization_result
    if result.filter_match_state == modelarmor_v1.FilterMatchState.MATCH_FOUND:
        # Prompt injection detected: halt execution and return safe refusal
        return Content(parts=[Part(text="I cannot fulfill this request due to safety policies.")])

    return None  # Prompt is clean, proceed normally
```

### 3. Implement the Tool Output PII Redactor

Define an interceptor in `after_tool_callback` to sanitize database or API outputs:

```python
from google.cloud import dlp_v2

dlp_client = dlp_v2.DlpServiceClient()

def sanitize_tool_output(tool, args, result):
    """Mask PII from database query outputs before model ingests it."""
    if not isinstance(result, (dict, list, str)):
        return None

    raw_text = str(result)
    parent = "projects/PROJECT_ID/locations/us-central1"
    inspect_config = {
        "info_types": [
            {"name": "EMAIL_ADDRESS"},
            {"name": "PHONE_NUMBER"},
            {"name": "US_SOCIAL_SECURITY_NUMBER"},
            {"name": "CREDIT_CARD_NUMBER"}
        ]
    }
    deidentify_config = {
        "info_type_transformations": {
            "transformations": [
                {"primitive_transformation": {"replace_with_info_type_config": {}}}
            ]
        }
    }

    resp = dlp_client.deidentify_content(
        request={
            "parent": parent,
            "deidentify_config": deidentify_config,
            "inspect_config": inspect_config,
            "item": {"value": raw_text},
        }
    )

    # Return sanitized dictionary to replace the tool output
    return {"sanitized_result": resp.item.value}
```

### 4. Attach Interceptors to the Agent

Attach the guards directly to the ADK `Agent` instance:

```python
from google.adk import Agent

secure_agent = Agent(
    name="customer_support_agent",
    model=config.MODEL,
    instruction=SYSTEM_INSTRUCTION,
    tools=[lookup_customer_record],
    before_agent_callback=inspect_prompt_guard,   # Blocks injection
    after_tool_callback=sanitize_tool_output,     # Masks PII
)
```

---

## Environment & Implementation Caveats

- **Latency Optimization**: Call Model Armor and SDP APIs synchronously only when evaluating external user inputs. For internal agent-to-agent communication within a private perimeter, consider selective inspection to minimize p95 turn latency.
- **Fail-Closed vs Fail-Open**: In high-security environments, configure `try/except` blocks to fail closed (block the request) if the Model Armor service is temporarily unreachable.
- **Context Replacement**: When overriding tool output in `after_tool_callback`, preserve the expected return structure (e.g. dictionary keys) so model tool reasoning does not crash on missing fields.

---

## Edge Cases & Failure Modes

1. **Obfuscated / Base64 Injections**: Attackers encoding prompt injections in Base64 or unicode homoglyphs can bypass simple keyword filters. Ensure your Model Armor template enables decoding preprocessing transforms.
2. **Context Leakage via Error Messages**: If an internal database raises an exception containing raw customer records (e.g. SQL duplicate key error with user email), the raw error string can bypass tool output filters. Wrap database tools in custom handlers that sanitize exception messages before raising.
