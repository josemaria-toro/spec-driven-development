"""An example business rule."""

DEFAULT_NAME = "world"


def build_greeting(name: str) -> str:
    """Return the greeting for a name, or for the default name when it is blank."""
    return f"Hello, {name.strip() or DEFAULT_NAME}!"
