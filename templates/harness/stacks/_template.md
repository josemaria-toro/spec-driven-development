# Stack: <project/technology name>

> Copy this file to `stacks/<name>.md` and fill it in. Replace every `<…>`.

## Summary

- **Purpose**: <what this project is>
- **Architecture**: <hexagonal | clean architecture> (see `guides/architecture.md`; anything else needs an ADR)

## Runtime and tooling

| Element | Choice | Minimum version |
|---|---|---|
| Language/runtime | <…> | <…> |
| Package manager | <…> | <…> |
| Framework | <…> | <…> |
| Linter / formatter | <…> | <…> |
| Typing | <…> | <…> |
| Testing | <…> | <…> |

## Standard commands

```bash
<install>
<format>
<lint>
<types>
<unit tests>
<integration tests>
<e2e tests (frontend only; remove for backend)>
<run locally>
```

## Folder structure

```
<project tree following architecture.md>
```

## Quality

- Minimum coverage: 80% or higher, enforced before each commit (unit tests) and in CI: <coverage command with threshold>
- Stack-specific lint rules: <…>
- Layer dependency check: <tool>

## Approved dependencies

| Library | Use | License |
|---|---|---|
| <…> | <…> | <…> |

## Specifics

<conventions or pitfalls particular to this stack>
