"""Publication safety: no competitor directory or link may be replaced."""

from __future__ import annotations

import pathlib
import tomllib
from typing import Any

import pytest

from catss_tf import agora_adapter, canonical_materializer as canonical


def _source(tmp_path: pathlib.Path) -> pathlib.Path:
    root = tmp_path / "source"
    root.mkdir()
    (root / "01.Genesis.par").write_text("Gen 1:1\nHB\tLOGOS\n", encoding="utf-8")
    return root


def test_concurrent_empty_directory_never_replaced(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Inject a real competing mkdir after initial preflight, before the publish."""
    source = _source(tmp_path)
    output = tmp_path / "published"
    original_write = canonical._write_canonical_tf
    competitor_inode: list[int] = []

    def competing_writer(staging: pathlib.Path, graph: Any) -> None:
        output.mkdir()
        competitor_inode.append(output.stat().st_ino)
        original_write(staging, graph)

    monkeypatch.setattr(canonical, "_write_canonical_tf", competing_writer)
    with pytest.raises(FileExistsError):
        canonical.materialize_corpus(source, output)

    assert competitor_inode
    assert output.is_dir() and not output.is_symlink()
    assert output.stat().st_ino == competitor_inode[0], "another actor's inode was overwritten"
    assert list(output.iterdir()) == [], "native writer replaced the claimed directory"
    assert list(tmp_path.glob(".published.tmp-*")) == [], "staged data must be cleaned up"
    assert (source / "01.Genesis.par").read_text(encoding="utf-8") == "Gen 1:1\nHB\tLOGOS\n"


def test_dangling_destination_symlink_fails_closed(tmp_path: pathlib.Path) -> None:
    source = _source(tmp_path)
    target = tmp_path / "not-created"
    destination = tmp_path / "published"
    destination.symlink_to(target, target_is_directory=True)
    with pytest.raises((FileExistsError, canonical.CanonicalMaterializationError)):
        canonical.materialize_corpus(source, destination)

    assert destination.is_symlink()
    assert destination.readlink() == target
    assert not target.exists()
    assert list(tmp_path.glob(".published.tmp-*")) == []


def test_agora_preflight_delegates_to_shared_host_helper_before_materialization(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = _source(tmp_path)
    output = tmp_path / "host-staging"
    output.mkdir()
    preflights: list[pathlib.Path] = []

    def host_preflight(root: pathlib.Path) -> pathlib.Path:
        preflights.append(root)
        assert root == output and list(root.iterdir()) == []
        return root

    def stop_native(*_args: object, **_kwargs: object) -> None:
        assert preflights, "host preflight must precede CATSS parsing"
        raise RuntimeError("stop after host preflight")

    monkeypatch.setattr(agora_adapter, "prepare_agora_output", host_preflight, raising=False)
    monkeypatch.setattr(agora_adapter, "materialize_corpus", stop_native)
    with pytest.raises(RuntimeError, match="stop after host preflight"):
        agora_adapter.main([str(source), "--output", str(output)])
    assert preflights == [output]
    assert list(output.iterdir()) == []


def test_tf_build_dependency_is_pinned_to_published_immutable_wheel() -> None:
    pyproject = pathlib.Path(__file__).resolve().parents[1] / "pyproject.toml"
    metadata = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    dependencies = metadata["project"]["dependencies"]
    expected = (
        "tf-build @ https://github.com/alexsosn/tf-build/releases/download/"
        "v0.1.0rc1/tf_build-0.1.0rc1-py3-none-any.whl"
        "#sha256=dff2a14c0299422b4716217d04e6d43b47e714f4dacdb21d9939292051e82c9a"
    )
    assert expected in dependencies
