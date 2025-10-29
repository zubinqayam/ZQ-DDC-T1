# Integrity Model
- `tools/hash_inventory.py` produces `manifest/hash-inventory.json` and Merkle root.
- `tools/sign_manifest.py` signs `manifest/core-v1.manifest.yaml` (doc_index only) using minisign.
- Release assets are uploaded by CI.
