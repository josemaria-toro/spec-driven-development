# Development guide: React (TypeScript)

Complements `development.md`. Tooling and commands live in `stacks/frontend-react.md`. Style is enforced by Prettier, ESLint and `tsc`; responsive and WCAG 2.2 AA rules are in the stack sheet.

## Best practices

- TypeScript `strict`; no `any` (use `unknown` and narrow), no `@ts-ignore` (use `@ts-expect-error` with a reason).
- Function components and hooks only; no class components.
- Components are small and presentational where possible; business logic lives in use cases/domain code, not in components or hooks (see `architecture.md`).
- Derive state instead of duplicating it; keep state as local as possible; server state through TanStack Query, not manual `useEffect` fetching.
- `useEffect` only for synchronizing with external systems; never to compute derived values or respond to events.
- Stable, unique `key` props (never array index for reorderable lists).
- Props are typed explicitly and immutable; avoid prop drilling beyond ~2 levels (use composition or context).
- Validate all external data at the edge (Zod) before it enters the domain.
- Never use `dangerouslySetInnerHTML` without a security review (see `security.md`).
- Memoization (`memo`, `useMemo`, `useCallback`) only after measuring a problem.
- Prefer named exports; default exports only where a framework requires them (e.g. lazy routes).
- Async code uses `async/await`; every promise is awaited or handled; handle loading and error states in the UI.

## Naming

| Element | Convention | Example |
|---|---|---|
| Component, type, interface, enum | `PascalCase` | `OrderList`, `OrderDto` |
| Component file | `PascalCase.tsx`, one component per file | `OrderList.tsx` |
| Other files / folders | `kebab-case` | `order-service.ts` |
| Function, variable | `camelCase`, verb for functions | `calculateTotal` |
| Hook | `use` + `PascalCase` | `useOrders` |
| Constant | `UPPER_SNAKE_CASE` | `MAX_RETRIES` |
| Boolean | `is/has/should` prefix | `isLoading`, `hasError` |
| Event handler prop / function | `on…` prop, `handle…` function | `onSubmit`, `handleSubmit` |
| Type parameter | `T` or `T` + `PascalCase` | `TItem` |
| Test file | same name + `.test.ts(x)`; e2e `*.spec.ts` | `OrderList.test.tsx` |

- Do not prefix interfaces with `I` nor types with `T`; use `type` for unions/aliases and `interface` for object shapes meant to be implemented/extended, consistently.
- Ports carry the role (`OrderRepository`); adapters include the technology (`HttpOrderRepository`).

## Member ordering

Inside a component file, top to bottom:

1. Imports (see below).
2. Types/interfaces for props.
3. Constants outside the component.
4. The component function, internally:
   1. Props destructuring
   2. Hooks (`useState`, `useContext`, custom hooks, `useQuery`) — always at the top level, in a stable order
   3. Derived values
   4. Handlers (`handle…`)
   5. Effects (`useEffect`)
   6. Early returns (loading / error / empty)
   7. Returned JSX
5. Small helper functions used only by the component, below it.

Classes (services, adapters, domain objects) follow the same order as the other stacks, top to bottom:

1. **Constructors**
2. **Properties**, alphabetical, **public first, then the rest** (`protected`, `private`/`#private`)
3. **Methods**, alphabetical, **public first, then the rest** (`protected`, `private`/`#private`)

In the same way, properties of interfaces, types and object literals are listed alphabetically (public API of the type; no visibility split), and in a module the exported functions come first, alphabetical, followed by the non-exported ones, alphabetical.

Exempt from alphabetical order, because order is semantic: **hooks inside a component** (the Rules of Hooks require a stable order), JSX children, function parameters, enum values and tuple types.

## Imports

Ordered by ESLint (`import/order` or `simple-import-sort`) and Prettier; never hand-sort. Groups separated by one blank line:

1. Side-effect imports (`import './styles.css'`) only where required
2. Node/built-in and external packages (`react` first, then others alphabetically)
3. Internal absolute aliases (`@/domain/…`, `@/application/…`)
4. Relative imports (parent `../` before sibling `./`)
5. Type-only imports (`import type { … }`), kept with their group or last, consistently

Rules:

- Use `import type` for types so they vanish at compile time.
- Path aliases (`@/`) for cross-folder imports; relative only within the same feature folder; no `../../../` chains.
- No wildcard imports (`import * as x`) except for namespaces of well-known libraries.
- No unused imports; no circular imports.
- Imports must respect the layer rule (domain imports no React or infrastructure); the boundaries lint rule fails the build otherwise.

## Dependencies

- Declared in `package.json`; `pnpm-lock.yaml` committed; install with `pnpm install --frozen-lockfile`.
- `dependencies` vs `devDependencies` kept correct; exact or tightly-ranged versions, updated through Dependabot/Renovate.
- Add a package only after the checks in `tech-stack.md` (license, maintenance, security, bundle size, exit cost); prefer the platform or existing libraries first.
- Third-party libraries are used behind adapters when they touch I/O or storage; the domain has no external dependencies.
- Remove unused packages; `pnpm audit --prod` runs in CI; watch bundle size.

## Code cleanliness

- Functions ≤ ~30 lines, components ≤ ~150 lines; split by responsibility, not by line count alone.
- Early returns instead of nested ternaries; no nested ternaries in JSX.
- No dead code, commented-out code, `console.log`, or stale TODOs (TODOs reference an issue: `TODO(#123)`).
- Comments explain why; JSDoc on exported functions of shared layers only when not obvious from types.
- No magic values; extract constants, enums or design tokens (colors, spacing, breakpoints).
- Run `pnpm format`, `pnpm lint` and `pnpm typecheck` before every commit (pre-commit does it).
