# Proposal

## Why

The project creator offers a catalogue of project types (`api`, `console`, `library`) when a project is created, and the catalogue is the same for every backend technology. `add-backend-project-types` introduces the catalogue and the C# templates; a Python backend still renders the single layered skeleton without a host, which is only a library in practice. Python needs the same three templates so that the choice means the same thing in both languages.

This is a **functional change**: it changes which project types Python offers and the file tree that rendering generates (observable output), so OpenSpec applies.

**Depends on** `add-backend-project-types` (the catalogue, the `project_type` field and the project-type-aware render plan), which must be applied and archived first.

## What Changes

- Python declares the three project types in the catalogue, so a Python spec may select `api`, `console` or `library`, and an omitted type is `api`.
- Three self-contained Python skeletons under `templates/apps/backend/python/`; the files of the existing skeleton move into `library/`:
  - `library`: the layered core (`domain`, `application`, `infrastructure`) packaged as a typed, installable distribution, with every public member documented (enforced by lint) and a build that produces the distribution files.
  - `console`: the core plus an `interfaces` layer with a command line entry point that writes the result to standard output and reports invalid arguments on standard error with a non-zero exit code.
  - `api`: the core plus an `interfaces` layer with a FastAPI application served by Uvicorn, one endpoint over the use case, input validation, errors without internal detail, security headers and API documentation disabled by default.
- The layer rule gains the `interfaces` layer (it may use `application` and `domain`; nothing imports it), and the forbidden-library rule for `domain` and `application` is unchanged.
- Extend the generated-skeleton test to run the gates of the three Python project types.

Out of scope (separate changes):

- Authentication, authorization, database, broker or any other runtime adapter in the skeletons.
- Package publishing metadata for the library (name on a registry, authors, URLs): project values stay out of verbatim files.
- Project types for the React frontend.
- The CI workflows for generated applications (`add-application-workflow-templates`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `project-spec`: Python offers the three project types.
- `application-skeletons`: adds the Python library, console and API skeletons and their quality gates.

## Impact

- **Backend application** (Python, hexagonal architecture; `harness/stacks/backend-python.md`): `domain/catalogue.py` lists the project types of Python; unit and integration tests change (the tests that used Python as the technology without project types use a test catalogue instead). No other production code change: the plan and the context already handle project types.
- **Templates:** `templates/apps/backend/python/` becomes three directories (`library/`, `console/`, `api/`), each about 20 files plus a `uv.lock`; the existing files move into `library/`.
- **Stack sheet** (a harness change approved with this proposal): `harness/stacks/backend-python.md` and its copy in `templates/harness/stacks/` describe the folder structure of the three types; the "Applications" section of `templates/project/README.md.tmpl` lists their commands.
- **CI of this repository (flag: CI configuration):** no workflow change; the generated job runs three more Python skeletons and takes longer.
- **Dependencies and supply chain (security-sensitive area):** the `api` skeleton adds FastAPI and Uvicorn as runtime dependencies and httpx for its tests, all in the approved table; Pydantic arrives with FastAPI. `console` and `library` add none. The new lock files are audited with `pip-audit`, and the PR completes the OWASP checklist (vulnerable and outdated components, software and data integrity).
- **Security of the generated API (flag: input validation, error handling):** the skeleton validates its input and never returns exception details; the specs carry negative scenarios for both.
- **Exceptions:** none. No ADR is required.
