"""The files of a rendered project, held in memory."""

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class RenderedFile:
    content: bytes
    executable: bool = False


@dataclass(frozen=True)
class RenderedTree:
    """Relative POSIX path to file; paths are already validated by the render plan."""

    files: Mapping[str, RenderedFile]

    def digest(self) -> str:
        """SHA-256 over the sorted paths, modes and contents."""
        hasher = hashlib.sha256()
        for path in sorted(self.files):
            file = self.files[path]
            hasher.update(path.encode("utf-8") + b"\0")
            hasher.update(b"x" if file.executable else b"-")
            hasher.update(str(len(file.content)).encode("ascii") + b"\0" + file.content)
        return hasher.hexdigest()
