"""Render each typology and run the quality gates of the generated applications.

Slow and networked (installs locked dependencies, audits them), so it is not collected by
`tests/unit` or `tests/integration`: run it with `pytest tests/generated`.
"""

import hashlib
import os
import re
import shutil
import subprocess
from collections.abc import Iterator, Sequence
from pathlib import Path

import pytest

from sdd.application.render_project import RenderProject
from sdd.infrastructure.filesystem_template_source import FilesystemTemplateSource
from sdd.infrastructure.filesystem_tree_writer import FilesystemTreeWriter
from sdd.infrastructure.jinja_engine import JinjaTemplateEngine
from tests.unit.factories import raw_spec

pytestmark = pytest.mark.generated

OWNER = "acme-platform"
TEMPLATES_ROOT = Path(__file__).resolve().parents[4] / "templates"
COMMAND_TIMEOUT_SECONDS = 900
IN_CI = os.environ.get("CI") == "true"
SKIP_E2E = os.environ.get("GENERATED_SKIP_E2E") == "1"


def require_tool(name: str) -> None:
    """Fail in CI and skip elsewhere when a tool the gates need is not installed."""
    if shutil.which(name) is not None:
        return
    message = f"'{name}' is not installed"
    if IN_CI:
        pytest.fail(message)
    pytest.skip(message)


def require_dotnet_sdk() -> None:
    """Fail in CI and skip elsewhere when no .NET SDK is installed (a runtime is not enough)."""
    require_tool("dotnet")
    sdks = run(["dotnet", "--list-sdks"], Path.cwd(), check=False).stdout.strip()
    if sdks:
        return
    message = "no .NET SDK is installed"
    if IN_CI:
        pytest.fail(message)
    pytest.skip(message)


def run(
    command: Sequence[str], cwd: Path, *, check: bool = True
) -> subprocess.CompletedProcess[str]:
    env = {key: value for key, value in os.environ.items() if key != "VIRTUAL_ENV"}
    env |= {
        "DOTNET_CLI_UI_LANGUAGE": "en",
        "DOTNET_NOLOGO": "1",
        "DOTNET_CLI_TELEMETRY_OPTOUT": "1",
    }
    result = subprocess.run(  # noqa: S603
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=COMMAND_TIMEOUT_SECONDS,
        check=False,
    )
    if check:
        assert result.returncode == 0, (
            f"{' '.join(command)} failed in {cwd.name}:\n{result.stdout[-3000:]}\n"
            f"{result.stderr[-3000:]}"
        )
    return result


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def fullstack(tmp_path_factory: pytest.TempPathFactory) -> Path:
    target = tmp_path_factory.mktemp("generated") / "fullstack"
    RenderProject(
        JinjaTemplateEngine(), FilesystemTemplateSource(TEMPLATES_ROOT), FilesystemTreeWriter()
    ).execute(raw_spec(), OWNER, target)
    return target


@pytest.fixture(scope="module")
def backend(fullstack: Path) -> Iterator[Path]:
    require_tool("uv")
    directory = fullstack / "apps/backend"
    lockfile = directory / "uv.lock"
    before = digest(lockfile)
    run(["uv", "lock", "--check"], directory)
    run(["uv", "sync", "--frozen"], directory)
    yield directory
    assert digest(lockfile) == before, "uv.lock changed while the gates ran"


@pytest.fixture(scope="module")
def csharp_backend(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Path]:
    require_dotnet_sdk()
    target = tmp_path_factory.mktemp("generated") / "csharp"
    RenderProject(
        JinjaTemplateEngine(), FilesystemTemplateSource(TEMPLATES_ROOT), FilesystemTreeWriter()
    ).execute(raw_spec(typology="backend", technologies={"backend": "csharp"}), OWNER, target)
    directory = target / "apps/backend"
    lockfiles = sorted(directory.rglob("packages.lock.json"))
    before = [digest(lockfile) for lockfile in lockfiles]
    assert lockfiles, "the C# skeleton ships no lock files"
    run(["dotnet", "restore", "--locked-mode"], directory)
    yield directory
    assert [digest(lockfile) for lockfile in lockfiles] == before, "a lock file changed"


