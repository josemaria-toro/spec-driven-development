from pathlib import Path

import pytest

from project_generator.application.errors import TemplateRenderError
from project_generator.application.render_project import RenderProject
from project_generator.domain.errors import ValidationFailedError
from project_generator.domain.project_spec import ProjectSpec
from tests.unit.factories import raw_spec
from tests.unit.fakes import (
    FakeTemplateSource,
    RecordingWriter,
    UppercaseEngine,
    standard_templates,
)

TARGET = Path("/unused/target")


def build(
    templates: dict[str, bytes] | None = None,
) -> tuple[RenderProject, RecordingWriter, UppercaseEngine, FakeTemplateSource]:
    source = FakeTemplateSource(templates or standard_templates())
    engine = UppercaseEngine()
    writer = RecordingWriter()
    return RenderProject(engine, source, writer), writer, engine, source


def test_valid_spec_is_rendered_and_written_once() -> None:
    use_case, writer, _, _ = build()

    result = use_case.execute(ProjectSpec.from_raw(raw_spec()), "acme-platform", TARGET)

    assert len(writer.calls) == 1
    tree, target = writer.calls[0]
    assert target == TARGET
    assert sorted(tree.files) == list(result.files)


def test_raw_invalid_spec_is_not_rendered() -> None:
    use_case, writer, _, _ = build()

    with pytest.raises(ValidationFailedError) as error:
        use_case.execute(raw_spec(repository_name="../x"), "acme-platform", TARGET)

    assert error.value.issues[0].field == "repository_name"
    assert writer.calls == []


def test_raw_valid_spec_is_validated_and_rendered() -> None:
    use_case, writer, _, _ = build()

    use_case.execute(raw_spec(), "acme-platform", TARGET)

    assert len(writer.calls) == 1


def test_owner_is_written_to_the_ownership_file() -> None:
    use_case, writer, _, _ = build()

    use_case.execute(raw_spec(), "acme-platform", TARGET)

    codeowners = writer.calls[0][0].files[".github/CODEOWNERS"].content
    assert codeowners == b"* @acme-platform\n"


def test_missing_owner_is_rejected_before_writing() -> None:
    use_case, writer, engine, _ = build()

    with pytest.raises(ValidationFailedError) as error:
        use_case.execute(raw_spec(), None, TARGET)

    assert error.value.issues[0].field == "owner"
    assert writer.calls == []
    assert engine.rendered == []


@pytest.mark.parametrize(
    "owner",
    ["acme platform; rm -rf", "-acme", "acme-", "a--b", "", "x" * 40, "a/b", "@acme"],
)
def test_invalid_owner_is_rejected_before_writing(owner: str) -> None:
    use_case, writer, _, _ = build()

    with pytest.raises(ValidationFailedError):
        use_case.execute(raw_spec(), owner, TARGET)

    assert writer.calls == []


@pytest.mark.parametrize("owner", ["a", "acme", "acme-platform", "A1-b2", "x" * 39])
def test_valid_owner_is_accepted(owner: str) -> None:
    use_case, writer, _, _ = build()

    use_case.execute(raw_spec(), owner, TARGET)

    assert len(writer.calls) == 1


def test_failing_template_writes_nothing() -> None:
    templates = standard_templates() | {"project/z-last.md.tmpl": b"FAIL"}
    use_case, writer, engine, _ = build(templates)

    with pytest.raises(TemplateRenderError):
        use_case.execute(raw_spec(), "acme-platform", TARGET)

    assert engine.rendered != []
    assert writer.calls == []


def test_same_inputs_give_equal_digests() -> None:
    first = build()[0].execute(raw_spec(), "acme-platform", TARGET)
    second = build()[0].execute(raw_spec(), "acme-platform", TARGET)

    assert first.template_digest == second.template_digest
    assert first.tree_digest == second.tree_digest


def test_changed_template_changes_both_digests() -> None:
    before = build()[0].execute(raw_spec(), "acme-platform", TARGET)
    changed = standard_templates() | {"project/README.md.tmpl": b"changed\n"}

    after = build(changed)[0].execute(raw_spec(), "acme-platform", TARGET)

    assert before.template_digest != after.template_digest
    assert before.tree_digest != after.tree_digest


def test_different_owner_changes_only_the_tree_digest() -> None:
    first = build()[0].execute(raw_spec(), "acme-platform", TARGET)
    second = build()[0].execute(raw_spec(), "other-owner", TARGET)

    assert first.template_digest == second.template_digest
    assert first.tree_digest != second.tree_digest


def test_rendered_files_use_lf_line_endings() -> None:
    templates = standard_templates() | {"project/README.md.tmpl": b"one\r\ntwo\rthree\n"}
    use_case, writer, _, _ = build(templates)

    use_case.execute(raw_spec(), "acme-platform", TARGET)

    assert writer.calls[0][0].files["README.md"].content == b"one\ntwo\nthree\n"


def test_verbatim_files_are_copied_byte_for_byte() -> None:
    use_case, writer, engine, _ = build()

    use_case.execute(raw_spec(), "acme-platform", TARGET)

    assert writer.calls[0][0].files["AGENTS.md"].content == b"# AGENTS\n"
    assert "# AGENTS\n" not in engine.rendered
