# Design

## Context

See `proposal.md` for the motivation. Observed state:

- `build_render_plan` (`apps/backend/src/sdd/domain/render_plan.py`) maps `apps/<kind>/<name>` to itself when the kind belongs to the typology. It knows kinds, not technologies, although `ProjectSpec` carries the technology of each application.
- `templates/apps/<kind>/README.md.tmpl` is the only application template today; it is rendered with the `application` values of its kind.
- Rendering must not run processes or use the network (`openspec/specs/project-rendering`), so a lockfile cannot be produced at render time. `pnpm-lock.yaml` has no project name; `uv.lock` records the root package name.
- This repository already contains working applications (`apps/backend`, `apps/frontend`) that pass every gate, which are the reference for what the skeletons must achieve. Templates are independent from `harness/` and from these applications (`CLAUDE.md`).
- The stack sheets fix the tools, commands and folder structure: `backend-python.md`, `frontend-react.md`.

## Goals / Non-Goals

**Goals:**

- A generated Python backend and React frontend pass their stack's gates on the first commit, and a CI job of this repository proves it.
- Rendering stays deterministic, offline and free of project values in code.

**Non-Goals:**

- The C# skeleton and the workflows of generated applications (see the proposal).
- Parameterizing the skeletons (package names, optional features).

## Decisions

1. **Layout by technology directory.** Skeleton files live under `templates/apps/<kind>/<technology>/` and render to `apps/<kind>/`; files directly under `templates/apps/<kind>/` (the README) apply to every technology. The directory name is the technology value from the catalogue (`python`, `csharp`, `react-typescript`), so the plan needs no mapping table: a first segment under the kind that is a catalogue technology is a technology directory, selected when it equals the spec's technology for that kind and skipped otherwise; the technology directory is dropped from the destination. Alternatives: a manifest file listing files per technology (one more format to maintain and validate); a technology prefix in file names (breaks tooling and paths); duplicating the kind README per technology. Destination collisions between shared and technology files are already refused by the plan.

2. **Fixed names, verbatim files.** Distribution `backend` and `frontend`, Python package `app`; no `.tmpl`, no project values. This keeps every skeleton byte-identical across projects, keeps `uv.lock` valid (its root package name never changes), removes the need for new escaping filters for Python, TOML and TSX, and avoids deriving identifiers from the repository name, which can start with a digit (`1-app`) and be invalid as a Python package. Alternative: derive names from the repository name; rejected for those three reasons, at the cost of a generic package name.

3. **Static, committed lockfiles.** They are generated once with `uv lock` and `pnpm install --lockfile-only` in a scratch copy and committed under the technology directory. Rendering stays offline. Alternatives: generate them at render time (violates "no external effects"); ship no lockfile (violates the stack sheets, which commit lockfiles, and makes `--frozen` installs fail).

4. **Minimal content, one example per layer.** Python: a domain function, an application use case that calls it, an empty `infrastructure` package, one unit test and one integration test. React: the page of this repository's skeleton with generic copy, the same lint, format and test configuration, one test per level. No HTTP, database, broker or authentication. Dependencies are limited to the dev tooling in the stack sheets (backend runtime dependencies: none).

5. **The same configuration as this repository's applications, copied, not shared.** Templates are independent from the repository's own applications, so there is no shared source; drift is caught by decision 6 rather than by coupling.

6. **A CI job proves the skeletons.** A test in `apps/backend/tests/generated/` (marker `generated`, not collected by `tests/unit` or `tests/integration`) renders each typology and runs the gates of the generated applications: frozen install, format, lint, types, layer rule, unit with coverage, integration, e2e with browsers, dependency audit, and that the lockfiles did not change. A new workflow runs it on pull requests that touch `templates/apps/`, `apps/backend/src/` or the test itself, and weekly (to catch vulnerabilities published after the lockfiles were frozen). Alternatives: only a structural test (does not prove the skeleton works); running it in every PR (minutes of Playwright for unrelated changes). Locally the test skips with a reason when `uv` or `pnpm` is missing; in CI (`CI=true`) a missing tool fails it.

7. **Dependency freshness is a CI signal, not a bot.** Dependabot does not watch `templates/`, and adding a Dependabot configuration is a CI-configuration change outside this proposal. The weekly run of decision 6 fails when the frozen dependencies gain a high or critical advisory, which prompts a manual refresh of the lockfiles.

## Risks / Trade-offs

- [Skeleton configuration drifts from this repository's applications] → Decision 6 runs the real gates on every skeleton change; the two are compared by hand when a stack sheet changes.
- [Frozen dependencies age and the audit of generated projects fails on day one] → Decision 7 (weekly audit) and the audit scenario of the spec; the lockfile refresh is a normal `chore` PR.
- [The CI job is slow and flaky (browsers, network installs)] → It is limited by paths and a weekly schedule, runs unrequired at first, and is not part of the ruleset checks; promote it to required only after it proves stable.
- [A generic package name `app` may collide with user code or be unwanted] → It is the default of a fixed skeleton; renaming is a normal refactor of the generated project and uv/pnpm manifests, and deriving names can be a later, separate change.
- [A technology directory name equals a normal subdirectory of another skeleton] → The plan only treats the first segment under a kind as a technology directory; no skeleton uses `python`, `csharp` or `react-typescript` as a deeper folder name, and a test pins the rule.
- [Node 20 pins older majors of some tools] → Reuse the pins and the justification in `apps/frontend/README.md` and ADR 0001 (expiry 2027-01-31); the skeleton must move with the ADR.

## Open Questions

- Whether to add a Dependabot configuration for `templates/apps/**` in this repository (decision 7) can be answered later without changing the specs, approach or tasks.
