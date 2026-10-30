"""Filesystem adapter of the template source port."""

import os
from pathlib import Path, PurePosixPath

from project_generator.application.errors import TemplateSourceError


class FilesystemTemplateSource:
    """Reads template files under one root and refuses symbolic links and escapes."""

    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def list_templates(self) -> tuple[str, ...]:
        """Relative POSIX paths of every template file, sorted."""
        found: list[str] = []
        for directory, directories, files in os.walk(self._root, followlinks=False):
            for name in [*directories, *files]:
                if (Path(directory) / name).is_symlink():
                    raise TemplateSourceError(f"templates must not contain links: '{name}'")
            found += [(Path(directory) / name).relative_to(self._root).as_posix() for name in files]
        return tuple(sorted(found))

    def read(self, path: str) -> bytes:
        """Content of one template file."""
        relative = PurePosixPath(path)
        if relative.is_absolute() or ".." in relative.parts or not relative.parts:
            raise TemplateSourceError(f"template path '{path}' is not a safe relative path")
        candidate = self._root.joinpath(*relative.parts)
        if candidate.is_symlink() or not candidate.resolve().is_relative_to(self._root):
            raise TemplateSourceError(f"template '{path}' is outside the templates root")
        return candidate.read_bytes()
