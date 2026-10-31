# Design

## Context

See `proposal.md` for the motivation. Observed state:

- The render plan already selects `apps/<kind>/<technology>/**` by the technology of each kind and drops the technology directory (`add-application-skeletons`). A `templates/apps/backend/csharp/` directory therefore renders into `apps/backend/` with no change to `domain/render_plan.py`, and the catalogue already lists `csharp` for the backend.
- `templates/apps/backend/python/` is the reference for what a backend skeleton must achieve: fixed names, verbatim files, one example per layer, a committed lockfile, and a test in `apps/backend/tests/generated/` that renders a project and runs every gate. `skeletons.yml` runs that test.
- The generated `dependabot.yml` already has a `nuget` block for `/apps/backend`.
- `harness/stacks/backend-csharp.md` and `harness/guides/development-csharp.md` fix the tools, commands, folder structure and naming. Hexagonal architecture is used, as in the Python skeleton.
- This environment has the .NET 10 runtime but **no SDK** (`dotnet --list-sdks` is empty), so nothing can be built or restored here until one is installed. GitHub-hosted runners have the SDK.

## Goals / Non-Goals

**Goals:**

- A generated C# backend passes the gates of its stack sheet on the first commit, and the CI job of this repository proves it.
- Rendering stays deterministic, offline and free of project values in code.

**Non-Goals:**

- An ASP.NET Core host, an `Api` project or any runtime adapter (see the proposal).
- Parameterizing the skeleton (namespaces, optional features).

## Decisions

1. **Layout under `templates/apps/backend/csharp/`, rendered to `apps/backend/`.** Files, relative to `apps/backend/`:
   - `App.slnx`, `global.json`, `Directory.Build.props`, `Directory.Packages.props`, `.editorconfig`, `.gitignore`;
   - `src/App.Domain`, `src/App.Application`, `src/App.Infrastructure`, each with its `.csproj` and `packages.lock.json`;
   - `tests/App.UnitTests`, `tests/App.IntegrationTests`, `tests/App.ArchitectureTests`, each with its `.csproj`, `packages.lock.json` and one test class.

   The stack sheet's `<App>.Api` project is omitted because there is no runtime adapter; the outermost project is `Infrastructure`, as `infrastructure` is the outermost package of the Python skeleton. Alternative: add an empty `Api` project now. Rejected: it would pull ASP.NET Core into the skeleton for no behavior, and adding it later is an additive change.

2. **Fixed names and verbatim files.** Solution `App`, root namespace `App` (`App.Domain`, ...), no `.tmpl` files, no project values. This keeps every skeleton byte-identical, keeps the lock files valid, and avoids deriving a namespace from a repository name that can start with a digit. Same trade-off as decision 2 of `add-application-skeletons`: a generic name, renamed later by a normal refactor. Alternative: derive names from the project name. Rejected for the same three reasons.

3. **`.slnx` solution format and an SDK pin.** `global.json` pins the SDK feature band of .NET 10 (the LTS the stack sheet requires) with `rollForward: latestFeature`, so a newer patch is accepted and an older SDK is refused with a clear message. `.slnx` is the default solution format of the .NET 10 SDK and is plain XML. Alternative: classic `.sln`, which has GUIDs and is noisier; rejected, since the SDK is pinned to 10 anyway.

4. **Build rules in `Directory.Build.props`, versions in `Directory.Packages.props`.**
   - `Nullable` enabled, `TreatWarningsAsErrors`, `AnalysisLevel` `latest-recommended` with `EnforceCodeStyleInBuild`, `ImplicitUsings` disabled (explicit usings, as the guide prefers), `RestorePackagesWithLockFile` true.
   - `NuGetAudit` on, `NuGetAuditMode` `all` (transitive packages included) and `NuGetAuditLevel` `high`, with NU1903 and NU1904 (high and critical advisories) as errors, so a vulnerable locked package fails restore and build, which is the guardrail's behavior. Weekly CI shows it when an advisory is published later.
   - Central package management with versions only in `Directory.Packages.props`. The stack sheet requires lock files; they are generated once with `dotnet restore --force-evaluate` in a scratch copy and committed, so rendering stays offline.

   Two consequences found while building it. `GenerateDocumentationFile` is on for the whole solution because the unused-usings rule (`IDE0005`) only runs in the build when it is; missing XML documentation on public members (`CS1591`) is then an error through warnings-as-errors. A `tests/Directory.Build.props` that imports the root one exempts the test projects from `CS1591` and from `CA1707`, because the development guide names tests `Method_Condition_Expected`. The use case example is a static class: with no dependency to hold, an instance member would raise `CA1822`; a use case with ports becomes a normal class when it gets its first port.

   Alternative for audit: only the `dotnet list package --vulnerable` command in CI, as the stack sheet allows. Rejected: a build that already fails on high advisories gives the same signal in the developer's inner loop at no extra tooling.

