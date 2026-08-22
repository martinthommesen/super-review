# Phase 12: frontend, UX, accessibility, and client behavior

When a user interface exists, review:

- Component structure.
- State management.
- Data fetching.
- Caching.
- Loading states.
- Empty states.
- Error states.
- Retry behavior.
- Optimistic updates.
- Form behavior.
- Validation.
- Navigation.
- Deep links.
- Responsiveness.
- Accessibility.
- Internationalization.
- Timezone behavior.
- Security.
- Performance.
- Browser compatibility.
- Mobile behavior.
- Offline or intermittent-connectivity behavior when applicable.

Look for:

- Client-only authorization assumptions.
- Sensitive information in browser storage.
- Tokens exposed unnecessarily.
- UI and API validation inconsistencies.
- Duplicate submissions.
- Race conditions between requests.
- Stale-state overwrites.
- Optimistic updates without rollback.
- Missing loading or error feedback.
- Destructive actions without confirmation.
- Confirmations that are present but ineffective.
- Forms that lose data on error.
- Keyboard traps.
- Missing labels.
- Poor focus management.
- Inaccessible custom controls.
- Incorrect semantic markup.
- Insufficient contrast encoded in design tokens.
- Missing reduced-motion support.
- Screen-reader-invisible status changes.
- Missing localization.
- Hard-coded locale assumptions.
- Incorrect pluralization.
- Incorrect date or number formatting.
- Large bundles.
- Repeated rendering.
- Excessive network requests.
- Missing pagination or virtualization.
- Error messages that expose implementation details.
- Features technically available but difficult to discover.
- Equivalent tasks behaving differently across screens.

Recommend UX or product changes where repository evidence reveals unnecessary
friction.
