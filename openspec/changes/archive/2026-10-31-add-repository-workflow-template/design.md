# Design

## Context

See `proposal.md` for the motivation. Observed state:

- Rendering maps `templates/github/<path>` to `.github/<path>`, except `rulesets/` (not rendered) and `issues/` (to `.github/ISSUE_TEMPLATE/`). A file at `templates/github/workflows/repository.yml` therefore lands at `.github/workflows/repository.yml` with no code change. Files without the `.tmpl` suffix are copied byte for byte.
- `templates/apps/` holds only a README per application, so a generated project has no code and no lockfiles.
- The ruleset template requires the contexts `Secret scan`, `OpenSpec validate` and `Commit type matches branch prefix`.
- This repository already runs a workflow with those three jobs (`.github/workflows/repository.yml`). Its secret scan uses `gitleaks/gitleaks-action`, which needs a paid license secret when the repository belongs to an organization.
- `openspec validate --all` in an empty generated layout (`openspec/specs/.gitkeep`, `openspec/changes/.gitkeep`) prints "No items found to validate" and exits 0 (checked with OpenSpec 1.15.0).

## Goals / Non-Goals

**Goals:**

- A generated project can satisfy the three generic required checks with no extra setup.
- The workflow cannot silently drift from the ruleset template: a test ties their names together.

**Non-Goals:**

- Application workflows and CodeQL (see the proposal).
- Parameterizing the workflow by project values or typology.

## Decisions

1. **Copy the workflow verbatim (no `.tmpl`).** It uses no project value, and GitHub expressions (`${{ ... }}`) must reach the output untouched. This also gives the "byte-identical for every spec" scenario for free. Alternative: render it as a template to inject the default branch or owner; rejected, YAGNI (`main` is the only persistent branch by the harness).

2. **No change to the render plan.** The existing `github/*` mapping is enough. A unit test pins that `github/workflows/*.yml` maps to `.github/workflows/*.yml`, so a future change to the mapping is noticed.

3. **Secret scan with the gitleaks release binary, not `gitleaks-action`.** The binary needs no license, so the workflow works for personal and organization owners and needs only `GITHUB_TOKEN`. The job downloads a pinned release tarball and checks it against a SHA-256 pinned in the workflow before extracting it. Alternatives: the action (license for organizations, rejected); the container image (needs Docker pull and a digest to pin, no gain over a verified tarball); downloading the checksums file from the same release (an attacker who replaces the tarball replaces the checksums, so it proves nothing, rejected).

4. **OpenSpec CLI through `npx` at a pinned version** on a pinned Node major, the same way this repository runs it. Verified to succeed on an empty project.

5. **Job names are the contract with the ruleset.** The three job `name:` values equal the ruleset contexts. An integration test reads the ruleset template, extracts the required contexts and checks each one is a job name in the rendered workflows, so renaming either side fails the build.

6. **Commit-type check stays an inline shell step**, as here: it only needs `git log` and a regular expression, and an extra action would add supply chain for no gain.

7. **Actions pinned to major tags**, consistent with this repository and with `harness/guides/security.md` ("pinned by version/SHA"). The generated `dependabot.yml` already has the `github-actions` ecosystem, which proposes updates.

## Risks / Trade-offs

- [The pinned gitleaks version and checksum go stale; Dependabot does not track a downloaded tarball] → The version and checksum sit together at the top of the job; the workflow's weekly run uses the pin, and the README of `templates/` (or the task that adds the workflow) documents how to bump both. Accepting an old scanner for a while is lower risk than an unverified download.
- [This repository's own workflow keeps `gitleaks-action` while the template uses the binary] → Both are valid for a personal account; aligning this repository to the template is a separate chore, noted here so the difference is deliberate.
- [A rejected or renamed required check blocks every merge in a generated repository] → Decision 5's test; the ruleset template and the workflow change together or not at all.
- [The OpenSpec CLI or npm registry is unavailable at CI time and the check fails] → The failure is visible and retryable; no secret or write permission is at stake.
- [Required checks make a project without the workflow unmergeable] → Not possible through rendering, since every typology receives the workflow.

## Threat model (supply chain)

The trust boundary changed by this design is the CI runner executing code fetched at run time: third-party actions (`actions/checkout`, `actions/setup-node`), the npm package `@fission-ai/openspec` and the gitleaks tarball.

- Actions and the npm package are pinned to versions; the tarball to a SHA-256. An unpinned or branch reference is a defect.
- The workflow has read-only `contents` permission and checks out without persisting credentials, so a compromised step cannot push or publish.
- No custom secrets are referenced, so none can be exfiltrated by these steps; `GITHUB_TOKEN` is read-only.
