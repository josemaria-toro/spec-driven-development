# Spec Delta

## Purpose

Defines the validated description of a development project to be created (names, description, typology, technologies and AI agent), so that every later step works from input that is safe, complete and unambiguous.

## ADDED Requirements

### Requirement: Project spec fields
A project spec SHALL contain a project name, a repository name, a description, a project typology, the technologies of each application and an AI agent. All of them are required except the description, which MAY be empty.

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
A valid spec SHALL have one canonical serialization and a content hash derived from it. Two specs with the same values MUST produce the same hash regardless of field order, and any change to a value MUST change the hash.

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
