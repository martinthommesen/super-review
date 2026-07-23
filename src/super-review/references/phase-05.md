# PHASE 5 — CORRECTNESS AND BUSINESS-LOGIC REVIEW

Review all meaningful first-party implementation for:

- Incorrect conditions.
- Incorrect comparisons.
- Reversed checks.
- Boolean-logic errors.
- Off-by-one errors.
- Incorrect defaults.
- Null, nil, undefined, or missing-value mishandling.
- Empty-collection behavior.
- Zero-value behavior.
- Incorrect ordering.
- Unstable ordering.
- Invalid assumptions about map iteration.
- Numeric overflow.
- Numeric underflow.
- Precision loss.
- Rounding errors.
- Currency errors.
- Unit-conversion errors.
- Date errors.
- Timezone errors.
- Daylight-saving errors.
- Clock-skew assumptions.
- Locale errors.
- Unicode normalization problems.
- Case-folding problems.
- Encoding errors.
- Path-handling errors.
- Platform-specific behavior.
- Mutable aliasing.
- Unintended shared state.
- Incorrect equality or hashing.
- Stale closure values.
- Incorrect async sequencing.
- Swallowed errors.
- Incorrect error translation.
- Success returned after failure.
- Cleanup skipped on early return.
- Incorrect retry conditions.
- Invalid state transitions.
- Missing enum or union handling.
- Serialization mismatches.
- Field-mapping errors.
- Pagination errors.
- Cursor errors.
- Filtering errors.
- Aggregation errors.
- Duplicate processing.
- Missing deduplication.
- Information loss.
- Silent coercion.
- Silent truncation.
- Non-deterministic behavior.
- Incorrect fallback behavior.
- Logic duplicated with behavioral drift.
- Conditions that are always true or false.
- Unreachable code.
- Feature combinations that cannot work.
- Configuration states that violate assumptions.

For suspicious behavior:

1. Find all callers.
2. Find all implementations.
3. Find all tests.
4. Inspect schemas.
5. Inspect configuration.
6. Inspect documentation.
7. Inspect related historical comments where available.
8. Establish intended behavior before labeling it a defect.

===============================================================================
