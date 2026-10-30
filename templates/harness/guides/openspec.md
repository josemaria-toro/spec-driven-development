# OpenSpec guide

[OpenSpec](https://github.com/Fission-AI/OpenSpec) is the specification tool of this harness. **Its use is mandatory for any functional change.**

## What is a functional change

A change that adds, modifies or removes **observable behavior**: features, business rules, API contracts, data formats, UI behavior, permissions, messages/events, or bug fixes that alter specified behavior.

| Change | OpenSpec required |
|---|---|
| New feature, changed behavior, API/event contract change, new or changed UI flow | **Yes** |
| Bug fix that restores already-specified behavior | Yes if the spec was ambiguous or wrong; otherwise reference the existing requirement in the PR |
| Behavior-preserving refactor, dependency bump, CI/tooling, formatting, docs-only (`chore`) | No |
| Urgent production fix (`hotfix`) | Yes, but the proposal may be written right after the fix, **within one working day** and before the next release |

When in doubt, it is functional: write the proposal.

## Flow

The flow is driven with the `/opsx:*` slash commands (installed in `.claude/commands/opsx/` by `openspec init`). The `openspec` CLI is used for validation and inspection.

| Step | Command | What it does |
|---|---|---|
| 0. Think (optional) | `/opsx:explore` | Thinking mode: investigate, compare options, clarify requirements. It never implements; it may capture decisions in change artifacts only after you confirm. |
| 1. Propose | `/opsx:propose <change-id or description>` | Creates `openspec/changes/<change-id>/` and generates all planning artifacts in one step. **Planning only: it does not edit code** and stops when the artifacts are ready. |
| 2. Revise | `/opsx:update` | Revises the existing planning artifacts and keeps them coherent with each other. It never edits code. |
| 3. Review | `openspec validate <change-id>` | Validates the change; the proposal is reviewed and approved before implementation starts. |
| 4. Implement | `/opsx:apply` | Works through the change's `tasks.md`, ticking tasks off. Starts only after approval, in a branch named after the change (see `git-workflow.md`); tests cover every scenario. |
| 5. Sync (optional) | `/opsx:sync` | Applies the change's delta specs to `openspec/specs/` without archiving, when the main specs must reflect the change earlier. |
| 6. Archive | `/opsx:archive` | After merge, archives the change and merges its deltas into `openspec/specs/` (it also assesses the sync state). The specs then describe the current behavior. |

Artifacts of a change, under `openspec/changes/<change-id>/`:

- `proposal.md`: why, what changes, impact.
- `specs/…`: the requirement deltas (added, modified, removed) with scenarios (Given/When/Then).
- `design.md`: only when the change has architecture or technical trade-offs.
- `tasks.md`: small, verifiable implementation tasks.

Project-specific rules for each artifact and for apply/archive live in `openspec/config.yaml` and are loaded automatically by the commands. Equivalent CLI commands: `openspec list`, `openspec show <change-id>`, `openspec status --change <change-id>`, `openspec archive <change-id>`.

## Rules

- `openspec/specs/` is the source of truth for behavior; code and tests must agree with it.
- Every requirement has at least one scenario, and every scenario has at least one test (unit, integration or e2e as applicable).
- One change per functional purpose; keep changes small and independent.
- Architecture decisions and exceptions go to an ADR; the change `design.md` links to it.
- The change id is `kebab-case`, verb-led (`add-order-export`), and is used in the branch name, commits scope and PR.
- Do not edit `openspec/specs/` directly; modify specs only through a change (`/opsx:sync` and `/opsx:archive` are the sanctioned ways to apply its deltas).
- AI agents must not implement a functional change without an approved proposal; if none exists, they run `/opsx:propose` first and ask for approval. `/opsx:propose`, `/opsx:update` and `/opsx:explore` never edit code, and `/opsx:apply` is run only after approval.

## Traceability

- Branch: `<prefix>/<change-id>` (e.g. `feature/add-order-export`, `change/split-invoice-lines`).
- Commits: scope is the change id when applicable (`feature(add-order-export): …`).
- PR: links `openspec/changes/<change-id>/` and states which requirements/scenarios it implements.
- CI: runs `openspec validate --all` and fails if a functional PR has no change proposal.
