# Tasks

## 1. Prerequisite

- [x] 1.1 Verify that `add-csharp-application-skeleton` is archived and merged (`openspec list --specs` shows its C# requirements in `application-skeletons`, `templates/apps/backend/csharp/` exists on `main`) and that `dotnet --list-sdks` lists a 10.x SDK; if either is missing, stop and ask

## 2. Project type in the project spec

- [x] 2.1 Add the `ProjectType` catalogue (`api`, `console`, `library`) and `TECHNOLOGY_PROJECT_TYPES` (only `csharp`) to `domain/catalogue.py`, and `project_type` to `Application`; verify with unit tests in `tests/unit/test_project_spec.py` for the six scenarios of "Supported project types" (accepted, default `api`, unsupported value listing the catalogue, technology without types rejects one, technology without types needs none, `frontend` typology)
- [x] 2.2 Read `project_type` from the raw spec, report its errors with the rest, and include it in the canonical form for a backend that has one, with `SCHEMA_VERSION = 2`; verify with unit tests for the new hash scenarios (different type changes the hash, default equals explicit `api`, Python hashes depend only on their own values) and update the existing canonical-form tests
- [x] 2.3 Add `project_type` to the application values of `domain/render_context.py` (empty for other technologies); verify with a unit test of the context for each type and for Python

## 3. Project-type-aware render plan

- [x] 3.1 In `domain/render_plan.py`, treat a first segment under a technology directory that is a project type of that technology as a project-type directory: select it by the spec's project type, skip the others and drop it from the destination; keep files directly under the technology directory shared; verify with unit tests for the four scenarios of "Project-type-specific application files" using the fake template set
- [x] 3.2 Add unit tests that a folder named like a project type is not treated as one under a technology without project types, that a shared file and a project-type file with the same destination are refused, and that a deeper folder named like a project type is kept; verify they pass
- [x] 3.3 Update the template mapping table in `apps/backend/README.md` for `apps/<kind>/<technology>/<project type>/**` and verify the paths it names exist

## 4. Library skeleton

- [x] 4.1 Move the files of `templates/apps/backend/csharp/` into `templates/apps/backend/csharp/library/` and update the expected file set; verify the rendering integration tests pass for the `library` type
- [x] 4.2 Make the layer projects packable, enable documentation files and keep CS1591 an error, in a scratch copy of `library/`; verify `dotnet pack` produces a package, that removing one documentation comment fails `dotnet build -warnaserror`, and that the base gates still pass
- [x] 4.3 Copy the scratch changes back to `library/` and verify with an integration test that rendering a spec with the `library` type yields exactly its files and none of the other types

## 5. Console skeleton

- [x] 5.1 Build the `console` skeleton in a scratch directory from `library/`: add `App.Console` (`Program.cs` and the `Cli` class), reference it from the solution and extend the architecture tests; verify restore, format, build with warnings as errors, unit tests with coverage and architecture tests pass there
- [x] 5.2 Add unit tests that run `Cli` in process for the three scenarios (one name, no argument, too many arguments with usage on standard error, empty standard output and a non-zero code) and integration tests that run the built executable for the valid and the invalid call; verify they pass
- [x] 5.3 Generate the lock files in the scratch copy, verify `dotnet restore --locked-mode` and a vulnerability check with no High or Critical package, copy the skeleton to `templates/apps/backend/csharp/console/` and verify with an integration test that rendering the `console` type yields exactly its files

## 6. ASP.NET Core skeleton

- [x] 6.1 Build the `api` skeleton in a scratch directory from `library/`: add `App.Api` (minimal API, input validation, problem details, HTTPS redirection and HSTS outside development, no developer exception page outside development), reference it from the solution and extend the architecture tests; verify restore, format, build with warnings as errors, unit tests with coverage and architecture tests pass there
- [x] 6.2 Add integration tests with `WebApplicationFactory<Program>` for the valid request, the name longer than the maximum (client error naming the field, no internal detail) and a failing use case outside development (generic server error, no exception data) plus a test that the security headers are present; verify they pass
- [x] 6.3 Generate the lock files in the scratch copy, verify `dotnet restore --locked-mode` and a vulnerability check with no High or Critical package, copy the skeleton to `templates/apps/backend/csharp/api/` and verify with an integration test that rendering the `api` type, and a C# spec with no type, yields exactly its files

## 7. Rendering properties of the project types

- [x] 7.1 Update the expected file sets of `test_render_project_end_to_end.py` and `test_application_skeletons.py` for each type, and add that the README of each C# type states its project type; verify they pass
- [x] 7.2 Extend the byte-identical and no-project-values tests to the three types; verify they pass
- [x] 7.3 Verify the template lint test, the deterministic-output tests and the no-network-or-process test still pass with the new templates

## 8. Generated skeletons pass their gates in CI

- [x] 8.1 Parametrize the C# gates of `tests/generated/test_generated_skeletons.py` over the three project types and add `dotnet pack` for `library`, the `App.Console` runs and the entry-project layer check; verify it passes locally
- [x] 8.2 Verify the Skeletons job passes on the pull request of this change and that its duration is recorded in the pull request
- [x] 8.3 Verify the job fails when the `api` skeleton is broken on purpose (for example a missing documentation comment or a warning in `App.Api`), on a temporary draft pull request that is closed afterwards, and record the result in the pull request

## 9. Quality gates and documentation

- [x] 9.1 Update the folder structure of `harness/stacks/backend-csharp.md` and `templates/harness/stacks/backend-csharp.md` for the console and library types, and the "Applications" section of `templates/project/README.md.tmpl` (project types, how to choose one in the spec, the C# commands per type, how to refresh lock files, the package metadata note for the library); verify the commands they name run as written in a rendered copy of each type
- [x] 9.2 Run `uv run ruff format --check . && uv run ruff check . && uv run mypy src && uv run lint-imports` in `apps/backend/` and verify they pass
- [x] 9.3 Run `uv run pytest tests/unit --cov --cov-fail-under=80` and `uv run pytest tests/integration` and verify coverage stays at or above 80% and all tests pass
- [x] 9.4 Run `openspec validate add-backend-project-types --strict` and verify it is valid
- [x] 9.5 Complete the OWASP checklist (vulnerable and outdated components, software and data integrity, input validation, error handling) in the pull request, including the justification of `Microsoft.AspNetCore.Mvc.Testing`, and verify the vulnerability and secret checks of CI pass without bypassing them

## Workflow follow-up

- Archive the change after the pull request is merged.
- Follow-ups outside this change: project types for Python (`add-python-project-types`), `add-application-workflow-templates`, a Dependabot configuration for `templates/apps/**`.
