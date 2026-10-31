# project-spec Specification

## Purpose

Defines the validated description of a development project to be created (names, description, typology, technologies and AI agent), so that every later step works from input that is safe, complete and unambiguous.

## Requirements

### Requirement: Project spec fields
A project spec SHALL contain a project name, a repository name, a description, a project typology, the technologies of each application, an AI agent and, optionally, a project type for the backend. All of them are required except the description, which MAY be empty, and the project type, which defaults to `api` where the backend technology offers project types.

#### Scenario: Complete spec is accepted
- **GIVEN** a spec with a project name, a repository name, a description, a supported typology, supported technologies and a supported AI agent
- **WHEN** the spec is validated
- **THEN** validation succeeds and the spec is available for later steps

#### Scenario: Missing required field is rejected
- **GIVEN** a spec with no repository name
- **WHEN** the spec is validated
- **THEN** validation fails and reports that the repository name is required

### Requirement: Repository name format
The repository name MUST be 1 to 100 characters, use only lowercase letters, digits and hyphens, and neither start nor end with a hyphen. It SHALL NOT contain path separators, dots, spaces or any other character.

#### Scenario: Valid repository name
- **GIVEN** the repository name `orders-platform`
- **WHEN** the spec is validated
- **THEN** the repository name is accepted

#### Scenario: Path traversal attempt is rejected
- **GIVEN** the repository name `../outside`
- **WHEN** the spec is validated
- **THEN** validation fails and no other step receives the value

#### Scenario: Unsupported characters are rejected
- **GIVEN** the repository name `Orders Platform!`
- **WHEN** the spec is validated
- **THEN** validation fails and reports the characters that are not allowed

#### Scenario: Name that is too long is rejected
- **GIVEN** a repository name of 101 characters
- **WHEN** the spec is validated
- **THEN** validation fails and reports the maximum length

### Requirement: Project name and description limits
The project name MUST be 1 to 100 characters and the description at most 350 characters. Neither SHALL contain control characters or line breaks, and surrounding whitespace SHALL be removed before validation.

#### Scenario: Surrounding whitespace is trimmed
- **GIVEN** the project name `  Orders Platform  `
- **WHEN** the spec is validated
- **THEN** the validated project name is `Orders Platform`

#### Scenario: Control characters are rejected
- **GIVEN** a description containing a line break or a control character
- **WHEN** the spec is validated
- **THEN** validation fails and reports the field and the reason

#### Scenario: Description that is too long is rejected
- **GIVEN** a description of 351 characters
- **WHEN** the spec is validated
- **THEN** validation fails and reports the maximum length

### Requirement: Supported typologies
The project typology MUST belong to the supported catalogue, which initially contains `backend`, `frontend` and `fullstack`. The typology SHALL determine which applications the project contains: `backend` has one backend application, `frontend` one frontend application and `fullstack` one of each.

#### Scenario: Typology determines the applications
- **GIVEN** a spec with the typology `fullstack`
- **WHEN** the applications of the project are resolved
- **THEN** the result contains one backend application and one frontend application

#### Scenario: Unsupported typology is rejected
- **GIVEN** a spec with the typology `mobile`
- **WHEN** the spec is validated
- **THEN** validation fails and lists the supported typologies

### Requirement: Supported technologies per application
Each application MUST use a technology supported by the harness for its kind: Python or C# for a backend application and React with TypeScript for a frontend application. A technology that does not match the kind of the application SHALL be rejected.

#### Scenario: Supported technologies are accepted
- **GIVEN** a `fullstack` spec with Python for the backend and React for the frontend
- **WHEN** the spec is validated
- **THEN** validation succeeds

#### Scenario: Technology of the wrong kind is rejected
- **GIVEN** a `backend` spec that selects React for the backend application
- **WHEN** the spec is validated
- **THEN** validation fails and reports the technologies supported for a backend

#### Scenario: Technology missing for an application is rejected
- **GIVEN** a `fullstack` spec that selects a technology only for the backend
- **WHEN** the spec is validated
- **THEN** validation fails and reports the application without a technology

### Requirement: Supported AI agents
The AI agent MUST belong to the supported catalogue, which initially contains `claude`. An agent outside the catalogue SHALL be rejected.

#### Scenario: Supported agent is accepted
- **GIVEN** a spec with the AI agent `claude`
- **WHEN** the spec is validated
- **THEN** the agent is accepted

