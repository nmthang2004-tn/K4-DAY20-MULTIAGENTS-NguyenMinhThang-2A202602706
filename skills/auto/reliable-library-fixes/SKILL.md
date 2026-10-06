---
name: reliable-library-fixes
description: Use when modifying an existing code package to fix behavior, formatting, or API-contract failures.
---
- Inspect the package, documentation, callers, and tests before editing; preserve existing files and public interfaces unless the requirements say otherwise.
- Translate each reported failure and documented behavior into an explicit expected result.
- Use decimal arithmetic for monetary values; parse supported symbols, separators, and accounting-style negative values deliberately.
- Apply the specified rounding mode explicitly rather than relying on binary floating-point or a language default.
- Use a standard CSV writer when producing CSV fields so quotes, delimiters, and embedded newlines are escaped correctly.
- Follow documented ordering and edge-case behavior; do not infer ordering from incidental input or container behavior.
- Add complete type annotations to public functions when required by package conventions or project rules.
- Add focused regression tests for each fixed behavior, including boundary cases and formatting.
- Update the changelog in the required section and format when the project asks for it.
- Run the relevant tests and then the full available suite; inspect failures before declaring the fix complete.