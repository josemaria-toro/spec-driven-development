# Development harness

A template for bootstrapping projects with guides, guardrails and versioned decisions, designed to work with people and AI agents (spec-driven development).

All content is written in **English**.

## Contents

```
AGENTS.md              # entry point: precedence and what to read per task
guides/
  development.md       # style, errors, logging, Definition of Done
  development-python.md  # Python: practices, naming, ordering, imports, dependencies
  development-csharp.md  # C#: practices, naming, ordering, usings, dependencies
  development-react.md   # React/TypeScript: practices, naming, ordering, imports, dependencies
  openspec.md            # OpenSpec: mandatory for every functional change
  architecture.md      # hexagonal or clean architecture, dependency rule, APIs, persistence
  tech-stack.md        # adoption criteria, licenses, dependencies
  security.md          # OWASP baseline, secrets, authn/z, data, supply chain
  guardrails.md        # non-negotiable rules and automatic controls
  testing.md           # pyramid, determinism, coverage
  git-workflow.md      # branches, commits, PRs, releases
stacks/
  _template.md         # blank sheet for a new technology/project
  backend-python.md    # backend: Python
  backend-csharp.md    # backend: C# (.NET)
  frontend-react.md    # frontend: React + TypeScript
adr/
  0000-template.md     # record of decisions and exceptions
```

## Usage

1. Copy the contents to the root of the new project.
2. Create `stacks/<name>.md` from `_template.md`, and initialize OpenSpec in the project (`openspec/`).
3. Adjust the guides to your context; any change to a guardrail is recorded as an ADR.
4. Automate the controls in `guides/guardrails.md` (pre-commit and CI).

## Repository workflow

`.github/workflows/repository.yml` is generated with every project and runs on pull requests to `main`, on pushes to `main` and weekly. Its jobs are named exactly like the status checks the `main` ruleset requires, so keep the names and the ruleset in sync:

| Job (required check) | What it does |
|---|---|
| `Secret scan` | Scans the full Git history with gitleaks. |
| `OpenSpec validate` | Runs `openspec validate --all`. |
| `Commit type matches branch prefix` | Checks that every commit type of a pull request equals its branch prefix (see `guides/git-workflow.md`). |

It needs no secret other than the default `GITHUB_TOKEN`. gitleaks is downloaded as a release binary and checked against a pinned SHA-256 before it runs. To bump it, change `GITLEAKS_VERSION` and `GITLEAKS_SHA256` together (the checksum of `gitleaks_<version>_linux_x64.tar.gz` in the release assets), and compute the checksum yourself from the downloaded file as well as reading it from the release.

## Still to define

- Pre-commit configuration and the CI workflows of the applications (tests, lint, types, dependency audit, CodeQL).
- PR template; OpenSpec initialization (`openspec init`).
