import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tests.integration.conftest import (
    BACKEND_CSHARP_FILES,
    BACKEND_PYTHON_FILES,
    FRONTEND_REACT_FILES,
    OWNER,
    TEMPLATES_ROOT,
    Render,
    build_use_case,
    read_tree,
)
from tests.unit.factories import raw_spec

pytestmark = pytest.mark.integration

LINT_IMPORTS = Path(sys.executable).parent / "lint-imports"


def application_files(target: Path, kind: str) -> set[str]:
    return {path for path in read_tree(target) if path.startswith(f"apps/{kind}/")}


def run_layer_check(backend: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        [str(LINT_IMPORTS)],
        cwd=backend,
        env={"PATH": "/usr/bin:/bin", "PYTHONPATH": "src"},
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    ("typology", "technologies"),
    [
        ("backend", {"backend": "python"}),
        ("fullstack", {"backend": "python", "frontend": "react-typescript"}),
    ],
)
def test_python_backend_gets_exactly_its_skeleton_files(
    tmp_path: Path, render: Render, typology: str, technologies: dict[str, str]
) -> None:
    render(tmp_path / "out", typology=typology, technologies=technologies)

    assert application_files(tmp_path / "out", "backend") == BACKEND_PYTHON_FILES


@pytest.mark.parametrize(
    ("typology", "technologies"),
    [
        ("frontend", {"frontend": "react-typescript"}),
        ("fullstack", {"backend": "python", "frontend": "react-typescript"}),
    ],
)
def test_react_frontend_gets_exactly_its_skeleton_files(
    tmp_path: Path, render: Render, typology: str, technologies: dict[str, str]
) -> None:
    render(tmp_path / "out", typology=typology, technologies=technologies)

    assert application_files(tmp_path / "out", "frontend") == FRONTEND_REACT_FILES


@pytest.mark.parametrize("project_type", sorted(BACKEND_CSHARP_FILES))
@pytest.mark.parametrize("typology", ["backend", "fullstack"])
def test_csharp_backend_gets_exactly_the_files_of_its_project_type(
    tmp_path: Path, render: Render, typology: str, project_type: str
) -> None:
    technologies = {"backend": "csharp", "frontend": "react-typescript"}
    if typology == "backend":
        del technologies["frontend"]
    render(
        tmp_path / "out", typology=typology, technologies=technologies, project_type=project_type
    )

    assert application_files(tmp_path / "out", "backend") == BACKEND_CSHARP_FILES[project_type]


def test_rendered_python_backend_passes_its_layer_rules(tmp_path: Path, render: Render) -> None:
    render(tmp_path / "out", typology="backend", technologies={"backend": "python"})

    result = run_layer_check(tmp_path / "out/apps/backend")

    assert result.returncode == 0, result.stdout


@pytest.mark.parametrize(
    ("import_line", "message"),
    [
        ("from app.infrastructure import adapters", "app.domain is not allowed to import"),
        ("import fastapi", "app.domain is not allowed to import fastapi"),
    ],
)
def test_forbidden_import_in_the_rendered_python_backend_fails_the_layer_check(
    tmp_path: Path, render: Render, import_line: str, message: str
) -> None:
    render(tmp_path / "out", typology="backend", technologies={"backend": "python"})
    backend = tmp_path / "out/apps/backend"
    domain_module = backend / "src/app/domain/greeting.py"
    domain_module.write_text(f"{domain_module.read_text()}\n{import_line}\n")

    result = run_layer_check(backend)

    assert result.returncode != 0
    assert message in result.stdout


BACKENDS = [
    ("python", None),
    *[("csharp", project_type) for project_type in sorted(BACKEND_CSHARP_FILES)],
]


def backend_overrides(backend: str, project_type: str | None) -> dict[str, object]:
    overrides: dict[str, object] = {
        "technologies": {"backend": backend, "frontend": "react-typescript"}
    }
    if project_type is not None:
        overrides["project_type"] = project_type
    return overrides


def skeleton_files(target: Path) -> dict[str, bytes]:
    return {
        path: content
        for path, content in read_tree(target).items()
        if path.startswith("apps/") and path.rsplit("/", 1)[-1] != "README.md"
    }


