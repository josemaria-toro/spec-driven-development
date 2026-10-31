from app.application.greet import greet


def test_greet_uses_the_domain_rule() -> None:
    assert greet(" Ada ") == "Hello, Ada!"
