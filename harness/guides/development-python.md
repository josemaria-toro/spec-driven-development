# Development guide: Python

Complements `development.md`. Tooling and commands live in `stacks/backend-python.md`. Style is enforced by Ruff and mypy; this guide explains the rules they cannot fully express.

## Best practices

- Follow PEP 8 and PEP 20; formatting is Ruff's job, never debated in review.
- Type hints on every public function, method and attribute; `mypy --strict` passes.
- Prefer immutability: `@dataclass(frozen=True)`, `tuple`, `frozenset`; Pydantic models only at the boundaries (see `architecture.md`).
- Prefer composition and small functions; avoid inheritance beyond abstract ports (`typing.Protocol` or `abc.ABC`).
- Use `pathlib`, `enum`, f-strings and context managers (`with`) for resources.
- No mutable default arguments; no bare `except:`; catch specific exceptions and chain with `raise ... from err`.
- Use `async` consistently inside a service; never block the event loop with sync I/O.
- No `print`, no `assert` for runtime validation; use the logger and explicit errors.
- No global mutable state; dependencies are injected through constructors.
- Public API of a module is declared (`__all__` only in package `__init__.py` that re-exports).

## Naming

| Element | Convention | Example |
|---|---|---|
| Package / module | `lower_snake_case`, short | `order_service` |
| Class, exception, Protocol | `PascalCase`; exceptions end in `Error` | `OrderNotFoundError` |
| Function, method, variable | `lower_snake_case`, verb for functions | `calculate_total` |
| Constant | `UPPER_SNAKE_CASE` | `MAX_RETRIES` |
| Type variable | `PascalCase`, short | `T`, `EntityT` |
| Private | single leading underscore | `_cache` |
| Boolean | reads as a question | `is_active`, `has_items` |
| Test | `test_<behavior>_<condition>` | `test_total_is_zero_when_empty` |

- Ports end with the role (`OrderRepository`, `Clock`); adapters include the technology (`PostgresOrderRepository`).
- Avoid abbreviations and single letters except in short comprehensions and loop indices.
- Names must not shadow built-ins (`id`, `type`, `list`, `input`).

## Member ordering

Inside a module, top to bottom:

1. Module docstring.
2. `from __future__` imports, then other imports (see below).
3. `__all__` (if any).
4. Constants.
5. Type aliases, TypeVars, Protocols.
6. Public classes and functions, then private helpers (or helpers right after their single user, consistently per module).

Inside a class:

1. Class docstring.
2. Class-level constants (`UPPER_SNAKE_CASE`).
3. **Constructors**: `__init__` first, then `__new__`/`__post_init__` and alternative constructors (`@classmethod`), alphabetical.
4. **Properties**, alphabetical, **public first, then the rest** (`_protected`, `__private`). Includes `@property` members and class/instance attributes declared in the body (e.g. dataclass fields).
5. **Methods**, alphabetical, **public first, then the rest** (`_protected`, `__private`). Dunder behavior methods (`__eq__`, `__iter__`, `__repr__`, …) count as public methods.

"Alphabetical" means case-insensitive ascending order of the member name, ignoring leading underscores. Where order carries meaning (dataclass/Pydantic field order with defaults, enum values) the language rule wins and the member is exempt.

One public class per module is the default; closely related small classes may share a module.

## Imports

Ordered by Ruff (`isort` rules, `I` enabled); never hand-sort. Groups separated by one blank line:

1. Standard library
2. Third-party
3. First-party (the project's own package)
4. Local relative imports (only within the same package)

Rules:

- Absolute imports are the default; relative imports only inside one package and never across layers.
- One import per line for `from x import …` lists is fine; sort names alphabetically.
- No wildcard imports (`from x import *`).
- No unused imports; no imports inside functions except to break a justified cycle or defer heavy optional dependencies.
- Imports must respect the layer dependency rule; import-linter fails the build otherwise.
- `if TYPE_CHECKING:` for imports used only in annotations.

## Dependencies

- Declared in `pyproject.toml`; versions locked in `uv.lock` (committed). Never `pip install` ad hoc.
- Runtime dependencies are separate from dev/test groups.
- Add a dependency only after the checks in `tech-stack.md` (license, maintenance, security, exit cost).
- Import third-party libraries only in `infrastructure/`/`adapters`/`interfaces` layers when they involve I/O or frameworks; the domain depends on the standard library only.
- Remove unused dependencies; `pip-audit` runs in CI.

## Code cleanliness

- Functions ≤ ~30 lines and ≤ 4 parameters (group extras in a dataclass); cyclomatic complexity ≤ 10 (Ruff `C901`).
- Early returns instead of deep nesting; no `else` after `return`/`raise`.
- No dead code, commented-out code, or stale TODOs (TODOs reference an issue: `TODO(#123)`).
- Docstrings on public modules, classes and functions: what and why, Google style; no docstrings that repeat the signature.
- No magic values; extract named constants or enums.
- Run `ruff format`, `ruff check --fix`, `mypy` and `lint-imports` before every commit (pre-commit does it).
