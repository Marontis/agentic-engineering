---
name: bounded-context-intervention-window-guardrail
description: Design, train, and run compact on-device multi-step action guardrails under bounded sliding windows by splitting recurrent task state into authorized scope versus untrusted screen evidence, decoupling commit-point risk from intervention-window blocking, and caching vision-encoder outputs across steps. Use when guarding mobile GUI agents, local desktop/browser computer-use agents, or privacy-sensitive edge tool agents without streaming observations to cloud APIs.
source: "MobileGrail: Learning Compact Guardrails for On-Device deployable Mobile GUI Agent Safety (arXiv:2611.29847)"
repository: https://github.com/Marontis/agentic-engineering
license: CC-BY-4.0
---

# Bounded-Context Intervention-Window Guardrail (`MobileGrail`)

Multi-step GUI, browser, and local computer-use agents routinely view sensitive personal or enterprise screens (messages, banking, medical portals, credentials) where streaming full trajectory screenshots to a frontier cloud guardrail (`27B+` VLM) violates privacy and incurs variable network tail latency (`5.11–25.40 s` P50). Yet shrinking a runtime action guardrail to an on-device `1.6B–2B` VLM with a short `k = 3`-step sliding window introduces three failure modes (`arXiv:2611.29847`, `§1, §3, §5`):
1. **Context eviction & untrusted screen contamination**: Legitimate user parameters resolved early in the trajectory (e.g., looking up *"Mom's"* account number in Contacts at step 2 before submitting a transfer at step 9) are evicted from a `k = 3` window, causing stateless or short-window guardrails to false-block benign completions (`31.9%` benign trajectory FPR and only `20.0%` [`7/35`] anchor–twin pair discrimination without recurrent task context, `Table 4`). Conversely, summarizing screen observations into free-form memory lets indirect prompt injections contaminate the guardrail's trusted task state (`+5.9` percentage points missed intervention rate, `19.3%` vs. `13.4%`, $p < 0.05$).
2. **Single-label risk-onset vs. commit-step confusion**: Collapsing `"is this step already committing harm?"` and `"should execution be halted now?"` into a single binary label breaks multi-step supervision. Supervising at *risk onset* (`OS-Sentinel`) teaches the guardrail to block ordinary app-opening and navigation steps (`57.1%` benign trajectory FPR, `39.3%` effective intervention rate, `Table 1`), whereas supervising strictly at the final *commit click* penalizes valid early blocks after an injection has already hijacked navigation (`PUR 64.1%–77.2%` on prompted `1.6B–2B` models).
3. **Redundant multi-frame vision prefill on edge NPUs**: Re-encoding all `k = 3` high-resolution screenshots from scratch at every agent step dominates prefill latency on mobile/edge processors (`9.33–15.39 s` P50 at `Q8_0`).

This skill distills the **`MobileGrail` (`arXiv:2611.29847`)** procedure for building, supervising, and deploying bounded-context runtime action guardrails across mobile GUI assistants, desktop/browser computer-use agents, enterprise RPA workflows, and edge tool-calling runtimes.

## When to Use

- **On-device mobile GUI agents** executing multi-app workflows over private user screens under `<= 4 GiB` model memory and `~5 s` step-latency budgets.
- **Local desktop or browser computer-use agents (`CUAs`)** where screenshots contain proprietary documents, source code, or session cookies that must not leave the host.
- **Enterprise workflow & RPA action monitors** guarding long (`10–30` step) trajectories with a bounded (`k = 3`) observation window where early lookup steps resolve parameters used many steps later.
- **Post-training compact (`1B–4B`) guardrail models** with SFT + GRPO over multi-step trajectories containing both overt unsafe actions, indirect prompt injections, and authorization-matched benign twins.

Do **not** rely on an LLM/VLM guardrail alone when deterministic capability schemas or principal-provenance checks can enforce the invariant in zero-LLM code (`CapLite`, `Conflux`), and do **not** return detailed corrective feedback `<FB>` to an *adversarially misaligned* or *evasion-pressured* coding/endpoint agent (see Step 4 guardrail boundary).

