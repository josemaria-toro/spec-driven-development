# Security guide

Baseline: OWASP. Security by design, not a final review.

## OWASP standards adopted

| Standard | How it is used |
|---|---|
| **OWASP ASVS** (Application Security Verification Standard) | Requirements baseline. Default target: **Level 2**; Level 3 for systems handling highly sensitive data or critical functions (decided in an ADR). Requirements relevant to a change are referenced in its OpenSpec proposal. |
| **OWASP Top 10** (latest published edition) | Awareness and review checklist: every PR review and threat model considers these risks. |
| **OWASP API Security Top 10** | Applied to every HTTP/event API the project exposes. |
| **OWASP Proactive Controls** | Guidance for developers on secure patterns while coding. |
| **OWASP Cheat Sheet Series** | Reference for concrete implementation details (auth, sessions, input validation, logging, secrets, etc.). When in doubt, follow the cheat sheet. |
| **OWASP Top 10 for LLM Applications** | Applies to any feature that uses an LLM (prompt injection, insecure output handling, excessive agency, data leakage). |

### Top 10 risks mapped to this harness

| Risk theme | Harness control |
|---|---|
| Broken access control | Server-side authorization, deny by default, negative tests (see Authentication and authorization) |
| Cryptographic failures | TLS 1.2+, encryption at rest, no custom crypto (see Personal data) |
| Injection | Parameterized queries, input validation at the boundary, output encoding (see Input and output) |
| Insecure design | Threat modeling for new features, hexagonal/clean boundaries, ADRs (see `architecture.md`) |
| Security misconfiguration | Secure defaults, debug off, headers, CORS, rate limiting (see Secure configuration) |
| Vulnerable and outdated components | Lockfiles, audit in CI, license/maintenance review (see Dependencies; `tech-stack.md`) |
| Identification and authentication failures | Standard libraries, short-lived tokens, revocation |
| Software and data integrity failures | Pinned CI actions and images, reviewed dependencies, signed release tags (see `git-workflow.md`) |
| Security logging and monitoring failures | Structured logs with correlation, alerts on security events, no secrets/PII in logs (see `development.md`) |
| Server-side request forgery (SSRF) | Allow-list outbound destinations, validate and resolve URLs, block internal ranges |

The numbering of the Top 10 changes between editions, so the mapping is by theme; review it when a new edition is published.

### Verification

- **Threat modeling** for every new feature or architecture change that crosses a trust boundary; recorded in the OpenSpec `design.md` or an ADR.
- **SAST, dependency and secret scanning** in CI (see `guardrails.md`); OWASP Dependency-Check or an equivalent audit tool is acceptable for dependencies.
- **DAST** with OWASP ZAP against a test environment before significant releases.
- **Security tests**: negative authorization and validation cases are part of unit/integration tests (see `testing.md`).
- High/critical dependency vulnerabilities and any detected secret block the commit (pre-commit) and the merge (CI); medium/low are triaged and fixed within 30 days.
- Findings from SAST and DAST are triaged by severity; high and critical block the merge or the release.

## Secrets

- **Never** in the repository, logs, tests or images. Inject them through the environment or a secrets manager.
- The real `.env` is in `.gitignore`; only `.env.example` without values is committed.
- Secret scanning in pre-commit and CI. A leaked secret is considered compromised: it is **rotated** (deleting the commit is not enough).

## Authentication and authorization

- Do not implement your own cryptography or authentication; use standard libraries/services.
- Authorization is checked server-side on every operation (deny by default).
- Least privilege for users, services and tokens.
- Short-lived sessions/tokens with the possibility of revocation.

## Input and output

- All external input is hostile: validate type, length, range and format at the boundary.
- Parameterized queries; never concatenate SQL/commands/templates with user input.
- Encode output for its context (HTML, URL, SQL, shell).
- File uploads: size limits, type verified by content, storage outside the web root.

## Personal data

- Collect the minimum necessary; define retention and deletion.
- Classify data (public, internal, confidential, personal) and protect it accordingly.
- Encryption in transit (TLS 1.2+) and at rest for confidential data.
- No real personal data in development environments or logs.

## Dependencies and supply chain

- **Vulnerability check before every commit** (pre-commit): dependency audit plus secret scan; high/critical vulnerabilities and any secret block the commit, medium/low are warnings to triage (see "Vulnerability gate before every commit" in `guardrails.md`).
- The same audit runs in CI and on a schedule, so newly published vulnerabilities are caught.
- Lockfiles, reproducible installs and review of new dependencies.
- Minimal base images pinned by digest.
- CI actions pinned by version/SHA.

## Secure configuration by default

- HTTPS required, security headers, restrictive CORS, rate limiting.
- Debug mode off outside local.
- Generic error messages to the client; detail only in logs.

## Security review

Every PR that touches authentication, authorization, personal data handling, cryptography, file uploads or dependencies requires the security checklist to be completed and ticked in the PR. The checklist is derived from the OWASP Top 10 themes and the ASVS requirements relevant to the change:

- [ ] Access control enforced server-side, with negative tests.
- [ ] Input validated, output encoded, queries parameterized.
- [ ] No secrets or personal data in code, logs or errors.
- [ ] Crypto and TLS use standard, current libraries and settings.
- [ ] New dependencies reviewed (license, maintenance, vulnerabilities).
- [ ] Outbound requests restricted (SSRF) and security events logged.
- [ ] Threat model updated if a trust boundary changed.

## Incidents

If you suspect a vulnerability or leak: stop the affected deployment, **do not discuss it in public channels**, notify the security owner, rotate credentials and write a blameless postmortem.
