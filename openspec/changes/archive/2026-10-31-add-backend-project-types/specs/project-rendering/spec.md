# Spec Delta

## ADDED Requirements

### Requirement: Project-type-specific application files
Rendering SHALL write into `apps/backend/` only the template files that belong to the project type selected for the backend, together with the files shared by every project type of its technology. It MUST NOT write files that belong to another project type, and it MUST NOT change the files rendered for a technology that offers no project types.

#### Scenario: Selected project type only
- **GIVEN** a valid spec whose backend is C# with the project type `console`
- **WHEN** the project is rendered
- **THEN** `apps/backend/` contains the console files and none of the files of the `api` or `library` types

#### Scenario: Default project type
- **GIVEN** a valid spec whose backend technology offers project types and has no project type
- **WHEN** the project is rendered
- **THEN** `apps/backend/` contains the files of the `api` type

#### Scenario: Technology without project types is unaffected
- **GIVEN** a valid spec whose backend technology offers no project types
- **WHEN** the project is rendered
- **THEN** `apps/backend/` contains exactly the files of that technology, whatever directory names they use

#### Scenario: Project type is available to the application README
- **GIVEN** a valid spec whose backend is C# with the project type `library`
- **WHEN** the project is rendered
- **THEN** `apps/backend/README.md` states the project type `library`
