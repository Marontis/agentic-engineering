# Interface Quilt: Modifying Applications with Computer Use Agents and Generative UI

> **Paper**: [Interface Quilt: Modifying Applications with Computer Use Agents and Generative UI](https://arxiv.org/abs/2611.01891) (Qiu et al., 2026)
> **Praxis source**: `src:2611-01891v1`
> **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | **Repository**: [Marontis/agentic-engineering](https://github.com/Marontis/agentic-engineering)

## Summary

Qiu et al. (Autodesk Research) present **Interface Quilt**, a system and design framework that combines **Computer Use Agents (CUAs)** at build time with **Generative UI (GenUI)** and pixel-level synchronization at runtime to create **interface patches**—persistent, interactive UI overlays that customize, bridge, and augment unmodified closed-source desktop and web applications (`Microsoft PowerPoint`, `Affinity`, `Autodesk Fusion`, `Slack`, and `Overleaf`) using rendered screen pixels alone, without requiring source code, plugin APIs, DOM hooks, or accessibility trees.

To address the fragility and high latency of running vision-language CUA loops on every user click, Interface Quilt introduces a strict **build-time vs. runtime separation**:
- **At Build Time**: An agentic coding harness (`Claude Code` powered by `Claude Opus 4.8`, `5`, and `Claude Fable 5`, `5.1`) autonomously explores the target application's GUI using local vision models—`OmniParser v2` for icon/control bounding-box detection, the `Apple Vision OCR API` for text and parameter reading, and `mlx-community/Holo2-8B-bf16` (an 8B coordinate-grounding model)—to discover how controls behave, verify actuation paths, and synthesize a reusable **interface patch** consisting of decoupled `TypeScript` interaction logic and a `JSON` target-binding configuration.
- **At Runtime**: The generated patch runs continuously inside a three-layer desktop architecture without invoking slow VLM exploration loops on the critical path. Instead, it synchronizes state with the underlying application at interactive frame rates using **local luminance text tags**, **zero-mean normalized cross-correlation (ZNCC) glyph template matching**, live video cutouts (`ScreenCaptureKit`), and background PID-targeted synthetic OS input events (`CGEvent.postToPid` / `SLEventPostToPid`).

---

## Design Space & Architectural Framework

### 1. Two-Axis Design Space of Software Modification

Interface Quilt organizes GUI modifications across **five target dimensions** and **four baseline relationships**:

| Modification Dimension | **Reductive** (Simplifies / Hides) | **Replacement** (Swaps Mechanism) | **Additive** (Extends Baseline) |
|:-----------------------|:-----------------------------------|:----------------------------------|:--------------------------------|
| **Presentation: Element** | Hide unused toolbar icons via masked background overlays | Restyle or relabel dense numeric inputs into visual sliders | Add inline color/contrast preview badges next to controls |
| **Presentation: Structure** | Collapse multi-tab ribbons into a minimal floating strip | Reorganize scattered panels into a unified task palette (*Cutouts*) | Embed cross-application live regions (e.g., `Affinity` canvas + `PowerPoint` slide) |
| **Interaction: Modality** | Disable error-prone gesture triggers | Replace nested menu navigation with radial *Marking Menus* or bimanual *Toolglass* | Add multimodal *Put-that-there* voice + cursor commands (`gpt-realtime-1.5` + `whisper-1`) |
| **Interaction: Steps** | Macro-collapse repetitive multi-click export/formatting sequences | Replace modal dialog workflows with direct manipulation | Inject a pre-send confirmation gate (e.g., `Slack` tone/sentiment check via `gpt-5.4-mini`) |
| **Capability** | Restrict access to destructive application actions | Swap native search with semantic CUA-backed lookup | Add cross-app live synchronization (`Affinity` vector edits auto-updating `PowerPoint` assets) |

### 2. Three-Layer Runtime Architecture (macOS `26.5.2`, Apple M2 Pro)

1. **Surface Layer (Electron Overlay + Cut Renderer)**:
   - Renders a transparent, always-on-top Electron window (`NSModalPanelWindowLevel`) spanning the display. Mouse events pass seamlessly through transparent regions to the underlying application and are captured only when the cursor enters an active patch's registered hit box.
   - Includes a shared `Cut Renderer` that crops and streams live pixel regions from underlying windows to create interactive spatial cutouts without screen-recording permission prompts per patch.
2. **Controller Layer (TypeScript / Node.js Stream Orchestrator)**:
   - Executes `runStreams()`, feeding continuous window-geometry and pixel streams into each patch's `onStream(ctx, params)` lifecycle hook.
   - Enforces a clean separation between **portable patch logic (`TypeScript`)** and **application-specific coordinate/template bindings (`JSON`)**, allowing a single interaction patch (such as a radial *Marking Menu*) to be retargeted from `PowerPoint` to `Overleaf` simply by regenerating the `JSON` binding file.
3. **Daemon Layer (Swift Native Capture & Background Event Injection)**:
   - Wraps `ScreenCaptureKit` and `CGWindowListCopyWindowInfo` for high-frequency window tracking and pixel capture.
   - Injects synthetic mouse and keyboard actions directly into background application process IDs via `CGEvent.postToPid` (`SLEventPostToPid`), allowing a user working in `PowerPoint` to trigger canvas updates inside a background `Affinity` window **without stealing OS window focus or hijacking the user's physical cursor** (falling back to `CGWarpMouseCursorPosition` only when an application explicitly requires live cursor hover state to reveal a menu).

---

## Key Engineering Insights & Documented Limitations

1. **Eliminating Runtime VLM Latency via Build-Time Grounding + Runtime Template Matching**:
   - Vision-language models (`OmniParser v2`, `Holo2-8B-bf16`) are invoked only during the build-time exploration phase to locate target controls and extract visual templates. At runtime, reading numeric values or button states from rendered pixels uses lightweight **luminance text tagging** and **ZNCC glyph template matching**, achieving real-time reactive state binding (`Reactive State Binding` on the synchronization spectrum) without LLM inference latency.
2. **Decoupling Interaction Logic from Grounding Bindings**:
   - Storing discovered coordinates, glyph templates, and shortcut mappings in a declarative `JSON` manifest separate from the `TypeScript` UI component enables rapid re-grounding when an application updates its layout or when porting a patch across applications.
3. **Hard OS and Security Constraints Identified by the Authors**:
   - *Build-time latency & cursor hijacking*: Autonomous CUA exploration and build-test verification take **tens of minutes** per patch and take over the host cursor unless isolated inside a virtual machine or secondary display session.
   - *OS single-cursor bottleneck*: Because macOS maintains a single global system cursor, bimanual patches like *Toolglass* (which attempt to use the trackpad and mouse simultaneously as two independent pointers) hit native OS pointer contention.
   - *Toolkit-specific event rejection*: While `PowerPoint`, `Affinity`, `Slack`, and `Overleaf` accept background PID-targeted events (`CGEvent.postToPid`), Qt-based applications (`Autodesk Fusion`) ignore background synthetic drag events unless the window holds active foreground focus.
   - *Exfiltration & sandboxing risk*: Because interface patches receive continuous `ScreenCaptureKit` pixel streams of the user's desktop and execute agent-generated `TypeScript` code, an unverified or prompt-injected patch could exfiltrate sensitive screen contents unless patch execution is network-firewalled and sandboxed.

---

## Why Not a Skill?

Interface Quilt is an exploratory human-computer interaction (HCI) system prototype and design-space taxonomy built specifically around macOS `26.5.2` native APIs (`ScreenCaptureKit`, `CGEvent.postToPid`, `NSModalPanelWindowLevel`, `Apple Vision OCR`) and qualitative case studies rather than a generalizable, cross-platform engineering procedure with controlled quantitative benchmarks. Its architectural patterns—compiling UI grounding into declarative `JSON` bindings at build time while using zero-VLM template matching at runtime, and isolating CUA exploration in a sandbox—inform our generative UI spec and human-interaction rules.

---

## Related Artifacts

- **Rule**: [Agent-Human Interaction](../rules/agent-human-interaction.md)
- **Rule**: [Agent Sandbox Safety](../rules/agent-sandbox-safety.md)
- **Spec**: [Mobile and Generative UI Spec](../specs/mobile-and-generative-ui.spec.md)