@pytest.fixture(scope="module")
def frontend(fullstack: Path) -> Iterator[Path]:
    require_tool("pnpm")
    directory = fullstack / "apps/frontend"
    lockfile = directory / "pnpm-lock.yaml"
    before = digest(lockfile)
    run(["pnpm", "install", "--frozen-lockfile"], directory)
    yield directory
    assert digest(lockfile) == before, "pnpm-lock.yaml changed while the gates ran"


@pytest.mark.parametrize(
    "command",
    [
        ["ruff", "format", "--check", "."],
        ["ruff", "check", "."],
        ["mypy", "src"],
        ["lint-imports"],
        ["pytest", "tests/unit", "--cov"],
        ["pytest", "tests/integration"],
    ],
    ids=lambda command: " ".join(command[:2]),
)
def test_backend_gate_passes(backend: Path, command: list[str]) -> None:
    run(["uv", "run", *command], backend)


def test_backend_locked_dependencies_have_no_known_vulnerability(
    backend: Path, tmp_path: Path
) -> None:
    requirements = tmp_path / "requirements.txt"
    run(
        ["uv", "export", "--frozen", "--no-hashes", "--no-emit-project", "-o", str(requirements)],
        backend,
    )

    run(["uvx", "pip-audit", "-r", str(requirements), "--no-deps", "--disable-pip"], backend)


@pytest.mark.parametrize(
    "command",
    [
        ["format", "--verify-no-changes"],
        ["build", "-warnaserror", "--no-restore"],
        ["test", "tests/App.UnitTests", "-p:CollectCoverage=true", "--no-restore"],
        ["test", "tests/App.IntegrationTests", "--no-restore"],
        ["test", "tests/App.ArchitectureTests", "--no-restore"],
    ],
    ids=lambda command: " ".join(command[:2]),
)
def test_csharp_backend_gate_passes(csharp_backend: Path, command: list[str]) -> None:
    run(["dotnet", *command], csharp_backend)


def test_csharp_backend_locked_packages_have_no_high_or_critical_vulnerability(
    csharp_backend: Path,
) -> None:
    result = run(
        ["dotnet", "list", "package", "--vulnerable", "--include-transitive"], csharp_backend
    )

    assert not re.search(r"\b(High|Critical)\b", result.stdout), result.stdout


def test_csharp_domain_using_an_http_library_fails_the_architecture_tests(
    csharp_backend: Path,
) -> None:
    leak = csharp_backend / "src/App.Domain/Remote.cs"
    leak.write_text(
        "using System.Net.Http;\n\nnamespace App.Domain;\n\n"
        "/// <summary>A forbidden dependency.</summary>\n"
        "public sealed class Remote\n{\n    /// <summary>The client.</summary>\n"
        "    public HttpClient Client { get; } = new();\n}\n"
    )
    try:
        result = run(["dotnet", "test", "tests/App.ArchitectureTests"], csharp_backend, check=False)
    finally:
        leak.unlink()

    assert result.returncode != 0
    assert "App.Domain.Remote" in result.stdout


def test_csharp_domain_referencing_infrastructure_fails_the_build(csharp_backend: Path) -> None:
    project = csharp_backend / "src/App.Domain/App.Domain.csproj"
    original = project.read_text()
    project.write_text(
        original.replace(
            "</Project>",
            "  <ItemGroup>\n"
            '    <ProjectReference Include="../App.Infrastructure/App.Infrastructure.csproj" />\n'
            "  </ItemGroup>\n</Project>",
        )
    )
    try:
        result = run(["dotnet", "build", "--no-restore"], csharp_backend, check=False)
    finally:
        project.write_text(original)

    assert result.returncode != 0
    assert "circular" in (result.stdout + result.stderr).lower()


