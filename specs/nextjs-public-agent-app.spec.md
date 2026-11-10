# Public-Facing Next.js & Full-Stack Agent Application Specification Template

> Fill in this template when architecting, building, or securing a public-facing web application (Next.js App Router, React Server Components, Server Actions, or BFF API routes) that routes user interactions to LLM agents, MCP servers, or multi-agent backends. Each section surfaces research-backed architectural decisions and security boundaries.
>
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## 1. Application Topology & BFF Trust Boundary

### How does the frontend communicate with the agent/model layer?

- [ ] **Backend-for-Frontend (BFF) via Next.js Route Handlers (`app/api/.../route.ts`) or Server Actions** *(Recommended Default — keeps model/MCP credentials strictly server-side; never expose model API keys, MCP endpoints, or raw system prompts to browser bundles)*
- [ ] **Dedicated Agent Orchestration Microservice (Cloud Run / GKE / FastAPI / ADK)** behind a signed BFF proxy
- [ ] **Direct Edge / Client-to-Gateway Streaming** with ephemeral, scope-bound session tokens (`<= 5 min` TTL)
- [ ] Other: ___

### What hosting and security substrate is used?

- [ ] **Managed GCP Stack**: Cloud Run / GKE + Cloud Armor WAF + Identity-Aware Proxy (IAP) / Firebase Auth + Vertex AI / Model Armor + Secret Manager
- [ ] **Cloud-Agnostic / Multi-Cloud Stack** (Vercel / AWS / Cloudflare / Railway / Self-Hosted): Requires explicit application-layer equivalents for prompt-injection screening, egress allowlisting, secrets vaulting, and API relay integrity verification (`arXiv:2611.07650`)
- [ ] **Hybrid**: Frontend on edge CDN (Vercel/Cloudflare), Agent & MCP runtime in isolated VPC/container cluster

---

## 2. Control-Flow Integrity & Prompt Injection Defense

> **Research basis**: Public-facing web apps mix trusted user session state with untrusted external data (search results, uploaded documents, database rows, third-party webhooks). Under standard ReAct loops, untrusted data can either hijack control flow (`Instruction Override`) or corrupt the parameters/data of the in-progress task (`Task-Tampering IPI`, `arXiv:2611.07640`).

### How are user requests compiled into backend tool/MCP actions?

- [ ] **Compile-Then-Execute Gateway (`arXiv:2611.06039`)** *(Recommended Default)*:
  1. **Compile Phase (Trusted Context Only)**: Parse the authenticated user request + session role into a typed action plan / DAG with locked control flow and symbolic data placeholders *before* any untrusted external content enters the context window.
  2. **Execute Phase (Quarantined Data Processing)**: Populate data placeholders using restricted, tool-less LLM calls or deterministic parsers over untrusted content; untrusted outputs cannot add nodes, switch tools, or alter destination parameters.
- [ ] **Declared-Destination View Splitting & Germline Verification (`arXiv:2611.06585`)**: Partition every tool/Server Action schema into destination parameters (`D`: URL, recipient, table/record ID, file path) and content parameters (`C`, `D ∩ C = ∅`), and authorize `D` via a data-free germline fork initialized only on the user's request.
- [ ] **Decode-Time Provenance Binding (`arXiv:2610.31974`)**: Tag every uploaded file, OCR output, or external webhook payload with `UNTRUSTED_EXTERNAL` HMAC provenance and block unpromoted tainted context at mutative sinks.

### How are uploaded documents and external inputs sanitized before reaching the model?

- [ ] **Pre-Compression Input Screening (`arXiv:2611.06380`)**: Run prompt-injection / safety classifiers (e.g., GCP Model Armor or local linear/deberta guards) on the **raw uncompressed input** before any context trimming or summarization.
- [ ] **Display-Fidelity Office Document Extraction (`Prism`, `arXiv:2611.05806`)**: Strip non-displayed OOXML runs (`w:vanish`, `< 2pt` font, low-contrast text, hidden sheets/columns) and reconcile against rendered views before feeding `.docx`/`.xlsx`/`.pptx` uploads to the agent.

---

## 3. Authentication, Multi-Hop Delegation & Continuous Authorization

> **Research basis**: When a Next.js BFF delegates to an orchestrator agent, which in turn calls downstream A2A agents or MCP servers, naive service-account sharing creates a `Confused Deputy` vulnerability (`arXiv:2611.07050`). Furthermore, static session-start tokens cannot revoke in-flight agent actions when runtime anomaly scores spike (`ACCA`, `arXiv:2611.05632`; `TRAP`, `arXiv:2611.06996`).

### How is user identity propagated across agent and MCP hops?

