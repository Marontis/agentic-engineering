# ControlAnything: On-Demand Generative UI and Mixed-Reality Device Integration

> **Paper**: [ControlAnything: Generative UI and On-Demand Device Integration for Mixed-Reality Hand Interaction by a Coding Agent](https://arxiv.org/abs/2611.08321) (Ryskeldiev, 2026)
> **Praxis source**: `src:2611-08321v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Executive Summary

**ControlAnything** is a mixed-reality (MR) runtime for a **Meta Quest 3** headset (running a WebXR `immersive-ar` client in Quest Browser paired with a Node.js server on a MacBook) where a wearer points at a physical device or screen, speaks a natural-language intent, and a coding agent (`muse-spark-1.3`) discovers the target on the local machine/network, writes a custom Node.js **connector** (`15–42` lines of code), tests an action against the live transport, and returns both floating 3D AR controls and a per-frame JavaScript **hand program** (`wire(s, out, mem)`) that maps 30 Hz 3D hand-pose features to continuous device commands.

Across a single-session evaluation of **10 spoken requests (`R1–R10`)** spanning **5 physical/software targets** (a WebGL visual synthesizer, Instagram Reels in Chrome, a MacBook laptop, a Teenage Engineering OP-1 Field USB-MIDI synthesizer, and a DJI Osmo Mobile 4 Bluetooth gimbal), **9 of 10 requests reached a ready state** in a **median of 32.5 s** (mean **37.8 s**, range **24.9–57.8 s**, $n = 9$, excluding `1.2–3.4 s` speech transcription). Sequential LLM calls (`73` calls across 10 runs, median **3.48 s/call**, P90 **8.88 s/call**) accounted for a **median of 89.9%** of end-to-end latency (range **82.5–96.2%**), while prompt caching supplied **91.7%** of the **656,844** total input tokens by reusing a fixed **5,489-token** prefix from `R2` onward.

---

## System Architecture & Execution Pipeline

### 1. Gated Visual Pointing & Voice Capture
- The Quest 3 client streams passthrough camera frames to **SAM 3.1** at most once every **1.2 s**, skipping frames whenever the wearer's head rotates faster than **$15^\circ\text{/s}$** and accepting segmented object masks with confidence score **$\ge 0.55$** (across 336 SAM 3.1 calls during pose recording, median latency was **0.83 s** and 40% returned no object).
- Spoken requests are transcribed via `Muse Voice Transcribe` (`1.2–3.4 s`) and bundled with the segmented crop and workspace state into a coding-agent session capped at **24 turns, 40 tool calls, 300 s wall-clock time, and 600,000 tokens** (one tool call per turn via streaming function calling).

### 2. On-Demand Connector Synthesis & Transport Testing
- Rather than selecting from pre-built smart-home integrations, the coding agent inspects the local environment and writes a standalone Node.js **connector** (`15–42` lines) exposing `1–16` typed actions (`set`, `trigger`, `toggle`) over three pre-written hardware bridges:
  1. **Web MIDI**: Clamped to integer CC/note values in `[0, 127]`.
  2. **Web Bluetooth Gimbal Bridge** (DJI Osmo Mobile 4): Clamped to pan $\pm 120^\circ$, tilt $\pm 45^\circ$, and rate-limited to **10 commands/s**.
  3. **macOS AppleScript**: Dispatches application key presses and system commands.
- The agent validates its code via `deploy_connector` (which waits **1.2 s** for process startup and JSON manifest registration) followed by `test_action` (which waits **900 ms** and checks stdout for a transport acknowledgement prefix `->` vs. an error refusal `✗`).

### 3. Sandboxed 30 Hz Per-Frame Hand Programs (`wire(s, out, mem)`)
- Alongside declarative 3D AR widgets (up to **6 simple controls** plus an optional composed instrument of up to **8 widgets**), the agent can synthesize a short JavaScript function `wire(s, out, mem)` (**$\le 4,096$ characters**) that maps continuous hand-tracking features (pinch distance, palm height, wrist roll, two-hand span) to normalized `[0, 1]` action outputs on every frame:
  - **Server-side dry-run gate**: Before shipping to the headset, the server executes `wire(s, out, mem)` inside `node:vm` across **480 synthetic pose frames** and rejects any program whose average execution time exceeds **2 ms/frame** or that throws runtime exceptions.
  - **Headset Web Worker isolation**: Approved hand programs run inside a browser Web Worker stripped of network (`fetch`, `WebSocket`), storage, and timer APIs, enforced by a **4 ms per-call budget**, a **50 ms watchdog**, a **3-strike termination limit**, and a **30 Hz output gate**.

### 4. Independent Hardware/OS Stop & Teardown Path
- Because agent-synthesized connectors and continuous hand-tracking loops control physical actuators (such as motorized gimbals and audio synthesizers), ControlAnything implements an **agent-independent kill switch** triggered by holding both palms open for **400 ms**, pressing the wrist menu, or tapping the card stop button:
  - Immediately dispatches neutral hardware releases (MIDI panic / all-notes-off, gimbal rotation stop).
  - Sends `SIGTERM` to the connector process at **250 ms**, escalates to `SIGKILL` at **600 ms**, and applies a **1.7 s post-retirement filter** to drop in-flight messages from retired sessions.

---

## Key Empirical Findings & Failure Modes

| Metric / Dimension | Exact Reported Value | Notes / Context |
|:---|:---|:---|
| **Request Completion Rate** | **9 / 10 (90%)** | `R6` stopped manually by wearer at 18.5 s |
| **Time to Ready ($n = 9$)** | **Median 32.5 s** (Mean **37.8 s**, Range **24.9–57.8 s**) | Excludes `1.2–3.4 s` voice transcription |
| **LLM Call Share of Latency** | **Median 89.9%** (Range **82.5–96.2%**) | `73` total calls; median **3.48 s/call** (P90 **8.88 s**) |
| **Non-LLM Tool & Wait Overhead** | **Median 3.0 s** (Range **2.1–5.5 s**) | Dominated by fixed `1.2 s` deploy + `0.9 s` test waits; other tools `1–6 ms` |
| **Prompt Cache Efficiency** | **91.7%** of **656,844** input tokens | Reuses fixed **5,489-token** system/tool prefix from `R2` onward |
| **Gimbal Transport Acknowledgements** | **889** `status-00` rotate acks | `881` from agent code (`2` in `test_action`, `879` over $\ge 87.9\text{ s}$ steering); `8` from stop/release |
| **Hand Pose Tracking (`R9–R10`)** | **3,247 frames** over **111.6 s** at **30.01 Hz** | Left hand untracked in **3.2%** of frames, right hand in **2.6%** (`24 MiB` log cap) |

### Critical Safety & Verification Insights

1. **The Transport Acknowledgement vs. Physical Effect Gap**:
   - In `test_action`, the agent verifies that a synthesized connector works by checking whether the transport bridge logs an acknowledgement line starting with `->`.
   - However, during development sessions with the OP-1 Field synthesizer, USB-MIDI packets were validly acknowledged by the transport while the physical instrument produced **zero sound** because its internal MIDI receive setting was disabled.
   - Furthermore, because `test_action` parses child-process `stdout` for lines beginning with `->`, a buggy or hallucinating connector script can **spoof its own verification** simply by printing `-> ok` to stdout without ever invoking the underlying hardware transport.
2. **Unsandboxed Connector Execution vs. Sandboxed Hand Programs**:
   - While per-frame `wire(s, out, mem)` programs are tightly constrained inside a networkless Web Worker (`4 ms` budget, `50 ms` watchdog, 3 strikes), the server-side Node.js connectors run as local OS child processes guarded only by a **20-regex bash deny-list**, leaving ambient filesystem and local-network authority exposed.

---

## Why Not a Skill?

1. **Single-User ($N = 1$) Hardware-Specific Prototype**: The evaluation is a single-session, author-only ($N = 1$) feasibility demonstration coupled to a Meta Quest 3 headset, internal Meta models (`muse-spark-1.3`, `Muse Voice Transcribe`, `SAM 3.1`), and three pre-authored local transport bridges (Web MIDI, a specific DJI Osmo Mobile 4 BLE protocol, and macOS AppleScript).
2. **Lack of Generalizable Procedural Transfer**: The core pipeline relies on standard ReAct tool calling (`deploy_connector` + `test_action` with fixed sleep intervals) rather than a novel, reusable algorithmic procedure that transfers across general software engineering projects.
3. **Value Captured Better as Safety & Verification Rules**: The paper's two strongest engineering lessons—(a) never equating stdout/transport acknowledgement (`->`) with physical actuator effect or unforgeable verification, and (b) pairing any agent-synthesized real-time control loop with an out-of-band hardware/OS kill switch (`400 ms` gesture $\rightarrow$ neutral actuator release $\rightarrow$ `SIGTERM` at `250 ms` $\rightarrow$ `SIGKILL` at `600 ms`)—directly reinforce Praxis's existing safety and evaluation rules rather than warranting a standalone skill.

---

## Related Artifacts

- **Spec**: [Mobile and Generative UI Spec](../specs/mobile-and-generative-ui.spec.md)
- **Rules**: [Agent Sandbox Safety](../rules/agent-sandbox-safety.md), [Agent Evaluation Quality](../rules/agent-evaluation-quality.md), [Agent Human Interaction](../rules/agent-human-interaction.md)
