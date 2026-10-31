# Tasks

## 1. Prerequisite

- [x] 1.1 Verify that `add-backend-project-types` is archived and merged (`openspec list --specs` shows its project-type requirements, `ProjectType` and `TECHNOLOGY_PROJECT_TYPES` exist in `domain/catalogue.py`) and that `uv --version` runs; if either is missing, stop and ask

## 2. Catalogue entry and library type

- [x] 2.1 Move the files of `templates/apps/backend/python/` into `templates/apps/backend/python/library/` and add `Technology.PYTHON` with the three project types to `TECHNOLOGY_PROJECT_TYPES`; verify with unit tests for the three scenarios of "Python project types" and that the rendering integration tests pass for the `library` type with the file set updated
- [x] 2.2 Replace the unit tests and the integration tests that used Python as the technology without project types with a test catalogue or a template copy without type directories; verify they pass
- [x] 2.3 In a scratch copy of `library/`, add the `py.typed` marker, enable Ruff's `D1` rules for `src` (tests exempt) and a test that the marker ships; verify `uv build` produces the wheel and the sdist, that removing one documentation string fails `uv run ruff check .`, and that the base gates still pass
- [x] 2.4 Copy the scratch changes back to `library/`, regenerate its `uv.lock` (`uv lock`), and verify `uv lock --check`, `uv sync --frozen` and `pip-audit` on the export report no vulnerability, and that an integration test renders exactly the library files and none of the other types

## 3. Console type

- [x] 3.1 Build `console` in a scratch directory from `library/`: add `app/interfaces/cli.py` (`run` over text streams, usage on standard error and code 2 for invalid arguments), `app/interfaces/__init__.py`, `app/__main__.py`, the `[project.scripts]` entry and the `interfaces` layer in the import-linter contract; verify `uv sync`, format, lint, `mypy src`, `lint-imports`, unit tests with coverage and integration tests pass there
- [x] 3.2 Add unit tests of `run` (one name, no argument, too many arguments with empty output and non-empty errors) and an integration test that starts `python -m app` in a subprocess for a valid and an invalid call; verify they pass, and that the installed command `backend` gives the same results
- [x] 3.3 Generate `uv.lock` in the scratch copy, verify `uv lock --check`, `uv sync --frozen` and `pip-audit` with no vulnerability, copy the skeleton to `templates/apps/backend/python/console/` and verify with an integration test that rendering the `console` type yields exactly its files

## 4. API type

- [x] 4.1 Build `api` in a scratch directory from `library/`: add `app/interfaces/api.py` (`create_app`, one validated endpoint, problem-details handlers, security headers, documentation disabled), `app/main.py`, the `fastapi` and `uvicorn` dependencies and `httpx` for tests, and the `interfaces` layer in the import-linter contract; verify `uv sync`, format, lint, `mypy src`, `lint-imports`, unit tests with coverage and integration tests pass there
- [x] 4.2 Add unit and integration tests through `TestClient` for the valid request with its headers, the name longer than the maximum (client error naming the field, input not echoed), a failing use case (generic server error with no exception type, message or stack trace) and the documentation endpoints answering not found; verify they pass
- [x] 4.3 Verify the layer rule in the scratch copy: a `domain` file importing from `interfaces` and an `application` file importing `fastapi` both fail `lint-imports` naming the import
- [x] 4.4 Generate `uv.lock` in the scratch copy, verify `uv lock --check`, `uv sync --frozen` and `pip-audit` with no vulnerability, copy the skeleton to `templates/apps/backend/python/api/` and verify with an integration test that rendering the `api` type, and a Python spec with no type, yields exactly its files

## 5. Rendering properties of the project types

- [x] 5.1 Update the expected file sets of `test_render_project_end_to_end.py` and `test_application_skeletons.py` for each Python type and add that the README states the project type; verify they pass
- [x] 5.2 Extend the byte-identical and no-project-values tests to the three Python types; verify they pass
- [x] 5.3 Verify the template lint test, the deterministic-output tests and the no-network-or-process test still pass with the new templates

## 6. Generated skeletons pass their gates in CI

- [x] 6.1 Parametrize the Python gates of `tests/generated/test_generated_skeletons.py` over the three project types and add `uv build` for `library`, the console run and the two layer-violation checks of design decision 8; verify it passes locally
- [ ] 6.2 Verify the Skeletons job passes on the pull request of this change and record its duration in the pull request
- [ ] 6.3 Verify the job fails when the `api` skeleton is broken on purpose (for example a lint error in `app/interfaces/api.py`), on a temporary draft pull request that is closed afterwards, and record the result in the pull request

## 7. Quality gates and documentation

- [x] 7.1 Update the folder structure of `harness/stacks/backend-python.md` and `templates/harness/stacks/backend-python.md` for the three types, and the "Applications" section of `templates/project/README.md.tmpl` (Python commands per type, the library renaming and metadata note, how to enable the API documentation for development); verify the commands they name run as written in a rendered copy of each type
- [x] 7.2 Run `uv run ruff format --check . && uv run ruff check . && uv run mypy src && uv run lint-imports` in `apps/backend/` and verify they pass
- [x] 7.3 Run `uv run pytest tests/unit --cov --cov-fail-under=80` and `uv run pytest tests/integration` and verify coverage stays at or above 80% and all tests pass
- [x] 7.4 Run `openspec validate add-python-project-types --strict` and verify it is valid
- [ ] 7.5 Complete the OWASP checklist (vulnerable and outdated components, software and data integrity, input validation, error handling) in the pull request, and verify the vulnerability and secret checks of CI pass without bypassing them

## Workflow follow-up

- Archive the change after the pull request is merged.
- Follow-ups outside this change: project types for the React frontend, `add-application-workflow-templates`, a Dependabot configuration for `templates/apps/**`.
