# AGENTS.md

Entry point for AI agents and people. It defines **how we work** in this project. Detailed rules live in `harness/guides/`; this file only says which one to read and when. The harness lives in `harness/`; its own documents refer to each other with paths relative to `harness/`.

## Precedence

If two documents conflict, the first one in this list wins:

1. `harness/guides/guardrails.md` and `harness/guides/security.md` (never relaxed without an ADR).
2. Active ADRs in `harness/adr/`.
3. The project's `harness/stacks/<stack>.md`.
4. The language guide (`harness/guides/development-<language>.md`).
5. The rest of `harness/guides/`.

## Which guide to read for each task

| Task | Read |
|---|---|
| Any change | `harness/guides/guardrails.md`, `harness/guides/development.md` |
| Any functional change | `harness/guides/openspec.md` (before writing code) |
| Writing code in a language | `harness/guides/development-python.md`, `development-csharp.md` or `development-react.md` |
| Creating modules, layers or dependencies | `harness/guides/architecture.md` |
| Choosing or adding a library/tool | `harness/guides/tech-stack.md`, `harness/stacks/` |
| Auth, personal data, secrets, dependencies | `harness/guides/security.md` |
| Writing or changing tests | `harness/guides/testing.md` |
| Commits, branches, PRs, releases | `harness/guides/git-workflow.md` |
| Non-trivial decisions | `harness/adr/0000-template.md` |

## Workflow (spec-driven)

**OpenSpec is mandatory for every functional change** (see `harness/guides/openspec.md`). No code is written for a functional change until its OpenSpec change proposal exists and is approved.

1. **Specify**: create the OpenSpec change proposal (what and why, requirements, scenarios) before writing code.
2. **Plan**: small, verifiable tasks listed in the change's `tasks.md`.
3. **Implement** with tests in the same change; tick tasks off as they are done.
4. **Verify**: lint, types, tests, security review and `openspec validate` all green.
5. **Archive**: archive the change so the specs reflect the new behavior.
6. **Record**: write an ADR if there was an architecture decision or an exception to a guide.

## Rules for agents

- Do not invent commands, paths or APIs: verify them in the repo.
- When an ambiguity would change the outcome, ask; otherwise pick the guides' default and say so.
- Keep changes small and reviewable. Do not mix refactoring with new functionality.
- Do not touch secrets, CI configuration or permissions without an explicit request.
- If a guide blocks you, do not bypass it: propose an ADR.

## Language

All project content (code, comments, docs, commits, PRs, ADRs) is written in **English**.