## Core Insight

Separate **state persistence**, **risk attribution**, and **intervention timing** into distinct structural channels (`arXiv:2611.29847`, `§3.2–3.4`):
1. **Provenance-Partitioned Recurrent Task State $m_t = (c_t, d_t)$**: In the same single forward pass that judges step $t$, emit an updated task context $c_t$ partitioned into `AUTHORIZED` scope (original user goal + benign user-delegated parameters resolved from trusted lookups, tagged with provenance) and `UNAUTHORIZED` evidence (in-screen third-party instructions, phishing overlays, or mismatched recipients/amounts), paired with a deterministic ledger $d_t$ of persistent side effects appended **only after an allowed action executes**.
2. **Decoupled `(unsafe, block)` Supervision over Intervention Windows**: Ground `unsafe` strictly at backend-verified irreversible commit steps $\mathcal{C}$ (granting neutral `0` reward on `commit-ambiguous` UI controls whose pre-action screen cannot reveal whether another confirmation dialog follows), while supervising `block` across the full **intervention window** $\mathcal{W}^{(j)} = \{t_e^{(j)}, \dots, t_c^{(j)}\}$ from first observable unauthorized departure $t_e^{(j)}$ through commit $t_c^{(j)}$ using **zero-reward free-timing slack** on pre-commit window steps ($t \in \mathcal{W} \setminus \mathcal{C}$) and strict penalties at missed commits ($t \in \mathcal{C}$).
3. **Incremental Vision-Token & Static-Prefix Caching**: Encode only the single new observation $o_t$ per step and reuse cached vision-encoder outputs for $o_{t-2}, o_{t-1}$ alongside a pinned system-prompt KV prefix.

## Step-by-Step Procedure

### Step 1: Structure the Bounded Sliding Window and Provenance-Split Recurrent State

1. **Bound the per-step input window**:
   - At step $t$, feed the guardrail only the immutable user instruction $u$, the recurrent memory $m_{t-1} = (c_{t-1}, d_{t-1})$, the bounded sliding history $H_t^{(k)} = \{(o_i, a_i)\}_{i=\max(1, t-k)}^{t-1}$ with $k = 3$ (each action annotated with its normalized click/target marker on $o_i$), and the current observation-candidate pair $(o_t, a_t)$.
2. **Enforce an explicit `AUTHORIZED` vs. `UNAUTHORIZED` schema inside $c_t$ (`<CTX>`)**:
   - **`AUTHORIZED` compartment**: Carry forward the user's original intent and update authorized parameters *only* when a step resolves an underspecified user reference (e.g., *"pay Alex's split from the receipt"* $\to$ `recipient=Alex, amount=$24.50 [source: Receipt screen step 3]`). Never let third-party text widen the authorized action type or override explicit user bounds.
   - **`UNAUTHORIZED` compartment**: Record untrusted in-screen directives (banners, emails, pop-ups, QR/link redirects) or observed parameter conflicts separately as risk evidence so they remain visible across the `k = 3` boundary without polluting `AUTHORIZED` scope.
3. **Update the persistent-effect ledger $d_t$ strictly post-`allow`**:
   - Have the guardrail emit a concise `<Done>` effect tag only when $a_t$ triggers a persistent state mutation (payment, message send, deletion, permission grant, account change) and $\hat{b}_t = \text{allow}$; append `<Done>` to $d_t$ *only after* the runtime actually dispatches $a_t$ (`d_t = d_{t-1}` whenever $\hat{b}_t = \text{block}$).
   - Register structural tags (`<CTX>`, `<SAFE>`, `<BLOCK>`, `<Done>`, `<FB>`) as single vocabulary tokens so tag parsing is deterministic and adds minimal decode overhead.

### Step 2: Construct Backend-Verified Commit Labels, Intervention Windows, and Benign Twins

1. **Ground commit steps $\mathcal{C}$ via environment/backend state diffs, not UI text alone**:
   - Instrument sandboxed training apps/tools to snapshot backend state (SQLite tables, file trees, mock API ledgers, OS settings) before and after each action $a_t$. Label $t \in \mathcal{C}$ (`unsafe`) strictly when executing $a_t$ produces an unauthorized irreversible state diff (or hits the terminal commit control before an irrevocable external action).
