# Mobile client deep checks

Review applicable first-party iOS, Android, cross-platform, and embedded mobile-client behavior for:

- Secure storage, credentials, device identifiers, backups, screenshots, logs, clipboard use, and data-at-rest protection.
- Offline and intermittent-connectivity state, conflict resolution, retries, idempotency, stale data, local migrations, and reconciliation.
- Background execution, lifecycle transitions, process death, task expiration, battery/network cost, and resource cleanup.
- Deep links, intent/URL handling, navigation state, authentication handoff, permission checks, and untrusted external input.
- Platform permissions, privacy declarations, notification behavior, upgrade/downgrade compatibility, and store/release configuration.
- Accessibility, localization, dynamic text, input methods, device sizes, reduced motion, and platform-specific interaction expectations.

Trace client assumptions through server contracts and persistence. Do not treat offline or background behavior as safe merely because the platform manages lifecycle events.
