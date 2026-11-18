---
name: agent-card-discovery-validation
description: >-
  Screen untrusted Agent2Agent (A2A) Agent Cards before orchestrator ingestion
  using a three-layer pre-invocation gate: protocol schema validation,
  deterministic NLP/structural screening, and an isolated read-only semantic
  LLM judge. Derived from SecCARD (arXiv:2611.18887).
source: https://arxiv.org/abs/2611.18887
license: CC-BY-4.0
repository: https://github.com/Marontis/agentic-engineering
---

# Agent Card Discovery Validation

> **Source**: [We Have All the Cards: Securing Agent Cards at the Operational Trust Boundary of the Agent2Agent Protocol](https://arxiv.org/abs/2611.18887) (Aguilera, Misra, & López-Morales, 2026) | Praxis: `src:2611-18887v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## When to Use

- Fetching external or third-party Agent2Agent (A2A) Agent Cards from `/.well-known/agent-card.json` (or legacy `/.well-known/agent.json`) before inserting their metadata into an orchestrator's planner prompt, agent registry, or semantic router.
- Defending multi-agent discovery pipelines against pre-invocation selection hijacking, ranking bias, capability misrepresentation, URL pivoting, and Unicode/context obfuscation.
- Selecting and calibrating a discovery-time security gate where JWS `signatures` and OAuth2/OIDC `securitySchemes` authenticate *who* published a card without verifying whether its free-text fields are safe to read.

## Overview

In the A2A protocol (`v1.0.0`, `14` schema fields: `8` required and `6` optional), discovery happens *before* invocation: a client agent fetches a remote server's JSON Agent Card and feeds its attacker-controlled free-text fields (`name`, `description`, `provider`, and `skills` entries including `id`, `name`, `description`, `tags`, and `examples`) directly into an orchestrator LLM to rank and select agents. Optional JWS `signatures` and `securitySchemes` prove origin authenticity and byte integrity, **not** semantic trustworthiness—a validly signed third-party card can still carry discovery-time prompt injection or capability deception.

Aguilera et al. performed the first Internet-scale measurement of deployed A2A Agent Cards across **`36.1 million`** domains (`CC-MAIN-2026-12`), recovering **`310` unique valid cards** (`96.8%` two-annotator agreement, `300/310`, Cohen's $\kappa = 0.804$): **`282` benign**, **`27` suspicious**, and **`1` live malicious card** (`emc2ai.io`, which embedded a directive to rank its agent first alongside unverified accuracy claims). Formalizing **`10` discovery-time attack classes** across selection manipulation (`indirect_injection`, `ranking_manipulation`, `evaluator_manipulation`), capability misrepresentation (`skill_deception`, `skill_chaining`, `out_of_context_skills`), and detection evasion (`url_pivot`, `unicode_tricks`, `context_pollution`, `metadata_gaps`), they introduced **SecCARD**, a three-layer pre-invocation validation pipeline evaluated across **`9` LLM judges** (`6` commercial APIs, `3` local open-weight models):

- **Real-card perturbation benchmark (`660` cards: `60` benign wild seeds + `600` adversarial across `10` classes)**: `GPT-5.5` achieves **`97.0%` security recall** (`98.7%` on malicious, `95.3%` on suspicious) at **`1.7%` seed false-positive rate (FPR)** (`4.4s` latency); `Gemini 3.1 Flash Lite` reaches **`92.3%` recall at `6.7%` FPR (`1.3s`)**; `Claude Opus 4.8` reaches **`91.0%` recall at `5.0%` FPR (`3.9s`)**.
- **Synthetic adversarial benchmark (`260` schema-verified cards across `3` obfuscation levels and `3` sophistication tiers)**: Security recall spans **`66.5` percentage points (`25.8%` on `Mistral Nemo` 12B to `92.3%` on `GPT-5.5`)** under the identical hardened prompt—proving that judge capability and explicit calibration determine whether semantic screening actually works.

---

## Step-by-Step Validation Procedure

### Step 1: Enforce Layer 1 Protocol & Schema Gate Before Parsing Content

1. **Fetch Over HTTPS with Strict Transport Bounds**:
   - Retrieve the candidate Agent Card over HTTPS with bounded connect/read timeouts, strict redirect caps, and a raw response byte ceiling before JSON deserialization.
   - Verify any required JWS `signatures` and `securitySchemes` / `securityRequirements` for publisher identity, while keeping the card marked **`UNTRUSTED`** until content validation completes.
2. **Validate Against the A2A `v1.0.0` Schema**:
   - Require valid JSON containing all **`8` protocol-mandated fields**: `name`, `description`, `supportedInterfaces`, `version`, `capabilities`, `defaultInputModes`, `defaultOutputModes`, and `skills`.
   - Immediately discard malformed payloads, HTML error pages, or partial records that omit mandatory protocol metadata before any downstream NLP or LLM processing.

---

### Step 2: Run Layer 2A Deterministic Structural & NLP Screening (Zero-LLM)

Execute deterministic, prompt-injection-immune checks over the parsed JSON structure to catch structural evasion (`url_pivot`, `unicode_tricks`, `context_pollution`, `metadata_gaps`) and surface lexical risk signals:

1. **Canonicalize Text Across All Nested Fields**:
   - Recursively extract strings across all card fields (`name`, `description`, `provider`, URLs, and nested `skills` `id`/`name`/`description`/`tags`/`examples`).
   - Normalize Unicode homoglyphs (such as Cyrillic or Greek lookalikes) to canonical Latin equivalents before pattern matching, while recording raw-vs-normalized divergences.
2. **Evaluate Seven Deterministic Indicator Groups**:
   - *Instruction patterns*: imperative override phrases, role reassignments, or system/evaluator directives embedded inside descriptive metadata.
   - *Ranking indicators*: superlative self-promotion, comparative claims over competing agents, or explicit selection instructions.
   - *Sensitive-action indicators*: references to credential harvesting, unrestricted shell/filesystem access, payment transfer, or cross-domain data forwarding unrelated to declared modes.
   - *URL analysis*: `supportedInterfaces`, `documentationUrl`, or embedded skill URLs pointing to private/loopback IP ranges (`127.0.0.0/8`, `10.0.0.0/8`, `169.254.169.254`, etc.), mismatched origins, or IDN homograph domains.
   - *Unicode analysis*: zero-width characters, invisible tag code points, or bidirectional control overrides.
   - *Context-length analysis*: abnormal field bloat or repetitive padding designed to push instructions past human inspection or dilution windows.
   - *Skill-consistency analysis*: compute `TF-IDF` cosine similarity between the top-level card `description` and each declared entry in `skills` to flag `out_of_context_skills` grafted onto an otherwise narrow agent.
3. **Assign Deterministic Severity Tier**:
   - Sum matched indicator severities into a deterministic score $S_{\text{det}}$: classify **`S_det >= 8` as `malicious`**, **`3 <= S_det <= 7` as `suspicious`**, and **`S_det < 3` as `benign`**.

---

### Step 3: Evaluate Semantic Intent in Layer 2B via an Isolated Read-Only Judge

Because purely semantic attacks (`indirect_injection`, `ranking_manipulation`, `evaluator_manipulation`, `skill_deception`, `skill_chaining`) can avoid obvious keywords or structural anomalies, pass surviving or `suspicious` cards to a hardened semantic judge:

1. **Minimize and Bound the Inspected Representation**:
   - Extract *only* the fields that enter orchestrator routing context: `name`, `description`, `provider`, endpoint `url` / `supportedInterfaces`, `documentationUrl`, and `skills` (including `examples`).
   - Serialize this reduced projection as canonical JSON and **truncate strictly at `6 KB`** (which preserves `100%` of content for `>95%` of real-world wild cards while bounding token cost and context-stuffing surface).
2. **Isolate the Judge Runtime**:
   - Invoke a **dedicated, read-only LLM instance** configured with **zero tools, zero persistent memory, and zero session/chat continuity** with the orchestrator.
   - Wrap the `6 KB` JSON payload inside explicit untrusted data delimiters (`<UNTRUSTED_CARD> ... </UNTRUSTED_CARD>`) and instruct the judge in its system prompt to treat everything inside the tags strictly as inert data under audit—including statements claiming prior security approval (`evaluator_manipulation`).
3. **Require Structured Three-Class Triage Output**:
   - Require the judge to output a structured verdict in `{BENIGN, SUSPICIOUS, MALICIOUS}` mapped to the `10` threat categories (`II`, `RM`, `EM`, `SD`, `SC`, `OC`, `UP`, `UT`, `CP`, `MG`) with brief field-grounded evidence.

---

### Step 4: Fuse Verdicts and Enforce Tiered Registry Admission

1. **Combine Layer 2A and Layer 2B Conservatively (Never Judge-Only)**:
   - Even frontier judges exhibit category-specific blind spots on structural omissions (`GPT-5.5` drops to `67%` recall on synthetic `metadata_gaps`, whereas `Gemini 3.1 Flash Lite` hits `93%` and Layer 1/2A rules catch missing or inconsistent fields deterministically).
   - Take the conservative maximum severity across Layer 2A and Layer 2B ($\text{Verdict} = \max(\text{Layer 2A}, \text{Layer 2B})$), or short-circuit directly to block whenever Layer 2A scores `malicious` (`>= 8`) or detects private/loopback `url_pivot` targets.
2. **Select a Judge Model Verified on Both Recall and Benign FPR**:
   - High accuracy (`GPT-5.5`: `97.0%` perturbation recall, `1.7%` seed FPR, `5.0%` wild FPR) or fast high-throughput screening (`Gemini 3.1 Flash Lite`: `92.3%` perturbation recall at `6.7%` seed FPR in `1.3s`, though `28.4%` FPR on noisy wild cards) can be paired in a two-tier cascade (`Gemini 2.5 Flash Lite` achieves `0.7%` wild FPR / `0.0%` seed FPR at `1.1s`, but `68.8%` perturbation recall—use it only for high-precision pre-flagging, never as sole allow-gate).
   - Avoid uncalibrated `8B–14B` open-weight judges as standalone gates: on the `310` wild cards they flag **`44.0%–46.5%`** of benign cards as untrusted, while on perturbed/synthetic attacks their recall collapses to **`25.8%–64.2%`** (`17%` on `ranking_manipulation` for `Phi-4` and `Mistral Nemo`).
3. **Apply Strict Admission Actions Before Orchestrator Exposure**:
   - **`MALICIOUS`**: Block registration, quarantine the raw card + hash for audit, and never expose any field to the orchestrator LLM.
   - **`SUSPICIOUS`**: Hold for human security review or admit only into a stripped, structured capability index (rewriting/omitting raw free-text `description` and `examples`) with elevated invocation sandboxing.
   - **`BENIGN`**: Admit into the discovery registry, pinned by content digest so silent remote card mutations trigger re-screening before reuse.

---

## Environment Caveats & Limitations

- **Pre-Invocation Scope Only**: Validating an Agent Card at discovery time does **not** guarantee honest runtime behavior after selection; a benign-looking card can still return malicious responses during task execution or mutate its card later (`rug pull`). Pair discovery screening with digest pinning, runtime envelope verification ([`multi-hop-delegation-auth-propagation`](../multi-hop-delegation-auth-propagation/SKILL.md)), and tool/response guardrails.
- **Standalone Layer 2B Benchmark Scope**: In Aguilera et al.'s empirical tables (`Tables VI–VIII`), the `9` LLM judges are benchmarked standalone on Layer 2B so fusion thresholds remain deployment-configurable. Production deployments should always run Layer 1 + Layer 2A ahead of Layer 2B rather than skipping deterministic checks.
- **Cross-Protocol Reuse (MCP Tool & Server Metadata)**: `8` of the `10` attack classes transfer directly to Model Context Protocol (MCP) `tools/list` descriptions (`url_pivot` maps partially to tool-argument redirect URLs, and `metadata_gaps` adapts from A2A's `14`-field card schema to MCP's `name`/`description`/`inputSchema` contract).

## Failure Modes to Avoid

- **Equating JWS Signatures or OIDC Schemes with Prompt Safety**: Treating cryptographic publisher verification as proof that `description` or `skills[].examples` can be pasted raw into an orchestrator's system prompt.
- **Running Semantic Inspection Inside the Orchestrator Context**: Asking the live planner agent—which holds tools, credentials, and session memory—to "be careful" while reading untrusted cards instead of isolating Layer 2B in a toolless, stateless judge.
- **Deploying Small Judges Without Measuring Both Recall and Benign FPR**: Picking a local `8B–14B` model on latency/privacy grounds without testing adversarial recall (`33.7%` on `Mistral Nemo` perturbation) and real-world benign rejection (`46.5%` wild FPR on `Phi-4`).

---

## Related Artifacts

- **Rule**: [ADK Security and Evaluation](../../rules/adk-security-and-evaluation.md)
- **Rule**: [Multi-Agent Coordination](../../rules/multi-agent-coordination.md)
- **Spec**: [ADK Multi-Agent A2A Spec](../../specs/adk-multi-agent-a2a.spec.md)
- **Skill**: [Multi-Hop Delegation Authorization Propagation](../multi-hop-delegation-auth-propagation/SKILL.md)
- **Skill**: [Description-Only Injection Detection](../description-only-injection-detection/SKILL.md)
- **Skill**: [Google ADK](../google-adk/SKILL.md)
