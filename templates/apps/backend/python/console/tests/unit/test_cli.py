import io
import runpy
import sys

import pytest

from app.interfaces.cli import USAGE_ERROR, run


def test_one_name_is_greeted_and_succeeds() -> None:
    output, errors = io.StringIO(), io.StringIO()

    exit_code = run(["Ada"], output, errors)

    assert exit_code == 0
    assert output.getvalue() == "Hello, Ada!\n"
    assert errors.getvalue() == ""


def test_no_argument_greets_the_default_name() -> None:
    output = io.StringIO()

    assert run([], output, io.StringIO()) == 0
    assert output.getvalue() == "Hello, world!\n"


@pytest.mark.parametrize("arguments", [["Ada", "Grace"], ["--unknown"]])
def test_invalid_arguments_write_the_usage_to_the_error_stream_only(
    arguments: list[str],
) -> None:
    output, errors = io.StringIO(), io.StringIO()

    exit_code = run(arguments, output, errors)

    assert exit_code == USAGE_ERROR
    assert output.getvalue() == ""
    assert "usage:" in errors.getvalue()


def test_module_entry_point_exits_with_the_code_of_the_run(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["backend", "Ada"])

    with pytest.raises(SystemExit) as exit_info:
        runpy.run_module("app", run_name="__main__")

    assert exit_info.value.code == 0
    assert capsys.readouterr().out == "Hello, Ada!\n"
