"""The validated description of a project to create."""

from __future__ import annotations

import hashlib
import json
import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass, replace
from enum import StrEnum

from sdd.domain.catalogue import (
    DEFAULT_PROJECT_TYPE,
    KIND_TECHNOLOGIES,
    TECHNOLOGY_PROJECT_TYPES,
    AiAgent,
    ApplicationKind,
    ProjectType,
    Technology,
    Typology,
    applications_of,
)
from sdd.domain.errors import ValidationFailedError, ValidationIssue
from sdd.domain.fields import (
    validate_description,
    validate_project_name,
    validate_repository_name,
)

SCHEMA_VERSION = 2
_BACKEND_ONLY = "applies only to a backend application"


@dataclass(frozen=True)
class Application:
    """One application of the monorepo: its kind, technology and, when offered, project type."""

    kind: ApplicationKind
    technology: Technology
    project_type: ProjectType | None = None

    @property
    def directory(self) -> str:
        """Directory of the application, relative to the repository root."""
        return f"apps/{self.kind.value}"


@dataclass(frozen=True)
class ProjectSpec:
    """A project spec that satisfies every rule; an invalid one cannot be built."""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "applications", tuple(_with_default_type(a) for a in self.applications)
        )
        object.__setattr__(self, "project_name", self.project_name.strip())
        object.__setattr__(self, "repository_name", self.repository_name.strip())
        object.__setattr__(self, "description", self.description.strip())
        issues = (
            validate_project_name(self.project_name)
            + validate_repository_name(self.repository_name)
            + validate_description(self.description)
            + _application_issues(self.typology, self.applications)
        )
        if issues:
            raise ValidationFailedError(issues)

    @classmethod
    def from_raw(cls, data: Mapping[str, object]) -> ProjectSpec:
        """Build a spec from untrusted data, reporting every invalid field at once."""
        issues: list[ValidationIssue] = []
        project_name = _read_text(data, "project_name", issues)
        repository_name = _read_text(data, "repository_name", issues)
        description = _read_text(data, "description", issues)
        typology = _read_choice(data, "typology", Typology, issues)
        agent = _read_choice(data, "agent", AiAgent, issues)
        applications = _read_applications(data, typology, issues)
        applications = _read_project_type(data, typology, applications, issues)
        issues += _field_issues(project_name, repository_name, description)
        if issues or typology is None or agent is None:
            raise ValidationFailedError(issues)
        return cls(
            agent=agent,
            applications=applications,
            description=description or "",
            project_name=project_name or "",
            repository_name=repository_name or "",
            typology=typology,
        )

    agent: AiAgent
    applications: tuple[Application, ...]
    description: str
    project_name: str
    repository_name: str
    typology: Typology

    def canonical_form(self) -> str:
        """Return the canonical JSON: sorted keys, no spaces, Unicode NFC, schema version."""
        document: dict[str, object] = {
            "agent": self.agent.value,
            "description": unicodedata.normalize("NFC", self.description),
            "project_name": unicodedata.normalize("NFC", self.project_name),
            "repository_name": self.repository_name,
            "schema_version": SCHEMA_VERSION,
            "technologies": {a.kind.value: a.technology.value for a in self.applications},
            "typology": self.typology.value,
        }
        project_type = next((a.project_type for a in self.applications if a.project_type), None)
        if project_type is not None:
            document["project_type"] = project_type.value
        return json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def content_hash(self) -> str:
        """Return the SHA-256 of the canonical form, hex-encoded."""
        return hashlib.sha256(self.canonical_form().encode("utf-8")).hexdigest()


def _application_issues(
    typology: Typology, applications: tuple[Application, ...]
) -> list[ValidationIssue]:
    expected = applications_of(typology)
    if tuple(application.kind for application in applications) != expected:
        return [ValidationIssue("technologies", f"must match the '{typology.value}' typology")]
    issues = [
        _unsupported_technology_issue(application.kind, application.technology.value)
        for application in applications
        if application.technology not in KIND_TECHNOLOGIES[application.kind]
    ]
    for application in applications:
        issue = _project_type_issue(application)
        if issue is not None:
            issues.append(issue)
    return issues


def _project_type_issue(application: Application) -> ValidationIssue | None:
    project_type = application.project_type
    if project_type is None:
        return None
    if application.kind is not ApplicationKind.BACKEND:
        return ValidationIssue("project_type", _BACKEND_ONLY)
    offered = TECHNOLOGY_PROJECT_TYPES.get(application.technology, ())
    if not offered:
        return ValidationIssue("project_type", _offers_none(application.technology))
    if project_type not in offered:
        return ValidationIssue("project_type", _unsupported_project_type(offered, project_type))
    return None


