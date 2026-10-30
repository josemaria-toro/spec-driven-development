# CLAUDE.md

**The harness in `harness/` is the single source of truth** for how to work in this repository, and `AGENTS.md` (repository root) is its entry point. This file defines no rules and lists no guides: follow `AGENTS.md` to the letter, including which guide to read for each task. If anything here disagrees with the harness, the harness wins.

@AGENTS.md

## Repository layout

- `AGENTS.md`: the entry point to the harness (repository root, where agents look for it).
- `harness/`: guides, stacks and ADRs. Its documents refer to each other with paths relative to `harness/`.
- `apps/`: the applications of this monorepo, one directory each.
- `openspec/`: OpenSpec specs, changes and configuration.
