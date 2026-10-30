# Harness

The harness of this repository: the guides, guardrails, stack sheets and decisions that define **how we work here**, for people and AI agents (spec-driven development).

It is the single source of truth. Its entry point is [`AGENTS.md`](../AGENTS.md) at the repository root, which sets the precedence between documents and says which guide to read for each task. `CLAUDE.md` only imports `AGENTS.md`.

All content is written in **English**.

## Purpose of this repository

This repository is used to **create development projects**: create the project repository, configure it, initialize it, generate the initial scaffolding and leave it ready to work.

It will be built as an application with two parts:

- a **web application** (frontend) that guides the user through the whole process;
- a **backend** that interacts with **GitHub** (repository creation and configuration) and with **Claude**.

The reusable material the generator works from lives in `templates/`. The `stacks/` sheets apply to this application itself and also describe the stacks of the projects it generates. Declared stack of the generator: frontend React (TypeScript), backend Python, hexagonal architecture.

The generator is a functional change, so it starts with an OpenSpec proposal (`/opsx:propose`).

## Contents

```
guides/
  development.md         # language-agnostic style, errors, logging, Definition of Done
  development-python.md  # Python: practices, naming, ordering, imports, dependencies
  development-csharp.md  # C#: practices, naming, ordering, usings, dependencies
  development-react.md   # React/TypeScript: practices, naming, ordering, imports, dependencies
  openspec.md            # OpenSpec: mandatory for every functional change, /opsx commands
  architecture.md        # hexagonal or clean architecture, dependency rule, APIs, persistence
  tech-stack.md          # supported languages, platform defaults, admitted tooling, licenses
  security.md            # OWASP baseline, secrets, authn/z, data, supply chain
  guardrails.md          # non-negotiable rules, pre-commit gates, automatic controls
  testing.md             # mandatory levels, frameworks, determinism, coverage
  git-workflow.md        # trunk-based flow, branches, commits, PRs, releases
stacks/
  backend-python.md      # backend: Python
  backend-csharp.md      # backend: C# (.NET)
  frontend-react.md      # frontend: React + TypeScript
  _template.md           # blank sheet for a new stack
adr/
  0000-template.md       # template for decisions and guardrail exceptions
  0001-node-20-minimum-version-exception.md   # proposed
```

Related, outside this folder:

- `openspec/`: OpenSpec specs and changes, configured in `openspec/config.yaml` to follow this harness.
- `templates/`: reusable templates for other projects (including a copy of a harness). They are independent from this folder and do not need to be aligned with it.

## How it is used

- Before acting, read `AGENTS.md` and the guides it assigns to the task.
- Functional changes go through OpenSpec first (see `guides/openspec.md`).
- Any exception to a guide or guardrail needs an ADR in `adr/` with an owner and an expiry date.
- Rule changes are made here, in `harness/`; other files such as `CLAUDE.md` must not restate them.

## Current status

The harness documents what must be enforced; the automation itself is not in the repository yet:

- Not yet implemented: pre-commit configuration (formatting, lint, secret and vulnerability scan, 80% coverage gate), CI workflows, the PR template and OpenSpec validation in CI.
- ADR-0001 (Node 20 as minimum version) is still `proposed`: the reason Node 20 is required and the expiry date need to be confirmed.
- Tool names, commands and licenses in the stack sheets were written without being run or verified; confirm them when the tools are first configured.
