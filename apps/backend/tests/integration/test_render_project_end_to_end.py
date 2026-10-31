import json
import os
import shutil
import socket
import subprocess
from pathlib import Path

import pytest
import yaml

from tests.integration.conftest import (
    OWNER,
    REPOSITORY_ROOT,
    TEMPLATES_ROOT,
    Render,
    build_use_case,
    read_tree,
)
from tests.unit.factories import raw_spec

pytestmark = pytest.mark.integration

ROOT_FILES = {
    ".github/CODEOWNERS",
    ".github/ISSUE_TEMPLATE/bug.yml",
    ".github/ISSUE_TEMPLATE/change.yml",
    ".github/ISSUE_TEMPLATE/feature.yml",
    ".github/dependabot.yml",
    ".github/workflows/repository.yml",
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "openspec/changes/.gitkeep",
    "openspec/config.yaml",
    "openspec/specs/.gitkeep",
}
HOSTILE_DESCRIPTION = 'x {{ 7 * 7 }} << 7 * 7 >> "q": a: b # c *d* [e](f) <g> 1. h \\ i \U0001f600'
HARNESS_FILES = {
    path.relative_to(TEMPLATES_ROOT).as_posix()
    for path in (TEMPLATES_ROOT / "harness").rglob("*")
    if path.is_file() and path.name != "AGENTS.md"
}


def test_fullstack_project_has_the_exact_expected_files(tmp_path: Path, render: Render) -> None:
    target = tmp_path / "fullstack"
    render(target)

    assert set(read_tree(target)) == (
        ROOT_FILES | HARNESS_FILES | {"apps/backend/README.md", "apps/frontend/README.md"}
    )


def test_backend_only_project_has_only_the_backend_application(
    tmp_path: Path, render: Render
) -> None:
    target = tmp_path / "backend"
    render(target, typology="backend", technologies={"backend": "csharp"})

    files = set(read_tree(target))
    assert files == ROOT_FILES | HARNESS_FILES | {"apps/backend/README.md"}
    assert "csharp" in (target / "apps/backend/README.md").read_text()


def test_frontend_only_project_has_only_the_frontend_application(
    tmp_path: Path, render: Render
) -> None:
    target = tmp_path / "frontend"
    render(target, typology="frontend", technologies={"frontend": "react-typescript"})

    assert set(read_tree(target)) == ROOT_FILES | HARNESS_FILES | {"apps/frontend/README.md"}


def test_rulesets_and_templates_suffixes_are_not_in_the_output(
    tmp_path: Path, render: Render
) -> None:
    target = tmp_path / "out"
    render(target)

    assert not [p for p in read_tree(target) if "ruleset" in p or p.endswith(".tmpl")]


def test_claude_entry_file_imports_agents_and_the_agents_file_is_at_the_root(
    tmp_path: Path, render: Render
) -> None:
    target = tmp_path / "out"
    render(target)

    assert "@AGENTS.md" in (target / "CLAUDE.md").read_text()
    assert "harness/guides/guardrails.md" in (target / "AGENTS.md").read_text()


def test_ownership_file_lists_the_owner(tmp_path: Path, render: Render) -> None:
    target = tmp_path / "out"
    render(target)

    codeowners = (target / ".github/CODEOWNERS").read_text()
    assert f"/harness/               @{OWNER}" in codeowners
    assert f"/openspec/              @{OWNER}" in codeowners
    assert "@josemaria-toro" not in codeowners


def test_dependabot_has_one_block_per_application(tmp_path: Path, render: Render) -> None:
    target = tmp_path / "out"
    render(target)

    updates = yaml.safe_load((target / ".github/dependabot.yml").read_text())["updates"]
    assert [(u["package-ecosystem"], u["directory"]) for u in updates] == [
        ("uv", "/apps/backend"),
        ("npm", "/apps/frontend"),
        ("github-actions", "/"),
    ]


def test_two_runs_produce_identical_trees_and_digests(tmp_path: Path, render: Render) -> None:
    first_target, second_target = tmp_path / "first", tmp_path / "second"

    first = render(first_target)
    second = render(second_target)

    assert read_tree(first_target) == read_tree(second_target)
    assert first.tree_digest == second.tree_digest
    assert first.template_digest == second.template_digest
    assert first.files == second.files


