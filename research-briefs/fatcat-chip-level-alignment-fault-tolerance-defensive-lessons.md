# FATCAT — Defensive Lessons on Edge-Accelerator Weight Integrity, Quantization Scales, and Embodied VLA Fault Containment

> **Source**: [arXiv:2611.31129](https://arxiv.org/abs/2611.31129) (`src:2611-31129v1`)
> **Category**: Edge AI Hardware Integrity, Quantized Inference Resilience & Embodied VLA Safety Interlocks *(Defensive Distillation)*
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

---

## Summary

Edge AI deployments—autonomous robots, industrial manipulators, and local privacy appliances running on embedded GPU SoCs (`NVIDIA Jetson Orin Nano` `8 GB LPDDR5` and `NVIDIA Jetson AGX Thor` `128 GB LPDDR5X`)—commonly rely on disk encryption, Secure Boot, and DRAM `AES-XTS` confidentiality encryption to protect aligned LLMs and Vision-Language-Action (`VLA`) policies in the field. *FATCAT* (`arXiv:2611.31129`) audits what happens to model safety alignment and physical robot trajectories when physical memory-bus faults corrupt resident weights or prefill memory transfers *after* Secure Boot and checkpoint verification have completed.

Distilled strictly for **defensive systems and safety engineering**, the study reveals four critical architectural vulnerabilities in standard edge inference stacks (`vLLM`, `Ollama`, `TensorRT`, `PyTorch`):
1. **Confidentiality-only DRAM encryption (`AES-XTS` without integrity MACs) amplifies faults into aligned `16`-byte random block corruptions**: Because `128`-bit `AES-XTS` lacks authentication tags, bit-level disturbances on off-chip `LPDDR5` traces or on-chip `LPDDR PHY` paths decrypt into **unflagged `16`-byte pseudorandom blocks** (`8` consecutive `FP16`/`BF16` weights) with zero OS, ECC-less bus, or inference-server alerts.
2. **Inference engines never re-attest resident GPU DRAM weights after load, and unbounded quantization scales are the primary vulnerability surface**: Across `FP8`, `INT8`, `INT4`, and `NVFP4`, corrupting bounded quantized weight codes produced **`0%` unsafe responses across `200` random faults** (`Table 9`), whereas corrupting **unbounded `FP32`/`FP16`/`BF16` scale factors** (`Q4_0` / `Q8_0` inline per-`32`-weight block scales hit by `88%–89%` and `47%–50%` of random `16`-byte faults, or load-time `BF16 -> FP8` tensor-scale computation) triggered tensor overflows; by contrast, **`NVFP4`'s bounded `E4M3` block scale suffered `0%` refusal collapse across every tensor of both models**.
3. **Normalization placement and low-rank refusal concentration turn single-layer overflows into silent alignment bypasses**: In post-norm `Gemma 3 1B`, overflowing one `down_proj` weight or scale causes post-block `RMSNorm` to flush that MLP's contribution cleanly to zero—matching software zero-ablation byte-for-byte on `98–100 / 100` `JailbreakBench` prompts across `11 / 12` layer wipes (`70%` of corrupting `Thor` load faults) and cutting `L15 down_proj` refusals from `93 -> 47` (`50` unsafe answers) at **`0.0` points MMLU loss (`39.0% -> 39.0%`, `Table 3`)**. In pre-norm `Llama 3.2 1B`, `BF16` weight overflow corrupts the residual stream (`DoS`), but load-time `FP8` scale wipes (`L11 MLP` refusals `98 -> 23–35`, MMLU `47.0% -> 46.0%`, `Table 4`) and transient prefill faults that zero upper-layer prompt `KV` caches (`up to 97%` unsafe answers within `50` trials, `Table 5`) bypass concentrated mid-layer refusal circuits while preserving fluent generation.
4. **Embodied VLA `NaN` output checks miss both `Silent` trajectory shifts and `106°–359°` `Erratic` physical lunges**: On `SmolVLA` (`450M`) driving a physical `6-DoF SO-101` arm at `30 Hz`, dropping `NaN` action chunks (`Detected`, `16.3%–49.1%` of live pulses; `59%` of corrupted `TensorRT` action-expert loads) completely missed **finite-float `Silent` deviations** (`34.6%` vision-encoder / `31.9%` prefill weight-read blocks, `3.8%–7.2%` live pulses, median `21°–26°` target shift within joint/step bounds) and **violent finite-float `Erratic` sweeps** (`119°–359°` in `0.5–0.75 s`, driven by `44%` of prefill `v_proj` corruptions producing `\ge 100^\circ` plans vs. `0%` in `k_proj`, plus **`33%` of corrupted `TensorRT` startup loads** permanently generating `106°–192.2°` erratic plans on *every* episode with **zero `NaN`s** and `83%` joint-limit excursions).

---

## Why Not a Skill?

`FATCAT` is a hardware fault-injection vulnerability study on embedded GPU SoCs rather than a standalone software agent workflow, and concrete physical fault-injection rig recipes fall outside Praxis scope (`output/AGENTS.md`). Its value for the knowledge base is a set of **defensive hardware-integrity, quantization-format, and embodied actuator-containment design invariants** captured here and distilled into [`output/rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md) and [`output/specs/agent-sandbox.spec.md`](../specs/agent-sandbox.spec.md).

---

## Defensive Technical Breakdown

### 1. Memory Encryption Without Integrity (`AES-XTS`) & Post-Load Attestation Gap (`§4.3, §5.2`)

- **Why disk signing and `AES-XTS` DRAM encryption do not guarantee weight integrity**: Edge platforms verify model signatures on storage at boot/load and encrypt off-chip DRAM with `128`-bit `AES-XTS`. Because `AES-XTS` provides confidentiality without message authentication (`MAC`s), any bit flip on the memory bus or unencrypted on-chip `PHY` path diffuses across the `128`-bit cipher block upon decryption, writing `16` arbitrary bytes (`8` `BF16`/`FP16` values) into GPU-accessible unified memory without raising a bus fault.
- **Persistent load-time vs. transient inference-time exposure**: Inference runtimes (`vLLM`, `Ollama`, `TensorRT`) deserialize and quantize weights into resident DRAM **once** at startup and serve thousands of episodes without re-checking weight digests. A single unverified load-time corruption (`33%` persistent `Erratic` `TensorRT` VLA loads; `70%` clean `down_proj` zero-wipes on post-norm `Gemma 3 1B`) persists silently until process restart.

### 2. Quantization Format Resilience: Unbounded Scales vs. Bounded `NVFP4` (`§5.2.3`, `Appendix A`, `Tables 9–10`)

| Format | Weight Code Type | Scale Encoding & Layout | Corrupted Weight Codes (`200` random `16B` faults, `Table 9`) | Scale / Dequantization Vulnerability (`Table 10`) |
|:---|:---|:---|:---:|:---|
| **`BF16` / `FP16`** | Unbounded float (`8` vals / `16B`) | None | High exponent overflow (`NaN`/`Inf` or post-norm zero flush) | Every `16`-byte block directly exposes `8` wide-exponent floats |
| **`Q4_0` / `Q8_0`** (`GGUF`) | Bounded `4`-bit / `8`-bit int | Inline `FP16` scale per `32`-weight block (`18B` / `34B` blocks) | **`0%` unsafe answers** | **`88%–89%` (`Q4_0`) and `47%–50%` (`Q8_0`)** of random `16B` faults hit an inline `FP16` block scale |
| **`FP8` (`E4M3`)** | Bounded `FP8` (`16` vals / `16B`) | Per-tensor `FP32` scale (`4B` separate tensor, `<0.1%` footprint) | **`0%` unsafe answers** | Safe against weight-code faults, **except** during on-the-fly `BF16 -> FP8` startup quantization (`max(|W|)/448` overflow zeroes the whole tensor, `Table 4`) or direct `FP32` scale corruption |
| **`NVFP4` (`E2M1`)** | Bounded `4`-bit float | **Bounded `E4M3` (`FP8`) per-`16`-weight block scale** + `1` `FP32` tensor scale | **`0%` unsafe answers** | **`0%` refusal collapse across every tensor of both `Gemma 3 1B` and `Llama 3.2 1B`** when block scales are corrupted (bounded max `448` prevents overflow; corrupting the lone `4B` `FP32` tensor scale overflows to `NaN`/DoS rather than silent zeroing) |

### 3. Architecture & Embodied VLA Failure Modes (`§5.2.2, §6`, `Tables 3–8`)

- **Post-norm silent block erasure vs. pre-norm residual propagation**:
  - In **post-norm** blocks (`Gemma 3`), `RMSNorm` sits *before* the residual addition: a single `10^{38}` overflow inside `down_proj` drives the `RMSNorm` denominator to infinity and flushes the entire MLP update to `0` (`h + 0 = h`), leaving downstream layers numerically clean while excising mid-layer safety refusal directions (`0.0` pt MMLU loss on `L15 down_proj`).
  - In **pre-norm** blocks (`Llama 3.2`, `SmolVLA`), persistent `BF16` weight overflow enters the residual stream unnormalized (`NaN` DoS), whereas transient **prefill** faults overflow upper-layer `RMSNorm` denominators to zero prompt `KV` projections above layer $L$ while decode steps run on intact weights (`up to 97%` unsafe answers within `50` trials), and `SmolVLA` prefill **`v_proj`** faults inject large finite values directly into attention weighted sums (`44%` of corrupted `v_proj` blocks caused `\ge 100^\circ` joint sweeps vs. `0%` for softmax-bounded `k_proj`).
- **Why `isnan()` checks fail on physical robots (`SmolVLA` + `SO-101` `6-DoF` arm)**:
  - Out of `16,800` simulated `16`-byte weight-read corruptions (`Table 6`), `34.6%` (vision encoder) and `31.9%` (prefill) produced **`Silent`** finite-float trajectories (`\ge 10^\circ` deviation, `\le 10^\circ`/step, inside joint limits), and `0.6%` produced **`Erratic`** `> 10^\circ`/step multi-joint lunges without a single `NaN`.
  - In live hardware runs (`Tables 7–8`), transient prefill faults triggered `119°–359°` physical arm lunges in `0.5–0.75 s` (`0.6%–1.3%` of pulses) and `3.8%–7.2%` `Silent` misplacements, while `33%` of faulted `TensorRT` startup loads produced permanent `106°–192.2°` `Erratic` lunges (`0` `NaN`s) on every subsequent run until reload.

---

## Recommended Defensive Controls (`§7.1` + Systems Synthesis)

1. **Continuous or Selective In-Memory Weight & Scale Attestation**:
   - Compute cryptographic digests (`SHA-256` / `HMAC`) over resident GPU/unified-memory weight buffers **after** startup quantization/deserialization (`BF16 -> FP8`, `TensorRT` engine load) and re-verify periodically during idle/inter-episode windows against immutable signed manifests—prioritizing tiny quantization scale buffers (`FP32` tensor scales are `4` bytes/tensor!) and safety-critical `MLP` (`down_proj`), `v_proj`, and VLA action-expert tensors.
2. **Prefer Bounded Quantization Scale Encodings (`NVFP4` `E4M3` Block Scales) and Clamp Dequantized Ranges**:
   - Avoid unverified on-the-fly `BF16 -> FP8` startup conversion over untrusted memory buses; serialize pre-quantized weights with signed scale digests, prefer bounded block-scale formats (`NVFP4` `E4M3`), and add explicit finite-norm / magnitude clamping on dequantized scale factors and post-norm residual branches so scale corruption triggers a fail-closed integrity fault rather than a silent zero-wipe.
3. **Reinforce Distributed Refusal Circuits & Independent Input/Output Guardrails**:
   - Because hardware or activation faults easily bypass single-layer low-rank refusal directions (`Arditi et al.`), combine distributed backup refusal alignment (`ABS-Align`, `arXiv:2611.06553`) with physically or process-isolated runtime guardrails whose weights are attested independently.
4. **Enforce Out-of-SoC Microcontroller Kinematic & Workspace Interlocks on Embodied Agents**:
   - Never rely on `isnan()`/`isinf()` tensor checks in the Python/CUDA host loop to protect physical actuators. Enforce hard per-step joint-velocity caps (`|\Delta q_t| \le \Delta q_{\max}`), acceleration/jerk limits, Cartesian workspace bounding boxes, and independent emergency-stop / torque-limit interlocks on a separate microcontroller or servo drive firmware outside the GPU SoC.
5. **Pair Authenticated Memory / Multi-Bit ECC with Redundant Critical Loads on Field Hardware**:
   - Standard single-error-correcting / double-error-detecting (`SECDED`) ECC is overwhelmed by `16`-byte burst corruptions decrypted through `AES-XTS`; high-assurance autonomous platforms should require authenticated memory encryption (`AES-GCM` / integrity trees), redundant verification of startup engine loads, and board-level voltage/clock/EM glitch monitors where physical access is plausible.

---

## Related Artifacts

- **Skills**:
  - [`bounded-context-intervention-window-guardrail`](../skills/bounded-context-intervention-window-guardrail/SKILL.md) — On-device quantized (`Q4_0`/`Q8_0`) guardrail deployment where scale-buffer attestation should be paired with runtime action gating (`arXiv:2611.29847`)
  - [`asymmetric-knowledge-contingent-execution`](../skills/asymmetric-knowledge-contingent-execution/SKILL.md) — Independent physical post-action state judgment above robot controllers (`arXiv:2611.30179`)
- **Research Briefs**:
  - [`detecting-is-not-choosing-vla-world-model-safety`](detecting-is-not-choosing-vla-world-model-safety.md) — VLA runtime safety filtering limits and fallback primitives (`arXiv:2611.29553`)
  - [`embodied-agent-configuration-plane-defensive-lessons`](embodied-agent-configuration-plane-defensive-lessons.md) — Companion configuration-plane hardening on physical robots (`arXiv:2611.22761`)
  - [`addition-by-subtraction-safety-alignment`](addition-by-subtraction-safety-alignment.md) — Reinforcing distributed backup refusal circuits so single-subspace ablation cannot collapse alignment (`ABS-Align`, `arXiv:2611.06553`)
- **Rules**:
  - [`output/rules/agent-sandbox-safety.md`](../rules/agent-sandbox-safety.md) — `"DO: Sandbox the inference serving runtime and treat output token streams as potential exploit vectors"`, `"DO: Screen uncompressed inputs and protect prefill/initial decode tokens and backup refusal circuits against compression and MoE expert pruning"`, and `"DON'T: Trust child-process stdout acknowledgements as proof of physical actuator execution, and always pair agent-synthesized hardware control loops with an out-of-band kill switch"`
