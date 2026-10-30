# Tasks

## 1. Backend skeleton and tooling

- [x] 1.1 Create `apps/backend/` with the hexagonal layout from `harness/stacks/backend-python.md` (`src/project_generator/{domain,application,infrastructure}/`, `tests/{unit,integration}/`, `pyproject.toml`, `uv.lock`); verify `uv sync` succeeds and `uv run pytest` runs with zero tests collected
- [x] 1.2 Configure Ruff, `mypy --strict`, pytest (`--strict-markers`, registered `integration` marker) and coverage with `fail_under = 80`; verify `uv run ruff format --check .`, `uv run ruff check .`, `uv run mypy src` and `uv run pytest tests/unit --cov` run clean on the empty skeleton
- [x] 1.3 Add an import-linter contract for `infrastructure → application → domain` and a forbidden-imports contract so `domain` cannot import Jinja2, PyYAML, Pydantic or I/O libraries; verify `uv run lint-imports` passes, and fails when a domain module imports `jinja2` (temporary check, reverted)
- [x] 1.4 Add Jinja2 as a runtime dependency and PyYAML as a development dependency, answering the adoption criteria of `harness/guides/tech-stack.md` (maintenance, license, CVEs, exit cost, size) in the PR notes, and add both to the approved dependencies table of `harness/stacks/backend-python.md` after confirming their licenses; verify the table lists them and `uv.lock` is committed

## 2. Project spec (domain)

- [x] 2.1 Implement `RepositoryName`, `ProjectName` and `Description` with the rules of the spec, trimming and control-character rejection; verify unit tests for every scenario of "Repository name format" (valid, path traversal, unsupported characters, too long) and "Project name and description limits" (trim, control characters, too long)
- [x] 2.2 Implement the typology, application-kind, technology and agent catalogues and the resolution of applications from a typology; verify unit tests for the scenarios of "Supported typologies", "Supported technologies per application" and "Supported AI agents"
- [x] 2.3 Implement `ProjectSpec` validation that returns every error with field and reason and never exposes paths or stack traces; verify unit tests for "Project spec fields" (complete and missing field) and "Validation reports every error" (two errors reported together)
- [x] 2.4 Implement the canonical form (sorted keys, NFC, `schema_version`) and SHA-256 hash; verify unit tests for same values in different field order, a changed value and whitespace normalization
- [x] 2.5 Document the spec fields, rules and catalogues in `apps/backend/README.md`; verify every rule in the document is covered by a test name or scenario

## 3. Templates

- [x] 3.1 Prefix the paths in `templates/harness/AGENTS.md` with `harness/` and verify no unprefixed `guides/`, `adr/` or `stacks/` path remains (grep)
- [x] 3.2 Rewrite `templates/github/CODEOWNERS` as `CODEOWNERS.tmpl` using `<< owner >>`, English comments and the paths `/openspec/`, `/harness/`, `/AGENTS.md`; verify it renders to a valid ownership file in the owner test of group 4
- [x] 3.3 Turn `templates/github/dependabot.yml` into `dependabot.yml.tmpl` with one block per application (`uv`, `nuget` or `npm`, directory `/apps/<name>`) plus `github-actions`; verify the rendered file is valid YAML for each typology (group 6)
- [x] 3.4 Add `templates/agents/claude/CLAUDE.md`, `templates/project/README.md.tmpl`, `templates/project/openspec/config.yaml.tmpl` and `templates/apps/<kind>/README.md.tmpl`, using the `json_str` and `md_escape` filters for every user value; verify each file renders in the end-to-end tests of group 6
- [x] 3.5 Add a template lint test that fails if a `.yml`, `.yaml`, `.json` or `.md` template prints a variable without its format filter, and another that fails if a verbatim file contains the delimiters `<<`, `<%` or `<#`; verify both tests pass, and fail on a deliberately wrong sample (temporary check, reverted)

## 4. Rendering core (application and domain)

- [x] 4.1 Implement the render plan in the domain (templates to destinations, `.tmpl` handling, agent entry file, `.github/ISSUE_TEMPLATE/` mapping, executable marks) with destination validation (relative, normalized, no `..`, no absolute path, no duplicates including case-insensitive); verify unit tests for the monorepo layout scenarios (fullstack, backend-only, frontend-only) and for a plan that escapes the target
- [x] 4.2 Define the `TemplateSource`, `TemplateEngine` and `TreeWriter` ports and the `RenderProject` use case that accepts only a validated spec, validates the owner as a GitHub account name, renders everything in memory, and returns the render and template digests; verify unit tests with fake ports for "Rendering requires a valid spec", "Repository owner" (written, missing, invalid), "Render result digests" and "All or nothing" (a template failing after other files were produced writes nothing)
- [x] 4.3 Implement the Jinja2 engine adapter (`SandboxedEnvironment`, `StrictUndefined`, custom delimiters, no autoescape) with the `json_str` and `md_escape` filters; verify unit tests that `{{ 7 * 7 }}` stays literal, that quotes and colons survive in YAML and JSON, that Markdown control characters are escaped and that an undefined variable fails

## 5. Filesystem adapters

- [x] 5.1 Implement the filesystem `TemplateSource` rooted at a configured directory that refuses symbolic links and paths outside the root; verify integration tests with `tmp_path` for a link and for a traversal attempt
- [x] 5.2 Implement the filesystem `TreeWriter`: refuse a non-empty target, write into a temporary sibling directory with fixed file modes, rename onto the empty target and remove the temporary directory on failure; verify integration tests for a non-empty target left unchanged, an injected failure mid-write leaving the target empty, and a plan path that resolves outside the target writing nothing outside it
- [x] 5.3 Document the writer's atomicity, its POSIX and same-filesystem assumption and the stale temporary directory behavior in `apps/backend/README.md`; verify the document matches the integration tests

## 6. End-to-end rendering checks

- [x] 6.1 Add integration tests that render the three typologies against the real `templates/` and assert the exact set of files for each; verify "Monorepo layout" and "AI agent entry file" scenarios pass
- [x] 6.2 Add determinism tests: render twice into two directories and compare paths and contents, render from two different working directories and assert no absolute host path appears, assert LF line endings and equal digests; verify "Deterministic output" scenarios pass
- [x] 6.3 Add tests that render hostile values (template syntax, quotes, colons, Markdown characters) and re-parse every generated YAML and JSON file; verify "Project values in generated files" scenarios pass
- [x] 6.4 Add a test that renders with `socket` and process-execution functions replaced by ones that raise, and a test that changed templates change the digests; verify "No external effects" and the second "Render result digests" scenario pass

## 7. Quality gates

- [x] 7.1 Run the full quality set from the stack sheet (`ruff format --check`, `ruff check`, `mypy src`, `lint-imports`, `pytest tests/unit --cov=src --cov-fail-under=80`, `pytest tests/integration`); verify all are green and coverage is at or above 80% without lowering any threshold
- [x] 7.2 Run the vulnerability gate (`pip-audit` on `uv.lock` with OSV-Scanner for severity, Bandit and gitleaks); verify no high or critical finding and no secret, without allowlisting or bypassing hooks
- [ ] 7.3 Complete the OWASP checklist for the PR (input validation, path traversal, injection, dependencies) and note the adoption criteria for Jinja2 and PyYAML; verify the checklist is in the PR description
- [x] 7.4 Run `openspec validate add-project-spec-and-rendering --strict`; verify it passes and every scenario of both specs maps to at least one test

## Workflow follow-up

- Work on a branch named `feature/add-project-spec-and-rendering`; never push directly to `main`.
- Archive the change after it is merged and its tasks are complete.
