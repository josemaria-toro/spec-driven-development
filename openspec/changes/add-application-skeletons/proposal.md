# Proposal

## Why

A generated project receives only a README per application (`templates/apps/<kind>/README.md.tmpl`): no manifest, no lockfile, no layers, no tests. Nothing can build or be checked in it, so the CI workflows the harness requires (tests, lint, types, audit, CodeQL; see the follow-up `add-application-workflow-templates`) would fail on day one, and each team starts by rebuilding the same hexagonal skeleton by hand.

This is a **functional change**: it alters the file tree that rendering generates (observable output), so OpenSpec applies.

## What Changes

- Add a minimal, working **application skeleton per technology**, rendered into `apps/<kind>/` only for the technology the spec selects:
  - **Backend, Python** (`harness/stacks/backend-python.md`): hexagonal layers (`domain`, `application`, `infrastructure`), `pyproject.toml` with Ruff, mypy strict, import-linter (layer rule and "no frameworks in the core") and an 80% coverage gate, `uv.lock`, one unit test and one integration test.
  - **Frontend, React and TypeScript** (`harness/stacks/frontend-react.md`): Vite app with one responsive, accessible page, ESLint (types, a11y, security, layer rule), Prettier, `tsc` strict, Vitest unit and integration tests with an 80% gate, Playwright e2e with axe at mobile, tablet and desktop widths, `pnpm-lock.yaml`, Node 20 pinned.
- Make the render plan **technology-aware**: files under a technology directory of a kind are rendered only when that technology is selected. The existing per-kind README keeps applying to every technology.
- Skeleton files are copied **verbatim**, with fixed names (distribution `backend` and `frontend`, Python package `app`) and no project values inside code, so the output is byte-identical for every project and the shipped lockfiles stay valid.
- A technology without a skeleton (C# for now) renders only the per-kind README, as today.
- Add checks that every generated skeleton passes its own quality gates, as a CI job of this repository.

Out of scope (separate changes):

- The **C# backend skeleton** (`add-csharp-application-skeleton`): this environment has no .NET SDK to verify it, so it is not proposed unverified.
- The CI workflows for generated applications and CodeQL (`add-application-workflow-templates`), and adding their checks to the ruleset template.
- Any runtime adapter: no HTTP server, database, broker, authentication or domain logic in the skeletons. They hold one trivial example per layer.
- The start/stop scripts (`app.sh`) of this repository's applications.
- Pre-commit configuration for generated projects.

## Capabilities

### New Capabilities

- `application-skeletons`: the initial, verified code of each application of a generated project (layout, quality gates, accessibility baseline, fixed names, lockfiles) for the Python backend and the React frontend.

### Modified Capabilities

- `project-rendering`: rendering selects application files by the technology of each application, not only by its kind.

## Impact

- **Templates:** new directories `templates/apps/backend/python/` and `templates/apps/frontend/react-typescript/` (about 25 files plus two lockfiles, roughly 5,500 lines, almost all lockfile). The two per-kind READMEs stay.
- **Backend application** (Python, hexagonal architecture; `harness/stacks/backend-python.md`): the render plan in `domain/render_plan.py` learns the technology of each kind; unit and integration tests are added. No change to ports or adapters.
- **CI of this repository (flag: CI configuration):** a new job renders each typology and runs the gates of the generated applications, which needs `uv`, Node and Playwright browsers. Touching CI is requested here for the first time and is subject to approval of this proposal.
- **Dependencies and supply chain (security-sensitive area):** the skeletons pin dependencies in lockfiles, all from the approved lists of the stack sheets, and no new library is introduced. Pinned versions go stale; the weekly Dependabot configuration that generated projects already get, plus an audit in the new CI job, mitigate it. The OWASP checklist (vulnerable components, software integrity) must be completed in the PR.
- **Security of rendering:** because project values are not inserted into code, there is no new injection surface; the existing filters and lint rule are unchanged.
- **Exceptions:** none. No ADR is required; Node 20 is already covered by `harness/adr/0001-node-20-minimum-version-exception.md`.
