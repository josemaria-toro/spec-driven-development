import pytest

from sdd.domain.catalogue import (
    ApplicationKind,
    ProjectType,
    Technology,
    Typology,
    applications_of,
)
from sdd.domain.errors import ValidationFailedError
from sdd.domain.project_spec import Application, ProjectSpec
from tests.unit.factories import raw_spec


def fields_with_issues(error: pytest.ExceptionInfo[ValidationFailedError]) -> list[str]:
    return [issue.field for issue in error.value.issues]


def test_complete_spec_is_accepted() -> None:
    spec = ProjectSpec.from_raw(raw_spec())

    assert spec.project_name == "Orders Platform"
    assert spec.repository_name == "orders-platform"
    assert spec.description == "Order management platform"
    assert spec.typology is Typology.FULLSTACK


def test_missing_repository_name_is_reported_as_required() -> None:
    data = raw_spec()
    del data["repository_name"]

    with pytest.raises(ValidationFailedError) as error:
        ProjectSpec.from_raw(data)

    assert error.value.issues[0].field == "repository_name"
    assert error.value.issues[0].reason == "is required"


def test_description_is_optional() -> None:
    data = raw_spec()
    del data["description"]

    assert ProjectSpec.from_raw(data).description == ""


def test_surrounding_whitespace_is_trimmed() -> None:
    spec = ProjectSpec.from_raw(raw_spec(project_name="  Orders Platform  "))

    assert spec.project_name == "Orders Platform"


def test_non_text_value_is_rejected() -> None:
    with pytest.raises(ValidationFailedError) as error:
        ProjectSpec.from_raw(raw_spec(project_name=42))

    assert fields_with_issues(error) == ["project_name"]
    assert error.value.issues[0].reason == "must be text"


@pytest.mark.parametrize(
    ("typology", "expected"),
    [
        (Typology.BACKEND, (ApplicationKind.BACKEND,)),
        (Typology.FRONTEND, (ApplicationKind.FRONTEND,)),
        (Typology.FULLSTACK, (ApplicationKind.BACKEND, ApplicationKind.FRONTEND)),
    ],
)
def test_typology_determines_the_applications(
    typology: Typology, expected: tuple[ApplicationKind, ...]
) -> None:
    assert applications_of(typology) == expected


def test_fullstack_spec_resolves_one_backend_and_one_frontend_application() -> None:
    spec = ProjectSpec.from_raw(raw_spec())

    assert spec.applications == (
        Application(ApplicationKind.BACKEND, Technology.PYTHON, ProjectType.API),
        Application(ApplicationKind.FRONTEND, Technology.REACT_TYPESCRIPT),
    )
    assert [a.directory for a in spec.applications] == ["apps/backend", "apps/frontend"]


def test_unsupported_typology_is_rejected_and_supported_ones_are_listed() -> None:
    with pytest.raises(ValidationFailedError) as error:
        ProjectSpec.from_raw(raw_spec(typology="mobile"))

    assert error.value.issues[0].field == "typology"
    assert "backend, frontend, fullstack" in error.value.issues[0].reason


def test_supported_technologies_are_accepted() -> None:
    spec = ProjectSpec.from_raw(raw_spec(typology="backend", technologies={"backend": "csharp"}))

    assert spec.applications == (
        Application(ApplicationKind.BACKEND, Technology.CSHARP, ProjectType.API),
    )


def test_technology_of_the_wrong_kind_is_rejected() -> None:
    with pytest.raises(ValidationFailedError) as error:
        ProjectSpec.from_raw(
            raw_spec(typology="backend", technologies={"backend": "react-typescript"})
        )

    assert error.value.issues[0].field == "technologies.backend"
    assert "supported: python, csharp" in error.value.issues[0].reason


def test_missing_technology_for_an_application_is_rejected() -> None:
    with pytest.raises(ValidationFailedError) as error:
        ProjectSpec.from_raw(raw_spec(technologies={"backend": "python"}))

    assert error.value.issues[0].field == "technologies.frontend"


def test_technologies_are_required() -> None:
    data = raw_spec()
    del data["technologies"]

    with pytest.raises(ValidationFailedError) as error:
        ProjectSpec.from_raw(data)

    assert fields_with_issues(error) == ["technologies"]


def test_technology_for_an_application_outside_the_typology_is_rejected() -> None:
    with pytest.raises(ValidationFailedError) as error:
        ProjectSpec.from_raw(
            raw_spec(
                typology="backend",
                technologies={"backend": "python", "frontend": "react-typescript"},
            )
        )

    assert fields_with_issues(error) == ["technologies.frontend"]


def test_supported_agent_is_accepted() -> None:
    assert ProjectSpec.from_raw(raw_spec(agent="claude")).agent.value == "claude"


