---
name: adk-mcp-multimodal-tool-interception
description: >
  Integrate Model Context Protocol (MCP) servers with Google ADK agents and implement
  multimodal tool parameter injection and response sanitization via tool lifecycle callbacks.
source: https://codelabs.developers.google.com/adk-multimodal-tool-part-2?hl=en
---

# ADK MCP Multimodal Tool Interception

Use this skill when integrating external Model Context Protocol (MCP) toolsets with Google ADK
agents, particularly for multimodal tools (video generation, image analysis, audio processing)
where tool inputs and outputs require runtime modification, parameter injection, or payload filtering.

## When to Use

- Connecting external standard MCP servers (e.g. Veo video, image generation, filesystem) to ADK
- Injecting hidden system parameters (e.g. negative prompts, aspect ratios, style seeds) into tool calls
- Sanitizing, transforming, or stripping heavy binary data from tool responses before context ingestion
- Enforcing deterministic constraints on third-party tool executions via `before_tool_callback` and `after_tool_callback`

---

## Core Mental Model

ADK integrates MCP tools as first-class `tools` using `mcp_toolset(...)`.
By wrapping these tools with ADK's **Tool Lifecycle Callbacks**, developers retain deterministic
control over what the model sends to the MCP server and what payload reaches the session context:

```
[Agent Emits MCP Tool Call: generate_video(prompt="a dragon flying")]
                       │
                       ▼
             [before_tool_callback]
                       │
                       ├── Injects strict brand constraints:
                       │   prompt += " high definition, 4k, cinematic lighting --no watermark"
                       │   aspect_ratio = "16:9"
                       │
                       ▼ (Transmits augmented payload to MCP Server)
             [External MCP Server]
                       │
                       ▼ (Returns heavy raw payload: video bytes / signed URL / telemetry)
             [after_tool_callback]
                       │
                       ├── Strips raw base64 data to save context tokens
                       ├── Writes video bytes to Cloud Storage
                       └── Emits compact URI payload: {"video_url": "gs://..."}
                       │
                       ▼
             [Agent Inference Turn Synthesizes Final Response]
```

---

## Step-by-Step Procedure

### 1. Initialize and Connect the MCP Server

Configure the connection to the MCP server (stdio, SSE, or HTTP transport) using `mcp_toolset`:

```python
from google.adk.tools import mcp_toolset

# Connect to local or containerized MCP server
veo_mcp_tools = mcp_toolset(
    command="uv",
    args=["run", "mcp-server-veo"],
    env={"GOOGLE_CLOUD_PROJECT": config.PROJECT_ID}
)
```

### 2. Implement Parameter Modification in `before_tool_callback`

To enforce brand guidelines or append mandatory negative prompts to tool parameters:

```python
def intercept_mcp_parameters(tool, args):
    """Modify or validate MCP tool arguments before external dispatch."""
    tool_name = tool.get("name") or getattr(tool, "name", "")

    if "generate_video" in tool_name:
        original_prompt = args.get("prompt", "")
        # Append quality tags and negative prompts
        augmented_prompt = f"{original_prompt} cinematic lighting, 4k, high fidelity --no text, no blurry artifacts"
        args["prompt"] = augmented_prompt
        # Inject standard duration constraint
        args["duration_seconds"] = 5

    # Returning None executes the tool with the modified args dictionary
    return None
```

### 3. Implement Response Sanitization in `after_tool_callback`

Multimodal tools often return massive base64 payloads that quickly exhaust model context windows.
Sanitize the response before context re-injection:

```python
from google.cloud import storage

storage_client = storage.Client()

def sanitize_mcp_response(tool, args, result):
    """Extract heavy media bytes, upload to Cloud Storage, and return URI."""
    if not isinstance(result, dict):
        return None

    # If MCP tool returns raw base64 or video data
    if "video_base64" in result:
        video_data = result.pop("video_base64")
        filename = f"renders/{args.get('call_id', 'clip')}.mp4"
        bucket = storage_client.bucket("my-agent-media-bucket")
        blob = bucket.blob(filename)
        blob.upload_from_string(video_data, content_type="video/mp4")

        # Replace heavy payload with compact reference
        result["gcs_uri"] = f"gs://my-agent-media-bucket/{filename}"
        result["public_url"] = blob.public_url

    # Returning a dictionary overrides the tool response in context
    return result
```

### 4. Attach Callbacks to the ADK Agent

Wire the MCP toolset and interceptors to the agent:

```python
from google.adk import Agent

multimodal_agent = Agent(
    name="video_production_agent",
    model=config.MODEL,
    instruction="Generate video scenes adhering to script directions.",
    tools=[veo_mcp_tools],
    before_tool_callback=intercept_mcp_parameters,  # Injects parameters
    after_tool_callback=sanitize_mcp_response,      # Saves tokens
)
```

---

## Environment & Implementation Caveats

- **Tool Call Cancellation**: In `before_tool_callback`, returning a non-`None` dictionary immediately cancels external tool execution and substitutes your return dictionary as the simulated tool result. Use this pattern for local mock testing or policy blocking.
- **Async Process Management**: Ensure background MCP child processes started via stdio are terminated when the parent ADK Runner process shuts down to prevent zombie sub-processes.
- **OpenAPI Compatibility**: MCP tools dynamically expose OpenAPI schemas. Ensure your LLM model supports function calling for the declared argument types.

---

## Edge Cases & Failure Modes

1. **Schema Mismatch on Mutated Keys**: If `before_tool_callback` inserts an argument key that is not defined in the MCP server's OpenAPI schema, the MCP server will reject the call with a 400 validation error. Always check the target tool's schema before appending parameters.
2. **Context Blowup on Unsanitized Payloads**: If an MCP tool returns high-resolution base64 encoded images or video frames without an `after_tool_callback` stripping them, the subsequent model inference call can exceed the context token limit or trigger exorbitant billing.
