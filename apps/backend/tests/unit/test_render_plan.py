import pytest

from sdd.domain.project_spec import ProjectSpec
from sdd.domain.render_plan import (
    RenderMode,
    RenderPlanError,
    build_render_plan,
)
from tests.unit.factories import raw_spec
from tests.unit.fakes import standard_templates


def destinations(spec: ProjectSpec, templates: dict[str, bytes] | None = None) -> list[str]:
    plan = build_render_plan(spec, (templates or standard_templates()).keys())
    return [file.destination for file in plan]


def test_fullstack_plan_has_the_root_files_and_both_applications() -> None:
    result = destinations(ProjectSpec.from_raw(raw_spec()))

    assert result == [
        ".github/CODEOWNERS",
        ".github/ISSUE_TEMPLATE/bug.yml",
        "AGENTS.md",
        "CLAUDE.md",
        "README.md",
        "apps/backend/README.md",
        "apps/frontend/README.md",
        "harness/guides/development.md",
        "openspec/specs/.gitkeep",
    ]


def test_backend_only_plan_has_only_the_backend_application() -> None:
    spec = ProjectSpec.from_raw(raw_spec(typology="backend", technologies={"backend": "python"}))

    result = destinations(spec)

    assert "apps/backend/README.md" in result
    assert "apps/frontend/README.md" not in result


def test_frontend_only_plan_has_only_the_frontend_application() -> None:
    spec = ProjectSpec.from_raw(
        raw_spec(typology="frontend", technologies={"frontend": "react-typescript"})
    )

    result = destinations(spec)

    assert "apps/frontend/README.md" in result
    assert "apps/backend/README.md" not in result


def test_rulesets_are_not_part_of_the_repository_tree() -> None:
    result = destinations(ProjectSpec.from_raw(raw_spec()))

    assert not any("ruleset" in destination for destination in result)


def test_only_the_selected_agent_entry_file_is_planned() -> None:
    result = destinations(ProjectSpec.from_raw(raw_spec()))

    assert "CLAUDE.md" in result
    assert "OTHER.md" not in result


def test_template_suffix_selects_render_mode_and_is_removed() -> None:
    plan = build_render_plan(ProjectSpec.from_raw(raw_spec()), standard_templates().keys())
    by_destination = {file.destination: file for file in plan}

    assert by_destination["README.md"].mode is RenderMode.RENDER
    assert by_destination["README.md"].source == "project/README.md.tmpl"
    assert by_destination["AGENTS.md"].mode is RenderMode.VERBATIM


@pytest.mark.parametrize(
    "source",
    ["project/../escape.txt", "project//double.txt", "project/./dot.txt", "project/a\\b.txt"],
)
def test_plan_that_escapes_the_target_is_refused(source: str) -> None:
    templates = standard_templates() | {source: b"x"}

    with pytest.raises(RenderPlanError, match="not a safe relative path"):
        build_render_plan(ProjectSpec.from_raw(raw_spec()), templates.keys())


def test_absolute_destination_is_refused() -> None:
    templates = standard_templates() | {"project//etc/passwd": b"x"}

    with pytest.raises(RenderPlanError):
        build_render_plan(ProjectSpec.from_raw(raw_spec()), templates.keys())


def test_destinations_that_differ_only_in_case_are_refused() -> None:
    templates = standard_templates() | {"project/readme.md": b"x"}

    with pytest.raises(RenderPlanError, match="more than once"):
        build_render_plan(ProjectSpec.from_raw(raw_spec()), templates.keys())


def test_template_without_destination_is_refused() -> None:
    templates = standard_templates() | {"unknown/file.txt": b"x"}

    with pytest.raises(RenderPlanError, match="has no destination"):
        build_render_plan(ProjectSpec.from_raw(raw_spec()), templates.keys())


def test_missing_agent_entry_template_is_refused() -> None:
    templates = standard_templates()
    del templates["agents/claude/CLAUDE.md"]

    with pytest.raises(RenderPlanError, match="agent entry file"):
        build_render_plan(ProjectSpec.from_raw(raw_spec()), templates.keys())
