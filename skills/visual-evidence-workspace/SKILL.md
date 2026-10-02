---
name: visual-evidence-workspace
description: >
  Manage image-valued intermediate evidence (crops, masks, overlays,
  renderings) produced by a sandboxed VLM agent: register every artifact
  in a ledger with stable ids and provenance, keep only a bounded set of
  images (focus + aux) visible, require an explicit Promote action to
  bring an artifact into view, and compile each request deterministically
  from recent turns plus a textual recap. Cuts tokens against append-only
  history while keeping or improving accuracy.
  Derived from "VLM-in-Sandbox: Visual Workspaces for Agentic Visual
  Reasoning" (arXiv:2609.24362).
source: https://arxiv.org/abs/2609.24362
---

# Visual Evidence Workspace for Sandboxed VLM Agents

Use this skill when a vision-language agent runs tools (Python, shell,
image editors) that produce new images as intermediate evidence, and
those images are currently appended to the conversation.

## When to Use

- A VLM agent crops, zooms, masks, renders plots, or annotates images
  across several tool steps, and every result is re-sent on each turn
- Token use or latency grows with trajectory length because image
  history accumulates
- The agent needs to return to an earlier crop without replaying all
  images generated since
- You are adding a code sandbox to a VLM and sandbox access alone does
  not beat the plain model (it can lower accuracy)

## Core Insight

**Separate evidence generation (tools) from evidence visibility
(runtime).** Files persist on disk under stable ids; only what the
model explicitly promotes into a small fixed number of slots is sent as
image input. Generating an image and deciding it should guide the next
step become two different acts, so exploratory or failed crops cost
disk space, not context.

**Evidence** (training-free; 7 benchmarks, 6,350 examples, 4 VLMs, max
20 agent steps):

- Highest sample-weighted accuracy for every base model; better than
  append-only sandboxing in all 28 model-benchmark pairs. Gains over
  plain VLM: +1.66 (GPT-4.1-mini), +3.54 (Gemini-2.5-Flash), +5.09
  (Qwen3.5-9B), +9.61 (Ministral-3-8B) points.
- Sandbox access alone can hurt: GPT-4.1-mini fell from 65.81 to 64.95
  with append-only sandboxing, and rose to 67.47 with the workspace.
- Token reduction vs append-only sandbox: 25.7%, 51.8%, 16.3%, 11.7%
  for the four models, while also improving accuracy.
- Compiler-matched control (GPT-4.1-mini, N = 1,260): +1.83 points over
  retain-all with 18.6% fewer tokens (52 rescues / 29 regressions,
  McNemar p = 0.014). **Bounded retention is the larger token lever**
  (16.7% under automatic visibility); model-directed selection over
  "two most recent" adds +0.63 points (not significant, p = 0.185).
- Replay scaling: as stored artifacts grew from 4 to 32, retain-all
  requests grew 8.90K → 42.30K tokens; the workspace grew 8.40K →
  17.90K with visible derived images held near two.

---

## Procedure

### 1. Register Every Image in a Ledger

For each input image and each image a tool writes, record: a stable id
(e.g. `asset://asset_0008`), file path, and provenance (the parent
asset(s) and the tool call that produced it). Parent-child links matter
for iterative localization (crop → sub-crop → zoom).

After each step, **evict inline payloads** of assets that are neither
active nor original inputs. Keep their metadata. The model still sees
that they exist and can reference them by id, and the pixels reload from
disk on promotion.

### 2. Bound the Active Visual Context

Define a fixed set of named slots rendered as images on the next
request. The default is two: `focus` (primary evidence) and `aux` (a
supporting view such as the parent crop or surrounding scene). In the
capacity sweep, one slot was cheapest, two gave the best observed
accuracy, and four added tokens without improving accuracy.

Original input images stay available. Derived images are visible
**only** through slots.

### 3. Require Explicit Promotion

Expose a routing command, not an image tool, e.g.
`promote asset://<id> slot=focus|aux`. It performs no image processing.
It only moves an existing ledger asset into a slot, replacing the
previous occupant (which stays on disk). Newly generated images are
**not** auto-promoted.

Expect promotion to be selective: in the paper's audit of recovered
examples, 7.4% of trajectories used promote at all, 27.1% for visual
search tasks vs 4.2% for math, where text tool outputs sufficed.
Do not force a promote on every step.

### 4. Compile Each Request Deterministically

Rebuild every model request from workspace state instead of replaying
history:

1. Fixed system and task instructions
2. A deterministic textual recap of older turns (action types and
   observation digests, no images)
3. The last k action-observation turns uncompressed (k = 3 default)
4. A workspace summary listing asset ids, provenance, and recent
   artifacts
5. Step-budget guidance
6. The active slots, rendered as images

In the paper, replacing unlimited raw replay with 3 recent turns plus
recap cut tokens 8.6% (12.61K → 11.53K) with accuracy 65.87% → 66.27%.

### 5. Gate Submission and Measure Per Model

- Check that an answer exists before accepting a submit.
- Evaluate with paired rescue/regression counts against the plain
  model, not only the aggregate. Sandbox reasoning also breaks answers
  the model would have got right directly (Qwen3.5-9B: 734 rescues vs
  411 regressions against the plain model, and a lower RealWorldQA
  mean). Consider routing easy questions straight to the model.

---

## Environment Caveats

- Evaluated on static images only; extension to video (frames/clips as
  ledger assets) is untested.
- Training-free: the base VLM decides when to use tools and what to
  promote. Weak tool-use judgment shows up as regressions on questions
  answerable directly.
- Bounded image slots do not make total context constant. Text history
  and ledger metadata still grow.
- With prefix caching (vLLM), the workspace had a lower cache-hit ratio
  (64.0% vs 67.0%) yet less uncached input (11.29K vs 13.50K tokens per
  example), with TTFT −19.7% and E2E −13.0%. Compare uncached tokens
  and latency, not hit ratio.
- Docker was used for isolation (0.82 s lifecycle per example, 2.0% of
  E2E); any executor with the same file-and-tool contract works.

## Failure Modes

| Failure Mode | Trigger | Mitigation |
|:--|:--|:--|
| Context bloat | Every generated image appended to history | Ledger + payload eviction + bounded slots (Steps 1–2) |
| Lost evidence | Image dropped from context and not addressable later | Stable ids with provenance; eviction removes payloads, not files |
| Buried evidence | Useful crop hidden among many later images | Explicit promote to `focus` (Step 3) |
| Over-tooling | Sandbox used on questions answerable directly, causing regressions | Paired rescue/regression tracking; selective sandbox routing (Step 5) |
| Misread evidence | Promoted overlay interpreted wrongly despite correct routing | Selection does not validate interpretation; keep evidence-quality checks separate from accuracy |

## Cross-References

- [`prefix-preserving-context-assembly`](../prefix-preserving-context-assembly/SKILL.md): deterministic context compilation for text agents
- [`protocol-preserving-context-trimming`](../protocol-preserving-context-trimming/SKILL.md): what must never be trimmed
- [`high-fanout-sandbox-memory-compression`](../high-fanout-sandbox-memory-compression/SKILL.md): memory pressure across many sandboxes
- [`transactional-coding-sandbox`](../transactional-coding-sandbox/SKILL.md): sandbox lifecycle and rollback

## Sources

> Yang, Chen, Cao & He, "VLM-in-Sandbox: Visual Workspaces for Agentic
> Visual Reasoning" (arXiv:2609.24362), Sep 2026.
