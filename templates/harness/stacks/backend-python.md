# Stack: Backend — Python

## Summary

- **Purpose**: backend services and APIs in Python.
- **Architecture**: <hexagonal | clean architecture> (see `guides/architecture.md`; declare one per project).

## Runtime and tooling

| Element | Choice | Minimum version |
|---|---|---|
| Language | Python | latest version with active support (≥ 3.12) |
| Package manager | uv (lockfile `uv.lock` committed) | — |
| Framework | FastAPI | — |
| ASGI server | Uvicorn | — |
| Database | PostgreSQL (default) via asyncpg | — |
| Message broker | RabbitMQ (default) via aio-pika | — |
| Validation / DTOs | Pydantic | v2 |
| Linter / formatter | Ruff | — |
| Typing | mypy (strict) or pyright | — |
| Testing | pytest (unit + integration), pytest-cov, pytest-asyncio | — |
| Layer checks | import-linter | — |

## Standard commands

```bash
uv sync                          # install
uv run ruff format .             # format
uv run ruff check .              # lint
uv run mypy src                  # types
uv run lint-imports              # layer dependency rule
uv run pytest tests/unit --cov         # unit tests + coverage
uv run pytest tests/integration        # integration tests (containers)
uv run uvicorn <package>.main:app --reload   # run locally
```

## Folder structure

```
src/<package>/
  domain/ application/ interfaces/ infrastructure/   # hexagonal
  # or: entities/ use_cases/ adapters/ frameworks/    # clean architecture
tests/
  unit/ integration/
pyproject.toml
uv.lock
```

### Project types

A Python backend is created with a project type (`project_type` in the project spec; `api` when omitted). The layers, the test layout and the quality gates are the same for every type; the type decides the inbound layer:

| Type | Inbound layer | Use |
|---|---|---|
| `api` | `interfaces/` with a FastAPI application (`app.main:app`) served by Uvicorn | HTTP service |
| `console` | `interfaces/` with a command line entry point (installed command `backend`, `python -m app`) | command line tool |
| `library` | none | reusable library: typed distribution (`py.typed`), every public member documented, built with `uv build` |

```
src/<package>/
  domain/ application/ infrastructure/
  interfaces/        # api and console only
  main.py            # api only: the ASGI application
  __main__.py        # console only: python -m <package>
tests/
  unit/ integration/
```

```bash
uv run uvicorn app.main:app --reload   # api
uv run backend <name>                  # console
uv build                               # library
```

## Quality

- Minimum coverage: 80%, gate before each commit and in CI: `uv run pytest tests/unit --cov=src --cov-fail-under=80` (set `fail_under = 80` in `[tool.coverage.report]`).
- Type hints on all public functions; `mypy --strict` with no unjustified `# type: ignore`.
- Domain/entities layer must not import FastAPI, Pydantic, SQLAlchemy or any I/O library (enforced by import-linter).
- Vulnerability gate (pre-commit and CI; high/critical vulnerabilities and any secret block): dependency audit with `pip-audit` against `uv.lock` (e.g. `uv export --frozen --no-hashes | pip-audit -r /dev/stdin`) and secret scan with gitleaks. `pip-audit` does not filter by severity itself: the hook resolves severity with OSV-Scanner (admitted in `guides/tech-stack.md`) and blocks only high/critical; confirm during hook implementation that the severity data is available in its output.

## Approved dependencies

| Library | Use | License |
|---|---|---|
| FastAPI | HTTP API | MIT |
| Pydantic | Boundary validation | MIT |
| Uvicorn | ASGI server | BSD-3-Clause |
| SQLAlchemy + Alembic | Persistence and migrations | MIT |
| asyncpg | PostgreSQL driver | Apache-2.0 |
| aio-pika | RabbitMQ client | Apache-2.0 |
| httpx | HTTP client | BSD-3-Clause |
| structlog | Structured logging | MIT / Apache-2.0 |
| pytest | Test framework (unit + integration) | MIT |
| pytest-cov | Coverage | MIT |
| pytest-asyncio | Async tests | Apache-2.0 |
| Testcontainers (Python) | PostgreSQL/RabbitMQ in integration tests | Apache-2.0 |
| Ruff, mypy, import-linter | Quality tooling | MIT / BSD |
| pip-audit | Dependency vulnerability audit (pre-commit + CI) | Apache-2.0 |
| OSV-Scanner | Vulnerability data with severity (to apply the high/critical threshold) | Apache-2.0 |
| Bandit | SAST (CI) | Apache-2.0 |
| gitleaks | Secret scanning (pre-commit + CI) | MIT |
| pre-commit | Hook runner | MIT |

## Specifics

- Use `async` consistently within a service; do not mix blocking I/O into async paths.
- Dependency injection through constructor arguments / FastAPI `Depends` only in `interfaces/`.
- Settings via `pydantic-settings`, validated at startup.
- Production: run Uvicorn (optionally under a process manager/orchestrator); no `--reload` outside local.
- `psycopg` is LGPL-3.0, so it needs an ADR (see `guides/tech-stack.md`); use `asyncpg` by default.
- pytest conventions: configure in `pyproject.toml` (`[tool.pytest.ini_options]`, `--strict-markers`); files `test_*.py`; shared setup in fixtures (`conftest.py`), not in base classes; use `@pytest.mark.parametrize` for case tables; mark slow/integration tests with registered markers (`integration`) so layers can run separately.
- Integration tests run PostgreSQL and RabbitMQ in containers (Testcontainers), never against shared environments.
