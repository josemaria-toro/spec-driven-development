"""Rules for the free-text fields of a project spec."""

import re
import unicodedata

from project_generator.domain.errors import ValidationIssue

MAX_DESCRIPTION_LENGTH = 350
MAX_NAME_LENGTH = 100
MAX_REPOSITORY_NAME_LENGTH = 100
MAX_REPORTED_CHARACTERS = 5

_FORBIDDEN_CATEGORIES = frozenset({"Cc", "Zl", "Zp"})
_REPOSITORY_NAME = re.compile(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?")
_REPOSITORY_NAME_CHARACTER = re.compile(r"[a-z0-9-]")


def validate_description(value: str) -> list[ValidationIssue]:
    """Return the issues of a description (it may be empty)."""
    issues = _control_character_issues("description", value)
    if len(value) > MAX_DESCRIPTION_LENGTH:
        issues.append(
            ValidationIssue("description", f"must be at most {MAX_DESCRIPTION_LENGTH} characters")
        )
    return issues


def validate_project_name(value: str) -> list[ValidationIssue]:
    """Return the issues of a project name."""
    if not value:
        return [ValidationIssue("project_name", "is required")]
    issues = _control_character_issues("project_name", value)
    if len(value) > MAX_NAME_LENGTH:
        issues.append(
            ValidationIssue("project_name", f"must be at most {MAX_NAME_LENGTH} characters")
        )
    return issues


def validate_repository_name(value: str) -> list[ValidationIssue]:
    """Return the issues of a repository name."""
    if not value:
        return [ValidationIssue("repository_name", "is required")]
    issues: list[ValidationIssue] = []
    if len(value) > MAX_REPOSITORY_NAME_LENGTH:
        issues.append(
            ValidationIssue(
                "repository_name", f"must be at most {MAX_REPOSITORY_NAME_LENGTH} characters"
            )
        )
    invalid = _invalid_repository_characters(value)
    if invalid:
        issues.append(
            ValidationIssue(
                "repository_name",
                f"contains characters that are not allowed: {', '.join(invalid)}; "
                "use only lowercase letters, digits and hyphens",
            )
        )
    elif not _REPOSITORY_NAME.fullmatch(value):
        issues.append(ValidationIssue("repository_name", "must not start or end with a hyphen"))
    return issues


def _control_character_issues(field: str, value: str) -> list[ValidationIssue]:
    if any(unicodedata.category(character) in _FORBIDDEN_CATEGORIES for character in value):
        return [ValidationIssue(field, "must not contain control characters or line breaks")]
    return []


def _invalid_repository_characters(value: str) -> list[str]:
    seen: list[str] = []
    for character in value:
        if not _REPOSITORY_NAME_CHARACTER.fullmatch(character) and repr(character) not in seen:
            seen.append(repr(character))
    return seen[:MAX_REPORTED_CHARACTERS]
