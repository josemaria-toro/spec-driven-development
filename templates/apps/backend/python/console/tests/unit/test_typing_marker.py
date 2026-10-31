from pathlib import Path

import app


def test_package_ships_the_typing_marker() -> None:
    assert (Path(app.__file__).parent / "py.typed").is_file()
