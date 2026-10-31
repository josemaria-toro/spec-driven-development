# Spec Delta

## ADDED Requirements

### Requirement: Python library skeleton
The Python library skeleton SHALL provide the layered core of the Python backend skeleton, with no entry point or host, as a typed distribution that can be built into installable files. Every public module, class and function MUST have a documentation string, and a public one without it SHALL fail lint.

#### Scenario: Files of the library skeleton
- **GIVEN** a valid spec whose backend is Python with the project type `library`
- **WHEN** the project is rendered
- **THEN** `apps/backend/` contains the manifest, the lockfile, the three layers under the package, the typing marker, a unit test directory and an integration test directory, and no `interfaces` layer

#### Scenario: Library can be built
- **GIVEN** a freshly rendered Python library
- **WHEN** it is built
- **THEN** the build succeeds and produces the distribution files

#### Scenario: Undocumented public function fails lint
- **GIVEN** the rendered Python library where a public function has no documentation string
- **WHEN** lint runs
- **THEN** it fails and names the function

### Requirement: Python console skeleton
The Python console skeleton SHALL provide the layered core, an `interfaces` layer with a command line entry point that runs the use case, and an installed command. It writes the result to standard output and exits with code 0; on invalid arguments it writes a usage message to standard error, writes nothing to standard output and exits with a non-zero code, without a stack trace.

#### Scenario: Files of the console skeleton
- **GIVEN** a valid spec whose backend is Python with the project type `console`
- **WHEN** the project is rendered
- **THEN** `apps/backend/` contains the files of the layered core, the `interfaces` layer and the command entry point, and none of the files of another project type

#### Scenario: Valid arguments
- **GIVEN** the rendered Python console application
- **WHEN** it runs with one name as argument
- **THEN** it writes the greeting for that name to standard output and exits with code 0

#### Scenario: Invalid arguments
- **GIVEN** the rendered Python console application
- **WHEN** it runs with more arguments than it accepts
- **THEN** it writes a usage message to standard error, writes nothing to standard output and exits with a non-zero code

### Requirement: Python API skeleton
The Python API skeleton SHALL provide the layered core and an `interfaces` layer with an HTTP application exposing one endpoint over the use case, started by an ASGI server. It MUST NOT include authentication, a database or a message broker.

#### Scenario: Files of the API skeleton
- **GIVEN** a valid spec whose backend is Python with the project type `api`
- **WHEN** the project is rendered
- **THEN** `apps/backend/` contains the files of the layered core, the `interfaces` layer and the application entry module, and none of the files of another project type

#### Scenario: Valid request
- **GIVEN** the rendered Python API running in memory
- **WHEN** a request asks for the greeting of a valid name
- **THEN** the response is successful, contains the greeting and carries the security headers

### Requirement: Python API secure defaults
The Python API skeleton MUST validate the endpoint input and answer invalid input with a client error that names the field and no internal detail. It MUST never return exception details or stack traces to the caller, MUST send security headers, and MUST keep interactive API documentation disabled by default.

#### Scenario: Invalid input is rejected
- **GIVEN** the rendered Python API running in memory
- **WHEN** a request asks for the greeting of a name longer than the maximum length
- **THEN** the response is a client error that names the invalid field and contains no internal detail

#### Scenario: Unhandled errors reveal nothing
- **GIVEN** the rendered Python API running in memory where the use case fails
- **WHEN** a request reaches the failing use case
- **THEN** the response is a server error with a generic message and no exception type, message or stack trace

#### Scenario: Documentation is off by default
- **GIVEN** the rendered Python API running in memory with its default configuration
- **WHEN** a request asks for the interactive API documentation
- **THEN** the response is not found

### Requirement: Every Python project type passes its quality gates
Each Python project type MUST pass, without edits and without network access beyond installing the locked dependencies, the gates of the Python skeleton: format, lint, types, layer rules, unit tests with the 80% coverage gate and integration tests. Its locked dependencies MUST have no known high or critical vulnerability when the skeleton is released.

#### Scenario: Gates pass for each project type
- **GIVEN** a freshly rendered Python backend of each project type
- **WHEN** its locked dependencies are installed and the format, lint, type, layer, unit with coverage and integration checks run
- **THEN** all of them pass for every project type

#### Scenario: Layer rule holds in the interfaces layer
- **GIVEN** the rendered Python backend of the `api` or `console` type where `domain` imports from `interfaces`
- **WHEN** the layer check runs
- **THEN** it fails and names the forbidden import

#### Scenario: Framework in the core is refused in every type
- **GIVEN** the rendered Python backend of the `api` type where `application` imports the web framework
- **WHEN** the layer check runs
- **THEN** it fails and names the forbidden import