def test_unsupported_agent_is_rejected_and_supported_ones_are_listed() -> None:
    with pytest.raises(ValidationFailedError) as error:
        ProjectSpec.from_raw(raw_spec(agent="unknown-agent"))

    assert error.value.issues[0].field == "agent"
    assert "claude" in error.value.issues[0].reason


def test_every_invalid_field_is_reported_together() -> None:
    with pytest.raises(ValidationFailedError) as error:
        ProjectSpec.from_raw(raw_spec(repository_name="../x", typology="mobile"))

    assert sorted(fields_with_issues(error)) == ["repository_name", "typology"]


def test_error_messages_do_not_expose_internals() -> None:
    with pytest.raises(ValidationFailedError) as error:
        ProjectSpec.from_raw(raw_spec(repository_name="../x", agent=None))

    message = str(error.value)
    assert "Traceback" not in message
    assert "/home" not in message
    assert ".py" not in message


def test_direct_construction_cannot_build_an_invalid_spec() -> None:
    with pytest.raises(ValidationFailedError):
        ProjectSpec(
            agent=ProjectSpec.from_raw(raw_spec()).agent,
            applications=(),
            description="",
            project_name="Orders",
            repository_name="orders",
            typology=Typology.BACKEND,
        )


def test_hash_is_equal_when_values_are_equal_in_any_field_order() -> None:
    first = raw_spec()
    second = dict(reversed(list(first.items())))
    second["technologies"] = dict(reversed(list(first["technologies"].items())))

    assert ProjectSpec.from_raw(first).content_hash() == ProjectSpec.from_raw(second).content_hash()


def test_hash_changes_when_a_value_changes() -> None:
    first = ProjectSpec.from_raw(raw_spec())
    second = ProjectSpec.from_raw(raw_spec(description="Another description"))

    assert first.content_hash() != second.content_hash()


def test_hash_ignores_whitespace_around_values() -> None:
    first = ProjectSpec.from_raw(raw_spec(project_name="Orders Platform"))
    second = ProjectSpec.from_raw(raw_spec(project_name="  Orders Platform  "))

    assert first.content_hash() == second.content_hash()


def test_hash_ignores_unicode_composition() -> None:
    composed = ProjectSpec.from_raw(raw_spec(description="café"))
    decomposed = ProjectSpec.from_raw(raw_spec(description="café"))

    assert composed.content_hash() == decomposed.content_hash()


def test_canonical_form_is_compact_sorted_and_versioned() -> None:
    canonical = ProjectSpec.from_raw(raw_spec()).canonical_form()

    assert canonical.startswith('{"agent":"claude","description":')
    assert '"schema_version":2' in canonical
    assert " " not in canonical.replace("Order management platform", "").replace(
        "Orders Platform", ""
    )


def test_hash_is_a_sha256_hex_digest() -> None:
    digest = ProjectSpec.from_raw(raw_spec()).content_hash()

    assert len(digest) == 64
    int(digest, 16)


def csharp_spec(**overrides: object) -> dict[str, object]:
    return raw_spec(typology="backend", technologies={"backend": "csharp"}, **overrides)


def backend_project_type(spec: ProjectSpec) -> ProjectType | None:
    return spec.applications[0].project_type


@pytest.mark.parametrize("project_type", ["api", "console", "library"])
def test_each_supported_project_type_is_accepted(project_type: str) -> None:
    spec = ProjectSpec.from_raw(csharp_spec(project_type=project_type))

    assert backend_project_type(spec) is ProjectType(project_type)


def test_omitted_project_type_defaults_to_api() -> None:
    assert backend_project_type(ProjectSpec.from_raw(csharp_spec())) is ProjectType.API


def test_unsupported_project_type_is_rejected_and_supported_ones_are_listed() -> None:
    with pytest.raises(ValidationFailedError) as error:
        ProjectSpec.from_raw(csharp_spec(project_type="worker"))

    assert fields_with_issues(error) == ["project_type"]
    assert "supported values: api, console, library" in error.value.issues[0].reason


def test_project_type_must_be_text() -> None:
    with pytest.raises(ValidationFailedError) as error:
        ProjectSpec.from_raw(csharp_spec(project_type=3))

    assert fields_with_issues(error) == ["project_type"]


@pytest.mark.usefixtures("python_without_project_types")
def test_technology_without_project_types_rejects_one() -> None:
    with pytest.raises(ValidationFailedError) as error:
        ProjectSpec.from_raw(
            raw_spec(typology="backend", technologies={"backend": "python"}, project_type="library")
        )

    assert fields_with_issues(error) == ["project_type"]
    assert "offers no project types" in error.value.issues[0].reason


