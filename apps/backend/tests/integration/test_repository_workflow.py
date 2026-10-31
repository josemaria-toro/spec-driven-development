import json
import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from tests.integration.conftest import TEMPLATES_ROOT, Render, read_tree

pytestmark = pytest.mark.integration

WORKFLOW = ".github/workflows/repository.yml"
WORKFLOW_TEMPLATE = TEMPLATES_ROOT / "github/workflows/repository.yml"
RULESET_TEMPLATE = TEMPLATES_ROOT / "github/rulesets/ruleset-for-branches.json"
MUTABLE_REFS = {"main", "master", "latest", "head"}
ALLOWED_SECRETS = {"GITHUB_TOKEN"}
TYPOLOGIES = {
    "backend": {"typology": "backend", "technologies": {"backend": "python"}},
    "frontend": {"typology": "frontend", "technologies": {"frontend": "react-typescript"}},
    "fullstack": {},
}


def parse(text: str) -> dict[str, Any]:
    loaded = yaml.safe_load(text)
    assert isinstance(loaded, dict)
    return loaded


def triggers(workflow: dict[str, Any]) -> dict[str, Any]:
    # PyYAML reads the bare key `on` as the boolean True.
    return workflow["on"] if "on" in workflow else workflow[True]


def steps(workflow: dict[str, Any]) -> list[dict[str, Any]]:
    return [step for job in workflow["jobs"].values() for step in job["steps"]]


def required_checks() -> set[str]:
    ruleset = json.loads(RULESET_TEMPLATE.read_text(encoding="utf-8"))
    return {
        check["context"]
        for rule in ruleset["rules"]
        if rule["type"] == "required_status_checks"
        for check in rule["parameters"]["required_status_checks"]
    }


def rendered_job_names(tree: dict[str, bytes]) -> set[str]:
    return {
        job["name"]
        for path, content in tree.items()
        if path.startswith(".github/workflows/") and path.endswith(".yml")
        for job in parse(content.decode("utf-8"))["jobs"].values()
    }


def write_permission_problems(workflow: dict[str, Any]) -> list[str]:
    problems = []
    if workflow.get("permissions") != {"contents": "read"}:
        problems.append(f"workflow permissions are {workflow.get('permissions')!r}")
    for name, job in workflow["jobs"].items():
        for scope, level in (job.get("permissions") or {}).items():
            if level == "write":
                problems.append(f"job {name} requests write access to {scope}")
    return problems


def unversioned_references(text: str) -> list[str]:
    problems = []
    for step in steps(parse(text)):
        used = step.get("uses")
        if used is None:
            continue
        _, _, ref = used.partition("@")
        if not ref or ref.lower() in MUTABLE_REFS:
            problems.append(used)
    problems.extend(re.findall(r"releases/latest\S*", text))
    return problems


def unverified_downloads(text: str) -> list[str]:
    problems = []
    for step in steps(parse(text)):
        script = step.get("run", "")
        if "curl" not in script:
            continue
        check = script.find("sha256sum --check")
        execution = min(
            (i for i in (script.find("tar "), script.find("chmod ")) if i >= 0),
            default=len(script),
        )
        if not 0 <= check < execution:
            problems.append(step.get("name", script))
    return problems


def custom_secrets(text: str) -> set[str]:
    return set(re.findall(r"secrets\.(\w+)", text)) - ALLOWED_SECRETS


def checkouts_that_keep_credentials(workflow: dict[str, Any]) -> list[str]:
    return [
        step["uses"]
        for step in steps(workflow)
        if step.get("uses", "").startswith("actions/checkout@")
        and step.get("with", {}).get("persist-credentials") is not False
    ]


@pytest.fixture(scope="module")
def workflow_text() -> str:
    return WORKFLOW_TEMPLATE.read_text(encoding="utf-8")


@pytest.mark.parametrize("overrides", TYPOLOGIES.values(), ids=TYPOLOGIES.keys())
def test_workflow_is_present_for_every_typology(
    tmp_path: Path, render: Render, overrides: dict[str, Any]
) -> None:
    target = tmp_path / "out"
    render(target, **overrides)

    assert WORKFLOW in read_tree(target)


