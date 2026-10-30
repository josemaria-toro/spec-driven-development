# Design

## Context

See `proposal.md` for the motivation and `specs/` for the requirements. This change builds the first part of the generator backend: Python, hexagonal architecture (`harness/stacks/backend-python.md`, `harness/guides/architecture.md`). The stack sheet forbids FastAPI, Pydantic, SQLAlchemy and any I/O library in `domain/`, and requires `mypy --strict`, import-linter and 80% coverage.

Facts about the current inputs that shape the design:

- `templates/` holds only a harness copy and `templates/github/` (CODEOWNERS, dependabot, issue forms, rulesets). There are no application skeletons, no root README, no `CLAUDE.md` template and no OpenSpec config template.
- `templates/harness/AGENTS.md` refers to guides without the `harness/` prefix, but the generated monorepo puts `AGENTS.md` at the root and the harness in `harness/` (as in this repository). It needs adapting.
- `templates/github/CODEOWNERS` has a hardcoded owner and Spanish comments.
- Files that will exist in generated projects later (CI workflows) contain `${{ ... }}`, and `pyproject.toml` contains `[[tool...]]`. The template syntax must not collide with them.

## Goals / Non-Goals

**Goals:**

- A pure domain core (spec, validation, canonical form, application resolution, render plan) with no framework or I/O imports.
- Rendering that is deterministic, side-effect free outside one directory, and all-or-nothing.
- A render result that lets later changes detect that templates changed between a failed run and its resume.

**Non-Goals:**

- Runnable application scaffolding. Each application directory contains a `README.md` that states its kind, technology and the stack sheet to follow; build files, lint configuration, pre-commit and CI workflows are later changes.
- Tailoring the copied harness to the selected technologies. The harness is copied whole and verbatim (apart from the files listed below).
- Emitting rulesets into the repository tree: they are applied through the GitHub API by `add-github-publishing`.
- An inbound adapter (HTTP or CLI). The use case is exercised directly by tests until the chat change needs one.

## Decisions

### D1. Validation lives in the domain as plain Python, not Pydantic

`ProjectSpec` and its value objects (`RepositoryName`, `ProjectName`, `Description`) are frozen dataclasses validated in the domain, which returns every error at once as a list of `(field, reason)`. Pydantic belongs to the HTTP edge (a later change), where it will map requests into these types.

Alternative: Pydantic models in the domain. Rejected: the stack sheet forbids it, and it would tie the core to a library.

### D2. Catalogues are domain data

Typologies, application kinds, technologies per kind and AI agents are constants in the domain:

| Catalogue | Content |
|---|---|
| Typology to applications | `backend` → backend; `frontend` → frontend; `fullstack` → backend + frontend |
| Technology per kind | backend: `python`, `csharp`; frontend: `react-typescript` |
| Agent | `claude` → entry file `CLAUDE.md` |

Application directories are `apps/backend` and `apps/frontend`. Adding a typology, technology or agent is then a data change plus its templates, with no change to the rendering logic.

### D3. Canonical form and hash

The canonical form is JSON with sorted keys, no insignificant whitespace, UTF-8, strings in Unicode NFC, and a `schema_version` field. The hash is SHA-256 over those bytes, hex-encoded. `schema_version` ensures that a future change of the spec shape cannot silently collide with an older hash.

### D4. Render in two stages: plan, then write

```
ProjectSpec + RenderInputs(owner)
        |  (domain, pure)
        v
   RenderPlan: [(template path, destination path, mode: render | verbatim)]
        |  (application: TemplateSource + TemplateEngine ports)
        v
   RenderedTree: {relative path -> bytes}  (all in memory, validated)
        |  (TreeWriter port)
        v
   target directory  (temp sibling dir, then rename)
```

- The plan is computed in the domain from the typology, applications and agent. It decides which templates apply to which destination (for example `templates/github/issues/*` goes to `.github/ISSUE_TEMPLATE/`, and the agent entry file comes from the agent catalogue).
- All files are rendered and validated in memory first, so almost every failure happens before the disk is touched. Destination paths are checked once, on the plan: relative, normalized, no `..`, no absolute path, no duplicate (including case-insensitive duplicates).
- The writer creates a temporary directory next to the target, writes the tree with fixed file modes (`0644`, or `0755` only for files the plan marks executable), and renames it onto the empty target. A rename of a directory over an empty directory is atomic on POSIX; a crash can leave only a stale temporary directory, never a partial target. The target must be empty or absent, and links in templates are refused rather than followed.

Alternative: write straight into the target and delete on failure. Rejected: a crash would leave a partial tree, which defeats the "all or nothing" requirement and the atomic steps of the later run engine.

### D4b. Ports

| Port | Owned by | Adapter |
|---|---|---|
| `TemplateSource` (list and read template files) | application | filesystem, rooted at the configured templates directory |
| `TemplateEngine` (render text with values) | application | Jinja2 |
| `TreeWriter` (write a `RenderedTree` to a directory) | application | filesystem |

The engine is behind a port so the domain and the use case do not import Jinja2.

