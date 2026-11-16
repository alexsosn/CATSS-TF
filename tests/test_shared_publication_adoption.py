"""RED-first regression for real filesystem publication and shared integration."""

from __future__ import annotations

import importlib
import pathlib
import sys
import tomllib
import types

import pytest

from catss_tf import agora_adapter, canonical_materializer
from catss_tf.tf_schema import TfModuleMetadata


def _source(root: pathlib.Path) -> pathlib.Path:
    root.mkdir()
    (root / "01.Genesis.par").write_text("Gen 1:1\n)B\tQEOS\n--+\tLOGOS\n", encoding="utf-8")
    return root


@pytest.mark.parametrize("competitor", ["empty-directory", "dangling-symlink"])
def test_canonical_publish_must_not_replace_late_competitor(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    competitor: str,
) -> None:
    """A destination claimed after preflight is still owned by the rival."""
    source = _source(tmp_path / "source")
    destination = tmp_path / "published"
    outside = tmp_path / "does-not-exist"
    baseline: list[int] = []
    original_writer = canonical_materializer._write_canonical_tf

    def claim_after_writing(
        staging: pathlib.Path, graph: canonical_materializer._CanonicalGraph
    ) -> None:
        original_writer(staging, graph)
        if competitor == "empty-directory":
            destination.mkdir()
        else:
            destination.symlink_to(outside, target_is_directory=True)
        baseline.append(destination.lstat().st_ino)

    monkeypatch.setattr(canonical_materializer, "_write_canonical_tf", claim_after_writing)

    with pytest.raises(FileExistsError):
        canonical_materializer.materialize_corpus(source, destination)

    assert destination.lstat().st_ino == baseline[0]
    if competitor == "empty-directory":
        assert destination.is_dir()
        assert list(destination.iterdir()) == []
    else:
        assert destination.is_symlink()
        assert destination.readlink() == outside
        assert not outside.exists()
    assert not tuple(tmp_path.glob(".published.tmp-*"))


@pytest.mark.parametrize("projection", ["bhsa", "lxx"])
def test_parent_module_publish_must_not_replace_late_empty_directory(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    projection: str,
) -> None:
    """Use real staged directory publication, mocking only TF serialization."""
    materializer = importlib.import_module(f"catss_tf.{projection}_materializer")
    destination = tmp_path / f"catss-{projection}"
    baseline: list[int] = []

    def claim_during_write(
        staging: pathlib.Path,
        features: dict[str, dict[int, int | str]],
        *,
        metadata: TfModuleMetadata,
        max_node: int,
    ) -> None:
        (staging / "otype.tf").write_text("staged", encoding="utf-8")
        destination.mkdir()
        baseline.append(destination.stat().st_ino)

    monkeypatch.setattr(materializer, "write_tf_module", claim_during_write)
    metadata = TfModuleMetadata(
        projection=projection,  # type: ignore[arg-type]
        parent_repo="parent", parent_version="test", parent_release=None,
        parent_commit=None, software_version="test",
    )

    with pytest.raises(FileExistsError):
        materializer._publish_bundle(destination, features={}, metadata=metadata, sidecars={})

    assert destination.stat().st_ino == baseline[0]
    assert list(destination.iterdir()) == []
    assert not tuple(tmp_path.glob(f".catss-{projection}.tmp-*"))


def test_agora_preflight_delegates_to_shared_public_api(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "staging"
    output.mkdir()
    checked: list[pathlib.Path] = []

    def reject_from_shared_helper(root: pathlib.Path) -> pathlib.Path:
        checked.append(root)
        raise ValueError("shared Agora preflight sentinel")

    # Supply an isolated public API boundary for genuine RED even before
    # the published library is listed among CATSS's install dependencies.
    package = types.ModuleType("tf_build")
    shared_agora = types.ModuleType("tf_build.agora")
    monkeypatch.setattr(shared_agora, "prepare_agora_output", reject_from_shared_helper, raising=False)
    monkeypatch.setitem(sys.modules, "tf_build", package)
    monkeypatch.setitem(sys.modules, "tf_build.agora", shared_agora)

    with pytest.raises(ValueError, match="shared Agora preflight sentinel"):
        agora_adapter._check_inputs(tmp_path / "absent-source", output)
    assert checked == [output]
    assert tuple(output.iterdir()) == ()


def test_installable_package_pins_published_verified_shared_wheel() -> None:
    project = tomllib.loads(
        (pathlib.Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(
            encoding="utf-8"
        )
    )["project"]
    published = (
        "tf-build @ https://github.com/alexsosn/tf-build/releases/download/v0.1.0rc1/"
        "tf_build-0.1.0rc1-py3-none-any.whl"
        "#sha256=dff2a14c0299422b4716217d04e6d43b47e714f4dacdb21d9939292051e82c9a"
    )
    assert published in project["dependencies"]