- [ ] **On-Behalf-Of (OBO) Scoped Delegation Tokens (`arXiv:2611.07050`)** *(Recommended Default)*:
  - Mint short-lived, cryptographically signed delegation tokens binding `(originating_user_sub, acting_agent_id, hop_count, permitted_tool_scopes, resource_tenant_id, exp)`.
  - Enforce downstream verification at **every** MCP server and A2A hop (never trust the immediate caller's ambient service account alone).
  - Strictly attenuate scopes at each hop (`Permissions(Hop k+1) ⊆ Permissions(Hop k)`).
- [ ] **Authority-Epoch Continuous Authorization (`ACCA`, `arXiv:2611.05632` & `TRAP`, `arXiv:2611.06996`)**:
  - Separate **Intrinsic Token Validity** $V(e, t)$ from **Contextual Applicability** $A(e, x_t)$ (current risk score, tenant boundary, rate anomaly).
  - Bind mutative Server Actions and MCP tool calls to a monotonic **authority epoch** $\tau_k$ so stepping down trust (`A3 -> A1`) immediately preempts in-flight tool calls.
- [ ] **Out-of-Band HITL for Consequential Actions (`I-HITL`, `arXiv:2610.35835`; `arXiv:2611.11571`)**:
  - Require hardware-attested out-of-band confirmation (separate from the chat stream) behind a canonicalized capability monitor, triggered by provenance taint with a deterministic per-episode approval cap ($n = 1$), for financial transactions, destructive DB mutations, external sends, or permission escalations.
- [ ] **Fact-Grounded Reverse-Proxy Access Control (`BACGuard`, `arXiv:2611.10157` — [`fact-grounded-access-control-proxy`](../skills/fact-grounded-access-control-proxy/SKILL.md))**:
  - Canonicalize paths, hard-reject duplicate parameters, and reconstruct caller identity + multi-path FK/join-table resource ownership deterministically via read-only DB joins (`88–90%` of requests in `< 1 ms`), reserving out-of-band identity-grounded LLM inspection strictly for response-path cross-user leakage (`<= 12%`).

---

## 4. Model Routing & Non-Managed API Relay Integrity

> **Research basis**: When routing outside first-party cloud endpoints (e.g., using third-party OpenAI-compatible API relays, multi-provider routers, or fallback proxies), empirical audits (`arXiv:2611.07650`) show relays frequently alter answer behavior, silently strip or corrupt tool-call schemas/permissions, and inflate billed token counts.

### Which model serving boundary is used?

- [ ] **First-Party Managed Endpoint** (GCP Vertex AI / Anthropic Direct / OpenAI Direct with private VPC peering or signed IAM credentials)
- [ ] **Third-Party API Relay / Multi-Provider Router** — If selected, enforce the **Relay Integrity Checklist (`arXiv:2611.07650`)**:
  - [ ] **Local Tokenizer Accounting**: Count prompt and completion tokens locally in the Next.js BFF and alert when billed relay usage diverges by `> 5%`.
  - [ ] **Tool-Schema Canary Probes**: Periodically dispatch deterministic canary tool-call requests to verify the relay preserves `tool_choice`, parallel tool calls, and strict JSON schema constraints without silent fallback to weaker models.
  - [ ] **Cryptographic Behavioral Fingerprinting**: Verify model identity on high-stakes routes rather than trusting the relay's echoed `model` string.

---

## 5. MCP Server & Data-Rendering Security Boundary

> **Research basis**: Multi-server MCP deployments suffer from reasoning, execution, and memory hallucinations (`MCPHallu`, `arXiv:2611.07689`), cross-server namespace shadowing (`arXiv:2611.03555`), and task-tampering payloads that corrupt numbers or links rendered in the user's UI (`arXiv:2611.07640`).

### How are MCP tool outputs validated and rendered in the Next.js UI?

- [ ] **Server-Prefixed Closed-World Resolution & Counterfactual Least-Privilege Roles (`<server_id>__<tool_name>`, `arXiv:2611.03555`, `arXiv:2609.19425`; `PRISM`, `arXiv:2611.11539`)**: Pin MCP tool schemas and container digests (`ETUDE`, `arXiv:2611.01976`), induce minimal pre-session tool role masks via sandbox `do(m)` counterfactual interventions ([`counterfactual-privilege-role-induction`](../skills/counterfactual-privilege-role-induction/SKILL.md)), harden MCP servers/clients/SDKs against shell interpolation, post-symlink path traversal, and local HTTP DNS rebinding (`arXiv:2611.11104`), and validate all tool return payloads against strict Zod/JSON schemas at the BFF boundary.
- [ ] **Typed UI Component Props (Zero Raw HTML/Markdown Injection)**:
  - Never render raw LLM or MCP strings via `dangerouslySetInnerHTML` or unsanitized Markdown/iframe links.
  - Stream structured, Zod-validated data objects from the BFF into typed React components (`Generative UI`), and bind critical numbers/citations directly to verified tool-return receipts (`MCPHallu`, `arXiv:2611.07689`) rather than letting the LLM re-transcribe tables from memory.
- [ ] **End-to-End UI-to-State Dataflow Verification (`FlowCheck`, `arXiv:2608.28880`)**:
  - Verify that every interactive UI form, toggle, or action button in the Next.js frontend is wired to a real, schema-validated Server Action / API route and persists to the expected backend state (preventing "vibe-coded" dead UI controls).

---

## 6. Abuse Prevention, Cost Envelopes & Tamper-Evident Auditing

- [ ] **Per-Tenant / Per-IP Token & Cost Budgets**: Enforce sliding-window token budgets, concurrency caps, and circuit breakers (`<= 2` tool retries on MCP faults, `arXiv:2610.32555`) at the BFF middleware layer before invoking any LLM or MCP server.
- [ ] **Sealed, Replayable Flight Recorder (`NovaFabric`, `arXiv:2610.34594`)**: Log every BFF request, compiled plan, model call, MCP tool input/output, and authority epoch transition into an append-only, hash-chained audit log for post-incident diffing and replay.
- [ ] **Post-Generation Security & Migration Gates (`A.S.E 2.0`, `arXiv:2611.06294`; `arXiv:2611.08269`; `arXiv:2611.11455`)**: Branch coding-agent completions into an isolated security-audit turn and run deterministic CWE static analysis, safeguard caller-contract checks, and behavioral differential tests on all agent-authored Next.js routes and SDK migrations before deployment.
- [ ] **RAG Output-to-Chunk Overlap Caps & Coverage Budgets (`SNAPRAG`, `arXiv:2611.12241`)**: Never rely on topical safety classifiers alone (`Llama Guard 3`, `Model Armor`) to stop proprietary RAG corpus extraction; enforce deterministic output-to-chunk verbatim overlap limits (`ROUGE-L` / LCS synthesis checks) and stateful per-principal cumulative unique-chunk rate limits.

