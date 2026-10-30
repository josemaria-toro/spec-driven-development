"""Fake ports for unit tests."""

from collections.abc import Mapping
from pathlib import Path

from project_generator.application.errors import TemplateRenderError
from project_generator.domain.rendered_tree import RenderedTree


class FakeTemplateSource:
    def __init__(self, files: Mapping[str, bytes]) -> None:
        self.files = dict(files)

    def list_templates(self) -> tuple[str, ...]:
        return tuple(self.files)

    def read(self, path: str) -> bytes:
        return self.files[path]


class UppercaseEngine:
    """Replaces `<<owner>>` and fails on the marker `FAIL`; enough to test the use case."""

    def __init__(self) -> None:
        self.rendered: list[str] = []

    def render(self, source: str, context: Mapping[str, object]) -> str:
        if "FAIL" in source:
            raise TemplateRenderError("boom")
        self.rendered.append(source)
        return source.replace("<<owner>>", str(context["owner"]))


class RecordingWriter:
    def __init__(self) -> None:
        self.calls: list[tuple[RenderedTree, Path]] = []

    def write(self, tree: RenderedTree, target: Path) -> None:
        self.calls.append((tree, target))


def standard_templates() -> dict[str, bytes]:
    """A small template set that covers every mapping rule."""
    return {
        "agents/claude/CLAUDE.md": b"@AGENTS.md\n",
        "agents/other/OTHER.md": b"other agent\n",
        "apps/backend/README.md.tmpl": b"backend\n",
        "apps/frontend/README.md.tmpl": b"frontend\n",
        "github/CODEOWNERS.tmpl": b"* @<<owner>>\n",
        "github/issues/bug.yml": b"name: Bug\n",
        "github/rulesets/ruleset.json": b"{}\n",
        "harness/AGENTS.md": b"# AGENTS\n",
        "harness/guides/development.md": b"# Development\n",
        "project/README.md.tmpl": b"readme\n",
        "project/openspec/specs/.gitkeep": b"",
    }