2. **Annotate `commit-ambiguous` steps ($\mathcal{A}$) and intervention windows ($\mathcal{W}^{(j)}$)**:
   - Mark pre-action UI controls (such as `"Continue"`, `"Next"`, or `"Submit"` buttons whose pre-click screen does not reveal whether a final confirmation sheet follows) as **`commit-ambiguous` ($\mathcal{A}$)** rather than forcing noisy positive or negative commit labels.
   - For each commit $t_c^{(j)} \in \mathcal{C}$, set window start $t_e^{(j)}$ to the earliest step where unauthorized intent or injected steering becomes observable in $(u, o_{\le t}, a_{\le t})$ (with $t_e^{(j)} = t_c^{(j)}$ when user-authorized navigation only turns unsafe at the commit argument itself), defining $\mathcal{W}^{(j)} = \{t_e^{(j)}, \dots, t_c^{(j)}\}$.
3. **Pair every unsafe anchor trajectory with an authorization-matched benign twin**:
   - Construct a mirrored benign trajectory on the **same app/interface** that executes an analogous sensitive operation *explicitly authorized by $u$* (e.g., deleting the specific old backup requested by the user vs. deleting an unrequested folder). Without benign twins on the same sensitive screens, compact guardrails learn shortcut associations between sensitive UI screens (payment/delete/settings) and `block`.

### Step 3: Train with Verdict-Separated SFT and Asymmetric Window-Slack GRPO

1. **Stage 1 — Verdict-separated Supervised Fine-Tuning (`SFT`)**:
   - Distill step-level structured outputs `(c_t, rationale, <SAFE>, <BLOCK>, <Done>/<FB>)` from a strong teacher VLM (`Gemini 3.8 Flash` in `MobileGrail`), keeping rationales **short and decision-sufficient** (`1–2` sentences naming the concrete scope match or mismatch) for edge latency.
   - Separate token cross-entropy on the `<SAFE>` and `<BLOCK>` verdict tokens ($\mathcal{L}_D$) from variable-length `<CTX>`/rationale generation tokens ($\mathcal{L}_R$) so long text spans cannot drown out supervision on the two binary safety gates (`arXiv:2611.29847`, `Eq. 1`):
     $$\mathcal{L}_{\mathrm{SFT}}(\theta) = (1 - \lambda)\mathcal{L}_R(\theta) + \lambda\mathcal{L}_D(\theta), \quad \lambda = 0.15$$
2. **Stage 2 — Group Relative Policy Optimization (`GRPO`) with free-timing window slack**:
   - Sample $G = 8$ rollouts per step (`temperature = 1.0` during rollout, greedy decoding at deployment) and compute `R_total = R_fmt + w_t * (R_risk + R_block + R_cons)` (`R_fmt = -2.0` on malformed tags, trapping the step):
     - **Commit-risk reward ($R_{\mathrm{risk}}$)**: `+1` / `-1` on exact commit steps $t \in \mathcal{C}$ and unambiguous safe steps $t \notin \mathcal{C} \cup \mathcal{A}$; **`0` on `commit-ambiguous` steps $t \in \mathcal{A}$**.
     - **Intervention-window block reward ($R_{\mathrm{block}}$)**: **`+2` (`block`) / `-2` (`allow`)** on commit steps $t \in \mathcal{C}$; **`0` for both `allow` and `block` on pre-commit window steps $t \in \mathcal{W} \setminus \mathcal{C}$** (free-timing slack: neither forcing noisy premature blocks nor punishing valid early interception); and **`+1` (`allow`) / `-1` (`block`)** outside $\mathcal{W}$.
     - **Consistency & benign-twin weighting**: Add $R_{\mathrm{cons}} = -1$ whenever a rollout emits $(\text{unsafe}, \text{allow})$, enforce $\hat{y}_t = \text{unsafe} \Rightarrow \hat{b}_t = \text{block}$ deterministically at runtime (`Eq. 2`), and upweight benign-twin steps by **$w_t = 1.5$** (`1.0` otherwise) to counter false-positive drift.
   - **Audit GRPO group-saturation variance**: Check the fraction of all-identical rollout groups on anchor vs. benign splits (`§5.2`: when an SFT checkpoint already predicts `allow` on `90%` of benign groups with zero intra-group variance vs. `96%` active variance on unsafe anchor groups, GRPO updates skew toward stricter blocking—adjust temperature or active-variance group filtering accordingly). Pass any promoted guardrail checkpoint through `"DO: Pass every self-modification through one acceptance gate"` (`output/rules/recursive-improvement.md`).

