# Release Process

Repository tooling is local and validation-gated: no script or make target commits, pushes, publishes, or creates a remote release. The only steps that touch a remote — publishing (step 8) and tag creation (step 9) — are explicit operator actions run by hand after every gate has passed.

## 1. Prepare the change

- Update `src/super-review/` and all coupled tests/docs.
- Update `VERSION`, `pyproject.toml`, the `Version:` line in `SKILL.md`, `CHANGELOG.md`, `README.md`, and every versioned marketplace or plugin manifest together for a release.
- If the consolidated CLI's install or command contract changes, update `cli/README.md` and its own version in `cli/pyproject.toml` (the CLI versions independently of the skill); keep CLI dev pins out of the root workbench dev group.
- Regenerate `examples/FINDINGS.example.md` after schema or fixture changes.
- Keep the original source prompt unchanged unless the archival source itself is intentionally being replaced; update its checksum in that exceptional case.

## 2. Run offline gates

```bash
python3 scripts/clean.py
python3 scripts/check.py
```

`check.py` runs syntax checks, repository tests, the shipped suite, validator self-test, temporary deterministic build, source/archive comparison, safe extraction, and tests from the extracted package.

## 3. Run the external specification gate

Install development dependencies and run:

```bash
python3 scripts/spec_validate.py
```

This uses the pinned `skills-ref` dependency. Record the validator version in release notes when it changes.

## 4. Validate marketplace metadata

Repository tests validate all three catalogs, their client manifests, canonical skill paths, and synchronized versions. When Claude Code is installed, also run its first-party strict validator:

```bash
claude plugin validate . --strict
claude plugin validate src --strict
```

Copilot and Codex marketplace smoke tests require their respective clients. Add this repository as a marketplace, install `super-review@super-review`, verify the skill source, and invoke the client-specific explicit command before publishing.

For Cursor, confirm `.cursor-plugin/plugin.json` points at `./src/super-review` and the Cursor command adapter, and registers no MCP server (decision D15). The consolidated CLI is validated separately by `make cli-test`.

## 5. Build the distributable

```bash
python3 scripts/build.py --output dist/super-review-skill.zip
```

The builder writes `dist/SHA256SUMS` and replaces the artifact atomically.

## 6. Verify the exact artifact

```bash
python3 scripts/verify_dist.py dist/super-review-skill.zip
```

Do not ship if archive contents differ from `src/super-review`, an unsafe path or mode is present, CRC validation fails, or clean-room tests fail.

## 7. Inspect release metadata

```bash
cat VERSION
cat dist/SHA256SUMS
unzip -l dist/super-review-skill.zip
```

Confirm the archive has one top-level `super-review/` directory and contains no workbench-only files.

## 8. Publish manually

Publishing is intentionally outside repository automation. Push the verified marketplace catalogs and plugin manifests together with the matching skill version. For direct-skill distribution, use the approved destination and process, preserve the ZIP bytes and checksum, and do not rebuild between verification and upload.

## 9. Tag the release

This step is an explicit operator action, like step 8: nothing in `scripts/` or the Makefile creates or pushes tags. After the release commit is on the default branch, create an immutable annotated tag so marketplace consumers can pin exact revisions (for example Codex `--ref`):

```bash
git tag -a vX.Y.Z -m "super-review X.Y.Z"
git push origin vX.Y.Z
```
