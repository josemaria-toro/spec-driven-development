# Proposal

## Why

This repository will become an application that creates development projects. Everything the generator does later (the guided chat, the persisted runs, the publication to GitHub) depends on two pure building blocks: a validated description of the project to create (`ProjectSpec`) and a deterministic way to turn that description into the initial file tree. Building them first, with no network access, no GitHub and no Claude, gives the rest of the system a stable, fully testable core.

This is a **functional change** (it introduces observable behavior: validation rules and generated output), so OpenSpec applies.

## What Changes

- Introduce `ProjectSpec`: project name, repository name, description, project typology, technologies and AI agent, with strict validation of every field.
- Introduce a canonical serialization and a content hash of a `ProjectSpec`, so later changes can confirm and freeze exactly what the user approved.
- Introduce deterministic rendering: given a valid `ProjectSpec` and the templates in `templates/`, produce the complete initial file tree of a **monorepo** (one harness, OpenSpec and `.github/` at the root, one directory per application under `apps/`) without side effects outside a target staging directory.
- Render the agent entry file that matches the chosen AI agent, importing the root `AGENTS.md`.
- Create the backend application skeleton that hosts this core (Python, hexagonal architecture), limited to what this change needs.

Out of scope (covered by later changes):

- The persisted runs, steps, progress streaming and resume (`add-run-engine`).
- Any call to `gh` or to GitHub, including `openspec init`, commits, pushes, repository settings and rulesets (`add-github-publishing`).
- The agentic chat and the confirmation button (`add-guided-chat`).
- The project list, detail and progress views (`add-project-dashboard`).
- Obtaining the owner, organization and visibility of the repository from backend configuration and freezing them with the confirmed spec: a later change. Rendering only receives the owner as an input.
- Any use of Claude. Rendering is deterministic and never calls a model.

## Capabilities

### New Capabilities

- `project-spec`: the validated description of a project to create, its allowed values, and its canonical form and hash.
- `project-rendering`: deterministic generation of the initial monorepo file tree from a valid project spec and the templates.

### Modified Capabilities

None. `openspec/specs/` has no capabilities yet.

## Impact

- **Stack and architecture:** new backend application in Python, hexagonal architecture (domain with no framework imports; the filesystem and the template source are adapters behind ports). Stack sheet: `harness/stacks/backend-python.md`.
- **Templates:** reads `templates/` as input. The change reveals that `templates/github/CODEOWNERS` and the rulesets are not parameterized yet; making them templates is part of this change's tasks only for the files that rendering emits.
- **Dependencies:** a template engine (Jinja2, see the design) and, for tests only, a YAML parser; both outside the current approved table and adopted under `harness/guides/tech-stack.md`. Validation is plain Python, so there is no validation library. No new platform service.
- **Security-sensitive areas:** input validation of user-provided names and descriptions that end up in file paths and file contents (path traversal, template injection, shell metacharacters). The OWASP checklist must be completed in the PR. No authentication, personal data, cryptography or uploads are touched.
- **Exceptions:** none. No ADR is required.
