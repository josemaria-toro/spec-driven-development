# Spec Delta

## ADDED Requirements

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

## MODIFIED Requirements

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
