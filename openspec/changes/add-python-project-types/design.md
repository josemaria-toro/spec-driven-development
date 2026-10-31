# Design

## Context

See `proposal.md` for the motivation. Observed state:

- `add-backend-project-types` (proposed, not applied) adds the technology-neutral catalogue (`api`, `console`, `library`), the `project_type` field, `TECHNOLOGY_PROJECT_TYPES` (C# only), the project-type-aware render plan and `application.project_type` in the template context. **It must be applied and archived first.** After it, offering Python's types is a catalogue entry plus templates.
- `templates/apps/backend/python/` holds the merged skeleton from `add-application-skeletons`: `src/app/{domain,application,infrastructure}`, one unit and one integration test, Ruff, mypy strict, import-linter (layer rule and forbidden libraries), an 80% coverage gate and `uv.lock`, with no dependencies at runtime. It is a library in practice, so it becomes the `library` type.
- The stack sheet (`harness/stacks/backend-python.md`) approves FastAPI, Uvicorn, Pydantic and httpx, lists `interfaces/` as the inbound layer of the hexagonal structure, and fixes the commands. The generated-skeleton test (`tests/generated/test_generated_skeletons.py`) renders a project and runs every gate per application.

## Goals / Non-Goals

**Goals:**

- Python offers the same three project types as C#, each passing the gates of its stack sheet, with the same fixed names and verbatim files as the other skeletons.
- Adding the types needs no change to the plan, the context or the spec model beyond the catalogue entry.

**Non-Goals:**

- Runtime adapters, authentication, publishing metadata or frontend types (see the proposal).

## Decisions

1. **The catalogue entry is the switch.** `TECHNOLOGY_PROJECT_TYPES[Technology.PYTHON]` lists the three types; because `python` then declares types, the plan treats `api`, `console` and `library` under `templates/apps/backend/python/` as project-type directories, so a Python skeleton without them would render nothing. The move of the existing files into `library/` and the catalogue entry land in the same change so that no commit renders an empty Python backend. Alternative: a transition where Python files may stay directly under `python/` as shared files; rejected, because shared files would then be rendered for every type and the layout would differ from C#.

2. **`library` is the existing skeleton plus packaging.** Files move under `library/`. Added: the `py.typed` marker in the package, wheel and sdist build through the existing Hatch configuration (`uv build`), and Ruff's documentation rules (`D1`, public members only) for `src`, with tests exempt. No project values: the distribution stays named `backend`; the README of the generated project says to rename it and set the metadata before publishing. Alternative: also add `twine` or publish tooling; rejected, publishing is out of scope.

3. **`console` adds an `interfaces` layer with `argparse`.** `app/interfaces/cli.py` has `run(arguments, output, errors) -> int`, a plain function over text streams, so unit tests call it with `io.StringIO`; `main()` calls it with `sys.argv`, and `app/__main__.py` plus a `[project.scripts]` entry (`backend`) give `python -m app` and an installed command. Zero or one argument is valid; anything else prints usage on standard error and returns 2 (a parser subclass raises instead of exiting). `argparse` is standard library, so no dependency: Click and Typer are not in the approved table and the example does not need them.

4. **`api` adds an `interfaces` layer with FastAPI.** `app/interfaces/api.py` builds the application (`create_app()`), `app/main.py` exposes `app` for `uvicorn app.main:app`. One `GET /greetings/{name}` endpoint over the use case; the name is validated at the edge with a maximum length through FastAPI's path validation. Secure defaults: a validation handler that returns a problem-details body naming the field and not echoing the input; a catch-all handler that returns a generic 500 body; middleware that adds `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Cache-Control: no-store` and `Strict-Transport-Security`; `docs_url`, `redoc_url` and `openapi_url` set to `None`. Settings and logging are not added (YAGNI). Runtime dependencies: `fastapi` and `uvicorn`; dev: `httpx` for `TestClient`. HTTPS itself is terminated outside the process, so unlike the C# skeleton there is no redirect.

5. **Layers and the layer rule.** Layers are `interfaces | infrastructure` (siblings, independent of each other) above `application` above `domain`, for `api` and `console`; `library` keeps its two-contract configuration. The forbidden-library rule for `domain` and `application` (FastAPI, Pydantic, SQLAlchemy, httpx, as today) is identical in the three types. Because the API entry layer legitimately imports FastAPI, the rule's source modules stay `domain` and `application` only.

6. **Tests per type.** `library`: the existing unit and integration tests plus a test that the typing marker ships. `console`: unit tests of `run` (valid, none, too many) and an integration test that starts `python -m app` in a subprocess and checks streams and exit code. `api`: unit tests of the endpoint through `TestClient` with the use case replaced where a failure is needed, and integration tests that exercise the real application object through the ASGI client (valid, invalid, headers, docs disabled, error without detail). Coverage gate 80% as before.

7. **Three lock files, three copies.** Each type has its own `pyproject.toml` and `uv.lock` generated in a scratch copy (`uv lock`), audited with `pip-audit`, committed under its directory. Same trade-off as the C# types: duplication of the shared configuration, caught by the generated test.

8. **The generated test is parametrized.** `test_generated_skeletons.py` runs the Python gates for each of the three types (frozen install, lock check, format, lint, types, layer rule, unit with coverage, integration, audit, lock unchanged) plus `uv build` for `library` and the console run through the installed command; the layer-violation checks add one file in `domain` (an import from `interfaces`) and one in `application` (an import of the web framework) and expect the layer check to fail. Tests that used Python as "a technology without project types" switch to a test catalogue (no real technology lacks types any more).

9. **Harness documents.** `harness/stacks/backend-python.md` and `templates/harness/stacks/backend-python.md` gain the folder structure of the three types next to the hexagonal one; this is the approved harness change of the proposal.

## Risks / Trade-offs

- [Python and C# types drift apart in behavior] → The specs state the same observable behavior for both (arguments, exit codes, validation, errors); each is proven by its own tests and the generated job.
- [Three more lock files age and the audit fails after a new advisory] → The weekly run flags it and the refresh is a `chore` PR; the audit scenario covers release time.
- [A catch-all error handler hides real failures from operators] → The skeleton returns a generic body to the caller; logging of the failure belongs to the first change that adds logging, and the README says so.
- [Disabled API docs surprise a developer] → The README says how to enable them for development; default-off is the secure choice.
- [`argparse` output formats differ across Python versions] → The tests assert the exit code, the empty standard output and that standard error contains the usage text, not its exact wording.
- [The move into `library/` breaks tools that expect `pyproject.toml` at the old path] → Only the plan reads that path, and rendering drops the type directory; the expected file sets in the integration tests pin the result.

## Migration Plan

Not applicable to users: Python projects generated before this change keep their files, and a new Python spec renders `api` by default. Order of work: archive `add-backend-project-types`, move the files into `library/` together with the catalogue entry, then add `console` and `api`. Rollback is reverting the pull request.

## Open Questions

- Whether `console` should grow subcommands, and whether `api` should expose a health endpoint, can be decided in later changes without altering these specs.
