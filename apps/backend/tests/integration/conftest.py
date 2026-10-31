from collections.abc import Callable
from pathlib import Path

import pytest

from sdd.application.render_project import RenderProject, RenderResult
from sdd.infrastructure.filesystem_template_source import FilesystemTemplateSource
from sdd.infrastructure.filesystem_tree_writer import FilesystemTreeWriter
from sdd.infrastructure.jinja_engine import JinjaTemplateEngine
from tests.unit.factories import raw_spec

OWNER = "acme-platform"
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
TEMPLATES_ROOT = REPOSITORY_ROOT / "templates"

Render = Callable[..., RenderResult]

BACKEND_PYTHON_FILES = {
    "apps/backend/.gitignore",
    "apps/backend/README.md",
    "apps/backend/pyproject.toml",
    "apps/backend/src/app/__init__.py",
    "apps/backend/src/app/application/__init__.py",
    "apps/backend/src/app/application/greet.py",
    "apps/backend/src/app/domain/__init__.py",
    "apps/backend/src/app/domain/greeting.py",
    "apps/backend/src/app/infrastructure/__init__.py",
    "apps/backend/tests/__init__.py",
    "apps/backend/tests/integration/__init__.py",
    "apps/backend/tests/integration/test_greet.py",
    "apps/backend/tests/unit/__init__.py",
    "apps/backend/tests/unit/test_greet.py",
    "apps/backend/tests/unit/test_greeting.py",
    "apps/backend/uv.lock",
}

BACKEND_CSHARP_LIBRARY_FILES = {
    "apps/backend/.editorconfig",
    "apps/backend/.gitignore",
    "apps/backend/App.slnx",
    "apps/backend/Directory.Build.props",
    "apps/backend/Directory.Packages.props",
    "apps/backend/README.md",
    "apps/backend/global.json",
    "apps/backend/src/App.Application/App.Application.csproj",
    "apps/backend/src/App.Application/GreetUseCase.cs",
    "apps/backend/src/App.Application/packages.lock.json",
    "apps/backend/src/App.Domain/App.Domain.csproj",
    "apps/backend/src/App.Domain/Greeting.cs",
    "apps/backend/src/App.Domain/packages.lock.json",
    "apps/backend/src/App.Infrastructure/App.Infrastructure.csproj",
    "apps/backend/src/App.Infrastructure/packages.lock.json",
    "apps/backend/tests/App.ArchitectureTests/App.ArchitectureTests.csproj",
    "apps/backend/tests/App.ArchitectureTests/LayerRulesTests.cs",
    "apps/backend/tests/App.ArchitectureTests/packages.lock.json",
    "apps/backend/tests/App.IntegrationTests/App.IntegrationTests.csproj",
    "apps/backend/tests/App.IntegrationTests/GreetIntegrationTests.cs",
    "apps/backend/tests/App.IntegrationTests/packages.lock.json",
    "apps/backend/tests/App.UnitTests/App.UnitTests.csproj",
    "apps/backend/tests/App.UnitTests/GreetUseCaseTests.cs",
    "apps/backend/tests/App.UnitTests/GreetingTests.cs",
    "apps/backend/tests/App.UnitTests/packages.lock.json",
    "apps/backend/tests/Directory.Build.props",
}
BACKEND_CSHARP_CONSOLE_FILES = BACKEND_CSHARP_LIBRARY_FILES | {
    "apps/backend/src/App.Console/App.Console.csproj",
    "apps/backend/src/App.Console/Cli.cs",
    "apps/backend/src/App.Console/Program.cs",
    "apps/backend/src/App.Console/packages.lock.json",
    "apps/backend/tests/App.IntegrationTests/ConsoleProcessTests.cs",
    "apps/backend/tests/App.UnitTests/CliTests.cs",
}
BACKEND_CSHARP_API_FILES = BACKEND_CSHARP_LIBRARY_FILES | {
    "apps/backend/src/App.Api/App.Api.csproj",
    "apps/backend/src/App.Api/GreeterService.cs",
    "apps/backend/src/App.Api/GreetingEndpoint.cs",
    "apps/backend/src/App.Api/GreetingResponse.cs",
    "apps/backend/src/App.Api/IGreeter.cs",
    "apps/backend/src/App.Api/Program.cs",
    "apps/backend/src/App.Api/SecurityHeadersMiddleware.cs",
    "apps/backend/src/App.Api/packages.lock.json",
    "apps/backend/tests/App.IntegrationTests/ApiTests.cs",
    "apps/backend/tests/App.UnitTests/GreetingEndpointTests.cs",
    "apps/backend/tests/App.UnitTests/SecurityHeadersMiddlewareTests.cs",
}
BACKEND_CSHARP_FILES = {
    "api": BACKEND_CSHARP_API_FILES,
    "console": BACKEND_CSHARP_CONSOLE_FILES,
    "library": BACKEND_CSHARP_LIBRARY_FILES,
}

FRONTEND_REACT_FILES = {
    "apps/frontend/.gitignore",
    "apps/frontend/.npmrc",
    "apps/frontend/.nvmrc",
    "apps/frontend/.prettierignore",
    "apps/frontend/.prettierrc.json",
    "apps/frontend/README.md",
    "apps/frontend/eslint.config.js",
    "apps/frontend/index.html",
    "apps/frontend/package.json",
    "apps/frontend/playwright.config.ts",
    "apps/frontend/pnpm-lock.yaml",
    "apps/frontend/src/domain/page-content.ts",
    "apps/frontend/src/interfaces/App.test.tsx",
    "apps/frontend/src/interfaces/App.tsx",
    "apps/frontend/src/interfaces/app.css",
    "apps/frontend/src/main.tsx",
    "apps/frontend/src/vite-env.d.ts",
    "apps/frontend/tests/e2e/home.spec.ts",
    "apps/frontend/tests/integration/mount.test.tsx",
    "apps/frontend/tests/setup.ts",
    "apps/frontend/tsconfig.json",
    "apps/frontend/vite.config.ts",
    "apps/frontend/vitest.integration.config.ts",
}


def build_use_case(templates: Path = TEMPLATES_ROOT) -> RenderProject:
    return RenderProject(
        JinjaTemplateEngine(), FilesystemTemplateSource(templates), FilesystemTreeWriter()
    )


def read_tree(directory: Path) -> dict[str, bytes]:
    return {
        path.relative_to(directory).as_posix(): path.read_bytes()
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


@pytest.fixture
def render(tmp_path: Path) -> Render:
    """Render a raw spec into a fresh directory and return the result."""
    counter = iter(range(1000))

    def _render(target: Path | None = None, **overrides: object) -> RenderResult:
        destination = target or tmp_path / f"out-{next(counter)}"
        return build_use_case().execute(raw_spec(**overrides), OWNER, destination)

    return _render
