# Agent Authenticator: Passkey-Grade, Hardware-Bound Authentication for AI Agents

> **Source**: [arXiv:2611.19536](https://arxiv.org/abs/2611.19536) — Harish Santhanalakshmi Ganesan (Independent Researcher, November 2026)
> **Praxis Source ID**: `src:2611-19536v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

Although the abstract presents **Agent Authenticator (`AA`)** as a complete authentication protocol over MCP, OAuth, ID-JAG, Git, and SSH, reading the full manuscript reveals three reasons it belongs as a **Research Brief** rather than an executable `SKILL.md` under [`skill-design-methodology`](../skills/skill-design-methodology/SKILL.md) and [`AGENTS.md`](../AGENTS.md):

1. **Unimplemented Design Specification with Zero Measurements (`Section 1` & `Section 10`)**: The author explicitly states that *no reference implementation has been built yet* (Linux `TPM 2.0`, macOS `Secure Enclave`, and confidential-computing prototypes are future work) and reports **zero latency, usability, or deployment measurements**. Furthermore, the security analysis in `Section 8` is explicitly informal (symbolic verification in `Tamarin` is deferred), and the five incident outcomes in `Table 4` are labeled *"qualitative judgments derived from the incident reports and the design, not measurements."* Per established repository convention (cf. [`commit-boundary-authorization-entity-resolution.md`](commit-boundary-authorization-entity-resolution.md)), unimplemented protocol proposals are recorded as research briefs rather than skills.
2. **Unstandardized Relying-Party Extensions (`Section 6.1` & `Section 10`)**: Full `AL2`/`AL3` assertions (`AgentData` carrying `mb` and `ha` flags plus `typ: "agent-mandate+jwt"`) require external relying parties (`github.com`, `registry.npmjs.org`) and enterprise IdPs to adopt new verification logic. For services that do not yet accept agent assertions, `Section 6.1` falls back to brokering legacy tokens at assurance level `AL1` without exposing them to the model—which reduces directly to our empirically probed [`vault-mediated-credential-injection`](../skills/vault-mediated-credential-injection/SKILL.md) (`arXiv:2609.33371`) skill.
3. **Strong Complementarity with Implemented Skills**: Adjacent subtasks—keeping bearer API secrets out of LLM context ([`vault-mediated-credential-injection`](../skills/vault-mediated-credential-injection/SKILL.md)), hardware-attested out-of-band human confirmation with a trusted display ([`out-of-band-hitl-verification`](../skills/out-of-band-hitl-verification/SKILL.md), `arXiv:2610.35835`), server-side MCP permission enforcement ([`mcp-zero-trust-tool-authorization`](../skills/mcp-zero-trust-tool-authorization/SKILL.md), `arXiv:2609.22573`), multi-hop delegation attenuation ([`multi-hop-delegation-auth-propagation`](../skills/multi-hop-delegation-auth-propagation/SKILL.md), `arXiv:2611.07050`), and transparency-logged sealed run records ([`sealed-replayable-agent-audit-log`](../skills/sealed-replayable-agent-audit-log/SKILL.md), `arXiv:2610.34594`)—already have empirically validated procedures in this knowledge base.

---

## Problem Diagnosis: Four Recurring Credential Failure Classes

Ganesan synthesizes five documented `2025–2026` developer and coding-agent security incidents alongside ecosystem-wide secret-sprawl measurements:

- **Ecosystem Secret-Sprawl Measurements (Cited Third-Party Studies, `Section 3.1`)**:
  - Across **`5,205` open-source MCP servers** (Astrix Security, 2025), **`88%`** require credentials, **`53%`** rely on static API keys or personal access tokens (`PATs`), and only **`8.5%`** use OAuth.
  - Across public GitHub in `2025` (GitGuardian *State of Secrets Sprawl 2026*), scanners detected **`28.65 million`** newly leaked secrets, an **`81%` rise** in leaked AI-service secrets, and **`24,008` secrets inside MCP configuration files** (**`2,117` still valid**).
  - During the **`Nx "s1ngularity"` supply-chain attack (`2025`)**, malicious npm package versions harvested **`2,349` credentials from `1,079` developer machines**, actively invoking locally installed AI CLIs to search disk for secrets.
- **Five Motivating Incidents (`Table 1`) & Four Failure Classes (`Section 3.2`)**:
  1. **GitHub MCP prompt injection (`2025`)**: Malicious public issue steered an agent holding a broad multi-repo PAT to exfiltrate private repository contents into a public PR (`F3 Over-broad scope`).
  2. **Comment and Control (`2026`)**: Crafted PR titles hijacked CI-hosted coding agents and leaked ambient repository secrets through the code host (`F1 Ambient bearer secrets`).
  3. **Coding-agent exploits (`2025–2026`)**: Crafted branch names exfiltrated tokens and repository config files disabled in-process trust prompts and write sandboxes (`F2 In-agent controls`).
  4. **Nx `s1ngularity` (`2025`)**: Co-resident install scripts read plaintext tokens and keys on disk (`F1 Ambient bearer secrets`).
  5. **Shai-Hulud worm (`2025–2026`, `400+` npm packages)**: Self-propagating worm stole long-lived npm and GitHub publish tokens usable from any host (`F1` + `F3` + `F4 Missing attribution`).

---

## Proposed Architecture: Passkey Properties Adapted for Autonomous Agents

`Agent Authenticator` separates the untrusted **agent** (model + spawned subprocesses, holding zero keys) from the **agent runtime** (harness owning TLS sockets) and an out-of-process **Agent Authenticator (`AA`) daemon** running in a distinct privilege domain against four adversary classes: content injectors (`A1`), same-host co-resident user-privilege code (`A2`), network/origin attackers (`A3`), and compromised cloud sandbox images (`A4`; host root/kernel compromise, physical hardware attacks, compromised IdPs, and malicious human approvers are out of scope):

1. **Four Isolated Hardware Key Roles & Normalized `EAT` Assurance Levels (`Section 5.2`, `Table 2`)**:
   - *Approver key*: Human owner's standard WebAuthn passkey.
   - *AA identity key*: Hardware-bound key for the lifetime of the laptop or enclave.
   - *Agent credential key*: One non-exportable hardware key **per `(agent, relying_party)`** (valid until mandate expiry/revocation locally, or **one task** in cloud; never copied when moving a session from laptop to cloud).
   - *Evidence key*: Separate hardware key rotated per epoch for forward-secure action logging.
   - To shield relying parties from vendor-specific attestation formats (`TPM 2.0`, `Secure Enclave` / `App Attest`, `Android StrongBox`, `AMD SEV-SNP`, `Intel TDX`, `AWS Nitro`, `Arm CCA`), a `RATS` verifier (`RFC 9334`) appraises platform evidence into an `RFC 9711` Entity Attestation Token (`EAT`) carrying a four-tier **Assurance Level**: **`AL3`** (confidential-computing TEE isolating both keys and measured agent runtime), **`AL2`** (dedicated secure hardware key storage such as `TPM 2.0` / `Secure Enclave` without host-OS isolation), **`AL1`** (software platform keystore, cloud workload identity, or brokered legacy tokens), and **`AL0`** (raw software keys).
2. **Runtime-Enforced Origin Binding (`Section 5.1` & `5.4`)**:
   - Mirroring the browser's role in WebAuthn, the **agent runtime extracts the target origin and relying-party (`RP`) identifier from the live TLS connection**, never from model-supplied arguments. Even under prompt injection (`A1`), the agent cannot induce the `AA` to sign an assertion for an unprovisioned origin or replay an assertion at an attacker-controlled server (`A3`).
3. **Passkey-Signed `RAR` Mandates & `AgentData` Step-Up Ceremonies (`Sections 5.3–5.5`)**:
   - During registration, the human signs a structured `typ: "agent-mandate+jwt"` (`jkt` agent key thumbprint per `RFC 7638`, `aa.min_al`, permitted `rps`, fine-grained `RFC 9396` Rich Authorization Request `authorization_details` such as `push` restricted to `refs: ["agent/fix-*"]`, `step_up` actions `["merge", "publish", "delete"]`, `delegable` boolean, and `exp`) using an ordinary WebAuthn assertion over the mandate hash.
   - Each authentication signs an `AgentData` structure containing runtime-supplied `RP` ID + origin, fresh RP challenge, credential ID, mandate hash, current `AL`, a strictly monotonic signature counter (cloning detection), requested action, and two flags replacing WebAuthn `UP`/`UV`: **`mb`** (*mandate-bounded*) and **`ha`** (*human-approved*, accompanied by a single-use cross-device WebAuthn signature over `SHA256(AgentData)`). Sub-delegation requires `delegable: true` and strict monotonic narrowing (`child ⊆ parent` in `rps`, `actions`, `exp`, and `child.min_al >= parent.min_al`), while revocation subscribes to OpenID Shared Signals (`CAEP`/`RISC`).
4. **Incremental Protocol Profiles & Hash-Chained `SCITT` Action Records (`Sections 6–7`, `Table 3`)**:
   - Deploys over existing auth flows: **MCP** (`DPoP` `RFC 9449` + workload-identity client provider), **Enterprise IdP `ID-JAG`** (`RFC 8693` Token Exchange with the user as `subject` and the `AA` assertion as the `actor` token, followed by `RFC 7523` JWT grant), **OAuth APIs** (`RAR` + `DPoP`), **Git over HTTPS** (`git credential helper` minting ephemeral per-remote tokens with zero tokens on disk), **Git over SSH** (`ssh-agent` with FIDO-style SSH signatures carrying flags and mandate hash), **Cloud** (workload identity federation), and **Package Registries** (trusted publishing gated on `ha` step-up).
   - Every allowed or denied signing request writes a hash-chained record signed by the `AA` evidence key; assertions carry the current chain head so relying parties act as independent witnesses, with periodic registration to a `SCITT` (`RFC 9943`) transparency service and signed heartbeats to expose daemon tampering.

---

## Defensive Takeaways for Agent Infrastructure

1. **Upgrade Vault Proxies from Bearer Secrets to `DPoP` / Hardware-Bound Keys Where Supported**: Keeping static PATs inside a proxy ([`vault-mediated-credential-injection`](../skills/vault-mediated-credential-injection/SKILL.md)) prevents prompt-context leakage (`F1` partial) but still leaves bearer tokens usable if intercepted or over-scoped (`F3`). Bind issued OAuth/MCP access tokens to non-exportable `TPM` / `Secure Enclave` / TEE keys via `DPoP` (`RFC 9449`) and serve Git/SSH through memory-only `git credential helper` and `ssh-agent` sockets so co-resident install scripts (`Nx s1ngularity`) find zero harvestable tokens on disk.
2. **Derive Request Origin from the Live TLS Socket in the Harness, Never from Tool Arguments**: Enforce WebAuthn-style origin binding in the runtime network layer so a prompt-injected model cannot steer credentialed assertions toward attacker-controlled endpoints.
3. **Separate Routine Mandate-Bounded Calls (`mb`) from Cross-Device Passkey Step-Up (`ha`)**: Use `RFC 9396` `authorization_details` (e.g., confining autonomous Git pushes to `agent/fix-*` branches on named repositories) for routine autonomous work while requiring payload-bound out-of-band human approval ([`out-of-band-hitl-verification`](../skills/out-of-band-hitl-verification/SKILL.md)) for irreversible `merge`, `publish`, and `delete` operations—noting that desktop process-lineage checks remain software controls defeatable by local `root`/admin adversaries unless the agent runs inside an attested microVM or enclave (`AL3`).

## Related Artifacts

- [`vault-mediated-credential-injection`](../skills/vault-mediated-credential-injection/SKILL.md) — Implemented boundary proxy & 16 black-box probes keeping bearer API secrets out of model vocabulary (`arXiv:2609.33371`)
- [`out-of-band-hitl-verification`](../skills/out-of-band-hitl-verification/SKILL.md) — Formal impossibility proofs & hardware-attested trusted-display HITL (`Countersign`, `arXiv:2610.35835`)
- [`mcp-zero-trust-tool-authorization`](../skills/mcp-zero-trust-tool-authorization/SKILL.md) — Server-side DNF permission enforcement for HTTP MCP (`arXiv:2609.22573`)
- [`multi-hop-delegation-auth-propagation`](../skills/multi-hop-delegation-auth-propagation/SKILL.md) — Origin-private asymmetric delegation commitments and monotonic scope attenuation (`arXiv:2611.07050`)
- [`sealed-replayable-agent-audit-log`](../skills/sealed-replayable-agent-audit-log/SKILL.md) — Tri-proof DSSE, RFC 3161 TSA, and Merkle transparency sealing (`arXiv:2610.34594`)
- [`rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md) — `"DO: Bind agent service authentication to per-relying-party hardware keys, TLS-derived runtime origins, and passkey-signed mandates"` and `"DON'T: Let API credentials enter model context or agent-visible state"`
