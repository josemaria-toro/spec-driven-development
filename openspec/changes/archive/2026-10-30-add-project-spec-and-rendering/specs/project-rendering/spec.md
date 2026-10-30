# Spec Delta

## Purpose

Defines how a valid project spec is turned into the complete initial file tree of a monorepo, deterministically and without side effects outside a target directory, so that the result can be regenerated at any time.

## ADDED Requirements

### Requirement: Monorepo layout
Rendering SHALL produce a single repository tree with `AGENTS.md`, `harness/`, `openspec/` and `.github/` at its root and one directory under `apps/` for each application of the project typology.

#### Scenario: Fullstack project
- **GIVEN** a valid `fullstack` spec
- **WHEN** the project is rendered
- **THEN** the tree contains the root files and directories, `apps/` has one directory for the backend and one for the frontend, and no other application directory exists

#### Scenario: Backend-only project
- **GIVEN** a valid `backend` spec
- **WHEN** the project is rendered
- **THEN** `apps/` contains only the backend directory

### Requirement: Deterministic output
Rendering the same spec, the same render inputs and the same templates MUST produce byte-identical files with the same relative paths on every run. The output SHALL NOT contain timestamps, random values, absolute paths or host-specific data, and text files SHALL use LF line endings.

#### Scenario: Two runs are identical
- **GIVEN** a valid spec rendered twice into two empty directories
- **WHEN** both trees are compared
- **THEN** they contain the same paths and every file has the same content

#### Scenario: Output does not depend on the host
- **GIVEN** the same spec rendered from two different working directories
- **WHEN** both trees are compared
- **THEN** no file contains an absolute path of the host

### Requirement: Render result digests
A successful rendering SHALL return a digest of the generated tree and a digest of the set of templates it used, so that callers can detect that the output differs from an earlier rendering of the same spec.

#### Scenario: Digest is stable for the same inputs
- **GIVEN** a valid spec rendered twice with unchanged templates
- **WHEN** both results are compared
- **THEN** the tree digests are equal and the template digests are equal

#### Scenario: Changed template changes the digests
- **GIVEN** a valid spec rendered once, then rendered again after a template changed
- **WHEN** both results are compared
- **THEN** the template digests are different and the tree digests are different

### Requirement: Project values in generated files
Rendering SHALL write the project name, the repository name and the description into the generated files that refer to them. Values SHALL be inserted as literal data and MUST NOT be interpreted as template syntax or markup of the target format.

#### Scenario: Values appear in the output
- **GIVEN** a valid spec
- **WHEN** the project is rendered
- **THEN** the root documentation of the generated project shows the project name and the description

#### Scenario: Template syntax in a value is kept literal
- **GIVEN** a spec whose description contains `{{ 7 * 7 }}`
- **WHEN** the project is rendered
- **THEN** the generated files contain the text `{{ 7 * 7 }}` and not `49`

#### Scenario: Structured file stays valid
- **GIVEN** a spec whose description contains quotes and colons
- **WHEN** the project is rendered
- **THEN** every generated YAML or JSON file that includes the description is still valid and holds the exact text

### Requirement: AI agent entry file
Rendering SHALL generate the entry file of the selected AI agent. For `claude` it SHALL generate `CLAUDE.md`, which imports the root `AGENTS.md` and defines no rules of its own.

#### Scenario: Claude entry file
- **GIVEN** a valid spec with the AI agent `claude`
- **WHEN** the project is rendered
- **THEN** the tree contains `CLAUDE.md` that imports `AGENTS.md`, and the rules of the project remain only in the harness

### Requirement: Repository owner
Rendering SHALL receive the repository owner as an input separate from the project spec, validate it as a GitHub account name and use it as the code owner in the generated ownership file. Rendering MUST fail when no valid owner is provided.

#### Scenario: Owner is written to the ownership file
- **GIVEN** a valid spec and the owner `acme-platform`
- **WHEN** the project is rendered
- **THEN** the ownership file lists `@acme-platform` for the harness and OpenSpec paths

#### Scenario: Missing owner is rejected
- **GIVEN** a valid spec and no owner
- **WHEN** the project is rendered
- **THEN** rendering fails before writing any file

#### Scenario: Invalid owner is rejected
- **GIVEN** a valid spec and the owner `acme platform; rm -rf`
- **WHEN** the project is rendered
- **THEN** rendering fails before writing any file

### Requirement: Output confinement
Rendering SHALL write only inside the target directory it is given. It MUST refuse a target that is not empty and MUST NOT follow symbolic links or write to any path that resolves outside the target.

#### Scenario: Non-empty target is refused
- **GIVEN** a target directory that already contains a file
- **WHEN** the project is rendered into it
- **THEN** rendering fails and the existing content is unchanged

#### Scenario: Template that escapes the target is refused
- **GIVEN** a template whose output path resolves outside the target
- **WHEN** the project is rendered
- **THEN** rendering fails and nothing is written outside the target

### Requirement: No external effects
Rendering SHALL NOT access the network, execute external processes, use git or call any AI model.

#### Scenario: Render without network or processes
- **GIVEN** an environment where network access and process execution are blocked
- **WHEN** a valid spec is rendered
- **THEN** rendering succeeds

### Requirement: All or nothing
When rendering fails for any reason, the target directory SHALL be left exactly as it was before, with no partial tree.

#### Scenario: Failure leaves no partial tree
- **GIVEN** a template that fails after other files have already been produced
- **WHEN** the project is rendered
- **THEN** rendering fails and the target directory is empty, as before

### Requirement: Rendering requires a valid spec
Rendering MUST accept only a spec that passed validation and SHALL NOT render an invalid or unvalidated one.

#### Scenario: Invalid spec is not rendered
- **GIVEN** a spec with an invalid repository name
- **WHEN** rendering is requested
- **THEN** rendering fails with the validation errors and writes nothing
