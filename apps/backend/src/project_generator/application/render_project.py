"""Use case: render a validated project spec into a directory."""

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from project_generator.application.ports import TemplateEngine, TemplateSource, TreeWriter
from project_generator.domain.owner import ensure_owner
from project_generator.domain.project_spec import ProjectSpec
from project_generator.domain.render_context import (
    build_application_contexts,
    build_render_context,
)
from project_generator.domain.render_plan import PlannedFile, RenderMode, build_render_plan
from project_generator.domain.rendered_tree import RenderedFile, RenderedTree


@dataclass(frozen=True)
class RenderResult:
    """What a successful rendering reports to its caller."""

    files: tuple[str, ...]
    template_digest: str
    tree_digest: str


class RenderProject:
    """Validates, plans and renders everything in memory, and writes only at the end."""

    def __init__(self, engine: TemplateEngine, source: TemplateSource, writer: TreeWriter) -> None:
        self._engine = engine
        self._source = source
        self._writer = writer

    def execute(
        self, spec: ProjectSpec | Mapping[str, object], owner: object, target: Path
    ) -> RenderResult:
        """Render the project into `target`; nothing is written if any step fails."""
        valid_spec = spec if isinstance(spec, ProjectSpec) else ProjectSpec.from_raw(spec)
        valid_owner = ensure_owner(owner)
        plan = build_render_plan(valid_spec, self._source.list_templates())
        context = build_render_context(valid_spec, valid_owner)
        applications = build_application_contexts(valid_spec)
        templates = {file.source: self._source.read(file.source) for file in plan}
        tree = RenderedTree(
            files={
                file.destination: self._render_file(
                    file, templates[file.source], _values_for(file, context, applications)
                )
                for file in plan
            }
        )
        self._writer.write(tree, target)
        return RenderResult(
            files=tuple(sorted(tree.files)),
            template_digest=_template_digest(templates),
            tree_digest=tree.digest(),
        )

    def _render_file(
        self, file: PlannedFile, content: bytes, context: Mapping[str, object]
    ) -> RenderedFile:
        if file.mode is RenderMode.VERBATIM:
            return RenderedFile(content=content, executable=file.executable)
        text = self._engine.render(content.decode("utf-8"), context)
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        return RenderedFile(content=normalized.encode("utf-8"), executable=file.executable)


def _values_for(
    file: PlannedFile,
    context: Mapping[str, object],
    applications: Mapping[str, Mapping[str, object]],
) -> Mapping[str, object]:
    """Add `application` for a file that belongs to one application directory."""
    if file.application_kind is None:
        return context
    return {**context, "application": applications[file.application_kind]}


def _template_digest(templates: Mapping[str, bytes]) -> str:
    hasher = hashlib.sha256()
    for path in sorted(templates):
        hasher.update(path.encode("utf-8") + b"\0" + hashlib.sha256(templates[path]).digest())
    return hasher.hexdigest()
