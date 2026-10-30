import re
from pathlib import Path

import pytest

from project_generator.domain.render_plan import TEMPLATE_SUFFIX
from tests.integration.conftest import TEMPLATES_ROOT

pytestmark = pytest.mark.integration

EXPRESSION = re.compile(r"<<(.*?)>>", re.DOTALL)
DELIMITERS = ("<<", "<%", "<#")
ALLOWED_FILTERS = {
    ".json": {"json_str"},
    ".md": {"md_escape"},
    ".yaml": {"json_str", "yaml_block"},
    ".yml": {"json_str", "yaml_block"},
}


def unfiltered_expressions(name: str, text: str) -> list[str]:
    """Expressions of a template that do not end in the filter of its target format."""
    extension = Path(name.removesuffix(TEMPLATE_SUFFIX)).suffix
    allowed = ALLOWED_FILTERS.get(extension)
    if allowed is None:
        return []
    problems = []
    for expression in EXPRESSION.findall(text):
        filter_name = expression.rsplit("|", 1)[-1].strip() if "|" in expression else ""
        if filter_name not in allowed:
            problems.append(expression.strip())
    return problems


def test_lint_flags_a_yaml_value_without_its_filter() -> None:
    assert unfiltered_expressions("x.yml.tmpl", "a: << project.name >>") == ["project.name"]


def test_lint_flags_a_markdown_value_with_the_wrong_filter() -> None:
    assert unfiltered_expressions("x.md.tmpl", "<< v | json_str >>") == ["v | json_str"]


def test_lint_accepts_the_filter_of_the_target_format() -> None:
    assert unfiltered_expressions("x.md.tmpl", "<< v | md_escape >>") == []
    assert unfiltered_expressions("x.yml.tmpl", '<< ("/" ~ a.d) | json_str >>') == []


def test_lint_ignores_formats_without_a_filter_requirement() -> None:
    assert unfiltered_expressions("CODEOWNERS.tmpl", "@<< owner >>") == []


def test_every_template_prints_its_values_with_the_filter_of_its_format() -> None:
    problems = {
        path.relative_to(TEMPLATES_ROOT).as_posix(): unfiltered_expressions(
            path.name, path.read_text(encoding="utf-8")
        )
        for path in TEMPLATES_ROOT.rglob("*.tmpl")
    }

    assert {name: found for name, found in problems.items() if found} == {}


def test_verbatim_files_do_not_contain_template_delimiters() -> None:
    offenders = [
        path.relative_to(TEMPLATES_ROOT).as_posix()
        for path in TEMPLATES_ROOT.rglob("*")
        if path.is_file()
        and not path.name.endswith(TEMPLATE_SUFFIX)
        and any(delimiter in path.read_text(encoding="utf-8") for delimiter in DELIMITERS)
    ]

    assert offenders == []
