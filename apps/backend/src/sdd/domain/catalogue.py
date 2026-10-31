"""Catalogues of what a project spec may select: typologies, technologies and AI agents."""

from collections.abc import Mapping
from enum import StrEnum
from types import MappingProxyType


class ApplicationKind(StrEnum):
    BACKEND = "backend"
    FRONTEND = "frontend"


class Typology(StrEnum):
    BACKEND = "backend"
    FRONTEND = "frontend"
    FULLSTACK = "fullstack"


class Technology(StrEnum):
    CSHARP = "csharp"
    PYTHON = "python"
    REACT_TYPESCRIPT = "react-typescript"


class ProjectType(StrEnum):
    API = "api"
    CONSOLE = "console"
    LIBRARY = "library"


class AiAgent(StrEnum):
    CLAUDE = "claude"


TYPOLOGY_APPLICATIONS: Mapping[Typology, tuple[ApplicationKind, ...]] = MappingProxyType(
    {
        Typology.BACKEND: (ApplicationKind.BACKEND,),
        Typology.FRONTEND: (ApplicationKind.FRONTEND,),
        Typology.FULLSTACK: (ApplicationKind.BACKEND, ApplicationKind.FRONTEND),
    }
)

KIND_TECHNOLOGIES: Mapping[ApplicationKind, tuple[Technology, ...]] = MappingProxyType(
    {
        ApplicationKind.BACKEND: (Technology.PYTHON, Technology.CSHARP),
        ApplicationKind.FRONTEND: (Technology.REACT_TYPESCRIPT,),
    }
)

DEFAULT_PROJECT_TYPE = ProjectType.API

TECHNOLOGY_PROJECT_TYPES: Mapping[Technology, tuple[ProjectType, ...]] = MappingProxyType(
    {
        Technology.CSHARP: (ProjectType.API, ProjectType.CONSOLE, ProjectType.LIBRARY),
        Technology.PYTHON: (ProjectType.API, ProjectType.CONSOLE, ProjectType.LIBRARY),
    }
)

TECHNOLOGY_ECOSYSTEMS: Mapping[Technology, str] = MappingProxyType(
    {
        Technology.CSHARP: "nuget",
        Technology.PYTHON: "uv",
        Technology.REACT_TYPESCRIPT: "npm",
    }
)

TECHNOLOGY_STACK_SHEETS: Mapping[tuple[ApplicationKind, Technology], str] = MappingProxyType(
    {
        (ApplicationKind.BACKEND, Technology.CSHARP): "backend-csharp.md",
        (ApplicationKind.BACKEND, Technology.PYTHON): "backend-python.md",
        (ApplicationKind.FRONTEND, Technology.REACT_TYPESCRIPT): "frontend-react.md",
    }
)

AGENT_ENTRY_FILES: Mapping[AiAgent, str] = MappingProxyType({AiAgent.CLAUDE: "CLAUDE.md"})


def applications_of(typology: Typology) -> tuple[ApplicationKind, ...]:
    """Return the kinds of application a typology contains."""
    return TYPOLOGY_APPLICATIONS[typology]