def test_csharp_warning_fails_the_build(csharp_backend: Path) -> None:
    source = csharp_backend / "src/App.Domain/Greeting.cs"
    original = source.read_text()
    source.write_text(
        original.replace("var trimmed = name.Trim();", "var trimmed = name.Trim(); var unused = 1;")
    )
    try:
        result = run(["dotnet", "build", "--no-restore"], csharp_backend, check=False)
    finally:
        source.write_text(original)

    assert result.returncode != 0
    assert "error" in result.stdout.lower()


def test_csharp_coverage_below_the_threshold_fails(csharp_backend: Path) -> None:
    tests = [
        csharp_backend / "tests/App.UnitTests" / name
        for name in ("GreetingTests.cs", "GreetUseCaseTests.cs")
    ]
    contents = [test.read_text() for test in tests]
    for test in tests:
        test.unlink()
    placeholder = csharp_backend / "tests/App.UnitTests/PlaceholderTests.cs"
    placeholder.write_text(
        "using Xunit;\n\nnamespace App.UnitTests;\n\npublic sealed class PlaceholderTests\n{\n"
        "    [Fact]\n    public void Placeholder_Always_Passes() => Assert.True(true);\n}\n"
    )
    try:
        result = run(
            ["dotnet", "test", "tests/App.UnitTests", "-p:CollectCoverage=true", "--no-restore"],
            csharp_backend,
            check=False,
        )
    finally:
        placeholder.unlink()
        for test, content in zip(tests, contents, strict=True):
            test.write_text(content)

    assert result.returncode != 0
    assert "below the specified 80" in result.stdout


@pytest.mark.parametrize(
    "script",
    ["format:check", "lint", "typecheck", "test:unit --coverage", "test:integration"],
)
def test_frontend_gate_passes(frontend: Path, script: str) -> None:
    run(["pnpm", *script.split()], frontend)


def test_frontend_end_to_end_tests_pass(frontend: Path) -> None:
    if SKIP_E2E:
        pytest.skip("GENERATED_SKIP_E2E=1")
    if IN_CI:
        run(["pnpm", "exec", "playwright", "install", "--with-deps", "chromium"], frontend)
    run(["pnpm", "e2e"], frontend)


def test_frontend_layer_rule_fails_lint_when_domain_imports_from_interfaces(
    frontend: Path,
) -> None:
    leak = frontend / "src/domain/leak.ts"
    leak.write_text("import { App } from '@/interfaces/App';\n\nexport const leaked = App;\n")
    try:
        result = run(["pnpm", "lint"], frontend, check=False)
    finally:
        leak.unlink()

    assert result.returncode != 0
    assert "leak.ts" in result.stdout
    assert "boundaries/dependencies" in result.stdout


def test_frontend_locked_dependencies_have_no_high_or_critical_vulnerability(
    frontend: Path,
) -> None:
    run(["pnpm", "audit", "--audit-level", "high"], frontend)


def test_single_application_typologies_render_the_same_skeletons(
    fullstack: Path, tmp_path: Path
) -> None:
    use_case = RenderProject(
        JinjaTemplateEngine(), FilesystemTemplateSource(TEMPLATES_ROOT), FilesystemTreeWriter()
    )
    use_case.execute(
        raw_spec(typology="backend", technologies={"backend": "python"}), OWNER, tmp_path / "b"
    )
    use_case.execute(
        raw_spec(typology="frontend", technologies={"frontend": "react-typescript"}),
        OWNER,
        tmp_path / "f",
    )

    for target, kind in ((tmp_path / "b", "backend"), (tmp_path / "f", "frontend")):
        for path in (target / "apps" / kind).rglob("*"):
            if path.is_file():
                relative = path.relative_to(target)
                assert (fullstack / relative).read_bytes() == path.read_bytes(), relative
