import json

import pytest
import yaml

from project_generator.application.errors import TemplateRenderError
from project_generator.infrastructure.jinja_engine import JinjaTemplateEngine, md_escape


def render(template: str, **context: object) -> str:
    return JinjaTemplateEngine().render(template, context)


def test_template_syntax_in_a_value_stays_literal() -> None:
    hostile = "{{ 7 * 7 }} << 7 * 7 >> <% if true %> <# x #>"

    assert render("<< value | json_str >>", value=hostile) == json.dumps(hostile)
    assert render("<< value | md_escape >>", value="{{ 7 * 7 }}") == r"\{\{ 7 \* 7 \}\}"


def test_jinja_default_delimiters_are_not_interpreted_in_the_template() -> None:
    assert render("${{ github.sha }} and [[tool.uv]]") == "${{ github.sha }} and [[tool.uv]]"


@pytest.mark.parametrize(
    "value",
    ['say "hi"', "key: value", "- item", "# not a comment", "a\\b", "café", "\U0001f600", "'"],
)
def test_yaml_and_json_values_round_trip_exactly(value: str) -> None:
    rendered = render("key: << value | json_str >>\n", value=value)

    assert yaml.safe_load(rendered) == {"key": value}
    assert json.loads(render('{"key": << value | json_str >>}', value=value)) == {"key": value}


def test_markdown_control_characters_are_escaped() -> None:
    assert md_escape("*bold* _it_ [l](u) `c` <b> # h | t ~ ! &") == (
        r"\*bold\* \_it\_ \[l\]\(u\) \`c\` \<b\> \# h \| t \~ \! \&"
    )


@pytest.mark.parametrize(("value", "expected"), [("- item", r"\- item"), ("1. item", r"1\. item")])
def test_markdown_list_markers_at_the_start_are_escaped(value: str, expected: str) -> None:
    assert md_escape(value) == expected


def test_plain_names_are_not_over_escaped() -> None:
    assert md_escape("orders-platform v1.2") == "orders-platform v1.2"


def test_undefined_variable_fails() -> None:
    with pytest.raises(TemplateRenderError):
        render("<< missing >>")


def test_syntax_error_fails() -> None:
    with pytest.raises(TemplateRenderError):
        render("<% if %>")


def test_sandbox_blocks_access_to_internals() -> None:
    with pytest.raises(TemplateRenderError):
        render("<< value.__class__.__mro__ >>", value="x")


def test_yaml_block_values_with_line_breaks_are_rejected() -> None:
    with pytest.raises(TemplateRenderError):
        render("<< value | yaml_block >>", value="a\nb")


def test_unknown_filter_fails() -> None:
    with pytest.raises(TemplateRenderError):
        render("<< value | upper >>", value="x")


def test_blocks_do_not_leave_blank_lines() -> None:
    template = "a\n<% for item in items %>\n- << item | json_str >>\n<% endfor %>\nb\n"

    assert render(template, items=["x", "y"]) == 'a\n- "x"\n- "y"\nb\n'


def test_trailing_newline_is_kept() -> None:
    assert render("text\n") == "text\n"
