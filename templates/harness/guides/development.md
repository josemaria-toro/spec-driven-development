# Development guide

Language-agnostic rules. Language-specific rules (best practices, naming, member ordering, imports/usings, dependencies, cleanliness) live in `development-python.md`, `development-csharp.md` and `development-react.md`.

## Principles

- **Clarity over cleverness**: code is read more often than it is written.
- **Small changes**: one purpose per change, reviewable in minutes.
- **Simplicity**: do not add abstractions, configuration or layers "just in case" (YAGNI).
- **Quality ownership**: whoever writes the code writes its tests and documentation.

## Code style

- Formatting and linting are automatic; style is not debated in review (see `stacks/`).
- Names express business intent; avoid ambiguous abbreviations.
- Short functions with a single responsibility; avoid more than 3 levels of nesting.
- Comments explain the **why**, not the what. Dead or commented-out code is deleted.
- No magic numbers or strings: use named constants.
- Everything is written in English: identifiers, comments, docs, commit messages.

## Error handling

- Fail early with actionable messages.
- Do not catch exceptions to ignore them; catch only what you know how to handle.
- Domain errors are explicit types, distinct from technical errors.
- Never include secrets or personal data in error messages or logs.

## Logging and observability

- Structured logs (JSON) with level, correlation (`request_id`) and minimal context.
- Levels: `ERROR` requires action; `WARN` recoverable anomaly; `INFO` business events; `DEBUG` diagnostics only.
- Every external operation (HTTP, DB, queues) has a timeout and metrics.

## Configuration

- Per-environment configuration through variables; nothing environment-specific in code.
- Validate configuration at startup and fail if anything required is missing.
- Secure defaults.

## Definition of Done

A change is done when:

- [ ] Functional changes have an approved OpenSpec change (`guides/openspec.md`) and it validates; it is archived after merge.
- [ ] It meets the specification and its acceptance criteria.
- [ ] It has unit and integration tests (and e2e for frontend changes) for what it affects, and they would fail without the change.
- [ ] Lint, types and tests pass in CI, coverage is ≥ 80% and the vulnerability check reports no high/critical vulnerability or secret (the pre-commit gates passed without bypassing them).
- [ ] Frontend changes are responsive and meet WCAG 2.2 AA (automated checks green and manual keyboard/screen-reader check noted).
- [ ] No secrets, and no new dependencies without justification.
- [ ] Documentation and ADR updated where applicable.
- [ ] Reviewed by another person (or a documented self-review when working alone).