5. **Layers enforced twice.** Project references only point inward (`Application` -> `Domain`; `Infrastructure` -> `Application`, `Domain`), so a `Domain` that references an outer project is a circular reference and fails the build. `App.ArchitectureTests` (NetArchTest) asserts the dependency direction and that `Domain` and `Application` depend on none of: `Microsoft.AspNetCore`, `Microsoft.EntityFrameworkCore`, `Npgsql`, `RabbitMQ.Client`, `System.Net.Http`, `System.Data`. The Python skeleton's forbidden list plays the same role. Alternative: ArchUnitNET. Rejected: the stack sheet lists NetArchTest as the approved library.

6. **Minimal content, one example per layer.** `Domain`: a `Greeting` rule that builds a greeting for a name, using the default for a blank one. `Application`: a `GreetUseCase` calling it. `Infrastructure`: an empty project that references the inner layers, ready for adapters. Tests: `GreetingTests` and `GreetUseCaseTests` as unit tests with `[Theory]`, one integration test that exercises the use case through the public API, and the architecture tests. No containers: nothing talks to PostgreSQL or RabbitMQ yet, so Testcontainers is not added. Test names follow `Method_Condition_Expected`; classes are `sealed`, types default to the narrowest access modifier.

7. **Coverage gate.** `coverlet.msbuild` in `App.UnitTests` with `Threshold` 80 and `ThresholdType` `line` set in the project file, so `dotnet test tests/App.UnitTests -p:CollectCoverage=true` fails below 80% without relying on a command-line flag. Alternative: the `XPlat Code Coverage` collector from the stack sheet's command list; it produces a report but has no threshold, so the stack sheet's own gate paragraph (Coverlet threshold) wins.

8. **Test dependencies.** `xunit`, `xunit.runner.visualstudio`, `Microsoft.NET.Test.Sdk`, `coverlet.msbuild` and `NetArchTest.Rules`, all pinned centrally. The first and the last two are in the approved table; the test host (`Microsoft.NET.Test.Sdk`) and the xUnit runner are required for any xUnit project to run under `dotnet test` and are not listed. They are justified in the PR with the criteria of `tech-stack.md` (maintained by Microsoft and the xUnit project, MIT and Apache-2.0, no runtime use); if review prefers, the approved table gets them in a separate `chore`.

9. **The generated test gains the C# gates.** `test_generated_skeletons.py` renders a project with a C# backend and, with `dotnet` available, runs `dotnet restore --locked-mode`, `dotnet format --verify-no-changes`, `dotnet build -warnaserror --no-restore`, the unit tests with coverage, the integration tests and the architecture tests, then `dotnet list package --vulnerable --include-transitive` (failing when the output reports a High or Critical package, since the command exits 0 either way) and that no `packages.lock.json` changed. Negative checks: a `Domain` file using `System.Net.Http.HttpClient` fails the architecture tests (no extra package is needed to prove the rule), and a `Domain` project reference to `Infrastructure` fails the build. As for the other tools, a missing `dotnet` skips the test locally and fails it when `CI=true`.

10. **Workflow change is a setup step.** `skeletons.yml` adds `actions/setup-dotnet` with the version taken from the skeleton's `global.json`, and nothing else; path filters already include `templates/apps/**`. Alternative: a second workflow only for C#. Rejected: one job proving every skeleton is simpler, and the job is not required by the ruleset.

11. **Verification without an SDK here.** Apply starts by installing a .NET 10 SDK for the current user outside the repository, using Microsoft's official `dotnet-install` script reviewed before it runs, and confirms `dotnet --list-sdks`. If that is not possible (no network, no approval), the skeleton is built and verified through the CI job on the pull request and the tasks that need a local run stay unticked until the run passes. The skeleton is never committed unverified.

## Risks / Trade-offs

- [Skeleton configuration drifts from the Python and React skeletons or from the stack sheet] → The generated test runs the real gates on every skeleton change; compare by hand when the stack sheet changes.
- [Frozen dependencies age and a published advisory fails restore on day one] → Same as the other skeletons: the weekly run flags it and the refresh is a `chore` PR; the audit scenario of the spec covers release time.
- [`NuGetAuditLevel` high with errors makes a freshly rendered project fail after a new advisory] → Intended by the vulnerability gate; the README of the generated project explains how to refresh lock files.
- [Lock files differ by SDK or platform] → Restore is run in the CI image the job uses; `packages.lock.json` has no paths or hashes of the host, and the test fails if restore changes it.
- [Member ordering of `development-csharp.md` is not machine-enforced] → No analyzer in the approved list enforces it; the skeleton follows it by hand and the rule stays a review item. Adding StyleCop would need its own change and approval.
- [A package outside the approved table (test host, runner)] → Justified in the PR (decision 8); an ADR only if review rejects them.
- [Namespace `App` collides with user code] → Same default as the Python package; renaming is a normal refactor.
- [`.slnx` is recent and some tools ignore it] → The SDK is pinned to 10 and the standard commands (`restore`, `build`, `test`, `format`) accept it; the generated test proves them.

## Open Questions

- Whether to add `Microsoft.NET.Test.Sdk` and `xunit.runner.visualstudio` to the approved dependencies table of the stack sheet can be answered in review without changing specs, approach or tasks.
- Adding an `Api` project with ASP.NET Core belongs to the first change that needs an HTTP adapter.
