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


def test_workflows_are_copied_verbatim_into_the_github_directory() -> None:
    templates = {**standard_templates(), "github/workflows/repository.yml": b"name: Repository\n"}
    plan = build_render_plan(ProjectSpec.from_raw(raw_spec()), templates)

    workflow = next(file for file in plan if file.source == "github/workflows/repository.yml")
    assert workflow.destination == ".github/workflows/repository.yml"
    assert workflow.mode is RenderMode.VERBATIM


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


def technology_templates() -> dict[str, bytes]:
    return standard_templates() | {
        "apps/backend/python/pyproject.toml": b"python",
        "apps/backend/python/src/app/__init__.py": b"",
        "apps/backend/csharp/Backend.csproj": b"csharp",
        "apps/frontend/react-typescript/package.json": b"{}",
    }


def test_only_the_files_of_the_selected_technology_are_planned() -> None:
    result = destinations(ProjectSpec.from_raw(raw_spec()), technology_templates())

    assert "apps/backend/pyproject.toml" in result
    assert "apps/backend/src/app/__init__.py" in result
    assert "apps/frontend/package.json" in result
    assert not any(
        "csharp" in destination or "Backend.csproj" in destination for destination in result
    )


def test_the_technology_directory_is_dropped_from_the_destination() -> None:
    result = destinations(ProjectSpec.from_raw(raw_spec()), technology_templates())

    assert not any("/python/" in destination for destination in result)
    assert not any("/react-typescript/" in destination for destination in result)


def test_files_shared_by_every_technology_are_planned_for_each_one() -> None:
    for technology in ("python", "csharp"):
        spec = ProjectSpec.from_raw(
            raw_spec(typology="backend", technologies={"backend": technology})
        )

        assert "apps/backend/README.md" in destinations(spec, technology_templates())


def test_kinds_select_their_technology_independently() -> None:
    spec = ProjectSpec.from_raw(
        raw_spec(technologies={"backend": "csharp", "frontend": "react-typescript"})
    )

    result = destinations(spec, technology_templates())

    assert "apps/backend/Backend.csproj" in result
    assert "apps/backend/pyproject.toml" not in result
    assert "apps/frontend/package.json" in result


def test_technology_without_files_plans_only_the_shared_files() -> None:
    spec = ProjectSpec.from_raw(raw_spec(typology="backend", technologies={"backend": "csharp"}))
    templates = standard_templates() | {"apps/backend/python/pyproject.toml": b"python"}

    result = destinations(spec, templates)

    assert [d for d in result if d.startswith("apps/")] == ["apps/backend/README.md"]


def test_technology_directory_of_a_kind_outside_the_typology_is_skipped() -> None:
    spec = ProjectSpec.from_raw(raw_spec(typology="backend", technologies={"backend": "python"}))

    result = destinations(spec, technology_templates())

    assert "apps/frontend/package.json" not in result


def test_shared_and_technology_file_with_the_same_destination_are_refused() -> None:
    templates = technology_templates() | {"apps/backend/pyproject.toml": b"shared"}

    with pytest.raises(RenderPlanError, match="more than once"):
        build_render_plan(ProjectSpec.from_raw(raw_spec()), templates.keys())


def test_a_deeper_folder_named_like_a_technology_is_not_a_technology_directory() -> None:
    templates = technology_templates() | {"apps/backend/python/docs/csharp/notes.md": b"x"}

    result = destinations(ProjectSpec.from_raw(raw_spec()), templates)

    assert "apps/backend/docs/csharp/notes.md" in result


def project_type_templates() -> dict[str, bytes]:
    return standard_templates() | {
        "apps/backend/csharp/shared.props": b"shared",
        "apps/backend/csharp/api/Api.csproj": b"api",
        "apps/backend/csharp/api/src/library/Notes.cs": b"deeper",
        "apps/backend/csharp/console/Console.csproj": b"console",
        "apps/backend/csharp/library/Library.csproj": b"library",
        "apps/backend/python/pyproject.toml": b"python",
        "apps/backend/python/library/notes.py": b"a folder named like a type",
    }


def csharp_spec(**overrides: object) -> ProjectSpec:
    return ProjectSpec.from_raw(
        raw_spec(typology="backend", technologies={"backend": "csharp"}, **overrides)
    )


@pytest.mark.parametrize(
    ("project_type", "expected", "others"),
    [
        ("api", "Api.csproj", ["Console.csproj", "Library.csproj"]),
        ("console", "Console.csproj", ["Api.csproj", "Library.csproj"]),
        ("library", "Library.csproj", ["Api.csproj", "Console.csproj"]),
    ],
)
def test_only_the_files_of_the_selected_project_type_are_planned(
    project_type: str, expected: str, others: list[str]
) -> None:
    result = destinations(csharp_spec(project_type=project_type), project_type_templates())

    assert f"apps/backend/{expected}" in result
    assert not [name for name in others if f"apps/backend/{name}" in result]
    assert not [d for d in result if d.split("/")[2:3] in (["api"], ["console"], ["library"])]


def test_omitted_project_type_plans_the_api_files() -> None:
    result = destinations(csharp_spec(), project_type_templates())

    assert "apps/backend/Api.csproj" in result
    assert "apps/backend/Library.csproj" not in result


@pytest.mark.parametrize("project_type", ["api", "console", "library"])
def test_files_shared_by_every_project_type_are_planned_for_each_one(project_type: str) -> None:
    result = destinations(csharp_spec(project_type=project_type), project_type_templates())

    assert "apps/backend/shared.props" in result


@pytest.mark.usefixtures("python_without_project_types")
def test_technology_without_project_types_keeps_folders_named_like_a_type() -> None:
    spec = ProjectSpec.from_raw(raw_spec(typology="backend", technologies={"backend": "python"}))

    result = destinations(spec, project_type_templates())

    assert "apps/backend/library/notes.py" in result
    assert "apps/backend/pyproject.toml" in result


def test_deeper_folder_named_like_a_project_type_is_kept() -> None:
    result = destinations(csharp_spec(project_type="api"), project_type_templates())

    assert "apps/backend/src/library/Notes.cs" in result


def test_shared_and_project_type_file_with_the_same_destination_are_refused() -> None:
    templates = project_type_templates() | {"apps/backend/csharp/Api.csproj": b"shared"}

    with pytest.raises(RenderPlanError, match="more than once"):
        build_render_plan(csharp_spec(project_type="api"), templates.keys())


def test_project_type_directory_of_a_kind_outside_the_typology_is_skipped() -> None:
    templates = project_type_templates() | {
        "apps/frontend/react-typescript/api/App.tsx": b"frontend",
    }

    result = destinations(csharp_spec(project_type="api"), templates)

    assert not [d for d in result if d.startswith("apps/frontend/") and d.endswith("App.tsx")]


@pytest.mark.parametrize(("project_type", "other"), [("console", "library"), ("library", "api")])
def test_python_files_are_selected_by_project_type(project_type: str, other: str) -> None:
    spec = ProjectSpec.from_raw(
        raw_spec(typology="backend", technologies={"backend": "python"}, project_type=project_type)
    )
    templates = standard_templates() | {
        f"apps/backend/python/{project_type}/pyproject.toml": b"selected",
        f"apps/backend/python/{other}/pyproject.toml": b"other",
    }

    plan = build_render_plan(spec, templates.keys())

    sources = [file.source for file in plan if file.destination == "apps/backend/pyproject.toml"]
    assert sources == [f"apps/backend/python/{project_type}/pyproject.toml"]