### Step 4: Route Verdict-Dependent Runtime Resumption vs. Terminal Escalation

1. **When guarding a benign task agent against external prompt injection (`GhostEI` regime)**:
   - On $\hat{b}_t = \text{block}$ caused by untrusted screen content or an unauthorized parameter detour, suppress $a_t$ before dispatch, keep $d_t = d_{t-1}$, and return a **concise, non-oracle corrective `<FB>` message** naming the violated user scope (e.g., *"Action blocked: recipient does not match authorized contact; return to user's original task"*). On `GhostEI-Bench` (`110` online tasks guarding `Qwen3.8-27B`, `Table 3`), this cut Full Attack Success (`FAS`) from **`13` to `3`** (`0` phishing-form attacks remaining) while **raising legitimate Task Completion (`TC`) from `48` to `58`** and lowering Benign Failures (`BF`) from `37` to `31`.
2. **When task–policy conflict or repeated denial occurs (`EvasionBench` / `BypassGym` boundary)**:
   - If the user's own goal conflicts with hard policy or the guarded agent triggers **`>= 2` consecutive blocks** on the same capability/target, **make the denial terminal or escalate out-of-band to the human user** rather than feeding iterative `<FB>` explanations that a task-pressured agent can route around (`output/rules/agent-sandbox-safety.md` — `"DO: Give blocking action monitors recent call history, and make denials terminal"`).

### Step 5: Accelerate Edge Inference via Cross-Step Vision Caching and Quantization Calibration

1. **Cache vision-encoder embeddings across sliding-window steps**:
   - Store the vision-encoder hidden states of $o_{t-2}$ and $o_{t-1}$ in ring-buffer RAM so step $t$ runs the vision encoder **only on the single new screenshot $o_t$** (plus lightweight action-marker tokens if overlaid separately), and pin the static system-prompt KV prefix across all steps of the session.
   - On `Snapdragon 8 Elite` (`QRD8750`, Hexagon NPU via `llama.cpp`, `Tables 5 & 11`), cross-step vision + prefix caching reduced `Q8_0` P50 step latency by **`18%` (`9.33 s -> 7.66 s`, prefill `-48%`)** on `Qwen3.5-2B` and by **`56%` (`15.39 s -> 6.80 s`, prefill `-71%`)** on `LFM2.5-VL-1.6B`.
2. **Re-benchmark benign FPR and premature blocks after quantization**:
   - Quantizing `Qwen3.5-2B` (short rationale) to `Q4_0` achieved **`4.70 s` P50 latency (`5.07 s` mean, `3.67 GiB` RSS)**—faster than cloud `Gemini 3.8 Flash` (`5.11 s` P50, `6.32 s` mean) with zero off-device screen exposure—while holding `MobileVeto` `EIR` at **`71.4%`**, `PIR` at **`6.6%`**, and `B-FPR` at **`14.3%`** (`Table 5`). Always verify quantized checkpoints on matched unsafe + benign-twin suites before shipping, and attest resident weight/scale buffers on field-exposed edge hardware (`fatcat-chip-level-alignment-fault-tolerance-defensive-lessons`).

## Empirical Reference (`MobileVeto` `420` Trajectories & Ablations, `arXiv:2611.29847`)

