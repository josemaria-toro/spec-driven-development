# Project generator: backend

Python backend of the project generator, hexagonal architecture (see `harness/stacks/backend-python.md`).

This package currently holds the core: the validated project spec and the deterministic rendering of a new project. It has no inbound adapter (HTTP or CLI) yet.

## Layout

```
src/project_generator/
  domain/          # project spec, catalogues, validation rules (standard library only)
  application/     # use cases and ports
  infrastructure/  # adapters: Jinja2 engine, filesystem
tests/
  unit/            # domain and use cases with fake ports
  integration/     # real filesystem and real templates
```

Commands (from `apps/backend/`):

```bash
uv sync
uv run ruff format --check . && uv run ruff check .
uv run mypy src
uv run lint-imports
uv run pytest tests/unit --cov
uv run pytest tests/integration
```

## Project spec

`ProjectSpec.from_raw(data)` validates untrusted data and reports **every** invalid field at once (`ValidationFailedError.issues`, each with a field and a readable reason). An invalid `ProjectSpec` cannot be constructed.

| Field | Rule |
|---|---|
| `project_name` | Required, trimmed, 1 to 100 characters, no control characters or line breaks |
| `repository_name` | Required, trimmed, 1 to 100 characters, only lowercase letters, digits and hyphens, not starting or ending with a hyphen |
| `description` | Optional, trimmed, at most 350 characters, no control characters or line breaks |
| `typology` | `backend`, `frontend` or `fullstack` |
| `technologies` | One technology per application of the typology (see below) |
| `agent` | `claude` |

Typologies and applications (each application lives in `apps/<kind>`):

| Typology | Applications |
|---|---|
| `backend` | backend |
| `frontend` | frontend |
| `fullstack` | backend and frontend |

Technologies per application kind: backend `python` or `csharp`; frontend `react-typescript`. A technology for an application the typology does not contain is rejected.

### Canonical form and hash

`canonical_form()` is JSON with sorted keys, no spaces, Unicode NFC text and a `schema_version`. `content_hash()` is its SHA-256 (hex). Equal values give equal hashes regardless of field order, surrounding whitespace or Unicode composition; any other change to a value changes the hash.

## Rendering

`RenderProject.execute(spec, owner, target)` validates the spec (a raw mapping or a `ProjectSpec`) and the owner (a GitHub account name), maps the templates to destinations, renders every file **in memory** and only then writes the tree. It returns the list of files, a digest of the generated tree and a digest of the templates used, so a caller can tell that a later rendering differs from an earlier one.

Templates (`templates/` at the repository root) are mapped as follows; only files ending in `.tmpl` are rendered, the rest are copied byte for byte:

| Template | Destination |
|---|---|
| `harness/AGENTS.md` | `AGENTS.md` |
| `harness/**` | `harness/**` |
| `github/issues/*` | `.github/ISSUE_TEMPLATE/*` |
| `github/rulesets/**` | not rendered (applied through the GitHub API) |
| `github/*` | `.github/*` |
| `agents/<agent>/*` | repository root (only the selected agent) |
| `project/**` | repository root |
| `apps/<kind>/**` | `apps/<kind>/**` (only the kinds of the typology) |

Template syntax is `<< value >>`, `<% block %>` and `<# comment #>`, so `${{ ... }}` and `[[ ... ]]` pass through untouched. Every user value must use the filter of its target format: `json_str` (YAML and JSON), `md_escape` (Markdown) or `yaml_block` (text inside a YAML block scalar); a lint test enforces it. Values are data and are never evaluated as template syntax.

### Writing the tree

`FilesystemTreeWriter` writes into a temporary directory next to the target and renames it onto the target, so the target is either left as it was or complete.

- The target must be missing or an empty directory; anything else (a file, a link, a directory with content) is refused and left unchanged.
- Paths that are absolute or contain `..` are refused before anything is written.
- File modes are fixed (`0644`, `0755` for executable files and directories).
- The rename is atomic on POSIX when both directories share a filesystem, which they do because the temporary directory is a sibling of the target. Windows is not supported.
- A crash can leave a stale directory named `.<target>.tmp-*` next to the target, never a partial target. Whoever owns the parent directory (the run engine, later) is expected to clean it.
- `FilesystemTemplateSource` refuses symbolic links and any path outside the templates root.
