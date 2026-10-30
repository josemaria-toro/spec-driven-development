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

## Still to define

- Pre-commit configuration and CI workflows.
- PR template; OpenSpec initialization (`openspec init`) and CI validation.
