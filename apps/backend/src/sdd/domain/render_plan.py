"""Which template becomes which file of the generated monorepo."""

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum

from sdd.domain.catalogue import AGENT_ENTRY_FILES
from sdd.domain.project_spec import ProjectSpec

TEMPLATE_SUFFIX = ".tmpl"
_RULESETS_PREFIX = "rulesets/"
_ISSUES_PREFIX = "issues/"


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
    kinds = {application.kind.value for application in spec.applications}
    planned: list[PlannedFile] = []
    for source in sorted(template_paths):
        destination = _destination(source, spec.agent.value, kinds)
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


def _destination(source: str, agent: str, kinds: set[str]) -> str | None:
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
        kind, _, name = rest.partition("/")
        return source if kind in kinds and name else None
    raise RenderPlanError(f"template '{source}' has no destination")


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
