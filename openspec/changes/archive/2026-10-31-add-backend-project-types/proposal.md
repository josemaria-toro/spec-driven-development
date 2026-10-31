# Proposal

## Why

A backend is not always an HTTP service: teams also build console tools and reusable libraries or packages. The project creator needs a **catalogue of project types** to offer when a project is created, for every backend technology. The C# skeleton proposed in `add-csharp-application-skeleton` is a single layered core without any host, so it fits none of the three well: it cannot answer a request, run from a terminal or be packed with confidence. Choosing the project type at creation lets each one start from a skeleton that already passes its gates.

This is a **functional change**: it adds a field to the project spec and changes the file tree that rendering generates (observable output), so OpenSpec applies.

**Depends on** `add-csharp-application-skeleton`, which must be applied and archived first: this change builds on the C# skeleton it introduces and moves its files.

## What Changes

- Add an optional **project type** to the project spec with a technology-neutral catalogue: `api`, `console` or `library`. Each backend technology declares which types it offers: C# offers all three here, Python offers none until `add-python-project-types`, which adds its templates to the same mechanism. It defaults to `api` when omitted for a technology that offers types, is rejected for a technology that offers none and for a typology without a backend, and takes part in the canonical form and the content hash.
- Make the render plan **project-type-aware**: for a technology that offers project types, files under `apps/backend/<technology>/<project type>/**` render only for the selected type and the project-type directory is dropped from the destination, as the technology directory already is.
- Add three self-contained C# skeletons under `templates/apps/backend/csharp/`:
  - `library`: the layered core of the base skeleton (Domain, Application, Infrastructure and the three test projects), packable, with XML documentation on the public API required by the build.
  - `console`: the same core plus a `Console` entry project that reads arguments, writes the result to standard output and reports errors on standard error with a non-zero exit code.
  - `api`: the same core plus an `Api` entry project (ASP.NET Core minimal API) with one endpoint over the use case, input validation, problem-details errors and in-memory integration tests.
- Pass the project type to templates (`application.project_type`) and show it in the per-kind README.
- Extend the generated-skeleton test to run the gates of every project type.

Out of scope (separate changes):

- Project types for Python (command line, package, API), proposed as `add-python-project-types` right after this change, and for the React frontend.
- Authentication, authorization, database, broker or any other runtime adapter in the skeletons.
- Publishing metadata of the library package (package id, authors, repository URL): they are project values and stay out of verbatim files.
- The CI workflows for generated applications (`add-application-workflow-templates`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `project-spec`: the optional project type, its catalogue, which technologies offer it, and its effect on the canonical form and the hash.
- `project-rendering`: rendering selects application files by the project type of the backend.
- `application-skeletons`: adds the ASP.NET Core, console and library skeletons and their quality gates.

## Impact

- **Backend application** (Python, hexagonal architecture; `harness/stacks/backend-python.md`): `domain/catalogue.py`, `domain/project_spec.py`, `domain/render_plan.py` and `domain/render_context.py` learn the project type; unit and integration tests change; the schema version of the canonical form changes, so every content hash changes once.
- **Templates:** `templates/apps/backend/csharp/` becomes three directories (`library/`, `console/`, `api/`), each about 40 files plus lock files; the files of the base skeleton move into `library/`. The per-kind README changes.
- **Stack of the generated skeleton** (C# on .NET 10 LTS, hexagonal architecture; `harness/stacks/backend-csharp.md`): the folder structure of the stack sheet and its copy in `templates/harness/stacks/` describe the three project types (a harness change, approved with this proposal).
- **CI of this repository (flag: CI configuration):** no workflow change; the job of `skeletons.yml` runs about three times more C# gates and takes longer.
- **Dependencies and supply chain (security-sensitive area):** the ASP.NET Core skeleton adds `Microsoft.AspNetCore.Mvc.Testing` (in-memory host for integration tests), which is not in the approved table; ASP.NET Core itself is approved. The console and library skeletons add no package. The PR justifies the new package with the criteria of `tech-stack.md` and completes the OWASP checklist (vulnerable and outdated components, software and data integrity).
- **Security of the generated API (flag: input validation, error handling):** the ASP.NET skeleton validates its input and never returns exception details; the specs carry negative scenarios for both.
- **Exceptions:** none. No ADR is required unless review rejects the new test package.
