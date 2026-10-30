"""Ports owned by the application layer; adapters live in infrastructure."""

from collections.abc import Mapping
from pathlib import Path
from typing import Protocol

from project_generator.domain.rendered_tree import RenderedTree


class TemplateSource(Protocol):
    def list_templates(self) -> tuple[str, ...]:
        """Relative POSIX paths of every template file."""
        ...

    def read(self, path: str) -> bytes:
        """Content of one template file."""
        ...


class TemplateEngine(Protocol):
    def render(self, source: str, context: Mapping[str, object]) -> str:
        """Render template text with the given values; raise TemplateRenderError on failure."""
        ...


class TreeWriter(Protocol):
    def write(self, tree: RenderedTree, target: Path) -> None:
        """Write the whole tree into an empty or missing target directory, or nothing at all."""
        ...