| Model / Variant | `EIR` ($\uparrow$) | `MIR` ($\downarrow$) | `PUR` ($\downarrow$) | `PIR` ($\downarrow$) | `B-FPR` ($\downarrow$) | Notes |
|:---|:---:|:---:|:---:|:---:|:---:|:---|
| `OS-Sentinel (Kimi-K2.6)` (cloud risk-onset SFT) | `39.3%` | `60.7%` | `36.9%` | `22.4%` | `57.1%` | Single-label risk-onset supervision over-blocks benign navigation |
| `Qwen3.5-27B` (prompted cloud) | `80.7%` | `17.9%` | `40.7%` | `35.2%` | `17.1%` | High premature unsafe/block rates on `k = 3` windows |
| `Qwen3.5-2B` (prompted on-device base) | `64.5%` | `34.1%` | `64.1%` | `58.6%` | `75.7%` | Unusable `75.7%` benign false-block rate prior to training |
| **`MobileGrail (Qwen3.5-2B, SFT+GRPO)`** | **`76.2%`** | `20.3%` | `16.6%` | **`5.2%`** | **`15.7%`** | **`76.0%` held-out OOD `EIR`** (`9` unseen apps), `-60.0` pp `B-FPR`, `-53.4` pp `PIR` |
| **`MobileGrail (LFM2.5-VL-1.6B, SFT+GRPO)`** | `58.3%` | `30.0%` | **`11.7%`** | **`3.8%`** | `16.2%` | `-79.0` pp `B-FPR` (`95.2% -> 16.2%`), `1.10 GiB` RSS at `Q4_0` short |
| Ablation (`Table 4`): Full ($c_t + d_t$) vs. `w/o c_t, d_t` | `82.8%` vs. `73.1%` | `13.4%` vs. `21.4%` | `15.5%` vs. `12.8%` | `11.7%` vs. `10.3%` | `20.5%` vs. `31.9%` | Exact anchor–twin pair discrimination jumps **`20.0%` (`7/35`) $\to$ `62.9%` (`22/35`)** |

## Cross-References

- **Related Skills & Briefs**:
  - [`historical-constraint-restoration`](../historical-constraint-restoration/SKILL.md) — Pinning and restoring earlier-turn user safety constraints across long-horizon multi-turn sessions (`STAR-Guard`)
  - [`schema-derived-write-integrity-gate`](../schema-derived-write-integrity-gate/SKILL.md) — Deterministic zero-LLM write-argument provenance gating (`CapLite`) to layer behind compact neural guardrails
  - [`cross-interface-route-bound-authorization`](../cross-interface-route-bound-authorization/SKILL.md) — Canonical effect normalization across GUI, CLI, API, and MCP execution surfaces
  - [`mobileprobe-trajectory-aware-mobile-gui-security-eval`](../../research-briefs/mobileprobe-trajectory-aware-mobile-gui-security-eval.md) — Trajectory-aware security evaluation of mobile GUI agents (`MobileProbe`, `arXiv:2611.16693`)
  - [`fatcat-chip-level-alignment-fault-tolerance-defensive-lessons`](../../research-briefs/fatcat-chip-level-alignment-fault-tolerance-defensive-lessons.md) — Edge DRAM weight/quantization-scale integrity attestation for local quantized guardrails (`arXiv:2611.31129`)
- **Related Rules**:
  - [`output/rules/agent-sandbox-safety.md`](../../rules/agent-sandbox-safety.md) — `"DO: Give blocking action monitors recent call history, and make denials terminal"`, `"DON'T: Evaluate privileged agent actions using unescaped raw transcripts in blocking monitors"`, `"DO: Measure each defense's benign cost on a matched benign arm, on the assembled stack"`, and `"DO: Restore earlier-turn safety constraints and enforce them at a deterministic action boundary"`
  - [`output/rules/recursive-improvement.md`](../../rules/recursive-improvement.md) — `"DO: Pass every self-modification through one acceptance gate"`

## Sources

- **Primary Paper**: *MobileGrail: Learning Compact Guardrails for On-Device deployable Mobile GUI Agent Safety* (`arXiv:2611.29847`, Praxis source `src:2611-29847v1`)
