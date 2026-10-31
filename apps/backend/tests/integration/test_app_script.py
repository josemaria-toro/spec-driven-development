import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

SCRIPT = Path(__file__).resolve().parents[2] / "app.sh"
BASH = "bash"
USAGE_EXIT_CODE = 2


def run(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 - fixed script path, arguments from the test
        [BASH, str(SCRIPT), *arguments], capture_output=True, text=True, check=False, timeout=30
    )


def test_start_fails_because_the_backend_has_no_inbound_adapter() -> None:
    result = run("start")

    assert result.returncode == 1
    assert "nothing to start" in result.stderr


def test_stop_succeeds_because_nothing_is_running() -> None:
    result = run("stop")

    assert result.returncode == 0
    assert "not running" in result.stdout


@pytest.mark.parametrize("arguments", [(), ("restart",), ("start", "stop")])
def test_anything_else_prints_the_usage(arguments: tuple[str, ...]) -> None:
    result = run(*arguments)

    assert result.returncode == USAGE_EXIT_CODE
    assert "Usage:" in result.stderr
