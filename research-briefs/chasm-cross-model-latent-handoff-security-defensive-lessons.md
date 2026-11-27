<!-- License: CC BY 4.0 | Repository: https://github.com/Marontis/agentic-engineering -->

# Chasm: Cross-Model KV-Cache Latent Handoff Security & Target-Side Guard Limits (Defensive Lessons)

**Paper**: *Latent-in-the-Middle: On the Security of Cross-Model Latent Communication in Multi-Agent Systems* (`arXiv:2611.34278`)  
**Authors**: Manit Baser\*, Vyoman Jain\*, Rachel Yeo Hui Min, Xianglin Yang, Meenatchi Sundaram Muthu Selva Annamalai, & Dinil Mon Divakaran (NUS, SUTD, University of Toronto, A\*STAR)  
**Category**: `cs.CR` / `cs.AI` / `cs.LG` (2026-11-26)  
**Triage**: **Research Brief** (strictly defensive architectural security lessons, capability-vs-safety audit findings, and target-side `HandoffGuard` characterization per `output/AGENTS.md`)

---

## Why Not a Standalone Skill?

`Chasm` (`arXiv:2611.34278`) is the first systematic security audit of **cross-model KV-cache latent communication** (`Cache-to-Cache` / `C2C`, `CacheBridge`, `NVIDIA Ridge`, `MLP`, and cross-tokenizer `SwaT` mappers) across `24` forward weak-to-strong settings, `24` reverse strong-to-weak settings, and `6` cross-family settings (`Qwen3`, `Llama-3`, `Ministral-3`, plus `Meta-SecAlign-8B`). Rather than introducing a general-purpose runtime workflow that makes cross-model latent handoffs safe for open deployment, the paper establishes a **negative architectural boundary**: passing projected KV caches bypasses target-model safety and input-role prompt-injection alignment (`SecAlign`) across *all* mapper families—even **without a mapper** when an undefended sibling prefills the prompt (`0.4% -> 31.9%` `AlpacaFarm` IPI ASR)—while leaking `94.6%` of private source tokens from layer-0 caches and losing `28.0–92.4` `GSM8K` points over `3–6` benign hops. Its proposed target-side residual adapter (`HandoffGuard`) mitigates black-box unaligned-source handoffs (`J3` within `4.5 pp` of native refusal), **but** defeats indirect prompt injection only by refusing the entire task (`24.2%–94%` refusal) and fails against white-box adaptive sources (`73.3%–87.5%` ASR). Accordingly, its durable contribution is a set of **defensive trust-boundary rules and evaluation controls**, not a standalone latent-handoff deployment skill.

---

## 1. Threat Model & Evaluation Matrix

Cross-model latent MAS pipelines avoid re-tokenizing inter-agent messages by having a source agent $M_s$ prefill context $x$, projecting its KV cache $\mathcal{C}_s(x)$ into target $M_t$'s key-value space via a learned benign-calibrated mapper $f_\phi$ (`FineWeb-Edu` `500 × 1,024`-token sequences or `UltraChat` dialogues), and decoding directly on $M_t$. `Chasm` audits `3` model families (`Qwen3 14B -> 32B`, `Llama-3.2-3B -> 3.1-8B`, `Ministral-3 8B -> 14B`, plus reverse `32B -> 14B`, `8B -> 3B`, `14B -> 8B` and cross-family `Llama-3.2-3B -> Qwen3-4B`, `Qwen3-8B -> Llama-3.1-8B`, `Llama-3.2-3B -> Ministral-3-14B`) across `4` mapper architectures:
- **Linear (`NVIDIA Ridge`)** and **2-layer `MLP`** per-layer projections (`~20M–500M` parameters),
- **`CacheBridge`** (cross-layer attention routing + per-head affine maps), and
- **`SwaT`** (byte/string-level token-alignment renderer enabling cross-tokenizer KV transfer).

