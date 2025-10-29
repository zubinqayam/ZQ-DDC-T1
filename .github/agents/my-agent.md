---
name: workflow-validator-agent
description: >
  A program that validates the core ZQ DDC provenance workflows. It checks that
  manifests are signed and verifiable, adhere to the schema, reference the correct
  schema URI, and that tags are protected by valid signatures. It only operates
  on Core V1 functionality and does not modify data beyond this scope.
---

# Workflow Validator Agent

This agent performs a series of checks against the ZQ DDC Core V1 workflow to ensure integrity and compliance:

1. **Manifest verification** – For each YAML manifest in the repository, it runs the deterministic verifier (`tools/verify_manifest.py`) to confirm that the signature (`signing.signature.value`) matches the canonical payload (with `signature.value` stripped prior to hashing).

2. **Schema validation** – It invokes `tools/validate_schema.py` on each manifest to ensure compliance with `schema/manifest.schema.json`, reporting any structural or field‑level errors.

3. **Documentation check** – The agent runs `tools/check_schema_uri.py` to ensure that every manifest’s `schema_uri` field references the expected schema (e.g., `schema/manifest.schema.json`), preventing mismatches or outdated references.

4. **Tag protection** – When executed in the context of a release tag, it calls `tools/tag_protect_unsigned.py` with the repository’s public key to verify that each manifest’s signature is present and valid, and fails the process if any signature is missing or invalid.

By aggregating the results of these checks, the workflow-validator-agent provides assurance that the critical provenance workflows operate correctly under the constraints of ZQ DDC Core V1.
---
name:
description:
---

# My Agent

Describe what your agent does here...aggregating the results of these checks, the workflow-validator-agent provides assurance that the critical provenance workflows operate correctly under the constraints of ZQ DDC Core V1.
