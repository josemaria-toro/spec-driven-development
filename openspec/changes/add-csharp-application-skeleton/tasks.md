# Tasks

## 1. Toolchain

- [x] 1.1 Install a .NET 10 SDK for the current user outside the repository (Microsoft's official `dotnet-install` script, read before running it) and verify `dotnet --list-sdks` lists a 10.x SDK; if it cannot be installed, stop and ask how to proceed (design decision 11)

## 2. C# backend skeleton

- [x] 2.1 Build the solution in a scratch directory: `App.slnx`, `global.json`, `Directory.Build.props`, `Directory.Packages.props`, `.editorconfig`, `.gitignore`, the `Domain`, `Application` and `Infrastructure` projects with one example per layer, and the unit and integration test projects with one test class each; verify `dotnet restore`, `dotnet format --verify-no-changes`, `dotnet build -warnaserror`, `dotnet test tests/App.UnitTests -p:CollectCoverage=true` and `dotnet test tests/App.IntegrationTests` pass there
- [x] 2.2 Add `App.ArchitectureTests` (NetArchTest): dependency direction between the layers and no `Microsoft.AspNetCore`, `Microsoft.EntityFrameworkCore`, `Npgsql`, `RabbitMQ.Client`, `System.Net.Http` or `System.Data` in `Domain` and `Application`; verify they pass, and that they fail when a `Domain` class uses `HttpClient` and the build fails when `Domain` references `Infrastructure`
- [x] 2.3 Set `Threshold` 80 with `ThresholdType` `line` in the unit test project and verify the run fails when an example test is removed so coverage drops below 80%
- [x] 2.4 Generate the `packages.lock.json` files in the scratch copy and verify `dotnet restore --locked-mode` succeeds with no lock file change and `dotnet list package --vulnerable --include-transitive` reports no High or Critical package
- [x] 2.5 Copy the solution to `templates/apps/backend/csharp/` without `.tmpl` files, excluding `bin/`, `obj/` and `TestResults/`, and verify no file contains the template delimiters (existing verbatim-files test)

## 3. Rendering tests

- [x] 3.1 Add `BACKEND_CSHARP_FILES` to `tests/integration/conftest.py` and tests in `tests/integration/test_application_skeletons.py` that rendering a `backend` and a `fullstack` spec with `csharp` yields exactly those files and none of the Python backend; verify they pass
- [x] 3.2 Replace the tests that used C# as the technology without a skeleton (`test_application_skeletons.py`, `test_render_project_end_to_end.py`) with a template copy that omits a technology directory, and check the README-only result; verify they pass
- [x] 3.3 Extend the byte-identical-skeletons and no-project-values tests to a C# backend, and the every-typology test to its skeleton; verify they pass
- [x] 3.4 Verify the template lint test, the deterministic-output tests and the no-network-or-process test still pass with the new templates

## 4. Generated C# skeleton passes its gates in CI

- [x] 4.1 Extend `tests/generated/test_generated_skeletons.py` with the C# gates, the vulnerability parse of `dotnet list package --vulnerable --include-transitive`, the lock-file-unchanged check and the two negative checks of design decision 9, skipping with a reason when `dotnet` is missing outside CI and failing when missing in CI; verify it passes locally
- [ ] 4.2 Add the `actions/setup-dotnet` step (version from the skeleton's `global.json`, pinned action version) to `.github/workflows/skeletons.yml` and verify the job passes on the pull request of this change
- [ ] 4.3 Verify the job fails when the C# skeleton is broken on purpose (for example an unused variable that raises a warning in a template file), on a temporary draft pull request that is closed afterwards, and record the result in the pull request

## 5. Quality gates and documentation

- [x] 5.1 Run `uv run ruff format --check . && uv run ruff check . && uv run mypy src && uv run lint-imports` in `apps/backend/` and verify they pass
- [x] 5.2 Run `uv run pytest tests/unit --cov --cov-fail-under=80` and `uv run pytest tests/integration` and verify coverage stays at or above 80% and all tests pass
- [x] 5.3 Update the "Applications" section of `templates/project/README.md.tmpl` (add the C# gates and how to refresh its lock files, and remove the sentence saying C# only has its README) and `apps/backend/README.md` (templates table), and verify the commands they name run as written in a rendered copy
- [x] 5.4 Run `openspec validate add-csharp-application-skeleton --strict` and verify it is valid
- [ ] 5.5 Complete the OWASP checklist (vulnerable and outdated components, software and data integrity) in the pull request, including the justification of the two test-host packages, and verify the vulnerability and secret checks of CI pass without bypassing them

## Workflow follow-up

- Archive the change after the pull request is merged.
- Follow-ups outside this change: `add-application-workflow-templates` (backend, frontend and CodeQL workflows, then their checks in the ruleset template), a Dependabot configuration for `templates/apps/**`, and an `Api` project with ASP.NET Core when the first HTTP adapter is needed.
