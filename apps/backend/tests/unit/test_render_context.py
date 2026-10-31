import pytest

from sdd.domain.project_spec import ProjectSpec
from sdd.domain.render_context import build_application_contexts, build_render_context
from tests.unit.factories import raw_spec


@pytest.mark.parametrize("project_type", ["api", "console", "library"])
def test_csharp_application_gets_its_project_type(project_type: str) -> None:
    spec = ProjectSpec.from_raw(
        raw_spec(typology="backend", technologies={"backend": "csharp"}, project_type=project_type)
    )

    assert build_application_contexts(spec)["backend"]["project_type"] == project_type


def test_csharp_application_without_a_type_gets_the_default() -> None:
    spec = ProjectSpec.from_raw(raw_spec(typology="backend", technologies={"backend": "csharp"}))

    assert build_application_contexts(spec)["backend"]["project_type"] == "api"


def test_application_without_project_types_gets_an_empty_value() -> None:
    contexts = build_application_contexts(ProjectSpec.from_raw(raw_spec()))

    assert contexts["frontend"]["project_type"] == ""


@pytest.mark.parametrize("project_type", ["api", "console", "library"])
def test_python_application_gets_its_project_type(project_type: str) -> None:
    spec = ProjectSpec.from_raw(
        raw_spec(typology="backend", technologies={"backend": "python"}, project_type=project_type)
    )

    assert build_application_contexts(spec)["backend"]["project_type"] == project_type


def test_render_context_lists_the_project_type_of_each_application() -> None:
    spec = ProjectSpec.from_raw(
        raw_spec(technologies={"backend": "csharp", "frontend": "react-typescript"})
    )

    applications = build_render_context(spec, "acme")["applications"]

    assert isinstance(applications, list)
    assert [a["project_type"] for a in applications] == ["api", ""]
