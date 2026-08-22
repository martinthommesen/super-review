# Phase 14: dependencies, build, packaging, and supply chain

Review:

- Direct dependencies.
- Transitive dependencies.
- Lockfiles.
- Version constraints.
- Package sources.
- Build scripts.
- Code-generation tools.
- Compiler settings.
- Feature flags.
- Optional dependencies.
- Packaging.
- Containers.
- Release artifacts.
- Signing.
- CI workflows.
- Artifact provenance.
- License obligations.

Look for:

- Vulnerable dependencies.
- Abandoned dependencies.
- Duplicate libraries serving the same purpose.
- Dependencies used for trivial functionality.
- Broad dependencies included for narrow use.
- Unpinned build actions.
- Floating container tags.
- Non-reproducible builds.
- Install scripts executing untrusted code.
- Dependency confusion risk.
- Typosquatting risk.
- Missing integrity verification.
- Build-time secrets leaking into artifacts.
- Development dependencies shipped to production.
- Unnecessary runtime dependencies.
- Platform-specific build assumptions.
- Generated code not checked or validated consistently.
- Generated artifacts drifting from source definitions.
- License incompatibilities.
- Missing software-bill-of-materials support where warranted.
- Overly permissive CI tokens.
- Untrusted pull requests accessing secrets.
- Release processes dependent on local state.
- Packages containing unintended files.
- Debug symbols or source maps exposed unexpectedly.
- Production images containing compilers or build tools.
- Excessively large container images.

Do not recommend dependency upgrades merely because newer versions exist.

Recommend replacement or removal only when there is a concrete reason, such as:

- Security.
- Abandonment.
- Maintenance burden.
- Duplicate capability.
- Runtime cost.
- Licensing risk.
- Compatibility problems.
- Better existing platform functionality.
