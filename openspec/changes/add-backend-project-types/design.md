# Design

## Context

See `proposal.md` for the motivation. Observed state:

- `ProjectSpec` (`domain/project_spec.py`) holds the typology, one `Application(kind, technology)` per kind and the agent; its canonical form carries `SCHEMA_VERSION = 1`. The catalogue (`domain/catalogue.py`) maps kinds to technologies and technologies to ecosystems and stack sheets.
- The render plan selects `apps/<kind>/<technology>/**` by the technology of the kind and drops the technology directory (`add-application-skeletons`). Templates see the values of their own kind as `application` (`domain/render_context.py`).
- `add-csharp-application-skeleton` (proposed, not applied) adds one C# skeleton directly under `templates/apps/backend/csharp/`: layered core, three test projects, build rules, lock files, no entry project. Its design is the base of this one; **it must be applied and archived first**.
- The stack sheet `backend-csharp.md` lists `<App>.Api` among the hexagonal projects and offers no folder structure for a console tool or a library.

## Goals / Non-Goals

**Goals:**

- A technology-neutral catalogue of project types and the mechanism that selects templates by it, so that adding a technology's types is only templates plus one catalogue entry.
- Three C# skeletons, each passing the gates of the stack sheet.
- No effect on Python, React or the hashes beyond the one-time schema version change.

**Non-Goals:**

- The Python project types (`add-python-project-types`), runtime adapters or authentication (see the proposal).
- A shared-source mechanism between the three skeletons.

## Decisions

