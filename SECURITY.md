# Security policy

## Security-sensitive components

The most sensitive components are:

- `src/super-review/scripts/commit_findings.py` validates and atomically replaces
  a repository-root report.
- `src/super-review/scripts/validate_findings.py` enforces report structure and
  cross-reference integrity.
- `src/super-review/scripts/finding_fingerprint.py` defines stable record identity.
- `src/super-review/references/command-safety.md` controls execution of untrusted
  repository commands.
- repository build and extraction verification in `scripts/build.py` and `scripts/verify_dist.py`.

## Threat model

Assume the repository under review may be malicious. It may contain same-named scripts, import-shadowing modules, lifecycle hooks, hostile build/test commands, symlinks, hard links, changing files, secrets, or concurrent writers. The skill package itself is trusted only after installation and must resolve helpers from its own canonical root.

The report writer is designed to prevent partial writes, stale overwrites, candidate swaps, candidate mutation, symlink traversal, hard-link aliasing, protected-annotation loss, and writing bytes different from those validated. Changes in this area require adversarial tests.

## Reporting a vulnerability

Use a private disclosure channel controlled by the repository owner. Include:

- affected version and file;
- threat scenario and prerequisites;
- minimal safe reproduction;
- expected and observed behavior;
- impact;
- suggested mitigation when known.

Do not include live credentials, customer data, production secrets, or unnecessary weaponized exploit details. If no private channel exists, open a minimal public issue requesting a secure contact method without publishing the exploit.

## Secret hygiene

This workbench and the shipped skill require no runtime secrets or environment
variables. [`.env.example`](.env.example) records that empty contract. Local
`.env` files are gitignored. CI runs gitleaks on every push and pull request
(see `.github/workflows/ci.yml`). Known false positives for template placeholders
are listed in `.gitleaksignore`.

## Supported version

The current development line named in `VERSION` receives fixes in this workbench. Older snapshots are historical and should be upgraded before security evaluation.
