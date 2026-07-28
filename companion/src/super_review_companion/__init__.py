"""Optional MCP companion for super-review FINDINGS helpers."""

__version__ = "0.1.0"

# Soft tool-call limit; the shipped validator still accepts up to 64 MiB via CLI.
MCP_MAX_CONTENT_BYTES = 1 * 1024 * 1024
