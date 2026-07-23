# PHASE 15 — CONFIGURATION, INFRASTRUCTURE, AND DEPLOYMENT

Review:

- Environment-variable handling.
- Configuration files.
- Secret injection.
- Default values.
- Validation.
- Configuration precedence.
- Environment differences.
- Infrastructure-as-code.
- Container definitions.
- Orchestration.
- Networking.
- Storage.
- Identity and access management.
- Autoscaling.
- Resource limits.
- Deployment strategies.
- Rollbacks.
- Migrations during deployment.
- Feature flags.
- Observability infrastructure.

Look for:

- Missing configuration validation.
- Silent fallback to unsafe defaults.
- Different behavior between environments.
- Secrets committed to configuration.
- Secrets passed through command-line arguments.
- Excessive permissions.
- Wildcard IAM grants.
- Public exposure.
- Missing network restrictions.
- Missing encryption.
- Missing resource limits.
- Missing autoscaling bounds.
- Health checks targeting the wrong behavior.
- Mutable container tags.
- Running as root unnecessarily.
- Writable filesystems where not needed.
- Missing seccomp or equivalent hardening when applicable.
- Deployment order dependencies.
- Database migrations coupled unsafely to application startup.
- Feature flags without owners or expiry dates.
- Environment-specific manual steps.
- Rollback paths that do not include schema compatibility.
- Production-only behavior that cannot be reproduced locally.
- Configuration keys that are no longer used.
- Multiple configuration mechanisms for the same behavior.

===============================================================================
