# project-rendering Specification

## Purpose

Defines how a valid project spec is turned into the complete initial file tree of a monorepo, deterministically and without side effects outside a target directory, so that the result can be regenerated at any time.

## Requirements

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

### Requirement: Repository checks workflow
Rendering SHALL include `.github/workflows/repository.yml` in every generated project, whatever its typology. The workflow MUST run on pull requests to `main`, on pushes to `main` and on a weekly schedule, and MUST contain a secret scan, an OpenSpec validation and a check that every commit type matches the branch prefix.

#### Scenario: Workflow is present for every typology
- **GIVEN** a valid `backend` spec, a valid `frontend` spec and a valid `fullstack` spec
- **WHEN** each project is rendered
- **THEN** each tree contains `.github/workflows/repository.yml`

#### Scenario: Workflow triggers
- **GIVEN** a rendered project
- **WHEN** the workflow is parsed
- **THEN** it is valid YAML and runs on pull requests to `main`, pushes to `main` and a weekly schedule

#### Scenario: Workflow does not depend on the project values
- **GIVEN** two valid specs with different names, descriptions and typologies
- **WHEN** both projects are rendered
- **THEN** their `.github/workflows/repository.yml` files are byte-identical

### Requirement: Required checks are produced by rendered workflows
Every status check required by the branches ruleset template SHALL be the name of a job in a workflow that rendering generates in every project, so that a repository using the ruleset can satisfy it without the administrator bypass.

#### Scenario: Ruleset checks match workflow jobs
- **GIVEN** the status checks required by the branches ruleset template and a rendered project
- **WHEN** the job names of the rendered workflows are compared with the required checks
- **THEN** every required check is the name of a job in a rendered workflow

#### Scenario: Ruleset is not rendered
- **GIVEN** a rendered project
- **WHEN** its tree is listed
- **THEN** it contains no file taken from `templates/github/rulesets/`

### Requirement: Workflow supply chain and permissions
The generated workflow MUST grant only read access to repository contents by default, and SHALL reference every third-party action and downloaded tool by an explicit version. Downloaded executables MUST be verified against a pinned checksum before they run.

#### Scenario: Read-only default permissions
- **GIVEN** a rendered `.github/workflows/repository.yml`
- **WHEN** its permissions are inspected
- **THEN** the workflow-level permissions grant only `contents: read` and no job requests write access

#### Scenario: Actions and tools are versioned
- **GIVEN** a rendered `.github/workflows/repository.yml`
- **WHEN** every `uses:` reference and every downloaded tool is inspected
- **THEN** each one names an explicit version and none follows a branch or `latest`

#### Scenario: Downloaded executable is verified
- **GIVEN** a rendered `.github/workflows/repository.yml` that downloads an executable
- **WHEN** its steps are inspected
- **THEN** the executable's checksum is compared with a pinned value before it is run

### Requirement: Workflow secrets
The generated workflow SHALL NOT need any repository or organization secret other than the default `GITHUB_TOKEN`, so that it runs unchanged for personal and organization owners.

#### Scenario: No custom secret is referenced
- **GIVEN** a rendered `.github/workflows/repository.yml`
- **WHEN** its secret references are listed
- **THEN** the only secret referenced, if any, is `GITHUB_TOKEN`
