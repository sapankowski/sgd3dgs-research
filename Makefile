.DEFAULT_GOAL := help
UV := ./scripts/uv.sh

.PHONY: help sync lint format test check validate-sample fetch-upstreams verify

help:
	@echo "SGD3DGS Research commands"
	@echo "  make sync             Create/sync the lightweight Python environment"
	@echo "  make lint             Run Ruff and strict mypy"
	@echo "  make format           Format Python code"
	@echo "  make test             Run CPU-only tests"
	@echo "  make check            Run lint and tests"
	@echo "  make validate-sample  Validate the example experiment record"
	@echo "  make fetch-upstreams  Fetch pinned external baselines"
	@echo "  make verify           Run all local repository checks"

sync:
	$(UV) sync

lint:
	$(UV) run ruff check src tests
	$(UV) run ruff format --check src tests
	$(UV) run mypy

format:
	$(UV) run ruff check --fix src tests
	$(UV) run ruff format src tests

test:
	$(UV) run pytest

check: lint test

validate-sample:
	$(UV) run sgd3dgs-research validate-experiment examples/minimal-experiment.yaml

fetch-upstreams:
	./scripts/fetch_upstreams.sh

verify: check validate-sample
	./scripts/verify_repository.sh
