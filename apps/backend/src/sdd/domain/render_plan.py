"""Which template becomes which file of the generated monorepo."""

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum

from sdd.domain.catalogue import (
    AGENT_ENTRY_FILES,
    TECHNOLOGY_PROJECT_TYPES,
    ProjectType,
    Technology,
)
from sdd.domain.project_spec import ProjectSpec

TEMPLATE_SUFFIX = ".tmpl"
_RULESETS_PREFIX = "rulesets/"
_ISSUES_PREFIX = "issues/"
_TECHNOLOGY_NAMES = frozenset(technology.value for technology in Technology)
_PROJECT_TYPE_NAMES = frozenset(project_type.value for project_type in ProjectType)
_TYPED_TECHNOLOGIES = frozenset(technology.value for technology in TECHNOLOGY_PROJECT_TYPES)


@dataclass(frozen=True)
class _Selection:
    """The technology and, when the technology offers them, the project type of one kind."""

    technology: str
    project_type: str | None


class RenderMode(StrEnum):
    RENDER = "render"
    VERBATIM = "verbatim"


class RenderPlanError(Exception):
    """Raised when the templates cannot be mapped to a safe set of destinations."""


@dataclass(frozen=True)
class PlannedFile:
    """One template, its destination and how it is processed."""

    destination: str
    mode: RenderMode
    source: str
    application_kind: str | None = None
    executable: bool = False


def build_render_plan(spec: ProjectSpec, template_paths: Iterable[str]) -> tuple[PlannedFile, ...]:
    """Map the available templates to destinations for this spec, sorted by destination."""
    technologies = {
        application.kind.value: _Selection(
            application.technology.value,
            application.project_type.value if application.project_type else None,
        )
        for application in spec.applications
    }
    planned: list[PlannedFile] = []
    for source in sorted(template_paths):
        destination = _destination(source, spec.agent.value, technologies)
        if destination is None:
            continue
        is_template = source.endswith(TEMPLATE_SUFFIX)
        if is_template:
            destination = destination.removesuffix(TEMPLATE_SUFFIX)
        planned.append(
            PlannedFile(
                destination=destination,
                mode=RenderMode.RENDER if is_template else RenderMode.VERBATIM,
                source=source,
                application_kind=_application_kind(source),
            )
        )
    _validate_destinations([file.destination for file in planned])
    entry_file = AGENT_ENTRY_FILES[spec.agent]
    if entry_file not in {file.destination for file in planned}:
        raise RenderPlanError(f"no template produces the agent entry file '{entry_file}'")
    return tuple(sorted(planned, key=lambda file: file.destination))


def _application_kind(source: str) -> str | None:
    head, _, rest = source.partition("/")
    return rest.partition("/")[0] if head == "apps" else None


def _destination(source: str, agent: str, technologies: dict[str, _Selection]) -> str | None:
    head, _, rest = source.partition("/")
    if head == "harness":
        return "AGENTS.md" if rest == "AGENTS.md" else source
    if head == "github":
        return _github_destination(rest)
    if head == "agents":
        selected, _, name = rest.partition("/")
        return name if selected == agent and name else None
    if head == "project" and rest:
        return rest
    if head == "apps":
        return _application_destination(rest, technologies)
    raise RenderPlanError(f"template '{source}' has no destination")


def _application_destination(rest: str, selections: dict[str, _Selection]) -> str | None:
    kind, _, name = rest.partition("/")
    if kind not in selections or not name:
        return None
    selection = selections[kind]
    technology, _, path = name.partition("/")
    if not path or technology not in _TECHNOLOGY_NAMES:
        return f"apps/{kind}/{name}"
    if technology != selection.technology:
        return None
    project_type, _, files = path.partition("/")
    if technology in _TYPED_TECHNOLOGIES and files and project_type in _PROJECT_TYPE_NAMES:
        return f"apps/{kind}/{files}" if project_type == selection.project_type else None
    return f"apps/{kind}/{path}"


def _github_destination(rest: str) -> str | None:
    if rest.startswith(_RULESETS_PREFIX):
        return None
    if rest.startswith(_ISSUES_PREFIX):
        return f".github/ISSUE_TEMPLATE/{rest.removeprefix(_ISSUES_PREFIX)}"
    return f".github/{rest}"


def _validate_destinations(destinations: list[str]) -> None:
    seen: set[str] = set()
    for destination in destinations:
        parts = destination.split("/")
        if (
            not destination
            or destination.startswith("/")
            or "\\" in destination
            or "\0" in destination
            or any(part in {"", ".", ".."} for part in parts)
        ):
            raise RenderPlanError(f"destination '{destination}' is not a safe relative path")
        key = destination.casefold()
        if key in seen:
            raise RenderPlanError(f"destination '{destination}' is produced more than once")
        seen.add(key)
