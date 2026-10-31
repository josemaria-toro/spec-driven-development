import pytest
from fastapi.testclient import TestClient

from app.interfaces import api
from app.interfaces.api import MAX_NAME_LENGTH, SECURITY_HEADERS, create_app


def failing_use_case(_: str) -> str:
    raise RuntimeError("secret detail")


def test_valid_name_is_greeted_with_the_security_headers() -> None:
    response = TestClient(create_app()).get("/greetings/Ada")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Ada!"}
    for header, value in SECURITY_HEADERS.items():
        assert response.headers[header] == value


def test_longest_name_is_accepted() -> None:
    response = TestClient(create_app()).get(f"/greetings/{'a' * MAX_NAME_LENGTH}")

    assert response.status_code == 200


def test_name_that_is_too_long_is_a_client_error_that_names_the_field() -> None:
    name = "a" * (MAX_NAME_LENGTH + 1)

    response = TestClient(create_app()).get(f"/greetings/{name}")

    assert response.status_code == 400
    assert response.headers["content-type"] == "application/problem+json"
    assert list(response.json()["errors"]) == ["name"]
    assert name not in response.text
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_unhandled_error_reveals_nothing_and_keeps_the_headers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(api, "greet", failing_use_case)
    client = TestClient(create_app(), raise_server_exceptions=False)

    response = client.get("/greetings/Ada")

    assert response.status_code == 500
    assert response.headers["content-type"] == "application/problem+json"
    assert "secret detail" not in response.text
    assert "RuntimeError" not in response.text
    assert "Traceback" not in response.text
    assert response.headers["X-Frame-Options"] == "DENY"


@pytest.mark.parametrize("path", ["/docs", "/redoc", "/openapi.json"])
def test_interactive_documentation_is_off_by_default(path: str) -> None:
    assert TestClient(create_app()).get(path).status_code == 404
