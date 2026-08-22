# Template D: positive pattern

Use this for important behavior that should remain and serve as a pattern elsewhere.

```markdown
## [POS-001] Positive pattern title

Record type: Positive pattern
ID category: POS
Primary component: <stable subsystem or workflow>
Identity statement: <stable invariant or design quality being preserved>
Fingerprint: sha256:<digest>
Status: Active

Classification: Positive pattern worth preserving
Severity or priority: Informational
Confidence: <Confirmed | High | Medium | Low>
Affected components: <where the pattern exists and where it may apply>

Evidence:
- <exact paths, tests, contracts, operational behavior, or workflow evidence>.

Why it is valuable:
<Correctness, security, reliability, clarity, workflow, or operational value.>

Why the current design is appropriate:
<Scale, ownership, compatibility, simplicity, and tradeoff evidence.>

Invariants to preserve:
<Behavior future changes must retain.>

Tests and controls that protect it:
<Current tests, schema constraints, monitoring, review gates, or missing protection.>

Risks of changing it:
<Likely regressions, compatibility breakage, or lost properties.>

Reuse opportunities:
<Specific locations where the pattern is applicable, or Not applicable with reason.>

Scope limits:
<Where copying the pattern would be inappropriate.>
```