### D5. Template engine: Jinja2, with custom delimiters

Jinja2 (BSD-3-Clause, allowed license) in a `SandboxedEnvironment` with `StrictUndefined` and autoescape off. Delimiters are changed to `<< ... >>` for variables, `<% ... %>` for blocks and `<# ... #>` for comments, which collide with neither `${{ }}` nor `[[ ]]`. A test asserts that no verbatim file contains these delimiters by accident.

Values reach the engine only as data in the render context and are never concatenated into template source, so a value such as `{{ 7 * 7 }}` is output as text. The sandbox is defense in depth: templates come from the repository, and the untrusted input is the values.

Alternatives: `string.Template` (stdlib, no logic, but no conditionals or loops for the dependabot blocks and per-application sections) and Mustache (logic-less, needs a new dependency with less ecosystem support). Jinja2 is the best fit for the few parametrized files.

A template is rendered only if its name ends in `.tmpl`, which is removed from the destination name. Everything else is copied byte for byte.

### D6. Escaping is per target format, with explicit filters

Autoescape cannot know the target format, so each format has a filter and templates must use it for every user value:

| Target | Filter |
|---|---|
| YAML and JSON values | `json_str` (`json.dumps` with `ensure_ascii=False`; a double-quoted JSON string is also a valid YAML scalar) |
| Text inside a YAML block scalar (`context: \|`) | `yaml_block` (the value unchanged, rejected if it has a line break) |
| Markdown | `md_escape` (escapes Markdown control characters and a leading list marker; line breaks are already impossible by validation) |
| Plain text or CODEOWNERS | none: the owner is already validated as a GitHub account name, and the project values are not used there |

`json_str` keeps non-ASCII text as is: with `ensure_ascii=True`, characters outside the BMP become surrogate pairs that YAML parsers read back as two lone surrogates instead of the original character.

A template lint test fails if a `.yml`, `.yaml`, `.json` or `.md` template prints a variable without its filter. This makes "forgot the filter" a test failure instead of a review finding.

### D7. Render result with digests

Rendering returns the tree digest (SHA-256 over sorted relative paths and contents) and a digest of the template set it read. The later run engine stores both. When a failed run is resumed after templates have changed, the digest differs and the run can refuse or flag it instead of publishing a mixed result. Rendering stays deterministic only relative to a given template version, so this signal is needed.

### D8. Templates this change adds or adapts

| Template | Change |
|---|---|
| `templates/harness/AGENTS.md` | Paths prefixed with `harness/`, as in this repository |
| `templates/github/CODEOWNERS` | `<< owner >>`, English comments, paths `/openspec/ /harness/ /AGENTS.md` |
| `templates/github/dependabot.yml` | Becomes a template with one block per application (`uv`, `nuget` or `npm`, directory `/apps/<name>`) plus `github-actions` |
| `templates/agents/claude/CLAUDE.md` | New: imports `AGENTS.md`, defines no rules |
| `templates/project/README.md.tmpl` | New: project name, description, layout |
| `templates/project/openspec/config.yaml.tmpl` | New: project context and the harness rules, as in this repository's `openspec/config.yaml` |
| `templates/apps/<kind>/README.md.tmpl` | New: kind, technology and stack sheet; rendered with an extra `application` value for its own kind |

Because `templates/` is independent from the repository harness, editing it does not require aligning `harness/`.

### D8b. Owner is a render input

`RenderInputs.owner` is validated as a GitHub account name (1 to 39 characters, letters, digits and single hyphens, no leading or trailing hyphen). It is not part of `ProjectSpec` and therefore not part of its hash; the run engine will merge it from backend configuration and freeze it with the confirmed spec.

## Risks / Trade-offs

- **A template prints a user value without its filter** (injection into YAML or Markdown) → the template lint test (D6) and scenarios that render hostile values and re-parse the output.
- **Path traversal through a value or a template** → names are validated by an allow-list in the domain, destinations are validated again on the plan, and the writer re-checks that the resolved path stays inside the target.
- **Stale temporary directory after a crash** → harmless for the target; the run engine owns the staging root and can clean it. Documented in the writer.
- **Templates change between a failure and its resume** → render and template digests (D7).
- **Sandbox is not a security boundary** → we never rely on it alone: values are never template source, templates are repository-controlled.
- **Rename atomicity assumes POSIX and one filesystem** → the temporary directory is created as a sibling of the target; other platforms are unsupported and stated in the stack notes.
- **Jinja2 and PyYAML are not in the approved dependency table** → adoption criteria answered in the PR and the table in `harness/stacks/backend-python.md` updated; PyYAML is a development dependency used only to re-parse generated files in tests.

## Open Questions

- Whether `openspec init` (skills and commands for the chosen agent) runs on the staging tree before the single commit, or its output is vendored in templates. It does not change this change; it is decided in `add-github-publishing`, which also has to check that `openspec init` accepts an existing `openspec/config.yaml`.
- Where the `templates/` directory lives at runtime once the backend is packaged (path from configuration, bundled in the image). The use case only sees the `TemplateSource` port, so this is decided with the deployment.
