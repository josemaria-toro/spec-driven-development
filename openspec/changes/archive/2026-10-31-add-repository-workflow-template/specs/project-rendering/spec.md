# Spec Delta

## ADDED Requirements

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
