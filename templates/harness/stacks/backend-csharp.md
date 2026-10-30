# Stack: Backend — C#

## Summary

- **Purpose**: backend services and APIs in C# on .NET.
- **Architecture**: <hexagonal | clean architecture> (see `guides/architecture.md`; declare one per project).

## Runtime and tooling

| Element | Choice | Minimum version |
|---|---|---|
| Language / runtime | C# on .NET | latest LTS (≥ .NET 10) |
| Package manager | NuGet (central package management, lock files enabled) | — |
| Framework | ASP.NET Core (Minimal APIs or controllers, one per project) | — |
| Database | PostgreSQL (default) via Npgsql / EF Core provider | — |
| Message broker | RabbitMQ (default) via RabbitMQ.Client | — |
| Linter / formatter | `dotnet format` + Roslyn analyzers (warnings as errors) | — |
| Typing | Nullable reference types enabled | — |
| Testing | xUnit (unit + integration), Testcontainers | — |
| Layer checks | NetArchTest or ArchUnitNET | — |

## Standard commands

```bash
dotnet restore --locked-mode     # install
dotnet format --verify-no-changes  # format check
dotnet build -warnaserror        # lint + types
dotnet test tests/<App>.UnitTests --collect:"XPlat Code Coverage"  # unit + coverage
dotnet test tests/<App>.IntegrationTests     # integration (containers)
dotnet run --project src/<Project>.Api       # run locally
dotnet list package --vulnerable --include-transitive  # dependency audit
```

## Folder structure

```
src/
  <App>.Domain/ <App>.Application/ <App>.Infrastructure/ <App>.Api/   # hexagonal
  # or: <App>.Entities/ <App>.UseCases/ <App>.Adapters/ <App>.Frameworks/  # clean architecture
tests/
  <App>.UnitTests/ <App>.IntegrationTests/ <App>.ArchitectureTests/
Directory.Build.props
Directory.Packages.props
```

## Quality

- Minimum coverage: 80%, gate before each commit and in CI: unit tests with the Coverlet threshold (`-p:CollectCoverage=true -p:Threshold=80 -p:ThresholdType=line`, via `coverlet.msbuild`).
- `<Nullable>enable</Nullable>` and `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>` in `Directory.Build.props`.
- Layering is enforced by project references (inner projects never reference outer ones) **and** by architecture tests.
- Vulnerability gate (pre-commit and CI; high/critical vulnerabilities and any secret block): `dotnet list package --vulnerable --include-transitive` (the hook fails when its output reports a package with High or Critical severity; the command alone returns exit code 0) and secret scan with gitleaks. Consider `NuGetAudit` set to warnings-as-errors in `Directory.Build.props`.

## Approved dependencies

| Library | Use | License |
|---|---|---|
| ASP.NET Core | HTTP API | MIT |
| Entity Framework Core | Persistence and migrations | MIT |
| Npgsql (+ EF Core provider) | PostgreSQL driver | PostgreSQL License |
| RabbitMQ.Client | RabbitMQ client | Apache-2.0 / MPL-2.0 |
| Serilog | Structured logging | Apache-2.0 |
| FluentValidation | Boundary validation | Apache-2.0 |
| xUnit | Test framework (unit + integration) | Apache-2.0 |
| Testcontainers (.NET) | PostgreSQL/RabbitMQ in integration tests | MIT |
| NetArchTest | Architecture tests | MIT |
| NuGetAudit / `dotnet list package --vulnerable` | Dependency vulnerability audit (pre-commit + CI) | built into .NET SDK |
| .NET Roslyn analyzers (security rules) | SAST (build + CI) | MIT |
| OSV-Scanner | Cross-check of vulnerability data with severity (optional) | Apache-2.0 |
| gitleaks | Secret scanning (pre-commit + CI) | MIT |
| pre-commit | Hook runner | MIT |

## Specifics

- Use `async`/`await` end to end and pass `CancellationToken` through every I/O call.
- Domain/entities projects have no reference to ASP.NET Core or EF Core.
- Built-in DI container is the composition root, wired only in the outermost project.
- Configuration via the options pattern with validation on start.
- xUnit conventions: one test class per unit under test; `[Fact]` for single cases and `[Theory]` with `[InlineData]` for case tables; shared setup via constructor and `IClassFixture<T>` / `ICollectionFixture<T>` (expensive resources such as containers), not inheritance; use the built-in `Assert` unless an ADR approves an assertion library; keep tests free of static mutable state (xUnit runs test classes in parallel).
- Integration tests run PostgreSQL and RabbitMQ in containers (Testcontainers), never against shared environments.
