"""Builders of raw project specs for tests."""

from typing import Any


def raw_spec(**overrides: Any) -> dict[str, Any]:
    """Return a valid fullstack raw spec, with the given fields replaced."""
    data: dict[str, Any] = {
        "agent": "claude",
        "description": "Order management platform",
        "project_name": "Orders Platform",
        "repository_name": "orders-platform",
        "technologies": {"backend": "python", "frontend": "react-typescript"},
        "typology": "fullstack",
    }
    data.update(overrides)
    return data
