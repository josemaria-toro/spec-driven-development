# Project generator: frontend

React (TypeScript) web application of the project generator (see `harness/stacks/frontend-react.md`). It currently holds the skeleton only: one page, the quality tooling and the test levels. The guided chat, the project list and the progress view are separate changes.

## Layout

```
src/
  interfaces/     # components, pages and routing (the only layer with code today)
  main.tsx        # mounts the app
tests/
  integration/    # Vitest + React Testing Library, real module wiring
  e2e/            # Playwright, at mobile, tablet and desktop widths, with axe checks
```

The layers follow the hexagonal architecture (`domain`, `application`, `interfaces`, `infrastructure`). Create a layer directory when it first has code. The dependency rule is enforced by `eslint-plugin-boundaries`: `domain` imports nothing, `application` only `domain`, `interfaces` and `infrastructure` may import `application` and `domain`.

## Commands (from `apps/frontend/`)

```bash
pnpm install --frozen-lockfile
pnpm format:check        # Prettier (pnpm format writes)
pnpm lint                # ESLint: types, jsx-a11y, security, layer rule
pnpm typecheck
pnpm test:unit --coverage        # coverage thresholds at 80%
pnpm test:integration
pnpm exec playwright install chromium   # once
pnpm e2e                         # builds the app and runs against `vite preview`
pnpm dev
pnpm audit                       # high and critical block (dev dependencies included)
```

## Node 20 and pinned tooling

The minimum Node version is 20 (`engines`, `.npmrc` `engine-strict=true`, `.nvmrc`), so some tools stay on an older major because their latest one requires Node 22 or newer:

| Tool | Kept at | Why |
|---|---|---|
| `vitest`, `@vitest/coverage-v8` | 4.x | 5.x needs Node 22.12+; 3.x has critical advisories in `tinypool` |
| `jsdom` | 26.x | 30.x needs Node 22.22+ |
| `@testing-library/jest-dom` | 6.x | 7.x needs Node 22+ |
| `@axe-core/playwright` | ~4.10 | 4.14 needs Node 22.12+ |
| `typescript` | ~5.9 | `typescript-eslint` does not support TypeScript 7 yet |
| `vite` | 7.x | 8.x was not evaluated against Node 20 |

Raising the minimum Node version is a stack change (see ADR-0001) and lifts these limits.

## Responsive and accessible

Every screen must be responsive and meet WCAG 2.2 AA (see the stack sheet). The e2e suite runs each flow at 360, 768 and 1280 px, checks there is no horizontal scrolling and runs axe with the WCAG 2.2 AA tags. Each pull request that changes the UI also needs a manual keyboard and screen-reader check.
