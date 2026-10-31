"""Validation errors shared by the domain."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationIssue:
    """One invalid field and a readable reason."""

    field: str
    reason: str


class ValidationFailedError(Exception):
    """Raised when one or more fields are invalid; carries every issue found."""

    def __init__(self, issues: list[ValidationIssue]) -> None:
        self.issues = tuple(issues)
        super().__init__("; ".join(f"{issue.field}: {issue.reason}" for issue in self.issues))
