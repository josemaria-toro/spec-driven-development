# Proposal

## Why

A generated project whose backend technology is C# receives only `apps/backend/README.md`: no solution, no layers, no tests, no lockfiles. The Python backend and the React frontend already start from a verified skeleton (`add-application-skeletons`); the third supported stack does not, so a C# team rebuilds the same hexagonal skeleton by hand and cannot run the quality gates of `harness/stacks/backend-csharp.md` on day one. The previous change left it out only because this environment had no .NET SDK to verify it; the proposal states how it is verified now.

This is a **functional change**: it alters the file tree that rendering generates (observable output), so OpenSpec applies.

## What Changes

- Add a minimal, working **C# backend skeleton** under `templates/apps/backend/csharp/`, rendered into `apps/backend/` only when the spec selects `csharp` for the backend (the technology-aware render plan already supports it; no change to `domain/render_plan.py`):
  - hexagonal layers as projects: `Domain`, `Application` and `Infrastructure` under `src/`, with one example per layer;
  - unit, integration and architecture test projects (xUnit, NetArchTest);
  - build configuration shared by the solution: nullable reference types, warnings as errors, Roslyn analyzers, central package management, NuGet lock files, NuGet audit at high severity, `.editorconfig` and an SDK pin;
  - an 80% line-coverage gate, a layer rule (project references plus architecture tests) and a rule that `Domain` and `Application` use no web, database, broker or HTTP library.
- Fixed names, as in the other skeletons: solution and root namespace `App`, files copied verbatim, no project values inside code, so the output is byte-identical for every project and the shipped lock files stay valid.
- Extend the generated-skeleton test and the `skeletons.yml` workflow to render a C# backend and run its gates, including the dependency audit and the lock-file check.
- The "technology without a skeleton" behavior stays, but C# stops being its example: no catalogue technology lacks a skeleton any more, so tests cover the rule with a template set that omits a technology directory.

Out of scope (separate changes):

- The CI workflows for generated applications and CodeQL (`add-application-workflow-templates`).
- Any runtime adapter: no ASP.NET Core host, `Api` project, database, broker or authentication; the skeleton holds one trivial example per layer, as the Python one does.
- Pre-commit configuration for generated projects, and the start/stop scripts.
- Enforcing the member-ordering rule of `development-csharp.md` by tooling (see the design); the skeleton follows it by hand.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `application-skeletons`: adds the C# backend skeleton and widens the requirements that were written for Python and React only (quality gates, lock files, fixed names, technology without a skeleton).

## Impact

- **Templates:** new directory `templates/apps/backend/csharp/` (about 35 files: 7 projects, build files, 7 `packages.lock.json` of a few hundred lines each). The per-kind README stays.
- **Backend application** (Python, hexagonal architecture; `harness/stacks/backend-python.md`): no production code changes; integration tests that used C# as the "no skeleton" example and the expected file sets change, and the generated test learns the C# gates.
- **Stack of the generated skeleton** (C# on .NET 10 LTS, hexagonal architecture; `harness/stacks/backend-csharp.md`): follows the stack sheet and `development-csharp.md`.
- **CI of this repository (flag: CI configuration):** `skeletons.yml` gains a .NET SDK setup step and now also runs on changes to `templates/apps/backend/csharp/**` (already covered by `templates/apps/**`). Touching CI is subject to approval of this proposal.
- **Dependencies and supply chain (security-sensitive area):** the skeleton pins NuGet packages in lock files: xUnit, NetArchTest and Coverlet from the approved list, plus `Microsoft.NET.Test.Sdk` and `xunit.runner.visualstudio`, which xUnit projects cannot run without and which are not in the approved table. The PR justifies them with the criteria of `tech-stack.md`; the OWASP checklist (vulnerable and outdated components, software and data integrity) must be completed in the PR.
- **Security of rendering:** no project values enter code, so there is no new injection surface; existing filters and the lint test are unchanged.
- **Exceptions:** none. No ADR is required unless review rejects the two test-host packages.
