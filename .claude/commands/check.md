Run the core offline workbench gate and report the result:

```bash
python3 scripts/check.py
```

When any file under `companion/` changed in the same work, also run:

```bash
make companion-test
```

Root `scripts/check.py` / `make lint` intentionally exclude companion. Do not commit, push, publish, or deploy. If a gate fails, fix only issues in scope of the current task.
