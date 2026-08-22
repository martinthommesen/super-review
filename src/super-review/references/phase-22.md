# Phase 22: prioritization and roadmap

Prioritize findings using evidence, not arbitrary scoring.

For defects, consider:

- Severity.
- Likelihood.
- Reach.
- Exploitability.
- Data impact.
- User impact.
- Operational impact.
- Detectability.
- Recoverability.
- Confidence.
- Fix complexity.
- Compatibility risk.

Use these severity levels:

### Critical

- Immediate risk of major security compromise, irreversible data loss,
  substantial cross-tenant exposure, widespread outage, or similarly severe
  consequences.
- Should block release or trigger immediate remediation.

### High

- Serious correctness, security, data-integrity, reliability, or operational
  risk.
- Likely to affect important workflows or create substantial damage.
- Should be prioritized urgently.

### Medium

- Material defect or design problem with bounded impact.
- Should be scheduled, but does not normally require emergency action.

### Low

- Limited-impact issue, maintainability problem, narrow edge case, or
  defense-in-depth opportunity.

### Informational

- Observation, positive pattern, optional optimization, or recommendation
  without a current defect.

For feature and improvement recommendations, consider:

- Strength of evidence.
- User or operator value.
- Risk reduction.
- Workflow reach.
- Strategic fit inferable from the repository.
- Complexity removed.
- Maintenance burden reduced.
- Delivery effort.
- Migration risk.
- Ongoing operating cost.
- Reversibility.
- Dependencies.

Do not fabricate numeric RICE, ROI, adoption, revenue, or effort values.

Use qualitative priority groups:

### Now

- Critical or high-severity issues.
- Low-risk fixes with immediate material value.
- Required foundations for other work.

### Next

- Important structural improvements.
- High-value workflow improvements.
- Strongly supported feature additions.
- Planned deprecations requiring preparation.

### Later

- Valuable but non-urgent improvements.
- Scale-dependent optimization.
- Larger redesigns requiring evidence or sequencing.

### Investigate

- Plausible opportunities lacking usage, product, performance, or operational
  evidence.
- Include the exact evidence-gathering plan.

### Do not pursue

- Recommendations whose cost, risk, or complexity outweigh likely value.
- Attractive but unnecessary rewrites.
- Premature scaling work.
- Features unsupported by repository evidence.
