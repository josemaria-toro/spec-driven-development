from types import MappingProxyType

import pytest

from sdd.domain import project_spec, render_plan
from sdd.domain.catalogue import TECHNOLOGY_PROJECT_TYPES, Technology


@pytest.fixture
def python_without_project_types(monkeypatch: pytest.MonkeyPatch) -> None:
    """Pretend that Python offers no project types, to test a technology that offers none.

    Every technology of the catalogue offers project types, so the rule is exercised with a
    catalogue where one of them does not.
    """
    reduced = MappingProxyType(
        {
            technology: types
            for technology, types in TECHNOLOGY_PROJECT_TYPES.items()
            if technology is not Technology.PYTHON
        }
    )
    monkeypatch.setattr(project_spec, "TECHNOLOGY_PROJECT_TYPES", reduced)
    monkeypatch.setattr(render_plan, "_TYPED_TECHNOLOGIES", frozenset(t.value for t in reduced))
