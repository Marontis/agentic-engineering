# Scaling Adaptive Prompt Injection Attacks with Agent Swarms

> **Source**: [arXiv:2611.11861](https://arxiv.org/abs/2611.11861) — Alexey Kurakin, Vishal Karande, Alex Bie, Chongyang Shi, Shuang Song, Saeed Mahloujifar, Abdullatif Köksal, Jamie Hayes, Juliette Pluto, Yinghao Sun, Kamalika Chaudhuri (2026)
> **Praxis Source ID**: `src:2611-11861v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Why Not a Skill?

This paper designs and scales an offensive multi-agent red-teaming swarm (`Agentic Optimizer`) that coordinates `16` attacker agents (`N = 8` teams $\times$ `M = 2` agents) with shared leaderboards, team whiteboards, and a live strategy database to break indirect prompt-injection (IPI) defenses. Per the offensive-security policy in [`AGENTS.md`](../AGENTS.md), we do not package offensive exploit-swarm architectures as skills; instead, this brief captures the paper's **instruction-hierarchy evaluation design** (decoupling prompt-injection resistance from safety harm refusal), **attacker-scaling telemetry**, and **concrete runtime defensive rules** (especially hiding defender chain-of-thought and defending against cross-episode strategy accumulation). For bounded defensive evaluation harness search, see [`agentic-prompt-injection-search`](../skills/agentic-prompt-injection-search/SKILL.md) and [`owner-authority-ipi-eval-construction`](../skills/owner-authority-ipi-eval-construction/SKILL.md).

---

## Evaluation Methodology: Disentangling Instruction Hierarchy from Harm Refusal

Static IPI benchmarks (`AgentDojo`, `InjecAgent`) saturated by mid-2025, and human crowd red-teaming on `GraySwan IPI Arena` neared saturation by Fall 2026 (`< 1%` transfer ASR against frontier Gemini and Claude models). Crucially, existing benchmarks almost always pair prompt injections with **overtly harmful targets** (`delete files`, `exfiltrate secrets`, `send phishing`), conflating two distinct model properties:
1. **Safety / harm refusal** (refusing actions that look dangerous regardless of who asked), and
2. **Instruction-hierarchy adherence** (ignoring untrusted tool-output instructions even when the requested tool call looks completely benign).

To isolate pure instruction-hierarchy adherence, the authors construct **`100` synthetic multi-step tool-use scenarios** spanning **`249` tools across `53` domains in `12` categories**:
- Each scenario pairs a benign multi-step **task domain** trajectory with an injected payload inside an untrusted tool response that attempts to trigger a **non-malicious target tool call** in an **orthogonal target domain** with up to $N \le 10$ complex arguments.
- An attack counts as successful only if a dense continuous similarity score exceeds **`score > 0.99`** (`0.4` weight on exact target tool name + `0.6` across exact parameter keys, exact numeric/boolean values, and `> 96%` character-multiset Jaccard similarity on string arguments), eliminating partial/accidental tool calls while giving adaptive attackers smooth black-box optimization signal (`Attack Resistance Rate`, `ARR@k` = fraction of scenarios unbroken after $k$ queries).
- All Gemini defenders were evaluated with external safety classifiers and out-of-model PI shields disabled (`high` thinking enabled, CoT hidden from the caller by default) to measure **intrinsic model-level instruction-hierarchy robustness**.

---

## Key Empirical Findings

### 1. Intrinsic Model Robustness Collapses on Benign Orthogonal Targets for Open-Weight Models, and Erodes Under Swarm Scaling for Frontier Models

Against the strongest `16`-agent swarm (`Gemini 4 Argon` attacker, `20` eval queries/agent = `320` max queries, defender CoT hidden):

| Defender Model | `ARR@150` (`<= 150` queries) | `ARR@320` (`<= 320` queries) | Implied `ASR@320` |
|:---|:---:|:---:|:---:|
| **`Gemini 4 Argon`** | **`87.0%`** | **`66.0%`** | `34.0%` |
| `Gemini 3.8 Flash` | `34.0%` | `10.0%` | `90.0%` |
| `Gemini 3.7 Flash` | `31.0%` | `6.0%` | `94.0%` |
| `Gemini 3.6 Flash` | `3.0%` | `1.0%` | `99.0%` |
| `Kimi K3` (open-weight) | `5.0%` | `1.0%` | `99.0%` |
| `GLM-5.3` (open-weight) | `1.0%` | `1.0%` | `99.0%` |
| `DeepSeek-V4.1-Flash` (open-weight) | `1.0%` | `1.0%` | `99.0%` |

**Takeaway**: Despite strong general coding/agentic benchmark capability, open-weight models (`Kimi K3`, `GLM-5.3`, `DeepSeek-V4.1-Flash`) exhibit virtually **zero intrinsic instruction-hierarchy separation (`1.0%–5.0%` ARR@150)** once safety harm-refusal triggers are removed via benign orthogonal tool targets. Even the strongest adversarially trained frontier defender (`Gemini 4 Argon`) drops from `87.0%` `ARR@150` to **`66.0%` `ARR@320` (`34%` ASR)** as adaptive swarm compute scales.

### 2. Attacker Capability Scaling Tracks `ExploitBench` — Weak Red-Teamers Create False Assurance

Evaluating weak or mid-tier red-team models against a frontier defender creates a severe illusion of invulnerability:
- Against `Gemini 4 Argon` as defender, `DeepSeek-V4.1-Flash` (`100.0%` ARR@150), `Gemini 3.8 Flash` (`99.1%`), `GLM-5.3` (`96.9%`), and `Kimi K3` (`96.7%`) attackers almost completely fail, whereas upgrading the attacker swarm to `Gemini 4 Argon` drops `Gemini 4 Argon` defender `ARR@150` to **`87.0%`** (and mean `ARR@150` across all 7 defenders drops from `42.1%` under `Flash 3.6/3.7` attackers to `38.7%` under `Flash 3.8` and **`23.1%`** under `Gemini 4 Argon`).
- Offensive prompt-injection potency tracks cybersecurity exploit-generation capability on **`ExploitBench`**: `Gemini 4 Argon` scores **`87.4%`** on `ExploitBench` vs. `54.4%` (`GLM-5.3`), `32.2%` (`Kimi K3`), `24.7%` (`DeepSeek-V4.1-Flash`), and `22.3%` (`Gemini 3.8 Flash`).
- On `AgentDojo` (`80` scenarios against production Vertex AI `Gemini 3.6 Flash` *with* out-of-model defenses enabled, `GLM-5.3` attacker), single-agent `Prompt Siren` (`mini-goat`) breaks `2/80` scenarios vs. **`6/80` within `25` queries** (`3x` higher break rate) for the coordinated swarm.

### 3. Exposing Defender Chain-of-Thought (`CoT`) Consistently Degrades Resistance

When the defender's internal thinking trace is returned to the caller (`Gemini 3.8 Flash` attacker swarm, `ARR@150`), attackers diagnose *why* an injection was noticed or ignored and adapt faster, lowering resistance across **every** Gemini generation:

| Defender Model | `ARR@150` (CoT Hidden) | `ARR@150` (CoT Visible) | Resistance Drop |
|:---|:---:|:---:|:---:|
| `Gemini 3.6 Flash` | `11.0%` | `9.0%` | `-2.0 pp` |
| `Gemini 3.7 Flash` | `70.0%` | `68.0%` | `-2.0 pp` |
| `Gemini 3.8 Flash` | `73.0%` | `61.0%` | **`-12.0 pp`** |
| `Gemini 4 Argon` | `100.0%` | `92.0%` | **`-8.0 pp`** |

### 4. Live Cross-Scenario Strategy Accumulation Multiplies Attack Efficacy `7x`

Against a `Gemini 3.8 Flash` defender (`ARR@150`), allowing the swarm to **dynamically write newly discovered bypass tactics into an initially empty strategy database during the evaluation sweep** dramatically outperforms both an empty frozen DB and a static pre-populated DB:
- **`Gemini 3.8 Flash` attacker**: `91.0%` ARR@150 (empty frozen DB) $\to$ `73.0%` (static pre-prepared DB) $\to$ **`61.0%`** (live updating DB, `-30.0 pp`).
- **`Gemini 4 Argon` attacker**: `35.0%` ARR@150 (empty frozen DB) / `34.0%` (static pre-prepared DB) $\to$ **`5.0%`** (live updating DB—**`95.0%` ASR**, reducing surviving scenarios by `7x`!).

---

## Defensive & Evaluation Takeaways

1. **Test instruction hierarchy on benign orthogonal tool calls, never harmful actions alone**: Pair harmful IPI suites with benign cross-domain tool-diversion tests (`score > 0.99` exact argument fidelity) so safety/harm refusal cannot mask a broken user-vs-data privilege boundary—especially before deploying open-weight models (`1%–5%` intrinsic ARR@150).
2. **Never expose raw defender `CoT` across untrusted API or tool-observation boundaries**: Keep raw reasoning traces strictly inside the trusted host boundary (where internal DLP/thought-injection monitors inspect them; see [thought-injection-attacks-reasoning-agents](thought-injection-attacks-reasoning-agents.md)), and strip or summarize reasoning before returning responses to external callers (`+8.0` to `+12.0 pp` ARR@150 preservation on `Gemini 4 Argon` and `Gemini 3.8 Flash`).
3. **Always red-team with an attacker model at least as capable (`ExploitBench`-equivalent) as the deployed defender, with live strategy memory enabled**: Evaluating a frontier defender with weaker attackers (`96.7%–100.0%` ARR@150) or frozen strategy prompts (`35.0%` vs. `5.0%` ARR@150) severely overstates real-world resilience.
4. **Enforce deterministic out-of-model authorization gates**: Because even `Gemini 4 Argon` reaches `34.0%` intrinsic ASR at `320` adaptive queries, model-level instruction hierarchy must be backed by system-level permission intersection ([`principal-context-permission-intersection`](../skills/principal-context-permission-intersection/SKILL.md)), compile-then-execute isolation ([`compile-then-execute-web-agent-gateway`](../skills/compile-then-execute-web-agent-gateway/SKILL.md)), and query/rate anomaly throttling against iterative probing.

## Related Artifacts

- [`owner-authority-ipi-eval-construction`](../skills/owner-authority-ipi-eval-construction/SKILL.md) — Converting utility benchmarks into owner-authority-validated IPI suites (`MetaPI`, `arXiv:2611.10026`).
- [`agentic-prompt-injection-search`](../skills/agentic-prompt-injection-search/SKILL.md) — Budgeted adversarial search for testing IPI defense stacks (`arXiv:2609.04495`).
- [role-separated-self-criticism-red-teaming](role-separated-self-criticism-red-teaming.md) — Corroborating `CoT` exposure risk (`6–17 pp` ASR drop when target reasoning traces are hidden during red-team criticism, `arXiv:2610.34965`).
- [`rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md) — `"DO: Test with evolving adversaries, not static attack sets"` and `"DO: Intersect permissions across all influencing principals in a no-laundering Principal Context outside model judgment"`.
