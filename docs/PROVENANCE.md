# Source Provenance

## Original review prompt

The archival source prompt is stored at `docs/ORIGINAL_REVIEW_PROMPT.md`.

```text
SHA-256: 6e72f4afbfca5896065c5b8a231cf3c03f42b8ea881bbe09e483fd9da9f9df80
Logical lines: 3201 (3200 newline characters)
```

The adjacent `ORIGINAL_REVIEW_PROMPT.sha256` file is checked by the repository regression suite. This source is retained for comparison and future protocol evolution; it is not loaded by the shipped skill.

## Imported 1.2.0 package

The source under `src/super-review/` was imported from the previously verified 1.2.0 distributable whose SHA-256 was:

```text
6d5f535b60f71bab1b21dac3eeaf1e66f3206adb277550b5d3fbfe3df8778544
```

At import time the workbench's deterministic builder produced a different archive byte hash because ZIP metadata and ordering are normalized, while extracted file bytes were identical to the imported 1.2.0 source. Releases after 1.2.0 intentionally modify `src/super-review/`; `CHANGELOG.md` records those changes.
