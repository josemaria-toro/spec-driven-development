import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

COMMAND = Path(sys.executable).parent / "backend"


def run_module(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        [sys.executable, "-m", "app", *arguments], capture_output=True, text=True, check=False
    )


def test_module_run_greets_the_name() -> None:
    result = run_module("Ada")

    assert result.returncode == 0
    assert result.stdout == "Hello, Ada!\n"
    assert result.stderr == ""


def test_module_run_with_too_many_arguments_fails_with_the_usage_on_standard_error() -> None:
    result = run_module("Ada", "Grace")

    assert result.returncode == 2
    assert result.stdout == ""
    assert "usage:" in result.stderr
    assert "Traceback" not in result.stderr


def test_installed_command_behaves_like_the_module() -> None:
    result = subprocess.run(  # noqa: S603
        [str(COMMAND), "Ada"], capture_output=True, text=True, check=False
    )

    assert result.returncode == 0
    assert result.stdout == "Hello, Ada!\n"
