# Spec Delta

## ADDED Requirements

### Requirement: C# library skeleton
The C# library skeleton SHALL provide the layered core of the C# backend skeleton, with no host or entry point, configured so that it can be packed into a package. Every public member MUST be documented, and a public member without documentation SHALL fail the build.

#### Scenario: Files of the library skeleton
- **GIVEN** a valid spec whose backend is C# with the project type `library`
- **WHEN** the project is rendered
- **THEN** `apps/backend/` contains the solution, the layer projects, the unit, integration and architecture test projects and their lock files, and no entry project

#### Scenario: Library can be packed
- **GIVEN** a freshly rendered C# library
- **WHEN** it is packed
- **THEN** packing succeeds and produces a package

#### Scenario: Undocumented public member fails the build
- **GIVEN** the rendered C# library where a public type has no documentation comment
- **WHEN** the solution is built
- **THEN** the build fails and names the undocumented member

### Requirement: C# console skeleton
The C# console skeleton SHALL provide the layered core and an entry project that runs the use case from the command line: it writes the result to standard output and exits with code 0, and on invalid arguments it writes a usage message to standard error and exits with a non-zero code, without a stack trace.

#### Scenario: Files of the console skeleton
- **GIVEN** a valid spec whose backend is C# with the project type `console`
- **WHEN** the project is rendered
- **THEN** `apps/backend/` contains the files of the layered core and the entry project, and none of the files of another project type

#### Scenario: Valid arguments
- **GIVEN** the rendered C# console application
- **WHEN** it runs with one name as argument
- **THEN** it writes the greeting for that name to standard output and exits with code 0

#### Scenario: Invalid arguments
- **GIVEN** the rendered C# console application
- **WHEN** it runs with more arguments than it accepts
- **THEN** it writes a usage message to standard error, writes nothing to standard output and exits with a non-zero code

### Requirement: ASP.NET Core skeleton
The ASP.NET Core skeleton SHALL provide the layered core and an entry project that exposes one HTTP endpoint over the use case. It MUST validate the input of the endpoint, answer invalid input with a client error and no internal detail, never return exception details or stack traces to the caller outside development, and send security headers and HTTPS redirection as secure defaults. It MUST NOT include authentication, a database or a message broker.

#### Scenario: Files of the ASP.NET Core skeleton
- **GIVEN** a valid spec whose backend is C# with the project type `api`
- **WHEN** the project is rendered
- **THEN** `apps/backend/` contains the files of the layered core and the entry project, and none of the files of another project type

#### Scenario: Valid request
- **GIVEN** the rendered ASP.NET Core application running in memory
- **WHEN** a request asks for the greeting of a valid name
- **THEN** the response is successful and contains the greeting

#### Scenario: Invalid input is rejected
- **GIVEN** the rendered ASP.NET Core application running in memory
- **WHEN** a request asks for the greeting of a name longer than the maximum length
- **THEN** the response is a client error that names the invalid field and contains no internal detail

#### Scenario: Unhandled errors reveal nothing
- **GIVEN** the rendered ASP.NET Core application running in memory outside development where the use case fails
- **WHEN** a request reaches the failing use case
- **THEN** the response is a server error with a generic message and no exception type, message or stack trace

### Requirement: Every C# project type passes its quality gates
Each C# project type MUST pass, without edits and without network access beyond restoring the locked packages, the gates of the C# skeleton: format, build with warnings as errors, unit tests with the 80% coverage gate, integration tests and architecture tests. Its locked packages MUST have no known high or critical vulnerability when the skeleton is released.

#### Scenario: Gates pass for each project type
- **GIVEN** a freshly rendered C# backend of each project type
- **WHEN** its locked packages are restored and the format, build, unit with coverage, integration and architecture checks run
- **THEN** all of them pass for every project type

#### Scenario: Layer rule holds in the entry project
- **GIVEN** the rendered C# backend of the `api` or `console` type where `Domain` depends on the entry project
- **WHEN** the solution is built
- **THEN** the build fails and names the forbidden dependency