def test_output_does_not_depend_on_the_working_directory(
    tmp_path: Path, render: Render, monkeypatch: pytest.MonkeyPatch
) -> None:
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    first_target, second_target = tmp_path / "first", tmp_path / "second"
    render(first_target)
    monkeypatch.chdir(elsewhere)

    render(second_target)

    assert read_tree(first_target) == read_tree(second_target)


def test_no_generated_file_contains_a_host_path_or_a_crlf(tmp_path: Path, render: Render) -> None:
    target = tmp_path / "out"
    render(target)

    host_markers = [str(tmp_path).encode(), str(REPOSITORY_ROOT).encode(), b"/home/"]
    for path, content in read_tree(target).items():
        assert b"\r" not in content, path
        assert not [m for m in host_markers if m in content], path


def test_hostile_values_are_kept_literal_and_structured_files_stay_valid(
    tmp_path: Path, render: Render
) -> None:
    target = tmp_path / "out"
    render(target, description=HOSTILE_DESCRIPTION, project_name="Name: {{ 7 * 7 }} *x*")

    tree = read_tree(target)
    for path, content in tree.items():
        if path.endswith((".yml", ".yaml")):
            yaml.safe_load(content)
        if path.endswith(".json"):
            json.loads(content)
    config = yaml.safe_load(tree["openspec/config.yaml"])
    assert f"Description: {HOSTILE_DESCRIPTION}" in config["context"]
    assert "Project: Name: {{ 7 * 7 }} *x*" in config["context"]
    readme = tree["README.md"].decode()
    assert "49" not in readme
    assert r"\{\{ 7 \* 7 \}\}" in readme
    assert r"\*x\*" in readme


def test_rendering_needs_no_network_and_no_processes(
    tmp_path: Path, render: Render, monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("external effect attempted")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(os, "system", forbidden)
    monkeypatch.setattr(os, "popen", forbidden)

    result = render(tmp_path / "out")

    assert result.files


def test_changed_template_changes_both_digests(tmp_path: Path, render: Render) -> None:
    templates = tmp_path / "templates"
    shutil.copytree(TEMPLATES_ROOT, templates)
    original = build_use_case(templates).execute(raw_spec(), OWNER, tmp_path / "before")
    readme = templates / "project" / "README.md.tmpl"
    readme.write_text(readme.read_text() + "\nExtra line.\n")

    changed = build_use_case(templates).execute(raw_spec(), OWNER, tmp_path / "after")

    assert changed.template_digest != original.template_digest
    assert changed.tree_digest != original.tree_digest


def test_invalid_spec_is_not_rendered_and_nothing_is_written(tmp_path: Path) -> None:
    from sdd.domain.errors import ValidationFailedError

    target = tmp_path / "out"

    with pytest.raises(ValidationFailedError):
        build_use_case().execute(raw_spec(repository_name="../x"), OWNER, target)

    assert not target.exists()


@pytest.mark.parametrize(
    ("typology", "technologies", "expected"),
    [
        ("backend", {"backend": "python"}, [("uv", "/apps/backend")]),
        ("backend", {"backend": "csharp"}, [("nuget", "/apps/backend")]),
        ("frontend", {"frontend": "react-typescript"}, [("npm", "/apps/frontend")]),
    ],
)
def test_dependabot_is_valid_yaml_for_every_typology(
    tmp_path: Path,
    render: Render,
    typology: str,
    technologies: dict[str, str],
    expected: list[tuple[str, str]],
) -> None:
    target = tmp_path / "out"
    render(target, typology=typology, technologies=technologies)

    updates = yaml.safe_load((target / ".github/dependabot.yml").read_text())["updates"]
    assert [(u["package-ecosystem"], u["directory"]) for u in updates] == [
        *expected,
        ("github-actions", "/"),
    ]


def test_root_documentation_shows_the_project_name_and_description(
    tmp_path: Path, render: Render
) -> None:
    target = tmp_path / "out"
    render(target)

    readme = (target / "README.md").read_text()
    assert "# Orders Platform" in readme
    assert "Order management platform" in readme
    assert "orders-platform" in readme