Safety and utility are scored on `HarmBench` (`240` text behaviors: `159` standard + `81` contextual), `StrongREJECT` (`313` prompts), `XSTest` (`250` benign look-alike prompts for over-refusal), `MMLU`, and `GSM8K`, plus `AlpacaFarm` (`208 × 8` variants) and `TaskTracker` (`3,000` items) for indirect prompt injection (`IPI`). A cross-family replication with `Gemma 4 31B` across `1.77M` verdicts confirmed `91.2%` agreement (Cohen's $\kappa = 0.79$) and replicated **`98.1%` (`782/797`)** of statistically significant findings at $p < 0.01$.

---

## 2. Five Defensive Security & Reliability Findings

### Finding 1: Benign KV Projection Erodes Refusal Without Any Attacker—and Capability Health Checks Miss It
- **Benign handoff safety drift (`No attack`)**: With an aligned source model and unmodified `HarmBench` prompts, a single cross-model KV handoff significantly increases target Attack Success Rate (`ASR`) in **`13/24` forward settings by up to `+24.6 pp`** (`Ministral SwaT Chat`: `25.0% -> 49.6%`; `7/13` exceed the standalone weaker source's own ASR!), **`15/24` strong-to-weak settings**, and up to **`+32.9 pp` cross-family** (`Qwen3-8B -> Llama-3.1-8B`).
- **Published templates (`J1`) & multi-hop switching (`J2`)**: Zero-shot published jailbreak framings (`J1`) jump by up to **`+69.2 pp` within-family** (`Llama SwaT Chat`; `+57.2 pp` `Qwen`, `+52.8 pp` `Ministral`), **`+73.0 pp` cross-family** (`14.5% -> 87.4%` role-play), and **`+82.4 pp` strong-to-weak** (`7.5% -> 89.9%`). Merely relaying unmodified requests across `<= 6` alternating aligned model switches (`J2`) raises `HarmBench` ASR significantly in **`16/24` settings by up to `+38.8 pp`** (`Ministral SwaT Chat`; `+29.2 pp` `Llama SwaT FineWeb`). *(Manuscript note: the abstract's phrasing "transfer alone raises attack success by up to 24.6 pp within a model family" refers to single-hop `No attack` `+24.6 pp` in `Table III`, whereas `J2` multi-switch transfer reaches `+38.8 pp`.)*
- **Chat calibration worsens safety (`§V-H`)**: Fitting mappers on `UltraChat` assistant dialogues rather than `FineWeb-Edu` prose increases `J1` and `J2` vulnerability in **`10/12` mapper pairs**, because chat calibration aligns conversational continuation modes (`"Sure, here is..."`) more tightly than refusal boundaries.
- **Benign multi-hop reasoning collapse (`§IV`, `Appendix C`)**: One KV handoff costs `3.0–14.4` `MMLU` points and up to **`46.0` `GSM8K` points** (`Llama SwaT FineWeb`: `88.8% -> 42.8%`), uncorrelated with benign ASR drift (Spearman $\rho = -0.40$). Over `3–6` benign hops, `GSM8K` drops significantly in **`24/24` chains from hop `3` onward**, losing **`28.0–92.4` points by hop `6`** (`16/24` chains collapse to `<= 10%` `GSM8K`; `Qwen CacheBridge` drops from `~91%` to `8.0%` `GSM8K` at hop `3` while 1-token `MMLU` stays at `71.2%`, showing single-token QA audits mask multi-step chain-of-thought collapse).

### Finding 2: Untrusted Sources (`J3`) & Differentiable Mappers (`J4`) Break Target Alignment Across `24/24` Settings
- **Untrusted / de-aligned source (`J3`)**: When a federated or third-party source agent runs an uncensored/abliterated checkpoint of the same architecture, KV transfer bypasses target alignment in **all `24/24` forward settings (`+16.3` to `+45.4 pp` `HarmBench`, `+16.0` to `+64.9 pp` `StrongREJECT`)** and **all `24/24` reverse settings (`+20.8` to `+59.2 pp`)**, while keeping target `MMLU` and `GSM8K` completely normal (`69.4% / 76.8%` on `Qwen3-32B`). Capability health checks on incoming mappers/caches cannot detect a de-aligned source.
- **Differentiable mapper surface (`J4`)**: Because projection mappers are continuous and differentiable, optimizing perturbations end-to-end through source + mapper (`40` behaviors refused by both models natively) exceeds **`90%` ASR across all three target families** (`90.0%` `Qwen`, **`92.5%` `Llama`**, `90.0%` `Ministral` via `SwaT Chat`)—shattering the standalone target optimization ceiling (`65.0%` `Qwen`, **`37.5%` `Llama`**, `42.5%` `Ministral`).

### Finding 3: Why Input-Role Prompt-Injection Defenses (`SecAlign`) Collapse Under Delegate-and-Return (`0.4% -> 44.2%`)
In a canonical delegate-and-return MAS pattern, an IPI-hardened orchestrator (`Meta-SecAlign-8B`, preference-tuned to ignore instructions inside untrusted `data`/`tool` roles) delegates reading untrusted external records to a cheaper reader (`Llama-3.2-3B-Instruct`) and decodes the returned KV cache:
- **Universal collapse across mappers (`Table V`)**: Native `Meta-SecAlign-8B` holds `AlpacaFarm` IPI ASR to **`0.4%`** (`TaskTracker`: **`2.1%`**). Receiving mapped KV caches from `Llama-3.2-3B-Instruct` spikes `AlpacaFarm` IPI ASR to **`26.2%–29.7%`** across all `4` default `FineWeb` mappers and **`44.2%` via `SwaT (Chat)`** (`TaskTracker`: **`6.7%–20.1%`**). *(Manuscript Footnote 2 note: `§VII-B` / `Table VII` evaluates a separate fit of stock `Ridge (FineWeb)` whose unguarded `AlpacaFarm` ASR is `29.6%` vs. `29.7%` in `Table V`, and `Table VI`'s `None` column reflects that separate fit relative to `Table III`.)*
- **The `No-Mapper` Smoking Gun (`0.4% -> 31.9%`)**: When undefended `Llama-3.1-8B-Instruct` (**identical architecture and tokenizer** to `Meta-SecAlign-8B`, requiring **zero mapper**) prefills the exact same role-tagged prompt and hands its raw KV cache directly to `Meta-SecAlign-8B` for decoding, `AlpacaFarm` IPI ASR jumps from **`0.4%` to `31.9%`** (`TaskTracker`: `19.7%`).
- **Architectural lesson**: Preference-tuned instruction-hierarchy defenses (`SecAlign`, `Spotlighting` role embeddings) reside in **how the hardened model's own encoder transforms untrusted data tokens into keys and values during prefill**, *not* in the decoder's weights alone. Skipping native target prefill bypasses input-role separation by construction.

### Finding 4: Projected KV Caches Are Not Privacy-Preserving Summaries & Mappers Carry Supply-Chain Backdoor Risk
- **Near-verbatim plaintext recovery (`Appendix A`)**: Projected KV caches do **not** obfuscate sensitive source prompts. Simple nearest-neighbor lookup against layer-`0` projected keys/values recovers **`94.6%` of exact tokens** and **`10/10` structured PII fields across all `500/500` private records** on default `Qwen (Ridge, FineWeb)` (`94.5%–100%` across all `Qwen` and `Ministral` mappers; `79.4%–94.1%` on `Llama`), and linear probes recover **`51%–86%`** of private tokens even if early layers are stripped.
- **Stealth mapper calibration backdoors (`Appendix B`)**: Poisoning a small triggered subset of mapper calibration data implants dormant safety-bypass triggers across `Ridge`/`MLP` (`46.7%–77.1%` triggered ASR) and `5/6` `SwaT` renderers (`72.9%–96.2%`) that **appear safer than clean mappers on standard untriggered safety audits** (`13.3%–13.8%` vs. `22.1%` clean `HarmBench` ASR) and survive benign-only target reconstruction adapters (`VReparo` ships `6/8` backdoored mappers intact).

### Finding 5: What Target-Side `HandoffGuard` Fixes—and Where It Still Fails
`Chasm` evaluates three defensive interventions (`§VII`, `Tables VI–VIII`):
1. **Refusal-calibrated mappers (`D1` — Insufficient)**: Adding refusal examples during mapper calibration cuts `J3` only partially (`51.6% -> ~32%` vs. `20.5%` native) because linear/low-depth mappers cannot synthesize refusal directions suppressed by a de-aligned source.
2. **Benign-only target reconstruction (`D2`, `VReparo` — Fails)**: Fitting a target adapter only on benign caches leaves `J3` at `26.7%–58.8%`, collapses `Llama SwaT FineWeb` `GSM8K` to `5.6%`, and preserves `6/8` mapper backdoors.
3. **Target-side `HandoffGuard` (`D3`, `p1` vs. `p2` — Scoped Black-Box Mitigation)**: A `~10M`-parameter rank-`64` residual adapter applied to pre-RoPE `K, V` tensors on the target model (`3.6%–8.2%` prefill latency overhead), trained via `32`-token teacher-forced KL divergence to match native target replies under **alternating aligned and de-aligned source checkpoints**:
   - **Success on black-box `J3` (`p1`)**: Brings `J3` `HarmBench` ASR within **`4.5 pp` of native target refusal** across all `3` families (`Ministral`: `57.1% -> 26.2%` vs. `25.0%` native; `Qwen`: `60.4% -> 23.3%` vs. `18.8%` native; `Llama`: `51.7% -> 26.7%` vs. `30.0%` native) with `<= 1.8` `MMLU` loss, up to `+10.0` `GSM8K` recovery, and `<= 1.2 pp` `XSTest` benign refusal shift. Adding input-embedding PGD (`p2`) lowers `J3` further (`9.2%–16.2%`) **at the cost of `87.4%` benign role-play false refusals on `Llama`**.
   - **Hard Limit A — Does NOT restore `SecAlign` IPI utility**: On `AlpacaFarm` IPI, `HandoffGuard` (`p1` / `p2`) reduces ASR (`29.6% -> 10.0% / 0%`) **only by refusing the entire user task** (`24.2%` / `94%` refusal on injected data; `18%` refusal on clean data under `p2`), rather than ignoring the injected instruction and completing the user's benign request as native `Meta-SecAlign-8B` does (`0.4%` ASR with full task completion).
   - **Hard Limit B — Broken by white-box guard-aware sources**: A `300`-step LoRA source fine-tuned with gradient access to `HandoffGuard` rebounds to **`73.3%–87.5%` ASR** while keeping last-token linear refusal-probe scores deceptively high (`0.71–0.81`, evading activation refusal monitors via forced affirmative openers).

---

## 3. Defensive Engineering Takeaways

1. **Never cross trust or untrusted-data boundaries via KV-cache projection**: Restrict latent KV handoffs (`C2C`, `CacheBridge`, `Ridge`, `SwaT`, `LatentMAS`, `ConvRSI`) strictly to **single-operator, mutually attested, homogeneous-trust pipelines processing trusted internal inputs** and cap chains to **`<= 2` hops** unless multi-hop reasoning (`GSM8K`, not just 1-token `MMLU`) is verified per hop.
2. **Always prefill untrusted external data natively through the hardened target model**: Whenever an agent reads untrusted web pages, emails, tool outputs, or third-party files, return **natural-language text + verbatim primary source spans inside typed role delimiters** so the hardened orchestrator's own encoder (`SecAlign` / `Spotlighting`) builds its own KV cache. Never decode a reader sub-agent's KV cache directly.
3. **Treat projected KV caches as plaintext for DLP and privacy**: Apply identical PII redaction, tenant isolation, and encryption-in-transit rules to KV tensors as to raw token strings (`94.6%` layer-0 token recovery).
4. **Pin mapper provenance and deploy `HandoffGuard (p1)` strictly as defense-in-depth**: Treat mapper checkpoints as executable supply-chain artifacts (verifying calibration-dataset lineage and cryptographic hashes rather than untriggered safety-benchmark scores), and attach a target-side `HandoffGuard (p1)` residual adapter only against **non-adaptive/black-box** source drift—never as a substitute for native target prefill on untrusted data or against untrusted white-box peers.

---

## Cross-References

- **Rules**:
  - [`multi-agent-coordination.md`](../rules/multi-agent-coordination.md) — `"DO: Use natural language as the inter-agent interface"` and `"DON'T: Delegate untrusted evidence reading to a weaker sub-agent without forwarding primary source records to the orchestrator or verifier"`
  - [`agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md) — `"DO: Bind cryptographic provenance at decode boundaries and verify both data and context lineage at critical sinks"` and `"DON'T: Place compacted history summaries in the user-request authorization slot or rely on prose-only summary tags"`
  - [`skill-system-design.md`](../rules/skill-system-design.md) — `"DO: Validate skill provenance before adding to library"`
  - [`agent-evaluation-quality.md`](../rules/agent-evaluation-quality.md) — `"DO: Enforce owner-authority boundaries, action-deflection cases, and reach-adjusted Effective ASR when evaluating indirect prompt injection defenses"`
- **Spec Templates**:
  - [`adk-multi-agent-a2a.spec.md`](../specs/adk-multi-agent-a2a.spec.md) — Inter-agent transport, untrusted-reader delegation, and trust-boundary enforcement
  - [`agent-sandbox.spec.md`](../specs/agent-sandbox.spec.md) — Taint/provenance isolation across agent boundaries
- **Related Skills**:
  - [`mcp-decode-provenance-binding`](../skills/mcp-decode-provenance-binding/SKILL.md) — Binding provenance tags at decode boundaries so untrusted external content cannot bypass sink checks
  - [`witnessed-request-compaction-gate`](../skills/witnessed-request-compaction-gate/SKILL.md) — Preserving input-role authorization separation across intermediate representations
- **Research Briefs**:
  - [`heterofold-cross-family-kv-transfer.md`](heterofold-cross-family-kv-transfer.md) — Cross-family KV-cache transfer mechanics whose security surface `Chasm` audits
  - [`convrsi-parallel-convolutional-latent-mas.md`](convrsi-parallel-convolutional-latent-mas.md) — Parallel latent-state multi-agent communication within trusted single-model loops
  - [`skillmem-compact-external-skill-memory-latent-mas.md`](skillmem-compact-external-skill-memory-latent-mas.md) — Role-conditioned latent skill prefixes for trusted latent MAS
  - [`weakest-agent-delegation-safety-collapse.md`](weakest-agent-delegation-safety-collapse.md) — Text-channel analogue (`arXiv:2611.17520`) showing weak sub-agent summarization launders forged records unless primary sources are re-read by the strong orchestrator
  - [`text-similarity-guardrail-limits-agent-relays.md`](text-similarity-guardrail-limits-agent-relays.md) — Limits of surface-similarity guardrails across multi-hop agent relays (`arXiv:2611.21520`)

## Sources

- Baser, E., Jain, S., Yeo, W. J., Yang, R., Annamalai, M. S. M. S., & Divakaran, A. (2026). *Latent-in-the-Middle: On the Security of Cross-Model Latent Communication in Multi-Agent Systems*. `arXiv:2611.34278`.
