Run root workbench lint and type-check:

```bash
make lint
```

That runs ruff check, ruff format --check, and ty check via uv (the CLI package is excluded from root tooling). When `cli/` changed, also run `make cli-test`. Fix only issues in scope of the current task; do not commit or push.
