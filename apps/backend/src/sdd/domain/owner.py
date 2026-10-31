"""The repository owner: a GitHub account name."""

import re

from sdd.domain.errors import ValidationFailedError, ValidationIssue

MAX_OWNER_LENGTH = 39

_OWNER = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9]))*")


def ensure_owner(value: object) -> str:
    """Return the owner when it is a valid GitHub account name, else raise."""
    if not isinstance(value, str) or not value:
        raise ValidationFailedError([ValidationIssue("owner", "is required")])
    if len(value) > MAX_OWNER_LENGTH or not _OWNER.fullmatch(value):
        raise ValidationFailedError(
            [
                ValidationIssue(
                    "owner",
                    f"must be a GitHub account name: 1 to {MAX_OWNER_LENGTH} letters, digits or "
                    "single hyphens, not starting or ending with a hyphen",
                )
            ]
        )
    return value
