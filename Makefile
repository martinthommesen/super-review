PYTHON ?= python3
PYTHON_ENV ?= PYTHONDONTWRITEBYTECODE=1
UV ?= uv
ARTIFACT ?= dist/super-review-skill.zip

.PHONY: help check test lint fmt coverage coverage-run coverage-clean-pycache spec build verify release clean example cli-test

help:
	@printf '%s\n' \
	  'make check    Run all offline source, package, and clean-room checks' \
	  'make test     Run repository tests and bundled skill regression tests' \
	  'make lint     Run ruff lint, ruff format check, and ty type check' \
	  'make fmt      Reformat Python sources with ruff' \
	  'make coverage Run both test suites under coverage.py (drops python -I)' \
	  'make spec     Run the external Agent Skills reference validator' \
	  'make build    Create a deterministic distributable ZIP' \
	  'make verify   Verify the distributable and run tests from extraction' \
	  'make release  Clean, check, spec-validate, CLI-test, build, and verify' \
	  'make example  Regenerate the valid example FINDINGS.md fixture' \
	  'make cli-test Sync and test the consolidated CLI package' \
	  'make clean    Remove generated local artifacts'

check:
	$(PYTHON_ENV) $(PYTHON) scripts/check.py

test:
	$(PYTHON_ENV) $(PYTHON) -I -B tests/run_tests.py
	$(PYTHON_ENV) $(PYTHON) -I -B src/super-review/tests/run_tests.py

lint:
	$(UV) run --locked ruff check .
	$(UV) run --locked ruff format --check .
	$(UV) run --locked ty check

fmt:
	$(UV) run --locked ruff format .

# Coverage is diagnostic. The ordinary test and check targets retain isolated
# Python execution for the untrusted-repository threat model.
coverage:
	@$(MAKE) coverage-run; status=$$?; \
	$(MAKE) coverage-clean-pycache; clean_status=$$?; \
	if [ $$status -ne 0 ]; then exit $$status; fi; \
	exit $$clean_status

coverage-run:
	$(PYTHON_ENV) $(UV) run --locked coverage erase
	$(PYTHON_ENV) $(UV) run --locked coverage run tests/run_tests.py
	$(PYTHON_ENV) $(UV) run --locked coverage run -a src/super-review/tests/run_tests.py
	$(PYTHON_ENV) $(UV) run --locked coverage report

coverage-clean-pycache:
	@$(PYTHON_ENV) $(PYTHON) -c "from pathlib import Path; import sys; \
sys.path.insert(0, 'scripts'); \
from workspace_hygiene import remove_generated; \
remove_generated(Path('.'), directory_names=('__pycache__',), suffixes=('.pyc', '.pyo'))"

spec:
	@if command -v $(UV) >/dev/null 2>&1; then \
	  $(PYTHON_ENV) $(UV) run --locked python scripts/spec_validate.py; \
	else \
	  $(PYTHON_ENV) $(PYTHON) scripts/spec_validate.py; \
	fi

build:
	$(PYTHON_ENV) $(PYTHON) scripts/build.py --output $(ARTIFACT)

verify:
	$(PYTHON_ENV) $(PYTHON) scripts/verify_dist.py $(ARTIFACT)

release: clean check spec cli-test build verify

example:
	$(PYTHON_ENV) $(PYTHON) scripts/generate_example.py

cli-test:
	cd cli && \
	if command -v $(UV) >/dev/null 2>&1; then \
	  $(PYTHON_ENV) $(UV) sync --locked && \
	  $(PYTHON_ENV) $(UV) run --locked ruff check . && \
	  $(PYTHON_ENV) $(UV) run --locked ruff format --check . && \
	  $(PYTHON_ENV) $(UV) run --locked pytest; \
	else \
	  $(PYTHON_ENV) $(PYTHON) -m uv sync --locked && \
	  $(PYTHON_ENV) $(PYTHON) -m uv run --locked ruff check . && \
	  $(PYTHON_ENV) $(PYTHON) -m uv run --locked ruff format --check . && \
	  $(PYTHON_ENV) $(PYTHON) -m uv run --locked pytest; \
	fi

clean:
	$(PYTHON_ENV) $(PYTHON) scripts/clean.py
