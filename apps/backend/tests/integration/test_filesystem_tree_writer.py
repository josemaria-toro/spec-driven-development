import stat
from pathlib import Path

import pytest

from project_generator.application.errors import TargetNotEmptyError, UnsafePathError
from project_generator.domain.rendered_tree import RenderedFile, RenderedTree
from project_generator.infrastructure.filesystem_tree_writer import FilesystemTreeWriter

pytestmark = pytest.mark.integration


def tree(**files: bytes) -> RenderedTree:
    return RenderedTree(files={path: RenderedFile(content) for path, content in files.items()})


def snapshot(directory: Path) -> dict[str, bytes | None]:
    return {
        path.relative_to(directory).as_posix(): path.read_bytes() if path.is_file() else None
        for path in sorted(directory.rglob("*"))
    }


def test_tree_is_written_into_a_missing_target(tmp_path: Path) -> None:
    target = tmp_path / "workspace" / "project"

    FilesystemTreeWriter().write(
        RenderedTree(
            files={
                "AGENTS.md": RenderedFile(b"agents\n"),
                "apps/backend/README.md": RenderedFile(b"backend\n"),
                "bin/run.sh": RenderedFile(b"#!/bin/sh\n", executable=True),
            }
        ),
        target,
    )

    assert (target / "AGENTS.md").read_bytes() == b"agents\n"
    assert (target / "apps/backend/README.md").read_bytes() == b"backend\n"
    assert stat.S_IMODE((target / "AGENTS.md").stat().st_mode) == 0o644
    assert stat.S_IMODE((target / "bin/run.sh").stat().st_mode) == 0o755
    assert stat.S_IMODE((target / "apps").stat().st_mode) == 0o755
    assert stat.S_IMODE(target.stat().st_mode) == 0o755


def test_tree_is_written_into_an_existing_empty_target(tmp_path: Path) -> None:
    target = tmp_path / "project"
    target.mkdir()

    FilesystemTreeWriter().write(tree(**{"README.md": b"x"}), target)

    assert snapshot(target) == {"README.md": b"x"}


def test_non_empty_target_is_refused_and_left_unchanged(tmp_path: Path) -> None:
    target = tmp_path / "project"
    target.mkdir()
    (target / "existing.txt").write_bytes(b"keep")

    with pytest.raises(TargetNotEmptyError):
        FilesystemTreeWriter().write(tree(**{"README.md": b"x"}), target)

    assert snapshot(target) == {"existing.txt": b"keep"}
    assert [p.name for p in tmp_path.iterdir()] == ["project"]


def test_target_that_is_a_file_is_refused(tmp_path: Path) -> None:
    target = tmp_path / "project"
    target.write_bytes(b"file")

    with pytest.raises(TargetNotEmptyError):
        FilesystemTreeWriter().write(tree(**{"README.md": b"x"}), target)

    assert target.read_bytes() == b"file"


def test_target_that_is_a_link_is_refused(tmp_path: Path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    target = tmp_path / "project"
    target.symlink_to(real)

    with pytest.raises(TargetNotEmptyError):
        FilesystemTreeWriter().write(tree(**{"README.md": b"x"}), target)

    assert list(real.iterdir()) == []


def test_failure_in_the_middle_of_writing_leaves_the_target_empty(tmp_path: Path) -> None:
    target = tmp_path / "project"
    target.mkdir()

    with pytest.raises(OSError):
        FilesystemTreeWriter().write(tree(**{"a": b"file", "a/b": b"conflict"}), target)

    assert snapshot(target) == {}
    assert [p.name for p in tmp_path.iterdir()] == ["project"]


def test_failure_when_the_target_is_missing_creates_no_target(tmp_path: Path) -> None:
    target = tmp_path / "project"

    with pytest.raises(OSError):
        FilesystemTreeWriter().write(tree(**{"a": b"file", "a/b": b"conflict"}), target)

    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("path", ["../outside.txt", "a/../../outside.txt", "/abs.txt", "a\\b", ""])
def test_path_outside_the_target_writes_nothing_outside(tmp_path: Path, path: str) -> None:
    target = tmp_path / "workspace" / "project"

    with pytest.raises(UnsafePathError):
        FilesystemTreeWriter().write(tree(**{"README.md": b"x", path: b"escape"}), target)

    assert not (tmp_path / "workspace" / "outside.txt").exists()
    assert not (tmp_path / "outside.txt").exists()
    assert not target.exists()
    assert not (tmp_path / "workspace").exists()
