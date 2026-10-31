import subprocess
import sys
from pathlib import Path

import pytest

from tests.integration.conftest import (
    BACKEND_PYTHON_FILES,
    FRONTEND_REACT_FILES,
    Render,
    read_tree,
)

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


def skeleton_files(target: Path) -> dict[str, bytes]:
    return {
        path: content
        for path, content in read_tree(target).items()
        if path.startswith("apps/") and path.rsplit("/", 1)[-1] != "README.md"
    }


def test_different_projects_get_byte_identical_skeletons(tmp_path: Path, render: Render) -> None:
    render(tmp_path / "first")
    render(
        tmp_path / "second",
        description="Something else entirely",
        project_name="Billing",
        repository_name="billing-service",
    )

    first, second = skeleton_files(tmp_path / "first"), skeleton_files(tmp_path / "second")

    assert first
    assert first == second


def test_project_values_do_not_reach_any_skeleton_file(tmp_path: Path, render: Render) -> None:
    values = ['{{ 7 * 7 }} "quoted"', "<< 7 * 7 >>", "Zebra Platform", "zebra-platform"]
    render(
        tmp_path / "out",
        description=values[0] + values[1],
        project_name=values[2],
        repository_name=values[3],
    )

    for path, content in skeleton_files(tmp_path / "out").items():
        text = content.decode()
        assert not [value for value in values if value in text], path


def test_technology_without_a_skeleton_renders_only_the_kind_readme(
    tmp_path: Path, render: Render
) -> None:
    render(tmp_path / "out", typology="backend", technologies={"backend": "csharp"})

    assert application_files(tmp_path / "out", "backend") == {"apps/backend/README.md"}


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
