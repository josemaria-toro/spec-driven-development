# Git and delivery guide

## Branches

Trunk-based flow: **`main` is the only persistent branch**. It is always deployable and protected. There are no long-lived `develop`, `release` or environment branches.

All work happens in temporary branches created from `main` and deleted after merge:

| Prefix | Use |
|---|---|
| `feature/<name>` | New functionality |
| `bug/<name>` | Non-urgent bug fix |
| `hotfix/<name>` | Urgent fix for a production issue |
| `chore/<name>` | Maintenance with no behavior change (deps, tooling, CI, docs) |
| `change/<name>` | Spec-driven change that alters or refactors existing behavior |

- Names are lowercase kebab-case and, for functional changes, use the OpenSpec change id: `feature/add-order-export` (see `openspec.md`).
- Maximum lifetime of a few days; split larger work into smaller branches.
- Integration through Pull Requests into `main`; squash or merge without noisy history.
- `hotfix/*` follows the same PR and CI rules, with expedited review; it is never pushed directly to `main`. After merge, release a patch version.

## Commits (Conventional Commits, aligned with branch prefixes)

```
<type>(<scope>): <summary in imperative mood, ≤72 characters>

<body: what and why, not how>
```

The commit type is the same as the branch prefix, so the type of a branch's commits is predictable:

| Type | Branch | Version bump |
|---|---|---|
| `feature` | `feature/*` | minor |
| `bug` | `bug/*` | patch |
| `hotfix` | `hotfix/*` | patch |
| `change` | `change/*` | minor (major if breaking) |
| `chore` | `chore/*` | none |

- Example: `feature(export): add CSV export for users`.
- Breaking change: `!` after the type (`change(api)!: …`) and `BREAKING CHANGE:` in the body; bumps major.
- Docs, tests, CI and refactors with no behavior change use `chore`, with the area in the scope (`chore(ci): …`, `chore(docs): …`).
- CI checks that the commit type matches the branch prefix.

## Pull Requests

- One purpose per PR; description with **what**, **why** and **how to test it**.
- Link the OpenSpec change (`openspec/changes/<change-id>/`) and list the requirements/scenarios implemented; mandatory for functional changes.
- Green CI before requesting review.
- Security checklist completed where applicable (see `security.md`).
- Review feedback is addressed in new commits; cleaned up on merge.

## Review

- Review: correctness, clarity, tests, security, architecture (dependency rule).
- Critique the code, not the person; distinguish blocking from suggestions.
- The author does not approve their own code alone. If the team is a single person, document the exception in an ADR.

## Versioning and releases

- Semantic versioning (`MAJOR.MINOR.PATCH`).
- Changelog generated from commit types (`feature`, `bug`, `hotfix`, `change` are listed; `chore` is omitted).
- Every release has a signed tag and release notes.
- Deployment automated from CI; no undocumented manual steps.
- A known rollback plan before every deployment.
