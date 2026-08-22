# C and C++ deep checks

Review applicable first-party C and C++ behavior for:

- Memory safety, ownership, lifetime, aliasing, bounds, integer overflow, signedness, alignment, and undefined or implementation-defined behavior.
- Resource acquisition and release, exception safety, partial construction, cleanup on all exits, file/socket ownership, and allocator boundaries.
- Concurrency, atomic ordering, data races, lock ordering, condition variables, shutdown, signal handling, and thread lifetime.
- Unsafe format strings, string termination, encoding, parsing, serialization, archive handling, and untrusted length/count fields.
- ABI and API compatibility, object layout, compiler and standard-library assumptions, conditional compilation, platform-specific code, and symbol visibility.
- Compiler-warning, sanitizer, hardening, optimization, and link settings; suppression quality; and test coverage of boundary conditions.

Do not treat style or use of lower-level constructs as a finding without demonstrating a violated invariant or material risk.
