# Spec Delta

## ADDED Requirements

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
