# Architecture guide

## Supported architectures

Two styles are supported. Each project **declares one** in its `stacks/<name>.md` and does not mix them.

| Style | Pick it when |
|---|---|
| **Hexagonal** (ports and adapters) | The focus is isolating the core from many external systems (DBs, APIs, queues, UIs). |
| **Clean Architecture** | The focus is a rich domain with explicit, layered use cases and strict inward dependencies. |

Any other style (CQRS, event sourcing, microservices, etc.) is allowed **only with an ADR** showing the concrete problem it solves. Default deployment shape: modular monolith.

## Shared rules (both styles)

- **Dependencies point inward**: the domain imports nothing from outer layers or from frameworks. Verified automatically (see `guardrails.md`).
- Outer layers depend on inner ones through interfaces defined by the inner layer (dependency inversion), wired by dependency injection.
- High cohesion within a module, low coupling between modules; modules talk through public interfaces only.
- Data boundaries (DTOs) are validated at the edge; inside the domain, data is already valid.
- Prefer composition over inheritance.
- Operations with side effects are idempotent, or state why they are not.

## Hexagonal (ports and adapters)

```
interfaces/      # inbound adapters: HTTP, CLI, events, UI
application/     # use cases; orchestrate, hold no business rules
domain/          # entities, value objects, rules; no external dependencies
infrastructure/  # outbound adapters: DB, external APIs, queues, files
```

- A **port** is an interface owned by the domain/application (`UserRepository`, `Clock`, `Mailer`).
- An **adapter** implements it in `infrastructure/` (outbound) or drives the use cases from `interfaces/` (inbound).
- Dependency rule: `interfaces → application → domain`; `infrastructure → application/domain`.

## Clean Architecture

```
entities/        # enterprise-wide business rules; no dependencies
use_cases/       # application-specific rules; define input/output boundaries and gateway interfaces
adapters/        # controllers, presenters, gateways/repositories implementations
frameworks/      # frameworks and drivers: web, DB, UI, config (outermost, kept thin)
```

- Dependency rule: `frameworks → adapters → use_cases → entities`; never the reverse.
- Use cases expose input/output boundaries; presenters shape the output, controllers shape the input.
- Gateways are interfaces declared in `use_cases/` and implemented in `adapters/`.
- Data crossing a boundary is a plain data structure, never an entity or a framework object.

## Equivalence

| Hexagonal | Clean Architecture |
|---|---|
| `domain/` | `entities/` |
| `application/` | `use_cases/` |
| `interfaces/` + `infrastructure/` | `adapters/` + `frameworks/` |
| Port | Boundary / gateway interface |

Folder names may follow the project's language conventions, but the layers and the dependency rule must stay identifiable and checkable.

## APIs

- Contract first (OpenAPI/JSON Schema) and explicit versioning.
- Uniform error format (e.g. RFC 9457 Problem Details).
- Pagination, limits and timeouts on every collection and external call.
- Breaking changes require a new version and an ADR.

## Persistence

- Versioned, reversible migrations; never edit a migration that has been applied.
- Transactions scoped to the use case.
- The DB schema is not exposed outside the service.

## Decisions

Every decision that is costly to reverse is recorded in `adr/` (see `adr/0000-template.md`). Changing a project's declared architecture requires an ADR.