def test_workflow_triggers_on_pull_requests_pushes_and_a_weekly_schedule(
    tmp_path: Path, render: Render
) -> None:
    target = tmp_path / "out"
    render(target)

    on = triggers(parse((target / WORKFLOW).read_text()))
    assert on["pull_request"]["branches"] == ["main"]
    assert on["push"]["branches"] == ["main"]
    assert re.fullmatch(r"\d+ \d+ \* \* \d", on["schedule"][0]["cron"])


def test_workflow_does_not_depend_on_the_project_values(tmp_path: Path, render: Render) -> None:
    first, second = tmp_path / "first", tmp_path / "second"
    render(first, project_name="Alpha", description="one", repository_name="alpha")
    render(
        second,
        project_name="Beta",
        description="two",
        repository_name="beta",
        **TYPOLOGIES["backend"],
    )

    assert read_tree(first)[WORKFLOW] == read_tree(second)[WORKFLOW]
    assert read_tree(first)[WORKFLOW] == WORKFLOW_TEMPLATE.read_bytes()


def test_every_check_required_by_the_ruleset_is_a_job_of_a_rendered_workflow(
    tmp_path: Path, render: Render
) -> None:
    target = tmp_path / "out"
    render(target)

    assert required_checks()
    assert required_checks() <= rendered_job_names(read_tree(target))


def test_ruleset_check_is_missing_when_a_job_is_renamed(workflow_text: str) -> None:
    renamed = workflow_text.replace("name: Secret scan", "name: Secrets")

    names = {job["name"] for job in parse(renamed)["jobs"].values()}

    assert not required_checks() <= names


def test_no_file_of_the_rulesets_directory_is_rendered(tmp_path: Path, render: Render) -> None:
    target = tmp_path / "out"
    render(target)

    ruleset_names = {path.name for path in (TEMPLATES_ROOT / "github/rulesets").iterdir()}
    assert not {Path(path).name for path in read_tree(target)} & ruleset_names


def test_workflow_grants_only_read_access(workflow_text: str) -> None:
    assert write_permission_problems(parse(workflow_text)) == []


def test_write_access_is_detected() -> None:
    broken = parse(
        "permissions: {contents: write}\njobs: {a: {permissions: {contents: write}, steps: []}}"
    )

    assert len(write_permission_problems(broken)) == 2


def test_checkouts_do_not_persist_credentials(workflow_text: str) -> None:
    assert checkouts_that_keep_credentials(parse(workflow_text)) == []


def test_persisted_credentials_are_detected(workflow_text: str) -> None:
    broken = workflow_text.replace("persist-credentials: false", "persist-credentials: true")

    assert checkouts_that_keep_credentials(parse(broken))


def test_actions_and_tools_name_an_explicit_version(workflow_text: str) -> None:
    assert unversioned_references(workflow_text) == []
    assert "@fission-ai/openspec@" in workflow_text
    assert "${GITLEAKS_VERSION}" in workflow_text


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("actions/checkout@v7", "actions/checkout@main"),
        ("actions/setup-node@v7", "actions/setup-node"),
        ("download/v${GITLEAKS_VERSION}", "releases/latest/download"),
    ],
)
def test_unversioned_references_are_detected(workflow_text: str, old: str, new: str) -> None:
    assert unversioned_references(workflow_text.replace(old, new))


def test_downloaded_executable_is_verified_before_it_runs(workflow_text: str) -> None:
    assert "curl" in workflow_text
    assert unverified_downloads(workflow_text) == []


def test_download_without_checksum_verification_is_detected(workflow_text: str) -> None:
    broken = re.sub(r".*sha256sum --check.*\n", "", workflow_text)

    assert unverified_downloads(broken)


def test_workflow_references_no_secret_but_the_default_token(workflow_text: str) -> None:
    assert custom_secrets(workflow_text) == set()


def test_custom_secret_is_detected(workflow_text: str) -> None:
    assert custom_secrets(workflow_text + "\n# ${{ secrets.GITLEAKS_LICENSE }}") == {
        "GITLEAKS_LICENSE"
    }
