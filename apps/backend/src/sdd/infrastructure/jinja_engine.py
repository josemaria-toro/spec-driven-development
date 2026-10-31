"""Jinja2 adapter of the template engine port."""

import json
import re
from collections.abc import Mapping

from jinja2 import StrictUndefined, TemplateError
from jinja2.sandbox import SandboxedEnvironment

from sdd.application.errors import TemplateRenderError

_MARKDOWN_SPECIAL = re.compile(r"([\\`*_{}\[\]()<>#|~!&])")
_MARKDOWN_LEADING = re.compile(r"^(?:([-+])|(\d+)([.)]))")
_LINE_BREAKS = ("\n", "\r", chr(0x2028), chr(0x2029))


def json_str(value: object) -> str:
    """Double-quoted string valid as a JSON string and as a YAML double-quoted scalar."""
    return json.dumps(str(value), ensure_ascii=False)


def md_escape(value: object) -> str:
    """Escape Markdown control characters so the value is shown as literal text."""
    escaped = _MARKDOWN_SPECIAL.sub(r"\\\1", str(value))
    return _MARKDOWN_LEADING.sub(_escape_leading_marker, escaped)


def _escape_leading_marker(match: re.Match[str]) -> str:
    if match.group(1):
        return "\\" + match.group(1)
    return match.group(2) + "\\" + match.group(3)


def yaml_block(value: object) -> str:
    """Text for a YAML block scalar: a single line, so no indentation can be broken."""
    text = str(value)
    if any(line_break in text for line_break in _LINE_BREAKS):
        raise TemplateRenderError("a value used in a YAML block must not contain line breaks")
    return text


class JinjaTemplateEngine:
    """Renders templates in a sandbox with `<< >>`, `<% %>` and `<# #>` delimiters."""

    def __init__(self) -> None:
        self._environment = SandboxedEnvironment(
            autoescape=False,
            block_end_string="%>",
            block_start_string="<%",
            comment_end_string="#>",
            comment_start_string="<#",
            keep_trailing_newline=True,
            lstrip_blocks=True,
            trim_blocks=True,
            undefined=StrictUndefined,
            variable_end_string=">>",
            variable_start_string="<<",
        )
        self._environment.filters.clear()
        self._environment.filters.update(
            {"json_str": json_str, "md_escape": md_escape, "yaml_block": yaml_block}
        )

    def render(self, source: str, context: Mapping[str, object]) -> str:
        """Render `source` with `context`; values are data and are never evaluated."""
        try:
            return self._environment.from_string(source).render(dict(context))
        except TemplateRenderError:
            raise
        except TemplateError as error:
            raise TemplateRenderError(f"template could not be rendered: {error}") from error
