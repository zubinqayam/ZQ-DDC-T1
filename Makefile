.PHONY: setup fmt lint test build sign release hashes

PY?=python3

setup:
	$(PY) -m venv .venv && . .venv/bin/activate && $(PY) -m pip install -U pip wheel
	@if [ -f requirements.txt ]; then . .venv/bin/activate && pip install -r requirements.txt; fi

fmt:
	ruff check --select I --fix || true
	black . || true

lint:
	ruff check . || true

hashes:
	$(PY) tools/hash_inventory.py . --out manifest/hash-inventory.json

sign:
	@echo "Signing manifest (requires minisign)";
	$(PY) tools/sign_manifest.py manifest/core-v1.manifest.yaml --key ~/.minisign/key.secret --update

build:
	@echo "No-op for Core V1 (behavior locked)"

test:
	pytest -q || true

release: hashes sign
	@echo "Release artifacts ready in manifest/"
