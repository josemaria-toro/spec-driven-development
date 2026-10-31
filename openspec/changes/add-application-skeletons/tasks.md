# Tasks

## 1. Technology-aware render plan

- [ ] 1.1 In `apps/backend/src/sdd/domain/render_plan.py`, select `apps/<kind>/<technology>/**` templates by the spec's technology for the kind and drop the technology directory from the destination; keep files directly under `apps/<kind>/` for every technology; verify with unit tests for the four scenarios of the `project-rendering` delta (selected technology only, shared files, independent kinds, technology without files) in `tests/unit/test_render_plan.py`, using the fake template set of `tests/unit/fakes.py`
- [ ] 1.2 Add unit tests that a technology directory outside the typology's kinds is skipped, that a shared file and a technology file with the same destination are refused, and that a deeper folder named like a technology is not treated as one; verify they pass
- [ ] 1.3 Update the template mapping table in `apps/backend/README.md` for `apps/<kind>/<technology>/**` and verify the paths it names exist

## 2. Python backend skeleton

- [ ] 2.1 Build the skeleton in a scratch directory: `pyproject.toml` (distribution `backend`, Ruff, mypy strict, pytest with `--strict-markers` and an `integration` marker, coverage `fail_under = 80`, import-linter layer rule and forbidden frameworks), the layers under `src/app/`, one example per layer, one unit test and one integration test; verify `uv sync`, `ruff format --check`, `ruff check`, `mypy src`, `lint-imports`, `pytest tests/unit --cov` and `pytest tests/integration` all pass there
- [ ] 2.2 Generate `uv.lock` in the scratch copy and verify `uv lock --check` and `uv sync --frozen` succeed and that `pip-audit` on the export reports no vulnerability
- [ ] 2.3 Copy the skeleton to `templates/apps/backend/python/` without `.tmpl` files and verify with an integration test that rendering a `backend` and a `fullstack` spec yields exactly the expected backend files, none of another technology, and that the layer-rule scenarios fail as specified when a forbidden import is added to a rendered copy (run import-linter on it)
- [ ] 2.4 Update `apps/backend/tests/integration/test_render_project_end_to_end.py` expected file sets for the new backend files and verify the existing determinism and confinement tests still pass

## 3. React frontend skeleton

- [ ] 3.1 Build the skeleton in a scratch directory from the configuration of `apps/frontend` (Vite, ESLint with a11y, security and layer rule, Prettier, strict `tsc`, Vitest unit and integration with an 80% gate, Playwright with axe at 360, 768 and 1280 px, `.nvmrc` 20 and `.npmrc` `engine-strict`), with a generic page, a skip link and a main landmark and one test per level; verify `pnpm install`, `format:check`, `lint`, `typecheck`, `test:unit --coverage`, `test:integration` and `e2e` pass there
- [ ] 3.2 Generate `pnpm-lock.yaml` in the scratch copy and verify `pnpm install --frozen-lockfile` and `pnpm audit --audit-level high` succeed
- [ ] 3.3 Copy the skeleton to `templates/apps/frontend/react-typescript/` without `.tmpl` files and verify with an integration test that rendering a `frontend` and a `fullstack` spec yields exactly the expected frontend files and none of another technology, and that a rendered copy fails lint when `domain` imports from `interfaces`
- [ ] 3.4 Update the expected file sets of the end-to-end rendering tests for the frontend files and verify they pass

## 4. Rendering properties of the skeletons

- [ ] 4.1 Add integration tests that two projects with different names, repository names and descriptions render byte-identical skeleton files (everything under `apps/` except the per-kind README), and that a hostile description (`{{ 7 * 7 }}`, quotes, `<< >>`) appears in no skeleton file; verify they pass
- [ ] 4.2 Add an integration test that a spec with a `csharp` backend renders only `apps/backend/README.md` and succeeds, and that every typology renders both the per-kind README and its skeleton; verify they pass
- [ ] 4.3 Verify the template lint test (`test_template_lint.py`) and the deterministic-output tests still pass with the new templates, and that rendering still performs no network or process access (existing test)

## 5. Generated skeletons pass their gates in CI

- [ ] 5.1 Add `apps/backend/tests/generated/test_generated_skeletons.py` (marker `generated`, registered in `pyproject.toml`) that renders `backend`, `frontend` and `fullstack` projects into a temp directory and runs the gates of each application, checks the lockfiles did not change and runs the dependency audits; skip with a reason when `uv` or `pnpm` is missing outside CI and fail when missing in CI; verify it passes locally for the backend part (no Playwright browsers needed)
- [ ] 5.2 Add `.github/workflows/skeletons.yml` that runs it on pull requests touching `templates/apps/**`, `apps/backend/src/**` or the test, on pushes to `main` and weekly, with pinned action versions, read-only permissions and Node 20 plus Playwright browsers; verify the job passes on the pull request of this change
- [ ] 5.3 Verify the job fails when a skeleton is broken on purpose (for example a lint error in a template file), by trying it on a temporary branch that is closed afterwards, and record the result in the pull request

## 6. Quality gates and documentation

- [ ] 6.1 Run `uv run ruff format --check . && uv run ruff check . && uv run mypy src && uv run lint-imports` in `apps/backend/` and verify they pass
- [ ] 6.2 Run `uv run pytest tests/unit --cov --cov-fail-under=80` and `uv run pytest tests/integration` and verify coverage stays at or above 80% and all tests pass
- [ ] 6.3 Document the generated applications in the README template of the harness (`templates/harness/README.md`) or the nearest document that describes the generated tree, including how to refresh the skeleton lockfiles, and verify the commands it names run as written
- [ ] 6.4 Run `openspec validate add-application-skeletons --strict` and verify it is valid
- [ ] 6.5 Complete the OWASP checklist (vulnerable and outdated components, software and data integrity) in the pull request, and verify the vulnerability and secret checks of CI pass without bypassing them

## Workflow follow-up

- Archive the change after the pull request is merged.
- Follow-ups outside this change: `add-csharp-application-skeleton`, `add-application-workflow-templates` (backend, frontend and CodeQL workflows, then their checks in the ruleset template), and deciding on a Dependabot configuration for `templates/apps/**`.
