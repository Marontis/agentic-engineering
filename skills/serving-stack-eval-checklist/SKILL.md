---
name: serving-stack-eval-checklist
description: >
  Treat the serving stack as part of the evaluation protocol when
  benchmarking local tool-use agents. Covers template-flag gating,
  cross-stack divergence, constrained decoding non-termination,
  retry exhaustion metadata loss, and pooling-level estimate
  discrepancies.
  Derived from "Measuring the Serving Stack Instead of the Model"
  (arXiv:2609.26693).
source: https://arxiv.org/abs/2609.26693
---

# Serving-Stack Evaluation Checklist

Use this skill when evaluating agent tool-use performance on local
serving stacks (Ollama, llama.cpp, vLLM, SGLang) and you need to
ensure measured outcomes reflect model behavior, not serving-layer
artifacts.

## When to Use

- Benchmarking tool-use fidelity of locally served models
- Comparing model performance across different serving backends
- Debugging unexpected 0% fidelity or non-termination in tool-use
  evaluations
- Publishing or reporting tool-use benchmark results

## Core Insight

Measured tool-use outcomes can depend on the **serving layer** rather
than model behavior alone. Ollama gates tool requests per model via a
static template flag: some models are accepted (return calls as text
or native tool_calls), while others are rejected before inference.
Rejection and retry exhaustion are not preserved as structured
failure metadata, so downstream analysis can misclassify them as
model non-calls and naively report 0% fidelity. Cross-stack probes
show different handling of the same request across Ollama, llama.cpp,
vLLM, and SGLang.

**Evidence**: Turn-pooled versus per-instance estimates differ by up
to ~55 points. Constrained decoding removes parse failures but can
induce non-termination.

---

## Checklist

### Pre-Evaluation

- [ ] **Record serving stack and version**: document exact backend
  (Ollama version, vLLM commit, SGLang version, llama.cpp build)
- [ ] **Check template-flag support**: for Ollama, verify the model's
  template includes tool-call support; if the flag is absent, the
  model is rejected before inference
- [ ] **Document tool-call protocol**: are tools passed via `tools=`
  parameter (native), text tool list, or both? Each produces
  different results
- [ ] **Test with a known-good model**: verify the harness can
  successfully process a tool call end-to-end before benchmarking

### During Evaluation

- [ ] **Preserve rejection metadata**: if the serving stack rejects a
  tool request, record the rejection as a distinct failure class —
  do NOT conflate with "model chose not to call"
- [ ] **Preserve retry exhaustion**: if retries are exhausted, record
  as retry exhaustion, not as model non-call
- [ ] **Monitor for non-termination**: constrained decoding can
  eliminate parse failures but induce infinite generation; set
  generation timeouts and record timeout events
- [ ] **Use per-instance estimates**: turn-pooled estimates (averaging
  across all turns) can differ from per-instance estimates by up to
  ~55 points; report per-instance

### Cross-Stack Comparison

- [ ] **Same request, multiple stacks**: if comparing results across
  stacks, send identical requests and document divergent handling
- [ ] **Native vs. text protocol**: a uniform text protocol may reduce
  fidelity for models with native tool-call support (e.g., Llama-3.2);
  adding a text fallback while retaining native channel recovers
  fidelity for accepted models
- [ ] **Constrained decoding disclosure**: if using constrained
  decoding, disclose it and report non-termination rate separately

### Reporting

- [ ] **Report serving stack as experimental condition**: the serving
  backend is a confound, not a constant
- [ ] **Separate model failures from serving failures**: rejection
  before inference, parse failures, and model non-calls are distinct
- [ ] **Report pooling method**: state whether estimates are
  turn-pooled or per-instance
- [ ] **Include a reproducibility block**: backend, version, tool
  protocol, decoding mode, timeout settings

---

## Failure Modes & Mitigations

| Failure Mode | Trigger | Mitigation |
|:-------------|:--------|:-----------|
| False 0% fidelity | Template-flag rejection misclassified as model non-call | Check template support; preserve rejection metadata |
| Inflated fidelity | Constrained decoding masks parse failures | Report constrained decoding separately; check for non-termination |
| Cross-stack inconsistency | Same model scores differently on different backends | Document stack as experimental condition |
| Pooling bias | Turn-pooled estimates mask per-instance variation | Use per-instance estimates; report both if possible |
| Silent retry exhaustion | Retries consumed without structured logging | Instrument retry loop to record each attempt and final status |

> Source: Tang & Zheng, "Measuring the Serving Stack Instead of the
> Model" (arXiv:2609.26693), Sep 2026.
