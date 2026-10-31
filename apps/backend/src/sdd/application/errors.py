"""Errors raised through the ports of the application layer."""


class TemplateRenderError(Exception):
    """A template could not be rendered (syntax error, undefined value, forbidden value)."""


class TargetNotEmptyError(Exception):
    """The target directory exists and is not an empty directory."""


class TemplateSourceError(Exception):
    """A template path is unsafe: outside the templates root or reached through a link."""


class UnsafePathError(Exception):
    """A path of the tree would be written outside the target directory."""
