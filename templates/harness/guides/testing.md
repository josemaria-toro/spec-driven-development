# Testing guide

## Mandatory test levels

Unit and integration tests are mandatory in **every** project. End-to-end (e2e) tests are mandatory **only for the frontend**. All required levels run in CI, and a missing level blocks the merge.

| Level | What it tests | Speed | Share | Applies to | Required in CI |
|---|---|---|---|---|---|
| Unit | Domain and use cases, with fake ports | ms | Majority | Backend and frontend | Every PR |
| Integration | Real adapters (PostgreSQL, RabbitMQ, contract APIs) | s | Moderate | Backend and frontend | Every PR |
| End-to-end | Critical user flows through the running UI | slow | Minimal | **Frontend only** | Every PR |

- A change must add or update tests at every required level it affects; "not applicable" needs a one-line justification in the PR.
- Frontend e2e covers the critical user flows; the list is kept in the stack sheet or spec and updated with each new critical flow.
- Backend has no e2e level: end-to-end behavior is covered by integration tests plus the frontend e2e suite.
- Skipping or disabling a required level is a guardrail exception and requires an ADR.

## Test frameworks by stack

| Stack | Framework |
|---|---|
| Backend Python | **pytest** (with pytest-cov, pytest-asyncio) |
| Backend C# | xUnit |
| Frontend React | Vitest + React Testing Library (unit/integration); **Playwright** (e2e, mandatory) |

## Rules

- Every behavior change includes tests in the same PR.
- A bug is fixed by first writing a test that reproduces it.
- Tests are deterministic: no dependence on time, real network, ordering or randomness (inject a `Clock`, fixed seeds).
- One test, one reason to fail; names describe the expected behavior.
- Arrange-Act-Assert (or Given-When-Then) structure.
- Test observable behavior, not implementation details.
- Mocks only at the boundaries (ports); do not mock the domain itself.
- Flaky tests are fixed or removed within days; they are not retried indefinitely.

## Test data

- Factories/builders instead of giant fixtures.
- Synthetic data; never real personal data.
- Each test leaves the environment clean.

## Coverage

- Minimum total coverage is **80%**, checked by unit tests before every commit (pre-commit hook) and again in CI; see "Coverage gate before every commit" in `guardrails.md`.
- Stacks may raise the threshold, never lower it; CI also fails if coverage drops.
- Coverage is an alarm, not a goal: prioritize business branches and edge cases.

## Security and non-functional tests

- Negative cases for authorization and input validation.
- Contract tests for consumed and exposed APIs.
- Performance and load tests on critical flows before significant releases.
