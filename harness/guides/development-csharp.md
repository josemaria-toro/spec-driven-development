# Development guide: C#

Complements `development.md`. Tooling and commands live in `stacks/backend-csharp.md`. Style is enforced by `.editorconfig`, Roslyn analyzers and `dotnet format`; warnings are errors.

## Best practices

- Nullable reference types enabled everywhere; no `!` (null-forgiving) without a justifying comment.
- Prefer immutability: `record`, `readonly struct`, `init` properties, `IReadOnlyList<T>`; expose collections as read-only interfaces.
- `async`/`await` end to end, no `.Result`/`.Wait()`; every I/O method accepts and forwards a `CancellationToken`; async methods end in `Async`.
- Dependency injection through constructors; no service locator, no static mutable state.
- Program to interfaces defined by the inner layer (ports); implementations are `internal` where possible.
- Default to the most restrictive access modifier (`internal`, `private`); `public` only for the layer's intended API.
- Use `using` / `await using` for `IDisposable`/`IAsyncDisposable`; `sealed` classes by default.
- Throw specific exceptions (domain errors as custom types); never catch `Exception` unless at a boundary that logs and rethrows/translates; use `throw;` not `throw ex;`.
- Use pattern matching, `switch` expressions, `is not null`, string interpolation, and `var` when the type is obvious from the right-hand side.
- LINQ for clarity, not cleverness; avoid multiple enumeration; no LINQ in hot paths without measuring.
- Structured logging with message templates (`logger.LogInformation("Order {OrderId} created", id)`), never string interpolation.

## Naming

| Element | Convention | Example |
|---|---|---|
| Namespace | `PascalCase`, matches folder/project | `Acme.Orders.Domain` |
| Class, record, struct, enum | `PascalCase`, noun | `OrderService` |
| Interface | `I` + `PascalCase` | `IOrderRepository` |
| Method, property, event | `PascalCase`; methods are verbs | `CalculateTotal` |
| Async method | suffix `Async` | `GetOrderAsync` |
| Parameter, local variable | `camelCase` | `orderId` |
| Private field | `_camelCase` | `_repository` |
| Constant, static readonly | `PascalCase` | `MaxRetries` |
| Generic parameter | `T` or `T` + `PascalCase` | `TEntity` |
| Boolean | reads as a question | `IsActive`, `HasItems` |
| Test | `Method_Condition_Expected` | `Total_WhenEmpty_ReturnsZero` |

- Adapters include the technology (`PostgresOrderRepository`); ports carry the role (`IOrderRepository`, `IClock`).
- One type per file, file named after the type.
- Avoid abbreviations except universally known ones (`Id`, `Url`, `Http`).

## Member ordering

Inside a type, top to bottom (enforced by analyzers configured to this order):

1. Constants and `static readonly` fields (type-level, not instance state).
2. **Constructors** (static constructor first, then instance constructors by parameter count; finalizer last).
3. **Properties**, alphabetical, **public first, then the rest** (`internal`, `protected`, `private`). Instance fields belong to this group and follow the same rule.
4. **Methods**, alphabetical, **public first, then the rest** (`internal`, `protected`, `private`).

"Alphabetical" means ordinal, case-insensitive ascending order of the member name. Overloads stay adjacent, ordered by parameter count. Where order carries meaning (enum members, positional record parameters, interface implementations required to match the interface) the language rule wins and the member is exempt. Nested types go at the end of the file's type. One type per file; file layout: `using` directives, file-scoped `namespace`, type.

## Usings

- Order enforced by `.editorconfig` (`dotnet_sort_system_directives_first = true`, `dotnet_separate_import_directive_groups = true`):
  1. `System.*`
  2. Third-party namespaces
  3. The project's own namespaces
  Each group separated by a blank line, alphabetical inside the group.
- `using` directives go **outside** the namespace; use file-scoped namespaces (`namespace X;`).
- No unused usings (IDE0005 as error); no `using static` except for well-known helpers (`System.Math`, test asserts).
- Use `<ImplicitUsings>` only if the whole solution agrees; otherwise disable it for explicitness.
- Aliases (`using Foo = Bar.Baz;`) only to resolve ambiguity.
- Usings must respect layer rules; architecture tests fail the build otherwise.

## Dependencies

- Packages are managed with NuGet central package management (`Directory.Packages.props`); versions pinned, lock files enabled (`RestorePackagesWithLockFile`).
- Project references follow the dependency rule: inner projects never reference outer ones. Domain/entities projects reference no framework packages.
- Add a package only after the checks in `tech-stack.md` (license, maintenance, security, exit cost).
- Remove unused packages; `dotnet list package --vulnerable --include-transitive` runs in CI.
- Wire dependencies only in the composition root (the outermost project).

## Code cleanliness

- Methods ≤ ~30 lines and ≤ 4 parameters (group extras in a record/options object); cyclomatic complexity ≤ 10.
- Early returns / guard clauses instead of deep nesting.
- No dead code, commented-out code, or stale TODOs (TODOs reference an issue: `TODO(#123)`).
- XML doc comments on public API of reusable layers: what and why; none that repeat the signature.
- No magic values; use constants, enums or options.
- Run `dotnet format` and `dotnet build -warnaserror` before every commit (pre-commit does it).
