import pytest

from app.domain.greeting import build_greeting


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Ada", "Hello, Ada!"),
        ("  Ada  ", "Hello, Ada!"),
        ("", "Hello, world!"),
        ("  ", "Hello, world!"),
    ],
)
def test_build_greeting(name: str, expected: str) -> None:
    assert build_greeting(name) == expected
