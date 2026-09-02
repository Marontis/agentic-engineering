---
name: deterministic-span-editing
description: >
  Deterministic, minimal-diff configuration remediation from LLM-proposed
  field changes. Separates semantic intent (resource, field, value) from
  file editing to eliminate diff misapplication and silent configuration
  corruption in automated GitOps pipelines. Derived from arXiv:2609.00227.
source: https://arxiv.org/abs/2609.00227
---

# Deterministic Span Editing

Use this skill when an AI agent needs to modify declarative infrastructure
or structured configuration files (YAML, JSON, TOML, Kubernetes manifests,
Terraform, Docker Compose, GitOps repos).

## When to Use

- An agent proposes remediation or updates to infrastructure-as-code
  manifests (Kubernetes, Helm, ArgoCD, Flux)
- Automated PR generation where changes must be committed and shipped
  without human intervention
- Preventing silent syntax corruption, dropped fields, or accidental
  collateral edits in structured documents
- Multi-tier agent pipelines where small models propose field changes

## Core Insight

LLMs are strong at **semantic diagnosis** (identifying which resource,
field, and target value need updating) but inherently unreliable at
**syntactic byte-level editing** of structured manifests.

**Quantitative Evidence (arXiv:2609.00227)**:
- **Diff generation is unsafe**: Under strict application, only 2.7% of
  frontier model diffs apply cleanly. When using tolerant tools (`patch`),
  **14–20% of applied diffs are silently misapplied** (wrong lines modified
  with no error triggered). Retrying fails because the retry repeats the same
  failure mode.
- **Full-file rewrite causes collateral damage**: Small models alter
  unrelated lines in **97.6% of outputs** (mean diff size: 921 lines).
  Even frontier models exhibit non-deterministic silent corruption in **7.2%
  of tasks** (randomly dropping comments, changing indentation, or deleting
  sibling keys).
- **Deterministic span editing achieves 100% correctness and 0% collateral
  edits**: By restricting the LLM to emit structured intent tuples and applying
  them via a deterministic parser/span-editor, changes are mathematically
  minimal (exactly 1 scalar updated) across 100% of runs.

---

## Procedure

### Step 1: Constrain LLM Output to Semantic Intent

Do **not** ask the LLM to output a unified diff or the full rewritten file.
Instead, prompt the model to return a structured JSON or YAML payload
specifying only the targeted mutation:

```json
{
  "target_file": "deployments/api-gateway.yaml",
  "resource_kind": "Deployment",
  "resource_name": "api-gateway",
  "field_path": "spec.template.spec.containers[name=proxy].resources.limits.memory",
  "target_value": "512Mi",
  "rationale": "Resolve OOMKilled crashloop detected in staging pod logs"
}
```

### Step 2: Validate Target Schema Before Touching Disk

Before modifying the file:
1. Parse the existing file into an AST / CST (Concrete Syntax Tree) that
   preserves comments and whitespace (e.g., `ruamel.yaml` in Python or
   `yaml-edit` in TypeScript).
2. Resolve the `field_path` against the AST. If the path does not exist or
   is ambiguous, fail closed immediately.
3. Validate `target_value` against the resource schema (e.g., Kubernetes
   OpenAPI spec / JSON Schema).

### Step 3: Perform In-Place Span Replacement

Locate the exact scalar token span `[start_byte, end_byte]` in the source
document corresponding to the target field:

1. Replace only the scalar value slice in the original byte buffer.
2. Preserve original indentation, quote styles, trailing comments, and
   unrelated keys.
3. Do not re-serialize the entire AST, as generic serializers reflow lines
   and strip formatting.

### Step 4: Verify Minimal Diff Invariants

Assert the post-mutation diff meets strict remediation invariants:

- **Single-chunk diff**: The generated Git diff must contain exactly 1 hunk.
- **Targeted line bounds**: Exactly 1 line removed, 1 line added (for scalar
  updates), or strictly bounded line additions for list insertions.
- **Zero collateral edits**: Unrelated resources, sibling attributes, and
  top-level metadata must have 0 diff lines.

---

## Environment Caveats

- **Multi-document YAML**: Kubernetes manifests frequently bundle multiple
  documents separated by `---`. Your resolver must key by `kind` and
  `metadata.name` across document streams.
- **YAML Anchors and Aliases**: If the target field participates in an anchor
  definition (`&anchor`) or alias (`*alias`), modifying the anchor affects
  all downstream references. Fail closed if the field is aliased unless
  explicitly requested.
- **Dynamic lists without identifiable keys**: Lists keyed by index
  (`spec.containers[0]`) are fragile under concurrent edits. Match list items
  by distinct identity keys (e.g., `name: proxy`) rather than raw numerical
  indices.

## Failure Modes

- **Silent Diff Misapplication**: Tolerant patch tools matching common lines
  may shift an edit into a different container block without failing.
- **Comment Stripping**: Round-tripping YAML through standard standard
  `PyYAML` discards all configuration comments, generating thousands of
  spurious diff lines.
- **Type Coercion Hazards**: Writing `512` instead of `"512"` or unquoted
  booleans (`yes`/`no`) can silently change document semantics in older YAML
  parsers.

## Cross-References

- [`agent-sandbox-safety`](../../rules/agent-sandbox-safety.md) — Guardrails
  for automated GitOps and infrastructure modifications.
- [`transactional-coding-sandbox`](../transactional-coding-sandbox/SKILL.md) —
  Rollback and commit primitives for local workspace operations.

## Sources

- Don't Let the Model Write the YAML: Deterministic, Minimal-Diff GitOps
  Remediation from LLM-Proposed Field Changes (arXiv:2609.00227)
- KubeAstra Reference Implementation: https://github.com/our-ark/kubeastra
