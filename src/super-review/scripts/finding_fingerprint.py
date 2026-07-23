#!/usr/bin/env python3
"""Compute deterministic Super Review record fingerprints.

The fingerprint identity is intentionally independent of volatile evidence such as
line numbers, revision hashes, severity, and current implementation locations.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import unicodedata
from dataclasses import dataclass

_ALLOWED_RECORD_TYPES = {
    "defect or risk",
    "improvement or alternative",
    "feature decision",
    "positive pattern",
}


@dataclass(frozen=True)
class Identity:
    record_type: str
    category: str
    primary_component: str
    identity_statement: str


def normalize(value: str, *, slash_normalization: bool = False) -> str:
    """Return the canonical text normalization used by the skill."""
    text = unicodedata.normalize("NFKC", value).casefold()
    if slash_normalization:
        text = text.replace("\\", "/")
        text = re.sub(r"/{2,}", "/", text)
    return " ".join(text.split())


def canonical_identity(identity: Identity) -> str:
    record_type = normalize(identity.record_type)
    if record_type not in _ALLOWED_RECORD_TYPES:
        allowed = ", ".join(sorted(_ALLOWED_RECORD_TYPES))
        raise ValueError(
            f"unsupported record type {identity.record_type!r}; expected one of: {allowed}"
        )

    category = unicodedata.normalize("NFKC", identity.category).strip().upper()
    if not re.fullmatch(r"[A-Z]{2,5}", category):
        raise ValueError("category must contain 2-5 ASCII uppercase letters")

    component = normalize(identity.primary_component, slash_normalization=True)
    statement = normalize(identity.identity_statement, slash_normalization=True)
    if not component:
        raise ValueError("primary component must not be empty")
    if not statement:
        raise ValueError("identity statement must not be empty")

    return "\n".join((record_type, category, component, statement))


def compute_fingerprint(identity: Identity) -> str:
    digest = hashlib.sha256(canonical_identity(identity).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compute a deterministic fingerprint for a Super Review canonical record."
    )
    parser.add_argument(
        "--record-type",
        required=True,
        choices=[
            "Defect or risk",
            "Improvement or alternative",
            "Feature decision",
            "Positive pattern",
        ],
    )
    parser.add_argument(
        "--category", required=True, help="ID prefix, such as SEC or FEAT"
    )
    parser.add_argument("--primary-component", required=True)
    parser.add_argument("--identity-statement", required=True)
    parser.add_argument(
        "--show-canonical",
        action="store_true",
        help="also print the normalized canonical identity before the fingerprint",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    identity = Identity(
        record_type=args.record_type,
        category=args.category,
        primary_component=args.primary_component,
        identity_statement=args.identity_statement,
    )
    try:
        canonical = canonical_identity(identity)
        fingerprint = compute_fingerprint(identity)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.show_canonical:
        print(canonical)
        print("---")
    print(fingerprint)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
