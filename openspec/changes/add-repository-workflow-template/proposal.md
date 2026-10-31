# Proposal

## Why

The branches ruleset template (`templates/github/rulesets/ruleset-for-branches.json`) requires the status checks `Secret scan`, `OpenSpec validate` and `Commit type matches branch prefix`, but the templates ship no workflow that produces them. A generated project with that ruleset applied can only merge through the admin bypass. The same three checks already run in this repository (`.github/workflows/repository.yml`), so the template can carry a proven workflow.

This is a **functional change**: it alters the file tree that rendering generates (observable output), so OpenSpec applies.

## What Changes

- Add `templates/github/workflows/repository.yml`, a workflow every generated project receives at `.github/workflows/repository.yml`. It runs on pull requests to `main`, on pushes to `main` and weekly, with three jobs named exactly like the checks the ruleset template requires: secret scan, OpenSpec validation and commit-type-matches-branch-prefix.
- The workflow works on an empty generated project (no application code, no lockfiles) and needs no secret other than the default `GITHUB_TOKEN`, so it also works when the owner is an organization.
- Pin third-party actions and the tools it downloads by version, run with read-only permissions, and keep the project values out of the workflow (it is copied verbatim, not rendered).
- Add tests that the workflow is rendered for every typology and that every status check required by the ruleset template is the name of a job in a rendered workflow.

Out of scope (separate changes):

- Workflows for the applications (backend, frontend) and CodeQL. They need application skeletons (`pyproject.toml`, `uv.lock`, `pnpm-lock.yaml`, sources) that `templates/apps/` does not ship yet, so they would fail on a freshly generated project. Candidate follow-ups: `add-application-skeletons`, then `add-application-workflow-templates`.
- Changing which checks the ruleset template requires. Stack-specific checks stay out of it until their workflows exist.
- Applying the ruleset to the generated repository (a later GitHub publishing change).
- Changing this repository's own workflows.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `project-rendering`: the generated tree includes the repository checks workflow for every typology, and the checks required by the ruleset template are produced by rendered workflows.

## Impact

- **Templates:** new file `templates/github/workflows/repository.yml`. No change to the rendering code is expected: the existing mapping already sends `github/*` to `.github/*`.
- **Projects and stack:** the backend application (Python, hexagonal architecture; see `harness/stacks/backend-python.md`) gains tests only. The generated workflow is stack-independent.
- **CI configuration of generated projects:** the change defines their pipeline. It is flagged here as CI configuration, as `AGENTS.md` asks for an explicit request; the request was made by the user.
- **Dependencies and supply chain (security-sensitive):** the workflow pulls third-party GitHub Actions and downloads a pinned gitleaks release and the OpenSpec CLI at CI time. Pinning, checksum verification and permissions are specified; the OWASP checklist (software and data integrity) must be completed in the PR. No authentication, personal data, cryptography or uploads are touched.
- **Exceptions:** none. No ADR is required.
