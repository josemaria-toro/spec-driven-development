import pytest

from sdd.domain.fields import (
    validate_description,
    validate_project_name,
    validate_repository_name,
)


def test_repository_name_is_accepted_when_valid() -> None:
    assert validate_repository_name("orders-platform") == []


@pytest.mark.parametrize("value", ["a", "a1", "1a", "a--b", "x" * 100])
def test_repository_name_is_accepted_at_boundaries(value: str) -> None:
    assert validate_repository_name(value) == []


def test_repository_name_is_rejected_when_it_is_a_path_traversal() -> None:
    issues = validate_repository_name("../outside")

    assert [issue.field for issue in issues] == ["repository_name"]
    assert "'.'" in issues[0].reason
    assert "'/'" in issues[0].reason


def test_repository_name_reports_the_characters_that_are_not_allowed() -> None:
    issues = validate_repository_name("Orders Platform!")

    assert "'O'" in issues[0].reason
    assert "' '" in issues[0].reason
    assert "'!'" in issues[0].reason


def test_repository_name_reports_the_maximum_length() -> None:
    issues = validate_repository_name("a" * 101)

    assert any("at most 100" in issue.reason for issue in issues)


@pytest.mark.parametrize("value", ["-orders", "orders-"])
def test_repository_name_is_rejected_when_it_starts_or_ends_with_a_hyphen(value: str) -> None:
    issues = validate_repository_name(value)

    assert [issue.reason for issue in issues] == ["must not start or end with a hyphen"]


def test_repository_name_is_rejected_when_empty() -> None:
    assert validate_repository_name("")[0].reason == "is required"


def test_project_name_is_accepted_when_valid() -> None:
    assert validate_project_name("Orders Platform") == []


def test_project_name_is_rejected_when_empty() -> None:
    assert validate_project_name("")[0].reason == "is required"


def test_project_name_is_rejected_when_too_long() -> None:
    assert "at most 100" in validate_project_name("a" * 101)[0].reason


@pytest.mark.parametrize("value", ["a\nb", "a\x00b", "a" + chr(0x2028) + "b", "a\tb"])
def test_names_and_description_are_rejected_when_they_contain_control_characters(
    value: str,
) -> None:
    assert "control characters" in validate_project_name(value)[0].reason
    assert "control characters" in validate_description(value)[0].reason


def test_description_is_accepted_when_empty() -> None:
    assert validate_description("") == []


def test_description_is_accepted_at_the_maximum_length() -> None:
    assert validate_description("a" * 350) == []


def test_description_is_rejected_when_too_long() -> None:
    assert "at most 350" in validate_description("a" * 351)[0].reason
