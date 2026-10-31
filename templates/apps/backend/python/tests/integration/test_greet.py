import pytest

from app.application.greet import greet

pytestmark = pytest.mark.integration


def test_greet_goes_through_the_domain() -> None:
    assert greet("Ada") == "Hello, Ada!"
