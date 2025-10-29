# Operations Runbook — Core V1

## Health
- CI green: lint, tests, inventory generated.
- Release tags: `v1.x.y` only.

## Integrity
- On release cut: run `make hashes && make sign`.
- Store `.minisig` out-of-band if not embedded.

## Incident
- Rebuild integrity inventory, compare `merkle_root`.
- If mismatch, bisect commits across integrity scope.
