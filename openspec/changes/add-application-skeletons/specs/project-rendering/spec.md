# Spec Delta

## ADDED Requirements

### Requirement: Technology-specific application files
Rendering SHALL write into `apps/<kind>/` the template files that belong to the technology selected for that kind, together with the files shared by every technology of the kind. It MUST NOT write files that belong to another technology.

#### Scenario: Selected technology only
- **GIVEN** a valid spec whose backend technology is `python`
- **WHEN** the project is rendered
- **THEN** `apps/backend/` contains the Python backend files and none of the files of another backend technology

#### Scenario: Shared files apply to every technology
- **GIVEN** two valid specs that differ only in the backend technology
- **WHEN** both projects are rendered
- **THEN** both trees contain the per-kind `apps/backend/README.md`

#### Scenario: Kinds are selected independently
- **GIVEN** a valid `fullstack` spec
- **WHEN** the project is rendered
- **THEN** `apps/backend/` holds the files of the backend technology, `apps/frontend/` holds the files of the frontend technology, and neither holds files of the other

#### Scenario: Technology without application files
- **GIVEN** a valid spec whose backend technology has no application files yet
- **WHEN** the project is rendered
- **THEN** rendering succeeds and `apps/backend/` contains only the files shared by every technology of the kind
