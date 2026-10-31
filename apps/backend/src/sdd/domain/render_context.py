"""The values that templates may use."""

from sdd.domain.catalogue import TECHNOLOGY_ECOSYSTEMS, TECHNOLOGY_STACK_SHEETS
from sdd.domain.project_spec import Application, ProjectSpec


def build_application_contexts(spec: ProjectSpec) -> dict[str, dict[str, object]]:
    """Values of each application, by kind; given as `application` to its own templates."""
    return {
        application.kind.value: _application_values(application)
        for application in spec.applications
    }


def build_render_context(spec: ProjectSpec, owner: str) -> dict[str, object]:
    """Return the data given to every rendered template."""
    return {
        "agent": spec.agent.value,
        "applications": list(build_application_contexts(spec).values()),
        "owner": owner,
        "project": {
            "description": spec.description,
            "name": spec.project_name,
            "repository": spec.repository_name,
        },
    }


def _application_values(application: Application) -> dict[str, object]:
    return {
        "directory": application.directory,
        "ecosystem": TECHNOLOGY_ECOSYSTEMS[application.technology],
        "kind": application.kind.value,
        "project_type": application.project_type.value if application.project_type else "",
        "stack_sheet": TECHNOLOGY_STACK_SHEETS[(application.kind, application.technology)],
        "technology": application.technology.value,
    }
