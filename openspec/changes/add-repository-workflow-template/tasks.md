# Tasks

## 1. Workflow template

- [ ] 1.1 Create `templates/github/workflows/repository.yml` from `.github/workflows/repository.yml`, with the job names `Secret scan`, `OpenSpec validate` and `Commit type matches branch prefix`; verify `python3 -c "import yaml; yaml.safe_load(open(...))"` parses it and the three job names are present
- [ ] 1.2 Replace the secret scan with the pinned gitleaks release tarball: download the release, check its SHA-256 against a value pinned in the workflow, then run `gitleaks git`; obtain the checksum from the release and verify it by downloading the tarball once and computing it locally
- [ ] 1.3 Set workflow-level `permissions: contents: read`, `persist-credentials: false` on every checkout, pinned action versions and the pinned OpenSpec CLI and Node versions; verify with the tests of group 2 (no unpinned `uses:`, no custom secret, no write permission)
- [ ] 1.4 Run the template workflow in a scratch GitHub repository or a branch of this one (copy it to `.github/workflows/` temporarily, never merged) and verify the three jobs pass on an empty generated layout and that the secret scan fails on a file with a fake test token; remove the temporary copy afterwards
- [ ] 1.5 Document in `templates/harness/README.md` (or the nearest document that describes the generated `.github/`) what the workflow provides and how to bump the gitleaks version and checksum, and verify the paths and commands it names exist

## 2. Tests

- [ ] 2.1 Add a unit test in `apps/backend/tests/unit/test_render_plan.py` that `github/workflows/repository.yml` maps to `.github/workflows/repository.yml` in verbatim mode, and verify it passes
- [ ] 2.2 Add `.github/workflows/repository.yml` to the expected files of `apps/backend/tests/integration/test_render_project_end_to_end.py` and add scenario tests for backend, frontend and fullstack specs (workflow present for every typology) and verify they pass
- [ ] 2.3 Add integration tests for the triggers (pull requests to `main`, pushes to `main`, weekly schedule) and for byte-identical output across two specs with different values, and verify they pass
- [ ] 2.4 Add an integration test that every context required by `templates/github/rulesets/ruleset-for-branches.json` is a job name in the rendered workflows, and that no file from `templates/github/rulesets/` is in the output; verify it fails when a job is renamed temporarily
- [ ] 2.5 Add integration tests for read-only permissions, versioned `uses:` references and tools, checksum verification before a downloaded executable runs, and no secret other than `GITHUB_TOKEN`; verify each fails against a deliberately broken copy of the workflow
- [ ] 2.6 Verify the template lint test (`test_template_lint.py`) still passes and the render stays deterministic (existing determinism tests green)

## 3. Quality gates

- [ ] 3.1 Run `uv run ruff format --check . && uv run ruff check . && uv run mypy src && uv run lint-imports` in `apps/backend/` and verify they pass
- [ ] 3.2 Run `uv run pytest tests/unit --cov --cov-fail-under=80` and `uv run pytest tests/integration` and verify coverage stays at or above 80% and all tests pass
- [ ] 3.3 Run `openspec validate add-repository-workflow-template --strict` and verify it is valid
- [ ] 3.4 Complete the OWASP checklist for software and data integrity in the PR (pinned actions, verified download, least privilege) and verify the vulnerability and secret checks of the commit hooks and CI pass without bypassing them

## Workflow follow-up

- Archive the change after the pull request is merged.
- Follow-ups outside this change: `add-application-skeletons`, `add-application-workflow-templates` (backend, frontend, CodeQL), and aligning this repository's own secret scan with the template.
