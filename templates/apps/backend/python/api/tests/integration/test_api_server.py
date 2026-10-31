import socket
import subprocess
import sys
import time
from collections.abc import Iterator

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app

pytestmark = pytest.mark.integration

STARTUP_TIMEOUT_SECONDS = 15


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


@pytest.fixture
def server_url() -> Iterator[str]:
    port = free_port()
    url = f"http://127.0.0.1:{port}"
    process = subprocess.Popen(  # noqa: S603
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            try:
                httpx.get(f"{url}/greetings/ready", timeout=1)
                break
            except httpx.TransportError:
                time.sleep(0.2)
        else:
            pytest.fail("the server did not start")
        yield url
    finally:
        process.terminate()
        process.wait(timeout=10)


def test_entry_module_serves_the_greeting() -> None:
    response = TestClient(app).get("/greetings/Ada")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Ada!"}


def test_entry_module_rejects_a_name_that_is_too_long() -> None:
    response = TestClient(app).get(f"/greetings/{'a' * 101}")

    assert response.status_code == 400


def test_running_server_answers_over_http_with_the_security_headers(server_url: str) -> None:
    response = httpx.get(f"{server_url}/greetings/Ada", timeout=5)

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Ada!"}
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_running_server_hides_the_interactive_documentation(server_url: str) -> None:
    assert httpx.get(f"{server_url}/docs", timeout=5).status_code == 404