def _with_default_type(application: Application) -> Application:
    offered = TECHNOLOGY_PROJECT_TYPES.get(application.technology, ())
    if application.project_type is None and application.kind is ApplicationKind.BACKEND and offered:
        return replace(application, project_type=DEFAULT_PROJECT_TYPE)
    return application


def _read_project_type(
    data: Mapping[str, object],
    typology: Typology | None,
    applications: tuple[Application, ...],
    issues: list[ValidationIssue],
) -> tuple[Application, ...]:
    value = data.get("project_type")
    if value is None or typology is None:
        return applications
    backend = next((a for a in applications if a.kind is ApplicationKind.BACKEND), None)
    if ApplicationKind.BACKEND not in applications_of(typology):
        issues.append(ValidationIssue("project_type", _BACKEND_ONLY))
    elif backend is not None:
        selected = _choose_project_type(value, backend.technology, issues)
        if selected is not None:
            return tuple(
                replace(a, project_type=selected) if a is backend else a for a in applications
            )
    return applications


def _choose_project_type(
    value: object, technology: Technology, issues: list[ValidationIssue]
) -> ProjectType | None:
    offered = TECHNOLOGY_PROJECT_TYPES.get(technology, ())
    if not offered:
        issues.append(ValidationIssue("project_type", _offers_none(technology)))
    elif isinstance(value, str) and value in {choice.value for choice in offered}:
        return ProjectType(value)
    else:
        issues.append(ValidationIssue("project_type", _unsupported_project_type(offered, value)))
    return None


def _offers_none(technology: Technology) -> str:
    return f"the '{technology.value}' technology offers no project types"


def _unsupported_project_type(offered: tuple[ProjectType, ...], value: object) -> str:
    supported = ", ".join(choice.value for choice in offered)
    return f"'{value}' is not supported; supported values: {supported}"


def _field_issues(
    project_name: str | None, repository_name: str | None, description: str | None
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if project_name is not None:
        issues += validate_project_name(project_name)
    if repository_name is not None:
        issues += validate_repository_name(repository_name)
    if description is not None:
        issues += validate_description(description)
    return issues


def _read_applications(
    data: Mapping[str, object], typology: Typology | None, issues: list[ValidationIssue]
) -> tuple[Application, ...]:
    if typology is None:
        return ()
    expected = applications_of(typology)
    raw = data.get("technologies")
    if not isinstance(raw, Mapping):
        issues.append(ValidationIssue("technologies", "is required"))
        return ()
    for key in raw:
        if key not in {kind.value for kind in expected}:
            issues.append(
                ValidationIssue(
                    f"technologies.{key}", f"not part of the '{typology.value}' typology"
                )
            )
    applications: list[Application] = []
    for kind in expected:
        technology = _read_technology(raw, kind, issues)
        if technology is not None:
            applications.append(Application(kind=kind, technology=technology))
    return tuple(applications)


def _read_choice[ChoiceT: StrEnum](
    data: Mapping[str, object],
    field: str,
    choices: type[ChoiceT],
    issues: list[ValidationIssue],
) -> ChoiceT | None:
    value = data.get(field)
    supported = ", ".join(choice.value for choice in choices)
    if value is None:
        issues.append(ValidationIssue(field, f"is required; supported values: {supported}"))
        return None
    if isinstance(value, str) and value in {choice.value for choice in choices}:
        return choices(value)
    issues.append(ValidationIssue(field, f"is not supported; supported values: {supported}"))
    return None


def _read_technology(
    raw: Mapping[object, object], kind: ApplicationKind, issues: list[ValidationIssue]
) -> Technology | None:
    value = raw.get(kind.value)
    if value is None:
        issues.append(
            ValidationIssue(
                f"technologies.{kind.value}",
                f"a technology is required for the {kind.value} application",
            )
        )
        return None
    supported = {technology.value: technology for technology in KIND_TECHNOLOGIES[kind]}
    if isinstance(value, str) and value in supported:
        return supported[value]
    issues.append(_unsupported_technology_issue(kind, str(value)))
    return None


def _read_text(data: Mapping[str, object], field: str, issues: list[ValidationIssue]) -> str | None:
    value = data.get(field)
    if value is None:
        return ""
    if not isinstance(value, str):
        issues.append(ValidationIssue(field, "must be text"))
        return None
    return value.strip()


def _unsupported_technology_issue(kind: ApplicationKind, value: str) -> ValidationIssue:
    supported = ", ".join(technology.value for technology in KIND_TECHNOLOGIES[kind])
    return ValidationIssue(
        f"technologies.{kind.value}",
        f"'{value}' is not supported for a {kind.value} application; supported: {supported}",
    )
