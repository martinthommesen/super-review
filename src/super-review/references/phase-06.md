# Phase 6: security, privacy, and abuse resistance

Establish:

- Sensitive assets.
- Sensitive data.
- Privileged operations.
- Trust boundaries.
- Threat actors.
- External entry points.
- Internal entry points.
- Likely attacker capabilities.
- Tenant boundaries.
- Administrative boundaries.

Review for:

1. Authentication bypass.
2. Authorization bypass.
3. Missing object-level authorization.
4. Missing function-level authorization.
5. Tenant-isolation failure.
6. Horizontal privilege escalation.
7. Vertical privilege escalation.
8. Fail-open behavior.
9. Insecure defaults.
10. Session fixation.
11. Weak session invalidation.
12. Token leakage.
13. Token replay.
14. Excessive token lifetime.
15. Incorrect token validation.
16. Missing issuer checks.
17. Missing audience checks.
18. Algorithm confusion.
19. Incorrect signature verification.
20. Missing nonce or freshness checks.
21. Weak credential handling.
22. Weak password reset behavior.
23. Weak cryptography.
24. Hard-coded secrets.
25. Secrets exposed to clients.
26. Secrets exposed in logs.
27. Secrets included in artifacts.
28. Injection vulnerabilities.
29. SQL injection.
30. Command injection.
31. Template injection.
32. Expression injection.
33. Header injection.
34. Log injection.
35. Cross-site scripting.
36. Cross-site request forgery.
37. Server-side request forgery.
38. Open redirects.
39. Path traversal.
40. Unsafe archive extraction.
41. Unsafe file upload.
42. MIME confusion.
43. Insecure deserialization.
44. Prototype pollution.
45. XML external-entity processing.
46. Regular-expression denial of service.
47. Unbounded request bodies.
48. Unbounded queries.
49. Unbounded recursion.
50. Unbounded concurrency.
51. Unbounded fan-out.
52. Unbounded retries.
53. Missing rate limits.
54. Missing abuse controls.
55. Time-of-check/time-of-use defects.
56. Authorization races.
57. Weak CORS policy.
58. Missing security headers.
59. Host-header trust.
60. Cache poisoning.
61. Shared-cache data leakage.
62. Sensitive-data logging.
63. Error-message information leakage.
64. Debug endpoints exposed in production.
65. Administrative endpoints lacking extra safeguards.
66. Unsafe support impersonation.
67. Webhook signature weaknesses.
68. Replayable webhooks.
69. Dependency confusion.
70. Build-pipeline credential exposure.
71. Unsafe CI permissions.
72. Untrusted code execution.
73. Sandbox escape risk.
74. Insecure temporary-file handling.
75. Insecure randomness.
76. Personal-data overcollection.
77. Missing retention or deletion behavior.
78. Incomplete account deletion.
79. Data export leaking other users' information.
80. Audit-log tampering or omission.

For each security finding, include:

- Threat scenario.
- Attacker prerequisites.
- Affected assets.
- Exploit path.
- Impact.
- Existing mitigations.
- Missing mitigations.
- Safe reproduction guidance.
- Recommended fix.
- Defense-in-depth improvement.
- Regression-test strategy.
- Disclosure sensitivity.

Do not include harmful operational exploit instructions beyond what is necessary
to establish and fix the issue.
