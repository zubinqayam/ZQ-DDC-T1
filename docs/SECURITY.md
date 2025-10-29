# Security — Core V1

- Secrets never committed. Use `secrets.GITHUB_TOKEN` and local `.env` only.
- Integrity: SHA-256 inventory + Merkle root, signed manifest (minisign).
- Reproducibility: canonical JSON, locale `C`, UTF-8 encodings.
- Dependencies: prefer stdlib; pin tools only (black, ruff, pytest, pyyaml).
- CI: no privileged runners; artifacts are integrity-only.