@pytest.mark.usefixtures("python_without_project_types")
def test_technology_without_project_types_needs_none() -> None:
    spec = ProjectSpec.from_raw(raw_spec(typology="backend", technologies={"backend": "python"}))

    assert backend_project_type(spec) is None


def test_project_type_without_a_backend_is_rejected() -> None:
    with pytest.raises(ValidationFailedError) as error:
        ProjectSpec.from_raw(
            raw_spec(
                typology="frontend",
                technologies={"frontend": "react-typescript"},
                project_type="api",
            )
        )

    assert fields_with_issues(error) == ["project_type"]
    assert "only to a backend application" in error.value.issues[0].reason


def test_project_type_is_reported_with_the_other_errors() -> None:
    with pytest.raises(ValidationFailedError) as error:
        ProjectSpec.from_raw(csharp_spec(project_type="worker", repository_name="../x"))

    assert set(fields_with_issues(error)) == {"project_type", "repository_name"}


def test_project_type_is_available_to_the_other_applications_of_a_fullstack_spec() -> None:
    spec = ProjectSpec.from_raw(
        raw_spec(
            technologies={"backend": "csharp", "frontend": "react-typescript"},
            project_type="console",
        )
    )

    assert [a.project_type for a in spec.applications] == [ProjectType.CONSOLE, None]


def test_direct_construction_resolves_the_default_type() -> None:
    spec = ProjectSpec(
        agent=ProjectSpec.from_raw(raw_spec()).agent,
        applications=(Application(ApplicationKind.BACKEND, Technology.CSHARP),),
        description="",
        project_name="Orders",
        repository_name="orders",
        typology=Typology.BACKEND,
    )

    assert backend_project_type(spec) is ProjectType.API


def test_direct_construction_refuses_a_project_type_on_a_frontend() -> None:
    with pytest.raises(ValidationFailedError):
        ProjectSpec(
            agent=ProjectSpec.from_raw(raw_spec()).agent,
            applications=(
                Application(ApplicationKind.FRONTEND, Technology.REACT_TYPESCRIPT, ProjectType.API),
            ),
            description="",
            project_name="Orders",
            repository_name="orders",
            typology=Typology.FRONTEND,
        )


@pytest.mark.usefixtures("python_without_project_types")
def test_direct_construction_refuses_a_type_the_technology_does_not_offer() -> None:
    with pytest.raises(ValidationFailedError):
        ProjectSpec(
            agent=ProjectSpec.from_raw(raw_spec()).agent,
            applications=(
                Application(ApplicationKind.BACKEND, Technology.PYTHON, ProjectType.API),
            ),
            description="",
            project_name="Orders",
            repository_name="orders",
            typology=Typology.BACKEND,
        )


def test_different_project_types_give_different_hashes() -> None:
    api = ProjectSpec.from_raw(csharp_spec(project_type="api"))
    library = ProjectSpec.from_raw(csharp_spec(project_type="library"))

    assert api.content_hash() != library.content_hash()


def test_default_project_type_hashes_like_an_explicit_api() -> None:
    omitted = ProjectSpec.from_raw(csharp_spec())
    explicit = ProjectSpec.from_raw(csharp_spec(project_type="api"))

    assert omitted.content_hash() == explicit.content_hash()


@pytest.mark.usefixtures("python_without_project_types")
def test_spec_without_project_types_has_none_in_its_canonical_form() -> None:
    canonical = ProjectSpec.from_raw(raw_spec()).canonical_form()

    assert "project_type" not in canonical


@pytest.mark.parametrize("project_type", ["api", "console", "library"])
def test_each_python_project_type_is_accepted(project_type: str) -> None:
    spec = ProjectSpec.from_raw(
        raw_spec(typology="backend", technologies={"backend": "python"}, project_type=project_type)
    )

    assert backend_project_type(spec) is ProjectType(project_type)


def test_omitted_project_type_defaults_to_api_for_python() -> None:
    spec = ProjectSpec.from_raw(raw_spec(typology="backend", technologies={"backend": "python"}))

    assert backend_project_type(spec) is ProjectType.API
    assert '"project_type":"api"' in spec.canonical_form()


def test_python_project_type_changes_the_hash() -> None:
    base = raw_spec(typology="backend", technologies={"backend": "python"})

    library = ProjectSpec.from_raw({**base, "project_type": "library"})
    console = ProjectSpec.from_raw({**base, "project_type": "console"})

    assert library.content_hash() != console.content_hash()


def test_canonical_form_of_a_csharp_spec_holds_the_resolved_project_type() -> None:
    assert '"project_type":"api"' in ProjectSpec.from_raw(csharp_spec()).canonical_form()
