"""An example use case."""

from app.domain.greeting import build_greeting


def greet(name: str) -> str:
    """Greet a person by name."""
    return build_greeting(name)
