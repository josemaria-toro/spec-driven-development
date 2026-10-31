# SDD Project Builder

SDD Project Builder is a repository used to **create development projects**: it validates a project description, renders a ready-to-work repository from templates (harness, GitHub configuration, AI agent files and application skeletons) and keeps the way of working in a versioned harness.

Everything is developed spec-driven: no functional change is coded before its [OpenSpec](https://github.com/Fission-AI/OpenSpec) change proposal exists and is approved.

All content is written in **English**.

## Start here

Read [`AGENTS.md`](AGENTS.md). It is the entry point for people and AI agents: it sets the precedence between documents and says which guide to read for each task. `CLAUDE.md` only imports it.

## Layout

```
AGENTS.md      # entry point to the harness
harness/       # guides, stacks and ADRs: how we work in this repository
apps/
  backend/     # sdd-api: Python backend (hexagonal), project spec and rendering
  frontend/    # sdd-web: React (TypeScript) web application skeleton
templates/     # reusable templates rendered into new projects (independent from harness/)
openspec/      # specs and change proposals
.claude/       # skills and commands for Claude Code
```

| Directory | What it holds |
|---|---|
| [`harness/`](harness/README.md) | Guardrails, development, testing, security, Git and architecture guides, stack sheets and ADRs. Authoritative. |
| [`apps/backend/`](apps/backend/README.md) | Python package `sdd`, distribution `sdd-api`. Validated `ProjectSpec` and deterministic rendering. No HTTP or CLI adapter yet. |
| [`apps/frontend/`](apps/frontend/README.md) | Distribution `sdd-web`. One page, quality tooling and test levels. |
| `templates/` | What a generated project receives. Edit only when the task is about the templates. |
| `openspec/` | Current specs (`specs/`), open changes (`changes/`) and archived ones (`changes/archive/`). |

## Requirements

- Python 3.12 or newer and [`uv`](https://docs.astral.sh/uv/)
- Node.js 20 or newer and [`pnpm`](https://pnpm.io/)

## Getting started

Backend (from `apps/backend/`):

```bash
uv sync
uv run ruff format --check . && uv run ruff check .
uv run mypy src
uv run lint-imports
uv run pytest tests/unit --cov
uv run pytest tests/integration
```

Frontend (from `apps/frontend/`):

```bash
pnpm install --frozen-lockfile
pnpm lint
pnpm typecheck
pnpm test:unit --coverage
pnpm test:integration
pnpm exec playwright install chromium   # once
pnpm e2e
pnpm dev
```

See each application's README for the full list of commands and its layout.

## How we work

1. **Specify**: create the OpenSpec change proposal before writing code.
2. **Plan**: small, verifiable tasks in the change's `tasks.md`.
3. **Implement** with tests in the same change.
4. **Verify**: lint, types, tests (coverage at least 80%), security review and `openspec validate` all green.
5. **Archive** the change so the specs reflect the new behavior.
6. **Record** an ADR for architecture decisions or exceptions to a guide.

Git is trunk-based: `main` is the only persistent branch and temporary branches use the prefixes `feature/`, `bug/`, `hotfix/`, `chore/` and `change/`. Details are in [`harness/guides/git-workflow.md`](harness/guides/git-workflow.md).
