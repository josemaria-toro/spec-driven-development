import pytest

from sdd.domain.catalogue import (
    ApplicationKind,
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
        Application(ApplicationKind.BACKEND, Technology.PYTHON),
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

    assert spec.applications == (Application(ApplicationKind.BACKEND, Technology.CSHARP),)


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
    assert '"schema_version":1' in canonical
    assert " " not in canonical.replace("Order management platform", "").replace(
        "Orders Platform", ""
    )


def test_hash_is_a_sha256_hex_digest() -> None:
    digest = ProjectSpec.from_raw(raw_spec()).content_hash()

    assert len(digest) == 64
    int(digest, 16)
