from collections.abc import Callable
from pathlib import Path

import pytest

from sdd.application.render_project import RenderProject, RenderResult
from sdd.infrastructure.filesystem_template_source import FilesystemTemplateSource
from sdd.infrastructure.filesystem_tree_writer import FilesystemTreeWriter
from sdd.infrastructure.jinja_engine import JinjaTemplateEngine
from tests.unit.factories import raw_spec

OWNER = "acme-platform"
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
TEMPLATES_ROOT = REPOSITORY_ROOT / "templates"

Render = Callable[..., RenderResult]


def build_use_case(templates: Path = TEMPLATES_ROOT) -> RenderProject:
    return RenderProject(
        JinjaTemplateEngine(), FilesystemTemplateSource(templates), FilesystemTreeWriter()
    )


def read_tree(directory: Path) -> dict[str, bytes]:
    return {
        path.relative_to(directory).as_posix(): path.read_bytes()
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


@pytest.fixture
def render(tmp_path: Path) -> Render:
    """Render a raw spec into a fresh directory and return the result."""
    counter = iter(range(1000))

    def _render(target: Path | None = None, **overrides: object) -> RenderResult:
        destination = target or tmp_path / f"out-{next(counter)}"
        return build_use_case().execute(raw_spec(**overrides), OWNER, destination)

    return _render