1. **The project type is a field of the spec, not a technology or a typology.** `project_type` is a top-level optional field with the catalogue `api`, `console`, `library`, valid when the backend technology offers project types (`TECHNOLOGY_PROJECT_TYPES` in the catalogue: C# today, Python in `add-python-project-types`). The catalogue is technology-neutral on purpose, because the project creator offers one list of types whatever the language; a technology without types rejects the field instead of silently ignoring it. Alternatives: technologies `csharp-api`, `csharp-console`, `csharp-library`, which break every stored `csharp` spec, the ecosystem and stack-sheet maps and the Dependabot mapping for no gain; new typologies `console` and `library`, which model the type as an application kind and then need kinds, plans and validation for something that is a variant of one technology. A field touches the spec, the plan and the context, and nothing else.

2. **Default `api`, resolved when the spec is built.** The most common backend is a service, so an omitted type means `api`; `Application` carries the resolved type (`None` for a technology that offers none), so the canonical form always holds the explicit value and an omitted type and an explicit `api` hash alike. The canonical form adds `project_type` only for a backend that has one, and `SCHEMA_VERSION` becomes 2 because the meaning of a spec changes; every hash changes once, which is acceptable because nothing persists hashes yet. A combination such as `fullstack` with `console` is allowed: rejecting it would be a product rule nobody asked for.

3. **Three self-contained directories, selected by the render plan.** Layout under `templates/apps/backend/csharp/`: `library/`, `console/`, `api/`, each a full skeleton. A first segment under a technology directory that is a project type is a project-type directory when the technology declares project types (`TECHNOLOGY_PROJECT_TYPES`, only `csharp` in this change): it is selected when it equals the spec's project type and skipped otherwise, and is dropped from the destination. Files directly under `csharp/` stay shared by every type (none today). Restricting the rule to technologies that declare types keeps a folder called `library` inside another skeleton from being dropped. Alternatives: shared base files plus per-type overlays (the solution file and the integration test project differ per type, so the overlay would replace more than it shares and need a collision rule); a manifest of files per type (one more format). Duplication across the three directories (build props, `.editorconfig`, the core) is the price, as with the Python and React skeletons, and the generated test is the drift detector.

4. **`library` is the base skeleton, packable.** The files of the base C# skeleton move into `library/`; `IsPackable` is true for the layer projects that form the public API and the tests stay unpackable; `GenerateDocumentationFile` is on and missing documentation (CS1591) is an error through the existing warnings-as-errors rule. No package id, authors or repository URL are set: they are project values, and the README of the generated project says to set them before publishing. The unit tests keep the base layout.
 `IsPackable` is set explicitly in the root build properties of `library` and set to false in those of `console` and `api`, whose layer projects are not meant to be published.
5. **`console` adds an `App.Console` entry project.** `Program.cs` is a few lines that call `Cli.Run(args, standardOutput, standardError)`; `Cli` is a plain class holding the argument handling, so the integration test runs it in-process with `StringWriter`s and checks the exit code, with no process spawning. Arguments are parsed by hand: zero or one argument is valid; anything else prints usage to standard error and returns 2. `System.CommandLine` is not in the approved table and the example does not need it. `App.Console` is the composition root and the only project allowed to reference `Infrastructure`; architecture tests assert nobody references it.
 The three argument scenarios of `Cli` are unit tests (in process, which also gives the project its coverage), and the integration tests run the real executable through the .NET host to check the same results on the real streams and exit code.
6. **`api` adds an `App.Api` entry project.** ASP.NET Core minimal API with one `GET /greetings/{name}` endpoint over the use case, composition root of the solution. Secure defaults: `UseHttpsRedirection`, `UseHsts` outside development, no developer exception page outside development, `IExceptionHandler` plus `AddProblemDetails` so every failure is a problem-details body without exception data, and input validation at the edge (name length limit, 400 with the invalid field named). The core still has no ASP.NET reference; `FrameworkReference` to `Microsoft.AspNetCore.App` lives only in `App.Api`. The integration tests use `WebApplicationFactory<Program>` (in-memory host, no sockets) and need `Microsoft.AspNetCore.Mvc.Testing`; a `public partial class Program` exposes the entry point to it. No authentication, database or broker, as in the base skeleton.
 While building it: the endpoint depends on a small `IGreeter` port with a `GreeterService` implementation registered in the composition root, so the integration tests can replace it with a failing one and prove that a failure returns a generic server error; the security headers are set in `OnStarting`, because the exception handler clears the response and would drop headers set earlier; `Program.cs` holds the whole composition and is excluded from the unit-test coverage by file (an entry point, reviewed here), while the endpoint, the greeter and the middleware are unit-tested and the host is exercised by the integration tests; HSTS is asserted on an HTTPS request to a non-local host, because HSTS skips `localhost` by default.
7. **Architecture tests per type.** The three test projects exist in every type. In `console` and `api`, `App.ArchitectureTests` also asserts that `Domain`, `Application` and `Infrastructure` do not depend on the entry project; the forbidden-library list for `Domain` and `Application` is the one of the base skeleton. The `Domain` -> entry project reference scenario is proven by the build (circular reference).

8. **Rendering context and README.** `application.project_type` is added to the values of the backend application (empty for other technologies) and the per-kind README prints `Project type: <value>` when it is set, escaped like the other values. The Dependabot template is unchanged: all three types use the `nuget` ecosystem at `/apps/backend`.

9. **The generated test runs the gates of every type.** `test_generated_skeletons.py` parametrizes the C# gates of the base change over the three project types (render, restore in locked mode, format, build, unit with coverage, integration, architecture, audit, lock files unchanged), plus: `dotnet pack` for `library`, a run of `App.Console` with valid and invalid arguments, and the api checks that live in its integration tests. Cost: three solutions per run; each restores from the NuGet cache, so the job grows by minutes, not by an order of magnitude. Alternative: only run the type touched by the pull request; rejected, because the shared configuration is duplicated and a drift would go unseen.

10. **Harness documents.** `harness/stacks/backend-csharp.md` and its copy in `templates/harness/stacks/` gain the folder structure of the console and library types next to the hexagonal one. This is the approved harness change of the proposal; templates stay independent of the repository's harness, so both files are edited and both are tested by the existing harness-copy tests.

## Risks / Trade-offs

- [Three copies of the same configuration drift apart] → The generated test runs the real gates on each; the three copies are compared when a stack sheet changes.
- [Changing `SCHEMA_VERSION` invalidates stored hashes] → Nothing stores hashes yet (the run engine is later); the spec scenarios pin the new equalities, and the version is a single constant.
- [An `api` default surprises someone who wants a library] → The default is stated in the spec and the README line names the type; changing it is a spec change.
- [`Microsoft.AspNetCore.Mvc.Testing` is outside the approved table] → Justified in the PR with the `tech-stack.md` criteria (Microsoft, MIT, test-only); an ADR only if review rejects it.
- [The ASP.NET example gives a false sense of production readiness] → The README and spec say there is no authentication or persistence; security headers and errors are defaults, not a threat model.
- [A library with `IsPackable` and no metadata publishes a generic package] → Publishing is not part of the skeleton; the README says to set the package id and metadata first.
- [The generated job gets slow] → Restores come from the NuGet cache; the job is path-filtered, scheduled weekly and not part of the ruleset.

## Migration Plan

Not applicable to users: no project has been generated from a C# skeleton yet. Order of work: archive `add-csharp-application-skeleton`, move its directory under `library/`, then add the type field and plan, then the other two skeletons. Rollback is reverting the pull request.

## Open Questions

- Whether the console type should offer subcommands, and whether the library type should enable package validation (`EnablePackageValidation`), can be decided in later changes without altering these specs.
