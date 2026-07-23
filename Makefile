PYTHON ?= python3
PYTHON_ENV ?= PYTHONDONTWRITEBYTECODE=1
ARTIFACT ?= dist/super-review-skill.zip

.PHONY: help check test lint fmt spec build verify release clean example

help:
	@printf '%s\n' \
	  'make check    Run all offline source, package, and clean-room checks' \
	  'make test     Run repository tests and bundled skill regression tests' \
	  'make lint     Run ruff lint, ruff format check, and ty type check' \
	  'make fmt      Reformat Python sources with ruff' \
	  'make spec     Run the external Agent Skills reference validator' \
	  'make build    Create a deterministic distributable ZIP' \
	  'make verify   Verify the distributable and run tests from extraction' \
	  'make release  Clean, check, spec-validate, build, and verify' \
	  'make example  Regenerate the valid example FINDINGS.md fixture' \
	  'make clean    Remove generated local artifacts'

check:
	$(PYTHON_ENV) $(PYTHON) scripts/check.py

test:
	$(PYTHON_ENV) $(PYTHON) -I -B tests/run_tests.py
	$(PYTHON_ENV) $(PYTHON) -I -B src/super-review/tests/run_tests.py

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run ty check

fmt:
	uv run ruff format .

spec:
	$(PYTHON_ENV) $(PYTHON) scripts/spec_validate.py

build:
	$(PYTHON_ENV) $(PYTHON) scripts/build.py --output $(ARTIFACT)

verify:
	$(PYTHON_ENV) $(PYTHON) scripts/verify_dist.py $(ARTIFACT)

release: clean check spec build verify

example:
	$(PYTHON_ENV) $(PYTHON) scripts/generate_example.py

clean:
	$(PYTHON_ENV) $(PYTHON) scripts/clean.py
