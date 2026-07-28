Run root workbench lint and type-check:

```bash
make lint
```

That runs ruff check, ruff format --check, and ty check via uv (companion is excluded from root tooling). When `companion/` changed, also run `make companion-test`. Fix only issues in scope of the current task; do not commit or push.
