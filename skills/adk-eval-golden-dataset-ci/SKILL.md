---
name: adk-eval-golden-dataset-ci
description: >
  Construct golden evaluation datasets from ADK Web traces and implement automated
  trajectory validation quality gates using adk eval and pytest in CI/CD pipelines.
source: https://codelabs.developers.google.com/adk-eval/instructions?hl=en
---

# ADK Evaluation & Golden Dataset CI/CD Gates

Use this skill when transitioning an ADK agent from local prototyping to production,
establishing an automated regression safety net that runs on every pull request to catch
tool selection errors, parameter regressions, and policy violations.

## When to Use

- Establishing an automated quality gate in GitHub Actions, GitLab CI, or Cloud Build
- Preventing regressions when modifying system prompts, adding new skills, or upgrading models
- Capturing realistic multi-turn conversation traces directly from `adk web`
- Enforcing deterministic assertions on tool execution sequences and parameter values

---

## Core Mental Model

Manual testing of conversational agents is subjective, non-repeatable, and blinds developers
to subtle regressions.

A **Golden Dataset** pairs real or simulated user inputs with expected **Tool Call Trajectories**
and **Reference Response Criteria**. The evaluation harness runs the agent deterministically,
comparing the live trajectory against the golden baseline:

```
[PR: Modify System Prompt or Model]
                 │
                 ▼
  [Run CI Job: pytest / adk eval]
                 │
                 ├──► Execute Agent against Golden Dataset
                 │
                 ├──► Assert Tool Call Sequence (Exact Match)
                 ├──► Assert Parameter Schemas (Pydantic Validation)
                 └──► Assert Policy Adherence (Safety & Prohibited Words)
                 │
      ┌──────────┴──────────┐
      ▼                     ▼
   [PASS: Score ≥ 0.95]  [FAIL: Trajectory Regression]
   Merge PR Approved     Block PR & Output Diff Report
```

---

## Step-by-Step Procedure

### 1. Capture Trajectories in ADK Web

1. Run the local development server: `adk web`.
2. Interact with the agent to execute key operational scenarios (e.g. valid order, edge-case booking, invalid format).
3. Verify that the agent called the exact correct sequence of tools with valid arguments.
4. In the ADK Web session view, click **Export Golden Trace** to save the verified session as JSON.

### 2. Structure the Golden Dataset File (`tests/eval/golden_dataset.json`)

Organize exported traces into a standardized evaluation dataset:

```json
[
  {
    "id": "scenario_book_table_party_4",
    "description": "User requests dinner table for party of 4 at 19:00",
    "messages": [
      {"role": "user", "content": "Can I book a table for 4 tonight at 7 PM?"}
    ],
    "expected_trajectory": [
      {
        "tool_name": "check_table_availability",
        "expected_args": {"party_size": 4}
      },
      {
        "tool_name": "confirm_reservation",
        "expected_args": {"party_size": 4, "time": "19:00"}
      }
    ],
    "assertions": {
      "must_contain": ["confirmed", "7:00 PM", "party of 4"],
      "prohibited": ["error", "credit card"]
    }
  }
]
```

### 3. Implement the Pytest Evaluation Test Suite

Create `tests/test_agent_evaluation.py` to drive evaluation programmatically:

```python
import pytest
from google.adk.eval import AgentEvaluator

@pytest.fixture(scope="module")
def evaluator():
    return AgentEvaluator(
        agent_module="app.agent:root_agent",
        dataset_path="tests/eval/golden_dataset.json"
    )

def test_tool_selection_accuracy(evaluator):
    """Assert agent invokes the exact expected sequence of tools."""
    results = evaluator.run()
    assert results.tool_trajectory_match_rate >= 0.98, (
        f"Tool trajectory degraded! Mismatches: {results.failed_trajectories}"
    )

def test_tool_parameter_conformance(evaluator):
    """Assert all generated tool parameters satisfy validation schemas."""
    results = evaluator.run()
    assert results.parameter_schema_errors == 0, (
        f"Schema violations found in tool calls: {results.schema_errors}"
    )

def test_policy_and_negative_constraints(evaluator):
    """Assert prohibited phrases and ungrounded commitments are never emitted."""
    results = evaluator.run()
    assert results.policy_violation_count == 0, (
        f"Policy violations detected in responses: {results.policy_violations}"
    )
```

### 4. Wire the CI/CD Pipeline Configuration

Add the evaluation job to your GitHub Actions workflow (`.github/workflows/agent-eval.yml`):

```yaml
name: ADK Agent Quality Gate

on:
  pull_request:
    branches: [main]

jobs:
  evaluate-agent:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: "3.12"
    - name: Install dependencies
      run: |
        pip install uv
        uv pip install -r requirements.txt pytest
    - name: Authenticate to Google Cloud
      uses: google-github-actions/auth@v2
      with:
        workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
        service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
    - name: Run ADK Eval Quality Gate
      run: pytest tests/test_agent_evaluation.py -v --tb=short
```

---

## Environment & Implementation Caveats

- **Deterministic Sampling**: In test configurations, set model `temperature=0.0` or use model seed parameters where supported to minimize random generative variance during trajectory evaluation.
- **Mocking External Databases**: Connect tools to mock databases or recorded fixtures during CI runs so tests do not incur third-party API costs or alter production records.
- **Cost Management**: Golden datasets should contain between 30 and 100 high-leverage test cases. For extensive suites (>500 cases), run a tiered strategy: run the critical tier on every PR, and the comprehensive tier nightly.

---

## Edge Cases & Failure Modes

1. **Flaky Order in Parallel Calls**: If an agent makes two independent tool calls in a single turn, their order in the JSON array may vary. Use set comparison or dependency-graph matching rather than strict index matching for unordered peer tool calls.
2. **Silent Hallucination Passing**: An agent that answers the user without calling the necessary tool can pass basic text similarity tests while failing the actual task. Always assert `tool_trajectory_match_rate` independently of semantic response similarity.
