# P46-01 (2026-04-26): single source of truth for "how do I run this thing".
# Real work lives in scripts/dev-serve.sh; the Makefile is just an
# alias so the muscle-memory `make dev` works.

.PHONY: dev test help

help:
	@echo "Targets:"
	@echo "  make dev   — start /workbench dev server (delegates to scripts/dev-serve.sh)"
	@echo "  make test  — run the full pytest suite under PYTHONPATH=src"
	@echo "Override PORT for dev: PORT=9000 make dev"

dev:
	@./scripts/dev-serve.sh

test:
	@PYTHONPATH=src python3 -m pytest tests/