@pytest.mark.parametrize(("backend", "project_type"), BACKENDS)
def test_different_projects_get_byte_identical_skeletons(
    tmp_path: Path, render: Render, backend: str, project_type: str | None
) -> None:
    overrides = backend_overrides(backend, project_type)
    render(tmp_path / "first", **overrides)
    render(
        tmp_path / "second",
        **overrides,
        description="Something else entirely",
        project_name="Billing",
        repository_name="billing-service",
    )

    first, second = skeleton_files(tmp_path / "first"), skeleton_files(tmp_path / "second")

    assert first
    assert first == second


@pytest.mark.parametrize(("backend", "project_type"), BACKENDS)
def test_project_values_do_not_reach_any_skeleton_file(
    tmp_path: Path, render: Render, backend: str, project_type: str | None
) -> None:
    values = ['{{ 7 * 7 }} "quoted"', "<< 7 * 7 >>", "Zebra Platform", "zebra-platform"]
    render(
        tmp_path / "out",
        **backend_overrides(backend, project_type),
        description=values[0] + values[1],
        project_name=values[2],
        repository_name=values[3],
    )

    for path, content in skeleton_files(tmp_path / "out").items():
        text = content.decode()
        assert not [value for value in values if value in text], path


def test_technology_without_a_skeleton_renders_only_the_kind_readme(tmp_path: Path) -> None:
    templates = tmp_path / "templates"
    shutil.copytree(TEMPLATES_ROOT, templates)
    shutil.rmtree(templates / "apps/backend/csharp")
    target = tmp_path / "out"

    build_use_case(templates).execute(
        raw_spec(typology="backend", technologies={"backend": "csharp"}), OWNER, target
    )

    assert application_files(target, "backend") == {"apps/backend/README.md"}


@pytest.mark.parametrize("project_type", sorted(BACKEND_CSHARP_FILES))
def test_every_csharp_project_type_renders_the_readme_and_its_skeleton(
    tmp_path: Path, render: Render, project_type: str
) -> None:
    render(
        tmp_path / "out",
        typology="backend",
        technologies={"backend": "csharp"},
        project_type=project_type,
    )

    files = application_files(tmp_path / "out", "backend")
    assert "apps/backend/README.md" in files
    assert len(files) > 1


@pytest.mark.parametrize(
    ("typology", "technologies", "kinds"),
    [
        ("backend", {"backend": "python"}, ["backend"]),
        ("frontend", {"frontend": "react-typescript"}, ["frontend"]),
        (
            "fullstack",
            {"backend": "python", "frontend": "react-typescript"},
            ["backend", "frontend"],
        ),
    ],
)
def test_every_typology_renders_the_readme_and_the_skeleton_of_each_application(
    tmp_path: Path, render: Render, typology: str, technologies: dict[str, str], kinds: list[str]
) -> None:
    render(tmp_path / "out", typology=typology, technologies=technologies)

    for kind in kinds:
        files = application_files(tmp_path / "out", kind)
        assert f"apps/{kind}/README.md" in files
        assert len(files) > 1


@pytest.mark.parametrize("project_type", sorted(BACKEND_CSHARP_FILES))
def test_readme_of_a_csharp_backend_states_its_project_type(
    tmp_path: Path, render: Render, project_type: str
) -> None:
    render(
        tmp_path / "out",
        typology="backend",
        technologies={"backend": "csharp"},
        project_type=project_type,
    )

    readme = (tmp_path / "out/apps/backend/README.md").read_text()
    assert f"Project type: {project_type}\n" in readme


def test_readme_of_a_backend_without_project_types_has_no_project_type_line(
    tmp_path: Path, render: Render
) -> None:
    render(tmp_path / "out", typology="backend", technologies={"backend": "python"})

    assert "Project type" not in (tmp_path / "out/apps/backend/README.md").read_text()


def test_omitted_project_type_renders_the_api_files(tmp_path: Path, render: Render) -> None:
    render(tmp_path / "out", typology="backend", technologies={"backend": "csharp"})

    assert application_files(tmp_path / "out", "backend") == BACKEND_CSHARP_FILES["api"]
