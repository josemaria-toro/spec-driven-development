from pathlib import Path

import pytest

from project_generator.application.errors import TemplateSourceError
from project_generator.infrastructure.filesystem_template_source import FilesystemTemplateSource

pytestmark = pytest.mark.integration


def make_root(tmp_path: Path) -> Path:
    root = tmp_path / "templates"
    (root / "project").mkdir(parents=True)
    (root / "project" / "README.md.tmpl").write_bytes(b"readme\n")
    (root / "project" / ".gitkeep").write_bytes(b"")
    return root


def test_templates_are_listed_as_sorted_relative_posix_paths(tmp_path: Path) -> None:
    source = FilesystemTemplateSource(make_root(tmp_path))

    assert source.list_templates() == ("project/.gitkeep", "project/README.md.tmpl")


def test_template_content_is_read_byte_for_byte(tmp_path: Path) -> None:
    source = FilesystemTemplateSource(make_root(tmp_path))

    assert source.read("project/README.md.tmpl") == b"readme\n"


def test_symbolic_link_to_a_file_is_refused_when_listing(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    secret = tmp_path / "secret.txt"
    secret.write_text("secret")
    (root / "project" / "link.txt").symlink_to(secret)

    with pytest.raises(TemplateSourceError, match="links"):
        FilesystemTemplateSource(root).list_templates()


def test_symbolic_link_to_a_directory_is_refused_when_listing(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    (root / "linked").symlink_to(tmp_path)

    with pytest.raises(TemplateSourceError, match="links"):
        FilesystemTemplateSource(root).list_templates()


def test_symbolic_link_is_refused_when_reading(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    secret = tmp_path / "secret.txt"
    secret.write_text("secret")
    (root / "project" / "link.txt").symlink_to(secret)

    with pytest.raises(TemplateSourceError):
        FilesystemTemplateSource(root).read("project/link.txt")


@pytest.mark.parametrize("path", ["../secret.txt", "project/../../secret.txt", "/etc/passwd", ""])
def test_traversal_is_refused_when_reading(tmp_path: Path, path: str) -> None:
    (tmp_path / "secret.txt").write_text("secret")

    with pytest.raises(TemplateSourceError):
        FilesystemTemplateSource(make_root(tmp_path)).read(path)
