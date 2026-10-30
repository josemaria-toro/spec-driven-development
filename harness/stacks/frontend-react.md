# Stack: Frontend — React

## Summary

- **Purpose**: web frontends in React with TypeScript.
- **Architecture**: <hexagonal | clean architecture> (see `guides/architecture.md`; declare one per project).

## Runtime and tooling

| Element | Choice | Minimum version |
|---|---|---|
| Language | TypeScript (`strict`) | latest stable |
| UI library | React | latest major with active support |
| Runtime | Node.js | **20** (minimum; newer versions allowed) |
| Package manager | pnpm (lockfile committed) | — |
| Build tool | Vite | — |
| Linter / formatter | ESLint + Prettier | — |
| Testing | Vitest, React Testing Library, Playwright (e2e) | — |
| Layer checks | eslint-plugin-boundaries or dependency-cruiser | — |

## Standard commands

```bash
pnpm install --frozen-lockfile   # install
pnpm format                      # format
pnpm lint                        # lint
pnpm typecheck                   # tsc --noEmit
pnpm test:unit --coverage        # unit tests + coverage
pnpm test:integration            # integration tests (components + adapters, mocked network)
pnpm e2e                         # e2e with Playwright
pnpm dev                         # run locally
pnpm audit --prod                # dependency audit
```

## Folder structure

```
src/
  domain/ application/ interfaces/ infrastructure/   # hexagonal
  # or: entities/ use-cases/ adapters/ frameworks/     # clean architecture
  # interfaces/ (or frameworks/) holds components, pages and routing
tests/
  e2e/
package.json
pnpm-lock.yaml
```

## Quality

- Minimum coverage: 80%, gate before each commit and in CI: Vitest `coverage.thresholds` (lines, functions, branches, statements = 80) with `pnpm test:unit --coverage`.
- `strict` TypeScript; no `any` without a justified comment.
- Domain/entities code is plain TypeScript: no React, no browser APIs, no fetch.
- Layer rule enforced in lint/CI.
- Accessibility: WCAG 2.2 AA; `eslint-plugin-jsx-a11y` and automated checks in e2e.

## Mandatory rule: responsive and accessible

**Every frontend must be responsive and conform to WCAG 2.2 level AA.** This is not optional and applies to every screen and component.

Responsive:
- Mobile-first layouts that work from 320 px wide up to large desktop, with no horizontal scrolling (except data tables/maps that need it).
- Fluid layouts and relative units (`rem`, `%`, `fr`, `clamp()`); breakpoints are defined once as design tokens.
- Touch targets of at least 24×24 CSS px (WCAG 2.5.8), ideally 44×44 px.
- Content reflows at 400% zoom and respects user text-size settings.
- Images and media are responsive (`srcset`/`sizes`, max-width).

Accessible (WCAG 2.2 AA):
- Semantic HTML first; ARIA only when native elements are not enough.
- Full keyboard operability with visible focus (including focus not obscured, WCAG 2.4.11).
- Color contrast ≥ 4.5:1 for text and ≥ 3:1 for UI components; information is never conveyed by color alone.
- Labels, error messages and instructions for all form controls; no redundant re-entry of data (WCAG 3.3.7).
- Text alternatives for non-text content; captions for video.
- Respect `prefers-reduced-motion` and `prefers-color-scheme` where applicable.

Verification (required in CI):
- `eslint-plugin-jsx-a11y` has no errors.
- Playwright e2e runs the critical flows at **mobile, tablet and desktop viewports** and runs axe checks (`@axe-core/playwright`) with zero violations of WCAG 2.2 AA rules.
- Automated checks do not cover everything: each PR that changes UI includes a manual keyboard and screen-reader check, noted in the PR.
- Violating this rule is a guardrail exception and requires an ADR with an expiry date.
- Vulnerability gate (pre-commit and CI; high/critical vulnerabilities and any secret block): `pnpm audit --prod --audit-level high` (extend to dev dependencies with `pnpm audit --audit-level high`) and secret scan with gitleaks; never place secrets in client-side env variables (they are public).

## Approved dependencies

| Library | Use | License |
|---|---|---|
| React, React DOM | UI | MIT |
| React Router | Routing | MIT |
| TanStack Query | Server state | MIT |
| Zod | Boundary validation | MIT |
| Vitest, React Testing Library | Testing | MIT |
| Playwright (`@playwright/test`) | E2E test framework | Apache-2.0 |
| @axe-core/playwright | Accessibility checks in e2e | MPL-2.0 |
| ESLint, Prettier | Quality tooling | MIT |
| Vite, @vitejs/plugin-react | Build tool and React plugin | MIT |
| TypeScript, typescript-eslint | Language and type-aware lint | Apache-2.0 / MIT |
| @vitest/coverage-v8, jsdom, @testing-library/jest-dom, @testing-library/user-event | Unit and integration test support | MIT |
| eslint-plugin-jsx-a11y, eslint-plugin-react-hooks, eslint-plugin-boundaries | Accessibility, hooks and layer lint | MIT |
| eslint-import-resolver-typescript | Lets the layer rule resolve `@/` aliases | ISC |
| `pnpm audit` | Dependency vulnerability audit (pre-commit + CI) | built into pnpm |
| eslint-plugin-security | SAST (lint, CI) | Apache-2.0 |
| OSV-Scanner | Cross-check of vulnerability data with severity (optional) | Apache-2.0 |
| gitleaks | Secret scanning (pre-commit + CI) | MIT |
| pre-commit | Hook runner | MIT |

## Node.js version

- **Minimum supported version: Node.js 20.** Newer versions are allowed; nothing may rely on features unavailable in Node 20.
- Declare it in `package.json` (`"engines": { "node": ">=20" }`) and set `engine-strict=true` in `.npmrc`, so installs fail on older versions.
- Pin the local/CI version in `.nvmrc` (or `.node-version`) and in the CI `setup-node` step; CI runs on the minimum (20) and may add a matrix with newer versions.
- Docker images and tooling use `node:20` or newer, never older.
- Dependency updates must stay compatible with `engines`; Dependabot does not raise the minimum on its own.
- Staying on Node 20 pins some tools to an older major (the latest `vitest`, `jsdom`, `@testing-library/jest-dom` and `@axe-core/playwright` require Node 22 or newer). The current pins and their reasons are listed in `apps/frontend/README.md`; with `engine-strict=true` an incompatible update fails the install instead of slipping in.
- Node 20 is an exception to the supported-versions policy, recorded in `adr/0001-node-20-minimum-version-exception.md` (expires 2027-01-31). Raising the minimum is a stack change and requires an ADR (see `guides/tech-stack.md`).

## Specifics

- Components are presentational where possible; business logic lives in use cases, not in components or hooks.
- All API responses are validated at the edge (Zod) before reaching the domain.
- No direct `fetch`/storage access from components: go through adapters.
- Playwright conventions (e2e, mandatory for the frontend): config in `playwright.config.ts`; tests in `tests/e2e/*.spec.ts`; locate elements by role/label/text (`getByRole`, `getByLabel`), not CSS or XPath; rely on auto-waiting and web-first assertions (`expect(locator).toBeVisible()`), never fixed sleeps; one independent test per user flow with isolated state (fresh context/storage); use the Page Object pattern for repeated flows; run against a built app in CI; keep traces/screenshots on failure as CI artifacts; browsers installed with `pnpm exec playwright install --with-deps`.
- Include automated accessibility checks in e2e (e.g. `@axe-core/playwright`).
- Never render unsanitized HTML (`dangerouslySetInnerHTML` requires a security review).