#### Scenario: Unsupported agent is rejected
- **GIVEN** a spec with an AI agent that is not in the catalogue
- **WHEN** the spec is validated
- **THEN** validation fails and lists the supported agents

### Requirement: Validation reports every error
Validation SHALL report all invalid fields at once, each with the field name and a readable reason, and SHALL NOT include internal paths or stack traces in the messages.

#### Scenario: Several errors are reported together
- **GIVEN** a spec with an invalid repository name and an unsupported typology
- **WHEN** the spec is validated
- **THEN** the result contains one error for each of the two fields

### Requirement: Canonical form and hash
A valid spec SHALL have one canonical serialization and a content hash derived from it. Two specs with the same values MUST produce the same hash regardless of field order, and any change to a value, including the project type, MUST change the hash. A spec without a project type whose backend technology offers project types and one that selects `api` SHALL have the same hash.

#### Scenario: Same values give the same hash
- **GIVEN** two specs with identical values supplied with their fields in a different order
- **WHEN** their hashes are computed
- **THEN** the hashes are equal

#### Scenario: A changed value changes the hash
- **GIVEN** a valid spec and a copy that differs only in the description
- **WHEN** their hashes are computed
- **THEN** the hashes are different

#### Scenario: Whitespace normalization does not change identity
- **GIVEN** two specs that differ only in whitespace around the project name
- **WHEN** their hashes are computed
- **THEN** the hashes are equal

#### Scenario: A different project type changes the hash
- **GIVEN** two specs with the same backend technology that differ only in the project type
- **WHEN** their hashes are computed
- **THEN** the hashes are different

#### Scenario: The default project type is the same as an explicit one
- **GIVEN** a spec with C# for the backend and no project type, and a copy that selects `api`
- **WHEN** their hashes are computed
- **THEN** the hashes are equal

### Requirement: Supported project types
A project spec MAY select a project type for its backend application from the supported catalogue, which initially contains `api`, `console` and `library`. Each backend technology SHALL declare the project types it offers (C# offers all three; Python offers none until it provides them). When omitted for a technology that offers project types, the project type SHALL be `api`. A project type MUST be rejected when the backend technology offers none and when the typology has no backend application.

#### Scenario: Supported project type is accepted
- **GIVEN** a `backend` spec with C# for the backend and the project type `console`
- **WHEN** the spec is validated
- **THEN** validation succeeds and the project type is `console`

#### Scenario: Omitted project type defaults to API
- **GIVEN** a `backend` spec with C# for the backend and no project type
- **WHEN** the spec is validated
- **THEN** validation succeeds and the project type is `api`

#### Scenario: Unsupported project type is rejected
- **GIVEN** a spec with C# for the backend and the project type `worker`
- **WHEN** the spec is validated
- **THEN** validation fails and lists the supported project types

#### Scenario: Technology without project types rejects one
- **GIVEN** a spec with a backend technology that offers no project types and the project type `library`
- **WHEN** the spec is validated
- **THEN** validation fails and reports that the technology offers no project types

#### Scenario: Technology without project types needs none
- **GIVEN** a spec with a backend technology that offers no project types and no project type
- **WHEN** the spec is validated
- **THEN** validation succeeds and the spec has no project type

#### Scenario: Project type without a backend is rejected
- **GIVEN** a `frontend` spec with the project type `console`
- **WHEN** the spec is validated
- **THEN** validation fails and reports that the project type applies only to a backend application

### Requirement: Python project types
The Python backend technology SHALL offer every project type of the catalogue: `api`, `console` and `library`. A Python backend spec without a project type SHALL have the project type `api`.

#### Scenario: Each project type is accepted for Python
- **GIVEN** a `backend` spec with Python for the backend and the project type `library`, `console` or `api`
- **WHEN** the spec is validated
- **THEN** validation succeeds and the project type is the selected one

#### Scenario: Omitted project type defaults to API for Python
- **GIVEN** a `backend` spec with Python for the backend and no project type
- **WHEN** the spec is validated
- **THEN** validation succeeds and the project type is `api`

#### Scenario: Project type of Python changes the hash
- **GIVEN** two specs with Python for the backend that differ only in the project type
- **WHEN** their hashes are computed
- **THEN** the hashes are different
