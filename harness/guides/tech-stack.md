# Tech stack guide

This guide defines **how the stack is chosen and governed**. Concrete choices live in `stacks/<name>.md`.

## Supported languages

| Area | Language / framework | Stack sheet |
|---|---|---|
| Backend | Python | `stacks/backend-python.md` |
| Backend | C# (.NET) | `stacks/backend-csharp.md` |
| Frontend | React (TypeScript) | `stacks/frontend-react.md` |

Each project uses **one** of these per area and declares it in its stack sheet. Any other language or framework requires an approved ADR (see "Changing the stack").

## Default platform services

| Need | Default | Notes |
|---|---|---|
| Relational database | **PostgreSQL** | Used unless an ADR justifies another engine. |
| Event/message broker | **RabbitMQ** | Used unless an ADR justifies another broker. |

- Access to both goes through ports/gateways (see `architecture.md`); the domain never knows the engine or the broker.
- Schema changes go through versioned migrations; messages have versioned, documented contracts.
- Consumers are idempotent and handle redelivery; every queue has a dead-letter queue.
- Credentials come from the environment (see `security.md`); TLS is required outside local.

## Admitted security tooling

These tools implement the vulnerability gate (see `guardrails.md`) and the OWASP verification (see `security.md`). They are admitted by default; any other scanner needs an ADR.

| Purpose | Tool | Scope | License |
|---|---|---|---|
| Secret scanning (pre-commit + CI) | **gitleaks** | All stacks | MIT |
| Dependency audit | **pip-audit** | Python | Apache-2.0 |
| Dependency audit | **`dotnet list package --vulnerable`** / NuGetAudit | C# | built into .NET SDK |
| Dependency audit | **`pnpm audit`** | React | built into pnpm |
| Dependency audit with severity data across ecosystems | **OSV-Scanner** | All stacks | Apache-2.0 |
| Dependency audit (OWASP) | **OWASP Dependency-Check** | All stacks (CI, optional) | Apache-2.0 |
| SAST | **Bandit** | Python | Apache-2.0 |
| SAST | **.NET Roslyn analyzers** (security rules, `CA` set) | C# | MIT |
| SAST | **eslint-plugin-security** | React | Apache-2.0 |
| DAST | **OWASP ZAP** | All stacks (test environments) | Apache-2.0 |
| Hook runner | **pre-commit** | All stacks | MIT |

Licenses are stated from memory and must be confirmed when the tool is first added. Tools run as development/CI tools only; they never become runtime dependencies.

## Criteria for adopting a technology

Before adding a library, framework or service, answer in the PR (or in an ADR if significant):

1. What problem does it solve that our current tools do not?
2. **Maintenance**: recent release, active community, more than one maintainer.
3. **License** compatible with the project (see the allowed list below).
4. **Security**: CVE history and a reasonable supply chain.
5. **Exit cost**: what would replacing it take? Isolate it behind a port if high.
6. **Size**: weight in transitive dependencies and in the final artifact.

## Licenses

- Allowed by default: MIT, BSD, Apache-2.0, ISC, MPL-2.0 (as a dependency).
- Require an ADR: LGPL, EPL, CC-BY and any license with special attribution terms.
- Forbidden unless an explicit ADR says otherwise: GPL/AGPL, SSPL, unidentified licenses.

## Dependency management

- Versions pinned through a lockfile committed to git.
- Automated updates (Dependabot/Renovate) with mandatory CI.
- Unused dependencies are removed; reviewed quarterly.
- One package manager per project.

## Supported versions

Use versions with active support (LTS when available). The minimum version of each runtime is declared in the stack file and in CI.

## Organization of `stacks/`

One file per technology/project, based on `stacks/_template.md`. Each one fixes: runtime and version, package manager, framework, linter/formatter, typing, testing and standard commands.

## Changing the stack

Changing the language, main framework or database requires an approved ADR.
