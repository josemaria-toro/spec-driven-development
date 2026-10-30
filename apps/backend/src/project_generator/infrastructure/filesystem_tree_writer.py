"""Filesystem adapter of the tree writer port.

The tree is written into a temporary directory next to the target and renamed onto it.
On POSIX, renaming a directory onto an empty directory is atomic, so the target ends up
either empty (as before) or complete. A crash can leave only a stale temporary sibling
directory named `.<target>.tmp-*`, never a partial target. Unsupported: Windows, and a
target and temporary directory on different filesystems (they are siblings, so they share one).
"""

import os
import shutil
import tempfile
from pathlib import Path, PurePosixPath

from project_generator.application.errors import TargetNotEmptyError, UnsafePathError
from project_generator.domain.rendered_tree import RenderedTree

DIRECTORY_MODE = 0o755
EXECUTABLE_MODE = 0o755
FILE_MODE = 0o644


class FilesystemTreeWriter:
    """Writes a rendered tree into an empty or missing directory, or nothing at all."""

    def write(self, tree: RenderedTree, target: Path) -> None:
        """Write the whole tree into `target`; leave `target` untouched on any failure."""
        _check_paths(tree)
        _check_target(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=f".{target.name}.tmp-", dir=target.parent))
        try:
            _write_files(tree, staging)
            os.rename(staging, target)
        except BaseException:
            shutil.rmtree(staging, ignore_errors=True)
            raise


def _check_paths(tree: RenderedTree) -> None:
    for path in tree.files:
        relative = PurePosixPath(path)
        if (
            not relative.parts
            or relative.is_absolute()
            or ".." in relative.parts
            or "." in relative.parts
            or "\\" in path
        ):
            raise UnsafePathError(f"path '{path}' is not a safe relative path")


def _check_target(target: Path) -> None:
    if target.is_symlink():
        raise TargetNotEmptyError(f"target '{target.name}' is a link")
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        raise TargetNotEmptyError(f"target '{target.name}' exists and is not an empty directory")


def _write_files(tree: RenderedTree, staging: Path) -> None:
    for path in sorted(tree.files):
        file = tree.files[path]
        destination = staging.joinpath(*PurePosixPath(path).parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(file.content)
        destination.chmod(EXECUTABLE_MODE if file.executable else FILE_MODE)
    for directory in [staging, *(p for p in staging.rglob("*") if p.is_dir())]:
        directory.chmod(DIRECTORY_MODE)
