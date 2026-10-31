# application-skeletons Specification

## Purpose
Defines the initial code of each application of a generated project, so that a new repository starts from a layered, tested and accessible baseline that already passes the quality gates of its stack.

## Requirements

### Requirement: Python backend skeleton
The Python backend skeleton SHALL provide the hexagonal layers `domain`, `application` and `infrastructure` under one package, a project manifest with a committed lockfile, one unit test and one integration test. Its configuration MUST enforce lint, strict typing, the layer dependency rule, a rule that `domain` and `application` import no framework or I/O library, and a coverage threshold of at least 80%.

#### Scenario: Files of the backend skeleton
- **GIVEN** a valid spec whose backend technology is `python`
- **WHEN** the project is rendered
- **THEN** `apps/backend/` contains the manifest, the lockfile, the three layers under the package, a unit test directory and an integration test directory

#### Scenario: Layer rule is enforced
- **GIVEN** the rendered Python backend where the `domain` layer imports from `infrastructure`
- **WHEN** the layer check runs
- **THEN** it fails and names the forbidden import

#### Scenario: Framework in the core is refused
- **GIVEN** the rendered Python backend where `domain` imports a web or database framework
- **WHEN** the layer check runs
- **THEN** it fails and names the forbidden import

### Requirement: React frontend skeleton
The React frontend skeleton SHALL provide one responsive page built with semantic HTML, a skip link and a main landmark, the hexagonal layer layout with the dependency rule enforced by lint, a manifest with a committed lockfile, the Node 20 minimum, and unit, integration and end-to-end tests. The end-to-end tests MUST run at mobile, tablet and desktop widths and MUST fail on any WCAG 2.2 AA violation found by an automated accessibility check.

#### Scenario: Files of the frontend skeleton
- **GIVEN** a valid spec whose frontend technology is `react-typescript`
- **WHEN** the project is rendered
- **THEN** `apps/frontend/` contains the manifest, the lockfile, the page, and unit, integration and end-to-end tests

#### Scenario: Accessible at every width
- **GIVEN** the rendered frontend served from its build
- **WHEN** the end-to-end tests open the page at 360, 768 and 1280 pixels wide
- **THEN** the page has no horizontal scrolling and the accessibility check reports no violation

#### Scenario: Layer rule is enforced
- **GIVEN** the rendered frontend where `domain` imports from `interfaces`
- **WHEN** lint runs
- **THEN** it fails and names the forbidden import

### Requirement: Skeletons pass their quality gates
Each generated skeleton MUST pass, without edits and without network access beyond installing the locked dependencies, every gate of its stack sheet: formatting, lint, types, unit tests with the 80% coverage gate, integration tests and, for the frontend, end-to-end tests. Its locked dependencies MUST have no known high or critical vulnerability when the skeleton is released.

#### Scenario: Backend gates pass
- **GIVEN** a freshly rendered Python backend
- **WHEN** its locked dependencies are installed and the format, lint, type, layer, unit with coverage and integration checks run
- **THEN** all of them pass

#### Scenario: C# backend gates pass
- **GIVEN** a freshly rendered C# backend
- **WHEN** its locked dependencies are restored and the format, build with warnings as errors, unit with coverage, integration and architecture checks run
- **THEN** all of them pass

#### Scenario: Frontend gates pass
- **GIVEN** a freshly rendered React frontend
- **WHEN** its locked dependencies are installed and the format, lint, type, unit with coverage, integration and end-to-end checks run
- **THEN** all of them pass

#### Scenario: Locked dependencies are clean
- **GIVEN** the lockfiles of the rendered skeletons
- **WHEN** a dependency audit runs
- **THEN** it reports no high or critical vulnerability

### Requirement: Lockfiles match their manifests
Each skeleton SHALL ship a lockfile that is consistent with its manifest, so that installing with the frozen lockfile succeeds and the lockfile does not change.

#### Scenario: Frozen install succeeds
- **GIVEN** a freshly rendered skeleton
- **WHEN** its dependencies are installed from the frozen lockfile
- **THEN** the installation succeeds and the lockfile is unchanged

#### Scenario: Lockfile is up to date
- **GIVEN** a freshly rendered Python backend
- **WHEN** the lockfile is checked against the manifest
- **THEN** the check reports that the lockfile is up to date

#### Scenario: C# restore in locked mode succeeds
- **GIVEN** a freshly rendered C# backend
- **WHEN** its packages are restored in locked mode
- **THEN** the restore succeeds and no lock file changes

### Requirement: Fixed names and no project values in code
Skeleton files SHALL be copied unchanged. They MUST use fixed names (distribution `backend` and `frontend`, Python package `app`, C# solution and root namespace `App`) and MUST NOT contain the project name, the repository name, the description or the owner, so the same skeleton is generated for every project.

#### Scenario: Same skeleton for different projects
- **GIVEN** two valid specs with different project names, repository names and descriptions but the same technologies
- **WHEN** both projects are rendered
- **THEN** every file of `apps/backend/` and `apps/frontend/` other than the per-kind README is byte-identical in both trees

#### Scenario: Project values stay out of the code
- **GIVEN** a spec whose description contains `{{ 7 * 7 }}` and quotes
- **WHEN** the project is rendered
- **THEN** no skeleton file contains the project name, the repository name or the description

### Requirement: C# backend skeleton
The C# backend skeleton SHALL provide the hexagonal layers `Domain`, `Application` and `Infrastructure` as separate projects of one solution, one unit test project, one integration test project and one architecture test project, and a committed lock file for every project.

#### Scenario: Files of the C# backend skeleton
- **GIVEN** a valid spec whose backend technology is `csharp`
- **WHEN** the project is rendered
- **THEN** `apps/backend/` contains the solution, the shared build configuration, the three layer projects, the unit, integration and architecture test projects, and the lock file of every project

### Requirement: C# backend build and layer rules
The C# backend skeleton MUST enable nullable reference types, treat warnings as errors, enforce the layer dependency rule, forbid `Domain` and `Application` from using any web, database, message broker or HTTP library, and enforce a line-coverage threshold of at least 80% on the unit tests.

#### Scenario: Layer rule is enforced
- **GIVEN** the rendered C# backend where the `Domain` layer depends on `Infrastructure`
- **WHEN** the solution is built and the architecture tests run
- **THEN** the build or the architecture tests fail and name the forbidden dependency

#### Scenario: Framework in the core is refused
- **GIVEN** the rendered C# backend where `Domain` uses an HTTP, web or database library
- **WHEN** the architecture tests run
- **THEN** they fail and name the forbidden dependency

#### Scenario: Warnings fail the build
- **GIVEN** the rendered C# backend where a source file produces a compiler or analyzer warning
- **WHEN** the solution is built
- **THEN** the build fails

#### Scenario: Coverage below the threshold fails
- **GIVEN** the rendered C# backend where the unit tests cover less than 80% of the lines
- **WHEN** the unit tests run with coverage
- **THEN** the run fails and reports the coverage threshold

### Requirement: Technology without application files
A technology that has no application files in the available templates SHALL still be accepted by the project spec, and its application directory SHALL contain only the per-kind README.

#### Scenario: Technology without application files
- **GIVEN** a valid spec whose backend technology has no skeleton in the available templates
- **WHEN** the project is rendered
- **THEN** rendering succeeds and `apps/backend/` contains only `README.md`

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
